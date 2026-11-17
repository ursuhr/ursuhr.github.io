"""Parámetros de la gradación por clip (ver neko_look.py)."""
PARAMS = {
    # máquina: el producto son los fideos (dorados al crecer, claros y neutros en el barrido); el azul baja a azul muy oscuro
    '8186':  dict(exp=1.0, pool=(0.5, 0.62, 0.95, 0.75), k_rad=0.35, amb=0.22, lit=0.95, lit_sat=0.88, blue_dark=0.62, bright_key=True, contrast=0.32),
    '8186b': dict(exp=1.0, pool=(0.5, 0.35, 0.95, 0.75), k_rad=0.35, amb=0.22, lit=0.95, lit_sat=0.88, blue_dark=0.62, bright_key=True, contrast=0.32),
    # preparación: sombras profundas en la maquinaria y luz cálida sobre la masa y las manos (las tres escenas se igualan entre sí)
    '8181': dict(black=0.03, wb=(1.0, 0.99, 1.10), exp=1.0, pool=(0.6, 0.6, 0.85, 0.75), k_rad=0.4, amb=0.22, lit=0.95, lit_sat=0.9, contrast=0.36),
    '8182': dict(black=0.03, exp=0.92, pool=(0.5, 0.55, 0.9, 0.75), k_rad=0.4, amb=0.22, lit=0.95, lit_sat=0.95, contrast=0.36),
    '8184': dict(black=0.03, exp=0.88, pool=(0.5, 0.6, 0.9, 0.75), k_rad=0.4, amb=0.22, lit=0.95, lit_sat=0.95, contrast=0.36),
    # ramen terminado: la comida es lo más iluminado y el bowl no se oscurece; el fondo (pared, ventanas) cae al ambiente
    '4716': dict(exp=0.95, pool=(0.5, 0.7, 0.8, 0.7), k_rad=0.7, k_subj=0.6, amb=0.2, lit=1.0, lit_sat=0.95, contrast=0.32),
}
