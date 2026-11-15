"""Joelho em vista lateral (anterior = esquerda): fêmur distal, patela, tíbia e fíbula
proximais, tendões patelar e quadricipital. Cartilagem articular e meniscos em verde-água."""
from ilustracoes._base import catmull_closed, catmull_open, frame, STROKE

def _femur():
    pts = [(204, -60), (200, 60), (194, 140), (182, 186), (176, 214), (182, 238), (196, 258), (214, 270),
           (238, 272), (262, 266), (282, 252), (294, 230), (292, 204), (278, 180), (256, 158), (246, 120),
           (244, 60), (246, -60)]
    return catmull_closed(pts, 0.85)

def _tibia():
    pts = [(184, 290), (196, 284), (232, 286), (262, 282), (286, 284), (296, 292), (292, 306), (278, 324),
           (264, 350), (258, 420), (256, 600), (210, 600), (206, 420), (200, 372), (190, 346), (186, 326),
           (182, 304)]
    return catmull_closed(pts, 0.8)

def _fibula():
    pts = [(256, 330), (266, 316), (282, 312), (296, 320), (298, 338), (288, 356), (282, 380), (280, 600),
           (264, 600), (264, 390), (260, 360)]
    return catmull_closed(pts, 0.8)

def _patela():
    pts = [(150, 182), (162, 172), (176, 176), (184, 196), (184, 224), (176, 244), (164, 254), (154, 248),
           (146, 228), (144, 204)]
    return catmull_closed(pts, 0.9)

from ilustracoes._base import muscle

def _muscles():
    vasto = muscle([(146, -60), (134, 40), (138, 120), (152, 178)], [(276, -60), (284, 40), (268, 120), (210, 176)],
                   "url(#roseM)", fiber="#5E2A25", n=16, fiber_op=.35, stroke="#7A3E38")
    gastro = muscle([(262, 262), (300, 300), (318, 380), (300, 480), (272, 600)], [(250, 290), (262, 330), (270, 400), (262, 500), (252, 600)],
                    "url(#roseM)", fiber="#5E2A25", n=12, fiber_op=.35, stroke="#7A3E38")
    return f'<g opacity=".78">{vasto}{gastro}</g>'

def knee(musculos=True):
    fem, tib, fib, pat = _femur(), _tibia(), _fibula(), _patela()
    # cartilagem do côndilo femoral: o mesmo contorno, um pouco maior, só na parte distal
    cart_fem = (f'<clipPath id="kneeLow"><rect x="150" y="196" width="170" height="90"/></clipPath>'
                f'<g clip-path="url(#kneeLow)"><path d="{fem}" fill="url(#cartG)" stroke="#2F7D72" stroke-width=".6" '
                f'transform="translate(237,232) scale(1.045) translate(-237,-232)" filter="url(#disc)"/></g>')
    # cartilagem posterior da patela
    cart_pat = f'<path d="{catmull_open([(178,178),(188,196),(189,222),(180,246)])}" stroke="url(#cartG)" stroke-width="6" fill="none" stroke-linecap="round" filter="url(#disc)"/>'
    # platô tibial com cartilagem
    cart_tib = f'<path d="M188,288 Q236,280 292,288 L292,294 Q236,287 188,294Z" fill="url(#cartG)" stroke="#2F7D72" stroke-width=".5" filter="url(#disc)"/>'
    # meniscos em corte (cunhas): corno anterior e posterior
    men = (f'<path d="M190,288 Q200,276 222,280 Q206,284 200,290Z" fill="url(#discG)" stroke="#2F7D72" stroke-width=".6" filter="url(#disc)"/>'
           f'<path d="M296,288 Q290,268 260,276 Q280,280 284,290Z" fill="url(#discG)" stroke="#2F7D72" stroke-width=".6" filter="url(#disc)"/>')
    # tendão patelar e quadricipital (fibras)
    tp = catmull_closed([(150, 244), (166, 252), (176, 290), (196, 330), (190, 344), (180, 336), (162, 300), (148, 262)], 0.9)
    tq = catmull_closed([(150, 186), (176, 176), (186, 120), (190, 30), (196, -60), (160, -60), (162, 40), (156, 120)], 0.9)
    fib_lines = "".join(f'<path d="M{153+k*3.6:.1f},250 Q{168+k*3:.1f},300 {182+k*2:.1f},338" stroke="#A89E8C" stroke-width=".5" fill="none" opacity=".55"/>' for k in range(6))
    fib_q = "".join(f'<path d="M{156+k*4.6:.1f},184 Q{163+k*4:.1f},90 {164+k*5:.1f},-60" stroke="#A89E8C" stroke-width=".5" fill="none" opacity=".5"/>' for k in range(7))
    epic = '<ellipse cx="248" cy="220" rx="26" ry="22" fill="#fff" opacity=".18" filter="url(#soft)"/><ellipse cx="256" cy="226" rx="30" ry="26" fill="none" stroke="#A89A80" stroke-width=".8" opacity=".35"/>'
    tub = '<ellipse cx="196" cy="334" rx="9" ry="13" fill="url(#tpG)" opacity=".6" filter="url(#bone)"/>'
    return ((_muscles() if musculos else '') + f'<g filter="url(#cast)">'
            f'<path d="{tib}" fill="url(#bodyG)" {STROKE} filter="url(#bone)"/>{tub}{cart_tib}'
            f'<path d="{fib}" fill="url(#postG)" {STROKE} filter="url(#bone)"/>'
            f'{cart_fem}<path d="{fem}" fill="url(#bodyG)" {STROKE} filter="url(#bone)"/>{epic}{men}'
            f'<path d="{tq}" fill="url(#tendG)" stroke="#B3A994" stroke-width=".5" filter="url(#disc)" opacity=".95"/>{fib_q}'
            f'<path d="{tp}" fill="url(#tendG)" stroke="#B3A994" stroke-width=".5" filter="url(#disc)"/>{fib_lines}'
            f'{cart_pat}<path d="{pat}" fill="url(#bodyG)" {STROKE} filter="url(#bone)"/>'
            f'</g>')

def cover_svg(B, BD, LIGHT_BG):
    return frame(f'<g transform="translate(222,262) scale(1.0) rotate(-4) translate(-236,-262)">{knee()}</g>', B,
                 glow=(222, 255, 200, 190))
