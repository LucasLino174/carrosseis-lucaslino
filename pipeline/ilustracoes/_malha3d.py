"""Mini motor 3D em SVG para as capas (padrão 3D pedido pelo Lucas em 15/11/2026).

Modela a anatomia como malhas (tubos, lofts, elipsoides deformados), aplica
iluminação real por face (difusa + especular de Blinn + luz de borda + oclusão
ambiente aproximada + névoa de profundidade) e desenha com o algoritmo do pintor.
Depois, `render()` embrulha a malha com filtros SVG de textura (relevo com
feTurbulence), suavização de facetas e sombra projetada.

Uso típico (ver disco_lombar.py, braco.py, aquiles.py):
    sc = Cena(yaw=-35, pitch=18, escala=1.0, centro=(210, 260))
    sc.tubo(eixo_pts, raios, OSSO, fibras=0)
    sc.elipsoide(c, (rx, ry, rz), TEAL)
    svg = sc.render()
"""
import math

# ---------------- materiais: (sombra, meio, luz, brilho especular, expoente) ----------------
def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[k:k + 2], 16) for k in (0, 2, 4))

def _mix(a, b, t):
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(3))

class Mat:
    def __init__(self, sombra, meio, luz, spec=.35, exp=24, borda=None, fibra=None, op=1.0, sss=0.0):
        self.s, self.m, self.l = _hex(sombra), _hex(meio), _hex(luz)
        self.spec, self.exp = spec, exp
        self.borda = _hex(borda) if borda else None
        self.fibra = fibra
        self.op = op
        self.sss = sss  # "subsurface": clareia as sombras (cartilagem, tendão)

    def cor(self, v):
        v = max(0.0, min(1.0, v))
        return _mix(self.s, self.m, v / .55) if v < .55 else _mix(self.m, self.l, (v - .55) / .45)

OSSO = Mat("#6F624E", "#D9CDB6", "#FAF5EA", spec=.30, exp=18, borda="#FFF6E0")
OSSO_ESCURO = Mat("#4E4537", "#B9AC93", "#E9E0CF", spec=.2, exp=14)
CORTICAL = Mat("#8C7F68", "#E8DFCD", "#FFFBF2", spec=.45, exp=30)
TEAL = Mat("#14544C", "#4FB0A3", "#C9F2EB", spec=.65, exp=40, borda="#D8FFF8", fibra="#E6FFFB", sss=.18)
TEAL_ESC = Mat("#0D3E38", "#2E8C80", "#8ED9CE", spec=.5, exp=30, fibra="#BFF1E9", sss=.12)
MUSCULO = Mat("#4A1A17", "#B15A4E", "#F0B3A6", spec=.35, exp=22, fibra="#FFD9CF", sss=.08)
MUSCULO_ESC = Mat("#36130F", "#8C4038", "#D58F82", spec=.25, exp=18, fibra="#F2BDB2", sss=.05)
TENDAO = Mat("#7E7767", "#D8D2C3", "#FFFDF6", spec=.7, exp=46, fibra="#FFFFFF", sss=.2)
LIGAMENTO = Mat("#6D776F", "#C6D0C8", "#F4FAF6", spec=.6, exp=40, fibra="#FFFFFF", sss=.15)
NERVO = Mat("#7A5A16", "#D9AE45", "#FBE7A6", spec=.55, exp=34, fibra="#FFF3C8", sss=.15)
VASO = Mat("#4B1420", "#A63A47", "#EC8E98", spec=.6, exp=40)
FASCIA = Mat("#7C8C88", "#D3DEDB", "#F7FBFA", spec=.5, exp=30, op=.55)
ANEL = Mat("#2C6E66", "#8FCFC5", "#E4FAF6", spec=.55, exp=34, fibra="#F2FFFD", sss=.2)
NUCLEO = Mat("#0F5F55", "#47C2B2", "#D2FFF8", spec=.9, exp=60, borda="#E8FFFB", sss=.3)
METAL = Mat("#1B2224", "#56636A", "#E2ECEF", spec=1.0, exp=70)
BORRACHA = Mat("#0E1213", "#2C3436", "#6E7B7E", spec=.4, exp=20)

# ---------------- álgebra ----------------
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def norm(a):
    l = math.sqrt(dot(a, a)) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)
def lerp3(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)

def catmull3(pts, m):
    """Amostra uma spline Catmull-Rom 3D (aberta) em m+1 pontos."""
    out = []
    n = len(pts)
    for j in range(m + 1):
        t = j / m * (n - 1)
        i = min(int(t), n - 2)
        u = t - i
        p0 = pts[max(i - 1, 0)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(i + 2, n - 1)]
        out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u * u
                                + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u ** 3) for k in range(3)))
    return out

def interp1(vals, t):
    """Interpola suavemente uma lista de valores (ou tuplas) em t∈[0,1]."""
    n = len(vals)
    if n == 1:
        return vals[0]
    x = t * (n - 1)
    i = min(int(x), n - 2)
    u = x - i
    u = u * u * (3 - 2 * u)
    a, b = vals[i], vals[i + 1]
    if isinstance(a, tuple):
        return tuple(a[k] + (b[k] - a[k]) * u for k in range(len(a)))
    return a + (b - a) * u


class Cena:
    def __init__(self, yaw=-30, pitch=15, roll=0, escala=1.0, centro=(210, 262), luz=(-0.55, 0.75, 0.55),
                 fundo="#F2F6F5", nevoa=0.35, prof=(-120, 120)):
        self.yaw, self.pitch, self.roll = math.radians(yaw), math.radians(pitch), math.radians(roll)
        self.k = escala
        self.cx, self.cy = centro
        self.L = norm(luz)
        self.H = norm(add(self.L, (0, 0, 1)))
        self.fundo = _hex(fundo)
        self.nevoa = nevoa
        self.zmin, self.zmax = prof
        self.faces = []   # (prof, pontos2d, cor, opacidade, extra_svg)
        self.over = []    # elementos desenhados por cima de tudo (brilhos)
        self.vies = 0.0   # viés de profundidade para a ordenação (camadas profundas < 0, superficiais > 0)

    # mundo -> câmera
    def cam(self, p):
        x, y, z = p
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        x, z = x * cy + z * sy, -x * sy + z * cy
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        y, z = y * cp - z * sp, y * sp + z * cp
        cr, sr = math.cos(self.roll), math.sin(self.roll)
        x, y = x * cr - y * sr, x * sr + y * cr
        return (x, y, z)

    def tela(self, pc):
        return (self.cx + pc[0] * self.k, self.cy - pc[1] * self.k)

    def projetar(self, p):
        return self.tela(self.cam(p))

    # ---------------- sombreamento ----------------
    def _cor(self, mat, n, ao=1.0, depth=0.0):
        lam = max(0.0, dot(n, self.L))
        wrap = (dot(n, self.L) + mat.sss) / (1 + mat.sss)
        lam = max(lam, wrap, 0)
        v = 0.03 + 0.92 * lam ** 1.15 + 0.10 * (0.5 + 0.5 * n[1])
        v *= ao
        c = mat.cor(v)
        sp = max(0.0, dot(n, self.H)) ** mat.exp * mat.spec
        c = _mix(c, (255, 255, 255), min(1, sp))
        rim = (1 - abs(n[2])) ** 3
        if mat.borda and dot(n, self.L) > 0.05:   # luz de borda só no lado iluminado
            c = _mix(c, mat.borda, rim * .4)
        # névoa de profundidade: peças de trás mais escuras/apagadas
        f = max(0.0, min(1.0, (-depth) / (-self.zmin) if self.zmin < 0 else 0)) * self.nevoa
        c = _mix(c, _mix(self.fundo, (0, 0, 0), .25 if sum(self.fundo) < 300 else .08), f)
        return c

    def quad(self, pts, mat, ref=None, ao=1.0, extra="", op=None, dupla=False):
        """Adiciona uma face (3 ou 4 pontos em coordenadas de mundo)."""
        pc = [self.cam(p) for p in pts]
        if len(pc) == 4:
            n = norm(cross(sub(pc[2], pc[0]), sub(pc[3], pc[1])))
        else:
            n = norm(cross(sub(pc[1], pc[0]), sub(pc[2], pc[0])))
        if ref is not None:
            rc = self.cam(ref)
            cen = mul(sum3(pc), 1 / len(pc))
            if dot(n, sub(cen, rc)) < 0:
                n = mul(n, -1)
        if n[2] < -0.02 and not dupla:
            return
        if dupla and n[2] < 0:
            n = mul(n, -1)
        depth = sum(p[2] for p in pc) / len(pc)
        c = self._cor(mat, n, ao, depth)
        p2 = [self.tela(p) for p in pc]
        self.faces.append((depth + self.vies, p2, c, mat.op if op is None else op, extra))

    # ---------------- primitivas ----------------
    def loft(self, secoes, mat, fechar_topo=True, fechar_base=True, ao_fn=None, fibras=0, fibra_op=.35, centro=None, fibra_desloc=0, extra_fn=None):
        """secoes: lista de anéis (cada anel = lista de pontos 3D com o mesmo nº de pontos)."""
        ns, nr = len(secoes), len(secoes[0])
        for i in range(ns - 1):
            A, B = secoes[i], secoes[i + 1]
            ca = mul(sum3(A), 1 / nr); cb = mul(sum3(B), 1 / nr)
            ref = lerp3(ca, cb, .5) if centro is None else centro
            for j in range(nr):
                j2 = (j + 1) % nr
                ao = ao_fn(i / (ns - 1), j / nr) if ao_fn else 1.0
                extra = ""
                if fibras and j % fibras == 0 and mat.fibra:
                    jb = (j + fibra_desloc) % nr; jb2 = (jb + 1) % nr
                    a = self.projetar(lerp3(A[j], A[j2], .5)); b = self.projetar(lerp3(B[jb], B[jb2], .5))
                    w = .35 + .35 * ((j * 7 + i) % 3) / 2
                    extra = (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                             f'stroke="{mat.fibra}" stroke-width="{w:.2f}" stroke-opacity="{fibra_op}" stroke-linecap="round"/>')
                if extra_fn:
                    extra += extra_fn(i, j, A, B)
                self.quad([A[j], A[j2], B[j2], B[j]], mat, ref=ref, ao=ao, extra=extra)
        if fechar_base:
            c0 = mul(sum3(secoes[0]), 1 / nr)
            for j in range(nr):
                self.quad([c0, secoes[0][j], secoes[0][(j + 1) % nr]], mat, ref=mul(sum3(secoes[1]), 1 / nr))
        if fechar_topo:
            c1 = mul(sum3(secoes[-1]), 1 / nr)
            for j in range(nr):
                self.quad([c1, secoes[-1][j], secoes[-1][(j + 1) % nr]], mat, ref=mul(sum3(secoes[-2]), 1 / nr))

    def tubo(self, eixo, raios, mat, n=28, m=None, fibras=0, fibra_op=.35, achatar=1.0, torcer=0.0,
             perfil=None, tampas=True, ao_fn=None, cima=(0, 0, 1)):
        """Tubo ao longo de uma spline 3D. raios: lista (interpolada) de raios ou de (rx, ry).
        perfil(theta, t) -> fator multiplicador do raio (bossas, cristas, achatamentos)."""
        m = m or max(16, len(eixo) * 10)
        P = catmull3(eixo, m)
        secoes = []
        prev_u = None
        for i, p in enumerate(P):
            t = i / m
            a = P[max(i - 1, 0)]; b = P[min(i + 1, m)]
            T = norm(sub(b, a))
            ref = cima if abs(dot(norm(cima), T)) < .95 else (1, 0, 0)
            u = norm(cross(T, ref)) if prev_u is None else norm(sub(prev_u, mul(T, dot(prev_u, T))))
            prev_u = u
            v = cross(T, u)
            r = interp1(raios, t)
            rx, ry = (r, r * achatar) if not isinstance(r, tuple) else r
            ring = []
            for j in range(n):
                th = 2 * math.pi * j / n + torcer * t
                f = perfil(th, t) if perfil else 1.0
                ring.append(add(p, add(mul(u, math.cos(th) * rx * f), mul(v, math.sin(th) * ry * f))))
            secoes.append(ring)
        self.loft(secoes, mat, fechar_topo=tampas, fechar_base=tampas, ao_fn=ao_fn, fibras=fibras, fibra_op=fibra_op)
        return P

    def elipsoide(self, c, r, mat, n=30, m=18, deform=None, rot=None, fibras=0):
        """Elipsoide (ou blob com deform(p_local, theta, phi) -> p_local)."""
        secoes = []
        for i in range(1, m):
            ph = math.pi * i / m - math.pi / 2
            ring = []
            for j in range(n):
                th = 2 * math.pi * j / n
                p = (r[0] * math.cos(ph) * math.cos(th), r[1] * math.sin(ph), r[2] * math.cos(ph) * math.sin(th))
                if deform:
                    p = deform(p, th, ph)
                if rot:
                    p = rot(p)
                ring.append(add(c, p))
            secoes.append(ring)
        self.loft(secoes, mat, fechar_topo=True, fechar_base=True, centro=c, fibras=fibras)

    def poligono_plano(self, pts, mat, op=None, extra=""):
        self.quad(pts, mat, op=op, extra=extra, dupla=True)

    def brilho(self, svg):
        self.over.append(svg)

    # ---------------- saída ----------------
    def svg_malha(self):
        out = []
        for depth, p2, c, op, extra in sorted(self.faces, key=lambda f: f[0]):
            d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in p2) + "Z"
            col = "#%02x%02x%02x" % tuple(int(max(0, min(255, k))) for k in c)
            if op < 1:
                out.append(f'<path d="{d}" fill="{col}" fill-opacity="{op}"/>' + extra)
            else:
                out.append(f'<path d="{d}" fill="{col}" stroke="{col}" stroke-width=".55" stroke-linejoin="round"/>' + extra)
        return "".join(out)


def sum3(pts):
    s = (0.0, 0.0, 0.0)
    for p in pts:
        s = add(s, p)
    return s


FILTROS_3D = """
<filter id="malha" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
 <feGaussianBlur in="SourceGraphic" stdDeviation=".35" result="lisa"/>
 <feTurbulence type="fractalNoise" baseFrequency="1.3" numOctaves="2" seed="7" result="ruido"/>
 <feColorMatrix in="ruido" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .9 0" result="alt"/>
 <feComposite in="alt" in2="SourceAlpha" operator="in" result="altIn"/>
 <feDiffuseLighting in="altIn" surfaceScale=".32" diffuseConstant="1.1" lighting-color="#fff" result="relevo"><feDistantLight azimuth="225" elevation="55"/></feDiffuseLighting>
 <feComposite in="lisa" in2="relevo" operator="arithmetic" k1=".9" k2=".14" result="tex"/>
 <feComposite in="tex" in2="SourceAlpha" operator="in"/>
</filter>
<filter id="sombra3d" x="-30%" y="-30%" width="160%" height="160%">
 <feGaussianBlur in="SourceAlpha" stdDeviation="9" result="b"/>
 <feOffset dx="10" dy="14" result="o"/>
 <feFlood flood-color="#03100E" flood-opacity=".38"/>
 <feComposite in2="o" operator="in"/>
</filter>
<filter id="desfoque"><feGaussianBlur stdDeviation="1.6"/></filter>
<filter id="brilhoT" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>
"""

def render(cena, sombra=True):
    """Malha com textura + sombra projetada (o que vai dentro de frame())."""
    m = cena.svg_malha()
    _id[0] += 1
    gid = f"malha{_id[0]}"
    s = f'<use href="#{gid}" filter="url(#sombra3d)" opacity=".9"/>' if sombra else ""
    # brilhos verde-água ficam ATRÁS da malha (aura), para não lavar o sombreamento
    return f'<defs><g id="{gid}">{m}</g></defs>' + "".join(cena.over) + s + f'<use href="#{gid}" filter="url(#malha)"/>'

_id = [0]
