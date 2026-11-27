import json, itertools, subprocess, os
# Reel: Tipos de páginas web · Ep. 1, la landing (fondo claro)
IV,BK,CO,SK='#F5F1E8','#0B0B0B','#FF6BA7','#6EC6FF'
GRIS='#8A8A8E'
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')+'/'
n=itertools.count(1); layers=[]
def L(type,name,start,end,x,y,w,h=100,**k):
    d=dict(id=f"l{next(n):02d}",type=type,name=name,start=round(start,2),end=round(end,2),x=x,y=y,w=w,h=h,rot=0,opacity=1,animIn='none',animOut='none',animDur=0.45)
    d.update(k); layers.append(d); return d

DUR=33.0
# ---- tiempos REALES de la voz clonada (transcripción con tiempos por palabra, voz_landing.mp3, ~30,9 s) ----
T=dict(hook=(0.0,3.0),defi=(3.0,11.5),vale=(11.5,19.0),matcha=(19.0,24.1),cierre=(24.1,DUR))
# momentos clave dentro de la voz
PERO_CUAL=1.7; PEDIR_HORA=9.2; COMPRAR=10.5; FORMULARIO=17.1; WHATSAPP=18.1; MERCADO=22.9; PREGUNTA=25.4; ESCRIBEME=29.4; FIN_VOZ=30.9

def halo(name,a,z,x,y,size,op,**k):
    L('shape',name,a,z,x,y,size,size,kind='halo',color=CO,color2=SK,opacity=op,animIn='fade',animOut='fade',animDur=0.8,**k)
def title(name,a,z,y,text,size,h,**k):
    d=dict(animIn='rise',animOut='fade',animDur=0.35,accent=CO); d.update(k)
    L('text',name,a,z,520,y,860,h,text=text,font='title',size=size,color=BK,align='left',lh=1.05,**d)
def body(name,a,z,y,text,size,h=60,color=BK,bold=False,**k):
    d=dict(animIn='fade',animOut='fade',animDur=0.3); d.update(k)
    L('text',name,a,z,520,y,860,h,text=text,font='body',size=size,bold=bold,color=color,align='left',lh=1.25,**d)
def pill(name,a,z,cx,y,w,h,label,fill,fg,size,**k):
    d=dict(animIn='pop',animOut='fade'); d.update(k)
    L('shape',name,a,z,cx,y,w,h,kind='pill',color=fill,label=label,labelColor=fg,labelSize=size,**d)

# ---- halo coral + azul desde la esquina inferior derecha (crece en el cierre) ----
halo('Halo gancho',0,T['hook'][1]+0.4,900,1800,1500,0.5,move=[[0,940,1840],[3.4,880,1760]],scaleKf=[[0,0.9],[3.4,1.05]])
halo('Halo fondo',3.0,24.5,900,1800,1500,0.35,move=[[3,900,1800],[14,860,1770],[24.5,920,1810]],scaleKf=[[3,1],[14,1.08],[24.5,1]])
halo('Halo cierre',24.1,DUR,820,1700,1900,0.5,move=[[24.1,900,1850],[DUR,760,1560]],scaleKf=[[24.1,0.85],[28,1.2],[DUR,1.35]])

# ---- marca fija arriba ----
L('logo','Logo HR',0,DUR,170,140,150,100,variant='dark')
L('text','URSULAHR',0,DUR,800,140,400,60,text='URSULAHR',font='body',bold=True,size=36,color=BK,align='right',tracking=0.2)

# ---- 1. Gancho ----
title('Gancho 1',0.05,3.0,640,'Pediste una\npágina web.',104,250)
title('Gancho 2',PERO_CUAL,3.0,930,'*¿Pero cuál?*',112,160,animIn='pop',hitAt=PERO_CUAL)

# ---- 2. Definición + tarjeta de la serie ----
a,b=T['defi']
title('Definición',a+0.05,b,380,'Una landing es\n*una sola página*',74,190)
body('Definición · bajada',a+0.4,b,570,'que reúne lo que alguien necesita\nsaber antes de dar un paso.',44,120)
L('shape','Tarjeta serie',a+0.3,b,540,1010,760,400,kind='rect',color='#FFFFFF',radius=36,shadow=True,animIn='rise',animOut='fade',animDur=0.4)
L('text','Tarjeta · título',a+0.4,b,520,860,640,50,text='Tipos de páginas web',font='body',size=32,bold=True,color=GRIS,align='left',animIn='fade',animOut='fade',animDur=0.3)
pill('Tarjeta · 1 Landing',a+0.55,b,540,960,680,86,'1   Landing',CO,BK,40)
L('text','Tarjeta · 2',a+0.6,b,520,1060,600,60,text='2   Multipágina',font='body',size=40,bold=True,color='#A9A9AD',align='left',animIn='fade',animOut='fade',animDur=0.3)
L('text','Tarjeta · 3',a+0.65,b,520,1140,600,60,text='3   Tienda',font='body',size=40,bold=True,color='#A9A9AD',align='left',animIn='fade',animOut='fade',animDur=0.3)
pill('Pill pedir una hora',PEDIR_HORA,b,365,1330,330,96,'Pedir una hora',BK,IV,38,hitAt=PEDIR_HORA)
pill('Pill comprar',COMPRAR,b,680,1330,240,96,'Comprar',SK,BK,38,hitAt=COMPRAR)

# ---- 3. Ejemplo real: Dra. Vale ----
PHONE=dict(x=540,y=915,w=410,h=820)   # más chico: queda sobre los 320 px de abajo que tapa Instagram
a,b=T['vale']
body('Vale · etiqueta',a+0.05,b,300,'Ejemplo real',40,60,color=CO,bold=True)
title('Vale · dominio',a+0.05,b,390,'dravale.cl',88,120)
# inicio del sitio y después el formulario (grabación vertical del sitio en el celular)
L('mockup','Celular · Dra. Vale inicio',a,13.8,**PHONE,kind='phone',asset='dravale-scroll.mp4',trim=0.0,speed=1.0,fit='cover',placeholder='Grabación de dravale.cl',animIn='rise',animOut='none',animDur=0.4)
L('mockup','Celular · Dra. Vale formulario',13.8,b,**PHONE,kind='phone',asset='dravale-scroll.mp4',trim=6.0,speed=0.5,fit='cover',placeholder='Formulario de dravale.cl')
pill('Pill formulario',FORMULARIO,b,400,1410,290,88,'Formulario',SK,BK,36,hitAt=FORMULARIO)
pill('Pill WhatsApp',WHATSAPP,b,700,1410,290,88,'WhatsApp',CO,BK,36,hitAt=WHATSAPP)

# ---- 4. Ejemplo real: MatchaMatch ----
a,b=T['matcha']
body('Matcha · etiqueta',a+0.05,b,300,'Ejemplo real',40,60,color=CO,bold=True)
title('Matcha · dominio',a+0.05,b,390,'matchamatch.cl',80,120)
L('mockup','Celular · MatchaMatch producto',a,21.1,**PHONE,kind='phone',asset='matchamatch-scroll.mp4',trim=3.4,speed=1.0,fit='cover',placeholder='Grabación de matchamatch.cl')
L('mockup','Celular · MatchaMatch botón',21.1,b,**PHONE,kind='phone',asset='matchamatch-scroll.mp4',trim=5.45,speed=0.02,fit='cover',placeholder='Botón Comprar ahora',
  scaleKf=[[21.1,1],[21.6,1.06],[b,1.06]])
pill('Pill comprar ahora',21.1,23.2,540,1410,620,86,'Comprar ahora → Mercado Libre',CO,BK,34,hitAt=21.1)
pill('Pill sin tienda',23.2,b,540,1410,600,86,'Vende sin tener tienda propia',SK,BK,34,hitAt=23.2)

# ---- 5. Cierre ----
a,b=T['cierre']
title('Cierre',a+0.05,b,560,'Piensa en\n*tu negocio.*',108,260,animOut='none')
body('Cierre · pregunta',PREGUNTA,b,800,'¿Qué quieres que haga la persona\nque entra a tu web?',48,130,animOut='none')
pill('Botón escríbeme',ESCRIBEME,b,460,1060,720,124,'Escríbeme · link en mi perfil',CO,BK,38,animOut='none',shadow=True,arrowIcon=True,arrowColor=BK,animDur=0.4,hitAt=ESCRIBEME)
body('Próximo',30.4,b,1220,'Próximo: Multipágina',38,60,color=BK,bold=True,animOut='none')

# ---- subtítulos: cláusulas con sentido, tiempos medidos en la voz real (voz_landing.mp3, 30,8 s) ----
CAP=[(0.0,1.25,'Pediste una página web.'),(1.70,2.45,'¿Pero cuál?'),(3.08,4.01,'Una landing es una sola página'),
 (4.16,6.0,'que reúne lo que alguien necesita'),(6.0,8.1,'saber antes de dar un paso,'),(8.2,10.83,'como pedir una hora o comprar.'),
 (11.25,12.78,'Mira la de la Dra. Vale.'),
 (13.27,14.67,'Lees sobre sus tratamientos'),(14.67,15.81,'de armonización facial'),(15.81,16.9,'y puedes contactarla'),(16.9,18.45,'por formulario o por WhatsApp.'),
 (18.96,20.59,'En MatchaMatch, en cambio,'),(20.79,21.7,'el botón de compra'),(21.7,23.47,'te lleva directo a Mercado Libre.'),
 (24.17,25.08,'Piensa en tu negocio.'),(25.61,26.96,'¿Qué quieres que haga la persona'),(26.96,27.76,'que entra a tu web?'),
 (28.33,29.42,'Si tienes dudas,'),(29.42,30.85,'escríbeme y lo vemos.')]
for i,(a,b,txt) in enumerate(CAP):
    L('caption',f'Subtítulos {i+1}',a,b+0.05,540,1520,960,110,text=txt,size=54,capStyle='pill',maxWords=9,capAlign='center',accent='#FFFFFF')

# ---- sonido ----
def snd(name,asset,start,vol):
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',ROOT+'assets/sfx/'+asset+'.mp3']).decode())
    L('sound',name,start,min(DUR,start+d),0,0,0,0,asset=asset,volume=vol)
snd('Whoosh gancho','whoosh-1',0.05,0.08); snd('Pop pero cuál','pop-1',PERO_CUAL,0.08)
snd('Whoosh definición','whoosh-2',3.0,0.08); snd('Pop tarjeta','pop-2',3.6,0.08)
snd('Pop pedir hora','pop-1',PEDIR_HORA,0.08); snd('Pop comprar','pop-2',COMPRAR,0.08)
snd('Whoosh Dra. Vale','whoosh-1',11.5,0.08); snd('Deslizar formulario','deslizar-1',13.8,0.06)
snd('Pop formulario','pop-1',FORMULARIO,0.08); snd('Pop WhatsApp','pop-2',WHATSAPP,0.08)
snd('Whoosh MatchaMatch','whoosh-2',19.0,0.08); snd('Clic comprar','clic-1',21.1,0.1); snd('Pop sin tienda','pop-1',23.2,0.08)
snd('Whoosh cierre','whoosh-1',24.1,0.08); snd('Pop botón','pop-1',ESCRIBEME,0.1); snd('Campanita botón','chime-1',ESCRIBEME+0.5,0.1)
# música baja en capa aparte (se puede apagar para la versión solo voz)
L('sound','Música',0,DUR,0,0,0,0,asset='musica-1',volume=0.04,fadeIn=1.2,fadeOut=2.5)

vo='Pediste una página web. Pero cuál.\n\nUna landing es una sola página que reúne lo que alguien necesita saber antes de dar un paso, como pedir una hora o comprar.\n\nMira la de la Dra. Vale. Lees sobre sus tratamientos de armonización facial y puedes contactarla por formulario o por WhatsApp.\n\nEn MatchaMatch, en cambio, el botón de compra te lleva directo a Mercado Libre.\n\nPiensa en tu negocio. ¿Qué quieres que haga la persona que entra a tu web? Si tienes dudas, escríbeme y lo vemos.'
media={'dravale-scroll.mp4':'assets/clips/dravale-scroll.mp4','matchamatch-scroll.mp4':'assets/clips/matchamatch-scroll.mp4'}
proj=dict(template='tipos-landing',rev=4,media=media,name='Reel · Tipos de páginas web 1: la landing',width=1080,height=1920,fps=30,duration=DUR,background=IV,voiceover=vo,layers=layers)
json.dump(proj,open(ROOT+'projects/tipos-landing.json','w'),ensure_ascii=False,indent=1)
print(len(layers),'capas · duración',DUR)

# ---- portada 1080x1920 (el grid recorta a 3:4: título y etiqueta dentro de y 240..1680) ----
layers.clear(); n=itertools.count(1)
L('shape','Halo portada',0,1,900,1800,1700,1700,kind='halo',color=CO,color2=SK,opacity=0.55)
L('logo','Logo HR',0,1,190,330,150,100,variant='dark')
L('text','URSULAHR',0,1,800,330,400,60,text='URSULAHR',font='body',bold=True,size=40,color=BK,align='right',tracking=0.2)
L('text','Título portada',0,1,520,900,840,520,text='Pediste una\npágina web.\n¿Pero *cuál?*',font='title',size=110,color=BK,align='left',lh=1.08,accent=CO)
L('shape','Etiqueta serie',0,1,420,1500,660,84,kind='pill',color=BK,label='TIPOS DE PÁGINAS WEB · 1',labelColor=IV,labelSize=34)
L('shape','Flecha',0,1,900,1500,80,80,kind='arrow',color=BK,rot=0)
cov=dict(template='tipos-landing-portada',rev=2,name='Portada · Tipos de páginas web 1',width=1080,height=1920,fps=30,duration=1,background=IV,voiceover='',layers=layers)
json.dump(cov,open(ROOT+'projects/tipos-landing-portada.json','w'),ensure_ascii=False,indent=1)
