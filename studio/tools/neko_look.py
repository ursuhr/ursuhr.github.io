"""Look de Neko Ramen para el reel de fideos: luz ámbar localizada sobre un ambiente casi negro.

Referencia: dos fotografías nocturnas reales del local. Medido en ellas:
  - negros casi absolutos (percentil 5 de luminancia 0,004 a 0,006; 19 % a 38 % de los píxeles por debajo de 0,03)
  - luminancia media 0,20 a 0,23 y mediana 0,07 a 0,15: ambiente muy oscuro
  - medios tonos ámbar saturados (aprox. RGB 0,60 0,32 0,14; tono 26° a 28°)
  - altas luces doradas y cremosas (aprox. RGB 0,95 0,77 0,49)
  - saturación de las zonas iluminadas alta (mediana 0,64 a 0,77); tonos concentrados entre 15° y 45°
Cómo se traslada al video:
  1. igualar: balance de blancos y exposición por clip (cada uno se grabó con luz distinta)
  2. máscara suave de "luz": sigue al producto (fideos, masa, manos) con una caída radial muy amplia
  3. el ambiente (fuera de la máscara) baja de exposición, aplasta los negros y queda neutro con un toque azulado
  4. la zona iluminada recibe curva de contraste, medios cobre/ámbar y luces doradas; el calor se aplica más a lo neutro y poco a lo ya saturado, para no teñir la comida
  5. selectivo: el azul de la máquina baja a azul muy oscuro; rojos y naranjas ganan algo de saturación
Trabaja con matrices float32 (H, W, 3) en 0..1.
"""
import numpy as np
from PIL import Image, ImageFilter

LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def luma(x):
    return x @ LUMA


def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def hue_deg(x):
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    mx = x.max(-1); d = mx - x.min(-1) + 1e-6
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    sat = d / (mx + 1e-6)
    return h, sat


def blur(m, frac):
    """desenfoque gaussiano de una máscara 2D, calculado a baja resolución"""
    h, w = m.shape
    sw = 160; sh = max(8, int(h * sw / w))
    im = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).resize((sw, sh), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(max(1, frac * sw)))
    return np.asarray(im.resize((w, h), Image.BICUBIC)).astype(np.float32) / 255


def radial(h, w, cx, cy, rx, ry, power=1.6):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx / w - cx) / rx) ** 2 + ((yy / h - cy) / ry) ** 2)
    return np.clip(1 - d, 0, 1) ** (1 / power)


def scurve(x, k):
    return np.clip(x + k * x * (1 - x) * (2 * x - 1) * 2, 0, 1)


def sat_mix(x, s):
    y = luma(x)[..., None]
    return np.clip(y + (x - y) * s, 0, 1)


def grade(x, p):
    """x: (H, W, 3) float32 0..1 ; p: parámetros del clip"""
    h, w, _ = x.shape
    # 1) igualar
    x = np.clip(x * np.array(p.get('wb', (1, 1, 1)), np.float32) * p.get('exp', 1.0), 0, 1)
    y = luma(x); hue, sat = hue_deg(x)
    # 2) máscara de luz: producto (cálido y/o claro no azul) + caída radial amplia
    warm = smooth(hue, p.get('h0', 12), p.get('h1', 24)) * (1 - smooth(hue, 62, 78)) * smooth(sat, 0.14, 0.32)
    subj = warm
    if p.get('bright_key'):
        subj = np.maximum(subj, smooth(y, 0.50, 0.80) * smooth(x[..., 0] - x[..., 2], -0.12, 0.02))
    m_s = blur(subj, p.get('mblur', 0.05))
    cx, cy, rx, ry = p.get('pool', (0.5, 0.55, 0.8, 0.7))
    m_r = radial(h, w, cx, cy, rx, ry)
    M = np.clip(p.get('k_subj', 1.0) * m_s + p.get('k_rad', 0.6) * m_r, 0, 1)
    M = blur(M, 0.02)[..., None]
    # 3) ambiente: oscuro, negros neutros con un toque azulado
    amb = x * p.get('amb', 0.30)
    mb = smooth(hue, 185, 215) * (1 - smooth(hue, 255, 275)) * smooth(sat, 0.25, 0.5)   # el azul de la máquina
    amb = amb * (1 - mb[..., None] * p.get('blue_dark', 0.0))
    amb = sat_mix(amb, 0.85)
    amb = amb + np.array([-0.004, 0.0, 0.014], np.float32) * ((1 - luma(amb)) ** 3)[..., None]
    # 4) zona iluminada: contraste, medios cobre/ámbar, luces doradas; poco calor sobre colores ya saturados
    lit = x * p.get('lit', 0.95)
    yl = luma(lit)[..., None]
    mult = np.array([1.02, 0.985, 0.93], np.float32) * (1 - yl) + np.array([1.10, 1.0, 0.76], np.float32) * yl
    protect = (1 - 0.8 * np.clip(sat, 0, 1))[..., None] * p.get('warm', 1.0)
    lit = np.clip(lit * (1 + (mult - 1) * protect), 0, 1)
    # 5) saturación selectiva: rojos y naranjas suben un poco, el resto queda natural
    red_orange = (1 - smooth(hue, 30, 48)) * (hue < 180) + smooth(hue, 335, 355) * (hue > 180)
    boost = (1 + p.get('sat_warm', 0.06) * red_orange)[..., None]
    yl2 = luma(lit)[..., None]
    lit = np.clip(yl2 + (lit - yl2) * boost * p.get('lit_sat', 1.0), 0, 1)
    out = amb * (1 - M) + lit * M
    # contraste y negros: punto negro bajo, curva en S, sin levantar sombras
    b0 = p.get('black', 0.018)
    out = np.clip((out - b0) / (1 - b0), 0, 1)
    out = scurve(out, p.get('contrast', 0.35))
    return out.astype(np.float32)
