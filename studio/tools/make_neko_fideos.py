#!/usr/bin/env python3
"""Plantilla del reel de Neko Ramen «Fideos hechos en casa» (montaje B).
El video y el audio salen de make_neko_base.py (material del cliente, fuera del repositorio): en Studio se importan
neko-B.mp4 (medios) y neko-B-audio.wav (botón de audio). Aquí solo van los textos, con la identidad de Neko:
Anton (títulos, mostaza), Raleway (kicker y textos secundarios, crema), negro cálido para el degradado de lectura.
Uso: python3 make_neko_fideos.py neko-B-tiempos.json"""
import json, sys, itertools, os
T = json.load(open(sys.argv[1])); DUR = T['total']
MOSTAZA, CREMA, NEGRO = '#D9A441', '#E7DFD2', '#161314'
n = itertools.count(1); layers = []
def L(type, name, start, end, x, y, w, h, **k):
    d = dict(id=f"l{next(n):02d}", type=type, name=name, start=round(start, 2), end=round(end, 2), x=x, y=y, w=w, h=h, rot=0, opacity=1,
             animIn='none', animOut='none', animDur=0.45)
    d.update(k); layers.append(d); return d

L('image', 'Montaje (neko-B.mp4)', 0, DUR, 540, 960, 1080, 1920, asset='neko-B.mp4', fit='cover', placeholder='Importa neko-B.mp4')

def bloque(nombre, a, z, kicker, titulo, ky, ty, th, fondo=None, fade_out=True, anim=0.35, retraso=0.15, ksize=62, tsize=None):
    """Kicker (Raleway, crema) + título (Anton, mostaza). Entradas suaves: solo fundido.
    fondo: None | ('abajo'|'arriba', y, alpha) degradado de lectura | ('halo', cx, cy, w, h, opacidad) sombra suave y local detrás del texto."""
    out = 'fade' if fade_out else 'none'
    if fondo and fondo[0] in ('abajo', 'arriba'):
        _, sy, al = fondo
        if fondo[0] == 'arriba':
            L('shape', f'Degradado · {nombre}', a, z, 540, sy / 2, 1080, sy, kind='scrim', color=NEGRO, alpha=al, dir='up', animIn='fade', animOut=out, animDur=anim)
        else:
            L('shape', f'Degradado · {nombre}', a, z, 540, (sy + 1920) / 2, 1080, 1920 - sy, kind='scrim', color=NEGRO, alpha=al, dir='down', animIn='fade', animOut=out, animDur=anim)
    elif fondo and fondo[0] == 'halo':
        _, cx, cy, w, h, op = fondo
        L('shape', f'Sombra suave · {nombre}', a, z, cx, cy, w, h, kind='halo', color=NEGRO, opacity=op, animIn='fade', animOut=out, animDur=anim)
    L('text', f'Kicker · {nombre}', a, z, 540, ky, 912, 84, text=kicker, font='raleway', weight=600, caps=False, size=ksize, color=CREMA, align='left',
      lh=1.1, animIn='fade', animOut=out, animDur=anim)
    L('text', f'Título · {nombre}', a + retraso, z, 540, ty, 912, th, text=titulo, font='anton', size=tsize or (124 if '\n' in titulo else 128), color=MOSTAZA, accent=MOSTAZA, align='left',
      lh=1.14 if '\n' in titulo else 1.0, animIn='fade', animOut=out, animDur=anim)

# 1) gancho sobre los fideos creciendo: entra en el primer fotograma (fundido de 0,2 s) y se retira antes de que la cortina clara llene el cuadro
bloque('Gancho', 0.0, 2.6, '¿Sabías que hacemos', 'los fideos\naquí mismo?', 1195, 1400, 283, fondo=('abajo', 1060, 0.72), anim=0.2, retraso=0.05)
# 2) preparación: sobre la zona oscura de la maquinaria (abajo a la izquierda), con una sombra suave y local, sin degradados grandes
bloque('Receta', T['B'] + 0.25, T['C'] - 0.05, 'Con nuestra', 'propia\nreceta.', 995, 1163, 250, fondo=('halo', 300, 1130, 860, 580, 1.0), ksize=56, tsize=108)
# 3) cierre sobre el ramen terminado: se retira en el segundo 11 y los últimos 2 s quedan solo con los fideos
bloque('Cierre', T['palillos_pleno'] + 0.2, 11.0, 'De nuestra cocina', 'a tu bowl.', 290, 400, 140, fondo=('arriba', 640, 0.62))

proj = dict(template='neko-fideos', rev=1, name='Reel · Fideos hechos en casa (Neko Ramen)', width=1080, height=1920, fps=30, duration=DUR,
            background=NEGRO, voiceover='¿Sabías que hacemos los fideos aquí mismo?\n\nCon nuestra propia receta.\n\nDe nuestra cocina a tu bowl.', layers=layers)
json.dump(proj, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'projects', 'neko-fideos.json'), 'w'), ensure_ascii=False, indent=1)
print(len(layers), 'capas · duración', DUR)
