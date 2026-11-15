"""Ombro esquerdo em vista anterior (medial = esquerda, lateral = direita): clavícula,
escápula com acrômio e coracoide, úmero e costelas ao fundo. Manguito rotador
(supraespinal e subescapular) em verde-água, com fibras."""
from ilustracoes._base import muscle, catmull_closed, catmull_open, frame, STROKE

def _costelas():
    out = []
    for k in range(6):
        y = 150 + k * 46
        d = catmull_open([(-40, y + 30), (40, y), (130, y + 6), (200, y + 34)])
        out.append(f'<path d="{d}" stroke="url(#postG)" stroke-width="18" fill="none" stroke-linecap="round" opacity=".55" filter="url(#bone)"/>')
    return "".join(out)

def shoulder():
    escapula = catmull_closed([(70, 172), (130, 168), (196, 176), (222, 196), (236, 222), (226, 250), (196, 320),
                               (150, 400), (118, 430), (100, 410), (84, 330), (70, 250)], .9)
    coracoide = catmull_closed([(186, 178), (208, 166), (234, 170), (250, 184), (244, 194), (226, 188), (206, 192), (192, 194)], .9)
    acromio = catmull_closed([(214, 146), (262, 134), (312, 138), (338, 152), (332, 166), (300, 162), (262, 162), (228, 170)], .9)
    clavicula = catmull_closed([(-40, 128), (40, 110), (110, 120), (180, 136), (240, 132), (296, 136), (300, 152),
                                (244, 152), (180, 156), (108, 142), (40, 134), (-40, 152)], .9)
    umero = catmull_closed([(236, 214), (238, 186), (256, 166), (284, 160), (310, 168), (326, 190), (328, 220),
                            (318, 248), (308, 276), (300, 360), (304, 600), (262, 600), (262, 360), (254, 280), (244, 250)], .85)
    glenoide = '<ellipse cx="236" cy="222" rx="7" ry="26" fill="url(#cartG)" stroke="#2F7D72" stroke-width=".5" filter="url(#disc)"/>'
    cab_cart = f'<path d="{catmull_open([(242,196),(256,170),(284,162),(312,170)])}" stroke="url(#cartG)" stroke-width="5" fill="none" stroke-linecap="round" opacity=".9"/>'
    tub = '<ellipse cx="312" cy="214" rx="13" ry="22" fill="url(#tpG)" opacity=".55" filter="url(#bone)"/>'
    sulco = f'<path d="{catmull_open([(290,224),(287,250),(285,280)])}" stroke="#A89A80" stroke-width="1" fill="none" opacity=".4"/>'
    # subescapular: leque sobre a face anterior da escápula, convergindo para o tubérculo menor
    subesc = muscle([(66, 186), (150, 200), (232, 232), (262, 236)], [(96, 440), (150, 366), (220, 288), (262, 256)],
                    "url(#tealM)", fiber="#E8FFFB", n=15, fiber_op=.42, stroke="#22665D")
    # supraespinal: da fossa supraespinal, por baixo do acrômio, até o tubérculo maior
    supra = muscle([(-60, 150), (60, 144), (150, 140), (240, 150), (300, 160), (326, 180)], [(-60, 184), (60, 182), (150, 178), (230, 186), (290, 192), (322, 202)],
                   "url(#tealM)", fiber="#E8FFFB", n=8, fiber_op=.42, stroke="#22665D")
    # cabeça longa do bíceps no sulco intertubercular
    biceps = catmull_closed([(283, 236), (291, 236), (290, 330), (282, 330)], .9)
    return (f'<g opacity=".9">{_costelas()}</g><g filter="url(#cast)">'
            f'<path d="{escapula}" fill="url(#postG)" {STROKE} filter="url(#bone)"/>'
            f'<clipPath id="escClip"><path d="{escapula}" transform="translate(150,300) scale(.97) translate(-150,-300)"/><rect x="200" y="180" width="80" height="110"/></clipPath>'
            f'{supra}<g clip-path="url(#escClip)">{subesc}</g>{glenoide}'
            f'<path d="{umero}" fill="url(#bodyG)" {STROKE} filter="url(#bone)"/>{cab_cart}{tub}'
            f'<path d="{coracoide}" fill="url(#postG)" {STROKE} filter="url(#bone)"/>'
            f'<path d="{acromio}" fill="url(#bodyG)" {STROKE} filter="url(#bone)"/>'
            f'<path d="{clavicula}" fill="url(#bodyG)" {STROKE} filter="url(#bone)"/>'
            f'</g>')

def cover_svg(B, BD, LIGHT_BG):
    return frame(f'<g transform="translate(232,250) scale(1.0) translate(-205,-250)">{shoulder()}</g>', B,
                 glow=(240, 250, 200, 190), fade_v=(0, .1, .26, .68, .88), fade_h=(0, .2, .88, 1))
