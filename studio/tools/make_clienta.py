import json, itertools, subprocess
IV,BK,CO,SU,GR,SK='#F5F1E8','#0B0B0B','#FF6BA7','#FFD357','#34D399','#6EC6FF'
n=itertools.count(1); layers=[]
def L(type,name,start,end,x,y,w,h=100,**k):
    d=dict(id=f"l{next(n):02d}",type=type,name=name,start=round(start,2),end=round(end,2),x=x,y=y,w=w,h=h,rot=0,opacity=1,animIn='none',animOut='none',animDur=0.45)
    d.update(k); layers.append(d); return d

# ---- tiempos REALES de la voz (medidos en el audio generado con la voz clonada) ----
DUR=39.0; E_=0.15
S1a,S1b,S2,S3,S4,S5,S6,S7,S8,S9a,S9b=(0.0,1.92),(2.54,3.97),(4.46,7.22),(7.74,10.71),(11.18,16.77),(17.26,21.70),(22.22,24.95),(25.43,30.99),(31.48,35.07),(35.58,37.10),(37.43,38.7)
Q2,Q3=27.74,29.26
bS2,bS4,bS5,bS6,bS7,bS8,bS9=4.3,11.0,17.1,22.1,25.3,31.3,35.4
CAP=[(S1a,'Doscientos mil pesos.'),(S1b,'Por las claves de su página web.'),(S2,'Eso me contó una clienta que quería actualizar su sitio.'),
(S3,'Ella solo tenía un usuario con permisos limitados.'),(S4,'Cuando pidió el acceso de administrador, el desarrollador le pidió doscientos mil pesos para entregárselo.'),
(S5,'Al final decidió dejar esa página, y conmigo hicimos una nueva desde cero.'),(S6,'Por eso, antes de contratar una web, pregunta:'),
(S7,'Si después quiero trabajar con otra persona o cambiar de hosting, ¿puedo hacerlo sin empezar de cero?'),
(S8,'Yo te asesoro para que contrates el dominio y el hosting a tu nombre.'),(S9a,'¿Quieres crear o renovar tu web?'),(S9b,'¡Escríbeme por WhatsApp!')]

def halo(name,a,z,x,y,c1,c2): L('shape',name,a,z,x,y,1100,1100,kind='halo',color=c1,color2=c2,animIn='fade',animOut='fade',animDur=0.8)
def title(name,a,z,y,text,size=92,h=300,**k):
    d=dict(animIn='rise',animOut='fade',animDur=0.3,accent=CO); d.update(k)
    L('text',name,a,z,540,y,900,h,text=text,font='title',size=size,color=BK,align='left',lh=1.05,**d)
def pill(name,a,z,cx,y,w,h,label,fill,fg,size,**k):
    d=dict(animIn='pop',animOut='fade'); d.update(k)
    L('shape',name,a,z,cx,y,w,h,kind='pill',color=fill,label=label,labelColor=fg,labelSize=size,**d)

L('logo','Logo HR',0,DUR,190,190,150,100,variant='dark')
L('shape','Flecha',0,DUR,900,190,64,64,kind='arrow',color=BK)

# 1. El monto aparece completo casi de inmediato, golpea, y luego se reduce y queda como etiqueta
halo('Halo monto',0,5.0,540,980,CO,SU)
L('text','Monto',0.05,bS4+0.2,540,800,1000,260,text='$200.000',font='title',size=186,color=CO,align='center',animIn='letters',stagger=0.045,hitAt=0.75,
  move=[[4.2,540,800],[4.8,840,330]],scaleKf=[[4.2,1],[4.8,0.4]],animOut='fade')
L('text','Bajada monto',S1b[0],bS2-0.1,540,1010,860,160,text='por las claves de\nsu página web',font='body',size=56,bold=True,color=BK,align='center',lh=1.2,animIn='fade',animOut='fade',animDur=0.3)
# 2-3. El navegador: se arma, se acerca al menú, intenta entrar y el aviso ocupa buena parte de la pantalla
halo('Halo 2',bS2,bS4+0.5,200,1500,SK,GR)
title('Título 2',bS2+0.55,bS4-0.1,560,'Una clienta\nquería actualizar\nsu sitio',size=84)
LOCK=S3[0]+1.95; C1=LOCK-2.4; C2=LOCK-0.05
L('mockup','Navegador · sitio',bS2+0.2,bS4+0.5,540,1130,860,480,kind='browser',asset='',wire='old',url='sitio-de-la-clienta.cl',
  buildAt=bS2+0.35,cursor=[[C1-1.5,0.30,0.62],[C1-0.7,0.60,0.40],[C1-0.05,0.855,0.123],[C1+0.4,0.855,0.123],[C2-0.1,0.78,0.553],[C2+3,0.78,0.553]],
  clicks=[C1,C2],menuAt=C1+0.05,lockAt=LOCK,animIn='rise',animOut='slide',animDur=0.45,
  move=[[6.0,540,1130],[6.9,540,1130],[7.4,180,1091],[LOCK-0.3,180,1091],[LOCK+0.2,540,1038],[11.0,540,1038]],
  scaleKf=[[6.0,1],[6.9,1],[7.4,1.5],[LOCK-0.3,1.5],[LOCK+0.2,1.3],[11.0,1.3]])
# 4. La llave que no alcanza a abrir: la etiqueta cae, se balancea y frena el movimiento
halo('Halo 4',bS4,bS5+0.5,880,1300,CO,SU)
title('Título 4',bS4+0.1,bS5-0.05,560,'Acceso de\nadministrador',size=92,h=230)
L('shape','Candado',bS4+0.2,bS5-0.05,800,960,340,340,kind='padlock',color=CO,color2=BK,animIn='pop',animOut='fade',animDur=0.3,shakeAt=14.72)
L('shape','Llave',bS4+0.4,bS5-0.05,355,960,640,300,kind='key',color=BK,rot=-4,stroke=30,animOut='fade',animDur=0.3,
  move=[[11.4,-380,960],[12.0,-380,960],[14.2,355,960],[14.3,355,960],[14.7,322,960]])
pill('Etiqueta precio',14.3,bS5-0.05,200,1135,300,96,'$200.000',CO,BK,48,animIn='drop',animDur=0.7,swing={'t0':14.75,'amp':14,'period':0.9,'decay':2.4},hitAt=14.75,shadow=True)
# 5. La página antigua se queda durante "dejar esa página"; la nueva se revela en "y conmigo hicimos una nueva"
halo('Halo 5',bS5,bS6+0.5,200,1350,GR,SK)
title('Título 5a',bS5+0.1,19.35,560,'Dejó esa\npágina',size=92,h=230)
title('Título 5b',19.5,bS6-0.1,560,'Una web\nnueva, desde\ncero',size=92)
L('mockup','Navegador · sitio anterior',bS5,bS6-0.05,540,1160,860,480,kind='browser',asset='pagina-antigua-portada.png',fit='cover',fy=0,wire='old',url='sitio-anterior',
  lockAt=bS5-1,recedeAt=19.45,animIn='rise',animDur=0.3,animOut='fade',scaleKf=[[17.1,1.1]])
L('mockup','Navegador · web nueva',19.5,bS8+E_,540,1160,860,480,kind='browser',asset='',fit='cover',fy=1,speed=0.7,wire='new',url='tu-web-nueva.cl',buildAt=19.7,dimAt=bS6,dimTo=0.35,
  animIn='slide',animDur=0.5,animOut='fade',move=[[19.5,540,1160],[20.7,540,1115]],scaleKf=[[19.5,1],[20.7,1.15]])
L('shape','Destello 5',20.9,bS6-0.1,930,520,90,90,kind='sparkle',color=BK,animIn='pop',animOut='fade',float=6)
# 6-7. La misma web se queda: cambia quien la administra y después el servidor. La pregunta se reemplaza en tres momentos.
halo('Halo 6',bS6,bS8+0.5,880,1500,SK,CO)
title('Pregunta intro',bS6+0.15,S7[0]-0.1,640,'Antes de\ncontratar,\n*pregunta*',size=100,h=330,accent=GR)
title('Pregunta 1',S7[0],Q2-0.05,600,'Si después quiero\ntrabajar con\notra persona',size=84,h=280,accent=GR,animDur=0.25)
title('Pregunta 2',Q2,Q3-0.05,600,'o cambiar\nde *hosting*',size=96,h=220,accent=GR,animDur=0.25)
title('Pregunta 3',Q3,bS8-0.2,600,'¿puedo hacerlo\nsin empezar\nde *cero*?',size=84,h=280,accent=GR,animDur=0.25)
pill('Administra tú',22.8,S7[0],380,1030,560,84,'Administra: tú',BK,IV,34,shadow=True)
pill('Administra otra persona',S7[0],bS8-0.1,380,1030,560,84,'Administra: otra persona',CO,BK,34,shadow=True)
pill('Servidor A',23.5,Q2,380,1130,560,84,'Servidor: hosting A',BK,IV,34,shadow=True)
pill('Servidor B',Q2,bS8-0.1,380,1130,560,84,'Servidor: hosting B',CO,BK,34,shadow=True)
pill('Sin empezar de cero',Q3,bS8-0.1,380,1230,560,84,'Sin empezar de cero',GR,BK,34,shadow=True)
# 8. Primero el cliente; después dominio y hosting conectados con él; tu acompañamiento al final
halo('Halo 8',bS8,bS9+0.5,200,1400,GR,SK)
title('Título 8',bS8+0.1,bS9-0.1,560,'Tú contratas\na tu nombre',size=100,h=280)
pill('Tuyo',32.0,bS9-0.05,800,945,320,250,'Tú',CO,BK,80,shadow=True)
pill('Dominio',32.9,bS9-0.05,330,880,480,110,'El dominio','#FFFFFF',BK,44,shadow=True)
L('shape','Línea dominio',33.2,bS9-0.05,615,902,110,10,kind='line',color=BK,stroke=6,rot=26.6,animIn='draw',animDur=0.35,animOut='fade')
pill('Hosting',33.6,bS9-0.05,330,1010,480,110,'El hosting',BK,IV,44)
L('shape','Línea hosting',33.9,bS9-0.05,615,988,110,10,kind='line',color=BK,stroke=6,rot=-26.6,animIn='draw',animDur=0.35,animOut='fade')
L('shape','Línea acompaño',34.6,bS9-0.05,800,1125,80,10,kind='line',color=BK,stroke=5,dash=12,rot=90,animIn='draw',animDur=0.3,animOut='fade')
pill('Yo te acompaño',34.5,bS9-0.05,800,1195,520,96,'Yo te acompaño',SU,BK,40)
# 9. Cierre: el botón está desde el inicio y pulsa cuando la voz dice "Escríbeme"
halo('Halo cierre',bS9,DUR,880,1560,CO,SU)
title('Título cierre',bS9+0.05,DUR,640,'¿Quieres crear\no renovar\ntu *web*?',size=100,h=420,animDur=0.3)
pill('Botón cierre',35.75,DUR,540,1150,720,130,'Escríbeme por WhatsApp',BK,IV,44,arrowIcon=True,arrowColor=CO,hitAt=37.45)
L('text','Tu nombre',36.2,DUR,540,1310,900,70,text='Úrsula HR',font='title',size=54,color=BK,align='center',animIn='rise',animDur=0.4)
L('text','Tu apoyo digital',36.4,DUR,540,1362,900,40,text='Tu apoyo digital',font='body',size=30,color=BK,tracking=0.18,caps=True,align='center',animIn='fade',animDur=0.4)

# ---- sonidos específicos y música ----
def snd(name,asset,start,vol):
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','/home/user/ursuhr.github.io/studio/assets/sfx/'+asset+'.mp3']).decode())
    L('sound',name,start,min(DUR,start+d),0,0,0,0,asset=asset,volume=vol)
snd('Golpe monto','golpe-1',0.75,0.3); snd('Montaje monto','whoosh-1',0.05,0.08)
for i,tt in enumerate([4.35,11.05,17.15,19.5,22.2,31.4]): snd(f'Whoosh {i+1}',f'whoosh-{1+i%2}',tt,0.12)
snd('Ventana entra','deslizar-1',bS2+0.2,0.2); snd('Ventana sale','deslizar-1',11.4,0.16)
snd('Clic 1','clic-1',C1,0.3); snd('Clic 2','clic-1',C2,0.3); snd('Bloqueo permisos','bloqueo-1',LOCK,0.3)
snd('Pop candado','pop-2',11.2,0.12); snd('Llave se desliza','deslizar-1',12.0,0.14)
snd('Pop etiqueta','pop-1',14.45,0.14); snd('Golpe etiqueta','golpe-1',14.72,0.2); snd('Bloqueo candado','bloqueo-1',14.76,0.22)
snd('Ventana se aleja','deslizar-1',19.45,0.15)
for i,tt in enumerate([22.8,23.5,S7[0],Q2,Q3]): snd(f'Pop etiqueta {i+1}',f'pop-{1+i%2}',tt,0.12)
for i,tt in enumerate([S7[0],Q2,Q3]): snd(f'Tick pregunta {i+1}','tick-1',tt,0.16)
for i,tt in enumerate([32.0,32.9,33.6,34.5]): snd(f'Pop trabajo {i+1}',f'pop-{1+i%2}',tt,0.12)
for i,tt in enumerate([33.2,33.9,34.6]): snd(f'Clic línea {i+1}','clic-1',tt,0.2)
snd('Pop botón','pop-2',35.75,0.12); snd('Campanita botón final','chime-1',37.45,0.14)
L('sound','Música de fondo',0,DUR,0,0,0,0,asset='musica-1',volume=0.07,fadeIn=1.5,fadeOut=3.0)

for i,((a,b),txt) in enumerate(CAP):
    L('caption',f'Subtítulos {i+1}',a,b,540,1450,960,110,text=txt,size=52,capStyle='pill',maxWords=6,accent=CO)

proj=dict(template='clienta-200k',rev=7,name='Reel · Los $200.000 por las claves',width=1080,height=1920,fps=30,duration=DUR,background=IV,
 voiceover=' '.join(t for _,t in CAP),layers=layers)
json.dump(proj,open('/home/user/ursuhr.github.io/studio/projects/clienta-200k.json','w'),ensure_ascii=False,indent=1)
print(len(layers),'capas · duración',DUR,'s')
