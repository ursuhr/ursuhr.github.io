import json, itertools, subprocess
IV,BK,CO,SK='#F5F1E8','#0B0B0B','#FF6BA7','#6EC6FF'
ROOT='/home/user/ursuhr.github.io/studio/'
n=itertools.count(1); layers=[]
def L(type,name,start,end,x,y,w,h=100,**k):
    d=dict(id=f"l{next(n):02d}",type=type,name=name,start=round(start,2),end=round(end,2),x=x,y=y,w=w,h=h,rot=0,opacity=1,animIn='none',animOut='none',animDur=0.45)
    d.update(k); layers.append(d); return d

DUR=41.3
# ---- tiempos REALES de la voz clonada (silencedetect -38dB d=0.18 sobre voz_seo.mp3, 40,28 s) ----
P=[(0.0,2.0,'Esta página no subió en Google.'),(2.36,3.04,'Y aun así,'),(3.24,4.84,'el doble de gente hizo clic.'),
 (5.30,7.34,'Es de una clínica estética de Antofagasta.'),(7.79,10.49,'El tratamiento se llamaba toxina botulínica.'),
 (10.86,11.77,'Es el nombre técnico.'),(12.27,13.91,'Pero casi nadie lo busca así.'),
 (14.43,17.35,'En octubre lo cambié por botox en Antofagasta,'),(17.62,18.90,'que es como lo escribe la gente.'),
 (19.53,22.02,'La página siguió prácticamente en el mismo lugar.'),(22.51,27.00,'Pero el porcentaje de clics pasó de cinco coma seis a diez coma nueve por ciento.'),
 (27.42,27.90,'Ojo,'),(28.10,30.48,'es un solo mes y con poco volumen,'),(30.68,31.78,'así que lo sigo midiendo.'),
 (32.44,34.69,'A veces no tienes que subir en Google.'),(35.03,37.09,'Basta con hablar como habla tu cliente.'),(37.59,40.28,'Escríbeme y te cuento cómo te está mostrando a ti.')]

def halo(name,a,z,x,y,size,op,**k):
    L('shape',name,a,z,x,y,size,size,kind='halo',color=CO,color2=SK,opacity=op,animIn='fade',animOut='fade',animDur=1.0,**k)
def title(name,a,z,y,text,size,h,**k):
    d=dict(animIn='rise',animOut='fade',animDur=0.35,accent=CO); d.update(k)
    L('text',name,a,z,520,y,840,h,text=text,font='title',size=size,color=IV,align='left',lh=1.05,**d)
def body(name,a,z,y,text,size,h=60,color=IV,bold=False,**k):
    d=dict(animIn='fade',animOut='fade',animDur=0.3); d.update(k)
    L('text',name,a,z,520,y,840,h,text=text,font='body',size=size,bold=bold,color=color,align='left',lh=1.25,**d)
def pill(name,a,z,cx,y,w,h,label,fill,fg,size,**k):
    d=dict(animIn='pop',animOut='fade'); d.update(k)
    L('shape',name,a,z,cx,y,w,h,kind='pill',color=fill,label=label,labelColor=fg,labelSize=size,**d)

# ---- halo coral + azul desde la esquina inferior derecha, intensidad variable, movimiento lento ----
halo('Halo portada',0,5.4,900,1800,1500,0.5,move=[[0,940,1840],[5.4,880,1760]],scaleKf=[[0,0.9],[5.4,1.05]])
halo('Halo fondo',5.0,27.7,900,1800,1500,0.2,move=[[5,900,1800],[16,860,1770],[27.7,920,1810]],scaleKf=[[5,1],[16,1.08],[27.7,1]])
halo('Halo calma',27.3,32.9,900,1800,1400,0.1,move=[[27.3,900,1800],[32.9,920,1820]])
halo('Halo cierre',32.3,DUR,820,1700,1900,0.5,move=[[32.3,900,1850],[DUR,760,1560]],scaleKf=[[32.3,0.85],[37,1.2],[DUR,1.35]])

# ---- 1. Hook (0:00-0:05) ----
title('Hook 1',0.05,5.0,600,'Mismo lugar\nen Google.',100,240)
title('Hook 2',2.4,5.0,950,'El *doble*\nde gente\nhizo clic.',100,330)

# ---- 2-4. Buscador y resultado (una capa) ----
S=dict(query='botox antofagasta',typeAt=5.5,typeDur=1.4,cardAt=7.6,titleOld='Toxina botulínica',titleNew='Botox en Antofagasta',
  grayAt=10.9,circleAt=11.3,eraseAt=14.45,eraseDur=0.95,typeNewAt=15.5,typeDur2=1.6,glowAt=17.4,labelOld='ANTES',labelNew='DESPUÉS',
  desc=['Información, indicaciones y cuidados.','Agenda tu evaluación en Antofagasta.'])
L('serp','Buscador y resultado',5.05,19.5,540,860,760,640,animIn='rise',animOut='fade',animDur=0.4,
  scaleKf=[[5.05,1],[10.9,1],[11.8,1.1],[14.2,1.1],[15.4,1.04],[18.2,1.04],[19.2,1]],
  move=[[10.9,540,860],[11.8,540,880],[14.2,540,880],[15.4,540,865],[19.2,540,860]],**S)

# ---- 5. Números ----
body('Pos · etiqueta',19.6,22.45,640,'Posición promedio',44,70,color='#B5B5BA',bold=True)
L('text','Pos · valores',19.7,22.45,520,780,840,170,text='5,0 → *4,5*',font='title',size=120,color=IV,align='left',accent=IV,animIn='rise',animOut='fade',animDur=0.35)
body('Pos · nota',20.4,22.45,920,'prácticamente el mismo lugar',42,70,color='#B5B5BA')
body('CTR · etiqueta',22.55,27.45,560,'Porcentaje de clics',48,70,color='#B5B5BA',bold=True)
L('text','CTR · contador',22.6,26.25,520,820,840,260,text='5,6%',font='title',size=220,color=IV,align='left',animIn='rise',animOut='none',animDur=0.3,
  count=dict(from_=5.6,to=10.9,at=25.0,dur=1.25,dec=1,suffix='%'))
L('text','CTR · final',26.25,27.5,520,820,840,300,text='10,9%',font='title',size=270,color=CO,align='left',animIn='pop',animOut='fade',animDur=0.3,hitAt=26.25)
body('CTR · nota',23.0,27.45,1030,'julio a septiembre vs octubre',42,70,color='#B5B5BA')

# ---- 6. Letra chica ----
pill('Etiqueta letra chica',27.5,32.1,300,640,360,84,'LETRA CHICA',SK,BK,36)
body('Letra chica texto',28.0,32.1,820,'1 mes de datos · 11 clics en octubre ·\nlo sigo midiendo',46,160,bold=True)

# ---- 7. Cierre ----
title('Cierre',32.45,DUR,720,'Habla como\nbusca *tu cliente.*',108,300,animOut='none')
pill('Botón escríbeme',37.6,DUR,460,1180,720,124,'Escríbeme · link en mi perfil',CO,BK,38,animOut='none',shadow=True,animDur=0.4)
body('URL',38.2,DUR,1300,'ursulahr.cl',40,60,color=IV,animOut='none')

# ---- subtítulos (una cláusula por bloque, tiempos medidos) ----
SPL={'Es de una clínica estética de Antofagasta.':['Es de una clínica estética','de Antofagasta.'],
 'El tratamiento se llamaba toxina botulínica.':['El tratamiento se llamaba','toxina botulínica.'],
 'En octubre lo cambié por botox en Antofagasta,':['En octubre lo cambié por','botox en Antofagasta,'],
 'La página siguió prácticamente en el mismo lugar.':['La página siguió prácticamente','en el mismo lugar.'],
 'Pero el porcentaje de clics pasó de cinco coma seis a diez coma nueve por ciento.':['Pero el porcentaje de clics pasó','de cinco coma seis','a diez coma nueve por ciento.'],
 'A veces no tienes que subir en Google.':['A veces no tienes','que subir en Google.'],
 'Basta con hablar como habla tu cliente.':['Basta con hablar','como habla tu cliente.'],
 'Escríbeme y te cuento cómo te está mostrando a ti.':['Escríbeme y te cuento','cómo te está mostrando a ti.']}
CAP=[]
for a,b,txt in P:
    parts=SPL.get(txt,[txt]); tot=sum(len(p) for p in parts); t=a
    for p in parts:
        d=(b-a)*len(p)/tot; CAP.append((round(t,2),round(t+d,2),p)); t+=d
def srt_t(x): h=int(x//3600); m=int(x%3600//60); sec=x%60; return f"{h:02d}:{m:02d}:{int(sec):02d},{int(round((sec-int(sec))*1000)):03d}"
open('/tmp/claude-0/-home-user-ursuhr-github-io/23d518a8-99e9-5a8c-80e1-dd2d0961eac5/scratchpad/seo-botox.srt','w').write('\n'.join(f"{i+1}\n{srt_t(a)} --> {srt_t(b)}\n{t}\n" for i,(a,b,t) in enumerate(CAP)))
for i,(a,b,txt) in enumerate(CAP):
    L('caption',f'Subtítulos {i+1}',a,b+0.05,540,1500,860,110,text=txt,size=52,capStyle='plain-light',maxWords=8,capAlign='center',accent='#FFFFFF')

# ---- sonido ----
def snd(name,asset,start,vol):
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',ROOT+'assets/sfx/'+asset+'.mp3']).decode())
    L('sound',name,start,min(DUR,start+d),0,0,0,0,asset=asset,volume=vol)
snd('Whoosh hook','whoosh-1',0.05,0.08); snd('Pop hook 2','pop-1',2.4,0.08)
snd('Whoosh buscador','whoosh-2',5.05,0.08)
for i in range(6): snd(f'Tecleo query {i+1}','tick-1',5.55+i*0.22,0.06)
snd('Pop tarjeta','pop-2',7.6,0.1); snd('Trazo círculo','whoosh-1',11.3,0.06)
for i in range(5): snd(f'Borrado {i+1}','tick-1',14.5+i*0.17,0.06)
for i in range(6): snd(f'Tecleo título {i+1}','tick-1',15.55+i*0.24,0.06)
snd('Pop después','pop-1',15.4,0.08); snd('Brillo subrayado','chime-2',17.4,0.08)
snd('Pop posición','pop-2',19.65,0.1); snd('Whoosh números','whoosh-2',22.5,0.08)
for i in range(6): snd(f'Contador {i+1}','tick-1',25.05+i*0.2,0.06)
snd('Golpe 10,9','golpe-1',26.25,0.16)
snd('Pop letra chica','pop-1',27.5,0.08)
snd('Whoosh cierre','whoosh-1',32.45,0.08); snd('Pop botón','pop-1',37.6,0.1); snd('Campanita botón','chime-1',38.1,0.1)

for l in layers:
    if 'count' in l: l['count']['from']=l['count'].pop('from_')
vo=['Esta página no subió en Google. Y aun así, el doble de gente hizo clic.','Es de una clínica estética de Antofagasta. El tratamiento se llamaba toxina botulínica.','Es el nombre técnico. Pero casi nadie lo busca así.','En octubre lo cambié por botox en Antofagasta, que es como lo escribe la gente.','La página siguió prácticamente en el mismo lugar. Pero el porcentaje de clics pasó de cinco coma seis a diez coma nueve por ciento.','Ojo, es un solo mes y con poco volumen, así que lo sigo midiendo.','A veces no tienes que subir en Google. Basta con hablar como habla tu cliente. Escríbeme y te cuento cómo te está mostrando a ti.']
proj=dict(template='seo-botox',rev=1,name='Reel · Botox en Antofagasta (caso SEO)',width=1080,height=1920,fps=30,duration=DUR,background=BK,voiceover='\n\n'.join(vo),layers=layers)
json.dump(proj,open(ROOT+'projects/seo-botox.json','w'),ensure_ascii=False,indent=1)
print(len(layers),'capas · duración',DUR)

# ---- portada 1080x1920 (el grid recorta a 3:4: título y etiqueta dentro de y 240..1680) ----
layers.clear(); n=itertools.count(1)
L('shape','Halo portada',0,1,900,1800,1700,1700,kind='halo',color=CO,color2=SK,opacity=0.55)
L('logo','Logo HR',0,1,190,130,150,100,variant='light')
L('text','URSULAHR',0,1,800,130,400,60,text='URSULAHR',font='body',bold=True,size=40,color=IV,align='right',tracking=0.2)
L('text','Título portada',0,1,520,900,840,720,text='Mismo lugar\nen Google.\n*El doble*\nde gente\nhizo clic.',font='title',size=104,color=IV,align='left',lh=1.08,accent=CO)
L('shape','Etiqueta caso SEO',0,1,260,1540,340,84,kind='pill',color=SK,label='CASO SEO',labelColor=BK,labelSize=36)
L('shape','Flecha',0,1,900,1540,80,80,kind='arrow',color=IV,rot=135)
cov=dict(template='seo-botox-portada',rev=1,name='Portada · Botox en Antofagasta',width=1080,height=1920,fps=30,duration=1,background=BK,voiceover='',layers=layers)
json.dump(cov,open(ROOT+'projects/seo-botox-portada.json','w'),ensure_ascii=False,indent=1)
