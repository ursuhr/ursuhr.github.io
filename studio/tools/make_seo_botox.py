import json, itertools, subprocess
IV,BK,CO,SK='#F5F1E8','#0B0B0B','#FF6BA7','#6EC6FF'
ROOT='/home/user/ursuhr.github.io/studio/'
n=itertools.count(1); layers=[]
def L(type,name,start,end,x,y,w,h=100,**k):
    d=dict(id=f"l{next(n):02d}",type=type,name=name,start=round(start,2),end=round(end,2),x=x,y=y,w=w,h=h,rot=0,opacity=1,animIn='none',animOut='none',animDur=0.45)
    d.update(k); layers.append(d); return d

DUR=31.0
# ---- tiempos ESTIMADOS (se reemplazan con silencedetect cuando exista la voz) ----
V=dict(s1=(0.1,3.8),s2=(4.1,7.8),s3=(8.1,10.8),s4=(11.1,15.7),s5=(16.1,21.8),s6=(22.1,24.8),s7=(25.1,30.0))

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
halo('Halo portada',0,4.6,900,1800,1500,0.5,move=[[0,940,1840],[4.6,880,1760]],scaleKf=[[0,0.9],[4.6,1.05]])
halo('Halo fondo',4.2,22.4,900,1800,1500,0.2,move=[[4.2,900,1800],[13,860,1770],[22.4,920,1810]],scaleKf=[[4.2,1],[13,1.08],[22.4,1]])
halo('Halo calma',22.0,25.2,900,1800,1400,0.1,move=[[22,900,1800],[25.2,920,1820]])
halo('Halo cierre',24.8,DUR,820,1700,1900,0.5,move=[[24.8,900,1850],[DUR,760,1560]],scaleKf=[[24.8,0.85],[28,1.2],[DUR,1.35]])

# ---- 1. Hook ----
title('Hook 1',0.05,3.85,600,'Mismo lugar\nen Google.',100,240)
title('Hook 2',0.55,3.85,950,'El *doble*\nde gente\nhizo clic.',100,330)

# ---- 2-4. Buscador y resultado (una capa) ----
S=dict(query='botox antofagasta',typeAt=4.35,typeDur=1.35,cardAt=5.85,titleOld='Toxina botulínica',titleNew='Botox en Antofagasta',
  grayAt=8.3,circleAt=8.9,eraseAt=11.3,eraseDur=0.95,typeNewAt=12.4,typeDur2=1.5,glowAt=14.2,labelOld='ANTES',labelNew='DESPUÉS',
  desc=['Información, indicaciones y cuidados.','Agenda tu evaluación en Antofagasta.'])
L('serp','Buscador y resultado',3.95,16.35,540,860,760,640,animIn='rise',animOut='fade',animDur=0.4,
  scaleKf=[[3.95,1],[8.0,1],[8.9,1.1],[11.0,1.1],[12.2,1.04],[14.5,1.04],[15.6,1]],
  move=[[8.0,540,860],[8.9,540,880],[11.0,540,880],[12.2,540,865],[15.6,540,860]],**S)

# ---- 5. Números ----
body('Pos · etiqueta',16.15,19.0,640,'Posición promedio',44,70,color='#B5B5BA',bold=True)
L('text','Pos · valores',16.25,19.0,520,780,840,170,text='5,0 → *4,5*',font='title',size=120,color=IV,align='left',accent=IV,animIn='rise',animOut='fade',animDur=0.35)
body('Pos · nota',16.9,19.0,920,'prácticamente el mismo lugar',42,70,color='#B5B5BA')
body('CTR · etiqueta',19.1,22.15,560,'Porcentaje de clics',48,70,color='#B5B5BA',bold=True)
L('text','CTR · contador',19.15,20.9,520,820,840,260,text='5,6%',font='title',size=220,color=IV,align='left',animIn='rise',animOut='none',animDur=0.3,
  count=dict(from_=5.6,to=10.9,at=19.35,dur=1.5,dec=1,suffix='%'))
L('text','CTR · final',20.9,22.25,520,820,840,300,text='10,9%',font='title',size=270,color=CO,align='left',animIn='pop',animOut='fade',animDur=0.3,hitAt=20.9)
body('CTR · nota',19.6,22.25,1030,'julio a septiembre vs octubre',42,70,color='#B5B5BA')

# ---- 6. Letra chica ----
pill('Etiqueta letra chica',22.2,24.95,300,640,360,84,'LETRA CHICA',SK,BK,36)
body('Letra chica texto',22.5,24.95,820,'1 mes de datos · 11 clics en octubre ·\nlo sigo midiendo',46,160,bold=True)

# ---- 7. Cierre ----
title('Cierre',25.1,DUR,720,'Habla como\nbusca *tu cliente.*',108,300,animOut='none')
pill('Botón escríbeme',27.9,DUR,460,1180,720,124,'Escríbeme · link en mi perfil',CO,BK,38,animOut='none',shadow=True,animDur=0.4)
body('URL',28.4,DUR,1300,'ursulahr.cl',40,60,color=IV,animOut='none')

# ---- subtítulos ----
def split(seg,parts):
    a,b=V[seg]; tot=sum(len(p) for p in parts); out=[]; t=a
    for p in parts:
        d=(b-a)*len(p)/tot; out.append((round(t,2),round(t+d,2),p)); t+=d
    return out
CAP=[]
CAP+=split('s1',['Esta página no subió en Google.','Y aun así, el doble de gente hizo clic.'])
CAP+=split('s2',['Es de una clínica estética','de Antofagasta.','El tratamiento se llamaba toxina botulínica.'])
CAP+=split('s3',['Es el nombre técnico.','Pero casi nadie lo busca así.'])
CAP+=split('s4',['En octubre lo cambié por','botox en Antofagasta,','que es como lo escribe la gente.'])
CAP+=split('s5',['La página siguió prácticamente','en el mismo lugar.','Pero el porcentaje de clics pasó','de cinco coma seis','a diez coma nueve por ciento.'])
CAP+=split('s6',['Ojo, es un solo mes','y con poco volumen,','así que lo sigo midiendo.'])
CAP+=split('s7',['A veces no tienes que subir en Google.','Basta con hablar como habla tu cliente.','Escríbeme y te cuento','cómo te está mostrando a ti.'])
for i,(a,b,txt) in enumerate(CAP):
    L('caption',f'Subtítulos {i+1}',a,b+0.05,540,1500,860,110,text=txt,size=52,capStyle='plain-light',maxWords=8,capAlign='center',accent='#FFFFFF')

# ---- sonido ----
def snd(name,asset,start,vol):
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',ROOT+'assets/sfx/'+asset+'.mp3']).decode())
    L('sound',name,start,min(DUR,start+d),0,0,0,0,asset=asset,volume=vol)
snd('Whoosh hook','whoosh-1',0.05,0.1); snd('Pop hook 2','pop-1',0.6,0.1)
snd('Whoosh buscador','whoosh-2',3.95,0.1)
for i in range(6): snd(f'Tecleo query {i+1}','tick-1',4.4+i*0.2,0.08)
snd('Pop tarjeta','pop-2',5.85,0.12); snd('Trazo círculo','whoosh-1',8.9,0.07)
for i in range(5): snd(f'Borrado {i+1}','tick-1',11.35+i*0.17,0.07)
for i in range(6): snd(f'Tecleo título {i+1}','tick-1',12.45+i*0.22,0.08)
snd('Pop después','pop-1',12.3,0.1); snd('Brillo subrayado','chime-2',14.2,0.1)
snd('Pop posición','pop-2',16.2,0.12); snd('Whoosh números','whoosh-2',19.05,0.1)
for i in range(7): snd(f'Contador {i+1}','tick-1',19.4+i*0.2,0.07)
snd('Golpe 10,9','golpe-1',20.9,0.2)
snd('Pop letra chica','pop-1',22.2,0.1)
snd('Whoosh cierre','whoosh-1',25.1,0.1); snd('Pop botón','pop-1',27.9,0.12); snd('Campanita botón','chime-1',28.5,0.12)

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
