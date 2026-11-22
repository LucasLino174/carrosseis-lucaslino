"""Capa 3D: braço em flexão de cotovelo (rosca), vista anterolateral 3/4.
Camadas: úmero (cabeça, diáfise, epicôndilos, tróclea/capítulo), rádio e ulna (olécrano),
deltoide, bíceps braquial (cabeça longa e curta, em verde-água, com fibras), tendões
proximais e distal + aponeurose bicipital, braquial, tríceps com tendão, braquiorradial
e grupos do antebraço, artéria braquial, veia cefálica e nervo mediano.
Tema: treino de força / sarcopenia."""
import math
from ilustracoes._base import frame
from ilustracoes._malha3d import (Cena, render, FILTROS_3D, OSSO, CORTICAL, TEAL, MUSCULO, MUSCULO_ESC, TENDAO,
                                  NERVO, VASO, Mat, add, mul, norm, sub, lerp3, dot)

S = (-62.0, 44.0, 0.0)    # centro da cabeça do úmero (ombro)
E = (30.0, -30.0, 0.0)    # cotovelo (centro da tróclea)
D = norm(sub(E, S))        # eixo do úmero
_A0 = (-D[1], D[0], 0.0)
_A0 = _A0 if _A0[1] > 0 else mul(_A0, -1)
_Z0 = (0.0, 0.0, 1.0)
_ROT = math.radians(30)    # gira o braço para mostrar a face anterior (3/4)
ANT = add(mul(_A0, math.cos(_ROT)), mul(_Z0, math.sin(_ROT)))
Z = add(mul(_A0, -math.sin(_ROT)), mul(_Z0, math.cos(_ROT)))   # lateral
POS = mul(ANT, -1)
_FLEX = math.radians(96)  # ângulo entre úmero e antebraço (rosca no meio do movimento)
_PF = norm(add(mul(_A0, .97), mul(_Z0, .24)))  # plano de flexão quase no plano da imagem (antebraço sai do quadro)
F = norm(add(mul(D, math.cos(_FLEX)), mul(_PF, math.sin(_FLEX))))
W = add(E, mul(F, 150))
FA = norm(sub(mul(D, -1), mul(F, dot(mul(D, -1), F))))  # "anterior" do antebraço (lado do bíceps)

def H(t, a=0.0, z=0.0):
    """Ponto ao longo do úmero (t de 0 ombro a 1 cotovelo), deslocado a anterior e z lateral."""
    return add(add(lerp3(S, E, t), mul(ANT, a)), mul(Z, z))

def A(t, a=0.0, z=0.0):
    """Ponto ao longo do antebraço (t de 0 cotovelo a 1 punho)."""
    return add(add(lerp3(E, W, t), mul(FA, a)), mul(Z, z))

VEIA = Mat("#1D2D4A", "#4F6E9E", "#AFC6E8", spec=.6, exp=40)

def ossos(sc):
    sc.vies = -6
    sc.elipsoide(S, (13, 13, 13), CORTICAL, n=30, m=16)
    sc.tubo([H(.05, 0, 0), H(.35, .5, 0), H(.7, 0, 0), H(.9, -.5, 0)], [7.2, 5.6, 5.4, 6.8], OSSO, n=24)
    # epicôndilos (medial maior, lateral menor) + tróclea e capítulo
    sc.elipsoide(H(.96, -1, -12), (5.6, 5.0, 6.0), CORTICAL, n=22, m=12)
    sc.elipsoide(H(.96, -1, 10), (4.4, 4.2, 4.6), CORTICAL, n=22, m=12)
    sc.tubo([H(1.0, 1, -9), H(1.0, 1.5, 0), H(1.0, 1, 8)], [6.0, 5.2, 5.6], CORTICAL, n=24)
    # ulna: olécrano atrás do cotovelo, diáfise até o punho (medial)
    ole = add(H(.98, -9, -3), mul(D, 3))
    sc.elipsoide(ole, (6.0, 7.0, 5.6), CORTICAL, n=22, m=12)
    sc.tubo([ole, A(.08, -5, -3), A(.5, -4, -3), A(1.0, -3, -2), A(1.15, -3, -2)], [5.2, 3.6, 2.6, 3.0, 1.0], OSSO, n=22)
    # rádio: cabeça junto ao capítulo, tuberosidade, alarga no punho
    sc.tubo([A(.04, 1, 7), A(.15, 1, 5), A(.6, 0, 3), A(1.0, 0, 3), A(1.15, 0, 3)], [4.6, 3.0, 2.8, 3.6, 1.0], OSSO, n=22)

def musculos(sc):
    sc.vies = 0
    # tríceps (posterior): cabeça longa + lateral, termina no tendão do olécrano
    sc.tubo([H(.0, -6, -3), H(.25, -12, -1), H(.55, -15, 1), H(.82, -12, 0), H(.95, -9, -2)],
            [8, 12, 14, 11, 6], MUSCULO_ESC, n=30, fibras=2, fibra_op=.28, achatar=.95)
    sc.tubo([H(.1, -8, 6), H(.4, -14, 9), H(.7, -13, 8), H(.88, -10, 5)], [7, 10, 9, 5], MUSCULO, n=28, fibras=2, fibra_op=.3)
    sc.tubo([H(.72, -13, 3), H(.86, -11, 1), H(.97, -9.5, -1)], [(7, 3), (6, 2.5), (5, 2.4)], TENDAO, n=20, fibras=2, fibra_op=.5, cima=(0, 0, 1))
    # braquial (sob o bíceps, metade distal)
    sc.tubo([H(.42, 5, 3), H(.65, 8, 5), H(.86, 8, 4), add(A(.12, 3, -2), (0, 0, 0))], [5, 10, 10, 4], MUSCULO, n=28, fibras=2, fibra_op=.3)
    # deltoide: leque sobre o ombro até a tuberosidade deltoidea
    for k, (a0, z0) in enumerate(((10, 4), (0, 12), (-10, 6))):
        sc.tubo([add(S, (a0 * .4 - 4, 14, z0)), add(S, (a0 * .5 + 4, 4, z0 + 4)), H(.3, a0 * .25, 7), H(.48, 0, 6)],
                [10, 11, 7, 2.5], MUSCULO if k != 2 else MUSCULO_ESC, n=26, fibras=2, fibra_op=.3)
    sc.vies = 1
    # antebraço: braquiorradial (lateral) + extensores (posterolateral) + flexores (medial)
    sc.vies = 3
    sc.tubo([H(.70, 4, 8), H(.92, 6, 9), A(.12, 5, 8), A(.45, 3, 7), A(.85, 2, 5), A(1.1, 1, 4)], [3, 8, 10.5, 8, 4, 2.5],
            MUSCULO, n=28, fibras=2, fibra_op=.3)
    sc.vies = -1
    sc.tubo([H(.95, -5, 9), A(.15, -7, 4), A(.55, -6, 2), A(.95, -4, 1), A(1.1, -4, 1)], [5, 9.5, 7.5, 4, 2.5], MUSCULO_ESC, n=28, fibras=2, fibra_op=.28)
    sc.tubo([H(.97, 0, -13), A(.15, 3, -8), A(.55, 2, -7), A(.95, 1, -5), A(1.1, 1, -4)], [5, 10, 8, 4, 2.5], MUSCULO_ESC, n=28, fibras=2, fibra_op=.28)

def biceps(sc):
    sc.vies = 2
    # cabeça longa (lateral) e curta (medial) se unindo num ventre só
    sc.tubo([H(.12, 9, 4), H(.3, 14, 4), H(.5, 17, 3), H(.68, 15, 2)], [4, 8, 10, 9], TEAL, n=30, fibras=2, fibra_op=.4)
    sc.tubo([H(.14, 9, -5), H(.3, 13, -5), H(.5, 16, -3), H(.68, 15, -1)], [4, 7.5, 9.5, 9], TEAL, n=30, fibras=2, fibra_op=.4)
    sc.tubo([H(.42, 15, 0), H(.56, 19, 1), H(.72, 17, 1), H(.84, 12, 1)], [(9, 8), (13.5, 11.5), (11, 9.5), (5.5, 4.6)], TEAL, n=36, fibras=2, fibra_op=.42)
    # tendões proximais (sulco intertubercular / coracoide)
    sc.tubo([add(S, (6, 13, 5)), H(.04, 7, 4), H(.14, 9, 4)], [1.6, 1.8, 2.6], TENDAO, n=14, fibras=0)
    sc.tubo([add(S, (14, 8, -9)), H(.06, 8, -6), H(.16, 9, -5)], [1.6, 1.8, 2.6], TENDAO, n=14, fibras=0)
    # tendão distal até a tuberosidade do rádio + aponeurose bicipital (por cima do antebraço)
    sc.vies = 2.5
    sc.tubo([H(.82, 12, 1), H(.92, 8, 2), A(.06, 5, 5), A(.14, 3, 7)], [(4.5, 3.6), (3.2, 2.6), (2.6, 2.2), (2.2, 2.0)], TENDAO, n=20, fibras=2, fibra_op=.5)

def feixe(sc):
    # artéria braquial, veia cefálica e nervo mediano no sulco medial/lateral
    sc.tubo([H(.1, 4, -11), H(.5, 2, -13), H(.88, 4, -11), A(.12, 4, -6)], [1.9, 1.9, 1.8, 1.6], VASO, n=14)
    sc.tubo([H(.1, 2, -13.5), H(.5, 0, -15), H(.9, 2, -12.5), A(.14, 3, -8)], [1.5, 1.5, 1.4, 1.3], NERVO, n=14, fibras=2, fibra_op=.4)
    sc.tubo([H(.0, 12, 10), H(.4, 13, 12), H(.8, 8, 13), A(.3, 6, 14), A(.8, 4, 12)], [1.4, 1.5, 1.5, 1.4, 1.3], VEIA, n=14)

def cover_svg(B, BD, LIGHT_BG):
    escuro = sum(int(LIGHT_BG[k:k + 2], 16) for k in (1, 3, 5)) < 300
    sc = Cena(yaw=-28, pitch=12, roll=8, escala=2.45, centro=(196, 290), luz=(-0.45, 0.8, 0.5),
              fundo=LIGHT_BG, nevoa=.45 if escuro else .32, prof=(-40, 40))
    ossos(sc)
    musculos(sc)
    biceps(sc)
    bx, by = sc.projetar(H(.56, 19, 1))
    sc.brilho(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="58" ry="40" fill="{B}" opacity=".22" filter="url(#brilhoT)"/>')
    content = render(sc)
    return frame(content, B, glow=(205, 250, 200, 170), fade_v=(0, .04, .2, .8, .96), fade_h=(0, .05, .9, 1),
                 defs_extra=FILTROS_3D, glow_op=.30 if escuro else .40)
