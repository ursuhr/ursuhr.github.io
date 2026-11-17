import json, itertools, re, subprocess
IV,BK,CO,SU,GR,SK='#F5F1E8','#0B0B0B','#FF6BA7','#FFD357','#34D399','#6EC6FF'
n=itertools.count(1); layers=[]
def L(type,name,start,end,x,y,w,h=100,**k):
    d=dict(id=f"l{next(n):02d}",type=type,name=name,start=round(start,2),end=round(end,2),x=x,y=y,w=w,h=h,rot=0,opacity=1,animIn='none',animOut='none',animDur=0.45)
    d.update(k); layers.append(d); return d

# ---- guion (voz) y subtítulos. La voz dice "punto ce ele"; el subtítulo muestra ".cl"
S=[("Si tu diseñador desaparece mañana, ¿puedes seguir administrando tu web?","Si tu diseñador desaparece mañana, ¿puedes seguir administrando tu web?"),
("Revisa tres cosas.","Revisa tres cosas."),
("Uno: el dominio, la dirección de tu página, a tu nombre o al de tu empresa.","Uno: el dominio, la dirección de tu página, a tu nombre o al de tu empresa."),
("Si termina en punto ce ele, revisa el titular en NIC Chile.","Si termina en .cl, revisa el titular en NIC Chile."),
("Dos: el hosting, donde se guarda tu web, en una cuenta que tú controles.","Dos: el hosting, donde se guarda tu web, en una cuenta que tú controles."),
("Tres: tu propio usuario de administrador en WordPress.","Tres: tu propio usuario de administrador en WordPress."),
("Así trabajo yo: te asesoro y tú contratas el dominio y el hosting a tu nombre.","Así trabajo yo: te asesoro y tú contratas el dominio y el hosting a tu nombre."),
("¿Quieres crear o renovar tu web? Escríbeme por WhatsApp.","¿Quieres crear o renovar tu web? Escríbeme por WhatsApp.")]
def syl(t): return max(1,len(re.findall(r'[aeiouáéíóúü]+',t.lower())))
# duración estimada de la voz: ~5,8 sílabas por segundo + pausa entre frases (se ajusta al cargar el audio real)
W=[]; t=0.1
for v,_ in S:
    d=syl(v)/5.8+ (0.25 if ':' in v else 0); W.append((round(t,2),round(t+d,2))); t+=d+0.45
DUR=round(W[-1][1]+1.2,1)
bA,bB,bC,bD,bE,bF=0,W[2][0]-0.15,W[4][0]-0.15,W[5][0]-0.15,W[6][0]-0.15,W[7][0]-0.15
E_=0.15
def halo(name,a,b,x,y,c1,c2): L('shape',name,a,b,x,y,1100,1100,kind='halo',color=c1,color2=c2,animIn='fade',animOut='fade',animDur=0.8)
def number(num,a,b): L('text',f'Número {num}',a,b,540,430,900,260,text=num,font='title',size=250,color=CO,align='left',animIn='rise',animOut='fade')
def title(name,a,b,y,text,size=92,h=120): L('text',name,a,b,540,y,900,h,text=text,font='title',size=size,color=BK,accent=GR,align='left',lh=1.05,animIn='rise',animOut='fade')
def sub(name,a,b,y,text): L('text',name,a,b,540,y,860,70,text=text,font='body',size=50,color=BK,align='left',animIn='fade',animOut='fade')
def pill(name,a,b,cx,y,w,h,label,fill,fg,size,**k): L('shape',name,a,b,cx,y,w,h,kind='pill',color=fill,label=label,labelColor=fg,labelSize=size,animIn='pop',animOut='fade',**k)

L('logo','Logo HR',0,DUR,190,190,150,100,variant='dark')
L('shape','Flecha',0,DUR,900,190,64,64,kind='arrow',color=BK)

# A: gancho
halo('Halo gancho',bA,bB+0.5,880,1560,SK,GR)
L('shape','Destello',0.3,bB+E_,940,380,80,80,kind='sparkle',color=BK,animIn='pop',animOut='fade',float=6)
title('Título gancho',0,bB+E_,640,'¿Puedes seguir\nadministrando\ntu *web*?',size=92,h=420)
pill('Revisa tres cosas',W[1][0]+0.2,bB+E_,100+320,1100,640,110,'Revisa 3 cosas hoy',BK,IV,42)
# B: dominio
halo('Halo 01',bB,bC+0.5,200,1500,CO,SU)
number('01',bB,bC+E_); title('Título 01',bB+0.2,bC+E_,690,'El dominio')
sub('Bajada 01',bB+0.5,bC+E_,800,'La dirección de tu página')
pill('A tu nombre',W[2][0]+2.6,bC+E_,100+380,895,760,100,'A tu nombre o al de tu empresa','#FFFFFF',BK,34,shadow=True)
L('mockup','Navegador · NIC Chile',W[3][0]-0.2,bC+E_,540,1190,880,440,kind='browser',asset='',url='nic.cl',fit='cover',placeholder='Aquí va tu búsqueda en NIC Chile (ursulahr.cl)',animIn='rise',animOut='fade')
# C: hosting
halo('Halo 02',bC,bD+0.5,880,1400,SU,CO)
number('02',bC,bD+E_); title('Título 02',bC+0.2,bD+E_,690,'El hosting')
sub('Bajada 02',bC+0.5,bD+E_,800,'Donde se guarda tu web')
pill('Cuenta que controlas',W[4][0]+2.6,bD+E_,100+400,980,800,110,'En una cuenta que tú controles',BK,IV,36)
# D: administrador
halo('Halo 03',bD,bE+0.5,200,1350,GR,SK)
number('03',bD,bE+E_); title('Título 03',bD+0.2,bE+E_,720,'Usuario\nadministrador',h=230)
sub('Bajada 03',bD+0.5,bE+E_,900,'En WordPress')
pill('Acceso propio',W[5][0]+1.6,bE+E_,100+260,1030,520,100,'Tu propio acceso','#FFFFFF',BK,40,shadow=True)
# E: así trabajo
halo('Halo 04',bE,bF+0.5,850,1300,SK,GR)
title('Título 04',bE,bF+E_,560,'Así\ntrabajo yo',size=120,h=300)
pill('Yo te asesoro',W[6][0]+1.8,bF+E_,100+280,900,560,100,'Yo te asesoro','#FFFFFF',BK,40,shadow=True)
pill('Tú compras',W[6][0]+3.4,bF+E_,100+400,1030,800,100,'Tú contratas a tu nombre',BK,IV,38)
# F: cierre
halo('Halo cierre',bF,DUR,880,1560,CO,SU)
L('shape','Destello 2',bF+0.3,DUR,930,420,90,90,kind='sparkle',color=BK,animIn='pop',float=6)
title('Título cierre',bF,DUR,640,'¿Quieres crear\no renovar\ntu *web*?',size=100,h=420)
pill('Botón cierre',W[7][0]+1.6,DUR,540,1150,560,130,'Escríbeme',BK,IV,48,arrowIcon=True,arrowColor=CO,float=5)

# sonidos
def snd(name,asset,start,vol):
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','/home/user/ursuhr.github.io/studio/assets/sfx/'+asset+'.mp3']).decode())
    L('sound',name,start,min(DUR,start+d),0,0,0,0,asset=asset,volume=vol)
for i,tt in enumerate([0.05,bB+0.2,bC+0.2,bD+0.2,bE+0.05,bF+0.05]): snd(f'Whoosh {i+1}',f'whoosh-{1+i%2}',tt,0.12)
for i,tt in enumerate([bB,bC,bD]): snd(f'Tick número 0{i+1}','tick-1',tt,0.16)
pops=[W[1][0]+0.2,W[2][0]+2.6,W[4][0]+2.6,W[5][0]+1.6,W[6][0]+1.8,W[6][0]+3.4]
for i,tt in enumerate(pops): snd(f'Pop {i+1}',f'pop-{1+i%2}',tt,0.12)
snd('Campanita botón final','chime-1',W[7][0]+1.6,0.14)
L('sound','Música de fondo',0,DUR,0,0,0,0,asset='musica-2',volume=0.07,fadeIn=1.5,fadeOut=3.0)

# subtítulos (una capa por frase)
for i,(v,c) in enumerate(S):
    L('caption',f'Subtítulos {i+1}',W[i][0],W[i][1],540,1450,960,110,text=c,size=52,capStyle='pill',maxWords=4,accent=CO)

proj=dict(template='a-tu-nombre',rev=1,name='Reel · ¿Tu web está a tu nombre?',width=1080,height=1920,fps=30,duration=DUR,background=IV,
 voiceover=' '.join(v for v,_ in S),layers=layers)
json.dump(proj,open('/home/user/ursuhr.github.io/studio/projects/a-tu-nombre.json','w'),ensure_ascii=False,indent=1)
print(len(layers),'capas · duración estimada',DUR,'s'); print([w for w in W])
