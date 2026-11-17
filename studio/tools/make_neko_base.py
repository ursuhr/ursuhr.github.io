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

ap = argparse.ArgumentParser()
ap.add_argument('--src', required=True, help='carpeta con IMG_8181/8182/8184/8186_720p.mp4')
ap.add_argument('--photo', required=True, help='fotografía cenital (jpg)')
ap.add_argument('--sticks', required=True, help='video de los palillos levantando los fideos (IMG_4716)')
ap.add_argument('--music', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--no-machine-audio', action='store_true', help='mezcla solo música + palillos')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
f = lambda n: os.path.join(a.src, f'IMG_{n}_720p.mp4')
FPS = 30

# ---- tiempos de salida (s) ----
# Segmentos y fuente: (archivo, desde, duración). El gancho (A) junta el crecimiento de la cortina de fideos
# con el barrido de corte del mismo video, que hace de transición hacia la preparación.
A1 = (f('8186'), 0.00, 1.80); A2 = (f('8186'), 5.10, 1.30)       # 3,1 s
B = (f('8181'), 8.30, 3.00)
C = (f('8182'), 2.40, 1.70)
D = (f('8184'), 2.90, 1.70)
E_DUR = 2.10
F = (a.sticks, 0.00, 4.90)
XF_AB, XF_EF = 0.2, 0.3
A_DUR = A1[2] + A2[2]
P_DUR = B[2] + C[2] + D[2] + E_DUR
T_AB = A_DUR - XF_AB                 # inicio de B en pantalla
T_END_P = A_DUR + P_DUR - XF_AB      # fin del bloque B..E
T_EF = T_END_P - XF_EF               # inicio del palillos
TOTAL = round(T_END_P + F[2] - XF_EF, 2)

up = f'scale=-2:1920:flags=lanczos,crop=1080:1920,fps={FPS},setsar=1'
grade = 'eq=contrast=1.04:saturation=1.05'
# el azul de la máquina (8186) baja en saturación y luminosidad, sin tocar el dorado de los fideos
blue = 'huesaturation=colors=c+b:saturation=-0.9:intensity=-0.4:strength=2'

def seg(idx, src, ss, dur, extra=''):
    return f"[{idx}:v]trim=start={ss}:duration={dur},setpts=PTS-STARTPTS,{up}{(','+extra) if extra else ''},{grade}[v{idx}]"

# foto cenital: recorte 9:16 centrado en el bowl, zoom suave hacia los fideos del centro
ZF = int(E_DUR * FPS)
tx, ty = 593 * 2, 1010 * 2       # fideos, en coordenadas de la foto ya recortada y duplicada
photo = (f"[4:v]crop=1125:2000:187:0,scale=2250:4000:flags=lanczos,"
         f"zoompan=z='1+0.5*(1-cos(PI*on/{ZF}))/2':x='clip({tx}-iw/zoom/2,0,iw-iw/zoom)':y='clip({ty}-ih/zoom/2,0,ih-ih/zoom)'"
         f":d={ZF}:s=1080x1920:fps={FPS},setsar=1,vignette=PI/7,{grade}[v4]")

fc = ';'.join([
    seg(0, *A1, extra=blue), seg(1, *A2, extra=blue),
    seg(2, *B), seg(3, *C), seg(5, *D),
    photo,
    seg(6, *F),
    "[v0][v1]concat=n=2:v=1:a=0,settb=1/30,fps=30[vA]",
    "[v2][v3][v5][v4]concat=n=4:v=1:a=0,settb=1/30,fps=30[vP]",
    f"[vA][vP]xfade=transition=fade:duration={XF_AB}:offset={A_DUR-XF_AB:.2f}[vAP]",
    f"[vAP][v6]xfade=transition=fade:duration={XF_EF}:offset={T_EF:.2f},settb=1/30,format=yuv420p[vout]",
])
# entradas: 0 y 1 = 8186 (dos tramos), 2 = 8181, 3 = 8182, 4 = foto, 5 = 8184, 6 = palillos
inputs = [A1[0], A2[0], B[0], C[0], None, D[0], F[0]]
cmd = ['ffmpeg', '-v', 'error', '-y']
for i, p in enumerate(inputs):
    cmd += (['-loop', '1', '-framerate', str(FPS), '-t', str(E_DUR + 0.5), '-i', a.photo] if p is None else ['-i', p])
cmd += ['-filter_complex', fc, '-map', '[vout]', '-an', '-t', str(TOTAL), '-c:v', 'libx264', '-crf', '14', '-preset', 'slow', '-pix_fmt', 'yuv420p',
        os.path.join(a.out, 'neko-base.mp4')]
print('video…'); subprocess.check_call(cmd)

# ---- audio ----
# Música suave de fondo + sonido de la máquina durante el gancho (opcional) + el sonido real de los fideos con palillos.
parts, labels = [], []
ai = ['-i', a.music, '-i', F[0]]
parts.append(f"[0:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,volume=0.55,afade=t=in:d=1.2,afade=t=out:st={TOTAL-1.8:.2f}:d=1.8[mus]"); labels.append('[mus]')
parts.append(f"[1:a]atrim=0:{F[2]},asetpts=PTS-STARTPTS,highpass=f=80,volume=1.0,afade=t=in:d=0.25,afade=t=out:st={F[2]-0.6:.2f}:d=0.6,adelay={int(T_EF*1000)}|{int(T_EF*1000)}[stk]"); labels.append('[stk]')
if not a.no_machine_audio:
    ai += ['-i', A1[0]]
    parts.append(f"[2:a]atrim=start={A1[1]}:duration={A1[2]},asetpts=PTS-STARTPTS,highpass=f=120,lowpass=f=6000,volume=0.5,afade=t=in:d=0.15[m1]")
    parts.append(f"[2:a]atrim=start={A2[1]}:duration={A2[2]},asetpts=PTS-STARTPTS,highpass=f=120,lowpass=f=6000,volume=0.5,afade=t=out:d=0.25,adelay={int(A1[2]*1000)}|{int(A1[2]*1000)}[m2]")
    labels += ['[m1]', '[m2]']
parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest,loudnorm=I=-16:TP=-1.5:LRA=9,atrim=0:{TOTAL}[aout]")
cmd = ['ffmpeg', '-v', 'error', '-y'] + ai + ['-filter_complex', ';'.join(parts), '-map', '[aout]', '-ar', '48000', '-ac', '2', '-c:a', 'aac', '-b:a', '192k',
       os.path.join(a.out, 'neko-audio.m4a')]
print('audio…'); subprocess.check_call(cmd)
print(f'listo · {TOTAL} s · inicio de cada bloque: B {T_AB:.1f}  C {T_AB+B[2]:.1f}  D {T_AB+B[2]+C[2]:.1f}  foto {T_AB+B[2]+C[2]+D[2]:.1f}  palillos {T_EF:.1f}')
