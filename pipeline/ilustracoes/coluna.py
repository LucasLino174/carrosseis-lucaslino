"""Coluna vertebral em vista lateral, desenhada em SVG com volume e iluminação.
Anterior = esquerda (-x), posterior = direita (+x)."""
import math

def catmull_closed(pts, tension=1.0):
    n = len(pts)
    d = f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * tension, p1[1] + (p2[1] - p0[1]) / 6 * tension)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * tension, p2[1] - (p3[1] - p1[1]) / 6 * tension)
        d += f" C{c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}"
    return d + "Z"

def interp(points, t):
    # Catmull-Rom 1D sobre (t, x)
    ts = [p[0] for p in points]
    for i in range(len(points) - 1):
        if ts[i] <= t <= ts[i + 1]:
            break
    p0 = points[max(i - 1, 0)][1]; p1 = points[i][1]; p2 = points[i + 1][1]; p3 = points[min(i + 2, len(points) - 1)][1]
    u = (t - ts[i]) / (ts[i + 1] - ts[i])
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)

# perfil sagital: lordose cervical, cifose torácica, lordose lombar
CURVE = [(0.00, -2), (0.08, -14), (0.17, 0), (0.40, 22), (0.62, 2), (0.76, -24), (0.88, -8), (1.0, 20)]

def build_levels():
    lv = []
    for k in range(7):
        f = k / 6
        lv.append(dict(r="C", w=26 + 6 * f, h=11 + 2 * f, dh=4.2))
    for k in range(12):
        f = k / 11
        lv.append(dict(r="T", w=33 + 12 * f, h=15 + 8 * f, dh=4.4 + 1.6 * f, f=f))
    for k in range(5):
        f = k / 4
        lv.append(dict(r="L", w=50 + 6 * f, h=25 + 3 * f, dh=8.5 + 1.5 * f - (2.5 if k == 4 else 0)))
    return lv

def posterior_element(v):
    w, h, r = v["w"], v["h"], v["r"]
    P = w / 2
    if r == "C":
        ped, L, th, sb, tt, sup = 0.24 * w, 0.62 * w, 18, 0.26 * h, 0.16 * h, 0.12 * h
    elif r == "T":
        f = v["f"]
        ped = 0.22 * w
        L = (0.80 + 0.28 * math.sin(math.pi * f)) * w
        th = 40 + 20 * math.sin(math.pi * min(1, f * 1.15))
        sb, tt, sup = 0.36 * h, 0.21 * h, 0.16 * h
    else:
        ped, L, th, sb, tt, sup = 0.26 * w, 0.62 * w, 8, 0.36 * h, 0.40 * h, 0.16 * h
    a = P + ped
    sx = a + 0.21 * w
    t = math.radians(th)
    d = (math.cos(t), math.sin(t)); n = (-math.sin(t), math.cos(t))
    T = (sx + L * d[0], L * d[1])
    pts = [
        (P - 3, -0.32 * h),
        (P + ped * 0.55, -0.22 * h),                       # incisura vertebral superior
        (a - 0.02 * w, -0.55 * h - sup),                   # processo articular superior
        (a + 0.07 * w, -0.62 * h - sup * 0.6),
        (a + 0.12 * w, -0.36 * h),
        (sx, -sb),
        (T[0] - n[0] * tt, T[1] - n[1] * tt),
        (T[0] + d[0] * tt * 0.9, T[1] + d[1] * tt * 0.9),  # ponta do espinhoso
        (T[0] + n[0] * tt, T[1] + n[1] * tt),
        (sx + 0.02 * w, sb + 0.05 * h),
        (a + 0.13 * w, 0.48 * h),
        (a + 0.07 * w, 0.72 * h + sup * 0.7),              # processo articular inferior
        (a - 0.03 * w, 0.62 * h),
        (P + ped * 0.5, 0.18 * h),                         # incisura inferior (forame)
        (P - 3, 0.16 * h),
    ]
    tp = (a + 0.02 * w, -0.08 * h, 0.12 * w, 0.17 * h) # processo transverso (elipse)
    return catmull_closed(pts, 0.9), tp, P, ped

def body_path(w, h):
    r = min(4.5, h * 0.25)
    x0, x1, y0, y1 = -w / 2, w / 2, -h / 2, h / 2
    return (f"M{x0+r:.2f},{y0:.2f} Q{0:.2f},{y0-h*0.05:.2f} {x1-r:.2f},{y0:.2f} Q{x1:.2f},{y0:.2f} {x1:.2f},{y0+r:.2f} "
            f"L{x1:.2f},{y1-r:.2f} Q{x1:.2f},{y1:.2f} {x1-r:.2f},{y1:.2f} Q{0:.2f},{y1+h*0.05:.2f} {x0+r:.2f},{y1:.2f} "
            f"Q{x0:.2f},{y1:.2f} {x0:.2f},{y1-r:.2f} Q{x0+w*0.07:.2f},0 {x0:.2f},{y0+r:.2f} Q{x0:.2f},{y0:.2f} {x0+r:.2f},{y0:.2f}Z")

DEFS = """
<linearGradient id="bodyG" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#CFC4B0"/><stop offset=".3" stop-color="#F4EEE3"/><stop offset=".7" stop-color="#E6DDCC"/><stop offset="1" stop-color="#C2B59E"/></linearGradient>
<linearGradient id="endG" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#8E8168" stop-opacity=".35"/><stop offset=".18" stop-color="#fff" stop-opacity="0"/><stop offset=".82" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#8E8168" stop-opacity=".4"/></linearGradient>
<linearGradient id="postG" x1="0" y1="0" x2="1" y2="1">
 <stop offset="0" stop-color="#EFE8DB"/><stop offset=".6" stop-color="#E2D8C5"/><stop offset="1" stop-color="#C9BCA3"/></linearGradient>
<radialGradient id="tpG" cx=".35" cy=".35" r=".75">
 <stop offset="0" stop-color="#F7F2E9"/><stop offset=".7" stop-color="#DCD1BC"/><stop offset="1" stop-color="#B9AB91"/></radialGradient>
<linearGradient id="discG" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#4FA79B"/><stop offset=".35" stop-color="#9ADBD1"/><stop offset=".8" stop-color="#6CC3B7"/><stop offset="1" stop-color="#3E8E83"/></linearGradient>
<filter id="bone" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">
 <feGaussianBlur in="SourceAlpha" stdDeviation="1.6" result="b"/>
 <feDiffuseLighting in="b" surfaceScale="2.6" diffuseConstant="1" lighting-color="#fff" result="diff"><feDistantLight azimuth="235" elevation="48"/></feDiffuseLighting>
 <feSpecularLighting in="b" surfaceScale="2.6" specularConstant=".55" specularExponent="18" lighting-color="#fff" result="spec"><feDistantLight azimuth="235" elevation="52"/></feSpecularLighting>
 <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4" result="noise"/>
 <feColorMatrix in="noise" type="matrix" values="0 0 0 0 .45  0 0 0 0 .40  0 0 0 0 .32  0 0 0 .10 0" result="grain"/>
 <feComposite in="SourceGraphic" in2="diff" operator="arithmetic" k1=".55" k2=".52" k3="0" k4="0" result="lit"/>
 <feComposite in="grain" in2="lit" operator="over" result="tex"/>
 <feComposite in="spec" in2="SourceAlpha" operator="in" result="specIn"/>
 <feComposite in="tex" in2="specIn" operator="arithmetic" k2="1" k3=".45" result="out"/>
 <feComposite in="out" in2="SourceAlpha" operator="in"/>
</filter>
<filter id="disc" x="-20%" y="-60%" width="140%" height="220%">
 <feGaussianBlur in="SourceAlpha" stdDeviation="1" result="b"/>
 <feSpecularLighting in="b" surfaceScale="2" specularConstant=".7" specularExponent="25" lighting-color="#fff" result="spec"><feDistantLight azimuth="235" elevation="55"/></feSpecularLighting>
 <feComposite in="spec" in2="SourceAlpha" operator="in" result="s"/>
 <feComposite in="SourceGraphic" in2="s" operator="arithmetic" k2="1" k3=".5"/>
</filter>
<filter id="soft"><feGaussianBlur stdDeviation="2.4"/></filter>
<filter id="cast" x="-30%" y="-10%" width="160%" height="120%"><feDropShadow dx="7" dy="9" stdDeviation="7" flood-color="#0E3B36" flood-opacity=".28"/></filter>
"""

STROKE = 'stroke="#9C8F77" stroke-width=".55" stroke-linejoin="round"'

def spine(start_level=0):
    """Retorna (conteudo_svg, bbox) com a coluna desenhada em unidades absolutas."""
    lv = build_levels()
    # empilha
    y = 0
    for v in lv:
        v["y"] = y + v["h"] / 2
        y += v["h"] + v["dh"]
    total = y + 150
    for v in lv:
        t = v["y"] / total
        v["x"] = interp(CURVE, t)
        dx = interp(CURVE, min(1, t + 0.004)) - interp(CURVE, max(0, t - 0.004))
        v["ang"] = -math.degrees(math.atan2(dx, total * 0.008))
    lv = lv[start_level:]
    shadows, posts, discs, bodies = [], [], [], []
    for i, v in enumerate(lv):
        w, h = v["w"], v["h"]
        path, tp, P, ped = posterior_element(v)
        g = f'transform="translate({v["x"]:.2f},{v["y"]:.2f}) rotate({v["ang"]:.2f})"'
        posts.append(f'<g {g}><path d="{path}" fill="url(#postG)" {STROKE} filter="url(#bone)"/>'
                     f'<ellipse cx="{tp[0]:.2f}" cy="{tp[1]:.2f}" rx="{tp[2]:.2f}" ry="{tp[3]:.2f}" fill="url(#tpG)" opacity=".85" filter="url(#bone)"/></g>')
        shadows.append(f'<g {g}><ellipse cx="{P + ped*0.55:.2f}" cy="{h/2 + v["dh"]/2:.2f}" rx="{ped*0.75:.2f}" ry="{h*0.32 + v["dh"]:.2f}" fill="#2B3B39" opacity=".55" filter="url(#soft)"/></g>')
        bodies.append(f'<g {g}><path d="{body_path(w, h)}" fill="url(#bodyG)" {STROKE} filter="url(#bone)"/>'
                      f'<path d="{body_path(w, h)}" fill="url(#endG)"/></g>')
        if i < len(lv) - 1 or True:
            dw = w * 0.96
            dy = h / 2 + v["dh"] / 2
            dh = v["dh"] + 1.6
            discs.append(f'<g {g}><rect x="{-dw/2:.2f}" y="{dy - dh/2:.2f}" width="{dw:.2f}" height="{dh:.2f}" rx="{dh/2:.2f}" fill="url(#discG)" stroke="#2F7D72" stroke-width=".5" filter="url(#disc)"/></g>')
    # sacro + cóccix (inclinado posteriormente, face anterior côncava)
    last = lv[-1]
    sy = last["y"] + last["h"] / 2 + last["dh"] + 1
    sx = last["x"] + 2
    sa = last["ang"] - 34
    pts = [(-27, 0), (2, -4), (31, -1), (44, 6), (51, 22), (51, 50), (45, 80), (33, 104), (19, 122),
           (10, 118), (5, 98), (-3, 70), (-13, 42), (-22, 18)]
    sac = f'<path d="{catmull_closed(pts, 0.9)}" fill="url(#postG)" {STROKE} filter="url(#bone)"/>'
    ridges = "".join(f'<path d="M{-20 + k*7.5:.1f},{24 + k*24:.1f} q{16},{-4} {38 - k*6},{3}" stroke="#A89A80" stroke-width=".9" fill="none" opacity=".75"/>' for k in range(4))
    crest = "".join(f'<ellipse cx="{50 - k*3.4:.1f}" cy="{22 + k*21:.1f}" rx="4.5" ry="6.5" fill="url(#tpG)" opacity=".9" filter="url(#bone)"/>' for k in range(4))
    cox = "".join(f'<ellipse cx="{15 - k*3:.1f}" cy="{132 + k*10:.1f}" rx="{6.5 - k*1.3:.1f}" ry="{4.6 - k*0.8:.1f}" fill="url(#tpG)" {STROKE} filter="url(#bone)"/>' for k in range(3))
    sac = f'<g transform="translate({sx:.2f},{sy:.2f}) rotate({sa:.2f})">{sac}{ridges}{crest}{cox}</g>'
    ridges = crest = cox = ""
    # ordem: sombras do forame, elementos posteriores (de baixo pra cima), discos, corpos
    content = ("".join(shadows) + sac + ridges + crest + cox + "".join(reversed(posts)) + "".join(discs) + "".join(bodies))
    y0 = lv[0]["y"] - lv[0]["h"]
    return f'<g filter="url(#cast)">{content}</g>', (-60, y0, 190, sy + 180 - y0)


def cover_svg(B, BD, LIGHT_BG):
    """Capa: coluna lombar ampliada, esmaecendo no fundo. Ocupa a área de 420x525."""
    content, _ = spine(0)
    return f'''<svg width="420" height="525" viewBox="0 0 420 525" xmlns="http://www.w3.org/2000/svg" style="position:absolute;inset:0">
<defs>{DEFS}
<linearGradient id="fadeV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/><stop offset=".16" stop-color="#000"/><stop offset=".36" stop-color="#fff"/><stop offset=".62" stop-color="#fff"/><stop offset=".8" stop-color="#000"/></linearGradient>
<linearGradient id="fadeH" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset=".2" stop-color="#fff"/><stop offset=".8" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
<mask id="fadeHm" maskUnits="userSpaceOnUse" x="0" y="0" width="420" height="525"><rect width="420" height="525" fill="url(#fadeH)"/></mask>
<mask id="fadeVm" maskUnits="userSpaceOnUse" x="0" y="0" width="420" height="525"><rect width="420" height="525" fill="url(#fadeV)"/></mask>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{B}" stop-opacity=".38"/><stop offset="1" stop-color="{B}" stop-opacity="0"/></radialGradient>
</defs>
<ellipse cx="215" cy="230" rx="190" ry="170" fill="url(#glow)"/>
<g mask="url(#fadeHm)"><g mask="url(#fadeVm)"><g transform="translate(196,-20) rotate(-6) scale(1.3) translate(-28,-300)">{content}</g></g></g>
</svg>'''
