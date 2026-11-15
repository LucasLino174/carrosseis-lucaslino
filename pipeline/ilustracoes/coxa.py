"""Coxa em vista lateral, deitada na diagonal (quadril à esquerda, joelho à direita):
isquiotibiais (bíceps femoral) em verde-água, vasto lateral e reto femoral em tom muscular,
trato iliotibial e o joelho em osso no padrão de coluna.py/joelho.py."""
from ilustracoes._base import muscle, catmull_closed, frame
from ilustracoes.joelho import knee

def thigh():
    # coordenadas na vertical (quadril em cima, joelho embaixo); anterior = esquerda
    reto = muscle([(150, -330), (128, -150), (118, 20), (128, 170), (156, 250)],
                  [(178, -330), (164, -150), (152, 20), (156, 170), (170, 252)],
                  "url(#roseM)", fiber="#5E2A25", n=6, fiber_op=.3, stroke="#7A3E38")
    vasto = muscle([(176, -330), (150, -150), (140, 20), (150, 170), (172, 254)],
                   [(240, -330), (250, -150), (252, 20), (246, 170), (214, 252)],
                   "url(#roseM)", fiber="#5E2A25", n=16, fiber_op=.38, stroke="#7A3E38")
    isquio = muscle([(252, -330), (256, -150), (262, 20), (258, 170), (258, 300), (262, 390)],
                    [(318, -330), (330, -150), (330, 20), (314, 170), (288, 290), (276, 392)],
                    "url(#tealM)", fiber="#E8FFFB", n=16, fiber_op=.42, stroke="#22665D")
    trato = catmull_closed([(238, -330), (254, -330), (258, -100), (258, 100), (248, 230), (236, 300), (224, 312), (230, 290), (242, 200), (244, 0), (242, -200)], .9)
    trato_f = "".join(f'<path d="M{240+k*3:.1f},-330 Q{252+k*2:.1f},60 {226+k*3:.1f},306" stroke="#A89E8C" stroke-width=".45" fill="none" opacity=".5"/>' for k in range(5))
    joelho = f'<g transform="translate(212,262) scale(.98) translate(-236,-232)">{knee(musculos=False)}</g>'
    return (f'<g filter="url(#cast)">{isquio}</g>' + joelho + f'<g filter="url(#cast)">{vasto}{reto}'
            f'<path d="{trato}" fill="url(#tendG)" stroke="#B3A994" stroke-width=".5" filter="url(#disc)" opacity=".92"/>{trato_f}</g>')

def cover_svg(B, BD, LIGHT_BG):
    return frame(f'<g transform="translate(170,128) rotate(-58) scale(.72) translate(-220,-40)">{thigh()}</g>', B,
                 glow=(220, 170, 210, 150), fade_v=(0, .03, .14, .58, .76), fade_h=(0, .14, .9, 1))
