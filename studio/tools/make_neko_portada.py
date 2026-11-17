#!/usr/bin/env python3
"""Portada del reel de Neko Ramen con la fotografía cenital real (fuera del repositorio) y la composición editorial de los carruseles:
kicker en Raleway crema + título en Anton mostaza + logo chico. El texto queda dentro de la zona visible de la cuadrícula del perfil
(recorte 3:4 centrado: entre y=240 e y=1680 en 1080x1920).
Uso: python3 make_neko_portada.py --photo foto.jpg --out portada.png [--titulo "nuestros propios\\nfideos?"] """
import argparse, base64, os, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ST = os.path.join(HERE, '..')
ap = argparse.ArgumentParser(); ap.add_argument('--photo', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--kicker', default='¿Sabías que hacemos'); ap.add_argument('--titulo', default='nuestros propios\nfideos?')
a = ap.parse_args()
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
html = f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:Anton;src:url(data:font/woff2;base64,{b64(os.path.join(ST,'fonts/anton-latin-400-normal.woff2'))})}}
@font-face{{font-family:Raleway;font-weight:600;src:url(data:font/woff2;base64,{b64(os.path.join(ST,'fonts/raleway-latin-600-normal.woff2'))})}}
html,body{{margin:0;background:#161314}} #c{{position:relative;width:1080px;height:1920px;overflow:hidden}}
#ph{{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;object-position:50% 50%}}
#sc{{position:absolute;left:0;top:0;width:1080px;height:760px;background:linear-gradient(#161314cc,#16131400)}}
#k{{position:absolute;left:84px;top:262px;font:600 60px Raleway;color:#E7DFD2}}
#t{{position:absolute;left:84px;top:340px;font:400 138px/1.1 Anton;color:#D9A441;text-transform:uppercase;white-space:pre}}
#lg{{position:absolute;right:84px;top:1450px;width:150px}}
</style><div id=c><img id=ph src="data:image/jpeg;base64,{b64(a.photo)}"><div id=sc></div><div id=k>{a.kicker}</div><div id=t>{a.titulo}</div>
<img id=lg src="data:image/png;base64,{b64(os.path.join(ST,'assets/neko/logo-neko-crema.png'))}"></div>"""
tmp = os.path.join(tempfile.mkdtemp(), 'p.html'); open(tmp, 'w', encoding='utf-8').write(html)
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{tmp}');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);await p.locator('#c').screenshot({{path:{a.out!r}}});await b.close()}})()"""
open(tmp + '.js', 'w').write(js)
subprocess.check_call(['node', tmp + '.js'], env=dict(os.environ, NODE_PATH=subprocess.check_output(['npm', 'root', '-g']).decode().strip()))
print(a.out)
