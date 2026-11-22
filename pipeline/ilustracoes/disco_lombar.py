"""Capa 3D: segmento lombar (L4-L5) em vista explodida 3/4, disco em corte.
Camadas: corpo vertebral (osso cortical + platô), arco posterior (pedículos, lâminas,
processos espinhoso, transversos e articulares), disco com lamelas do anel fibroso,
núcleo pulposo herniando em direção à raiz nervosa, saco dural e raízes, ligamento
longitudinal anterior. Estrutura-alvo (disco/hérnia) em verde-água."""
import math
from ilustracoes._base import frame
from ilustracoes._malha3d import (Cena, render, FILTROS_3D, OSSO, CORTICAL, TEAL, ANEL, NUCLEO, NERVO,
                                  LIGAMENTO, Mat, add, interp1)

A, Bz = 26.0, 18.5   # semi-eixos do corpo vertebral (lateral x, ântero-posterior z)

def contorno(th, esc=1.0, rec=0.32):
    """Corte do corpo vertebral em forma de rim (borda posterior côncava)."""
    s = math.sin(th)
    x = A * math.cos(th)
    z = Bz * s + (Bz * rec * max(0.0, -s) ** 4)
    return x * esc, z * esc

def corpo(sc, y0, h, n=72, m=14, mat=OSSO):
    secs = []
    for i in range(m + 1):
        t = i / m
        y = y0 + h * t
        # cintura côncava no meio + bisel do anel apofisário nas bordas
        f = 1 - 0.07 * math.sin(math.pi * t) ** 1.5
        if t < .06 or t > .94:
            f *= .965 + .035 * (min(t, 1 - t) / .06)
        ring = []
        for j in range(n):
            th = 2 * math.pi * j / n
            x, z = contorno(th, f)
            ring.append((x, y, z))
        secs.append(ring)
    ao = lambda t, u: .82 + .18 * math.sin(math.pi * t) ** .5
    sc.loft(secs, mat, ao_fn=ao, fechar_topo=False)
    # platô vertebral: anel apofisário (cortical claro) + centro poroso mais escuro
    yt = y0 + h
    PLATO = Mat("#5E5240", "#B8A98C", "#E9DFC9", spec=.15, exp=10)
    import random
    rnd = random.Random(int(y0 * 10) + 3)
    for (e0, e1, mt, dy) in ((.965, .84, CORTICAL, .3), (.84, .0, PLATO, -.4)):
        for j in range(n):
            t0, t1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
            a0 = contorno(t0, e0); a1 = contorno(t1, e0); b0 = contorno(t0, max(e1, .001)); b1 = contorno(t1, max(e1, .001))
            extra = ""
            if mt is PLATO:  # poros do osso esponjoso, presos à face (respeitam a oclusão)
                for _ in range(2):
                    e = .12 + .68 * rnd.random(); th = t0 + (t1 - t0) * rnd.random()
                    x, z = contorno(th, e); p = sc.projetar((x, yt - .3, z)); r = .45 + rnd.random() * .9
                    extra += f'<ellipse cx="{p[0]:.1f}" cy="{p[1]:.1f}" rx="{r*1.3:.2f}" ry="{r*.7:.2f}" fill="#3B3226" opacity=".38"/>'
            sc.quad([(a0[0], yt, a0[1]), (a1[0], yt, a1[1]), (b1[0], yt + dy, b1[1]), (b0[0], yt + dy, b0[1])], mt, ref=(0, yt - 20, 0), extra=extra)

def arco(sc, y, sobe=1):
    """Arco posterior de uma vértebra lombar com o corpo na altura y (centro)."""
    zp = -Bz * (1 - .32) - 1
    for s in (-1, 1):
        # pedículo
        sc.tubo([(s * 13, y + 3, zp + 2), (s * 14, y + 3, zp - 6), (s * 14.5, y + 3, zp - 12)], [5.6, 5.0, 5.6], CORTICAL, n=22)
        # processo transverso (lombar: longo e achatado)
        sc.tubo([(s * 15, y + 4, zp - 12), (s * 28, y + 5, zp - 13), (s * 39, y + 6, zp - 16), (s * 42, y + 6.2, zp - 17)],
                [(4.2, 3.0), (3.4, 2.4), (3.0, 2.8), (1.2, 1.1)], OSSO, n=20, cima=(0, 1, 0))
        # processo articular superior (sobe, faceta voltada para trás/medial)
        sc.tubo([(s * 15, y + 4, zp - 13), (s * 16.5, y + 13, zp - 15), (s * 17, y + 20, zp - 17), (s * 17.1, y + 22.5, zp - 17.6)],
                [(4.6, 3.4), (4.3, 3.0), (3.6, 2.6), (1.1, 1.0)], OSSO, n=20)
        sc.elipsoide((s * 18.5, y + 16, zp - 17), (2.6, 4.4, 3.0), CORTICAL, n=18, m=10)  # processo mamilar
        # processo articular inferior (desce)
        sc.tubo([(s * 9, y - 1, zp - 21), (s * 11, y - 9, zp - 22), (s * 11.5, y - 15, zp - 21), (s * 11.6, y - 17.5, zp - 20.5)],
                [(4.0, 3.2), (3.6, 3.0), (3.0, 2.6), (1.0, .9)], OSSO, n=20)
        # lâmina
        sc.tubo([(s * 14.5, y + 3, zp - 12), (s * 9, y + 1, zp - 19), (s * 1, y, zp - 23)],
                [(5.0, 3.0), (4.6, 2.8), (4.8, 3.0)], OSSO, n=20, cima=(0, 1, 0))
    # processo espinhoso: lâmina alta e grossa, horizontal (lombar)
    sc.tubo([(0, y, zp - 22), (0, y - 1, zp - 34), (0, y - 2, zp - 46), (0, y - 3, zp - 52)],
            [(3.2, 8.5), (2.8, 9.5), (3.0, 10.0), (3.6, 8.0)], OSSO, n=26, cima=(1, 0, 0), perfil=lambda th, t: 1 - .35 * max(0, t - .8) / .2)

def disco(sc, y0, h):
    n, m = 72, 8
    secs = []
    for i in range(m + 1):
        t = i / m
        f = 1.0 + 0.05 * math.sin(math.pi * t)  # abaulamento natural
        ring = []
        for j in range(n):
            th = 2 * math.pi * j / n
            x, z = contorno(th, f * .985)
            # abaulamento posterolateral esquerdo onde o núcleo empurra
            d = math.cos(th - math.radians(-58))
            bump = 1 + .10 * max(0, d) ** 6 * math.sin(math.pi * t)
            ring.append((x * bump, y0 + h * t, z * bump))
        secs.append(ring)
    sc.loft(secs, ANEL, fechar_topo=False, fibras=2, fibra_op=.4, fibra_desloc=3)
    # face de corte: lamelas concêntricas do anel fibroso
    yt = y0 + h + .05
    escalas = [1.0, .92, .84, .76, .68, .60, .52]
    for k in range(len(escalas) - 1):
        e0, e1 = escalas[k] * .985 * 1.0, escalas[k + 1] * .985
        mat = ANEL if k % 2 == 0 else Mat("#1E5E56", "#69B8AC", "#C6EEE7", spec=.5, exp=30)
        for j in range(n):
            t0, t1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
            p = []
            for e, th in ((e0, t0), (e0, t1), (e1, t1), (e1, t0)):
                x, z = contorno(th, e)
                d = math.cos(th - math.radians(-58))
                bump = 1 + .10 * max(0, d) ** 6 * (e / 1.0)
                p.append((x * bump, yt + (1 - e) * 1.6, z * bump))
            sc.quad(p, mat, ref=(0, yt - 10, 0))
    # miolo (zona de transição) sob o núcleo
    for j in range(n):
        t0, t1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
        x0, z0 = contorno(t0, .52); x1, z1 = contorno(t1, .52)
        sc.quad([(0, yt + .9, -2), (x0, yt + .8, z0), (x1, yt + .8, z1)], Mat("#1A5C54", "#5DB5A8", "#BFEFE7"), ref=(0, yt - 10, 0))
    # núcleo pulposo (gel brilhante) + hérnia posterolateral
    ang = math.radians(-58)
    dx, dz = math.cos(ang), math.sin(ang)
    # fissura radial escura no anel, por onde o núcleo escapa
    FIS = Mat("#061A18", "#0E3532", "#245A54", spec=.1, exp=10)
    px, pz = -dz, dx
    for k in range(10):
        r0, r1 = 7 + k * 1.9, 7 + (k + 1) * 1.9
        w0, w1 = 3.6 - k * .12, 3.6 - (k + 1) * .12
        q = [(dx * r0 + px * w0, yt + 1.75, dz * r0 * .9 + pz * w0), (dx * r1 + px * w1, yt + 1.75, dz * r1 * .9 + pz * w1),
             (dx * r1 - px * w1, yt + 1.75, dz * r1 * .9 - pz * w1), (dx * r0 - px * w0, yt + 1.75, dz * r0 * .9 - pz * w0)]
        sc.quad(q, FIS, ref=(0, yt - 10, 0))
    sc.elipsoide((0, yt + 1.6, -1), (9.5, 3.0, 7.4), NUCLEO, n=36, m=14)
    eixo = [(dx * k, yt + 1.4 - .3 * max(0, k - 12), dz * k * .9) for k in (4, 10, 15, 20, 24)]
    sc.tubo(eixo, [3.0, 2.4, 2.6, 3.4, 4.0], NUCLEO, n=26, achatar=.75, cima=(0, 1, 0))
    c = (dx * 26, yt - 4, dz * 26 * .9)
    sc.elipsoide(c, (6.6, 5.6, 6.0), NUCLEO, n=30, m=16)
    return c

def nervos(sc, y_mid, alvo):
    zc = -Bz * .68 - 9
    # saco dural (meninges): translúcido-amarelado
    DURA = Mat("#4C5552", "#A9B5AF", "#EEF4EE", spec=.7, exp=44, op=.78, sss=.25, fibra="#FFFFFF")
    sc.tubo([(0, y_mid - 95, zc + 1), (0, y_mid, zc), (0, y_mid + 130, zc + 1)], [8.2, 8.6, 8.4], DURA, n=30, fibras=4, fibra_op=.25)
    # raízes que saem pelo forame (a esquerda passa encostada na hérnia)
    for s, dy in ((1, 0), (1, 52)):
        y = y_mid + dy
        pts = [(s * 5, y + 8, zc + 1), (s * 12, y + 2, zc + 3), (s * 20, y - 6, zc + 5), (s * 30, y - 16, zc + 9), (s * 44, y - 30, zc + 12)]
        sc.tubo(pts, [2.0, 1.9, 2.1, 2.4, 2.7], NERVO, n=20, fibras=3, fibra_op=.4)
        # gânglio da raiz dorsal
        sc.elipsoide((s * 21, y - 7, zc + 5), (3.4, 2.8, 3.0), NERVO, n=20, m=10)

def cover_svg(B, BD, LIGHT_BG):
    escuro = sum(int(LIGHT_BG[k:k + 2], 16) for k in (1, 3, 5)) < 300
    sc = Cena(yaw=-46, pitch=40, roll=-6, escala=2.7, centro=(176, 236), luz=(-0.5, 0.8, 0.45),
              fundo=LIGHT_BG, nevoa=.55 if escuro else .3, prof=(-70, 70))
    h_corpo, h_disco = 27, 10
    # L5 embaixo
    corpo(sc, -h_corpo, h_corpo)
    arco(sc, -h_corpo / 2)
    # ligamento longitudinal anterior (faixa na frente do corpo)
    alvo = disco(sc, 0, h_disco)
    nervos(sc, -2, alvo)
    # L4 explodida para cima (deixa ver o disco)
    y4 = h_disco + 30
    corpo(sc, y4, h_corpo)
    arco(sc, y4 + h_corpo / 2)
    LLA = Mat("#5F6B66", "#BFCBC6", "#F2F8F5", spec=.6, exp=38, fibra="#FFFFFF", op=.85)
    for (ya, yb) in ((-h_corpo + 2, -1), (y4 + 1, y4 + h_corpo - 2)):
        secs = []
        for i in range(7):
            y = ya + (yb - ya) * i / 6
            f = 1 - 0.07 * math.sin(math.pi * i / 6) ** 1.5
            ring = []
            for j in range(9):
                th = math.radians(62 + 56 * j / 8)
                x, z = contorno(th, f * 1.02)
                ring.append((x, y, z))
            secs.append(ring)
        # faixa aberta: desenha como quads entre seções sem fechar o anel
        for i in range(6):
            for j in range(8):
                p = [secs[i][j], secs[i][j + 1], secs[i + 1][j + 1], secs[i + 1][j]]
                sc.quad(p, LLA, ref=(0, (ya + yb) / 2, 0), op=.55)
    # ligamento amarelo (entre as lâminas) e interespinhoso, esticados na vista explodida
    zp = -Bz * (1 - .32) - 1
    AMARELO = Mat("#6B5A1E", "#CDB766", "#FBF0C2", spec=.5, exp=30, fibra="#FFF8DD", op=.8, sss=.2)
    for s_ in (-1, 1):
        sc.tubo([(s_ * 7, -h_corpo / 2 - 1, zp - 21), (s_ * 7.5, (y4 - h_corpo / 2) / 2 + 8, zp - 22), (s_ * 7, y4 + h_corpo / 2 - 1, zp - 21)],
                [(4.6, 1.6), (3.6, 1.3), (4.6, 1.6)], AMARELO, n=18, fibras=2, fibra_op=.35, cima=(0, 0, 1))
    # brilho verde-água na hérnia
    hx, hy = sc.projetar(alvo)
    sc.brilho(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="30" fill="{B}" opacity=".5" filter="url(#brilhoT)"/>')
    content = render(sc)
    return frame(content, B, glow=(220, 220, 200, 170), fade_v=(0, .02, .16, .62, .86), fade_h=(0, .06, .94, 1),
                 defs_extra=FILTROS_3D, glow_op=.30 if escuro else .40)
