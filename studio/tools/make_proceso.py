import json, itertools
IV,BK,CO,SU,GR,SK='#F5F1E8','#0B0B0B','#FF6BA7','#FFD357','#34D399','#6EC6FF'
n=itertools.count(1)
layers=[]
def L(type,name,start,end,x,y,w,h=100,**k):
    d=dict(id=f"l{next(n):02d}",type=type,name=name,start=start,end=end,x=x,y=y,w=w,h=h,rot=0,opacity=1,animIn='none',animOut='none',animDur=0.45)
    d.update(k); layers.append(d); return d
def halo(name,a,b,x,y,c1,c2): L('shape',name,a,b,x,y,1100,1100,kind='halo',color=c1,color2=c2,animIn='fade',animOut='fade',animDur=0.8)
def number(num,a,b): L('text',f'Número {num}',a,b,540,430,900,260,text=num,font='title',size=250,color=CO,align='left',animIn='rise',animOut='fade')
def pill(name,a,b,cx,y,w,h,label,fill,fg,size,**k): L('shape',name,a,b,cx,y,w,h,kind='pill',color=fill,label=label,labelColor=fg,labelSize=size,animIn='pop',animOut='fade',**k)

DUR=40.0
# límites de escena (según las pausas del audio)
B1,B2,B3,B4,B5,B6=7.0,15.2,25.1,31.4,36.65,DUR
E=0.15

# cabecera persistente
L('logo','Logo HR',0,B5+0.3,190,190,150,100,variant='dark')
L('shape','Flecha',0,B5+0.3,900,190,64,64,kind='arrow',color=BK)

# ---- Escena 1: gancho (0 - 7.0)
halo('Halo gancho',0,B1+0.5,880,1560,SK,GR)
L('shape','Destello',0.3,B1+E,940,380,80,80,kind='sparkle',color=BK,animIn='pop',animOut='fade',float=6)
L('text','Título gancho',0,B1+E,540,640,900,420,text='¿Qué quieres\nque haga\nalguien en\ntu *web*?',font='title',size=92,color=BK,accent=GR,align='left',lh=1.05,animIn='rise',animOut='fade')
for i,(t,w,s) in enumerate([('Que te escriba',500,3.4),('Reserve una hora',580,4.5),('Te pida una cotización',720,5.5)]):
    pill(f'Opción {i+1}',s,B1+E,100+w/2,1050+i*125,w,100,t,'#FFFFFF',BK,40,shadow=True)

# ---- Escena 2: 01 Conversamos (7.0 - 15.2)
halo('Halo 01',B1,B2+0.5,200,1500,CO,SU)
number('01',B1,B2+E)
L('text','Título 01',B1+0.2,B2+E,540,690,900,120,text='Conversamos',font='title',size=92,color=BK,align='left',animIn='rise',animOut='fade')
for i,(t,w,s) in enumerate([('Tu negocio',440,10.7),('Tus clientes',480,11.8),('Lo que necesitan saber',720,13.0)]):
    pill(f'Tema {i+1}',s,B2+E,100+w/2,920+i*130,w,100,t,'#FFFFFF',BK,40,shadow=True)

# ---- Escena 3: 02 Análisis y diseño (15.2 - 25.1)
halo('Halo 02',B2,B3+0.5,880,1400,SU,CO)
number('02',B2,B3+E)
L('text','Título 02',B2+0.2,B3+E,540,640,900,230,text='Análisis\ny diseño',font='title',size=92,color=BK,align='left',animIn='rise',animOut='fade')
pill('Chip competencia',16.4,B3+E,310,800,420,84,'Tu competencia',BK,IV,32)
pill('Chip destacar',18.2,B3+E,775,800,420,84,'Lo que destacas',BK,IV,32)
L('mockup','Navegador · Tablero de competencia',15.9,B3+E,540,1130,880,500,kind='browser',asset='',url='notion.so',fit='cover',placeholder='Aquí va tu tablero de competencia (Notion)',animIn='rise',animOut='fade')

# ---- Escena 4: 03 Construcción (25.1 - 31.4)
halo('Halo 03',B3,B4+0.5,200,1350,GR,SK)
number('03',B3,B4+E)
L('text','Título 03',B3+0.2,B4+E,540,640,900,120,text='Construcción',font='title',size=88,color=BK,align='left',animIn='rise',animOut='fade')
pill('Chip rápida',28.9,B4+E,290,800,380,84,'Carga rápida',BK,IV,32)
pill('Chip contacto',30.0,B4+E,700,800,380,84,'Fácil de contactar',BK,IV,32)
L('mockup','Navegador · Elementor',25.6,B4+E,540,1140,880,460,kind='browser',asset='',url='ursulahr.cl',fit='cover',placeholder='Aquí va tu grabación de Elementor',animIn='rise',animOut='fade')

# ---- Escena 5: 04 Entrega (31.4 - 36.65)
halo('Halo 04',B4,B5+0.5,850,1300,SK,GR)
number('04',B4,B5+0.3)
L('text','Título 04',B4+0.2,B5+0.3,540,640,900,120,text='Entrega',font='title',size=100,color=BK,align='left',animIn='rise',animOut='fade')
L('text','Bajada 04',B4+0.7,B5+0.3,360,960,520,300,text='Te enseño a actualizarla',font='body',size=50,color=BK,align='left',lh=1.25,animIn='fade',animOut='fade')
pill('Soporte 30 días',34.9,B5+0.3,360,1180,520,100,'30 días de soporte',CO,BK,38)
L('mockup','Celular · sitio',B4+0.4,B5+0.3,810,1050,340,660,kind='phone',asset='',fit='cover',placeholder='Tu sitio en el celular',animIn='rise',animOut='fade')

# ---- Escena 6: cierre oscuro (36.65 - 40)
L('shape','Fondo oscuro',B5,DUR,540,960,1080,1920,kind='rect',color=BK,animIn='fade',animDur=0.5)
L('shape','Glow verde',B5,DUR,900,1560,1300,1300,kind='halo',color=GR,color2=SU,animIn='fade',animDur=0.9)
L('shape','Glow coral',B5+0.2,DUR,120,320,900,900,kind='halo',color=CO,color2=SU,animIn='fade',animDur=0.9,opacity=0.7)
L('logo','Logo HR claro',B5,DUR,190,190,150,100,variant='light')
L('shape','Flecha clara',B5,DUR,900,190,64,64,kind='arrow',color=IV)
L('text','Título cierre',B5+0.2,DUR,540,640,900,420,text='¿Tienes un\n*proyecto*\nen mente?',font='title',size=100,color=IV,accent=GR,align='left',lh=1.05,animIn='rise')
L('text','Invitación',38.3,DUR,540,1030,860,120,text='Cuéntamelo por *WhatsApp*',font='body',size=58,bold=True,color=IV,accent=GR,align='left',animIn='fade')
pill('Botón cierre',38.6,DUR,540,1200,560,130,'Escríbeme',CO,BK,48,arrowIcon=True,arrowColor=BK,float=5)
L('shape','Destello 1',B5+0.5,DUR,930,400,90,90,kind='sparkle',color=IV,animIn='pop',float=6)
L('shape','Destello 2',B5+0.8,DUR,830,520,50,50,kind='sparkle',color=SU,animIn='pop',float=4)

# ---- Subtítulos: una frase por capa, con las ventanas reales de la voz
caps=[(0.0,2.53,'¿Qué quieres que haga alguien cuando entre a tu web?'),
(2.94,6.69,'¿Que te escriba, reserve una hora o te pida una cotización?'),
(7.30,9.49,'Cuando trabajamos juntos, partimos por ahí.'),
(9.88,14.89,'Conversamos sobre tu negocio, tus clientes y lo que necesitan saber antes de elegirte.'),
(15.47,20.04,'Después reviso cómo se muestra tu competencia y qué podemos destacar de tu trabajo.'),
(20.52,24.88,'Con eso ordeno las fotos y los textos, y te muestro cómo quedaría tu web.'),
(25.32,27.37,'Cuando apruebas el diseño, la construyo.'),
(27.78,31.08,'Me aseguro de que cargue rápido y de que sea fácil contactarte.'),
(31.68,36.43,'Al entregártela, te enseño a actualizarla y te acompaño durante los primeros 30 días.'),
(36.87,38.00,'¿Tienes un proyecto en mente?'),
(38.36,39.55,'¡Cuéntamelo por WhatsApp!')]
for i,(a,b,t) in enumerate(caps):
    L('caption',f'Subtítulos {i+1}',a,b,540,1450,960,110,text=t,size=52,capStyle='plain-light' if a>=B5 else 'pill',maxWords=4,accent=CO)


# ---- Efectos de sonido (biblioteca en assets/sfx), calzados con la aparición de cada elemento
import subprocess
def _dur(a): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','/home/user/ursuhr.github.io/studio/assets/sfx/'+a+'.mp3']).decode())
SFXD={a:_dur(a) for a in ['whoosh-1','whoosh-2','pop-1','pop-2','tick-1','chime-1','chime-2']}
def snd(name,asset,start,vol,dur=None):
    d=SFXD[asset]
    L('sound',name,round(start,2),round(min(DUR,start+d),2),0,0,0,0,asset=asset,volume=vol)
for i,t in enumerate([0.05,7.2,15.4,25.3,31.6,36.85]):
    snd(f'Whoosh {i+1}',f'whoosh-{1+i%2}',t,0.12)
for i,t in enumerate([7.0,15.2,25.1,31.4]):
    snd(f'Tick número 0{i+1}','tick-1',t,0.16,1.0)
pops=[3.4,4.5,5.5,10.7,11.8,13.0,16.4,18.2,28.9,30.0,34.9]
for i,t in enumerate(pops):
    snd(f'Pop {i+1}',f'pop-{1+i%2}',t,0.12,1.2)
snd('Campanita botón final','chime-1',38.6,0.14,2.04)
L('sound','Música de fondo',0,DUR,0,0,0,0,asset='musica-1',volume=0.07,fadeIn=1.5,fadeOut=3.0)

proj=dict(template='proceso',rev=6,name='Reel · Cómo trabajo',width=1080,height=1920,fps=30,duration=DUR,background=IV,
 voiceover=' '.join(c[2] for c in caps),layers=layers)
json.dump(proj,open('/home/user/ursuhr.github.io/studio/projects/proceso.json','w'),ensure_ascii=False,indent=1)
print(len(layers),'capas')
