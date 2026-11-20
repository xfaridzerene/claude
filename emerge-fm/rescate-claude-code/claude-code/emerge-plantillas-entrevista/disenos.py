# Propuestas de diseño (imágenes fijas) para automatizar los reels de entrevistas de Emerge Noticias.
# 3 verticales (1080×1920) y 2 horizontales (1920×1080), con el mismo contenido de ejemplo
# (Nicolás Larenas) para poder compararlas.
#   python disenos.py   -> salida/V1..V3, H1..H2 + salida/comparativa.png
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
EFM = r'C:\Users\farid\Desktop\EMERGE FM'
F_UNB = os.path.join(EFM, 'Fuentes', 'Unbounded', 'static', 'Unbounded-{}.ttf')
F_SG = os.path.join(EFM, 'Fuentes', 'Space_Grotesk', 'static', 'SpaceGrotesk-{}.ttf')
LOGO_H = os.path.join(EFM, 'LOGO', 'Logo 105.5', 'PNG', 'emerge-fm-105.5-horizontal-color-transparente.png')

VERDE = (0, 230, 171)
NEGRO = (10, 10, 10)
BLANCO = (255, 255, 255)

# ---- contenido de ejemplo (en la automatización vendría de la ficha de cada entrevista) ----
NOMBRE = 'Nicolás Larenas'
CARGO = "Director regional Gremio Agricultores en O'Higgins"
TEMA = 'ALZA DE COMBUSTIBLES'
TITULAR = ['«En la medida que el', 'gobierno no ', ('baje el moño', 1), ',', 'no vamos a avanzar»']
SUB = ['Hoy', 'día', 'no', 'tenemos', 'para', 'salir', 'a', 'trabajar.']
ACTIVA = 3  # índice de la palabra que suena
FECHA = '12 NOV 2026'

CUADRO = Image.open(os.path.join(AQUI, 'recursos', 'cuadro_88.png')).convert('RGB')  # 16:9 del programa
FOTO = Image.open(os.path.join(AQUI, 'recursos', 'larenas.png')).convert('RGB')     # cuadrada
_lh = Image.open(LOGO_H).convert('RGBA')
LOGO = _lh.crop(_lh.getbbox())


def f(tipo, peso, tam):
    return ImageFont.truetype((F_UNB if tipo == 'u' else F_SG).format(peso), tam)


def logo(ancho):
    return LOGO.resize((ancho, int(LOGO.height * ancho / LOGO.width)), Image.LANCZOS)


def fondo_borroso(w, h, osc=0.34):
    im = CUADRO.copy()
    cw = int(im.height * w / h) if w / h < im.width / im.height else im.width
    ch = int(cw * h / w)
    x = (im.width - cw) // 2
    y = (im.height - ch) // 2
    im = im.crop((x, y, x + cw, y + ch)).resize((w // 20, h // 20), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(2)).resize((w, h), Image.BICUBIC)
    a = np.asarray(im).astype(np.float32) * osc
    yy = np.linspace(-1, 1, h)[:, None, None]
    a *= 1 - 0.45 * np.clip(yy ** 2, 0, 1)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')


def video(w):
    return CUADRO.resize((w, int(w * 9 / 16)), Image.LANCZOS).convert('RGBA')


def chip(d, x, y, txt, fnt, fondo=VERDE, color=NEGRO, padx=18, pady=10, esp=3, radio=None):
    anchos = [d.textlength(c, font=fnt) for c in txt]
    tw = sum(anchos) + esp * (len(txt) - 1)
    asc, desc = fnt.getmetrics()
    bb = fnt.getbbox('ÁEMg')
    th = bb[3] - bb[1]
    w, h = tw + padx * 2, th + pady * 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=h / 2 if radio is None else radio, fill=fondo)
    cx = x + padx
    for c, a in zip(txt, anchos):
        d.text((cx, y + pady - bb[1]), c, font=fnt, fill=color)
        cx += a + esp
    return w, h


def foto_circulo(diam, aro=0, color_aro=VERDE):
    fw, fh = FOTO.size
    lado = min(fw, fh)
    im = FOTO.crop(((fw - lado) // 2, 0, (fw - lado) // 2 + lado, lado)).resize((diam, diam), Image.LANCZOS)
    out = Image.new('RGBA', (diam + 2 * aro, diam + 2 * aro), (0, 0, 0, 0))
    if aro:
        ImageDraw.Draw(out).ellipse([0, 0, out.width - 1, out.height - 1], fill=color_aro)
    m = Image.new('L', (diam * 4, diam * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, diam * 4 - 1, diam * 4 - 1], fill=255)
    out.paste(im, (aro, aro), m.resize((diam, diam), Image.LANCZOS))
    return out


def foto_tarjeta(w, h, borde=8, radio=28):
    fw, fh = FOTO.size
    cw = int(fh * w / h)
    x0 = max(0, min(fw - cw, 385 - cw // 2))
    im = FOTO.crop((x0, 0, x0 + cw, fh)).resize((w, h), Image.LANCZOS)
    out = Image.new('RGBA', (w + 2 * borde, h + 2 * borde), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle([0, 0, out.width - 1, out.height - 1], radius=radio + borde, fill=VERDE)
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=radio, fill=255)
    out.paste(im, (borde, borde), m)
    return out


_rng = np.random.default_rng(7)
ENV = np.clip(np.convolve(np.abs(_rng.normal(0.55, 0.35, 400)), np.ones(3) / 3, 'same'), 0.05, 1)
ENV[np.arange(400) % 37 < 5] = 0.06  # pausas


def onda(d, x0, x1, cy, alto, n=46, gap=8, color=VERDE, desvanecer=True):
    bw = (x1 - x0 - gap * (n - 1)) / n
    for k in range(n):
        v = ENV[k * 3 + 10]
        h = max(6, v * alto)
        a = int(110 + 145 * k / (n - 1)) if desvanecer else 255
        x = x0 + k * (bw + gap)
        d.rounded_rectangle([x, cy - h / 2, x + bw, cy + h / 2], radius=bw / 2, fill=color + (a,))


def onda_anillo(d, cx, cy, r, largo, n=72, color=VERDE):
    for k in range(n):
        ang = 2 * np.pi * k / n - np.pi / 2
        v = ENV[(k * 5) % 400]
        l = 6 + v * largo
        x0, y0 = cx + np.cos(ang) * r, cy + np.sin(ang) * r
        x1, y1 = cx + np.cos(ang) * (r + l), cy + np.sin(ang) * (r + l)
        d.line([x0, y0, x1, y1], fill=color + (235,), width=6)


def lineas(palabras, fnt, ancho_max, d, mayus=False):
    esp = d.textlength(' ', font=fnt)
    res, act, w = [], [], 0
    for i, p in enumerate(palabras):
        t = p.upper() if mayus else p
        a = d.textlength(t, font=fnt)
        if act and w + esp + a > ancho_max:
            res.append(act); act, w = [], 0
        act.append((i, t, a))
        w += (esp if w else 0) + a
    res.append(act)
    return res, esp


def subtitulo(d, cx, y, fnt, ancho_max, estilo, alto_linea=None, mayus=False):
    """estilo: 'caja' (palabra activa en caja verde), 'color' (activa en texto verde),
    'banda' (todo sobre caja blanca, activa en verde), 'oscura' (sobre caja negra translúcida)."""
    ls, esp = lineas(SUB, fnt, ancho_max, d, mayus)
    asc, desc = fnt.getmetrics()
    alto_linea = alto_linea or int((asc + desc) * 1.12)
    if estilo in ('banda', 'oscura'):
        anchos = [sum(a for _, _, a in l) + esp * (len(l) - 1) for l in ls]
        pad = 26
        x0, x1 = cx - max(anchos) / 2 - pad, cx + max(anchos) / 2 + pad
        fondo = BLANCO + (255,) if estilo == 'banda' else (0, 0, 0, 165)
        d.rounded_rectangle([x0, y - 14, x1, y + alto_linea * len(ls) + 4], radius=18, fill=fondo)
    for j, l in enumerate(ls):
        ancho = sum(a for _, _, a in l) + esp * (len(l) - 1)
        x = cx - ancho / 2
        yy = y + j * alto_linea
        for i, t, a in l:
            activa = i == ACTIVA
            dicha = i <= ACTIVA
            if estilo == 'caja':
                if activa:
                    d.rounded_rectangle([x - 10, yy + 2, x + a + 10, yy + asc + desc - 2], radius=12, fill=VERDE)
                    col = NEGRO
                else:
                    d.text((x + 2, yy + 3), t, font=fnt, fill=(0, 0, 0, 170))
                    col = BLANCO if dicha else (190, 190, 190)
            elif estilo == 'color':
                d.text((x + 3, yy + 4), t, font=fnt, fill=(0, 0, 0, 200))
                col = VERDE if activa else (BLANCO if dicha else (200, 200, 200))
            elif estilo == 'banda':
                if activa:
                    d.rounded_rectangle([x - 8, yy + 2, x + a + 8, yy + asc + desc - 2], radius=10, fill=VERDE)
                col = NEGRO if dicha else (120, 120, 120)
            else:  # oscura
                col = VERDE if activa else (BLANCO if dicha else (185, 185, 185))
            d.text((x, yy), t, font=fnt, fill=col)
            x += a + esp
    return alto_linea * len(ls)


def titular(d, x, y, fnt, alto_linea, color=BLANCO, acento=VERDE, ancho_max=940):
    """TITULAR: lista de fragmentos; (texto, 1) va en verde. Corta líneas por palabras."""
    piezas = []
    for frag in TITULAR:
        txt, verde = (frag if isinstance(frag, tuple) else (frag, 0))
        for k, pal in enumerate(txt.split(' ')):
            if pal == '' and k:
                continue
            piezas.append((pal, verde, k > 0 or txt.startswith(' ')))
    # reconstruir con espacios correctos
    esp = d.textlength(' ', font=fnt)
    cx, cy = x, y
    primera = True
    for pal, verde, con_esp in piezas:
        if pal == '':
            continue
        a = d.textlength(pal, font=fnt)
        sep = esp if (con_esp and not primera and pal not in (',', '.')) else 0
        if not primera and cx + sep + a > x + ancho_max:
            cx, cy = x, cy + alto_linea
            sep = 0
        d.text((cx + sep, cy), pal, font=fnt, fill=acento if verde else color)
        cx += sep + a
        primera = False
    return cy + alto_linea - y


# =====================================================================================
def v1_titular():
    """V1 · TITULAR: la frase fuerte arriba en grande; el invitado como insignia sobre el video."""
    W, H = 1080, 1920
    im = fondo_borroso(W, H)
    d = ImageDraw.Draw(im)
    lg = logo(230)
    im.alpha_composite(lg, ((W - lg.width) // 2, 80))
    chip(d, 70, 210, TEMA, f('s', 'Bold', 28))
    d.text((58, 262), '«', font=f('u', 'Black', 150), fill=VERDE)
    titular(d, 70, 410, f('u', 'ExtraBold', 62), 84)
    BOX_Y = 840
    v = video(W)
    im.alpha_composite(v, (0, BOX_Y))
    d.rectangle([0, BOX_Y - 8, W, BOX_Y - 1], fill=VERDE)
    d.rectangle([0, BOX_Y + v.height, W, BOX_Y + v.height + 7], fill=VERDE)
    # insignia del invitado montada sobre el borde superior del video
    fc = foto_circulo(150, aro=7)
    px, py = 60, BOX_Y - 90
    d.rounded_rectangle([px + 70, py + 38, px + 760, py + 128], radius=45, fill=(12, 12, 12, 235))
    im.alpha_composite(fc, (px, py))
    d.text((px + 190, py + 46), NOMBRE, font=f('u', 'Bold', 34), fill=BLANCO)
    d.text((px + 190, py + 92), CARGO, font=f('s', 'Medium', 24), fill=(205, 205, 205))
    y = BOX_Y + v.height + 70
    subtitulo(d, W / 2, y, f('s', 'Bold', 56), 900, 'caja')
    onda(d, 120, W - 120, 1790, 70, n=40)
    return im.convert('RGB')


def v2_dividida():
    """V2 · PANTALLA DIVIDIDA: el invitado arriba a sangre (como videollamada), el programa abajo."""
    W, H = 1080, 1920
    im = Image.new('RGBA', (W, H), (12, 12, 12, 255))
    # foto a sangre 1080×900
    fw, fh = FOTO.size
    ft = FOTO.resize((W, W), Image.LANCZOS).crop((0, 70, W, 70 + 900)).convert('RGBA')
    im.alpha_composite(ft, (0, 0))
    g = np.zeros((900, W, 4), np.uint8)
    a = np.clip((np.linspace(0, 1, 900) - 0.45) / 0.55, 0, 1) ** 1.6
    g[..., 3] = (a[:, None] * 245).astype(np.uint8)
    g[..., :3] = 12
    im.alpha_composite(Image.fromarray(g, 'RGBA'), (0, 0))
    # sombra arriba para el logo
    g2 = np.zeros((220, W, 4), np.uint8)
    g2[..., 3] = (np.linspace(150, 0, 220)[:, None]).astype(np.uint8)
    im.alpha_composite(Image.fromarray(g2, 'RGBA'), (0, 0))
    d = ImageDraw.Draw(im)
    lg = logo(220)
    im.alpha_composite(lg, (60, 64))
    chip(d, 60, 600, 'EN EMERGE NOTICIAS', f('s', 'Bold', 26))
    d.text((56, 650), 'Nicolás', font=f('u', 'ExtraBold', 84), fill=BLANCO)
    d.text((56, 748), 'Larenas', font=f('u', 'ExtraBold', 84), fill=BLANCO)
    d.text((60, 862), CARGO, font=f('s', 'Medium', 32), fill=(215, 215, 215))
    # onda en la costura
    onda(d, 60, W - 60, 960, 70, n=46)
    BOX_Y = 1030
    v = video(W)
    im.alpha_composite(v, (0, BOX_Y))
    d.rectangle([0, BOX_Y - 6, W, BOX_Y - 1], fill=VERDE)
    subtitulo(d, W / 2, BOX_Y + v.height + 70, f('u', 'Bold', 50), 940, 'color', mayus=True, alto_linea=74)
    return im.convert('RGB')


def v3_noticiero():
    """V3 · NOTICIERO: estilo canal de noticias, con titular, GC del invitado como el del programa y cintillo."""
    W, H = 1080, 1920
    im = fondo_borroso(W, H, osc=0.22)
    d = ImageDraw.Draw(im)
    # cabecera
    d.rectangle([0, 0, W, 150], fill=(8, 8, 8, 255))
    d.rectangle([0, 150, W, 156], fill=VERDE)
    lg = logo(220)
    im.alpha_composite(lg, (50, (150 - lg.height) // 2 + 4))
    fs = f('s', 'Bold', 28)
    d.text((W - 50 - d.textlength(FECHA, font=fs), 58), FECHA, font=fs, fill=(200, 200, 200))
    # titular
    chip(d, 60, 250, TEMA, f('s', 'Bold', 28), fondo=BLANCO, color=NEGRO, radio=6)
    ft = f('u', 'ExtraBold', 58)
    d.text((60, 330), 'Agricultores: «Hoy no es', font=ft, fill=BLANCO)
    d.text((60, 410), 'rentable salir a trabajar»', font=ft, fill=VERDE)
    BOX_Y = 560
    v = video(W)
    im.alpha_composite(v, (0, BOX_Y))
    # GC del invitado, mismo lenguaje que el GC del programa (bloque verde + barra blanca)
    gy = BOX_Y + v.height + 40
    d.rectangle([40, gy, 250, gy + 170], fill=VERDE)
    fc = foto_circulo(140, aro=0)
    im.alpha_composite(fc, (75, gy + 15))
    d.rectangle([250, gy, W - 40, gy + 170], fill=BLANCO)
    d.text((280, gy + 30), NOMBRE, font=f('u', 'Bold', 46), fill=NEGRO)
    d.text((282, gy + 102), CARGO, font=f('s', 'Medium', 28), fill=(70, 70, 70))
    d.rectangle([40, gy + 170, W - 40, gy + 176], fill=VERDE)
    # subtítulos
    subtitulo(d, W / 2, gy + 260, f('s', 'Bold', 54), 900, 'banda')
    # cintillo
    cy = H - 170
    d.rectangle([0, cy, W, cy + 90], fill=(8, 8, 8, 255))
    w, h = chip(d, 0, cy, 'ÚLTIMO', f('u', 'Bold', 30), fondo=VERDE, color=NEGRO, padx=30, pady=28, radio=0)
    d.text((w + 26, cy + 26), 'Agricultores de O\'Higgins se suman al paro de camioneros  •  Piden atacar',
           font=f('s', 'SemiBold', 32), fill=BLANCO)
    return im.convert('RGB')


def h1_panel():
    """H1 · PANEL LATERAL (16:9): video del programa a la izquierda, ficha del invitado a la derecha."""
    W, H = 1920, 1080
    im = fondo_borroso(W, H, osc=0.25)
    d = ImageDraw.Draw(im)
    v = video(1380)
    vx, vy = 50, 60
    d.rounded_rectangle([vx - 6, vy - 6, vx + v.width + 5, vy + v.height + 5], radius=10, fill=VERDE)
    im.alpha_composite(v, (vx, vy))
    # columna derecha
    cx0 = vx + v.width + 50
    lg = logo(250)
    im.alpha_composite(lg, (cx0, 70))
    ft = foto_tarjeta(300, 380)
    im.alpha_composite(ft, (cx0, 170))
    chip(d, cx0, 590, 'EN EMERGE NOTICIAS', f('s', 'Bold', 22))
    d.text((cx0, 640), 'Nicolás', font=f('u', 'ExtraBold', 52), fill=BLANCO)
    d.text((cx0, 702), 'Larenas', font=f('u', 'ExtraBold', 52), fill=BLANCO)
    for j, l in enumerate(['Director regional', 'Gremio Agricultores', "en O'Higgins"]):
        d.text((cx0, 790 + j * 38), l, font=f('s', 'Medium', 28), fill=(210, 210, 210))
    onda(d, cx0, W - 50, 960, 60, n=20, gap=7)
    # subtítulos bajo el video
    subtitulo(d, vx + v.width / 2, vy + v.height + 50, f('s', 'Bold', 50), 1300, 'caja')
    return im.convert('RGB')


def h2_burbuja():
    """H2 · BURBUJA (16:9): el programa a pantalla completa; el invitado entra como burbuja con anillo de audio."""
    W, H = 1920, 1080
    im = video(W)
    im = im.crop((0, 0, W, H)) if im.height >= H else im.resize((W, H))
    d = ImageDraw.Draw(im)
    # burbuja arriba a la izquierda
    cx, cy, r = 190, 200, 105
    halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([cx - r - 70, cy - r - 70, cx + r + 70, cy + r + 70], fill=(0, 0, 0, 120))
    im.alpha_composite(halo.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(im)
    onda_anillo(d, cx, cy, r + 12, 38)
    fc = foto_circulo(2 * r, aro=6)
    im.alpha_composite(fc, (cx - r - 6, cy - r - 6))
    # ficha junto a la burbuja
    x0 = cx + r + 70
    d.rounded_rectangle([x0, cy - 78, x0 + 700, cy + 78], radius=24, fill=(10, 10, 10, 215))
    chip(d, x0 + 26, cy - 60, 'EN EMERGE NOTICIAS', f('s', 'Bold', 20))
    d.text((x0 + 26, cy - 16), NOMBRE, font=f('u', 'Bold', 40), fill=BLANCO)
    d.text((x0 + 28, cy + 38), CARGO, font=f('s', 'Medium', 24), fill=(210, 210, 210))
    # subtítulos sobre el video, por encima del GC del programa
    subtitulo(d, W / 2, 770, f('s', 'Bold', 52), 1500, 'oscura')
    return im.convert('RGB')


def main():
    os.makedirs(os.path.join(AQUI, 'salida'), exist_ok=True)
    piezas = [('V1-titular', v1_titular), ('V2-pantalla-dividida', v2_dividida), ('V3-noticiero', v3_noticiero),
              ('H1-panel-lateral', h1_panel), ('H2-burbuja', h2_burbuja)]
    ims = {}
    for nombre, fn in piezas:
        im = fn()
        im.save(os.path.join(AQUI, 'salida', nombre + '.png'))
        ims[nombre] = im
        print('ok', nombre, im.size)
    # comparativa: verticales arriba, horizontales abajo
    alto_v = 900
    vs = [ims[k].resize((int(1080 * alto_v / 1920), alto_v), Image.LANCZOS) for k in list(ims)[:3]]
    hs = [ims[k].resize((int(1920 * 440 / 1080), 440), Image.LANCZOS) for k in list(ims)[3:]]
    ancho = max(sum(v.width for v in vs) + 40 * 4, sum(h.width for h in hs) + 40 * 3)
    hoja = Image.new('RGB', (ancho, alto_v + 440 + 40 * 3 + 90), (24, 24, 24))
    dh = ImageDraw.Draw(hoja)
    x = 40
    for k, v in zip(list(ims)[:3], vs):
        hoja.paste(v, (x, 40)); dh.text((x, 40 + alto_v + 8), k, font=f('s', 'Bold', 26), fill=VERDE); x += v.width + 40
    x = 40
    y = 40 + alto_v + 60
    for k, h in zip(list(ims)[3:], hs):
        hoja.paste(h, (x, y)); dh.text((x, y + 448), k, font=f('s', 'Bold', 26), fill=VERDE); x += h.width + 40
    hoja.save(os.path.join(AQUI, 'salida', 'comparativa.png'))
    print('ok comparativa', hoja.size)


if __name__ == '__main__':
    main()
