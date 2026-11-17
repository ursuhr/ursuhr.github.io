import json, itertools, subprocess
IV,BK,CO,SU,GR,SK='#F5F1E8','#0B0B0B','#FF6BA7','#FFD357','#34D399','#6EC6FF'
n=itertools.count(1); layers=[]
def L(type,name,start,end,x,y,w,h=100,**k):
    d=dict(id=f"l{next(n):02d}",type=type,name=name,start=round(start,2),end=round(end,2),x=x,y=y,w=w,h=h,rot=0,opacity=1,animIn='none',animOut='none',animDur=0.45)
    d.update(k); layers.append(d); return d

DUR=41.5
# ---- tiempos REALES de la voz clonada (medidos con silencedetect en voz_millon.mp3, 39,47 s) ----
V=dict(s1=(0.0,1.63),s2=(2.93,6.87),s3=(7.41,9.03),s4=(9.49,10.41),s5=(11.01,12.30),s6=(12.84,13.86),s7=(14.13,16.07),s8=(16.39,18.61),
 s9=(19.69,21.23),s10=(21.74,22.65),s11=(23.45,27.32),s12=(27.77,30.99),s13=(31.39,32.39),s14=(32.64,33.92),s15=(34.29,35.30),s16=(35.51,36.69),s17=(37.10,37.81),s18=(38.25,39.47))
CUT=19.64          # corte a negro: el monto sigue oculto hasta que la voz dice "millón"
BACK=23.0          # vuelve el marfil

def halo(name,a,z,x,y,c1,c2=None): L('shape',name,a,z,x,y,1100,1100,kind='halo',color=c1,opacity=0.3,animIn='fade',animOut='fade',animDur=0.8)
def title(name,a,z,y,text,size=96,h=260,**k):
    d=dict(animIn='rise',animOut='fade',animDur=0.3,accent=CO); d.update(k)
    L('text',name,a,z,540,y,920,h,text=text,font='title',size=size,color=BK,align='center',lh=1.05,**d)
def pill(name,a,z,cx,y,w,h,label,fill,fg,size,**k):
    d=dict(animIn='pop',animOut='fade'); d.update(k)
    L('shape',name,a,z,cx,y,w,h,kind='pill',color=fill,label=label,labelColor=fg,labelSize=size,**d)

# ---- marca fija (cambia de versión sobre el fondo negro) ----
L('logo','Logo HR',0,CUT,190,190,150,100,variant='dark'); L('shape','Flecha',0,CUT,900,190,64,64,kind='arrow',color=BK)
L('logo','Logo HR · cierre',BACK,DUR,190,190,150,100,variant='dark'); L('shape','Flecha · cierre',BACK,DUR,900,190,64,64,kind='arrow',color=BK)

# ---- 1. Gancho: la foto, la línea que la señala y la solicitud escrita ----
halo('Halo 1',0,7.6,200,1350,SK)
L('shape','Foto de ejemplo',0.05,2.8,700,640,460,320,kind='photo',radius=30,rot=-3,animIn='pop',animOut='fade',animDur=0.3,shadow=True,
  move=[[0.05,700,650],[0.7,700,640]])
L('shape','Línea foto → mensaje',0.45,2.8,700,892,185,10,kind='line',color=BK,stroke=7,dash=14,rot=90,animIn='draw',animDur=0.35,animOut='fade')

# ---- Chat reconstruido (una sola capa, cámara interna) ----
M0,M1,W0,M2,M3=-60,330,720,960,960
msgs=[
 dict(from_='me',text='¿Podemos cambiar esta foto?',at=0.55,y=M0,maxW=640,out=None),
 dict(from_='me',text='¿Me ayudas con el cambio?',at=9.5,y=M1,maxW=640,dim=[[9.5,1],[10.3,0.5],[10.5,0.18]]),
 dict(kind='wait',at=10.45,until=12.3,y=W0,label='Sin respuesta',dim=[[10.45,1],[13.6,1],[14.3,0.3]]),
 dict(from_='them',text='Agenda llena por 4 meses',at=13.6,y=M2,maxW=560,type=0.95,hl='4 meses',hlAt=15.35,out=16.3),
 dict(from_='them',text='Si lo necesitas urgente, te cobro…',at=16.5,y=M2,maxW=720,type=1.3),
]
for m in msgs:
    if 'from_' in m: m['from']=m.pop('from_')
    if m.get('out',1) is None: m.pop('out')
msgs[0]['dim']=[[2.9,1],[3.3,0.5],[7.5,0.5],[7.9,1],[9.5,1],[10.3,0.5],[10.5,0.18]]; msgs[0]['out']=10.8
msgs[1]['dim']=[[9.5,1],[13.6,1],[14.3,0.3]]; msgs[1]['out']=13.75; msgs[2]['out']=13.75
L('chat','Chat reconstruido',0,CUT,540,900,960,1100,tag='',note='',size=62,
  alphaKf=[[0,1],[2.75,1],[3.2,0.1],[7.35,0.1],[7.75,1]],
  cam=[[0,1,-40,0],[2.7,1,-40,0],[3.3,0.9,40,0],[7.4,0.9,40,0],[7.9,1.3,97,110],[9.3,1.3,97,110],[10.1,1,292,0],[10.6,1,520,0],[12.8,1,520,0],[13.4,1,745,0],
       [13.9,1,900,0],[15.0,1,900,0],[15.45,1.36,1100,-130],[16.2,1.36,1100,-130],[16.65,1.1,1085,-60]],msgs=msgs,animIn='none',animOut='none')
# insignia mínima mientras el chat está atenuado
# ---- 2. "Un cliente me contó": la atribución ocupa el primer plano ----
title('Título · Un cliente me contó',2.95,4.05,760,'Un *cliente*\nme contó',size=124,h=330,animDur=0.25,accent=BK)
# ---- 3. El panel ilustrado ----
pill('Etiqueta panel',4.35,7.3,540,470,520,76,'Panel ilustrado',BK,IV,34)
PB=(540,980)
L('mockup','Panel · como me lo entregaron',4.15,7.45,PB[0],PB[1],900,640,kind='browser',asset='',wire='panel',url='panel-del-sitio.cl',buildAt=4.3,
  animIn='rise',animDur=0.4,animOut='slide',
  cursor=[[4.6,0.85,0.18],[5.4,0.62,0.46],[6.05,0.45,0.86],[7.6,0.45,0.86]],clicks=[6.35],menuAt=6.4,
  move=[[5.5,540,980],[6.1,560,690],[7.0,560,690]],scaleKf=[[5.5,1],[6.1,1.12],[7.0,1.12]])
# ---- 4. vuelve la solicitud en primer plano ----
# ---- 5. espera / respuesta: todo ocurre dentro de la capa de chat ----

# ---- 6. EL MILLÓN: negro + amarillo, solo cuando lo dice la voz ----
L('shape','Corte a negro',CUT,BACK+0.2,540,960,1080,1920,kind='rect',color=BK,animIn='none',animOut='fade',animDur=0.3)
L('logo','Logo HR (sobre negro)',CUT,BACK,190,190,150,100,variant='light'); L('shape','Flecha (sobre negro)',CUT,BACK,900,190,64,64,kind='arrow',color=IV)
L('text','Monto',19.92,22.75,540,860,1010,230,text='$1.000.000',font='title',size=146,color=SU,align='center',animIn='pop',animDur=0.22,animOut='fade',hitAt=19.92,
  scaleKf=[[19.92,1.22],[20.2,1]])
L('text','Aclaración monto',20.75,22.75,540,1100,900,50,text='Precio pedido por el cambio urgente',font='body',size=34,bold=True,color=IV,align='center',animIn='fade',animOut='fade',animDur=0.3)
L('shape','Foto junto al monto',21.74,22.75,540,560,440,310,kind='photo',radius=28,rot=2,animIn='pop',animOut='fade',animDur=0.25,shadow=False,
  move=[[21.74,540,578],[22.15,540,560]])

# ---- 7. Lo que debería ser: editar sin depender ----
halo('Halo 7',BACK,27.7,880,1450,SK)
BR=(540,1040)
L('mockup','Navegador · editar sin depender',BACK-0.05,27.75,BR[0],BR[1],900,640,kind='browser',asset='',wire='editor',url='tu-web.cl',buildAt=BACK+0.1,
  animIn='rise',animDur=0.45,animOut='slide',
  scaleKf=[[BACK,0.92],[25.2,1],[25.55,1.1],[27.3,1.1]],move=[[25.3,540,1040],[25.7,540,1060],[27.3,540,1060]])
title('Título · Poder hacer cambios',23.5,25.38,520,'Poder hacer\n*cambios*',size=100,h=260,animDur=0.25,accent=BK)
title('Título · Sin depender',25.55,27.55,520,'Sin *depender*\nde una respuesta',size=88,h=260,animDur=0.25,accent=BK)
# ---- 8. Dominio y hosting a tu nombre ----
halo('Halo 8',27.7,31.4,200,1350,SK)
def ficha(name,a,y,t1,t2,stamp_at):
    L('shape',name,a,31.35,540,y,820,210,kind='rect',color='#FFFFFF',radius=44,shadow=True,animIn='rise',animDur=0.4,animOut='fade')
    L('text',name+' · título',a+0.1,31.35,400,y-30,440,90,text=t1,font='title',size=60,color=BK,align='left',animIn='fade',animOut='fade',animDur=0.3)
    L('text',name+' · detalle',a+0.15,31.35,400,y+40,440,50,text=t2,font='body',size=32,bold=True,color=BK,align='left',animIn='fade',animOut='fade',animDur=0.3)
    pill(name+' · a tu nombre',stamp_at,31.35,740,y,300,84,'A tu nombre',CO,BK,34,animDur=0.25,hitAt=stamp_at+0.05,shadow=True)
ficha('Ficha Dominio',28.25,720,'Dominio','tunegocio.cl',30.25)
ficha('Ficha Hosting',29.0,980,'Hosting','donde vive tu web',30.5)
# ---- 9. Tú administras / te enseño a editarla ----
halo('Halo 9',31.3,37.0,880,1500,SK)
pill('Etiqueta ejemplo',31.5,34.2,540,390,540,70,'Ejemplo de mi servicio',BK,IV,32)
title('Título · Tú administras',31.45,32.55,560,'Tú *administras*',size=92,h=180,animDur=0.25)
title('Título · Te enseño a editarla',32.7,34.2,570,'Te enseño\na *editarla*',size=88,h=240,animDur=0.25)
L('mockup','Navegador · editando',31.3,37.0,540,1090,900,640,kind='browser',asset='',wire='editor',url='tu-web.cl',buildAt=31.4,animIn='rise',animDur=0.45,animOut='fade',
  selectAt=32.2,cursor=[[31.6,0.85,0.12],[32.2,0.62,0.4],[32.7,0.792,0.585],[34.4,0.792,0.585]],clicks=[32.95],swapAt=33.15,
  move=[[32.2,540,1090],[32.9,520,1090],[34.2,520,1090],[34.9,330,1140],[37.0,330,1140]],scaleKf=[[32.2,1],[32.9,1.06],[34.2,1.06],[34.9,0.62],[37.0,0.62]])
# ---- 10. Delegar ----
title('Título · Prefieres delegar',34.35,35.45,560,'¿Prefieres\n*delegar*?',size=100,h=260,animDur=0.25)
title('Título · Planes de mantención',35.55,37.05,560,'Planes de\n*mantención*',size=100,h=260,animDur=0.25)
pill('Píldora acompañamiento',35.0,37.0,720,1280,500,110,'Te acompaño',BK,IV,46,animDur=0.35,hitAt=35.55)
# ---- 11. Cierre ----
halo('Halo cierre',37.0,DUR,880,1560,CO)
title('Título · Creamos la tuya',37.0,DUR,520,'¿Creamos\n*la tuya*?',size=118,h=330,animDur=0.3)
L('text','Firma',37.15,DUR,540,820,960,60,text='Úrsula HR · Diseño web en Antofagasta',font='body',size=40,bold=True,color=BK,align='center',animIn='rise',animDur=0.4)
pill('Botón WhatsApp',37.2,DUR,540,1010,800,140,'Escríbeme por WhatsApp',BK,IV,46,arrowIcon=True,arrowColor=CO,hitAt=38.3,shadow=True,animDur=0.4)

# ---- subtítulos: cláusulas con sentido, tiempos de la voz real ----
def split(seg,parts):
    a,b=V[seg]; tot=sum(len(p) for p in parts); out=[]; t=a
    for p in parts:
        d=(b-a)*len(p)/tot; out.append((round(t,2),round(t+d,2),p)); t+=d
    return out
CAP=[]
CAP.append((*V['s1'],'Solo quería cambiar una foto.'))
CAP+=split('s2',['Un cliente me contó que','el panel que le entregaron','casi no le dejaba editar.'])
CAP.append((*V['s3'],'Así que dependía del desarrollador.'))
CAP.append((*V['s4'],'Escribía…')); CAP.append((*V['s5'],'y no recibía respuesta.'))
CAP.append((*V['s6'],'Hasta que le dijeron:')); CAP.append((*V['s7'],'agenda llena por cuatro meses.'))
CAP.append((*V['s8'],'Y ya, si lo necesitas urgente te cobro…'))
CAP.append((*V['s9'],'Un millón de pesos.')); CAP.append((*V['s10'],'Por una foto.'))
CAP+=split('s11',['Tu web debería dejarte hacer cambios','sin depender de que alguien te conteste.'])
CAP+=split('s12',['Conmigo, el dominio y el hosting','los contratas a tu nombre.'])
CAP.append((*V['s13'],'Tú administras tu web')); CAP.append((*V['s14'],'y yo te enseño a editarla.'))
CAP.append((*V['s15'],'Y si prefieres delegar,')); CAP.append((*V['s16'],'tengo planes de mantención.'))
CAP.append((*V['s17'],'¿Creamos la tuya?')); CAP.append((*V['s18'],'Escríbeme por WhatsApp.'))
for i,(a,b,txt) in enumerate(CAP):
    sty='plain-light' if 19.6<a<22.9 else 'pill'
    L('caption',f'Subtítulos {i+1}',a,b+0.05,540,1470,960,110,text=txt,size=54,capStyle=sty,maxWords=9,capAlign='center',accent='#FFFFFF')

# ---- sonido ----
def snd(name,asset,start,vol):
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','/home/user/ursuhr.github.io/studio/assets/sfx/'+asset+'.mp3']).decode())
    L('sound',name,start,min(DUR,start+d),0,0,0,0,asset=asset,volume=vol)
snd('Pop foto','pop-1',0.05,0.14)
for i,tt in enumerate([0.85,9.8,13.9,16.8]): snd(f'Tecleo {i+1}','tick-1',tt,0.1)
snd('Whoosh atribución','whoosh-1',2.92,0.1); snd('Pop panel','pop-2',4.2,0.12); snd('Clic panel','clic-1',6.35,0.25)
snd('Whoosh vuelve chat','whoosh-2',7.45,0.12); snd('Pop seguimiento','pop-1',9.5,0.12)
snd('Pop respuesta','pop-2',13.6,0.14); snd('Golpe 4 meses','golpe-1',15.4,0.16)
snd('Golpe millón','golpe-1',19.9,0.22)
snd('Whoosh vuelve marfil','whoosh-2',22.95,0.1)
snd('Whoosh cambios','whoosh-1',25.5,0.08)
snd('Pop dominio','pop-1',28.25,0.12); snd('Pop hosting','pop-2',29.0,0.12)
snd('Tick a tu nombre 1','tick-1',30.25,0.16); snd('Tick a tu nombre 2','tick-1',30.5,0.16)
snd('Whoosh edición','whoosh-1',31.3,0.1); snd('Clic cambiar imagen','clic-1',32.95,0.25); snd('Confirmación','chime-2',33.45,0.12)
snd('Se aleja el navegador','deslizar-1',34.45,0.12); snd('Pop acompañamiento','pop-2',35.0,0.12)
snd('Pop botón','pop-1',37.2,0.12); snd('Campanita botón','chime-1',38.3,0.14)
L('sound','Música A',0,18.5,0,0,0,0,asset='musica-1',volume=0.06,fadeIn=1.2,fadeOut=2.2)
L('sound','Música B (regresa tras el silencio)',22.3,DUR,0,0,0,0,asset='musica-1',volume=0.06,fadeIn=1.6,fadeOut=3.0)


# ---- reubicar todo sobre la voz nueva (clon actualizado, pausa inicial recortada) ----
NEWV=[(0.0, 1.63), (2.09, 6.37), (6.82, 8.6), (9.08, 9.88), (10.35, 11.73), (12.24, 13.18), (13.46, 15.84), (16.19, 18.78), (19.32, 20.6), (21.15, 21.98), (22.61, 27.04), (27.49, 30.86), (31.25, 32.25), (32.52, 33.7), (34.11, 35.12), (35.33, 36.55), (37.09, 37.79), (38.16, 39.38)]
OLDV=[V[k] for k in ['s1','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','s12','s13','s14','s15','s16','s17','s18']]
NEWDUR=round(NEWV[-1][1]+(DUR-OLDV[-1][1]),2)
anc=[(0.0,0.0)]
for (oa,ob),(na,nb) in zip(OLDV,NEWV): anc+= [(oa,na),(ob,nb)]
anc.append((DUR,NEWDUR))
def ft(t):
    if t<=anc[0][0]: return t
    for (o1,n1),(o2,n2) in zip(anc,anc[1:]):
        if t<=o2: return n1 if o2==o1 else n1+(n2-n1)*(t-o1)/(o2-o1)
    return t-DUR+NEWDUR
def rt(t): return round(ft(t),2)
def rkf(kf): return [[rt(k[0])]+k[1:] for k in kf]
SCAL=['start','end','at','until','out','hlAt','hitAt','buildAt','menuAt','selectAt','swapAt','lockAt','recedeAt','dimAt','shakeAt','noteUntil']
for l in layers:
    snd = l['type']=='sound' and not l['asset'].startswith('musica')
    if snd:
        d=l['end']-l['start']; l['start']=rt(l['start']); l['end']=round(min(NEWDUR,l['start']+d),2)
    else:
        for k in SCAL:
            if k in l and l[k] is not None: l[k]=rt(l[k])
    for k in ['move','scaleKf','cam','alphaKf','cursor']:
        if k in l and l[k]: l[k]=rkf(l[k])
    if 'clicks' in l: l['clicks']=[rt(c) for c in l['clicks']]
    if 'swing' in l and isinstance(l['swing'],dict): l['swing']['t0']=rt(l['swing']['t0'])
    for m in l.get('msgs',[]):
        for k in ['at','until','out','hlAt']:
            if k in m and m[k] is not None: m[k]=rt(m[k])
        if 'dim' in m: m['dim']=rkf(m['dim'])
DUR=NEWDUR
vo=['Solo quería cambiar una foto.','Un cliente me contó que el panel que le entregaron casi no le dejaba editar.','Así que dependía del desarrollador.','Escribía… y no recibía respuesta.','Hasta que le dijeron: agenda llena por cuatro meses.','Y ya, si lo necesitas urgente te cobro…','Un millón de pesos.','Por una foto.','Tu web debería dejarte hacer cambios sin depender de que alguien te conteste.','Conmigo, el dominio y el hosting los contratas a tu nombre.','Tú administras tu web y yo te enseño a editarla.','Y si prefieres delegar, tengo planes de mantención.','¿Creamos la tuya? Escríbeme por WhatsApp.']
proj=dict(template='millon-foto',rev=10,name='Reel · Un millón por cambiar una foto',width=1080,height=1920,fps=30,duration=DUR,background=IV,voiceover='\n\n'.join(vo),layers=layers)
json.dump(proj,open('/home/user/ursuhr.github.io/studio/projects/millon-foto.json','w'),ensure_ascii=False,indent=1)
print(len(layers),'capas · duración',DUR)
