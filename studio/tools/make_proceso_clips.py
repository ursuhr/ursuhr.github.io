import json, itertools
IV,BK,GR,SK='#F5F1E8','#0B0B0B','#34D399','#6EC6FF'
ROOT='/home/user/ursuhr.github.io/studio/'
n=itertools.count(1); layers=[]
def L(type,name,start,end,x,y,w,h=100,**k):
    d=dict(id=f"l{next(n):02d}",type=type,name=name,start=round(start,2),end=round(end,2),x=x,y=y,w=w,h=h,rot=0,opacity=1,animIn='none',animOut='none',animDur=0.45)
    d.update(k); layers.append(d); return d

DUR=33.4
# ---- tiempos REALES de la voz clonada (silencedetect -38dB d=0.15 sobre voz_web.mp3, 32,37 s) ----
T=dict(hook=(0.0,3.55),conv=(3.55,6.76),marca=(6.76,9.42),invest=(9.42,13.69),proto=(13.69,18.08),elem=(18.08,22.47),seo=(22.47,25.22),entrega=(25.22,29.32),cierre=(29.32,DUR))
CAP_P=[(0.0,1.52,['Antes de construir tu página,']),(1.70,3.08,['te muestro cómo va a quedar.']),
 (3.55,6.34,['Primero conversamos de tu negocio','y de lo que necesitas.']),
 (6.76,8.07,['Si hay que trabajar tu marca,']),(8.22,8.97,['partimos por ahí.']),
 (9.42,13.25,['Después investigo qué buscan tus clientes','y qué hace tu competencia.']),
 (13.69,15.21,['Con eso armo el prototipo,']),(15.49,17.70,['lo revisamos juntos','y hacemos los cambios.']),
 (18.08,22.07,['Cuando está aprobado,','la construyo en Elementor','para que tú puedas editarla.']),
 (22.47,24.87,['Le dejo la base SEO','para que Google la entienda.']),
 (25.22,28.85,['Y al entregarla,','te enseño a usarla','y tienes 30 días de soporte.']),
 (29.32,30.63,['Estás pensando en hacer tu web?']),(31.12,32.37,['Cuéntame de tu negocio.'])]

def halo(name,a,z,x,y,size,op,c,**k):
    L('shape',name,a,z,x,y,size,size,kind='halo',color=c,opacity=op,animIn='fade',animOut='fade',animDur=0.6,**k)
def halos(name,a,z,x,y,size,op,**k):  # celeste en los bordes, verde al medio
    halo(name+' · celeste',a,z,x,y,size,op,SK,**k)
    halo(name+' · verde',a,z,x-90,y-70,size*0.55,op*0.9,GR,**k)
def title(name,a,z,y,text,size,h,**k):
    d=dict(animIn='fade',animOut='none',animDur=0.18,accent=GR); d.update(k)
    L('text',name,a,z,520,y,860,h,text=text,font='title',size=size,color=BK,align='left',lh=1.06,**d)
def body(name,a,z,y,text,size,h=60,bold=False,**k):
    d=dict(animIn='fade',animOut='none',animDur=0.25); d.update(k)
    L('text',name,a,z,520,y,860,h,text=text,font='body',size=size,bold=bold,color=BK,align='left',lh=1.25,**d)

# ---- halos: sutiles detrás del texto de los pasos, fuertes en las láminas ----
halos('Halo pasos',0,3.55,820,380,1150,0.2)
halos('Halo pasos 2',6.76,25.22,820,380,1150,0.2)
halos('Halo conversamos',*T['conv'],900,1600,1500,0.42,move=[[T['conv'][0],940,1640],[T['conv'][1],860,1560]])
halos('Halo entrega',*T['entrega'],900,1600,1500,0.42,move=[[T['entrega'][0],940,1640],[T['entrega'][1],860,1560]])
halos('Halo cierre',*T['cierre'],860,1560,1900,0.5,move=[[T['cierre'][0],920,1700],[DUR,820,1500]],scaleKf=[[T['cierre'][0],0.85],[DUR,1.25]])

# ---- clips: tarjeta con zoom lento dentro del marco ----
CARD=dict(x=540,y=1050,w=960,h=960)
def clip(name,seg,asset,trim,speed,z0,z1,fx0,fx1,fy0,fy1):
    a,b=T[seg]
    L('image',name,a,b,CARD['x'],CARD['y'],CARD['w'],CARD['h'],asset=asset,trim=trim,speed=speed,radius=36,shadow=True,fit='cover',
      zoom=z0,fx=fx0,fy=fy0,zoomEnd=z1,fxEnd=fx1,fyEnd=fy1)
clip('Clip · gancho','hook','IMG_5233.mov',0.0,1.0,1.2,1.32,0.74,0.68,0.75,0.72)
clip('Clip · tu marca','marca','IMG_5232.mov',3.5,1.0,1.2,1.38,0.26,0.26,0.75,0.70)
clip('Clip · investigo','invest','IMG_5237.mov',0.0,0.936,1.3,1.45,0.3,0.3,0.08,0.08)
clip('Clip · prototipo','proto','IMG_5233.mov',2.5,1.0,1.2,1.38,0.74,0.64,0.75,0.72)
clip('Clip · Elementor','elem','IMG_5235.mov',0.0,0.78,1.2,1.38,0.38,0.43,0.59,0.56)
clip('Clip · SEO','seo','IMG_5237.mov',4.5,0.8,1.3,1.45,0.3,0.3,0.08,0.08)

# ---- textos de los pasos ----
a,b=T['hook'];   title('Gancho',a+0.05,b,390,'Antes de construir tu web, te muestro cómo va a quedar',64,320,accent=BK)
a,b=T['conv'];   title('1. Conversamos',a+0.05,b,720,'*1.*\nConversamos',92,300); body('1. detalle',a+0.3,b,980,'tu negocio, lo que necesitas, tu estilo',48,130)
a,b=T['marca'];  title('2. Tu marca',a+0.05,b,390,'*2.* Tu marca',96,300)
a,b=T['invest']; title('3. Investigo',a+0.05,b,390,'*3.* Investigo qué busca tu cliente',70,330)
a,b=T['proto'];  title('4. Prototipo',a+0.05,b,390,'*4.* Prototipo: lo ves y lo corregimos antes de construir',58,330)
a,b=T['elem'];   title('5. Elementor',a+0.05,b,390,'*5.* En Elementor, para que la edites tú',70,330)
a,b=T['seo'];    title('6. SEO',a+0.05,b,390,'*6.* Base SEO incluida',84,300)
a,b=T['entrega'];title('7. Entrega',a+0.05,b,720,'*7.*\nEntrega',130,330); body('7. detalle',a+0.3,b,1000,'capacitación + 30 días de soporte',48,130)
a,b=T['cierre']; title('Cierre',a+0.05,b,700,'Estás pensando en hacer *tu web?*',84,420); body('Cierre · detalle',a+0.5,b,1010,'Cuéntame de tu negocio · ursulahr.cl',48,130,bold=True)

# ---- subtítulos: bloques de 2 a 6 palabras, tiempos medidos ----
cap_i=0
for a,b,parts in CAP_P:
    tot=sum(len(p) for p in parts); t=a
    for p in parts:
        d=(b-a)*len(p)/tot; cap_i+=1
        L('caption',f'Subtítulos {cap_i}',round(t,2),round(t+d+0.05,2),540,1430,860,110,text=p,size=50,capStyle='pill',maxWords=8,capAlign='center',accent='#FFFFFF')
        t+=d

# ---- música (baja, ~-20 dB bajo la voz; capa aparte para versión sin música) ----
L('sound','Música',0,DUR,0,0,0,0,asset='musica-1',volume=0.04,fadeIn=1.2,fadeOut=2.5)

vo='Antes de construir tu página, te muestro cómo va a quedar. Primero conversamos de tu negocio y de lo que necesitas. Si hay que trabajar tu marca, partimos por ahí. Después investigo qué buscan tus clientes y qué hace tu competencia. Con eso armo el prototipo, lo revisamos juntos y hacemos los cambios. Cuando está aprobado, la construyo en Elementor para que tú puedas editarla. Le dejo la base SEO para que Google la entienda. Y al entregarla, te enseño a usarla y tienes 30 días de soporte. Estás pensando en hacer tu web? Cuéntame de tu negocio.'
proj=dict(template='proceso-clips',rev=1,name='Reel · Cómo trabajo (clips)',width=1080,height=1920,fps=30,duration=DUR,background=IV,voiceover=vo,layers=layers)
json.dump(proj,open(ROOT+'projects/proceso-clips.json','w'),ensure_ascii=False,indent=1)
print(len(layers),'capas · duración',DUR)
