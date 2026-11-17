"""Corrección de color del reel de fideos de Neko Ramen (estética yokocho: cálida, íntima, sombras profundas).

Dos pasos por clip: 1) igualar exposición, contraste y balance de blancos entre escenas, 2) un look común
(sombras y medios tonos ámbar, viñeteado leve). Cada clip lleva sus propios valores porque se grabaron con luz distinta.
Todo son cadenas de filtros de ffmpeg; se editan aquí y make_neko_base.py las aplica.
"""
# paso 2: look común. Solo se mueve la temperatura de sombras, medios y luces; la comida no se tiñe.
LOOK = 'colorbalance=rs=0.02:bs=-0.03:rm={rm}:bm={bm}:rh={rh}:bh={bh}'

def look(rm=0.03, bm=-0.04, rh=0.03, bh=-0.05):
    return LOOK.format(rm=rm, bm=bm, rh=rh, bh=bh)

GRADES = {
    # máquina: el azul baja a un azul oscuro poco saturado; los fideos conservan su dorado
    '8186': "huesaturation=colors=c+b:saturation=-0.6:intensity=-0.45,"
            "eq=contrast=1.12:gamma=0.95," + look(0.07, -0.09, 0.05, -0.07) + ",vignette=PI/7",
    # preparación: las tres escenas se igualan entre sí (contraste, negros, exposición y temperatura)
    '8181': "eq=contrast=1.22:gamma=0.88:saturation=1.0,curves=all='0/0 0.12/0.04 0.5/0.46 0.85/0.78 1/0.93',"
            + look(0.03, -0.04, 0.03, -0.04) + ",vignette=PI/6.5",
    '8182': "eq=contrast=1.22:gamma=0.84:saturation=1.05,curves=all='0/0 0.12/0.04 0.5/0.46 0.85/0.78 1/0.93',"
            + look(0.09, -0.11, 0.06, -0.08) + ",vignette=PI/6.5",
    '8184': "eq=contrast=1.22:gamma=0.82:saturation=1.05,curves=all='0/0 0.12/0.04 0.5/0.46 0.85/0.78 1/0.93',"
            + look(0.08, -0.10, 0.06, -0.08) + ",vignette=PI/6.5",
    # palillos: menos luz y menos frío, sin oscurecer la comida
    '4716': "eq=contrast=1.1:brightness=-0.03,curves=all='0/0 0.12/0.05 0.5/0.48 0.85/0.8 1/0.92',"
            + look(0.04, -0.05, 0.03, -0.05) + ",vignette=PI/7",
    # foto cenital: la mesa verde baja de protagonismo
    'photo': "huesaturation=colors=g:saturation=-0.45:intensity=-0.35,eq=contrast=1.1:gamma=0.95,"
             + look(0.04, -0.05, 0.03, -0.05) + ",vignette=PI/7",
}
