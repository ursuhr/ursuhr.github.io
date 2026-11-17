#!/usr/bin/env python3
"""Reel de los fideos de Neko Ramen: montaje base (sin textos) con ffmpeg.

Los videos y fotos de Neko NO viven en el repositorio (material del cliente). Este script los lee desde
carpetas locales y deja en --out dos archivos que Studio importa como medios:
  neko-base.mp4   video 1080x1920 a 30 fps, 16 s, sin audio (color corregido, cortes y zoom de la foto)
  neko-audio.m4a  mezcla de música suave + sonidos originales

Uso:
  python3 make_neko_base.py --src studio/assets/neko --photo cenital.jpg --sticks IMG_4716.mov \
      --music studio/assets/sfx/musica-2.mp3 --out /ruta/fuera/del/repo
"""
import argparse, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import neko_lr

ap = argparse.ArgumentParser()
ap.add_argument('--src', required=True, help='carpeta con IMG_8181/8182/8184/8186_720p.mp4')
ap.add_argument('--photo', required=True, help='fotografía cenital (jpg)')
ap.add_argument('--sticks', required=True, help='video de los palillos levantando los fideos (IMG_4716)')
ap.add_argument('--music', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--version', choices=['A', 'B'], default='B', help='A con la foto cenital, B pasa directo de la preparación a los palillos')
ap.add_argument('--name', default='neko-base')
ap.add_argument('--zoom', type=float, default=1.10, help='encuadre más cerrado del ramen final (1 = sin zoom)')
ap.add_argument('--zx', type=float, default=0.40); ap.add_argument('--zy', type=float, default=0.75)
ap.add_argument('--bpm', type=float, help='sincroniza los cortes con el pulso de la música (A 6 tiempos, B 6, C 3, D 3)')
ap.add_argument('--music-start', type=float, default=0.0, help='segundo de la pista donde cae un tiempo; el reel parte ahí')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
f = lambda n: os.path.join(a.src, f'IMG_{n}_720p.mp4')
FPS = 30

# ---- tiempos de salida (s) ----
# Segmentos y fuente: (archivo, desde, duración). El gancho (A) junta el crecimiento de la cortina de fideos
# con el barrido de corte del mismo video, que hace de transición hacia la preparación.
A1 = (f('8186'), 0.00, 2.20); A2 = (f('8186'), 5.55, 0.85)       # 3,05 s: crecimiento + barrido de corte
B = (f('8181'), 8.30, 3.00)
C = (f('8182'), 2.40, 1.70)
D = (f('8184'), 2.90, 1.70)
if a.bpm:   # cortes sobre tiempos enteros: A->B (fundido) en el tiempo 6, B->C en el 12, C->D en el 15, D->palillos en el 18
    bt = 60 / a.bpm
    A2 = (f('8186'), 5.55, 0.85); A1 = (f('8186'), 0.00, 6 * bt + 0.1 - 0.85)
    B = (f('8181'), 8.30, 6 * bt + 0.1); C = (f('8182'), 2.30, 3 * bt); D = (f('8184'), 2.90, 3 * bt + 0.15)
E_DUR = 2.10 if a.version == 'A' else 0.0
F = (a.sticks, 0.00, 4.50)               # termina en el segundo 4,5 del clip, sin congelar el fotograma
XF_AB, XF_EF = 0.2, 0.3
A_DUR = A1[2] + A2[2]
P_DUR = B[2] + C[2] + D[2] + E_DUR
T_AB = A_DUR - XF_AB                 # inicio de B en pantalla
T_END_P = A_DUR + P_DUR - XF_AB      # fin del bloque B..E
T_EF = T_END_P - XF_EF               # inicio del palillos
TOTAL = round(T_END_P + F[2] - XF_EF, 2)

up = f'scale=-2:1920:flags=lanczos,crop=1080:1920,fps={FPS},setsar=1'

LUTS = neko_lr.luts(os.path.join(a.out, 'luts'))   # corrección tipo Lightroom por clip (neko_lr_valores.json)
def seg_zoom(idx, ss, dur, key):
    zh = int(round(1920 * a.zoom / 2) * 2); zw = int(round(1080 * a.zoom / 2) * 2)
    x = int((zw - 1080) * a.zx); y = int((zh - 1920) * a.zy)
    return f"[{idx}:v]trim=start={ss}:duration={dur},setpts=PTS-STARTPTS,{neko_lr.HLG_A_SDR},scale={zw}:{zh}:flags=lanczos,crop=1080:1920:{x}:{y},fps={FPS},setsar=1,lut3d=file={LUTS['ramen']}:interp=tetrahedral[v{idx}]"
def seg(idx, src, ss, dur, key):
    return f"[{idx}:v]trim=start={ss}:duration={dur},setpts=PTS-STARTPTS,{up},lut3d=file={LUTS[key]}:interp=tetrahedral[v{idx}]"

# foto cenital: recorte 9:16 centrado en el bowl, zoom suave hacia los fideos del centro
ZF = max(1, int((E_DUR or 2.1) * FPS))
tx, ty = 593 * 2, 1010 * 2       # fideos, en coordenadas de la foto ya recortada y duplicada
photo = (f"[4:v]crop=1125:2000:187:0,scale=2250:4000:flags=lanczos,"
         f"zoompan=z='1+0.5*(1-cos(PI*on/{ZF}))/2':x='clip({tx}-iw/zoom/2,0,iw-iw/zoom)':y='clip({ty}-ih/zoom/2,0,ih-ih/zoom)'"
         f":d={ZF}:s=1080x1920:fps={FPS},setsar=1[v4]")

fc = ';'.join([
    seg(0, *A1, '8186'), seg(1, *A2, '8186'),
    seg(2, *B, '8181'), seg(3, *C, '8182'), seg(5, *D, '8184'),
    *([photo] if a.version == 'A' else []),
    seg_zoom(6, F[1], F[2], 'ramen'),
    "[v0][v1]concat=n=2:v=1:a=0,settb=1/30,fps=30[vA]",
    ("[v2][v3][v5][v4]concat=n=4" if a.version == 'A' else "[v2][v3][v5]concat=n=3") + ":v=1:a=0,settb=1/30,fps=30[vP]",
    f"[vA][vP]xfade=transition=fade:duration={XF_AB}:offset={A_DUR-XF_AB:.2f}[vAP]",
    f"[vAP][v6]xfade=transition=fade:duration={XF_EF}:offset={T_EF:.2f},settb=1/30,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[vout]",
])
# entradas: 0 y 1 = 8186 (dos tramos), 2 = 8181, 3 = 8182, 4 = foto, 5 = 8184, 6 = palillos
inputs = [A1[0], A2[0], B[0], C[0], None, D[0], F[0]]
cmd = ['ffmpeg', '-v', 'error', '-y']
for i, p in enumerate(inputs):
    cmd += (['-loop', '1', '-framerate', str(FPS), '-t', str((E_DUR or 2.1) + 0.5), '-i', a.photo] if p is None else ['-i', p])
cmd += ['-filter_complex', fc, '-map', '[vout]', '-an', '-t', str(TOTAL), '-c:v', 'libx264', '-crf', '14', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
        os.path.join(a.out, a.name + '.mp4')]
print('video…'); subprocess.check_call(cmd)

# ---- audio ----
# Solo música instrumental. Los audios originales de los videos se descartan por completo (sin voces ni ruido de máquina).
mus = (f"[0:a]atrim=start={a.music_start}:duration={TOTAL + 0.05},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={TOTAL-1.4:.2f}:d=1.4,"
       f"loudnorm=I=-15:TP=-1.5:LRA=9,atrim=0:{TOTAL}[aout]")
cmd = ['ffmpeg', '-v', 'error', '-y', '-i', a.music, '-filter_complex', mus, '-map', '[aout]', '-ar', '48000', '-ac', '2', '-c:a', 'aac', '-b:a', '192k',
       os.path.join(a.out, a.name + '-audio.m4a')]
print('audio…'); subprocess.check_call(cmd)
subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(a.out, a.name + '-audio.m4a'), '-c:a', 'pcm_s16le', os.path.join(a.out, a.name + '-audio.wav')])
import json
tiempos = dict(total=TOTAL, A_fin=round(T_AB + XF_AB, 2), B=round(T_AB, 2), C=round(T_AB + B[2], 2), D=round(T_AB + B[2] + C[2], 2), palillos=round(T_EF, 2), palillos_pleno=round(T_EF + XF_EF, 2), foto=a.version == 'A')
json.dump(tiempos, open(os.path.join(a.out, a.name + '-tiempos.json'), 'w'), indent=1)
print(f'listo · {TOTAL} s · inicio de cada bloque: B {T_AB:.1f}  C {T_AB+B[2]:.1f}  D {T_AB+B[2]+C[2]:.1f}  foto {T_AB+B[2]+C[2]+D[2]:.1f}  palillos {T_EF:.1f}')
