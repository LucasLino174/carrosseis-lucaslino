"""Capa 3D: perna e tornozelo em vista posterolateral 3/4, tendão de Aquiles em verde-água.
Camadas: tíbia, fíbula (maléolo lateral), tálus, calcâneo (tuberosidade), cuboide,
navicular, metatarsos; gastrocnêmio (2 cabeças) e sóleo com fibras; tendão de Aquiles
(fibras torcidas, cintura na porção média) com paratendão; gordura de Kager; tendões
fibulares atrás do maléolo; flexor longo do hálux; ligamentos calcaneofibular e
talofibular; fáscia plantar. Tema: tendinopatia e carga progressiva."""
import math
from ilustracoes._base import frame
from ilustracoes._malha3d import (Cena, render, FILTROS_3D, OSSO, CORTICAL, TEAL, MUSCULO, MUSCULO_ESC, TENDAO,
                                  LIGAMENTO, Mat, add, mul)

TEAL_T = Mat("#13524A", "#4DB0A3", "#D2F7F1", spec=.8, exp=50, borda="#E0FFFA", fibra="#185F56", sss=.15)
GORDURA = Mat("#8A6A24", "#E6C46A", "#FFF1C4", spec=.5, exp=30, op=.9, sss=.3)
PARATENDAO = Mat("#5E8C86", "#CFEDE8", "#FFFFFF", spec=.8, exp=50, op=.28, sss=.4)

def ossos(sc):
    sc.vies = -8
    # tíbia (anterior/medial) e fíbula (lateral, posterior)
    sc.tubo([(-6, 260, -2), (-5, 150, -2), (-4, 60, -2), (-3, 22, -3)], [12, 10, 10.5, 13], OSSO, n=30)
    sc.elipsoide((-2, 12, -12), (8, 9, 5.5), CORTICAL, n=24, m=12)         # maléolo medial
    sc.tubo([(4, 255, 11), (5, 150, 12), (5, 50, 13), (4, 20, 14)], [5, 3.6, 3.8, 5], OSSO, n=22)
    sc.elipsoide((4, 8, 15), (7, 11, 5.5), CORTICAL, n=24, m=12)           # maléolo lateral
    # tálus e calcâneo (tuberosidade posterior onde o Aquiles se insere)
    sc.elipsoide((-4, 2, 0), (14, 9, 11), CORTICAL, n=28, m=14)
    def calc_def(p, th, ph):
        x, y, z = p
        y += -3 * math.exp(-((x + 6) / 8) ** 2)                 # sustentáculo/face inferior
        y += 4 * math.exp(-((x - 18) / 6) ** 2) * (1 if y > 0 else 0)  # bursa/tuberosidade
        return (x, y, z * (1 - .15 * (x > 10)))
    sc.elipsoide((10, -12, 1), (26, 12, 11), OSSO, n=34, m=16, deform=calc_def)
    sc.elipsoide((-26, -10, 6), (9, 7, 8), OSSO, n=22, m=12)     # cuboide
    sc.elipsoide((-24, 0, -6), (8, 8, 9), OSSO, n=22, m=12)      # navicular
    for k, z in enumerate((-10, -4, 1, 6)):                        # cuneiformes
        pass
    sc.elipsoide((-36, -2, -9), (7, 7, 5), OSSO, n=20, m=10)
    sc.elipsoide((-37, -3, -1), (7, 6.5, 4), OSSO, n=20, m=10)
    sc.elipsoide((-36, -5, 6), (7, 6, 4), OSSO, n=20, m=10)
    for k, z in enumerate((-12, -5, 2, 9, 15)):
        a = (-42, -6 - k * 1.2, z * .8); b = (-66, -15 - k * .8, z); c = (-90, -24 - k * .5, z * 1.1)
        sc.tubo([a, b, c], [4.6 - k * .3, 3.0 - k * .15, 3.6 - k * .2], OSSO, n=18)
        sc.elipsoide(c, (5 - k * .3, 4.6 - k * .3, 4.6 - k * .3), CORTICAL, n=16, m=8)

def partes_moles(sc):
    sc.vies = -4
    # gordura de Kager (entre o Aquiles e o flexor longo do hálux)
    sc.elipsoide((15, 34, 2), (8, 24, 9), GORDURA, n=24, m=14)
    # flexor longo do hálux (ventre profundo + tendão)
    sc.tubo([(6, 160, 2), (8, 100, 3), (8, 60, 3), (6, 30, 0)], [5, 8, 7, 3], MUSCULO_ESC, n=22, fibras=2, fibra_op=.25)
    sc.tubo([(6, 30, 0), (2, 8, -6), (-6, -10, -8), (-40, -22, -10)], [2.2, 2.0, 1.8, 1.6], TENDAO, n=12)
    # fibulares: ventres laterais + tendões passando atrás do maléolo lateral
    sc.vies = -2
    sc.tubo([(6, 230, 15), (8, 150, 17), (9, 80, 17), (9, 40, 17)], [6, 7.5, 6, 3], MUSCULO, n=24, fibras=2, fibra_op=.3)
    for dz, r in ((0, 2.3), (2.6, 1.8)):
        sc.tubo([(9, 40, 17 + dz), (10, 14, 19 + dz), (6, -2, 19 + dz), (-6, -10, 16 + dz), (-28, -14, 13 + dz)],
                [r, r, r, r * .9, r * .8], TENDAO, n=14, fibras=2, fibra_op=.4)
    # ligamentos laterais do tornozelo
    sc.vies = 1
    sc.tubo([(6, 0, 17), (12, -10, 14), (14, -14, 12)], [(2.6, 1.0), (2.4, 1.0), (2.6, 1.0)], LIGAMENTO, n=12, fibras=2, fibra_op=.5)
    sc.tubo([(0, 4, 18), (-6, 3, 13), (-10, 2, 9)], [(2.4, 1.0), (2.2, 1.0), (2.4, 1.0)], LIGAMENTO, n=12, fibras=2, fibra_op=.5)
    # fáscia plantar

def musculos(sc):
    sc.vies = 0
    # sóleo (largo, por baixo do gastrocnêmio, desce mais)
    sc.tubo([(8, 220, 2), (18, 160, 2), (22, 115, 2), (22, 85, 2), (22, 62, 2)], [(12, 16), (15, 21), (13, 18), (8, 11), (3, 4)],
            MUSCULO_ESC, n=32, fibras=2, fibra_op=.28)
    sc.vies = 2
    # gastrocnêmio: cabeça medial (maior, mais baixa) e lateral
    sc.tubo([(12, 280, -8), (26, 225, -9), (34, 175, -8), (32, 135, -4), (28, 108, -1), (26, 92, 0)], [9, 18, 21, 15, 8, 3], MUSCULO, n=32, fibras=2, fibra_op=.32)
    sc.tubo([(12, 280, 10), (26, 228, 11), (32, 185, 9), (30, 148, 6), (28, 118, 3), (26, 100, 2)], [8, 15, 17, 12, 7, 3], MUSCULO, n=32, fibras=2, fibra_op=.32)
    # aponeurose do gastrocnêmio (lâmina tendínea que vira o Aquiles)
    APO = Mat("#4C7E77", "#BDE7E0", "#F4FFFD", spec=.7, exp=44, fibra="#FFFFFF", op=.65)
    sc.vies = 3
    sc.tubo([(33, 160, 0), (31, 135, 0), (26, 112, 1)], [(12, 1.2), (11, 1.2), (8, 1.4)], APO, n=16, fibras=2, fibra_op=.5, cima=(1, 0, 0))

def aquiles(sc):
    sc.vies = 1
    # parte alta: some por baixo do tríceps sural
    sc.vies = -6
    sc.tubo([(28, 150, 1), (27, 128, 1), (26, 104, 1)], [(1.5, 3), (4.5, 8.0), (5.6, 7.6)], TEAL_T, n=40, fibras=2, fibra_op=.24, cima=(0, 0, 1))
    sc.vies = 1
    eixo = [(26, 106, 1), (24.5, 85, 1), (23, 58, 1), (22.5, 36, 1), (23.5, 16, 1), (26.5, 4, 1), (28, -6, 1)]
    # oval, leve espessamento fusiforme na porção média (onde a tendinopatia é mais comum,
    # 2-6 cm acima da inserção) e alarga na inserção
    raios = [(5.6, 7.6), (6.0, 7.0), (6.4, 6.8), (7.4, 7.6), (6.4, 7.2), (6.4, 9.0), (5.0, 8.4)]
    sc.tubo(eixo, raios, TEAL_T, n=40, m=90, fibras=2, fibra_op=.24, torcer=math.radians(40), cima=(0, 0, 1), tampas=False)
    return (22.5, 36, 1)

def cover_svg(B, BD, LIGHT_BG):
    escuro = sum(int(LIGHT_BG[k:k + 2], 16) for k in (1, 3, 5)) < 300
    sc = Cena(yaw=-62, pitch=10, roll=3, escala=2.35, centro=(200, 226), luz=(-0.5, 0.5, 0.7),
              fundo=LIGHT_BG, nevoa=.45 if escuro else .3, prof=(-50, 50))
    ossos(sc)
    partes_moles(sc)
    musculos(sc)
    alvo = aquiles(sc)
    hx, hy = sc.projetar(alvo)
    sc.brilho(f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="34" ry="80" fill="{B}" opacity=".35" filter="url(#brilhoT)"/>')
    content = render(sc)
    return frame(content, B, glow=(220, 230, 190, 190), fade_v=(0, .0, .14, .64, .86), fade_h=(.06, .34, .94, 1),
                 defs_extra=FILTROS_3D, glow_op=.30 if escuro else .42)
