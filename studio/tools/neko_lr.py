#!/usr/bin/env python3
"""Corrección de color con controles equivalentes a Lightroom, para el reel de fideos de Neko Ramen.

Los valores por clip viven en neko_lr_valores.json y se editan uno por uno. Este script:
  - traduce esa escala (-100..+100, exposición en EV) a operaciones reales con las constantes de "calibracion"
  - genera una LUT 3D (.cube) por clip, que ffmpeg aplica con el filtro lut3d (mismo resultado en la hoja comparativa y en el render)
Es una corrección global: sin viñeta, sin máscaras, sin luz localizada, sin glow, sin grano y sin filtro cálido adicional.

Orden de las operaciones (como el panel Básico de Lightroom): exposición > contraste > iluminaciones > sombras > blancos y negros >
temperatura > intensidad > saturación > HSL. Las operaciones de tono actúan sobre la luminancia y conservan el color (proporción RGB).

Uso:  python3 neko_lr.py --out carpeta_de_luts        genera 8186.cube, 8181.cube, ... y imprime los valores efectivos
"""
import argparse, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VALORES = os.path.join(HERE, 'neko_lr_valores.json')
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)
# centros de banda HSL (grados) y semiancho de cada una
BANDAS = {'rojo': (0, 30), 'naranja': (30, 30), 'amarillo': (60, 30), 'verde': (120, 40), 'aqua': (180, 40), 'azul': (240, 40), 'morado': (275, 35), 'magenta': (320, 35)}


def cargar():
    with open(VALORES, encoding='utf-8') as f:
        return json.load(f)


def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def hue_sat(x):
    mx = x.max(-1); mn = x.min(-1); d = mx - mn + 1e-9
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, d / (mx + 1e-9)


def peso_banda(h, centro, semi):
    d = np.abs((h - centro + 180) % 360 - 180)
    return np.clip(1 - d / semi, 0, 1)


def aplicar(rgb, v, cal):
    """rgb: (N, 3) float32 en 0..1 (sRGB con gamma); v: valores del clip; cal: constantes de calibración"""
    x = np.clip(rgb, 0, 1).astype(np.float32)
    # exposición: ganancia en luz lineal
    ev = v.get('exposicion', 0.0)
    if ev:
        x = np.clip((x ** 2.2) * (2.0 ** ev), 0, None) ** (1 / 2.2)
    Y0 = x @ LUMA
    y = np.clip(Y0, 0, 1)
    # contraste: curva en S alrededor del gris medio
    k = v.get('contraste', 0) / 100 * cal['contraste_k']
    y = y + k * y * (1 - y) * (2 * y - 1) * 2
    # iluminaciones: actúan en el tercio alto; sombras: en el tercio bajo
    y = y + v.get('iluminaciones', 0) / 100 * cal['iluminaciones_amp'] * smooth(y, 0.45, 0.95)
    y = y + v.get('sombras', 0) / 100 * cal['sombras_amp'] * (1 - smooth(y, 0.10, 0.55))
    # negros y blancos: mueven los extremos de la curva
    b0 = -v.get('negros', 0) * cal['negros_k']
    w1 = 1 - v.get('blancos', 0) * cal['blancos_k']
    y = np.clip((y - b0) / (w1 - b0), 0, 1.0)
    # el color conserva su proporción RGB al cambiar la luminancia
    x = x * ((y + 0.003) / (Y0 + 0.003))[..., None]
    mx = x.max(-1, keepdims=True)
    x = x / np.maximum(1, mx)
    # temperatura: ganancia en rojo y azul que no cambia la luminancia
    t = v.get('temperatura', 0)
    if t:
        g = np.array([1 + cal['temperatura_r'] * t, 1.0, 1 - cal['temperatura_b'] * t], np.float32)
        g = g / (g @ LUMA)
        x = np.clip(x * g, 0, 1)
    # intensidad (vibrance): más color a lo poco saturado y poca ayuda a la piel (naranja)
    h, s = hue_sat(x)
    Y = (x @ LUMA)[..., None]
    c = x - Y
    skin = peso_banda(h, 30, 25)
    vib = 1 + v.get('intensidad', 0) / 100 * cal['intensidad_k'] * ((1 - s) ** 1.5) * (1 - 0.5 * skin)
    sat = 1 + v.get('saturacion', 0) / 100
    c = c * (vib * sat)[..., None]
    x = np.clip(Y + c, 0, 1)
    # HSL por banda: saturación (escala del color) y luminancia (multiplica los canales)
    hsl = v.get('hsl', {})
    if hsl:
        h, s = hue_sat(x)
        for nombre, aj in hsl.items():
            centro, semi = BANDAS[nombre]
            w = peso_banda(h, centro, semi) * smooth(s, 0.06, 0.30)
            Y = (x @ LUMA)[..., None]
            x = Y + (x - Y) * (1 + aj.get('sat', 0) / 100 * cal['hsl_sat'] * w)[..., None]
            x = x * (1 + aj.get('lum', 0) / 100 * cal['hsl_lum'] * w)[..., None]
    return np.clip(x, 0, 1)


def escribir_cube(ruta, v, cal, n=65):
    g = np.linspace(0, 1, n, dtype=np.float32)
    B, G, R = np.meshgrid(g, g, g, indexing='ij')           # el rojo varía más rápido
    rgb = np.stack([R.ravel(), G.ravel(), B.ravel()], -1)
    out = aplicar(rgb, v, cal)
    with open(ruta, 'w') as f:
        f.write(f'TITLE "Neko Ramen"\nLUT_3D_SIZE {n}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        np.savetxt(f, out, fmt='%.6f')


def luts(destino):
    d = cargar(); os.makedirs(destino, exist_ok=True); rutas = {}
    for clip, v in d['clips'].items():
        rutas[clip] = os.path.join(destino, f'{clip}.cube'); escribir_cube(rutas[clip], v, d['calibracion'])
    return rutas


def texto_valores(clip, d=None):
    d = d or cargar(); v = d['clips'][clip]
    L = [f"Exposición {v['exposicion']:+.2f} EV", f"Contraste {v['contraste']:+d}", f"Iluminaciones {v['iluminaciones']:+d}", f"Sombras {v['sombras']:+d}",
         f"Blancos {v['blancos']:+d}", f"Negros {v['negros']:+d}", f"Temperatura {v['temperatura']:+d}", f"Intensidad {v['intensidad']:+d}", f"Saturación {v['saturacion']:+d}"]
    for n, aj in v.get('hsl', {}).items():
        L.append(f"HSL {n}: sat {aj.get('sat', 0):+d}, lum {aj.get('lum', 0):+d}")
    return L


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
    d = cargar(); print(json.dumps({'efectos': d['efectos'], 'calibracion': d['calibracion']}, ensure_ascii=False, indent=1))
    for c in d['clips']: print(c, '·', ' | '.join(texto_valores(c, d)))
    print(luts(a.out))
