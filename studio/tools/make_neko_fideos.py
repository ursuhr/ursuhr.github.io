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

def bloque(nombre, a, z, kicker, titulo, ky, ty, th, scrim_y=1130, alpha=0.55, fade_out=True, arriba=False):
    """degradado de lectura + kicker (Raleway, crema) + título (Anton, mostaza). Entradas suaves: solo fundido."""
    out = 'fade' if fade_out else 'none'
    if arriba:   # degradado desde el borde superior hasta scrim_y
        L('shape', f'Degradado · {nombre}', a - 0.1, z, 540, scrim_y / 2, 1080, scrim_y, kind='scrim', color=NEGRO, alpha=alpha, dir='up', animIn='fade', animOut=out, animDur=0.5)
    else:
        L('shape', f'Degradado · {nombre}', a - 0.1, z, 540, (scrim_y + 1920) / 2, 1080, 1920 - scrim_y, kind='scrim', color=NEGRO, alpha=alpha, dir='down', animIn='fade', animOut=out, animDur=0.5)
    L('text', f'Kicker · {nombre}', a + 0.05, z, 540, ky, 912, 76, text=kicker, font='raleway', weight=600, caps=False, size=52, color=CREMA, align='left',
      lh=1.1, animIn='fade', animOut=out, animDur=0.5)
    L('text', f'Título · {nombre}', a + 0.2, z, 540, ty, 912, th, text=titulo, font='anton', size=124 if '\n' in titulo else 128, color=MOSTAZA, accent=MOSTAZA, align='left',
      lh=1.14 if '\n' in titulo else 1.0, animIn='fade', animOut=out, animDur=0.5)

# 1) gancho sobre los fideos creciendo; se retira antes de que la cortina clara llene el cuadro
bloque('Gancho', 0.15, 2.55, '¿Sabías que hacemos', 'los fideos\naquí mismo?', 1215, 1410, 283, scrim_y=1080, alpha=0.72)
# 2) preparación
bloque('Receta', T['B'] + 0.35, T['C'] - 0.05, 'Con nuestra', 'propia receta.', 1370, 1465, 140, scrim_y=1150, alpha=0.72)
# 3) cierre sobre el ramen terminado; se queda hasta el final del reel
bloque('Cierre', T['palillos_pleno'] + 0.2, DUR, 'De nuestra cocina', 'a tu bowl.', 290, 400, 140, scrim_y=640, alpha=0.62, fade_out=False, arriba=True)

proj = dict(template='neko-fideos', rev=1, name='Reel · Fideos hechos en casa (Neko Ramen)', width=1080, height=1920, fps=30, duration=DUR,
            background=NEGRO, voiceover='¿Sabías que hacemos los fideos aquí mismo?\n\nCon nuestra propia receta.\n\nDe nuestra cocina a tu bowl.', layers=layers)
json.dump(proj, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'projects', 'neko-fideos.json'), 'w'), ensure_ascii=False, indent=1)
print(len(layers), 'capas · duración', DUR)
