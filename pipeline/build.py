"""Gera o carrossel do @lucaslino.fisio a partir de uma spec JSON.

Uso:
    python3 pipeline/build.py carrosseis/<pasta>/spec.json
Saída (na mesma pasta da spec):
    carrossel.html   prévia com moldura do Instagram (arraste para o lado)
    slide_N.png      1080x1350
    slide_N.jpg      1080x1350, o formato que vai para o Instagram

Marcação de texto dentro da spec:
    **texto**   destaque em verde-água (negrito colorido)
    ==texto==   bloco de destaque atrás do texto (só na manchete da capa)
"""
import asyncio, base64, importlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# ---------------- Identidade visual (não alterar sem pedir ao Lucas) ----------------
B = "#6CC3B7"         # verde-água principal
BL = "#A6DDD5"        # verde-água claro
BD = "#2B7E73"        # verde-água escuro
LIGHT_BG = "#F2F6F5"
LIGHT_BORDER = "#DFE8E6"
DARK_BG = "#111718"
GRAY = "#6B7775"
INK = "#111718"
# Cores complementares (combinam com o verde-água; usar com moderação, quando o tema pedir)
CORAL = "#E07A5F"      # terracota: "mito", "erro", alerta
AREIA = "#EFE6D8"      # fundo claro quente
AREIA_BORDA = "#E2D6C2"
MARINHO = "#14243B"    # fundo escuro frio
OCRE = "#E9B44C"       # destaque quente pontual
HANDLE = "@lucaslino.fisio"
NOME = "Lucas Lino"
AVATAR = "data:image/jpeg;base64," + base64.b64encode((ROOT / "assets/avatar.jpg").read_bytes()).decode()

def _img(name):
    return "data:image/png;base64," + base64.b64encode((ROOT / "assets" / name).read_bytes()).decode()
LOGO_H = _img("logo_horizontal.png"); LOGO_H_W = _img("logo_horizontal_branco.png")
LOGO_S = _img("logo_simbolo.png"); LOGO_S_W = _img("logo_simbolo_branco.png")

FONT_DIRS = [Path("/usr/share/fonts/truetype/google-fonts"), ROOT / "assets/fonts"]
def _font(weight, file):
    for d in FONT_DIRS:
        if (d / file).exists():
            data = base64.b64encode((d / file).read_bytes()).decode()
            return ("@font-face{font-family:'Poppins';font-weight:%d;font-style:normal;"
                    "src:url(data:font/ttf;base64,%s) format('truetype');}" % (weight, data))
    return ""
FONTS = "".join(_font(w, f) for w, f in [(300, "Poppins-Light.ttf"), (400, "Poppins-Regular.ttf"),
                                           (500, "Poppins-Medium.ttf"), (700, "Poppins-Bold.ttf")])

def pal(light):
    if light == "areia":
        c = pal(True); c.update(bg=f"background:{AREIA};", line=AREIA_BORDA, box_bg="#FBF7F1", box_border=AREIA_BORDA,
                                pill=f"background:rgba(224,122,95,0.14);color:#A4452D;", mode="light", base=AREIA)
        return c
    if light == "marinho":
        c = pal(False); c.update(bg=f"background:radial-gradient(120% 90% at 0% 100%, #1F3A5C 0%, {MARINHO} 60%);",
                                 box_bg="rgba(255,255,255,0.06)", pill=f"background:rgba(233,180,76,0.16);color:{OCRE};", mode="dark", base=MARINHO)
        return c
    if light == "teal":
        return dict(bg=f"background:linear-gradient(160deg, #23685F 0%, {BD} 55%, #3E9A8E 100%);", title="#fff",
                    text="rgba(255,255,255,0.82)", strong="#fff", accent="#0E2422", accent2="#fff", line="rgba(255,255,255,0.18)",
                    muted="rgba(255,255,255,0.6)", handle="rgba(255,255,255,0.9)",
                    pill="background:rgba(255,255,255,0.18);color:#fff;", track="rgba(255,255,255,0.2)",
                    count="rgba(255,255,255,0.6)", arrow_bg="rgba(255,255,255,0.08)", arrow="rgba(255,255,255,0.5)",
                    box_bg="rgba(255,255,255,0.12)", box_border="rgba(255,255,255,0.2)", icon_bg="rgba(255,255,255,0.15)",
                    fill="#fff", mode="teal", base=BD)
    if light:
        return dict(bg=f"background:{LIGHT_BG};", title=INK, text=GRAY, strong=INK, accent=BD, accent2=B,
                    line=LIGHT_BORDER, muted="rgba(17,23,24,0.45)", handle="rgba(17,23,24,0.75)",
                    pill=f"background:rgba(43,126,115,0.12);color:{BD};", track="rgba(0,0,0,0.08)",
                    count="rgba(0,0,0,0.35)", arrow_bg="rgba(0,0,0,0.05)", arrow="rgba(0,0,0,0.28)",
                    box_bg="#fff", box_border=LIGHT_BORDER, icon_bg="rgba(43,126,115,0.10)", fill=B, mode="light", base=LIGHT_BG)
    return dict(bg=f"background:radial-gradient(120% 90% at 100% 0%, #1E2829 0%, {DARK_BG} 55%);", title="#fff",
                text="rgba(255,255,255,0.6)", strong="#fff", accent=B, accent2=B, line="rgba(255,255,255,0.08)",
                muted="rgba(255,255,255,0.45)", handle="rgba(255,255,255,0.8)",
                pill=f"background:rgba(108,195,183,0.14);color:{BL};", track="rgba(255,255,255,0.12)",
                count="rgba(255,255,255,0.4)", arrow_bg="rgba(255,255,255,0.06)", arrow="rgba(255,255,255,0.35)",
                box_bg="rgba(0,0,0,0.25)", box_border="rgba(255,255,255,0.08)", icon_bg="rgba(108,195,183,0.12)", fill=B, mode="dark", base=DARK_BG)

def md(text, c):
    """**x** vira destaque colorido."""
    return re.sub(r"\*\*(.+?)\*\*", lambda m: f'<span style="color:{c["accent"]};font-weight:700">{m.group(1)}</span>', text or "")

def md_strong(text, c):
    return re.sub(r"\*\*(.+?)\*\*", lambda m: f'<b style="color:{c["strong"]}">{m.group(1)}</b>', text or "")

ICONS = {
    "carga": '<path d="M6 7h12l-1.5 12h-9z"/><path d="M9 7a3 3 0 0 1 6 0"/>',
    "cadeira": '<path d="M7 3v9h10"/><path d="M7 12v8M17 12v8M7 16h10"/>',
    "lua": '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
    "escudo": '<path d="M12 3l7 3v5c0 5-3.5 8-7 10-3.5-2-7-5-7-10V6z"/>',
    "livro": '<path d="M6 4h12v16l-6-3-6 3z"/>',
    "lampada": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9V16h7v-2.1A6 6 0 0 0 12 3z"/>',
    "pulso": '<path d="M3 12h4l2-5 4 10 2-5h6"/>',
    "lupa": '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
    "pessoa": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "alvo": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>',
    "corrida": '<circle cx="14" cy="4.5" r="2"/><path d="M8 21l3-6 3 2v5M6 11l3-3 4 1 3 4 3 1"/>',
    "haltere": '<path d="M6 8v8M18 8v8M3 10v4M21 10v4M6 12h12"/>',
    "relogio": '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
    "coracao": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
    "alerta": '<path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17h.01"/>',
    "equilibrio": '<path d="M12 3v18M5 7h14M5 7l-3 6h6zM19 7l-3 6h6z"/>',
    "articulacao": '<circle cx="12" cy="12" r="3"/><path d="M12 3v6M12 15v6"/>',
}
def icon(name, color, size=18):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS.get(name, ICONS["check"])}</svg>')

# ---------------- Componentes fixos ----------------
def progress_bar(i, total, c, fill=None):
    pct = (i + 1) / total * 100
    return (f'<div style="position:absolute;bottom:0;left:0;right:0;padding:16px 28px 20px;z-index:10;display:flex;align-items:center;gap:10px;">'
            f'<div style="flex:1;height:3px;background:{c["track"]};border-radius:2px;overflow:hidden;"><div style="height:100%;width:{pct}%;background:{fill or B};border-radius:2px;"></div></div>'
            f'<span style="font-size:11px;color:{c["count"]};font-weight:500;">{i+1}/{total}</span></div>')

def swipe_arrow(c):
    return (f'<div style="position:absolute;right:0;top:0;bottom:0;width:48px;z-index:9;display:flex;align-items:center;justify-content:center;background:linear-gradient(to right,transparent,{c["arrow_bg"]});">'
            f'<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="{c["arrow"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')

def top_bar(c, tag, solid=False, show_handle=True):
    pill = f"background:{INK};color:#fff;" if solid else c["pill"]
    handle = (f'<span style="display:flex;align-items:center;gap:8px;"><img src="{AVATAR}" style="width:26px;height:26px;border-radius:50%;object-fit:cover;border:1.5px solid {"#fff" if c["mode"]=="teal" else B};"/>'
              f'<span style="font-size:11px;font-weight:600;color:{c["handle"]};letter-spacing:.2px;">{HANDLE}</span></span>') if show_handle else "<span></span>"
    tag_html = f'<span style="font-size:8.5px;font-weight:700;letter-spacing:1.4px;padding:4px 9px;border-radius:20px;{pill}">{tag}</span>' if tag else ""
    return f'<div style="position:absolute;top:20px;left:28px;right:28px;z-index:11;display:flex;align-items:center;justify-content:space-between;">{handle}{tag_html}</div>'

def label(text, c):
    if not text:
        return ""
    return (f'<div style="font-size:10px;font-weight:700;letter-spacing:3px;color:{c["accent"]};">{text}</div>'
            f'<div style="width:34px;height:2px;background:{c["accent"]};margin:8px 0 14px;border-radius:2px;"></div>')

def source(text, c):
    if not text:
        return ""
    return (f'<div style="display:flex;align-items:center;gap:8px;margin-top:14px;padding-top:12px;border-top:1px solid {c["line"]};">{icon("livro", c["accent"])}'
            f'<span style="font-size:10.5px;color:{c["muted"]};">{text}</span></div>')

def signature(c):
    return (f'<div style="display:flex;align-items:center;gap:12px;margin-top:18px;"><div style="flex:1;height:1px;background:{c["line"]}"></div>'
            f'<span style="font-size:9px;font-weight:700;letter-spacing:3px;color:{c["muted"]}">LUCAS LINO</span><div style="flex:1;height:1px;background:{c["line"]}"></div></div>')

DISPOSICAO = {"base": "flex-end", "topo": "flex-start", "centro": "center"}
_ALINHAR = {"v": "base", "centro_texto": False}
def body_wrap(inner):
    v = DISPOSICAO.get(_ALINHAR["v"], "flex-end")
    top_pad = "72px" if v == "flex-start" else "0"
    ta = "text-align:center;align-items:center;" if _ALINHAR["centro_texto"] else ""
    return f'<div style="position:absolute;inset:0;padding:{top_pad} 48px 60px 36px;display:flex;flex-direction:column;justify-content:{v};{ta}">{inner}</div>'

def h2(text, c, size=27, mb=0):
    return f'<h2 style="font-size:{size}px;line-height:1.12;font-weight:700;letter-spacing:-0.5px;color:{c["title"]};margin-bottom:{mb}px;">{md(text, c)}</h2>'

def para(text, c, mt=12):
    return f'<p style="font-size:13.5px;line-height:1.55;color:{c["text"]};margin-top:{mt}px;">{md_strong(text, c)}</p>' if text else ""

# ---------------- Tipos de slide ----------------
def s_capa(s, c):
    """Capa. Layouts: 'base' (manchete embaixo) ou 'topo' (manchete em cima, arte embaixo).
    Fundo segue o estilo: claro (padrão) ou escuro."""
    mod = importlib.import_module("ilustracoes." + s["ilustracao"])
    dark = c["mode"] != "light"
    bgc = c.get("base", DARK_BG if dark else LIGHT_BG)
    art = mod.cover_svg(B, BD, bgc)
    layout = s.get("layout", "base")
    titulo = re.sub(r"==(.+?)==", lambda m: f'<span style="background:{B};color:{INK};padding:0 6px;border-radius:4px;-webkit-box-decoration-break:clone;box-decoration-break:clone;">{m.group(1)}</span>', s["titulo"])
    tcol = "#fff" if dark else INK
    sub_c = "rgba(255,255,255,0.65)" if dark else GRAY
    rgb = ",".join(str(int(bgc[k:k+2], 16)) for k in (1, 3, 5))
    titulo_html = (f'<h1 style="font-size:{s.get("tamanho", 28)}px;line-height:1.1;font-weight:700;letter-spacing:-0.6px;color:{tcol};text-transform:uppercase;">{titulo}</h1>'
                   f'<div style="width:34px;height:2px;background:{B if dark else BD};margin:12px 0 10px;border-radius:2px;"></div>'
                   f'<p style="font-size:12.5px;line-height:1.45;color:{sub_c};">{md_strong(s.get("subtitulo", ""), c)}</p>')
    marca = f'<img src="{LOGO_S_W if dark else LOGO_S}" style="position:absolute;right:30px;bottom:56px;width:30px;opacity:.55;z-index:6"/>' if s.get("marca", True) else ""
    if layout == "topo":
        return (f'<div style="position:absolute;inset:0;transform:translateY({s.get("deslocamento_arte", 120)}px)">{art}</div>' + top_bar(c, s.get("tag", "")) +
                f'<div style="position:absolute;left:0;right:0;top:0;height:270px;background:linear-gradient(to bottom,{bgc} 58%,rgba({rgb},0));"></div>'
                f'<div style="position:absolute;left:0;right:0;bottom:0;height:70px;background:linear-gradient(to top,{bgc},rgba({rgb},0));"></div>'
                f'<div style="position:absolute;left:36px;right:48px;top:66px;">{titulo_html}</div>' + marca)
    return (art + top_bar(c, s.get("tag", "")) +
            f'<div style="position:absolute;left:0;right:0;bottom:0;height:250px;background:linear-gradient(to top,{bgc} 62%,rgba({rgb},0));"></div>'
            f'<div style="position:absolute;left:36px;right:48px;bottom:54px;">{titulo_html}</div>' + marca)

def s_mito(s, c):
    pills = "".join(f'<span style="font-size:11.5px;padding:6px 13px;border:1px solid {"rgba(0,0,0,0.12)" if c["mode"]=="light" else "rgba(255,255,255,0.18)"};border-radius:20px;color:{c["muted"]};text-decoration:line-through;">{p}</span>' for p in s.get("riscados", []))
    box = (f'<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;border:1.5px solid {c["accent2"] if c["mode"]=="teal" else B};border-radius:14px;background:{c["box_bg"] if c["mode"]!="dark" else "transparent"};">'
           f'<div style="width:34px;height:34px;border-radius:50%;background:{c["icon_bg"]};display:flex;align-items:center;justify-content:center;flex-shrink:0">{icon(s.get("icone","lampada"), c["accent"])}</div>'
           f'<p style="font-size:13.5px;line-height:1.4;color:{c["strong"]};">{md(s.get("caixa",""), c)}</p></div>') if s.get("caixa") else ""
    return top_bar(c, s.get("tag", "")) + body_wrap(
        label(s.get("rotulo"), c) + h2(s["titulo"], c, 28) +
        (f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 22px;">{pills}</div>' if pills else para(s.get("texto"), c) + '<div style="height:18px"></div>') +
        box + signature(c))

def s_evidencia(s, c):
    big = (f'<div style="display:flex;align-items:flex-end;gap:12px;margin-bottom:10px;">'
           f'<span style="font-size:76px;line-height:.85;font-weight:700;letter-spacing:-3px;color:{"#fff" if c["mode"]=="teal" else B};">{s["numero"]}</span>'
           f'<span style="font-size:12px;line-height:1.3;color:{c["text"]};padding-bottom:4px;">{s.get("legenda_numero","")}</span></div>') if s.get("numero") else ""
    return top_bar(c, s.get("tag", "")) + body_wrap(
        label(s.get("rotulo"), c) + big + h2(s["titulo"], c, 26) + para(s.get("texto"), c) + source(s.get("fonte"), c))

def s_destaque(s, c):
    box = (f'<div style="margin-top:18px;padding:15px 16px;background:{c["box_bg"]};border:1px solid {c["box_border"]};border-radius:14px;">'
           f'<p style="font-size:10px;font-weight:700;letter-spacing:2px;color:{c["accent"]};margin-bottom:6px;">{s.get("caixa_rotulo","")}</p>'
           f'<p style="font-size:13.5px;line-height:1.45;color:{c["strong"]};">{md(s.get("caixa",""), c)}</p></div>') if s.get("caixa") else ""
    return top_bar(c, s.get("tag", "")) + body_wrap(
        label(s.get("rotulo"), c) + h2(s["titulo"], c, 27) + para(s.get("texto"), c) + box + source(s.get("fonte"), c))

def s_lista(s, c):
    rows = "".join(f'<div style="display:flex;align-items:flex-start;gap:14px;padding:11px 0;border-bottom:1px solid {c["line"]};">'
                   f'<div style="width:32px;height:32px;border-radius:50%;border:1.5px solid {"#fff" if c["mode"]=="teal" else B};display:flex;align-items:center;justify-content:center;flex-shrink:0">{icon(it.get("icone","check"), c["accent"])}</div>'
                   f'<div><div style="font-size:14px;font-weight:700;color:{c["strong"]};line-height:1.25">{it["titulo"]}</div>'
                   f'<div style="font-size:12px;color:{c["text"]};line-height:1.4;margin-top:2px">{it.get("texto","")}</div></div></div>' for it in s["itens"])
    return top_bar(c, s.get("tag", "")) + body_wrap(label(s.get("rotulo"), c) + h2(s["titulo"], c, 26, 8) + rows)

def s_passos(s, c):
    rows = "".join(f'<div style="display:flex;align-items:flex-start;gap:14px;padding:10px 0;border-bottom:1px solid {c["line"]};">'
                   f'<span style="font-size:24px;font-weight:300;color:{"#fff" if c["mode"]=="teal" else B};min-width:32px;line-height:1;">{k+1:02d}</span>'
                   f'<div><div style="font-size:14px;font-weight:700;color:{c["strong"]};line-height:1.25">{it["titulo"]}</div>'
                   f'<div style="font-size:12px;color:{c["text"]};line-height:1.4;margin-top:2px">{it.get("texto","")}</div></div></div>' for k, it in enumerate(s["itens"]))
    return top_bar(c, s.get("tag", "")) + body_wrap(label(s.get("rotulo"), c) + h2(s["titulo"], c, 28, 8) + rows)

def s_cta(s, c):
    titulo = re.sub(r"\*\*(.+?)\*\*", lambda m: f'<span style="color:{DARK_BG}">{m.group(1)}</span>', s["titulo"])
    return (top_bar(c, s.get("tag", "AGORA"), solid=True, show_handle=False) +
            f'<img src="{LOGO_S_W}" style="position:absolute;right:-70px;top:60px;width:300px;opacity:.08;"/>'
            '<div style="position:absolute;inset:0;padding:0 40px 60px 36px;display:flex;flex-direction:column;justify-content:center;">'
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:26px;"><img src="{AVATAR}" style="width:44px;height:44px;border-radius:50%;object-fit:cover;border:2px solid #fff;"/>'
            f'<div><div style="font-size:13px;font-weight:700;letter-spacing:.5px;color:#fff">{NOME}</div><div style="font-size:11px;color:rgba(255,255,255,0.75)">{HANDLE}</div></div></div>'
            f'<h2 style="font-size:30px;line-height:1.1;font-weight:700;letter-spacing:-0.6px;color:#fff;">{titulo}</h2>'
            f'<p style="font-size:13.5px;line-height:1.5;color:rgba(255,255,255,0.8);margin:14px 0 22px;">{s.get("texto","")}</p>'
            f'<div><span style="display:inline-flex;align-items:center;gap:8px;padding:12px 24px;background:{LIGHT_BG};color:{BD};font-weight:700;font-size:13px;letter-spacing:1px;border-radius:28px;">'
            f'<svg width="14" height="14" viewBox="0 0 24 24" fill="{BD}"><path d="M6 3h12v18l-6-4-6 4z"/></svg>{s.get("botao","SALVAR ESTE POST")}</span></div>'
            f'<p style="font-size:9.5px;line-height:1.5;color:rgba(255,255,255,0.55);margin-top:26px;">{("Referências: " + s["referencias"]) if s.get("referencias") else ""}</p>'
            f'<img src="{LOGO_H_W}" style="width:120px;opacity:.9;margin-top:16px;"/></div>')


# ---------------- Tipos de slide extras (disposições de texto diferentes) ----------------
def _xicon(color):
    return f'<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'
def _vicon(color):
    return f'<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5 9-10"/></svg>'

def s_comparacao(s, c):
    """Duas colunas lado a lado: mito (terracota) x ciência (verde-água)."""
    def col(lado, cor, ic, fundo):
        itens = "".join(f'<div style="display:flex;gap:8px;align-items:flex-start;padding:8px 0;border-top:1px solid {c["line"]};">'
                        f'<span style="margin-top:3px;flex-shrink:0">{ic(cor)}</span><span style="font-size:12px;line-height:1.35;color:{c["strong"]}">{md(t, c)}</span></div>'
                        for t in lado["itens"])
        return (f'<div style="flex:1;padding:14px 12px;border-radius:14px;background:{fundo};">'
                f'<div style="font-size:9.5px;font-weight:700;letter-spacing:2px;color:{cor};margin-bottom:8px;">{lado["rotulo"]}</div>{itens}</div>')
        
    esq = col(s["esquerda"], CORAL, _xicon, "rgba(224,122,95,0.10)")
    dir_ = col(s["direita"], BD if c["mode"] == "light" else B, _vicon, "rgba(108,195,183,0.14)")
    return top_bar(c, s.get("tag", "")) + body_wrap(
        label(s.get("rotulo"), c) + h2(s["titulo"], c, 25, 16) +
        f'<div style="display:flex;gap:10px;text-align:left;">{esq}{dir_}</div>' + source(s.get("fonte"), c))

def s_grade(s, c):
    """Cartões 2x2 com ícone."""
    cards = "".join(f'<div style="padding:14px 12px;border-radius:14px;background:{c["box_bg"]};border:1px solid {c["box_border"]};text-align:left;">'
                    f'<div style="width:30px;height:30px;border-radius:9px;background:{c["icon_bg"]};display:flex;align-items:center;justify-content:center;margin-bottom:10px;">{icon(it.get("icone","check"), c["accent"] if c["mode"]!="teal" else "#fff", 16)}</div>'
                    f'<div style="font-size:13px;font-weight:700;color:{c["strong"]};line-height:1.25">{it["titulo"]}</div>'
                    f'<div style="font-size:11px;color:{c["text"]};line-height:1.4;margin-top:4px">{it.get("texto","")}</div></div>' for it in s["itens"])
    return top_bar(c, s.get("tag", "")) + body_wrap(
        label(s.get("rotulo"), c) + h2(s["titulo"], c, 25, 14) +
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">{cards}</div>')

def s_linha_do_tempo(s, c):
    """Linha do tempo vertical (fases, semanas, progressão)."""
    lc = B if c["mode"] != "teal" else "#fff"
    rows = "".join(f'<div style="display:flex;gap:14px;position:relative;padding-bottom:14px;">'
                   f'<div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;width:14px;">'
                   f'<div style="width:12px;height:12px;border-radius:50%;background:{lc};box-shadow:0 0 0 4px rgba(108,195,183,0.2);margin-top:3px"></div>'
                   + (f'<div style="flex:1;width:2px;background:{c["line"]};margin-top:4px"></div>' if k < len(s["itens"]) - 1 else "") +
                   f'</div><div style="text-align:left"><div style="font-size:9.5px;font-weight:700;letter-spacing:2px;color:{c["accent"]}">{it.get("marco","")}</div>'
                   f'<div style="font-size:14px;font-weight:700;color:{c["strong"]};line-height:1.25;margin-top:2px">{it["titulo"]}</div>'
                   f'<div style="font-size:11.5px;color:{c["text"]};line-height:1.4;margin-top:2px">{it.get("texto","")}</div></div></div>'
                   for k, it in enumerate(s["itens"]))
    return top_bar(c, s.get("tag", "")) + body_wrap(label(s.get("rotulo"), c) + h2(s["titulo"], c, 25, 16) + rows)

def s_citacao(s, c):
    """Frase de impacto grande entre aspas, com a fonte embaixo."""
    q = B if c["mode"] != "teal" else "#fff"
    return top_bar(c, s.get("tag", "")) + body_wrap(
        f'<div style="font-size:90px;line-height:.6;font-weight:700;color:{q};opacity:.9;height:44px">&ldquo;</div>'
        f'<p style="font-size:24px;line-height:1.25;font-weight:500;letter-spacing:-0.3px;color:{c["title"]};">{md(s["frase"], c)}</p>'
        f'<div style="display:flex;align-items:center;gap:10px;margin-top:18px;"><div style="width:26px;height:2px;background:{q}"></div>'
        f'<span style="font-size:11px;color:{c["muted"]}">{s.get("fonte","")}</span></div>')

def s_manchete(s, c):
    """Só tipografia: uma afirmação enorme. Bom para virada de narrativa."""
    return top_bar(c, s.get("tag", "")) + body_wrap(
        label(s.get("rotulo"), c) +
        f'<h2 style="font-size:{s.get("tamanho", 40)}px;line-height:1.02;font-weight:700;letter-spacing:-1.2px;color:{c["title"]};text-transform:{"uppercase" if s.get("caixa_alta") else "none"};">{md(s["titulo"], c)}</h2>'
        + para(s.get("texto"), c, 16))

def s_dado(s, c):
    """Número gigante centralizado dentro de um anel, com a frase e a fonte."""
    rc = B if c["mode"] != "teal" else "#fff"
    pct = max(0, min(100, float(s.get("anel", 0))))
    circ = 2 * 3.14159 * 70
    ring = (f'<svg width="170" height="170" viewBox="0 0 170 170" style="position:absolute;inset:0"><circle cx="85" cy="85" r="70" fill="none" stroke="{c["line"]}" stroke-width="8"/>'
            f'<circle cx="85" cy="85" r="70" fill="none" stroke="{rc}" stroke-width="8" stroke-linecap="round" stroke-dasharray="{circ*pct/100:.1f} {circ:.1f}" transform="rotate(-90 85 85)"/></svg>') if pct else ""
    return top_bar(c, s.get("tag", "")) + body_wrap(
        label(s.get("rotulo"), c) +
        f'<div style="position:relative;width:170px;height:170px;display:flex;align-items:center;justify-content:center;margin:4px auto 14px;">{ring}'
        f'<div style="text-align:center"><div style="font-size:52px;font-weight:700;letter-spacing:-2px;line-height:1;color:{c["title"]}">{s["numero"]}</div>'
        f'<div style="font-size:11px;color:{c["text"]};margin-top:4px">{s.get("unidade","")}</div></div></div>'
        + h2(s["titulo"], c, 22) + para(s.get("texto"), c) + source(s.get("fonte"), c))

# ---------------- Estilos (variar a cada post; a paleta é sempre a mesma) ----------------
ESTILOS = {
    "alternado": ["claro", "escuro"],            # claro/escuro intercalados (estilo do 1º post)
    "escuro":    ["escuro"],                     # tudo escuro, capa escura, números-fantasma
    "claro":     ["claro"],                      # tudo claro, barra lateral verde-água, números-fantasma
    "blocos":    ["claro", "verde", "escuro"],   # rodízio claro / bloco verde-água / escuro
    "verde":     ["escuro", "verde"],            # capa escura, intercala escuro e verde-água
    "areia":     ["areia", "marinho"],           # quente e frio: areia + azul-marinho, verde-água como acento
    "editorial": ["claro", "areia", "escuro"],   # revista: claro, areia, escuro
}
def modo_do_estilo(estilo, i):
    seq = ESTILOS.get(estilo, ESTILOS["alternado"])
    return seq[i % len(seq)]

def decor(estilo, i, c):
    out = ""
    if estilo in ("escuro", "claro", "verde") and i > 0:
        col = "rgba(255,255,255,0.05)" if c["mode"] != "light" else "rgba(43,126,115,0.07)"
        out += f'<div style="position:absolute;right:40px;top:44px;font-size:120px;font-weight:700;line-height:1;color:{col};letter-spacing:-4px;">{i+1:02d}</div>'
    if estilo == "claro" and i > 0:
        out += f'<div style="position:absolute;left:0;top:0;bottom:0;width:5px;background:linear-gradient({B},{BD});"></div>'
    if estilo == "blocos" and c["mode"] == "teal":
        out += f'<img src="{LOGO_S_W}" style="position:absolute;left:-50px;top:40px;width:240px;opacity:.06;"/>'
    return out

TIPOS = dict(capa=s_capa, mito=s_mito, evidencia=s_evidencia, destaque=s_destaque, lista=s_lista, passos=s_passos, cta=s_cta,
             comparacao=s_comparacao, grade=s_grade, linha_do_tempo=s_linha_do_tempo, citacao=s_citacao, manchete=s_manchete, dado=s_dado)

def build_html(spec):
    slides = spec["slides"]
    total = len(slides)
    out = []
    for i, s in enumerate(slides):
        last = i == total - 1
        if s["tipo"] == "cta":
            bg = f"background:linear-gradient(165deg, #174F48 0%, {BD} 50%, #4FAEA1 100%);"
            c = pal(False)
            inner = s_cta(s, c) + progress_bar(i, total, c, "#fff")
        else:
            modo = s.get("fundo") or modo_do_estilo(spec.get("estilo", "alternado"), i)
            _ALINHAR["v"] = s.get("disposicao", "base")
            _ALINHAR["centro_texto"] = s.get("disposicao") == "centro"
            c = pal({"claro": True, "escuro": False, "verde": "teal", "areia": "areia", "marinho": "marinho"}[modo])
            bg = c["bg"]
            inner = (decor(spec.get("estilo", "alternado"), i, c) + TIPOS[s["tipo"]](s, c) +
                     progress_bar(i, total, c, c["fill"] if c["mode"] == "teal" else None) + ("" if last else swipe_arrow(c)))
        out.append(f'<div class="slide" style="{bg}">{inner}</div>')
    css = FONTS + """*{margin:0;padding:0;box-sizing:border-box}
body{background:#E9EEED;font-family:'Poppins',sans-serif;display:flex;justify-content:center;padding:24px 0;-webkit-font-smoothing:antialiased}
.ig-frame{width:420px;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.12)}
.ig-header{display:flex;align-items:center;gap:10px;padding:12px 14px}.ig-avatar{width:32px;height:32px;border-radius:50%;object-fit:cover}
.ig-handle{font-size:13px;font-weight:700;color:#111}.ig-sub{font-size:11px;color:#888}
.carousel-viewport{width:420px;aspect-ratio:4/5;overflow:hidden;position:relative;cursor:grab;touch-action:pan-y}
.carousel-track{display:flex;height:100%;transition:transform .35s ease}
.slide{width:420px;min-width:420px;height:525px;position:relative;overflow:hidden}
.ig-dots{display:flex;justify-content:center;gap:4px;padding:10px 0}.ig-dots span{width:6px;height:6px;border-radius:50%;background:#ccc}.ig-dots span.on{background:%B%}
.ig-actions{display:flex;gap:14px;padding:0 14px 6px}.ig-caption{font-size:12.5px;padding:0 14px 14px;color:#111;line-height:1.4;white-space:pre-line}
.ig-caption small{display:block;color:#999;font-size:10px;margin-top:6px;letter-spacing:.5px}""".replace("%B%", B)
    act = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#111" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    resumo = spec.get("legenda", "").split("\n")[0]
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{spec.get('titulo','Carrossel')}</title><style>{css}</style></head><body>
<div class="ig-frame"><div class="ig-header"><img class="ig-avatar" src="{AVATAR}"/><div><div class="ig-handle">{HANDLE[1:]}</div><div class="ig-sub">Fisioterapia | Biomecânica</div></div></div>
<div class="carousel-viewport" id="vp"><div class="carousel-track" id="tr">{''.join(out)}</div></div>
<div class="ig-dots" id="dots">{''.join('<span></span>' for _ in range(total))}</div>
<div class="ig-actions">{act}<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/></svg>{act}<path d="M21 12a8 8 0 0 1-11.8 7L3 21l2-6A8 8 0 1 1 21 12z"/></svg>{act}<path d="M22 2L11 13M22 2l-7 20-4-9-9-4z"/></svg><span style="flex:1"></span>{act}<path d="M6 3h12v18l-6-4-6 4z"/></svg></div>
<div class="ig-caption"><b>{HANDLE[1:]}</b> {resumo}<small>HÁ 2 HORAS</small></div></div>
<script>
const tr=document.getElementById('tr'),vp=document.getElementById('vp'),dots=[...document.querySelectorAll('#dots span')];let i=0,sx=null;
function go(n){{i=Math.max(0,Math.min({total-1},n));tr.style.transform='translateX('+(-i*420)+'px)';dots.forEach((d,k)=>d.classList.toggle('on',k===i));}}
vp.addEventListener('pointerdown',e=>{{sx=e.clientX}});vp.addEventListener('pointerup',e=>{{if(sx===null)return;const dx=e.clientX-sx;if(Math.abs(dx)>30)go(i+(dx<0?1:-1));sx=null;}});
document.addEventListener('keydown',e=>{{if(e.key==='ArrowRight')go(i+1);if(e.key==='ArrowLeft')go(i-1);}});go(0);
</script></body></html>"""

async def export(html_path, out_dir, total):
    from playwright.async_api import async_playwright
    from PIL import Image
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page(viewport={"width": 420, "height": 525}, device_scale_factor=1080 / 420)
        await page.set_content(html_path.read_text(encoding="utf-8"), wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.evaluate("""() => {
          document.querySelectorAll('.ig-header,.ig-dots,.ig-actions,.ig-caption').forEach(e=>e.style.display='none');
          document.querySelector('.ig-frame').style.cssText='width:420px;height:525px;max-width:none;border-radius:0;box-shadow:none;overflow:hidden;margin:0;';
          document.querySelector('.carousel-viewport').style.cssText='width:420px;height:525px;aspect-ratio:unset;overflow:hidden;cursor:default;';
          document.body.style.cssText='padding:0;margin:0;display:block;overflow:hidden;';}""")
        for i in range(total):
            await page.evaluate("(i)=>{const t=document.querySelector('.carousel-track');t.style.transition='none';t.style.transform='translateX('+(-i*420)+'px)';}", i)
            await page.wait_for_timeout(250)
            png = out_dir / f"slide_{i+1}.png"
            await page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": 420, "height": 525})
            Image.open(png).convert("RGB").save(out_dir / f"slide_{i+1}.jpg", quality=93)
        await b.close()

if __name__ == "__main__":
    spec_path = Path(sys.argv[1]).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    html = build_html(spec)
    out = spec_path.parent
    (out / "carrossel.html").write_text(html, encoding="utf-8")
    asyncio.run(export(out / "carrossel.html", out, len(spec["slides"])))
    print(f"ok: {len(spec['slides'])} slides em {out}")
