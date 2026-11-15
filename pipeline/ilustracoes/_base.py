"""Utilidades compartilhadas pelas ilustrações de capa (músculos com fibras, tendões,
moldura com glow verde-água e esmaecimento nas bordas). Reaproveita DEFS de coluna.py."""
from ilustracoes.coluna import DEFS, catmull_closed

def catmull_open(pts, tension=1.0):
    d = f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * tension, p1[1] + (p2[1] - p0[1]) / 6 * tension)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * tension, p2[1] - (p3[1] - p1[1]) / 6 * tension)
        d += f" C{c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}"
    return d

def _sample(pts, m=40):
    """Amostra uma spline Catmull-Rom aberta em m pontos (para gerar fibras)."""
    out = []
    n = len(pts)
    for j in range(m + 1):
        t = j / m * (n - 1)
        i = min(int(t), n - 2)
        u = t - i
        p0 = pts[max(i - 1, 0)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(i + 2, n - 1)]
        out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u * u
                                + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u ** 3) for k in range(2)))
    return out

_uid = [0]
def muscle(L, R, fill, fiber="#fff", n=14, fiber_op=.35, stroke="#2F7D72", sw=.6, filt="muscle", extra=""):
    """Músculo entre duas bordas (listas de pontos com o mesmo sentido: origem -> inserção).
    Desenha o ventre com volume e fibras que acompanham a direção do músculo."""
    _uid[0] += 1
    cid = f"mc{_uid[0]}"
    shape = catmull_open(L) + " " + catmull_open(list(reversed(R))).replace("M", "L", 1) + "Z"
    a, b = _sample(L), _sample(R)
    fibers = []
    for k in range(1, n):
        f = k / n
        pts = [(a[j][0] * (1 - f) + b[j][0] * f, a[j][1] * (1 - f) + b[j][1] * f) for j in range(len(a))]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        w = .55 + .5 * ((k * 37) % 5) / 5
        fibers.append(f'<path d="{d}" stroke="{fiber}" stroke-width="{w:.2f}" fill="none" opacity="{fiber_op * (0.6 + 0.4 * ((k * 13) % 3) / 2):.2f}"/>')
    return (f'<clipPath id="{cid}"><path d="{shape}"/></clipPath>'
            f'<path d="{shape}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" filter="url(#{filt})"/>'
            f'<g clip-path="url(#{cid})">{"".join(fibers)}{extra}</g>')

EXTRA_DEFS = """
<linearGradient id="tealM" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#2E8478"/><stop offset=".4" stop-color="#8FD6CB"/><stop offset=".75" stop-color="#5DB8AB"/><stop offset="1" stop-color="#256F65"/></linearGradient>
<linearGradient id="roseM" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#8E4A43"/><stop offset=".4" stop-color="#D49A8D"/><stop offset=".75" stop-color="#B9776B"/><stop offset="1" stop-color="#7A3E38"/></linearGradient>
<linearGradient id="tendG" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#C9C2B4"/><stop offset=".45" stop-color="#F6F2EA"/><stop offset="1" stop-color="#BDB4A3"/></linearGradient>
<linearGradient id="cartG" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#A6E3DA"/><stop offset=".5" stop-color="#6CC3B7"/><stop offset="1" stop-color="#3E9A8E"/></linearGradient>
<filter id="muscle" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">
 <feGaussianBlur in="SourceAlpha" stdDeviation="6" result="b"/>
 <feSpecularLighting in="b" surfaceScale="7" specularConstant=".6" specularExponent="16" lighting-color="#fff" result="spec"><feDistantLight azimuth="235" elevation="50"/></feSpecularLighting>
 <feComposite in="spec" in2="SourceAlpha" operator="in" result="s"/>
 <feDiffuseLighting in="b" surfaceScale="7" diffuseConstant="1" lighting-color="#fff" result="diff"><feDistantLight azimuth="235" elevation="55"/></feDiffuseLighting>
 <feComposite in="SourceGraphic" in2="diff" operator="arithmetic" k1=".6" k2=".5" result="lit"/>
 <feComposite in="lit" in2="s" operator="arithmetic" k2="1" k3=".35" result="o"/>
 <feComposite in="o" in2="SourceAlpha" operator="in"/>
</filter>
"""

STROKE = 'stroke="#9C8F77" stroke-width=".6" stroke-linejoin="round"'

def frame(content, B, glow=(215, 260, 190, 180), fade_v=(0, .14, .32, .7, .9), fade_h=(0, .16, .84, 1)):
    """Moldura 420x525: glow verde-água atrás e máscaras que esmaecem a arte nas bordas."""
    gx, gy, rx, ry = glow
    v0, v1, v2, v3, v4 = fade_v
    h0, h1, h2, h3 = fade_h
    def eased(a, b, c, d):
        # rampas suaves (smoothstep) para não criar "linha" visível onde o esmaecimento termina
        stops = []
        for k in range(41):
            t = k / 40
            if t <= a or t >= d:
                v = 0
            elif b <= t <= c:
                v = 1
            elif t < b:
                u = (t - a) / (b - a); v = u * u * (3 - 2 * u)
            else:
                u = (d - t) / (d - c); v = u * u * (3 - 2 * u)
            g = int(round(v * 255))
            stops.append(f'<stop offset="{t:.3f}" stop-color="rgb({g},{g},{g})"/>')
        return "".join(stops)
    sv = eased(v1, v2, v3, v4)
    sh = eased(h0, h1, h2, h3)
    return f'''<svg width="420" height="525" viewBox="0 0 420 525" xmlns="http://www.w3.org/2000/svg" style="position:absolute;inset:0">
<defs>{DEFS}{EXTRA_DEFS}
<linearGradient id="fadeV" x1="0" y1="0" x2="0" y2="1">{sv}</linearGradient>
<linearGradient id="fadeH" x1="0" y1="0" x2="1" y2="0">{sh}</linearGradient>
<mask id="fadeHm" maskUnits="userSpaceOnUse" x="0" y="0" width="420" height="525"><rect width="420" height="525" fill="url(#fadeH)"/></mask>
<mask id="fadeVm" maskUnits="userSpaceOnUse" x="0" y="0" width="420" height="525"><rect width="420" height="525" fill="url(#fadeV)"/></mask>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{B}" stop-opacity=".40"/><stop offset="1" stop-color="{B}" stop-opacity="0"/></radialGradient>
</defs>
<ellipse cx="{gx}" cy="{gy}" rx="{rx}" ry="{ry}" fill="url(#glow)"/>
<g mask="url(#fadeHm)"><g mask="url(#fadeVm)">{content}</g></g>
</svg>'''
