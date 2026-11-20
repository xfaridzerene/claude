# Variaciones del diseño V1 · Titular (vertical 1080×1920) para los reels de entrevistas.
# Usa los recursos y ayudas de disenos.py.
#   python disenos_v1.py  -> salida/V1a..V1e + salida/comparativa-v1.png
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import disenos as D
from disenos import f, VERDE, NEGRO, BLANCO, NOMBRE, CARGO, TEMA, FOTO

W, H = 1080, 1920
LOGO_NEGRO = os.path.join(D.EFM, 'LOGO', 'Logo 105.5', 'PNG', 'emerge-fm-105.5-horizontal-mono-negro.png')


def tokens():
    out, verde = [], False
    for pal in D.TITULAR.split(' '):
        if pal.startswith('['):
            verde, pal = True, pal[1:]
        cierra = ']' in pal
        out.append((pal.replace(']', ''), verde))
        if cierra:
            verde = False
    return out


def armar(d, fnt, ancho_max):
    esp = d.textlength(' ', font=fnt)
    lineas, act, w = [], [], 0
    for pal, verde in tokens():
        a = d.textlength(pal, font=fnt)
        if act and w + esp + a > ancho_max:
            lineas.append(act); act, w = [], 0
        act.append((pal, verde, a))
        w += (esp if w else 0) + a
    lineas.append(act)
    return lineas, esp


def titular(d, x, y, fnt, alto, ancho_max, color=BLANCO, acento=VERDE, centrar=False):
    lineas, esp = armar(d, fnt, ancho_max)
    for j, l in enumerate(lineas):
        ancho = sum(a for *_, a in l) + esp * (len(l) - 1)
        cx = x - ancho / 2 if centrar else x
        for pal, verde, a in l:
            d.text((cx, y + j * alto), pal, font=fnt, fill=acento if verde else color)
            cx += a + esp
    return len(lineas) * alto


def logo_negro(ancho):
    lg = Image.open(LOGO_NEGRO).convert('RGBA')
    lg = lg.crop(lg.getbbox())
    return lg.resize((ancho, int(lg.height * ancho / lg.width)), Image.LANCZOS)


def poner_video(im, d, y, filetes=True):
    v = D.video(W)
    im.alpha_composite(v, (0, y))
    if filetes:
        d.rectangle([0, y - 8, W, y - 1], fill=VERDE)
        d.rectangle([0, y + v.height, W, y + v.height + 7], fill=VERDE)
    return v.height


def insignia(im, d, x, y, diam=150):
    """Foto redonda + píldora oscura con nombre y cargo (como en V1)."""
    fn, fc = f('u', 'Bold', 34), f('s', 'Medium', 24)
    ancho = max(d.textlength(NOMBRE, font=fn), d.textlength(CARGO, font=fc))
    k = diam / 150
    d.rounded_rectangle([x + 70 * k, y + 34 * k, x + diam + 40 + ancho + 40, y + diam - 18 * k],
                        radius=(diam - 52 * k) / 2, fill=(12, 12, 12, 235))
    im.alpha_composite(D.foto_circulo(diam, aro=7), (x, y))
    d.text((x + diam + 40, y + 44 * k), NOMBRE, font=fn, fill=BLANCO)
    d.text((x + diam + 40, y + 92 * k), CARGO, font=fc, fill=(205, 205, 205))


def cierre(d, y_sub, onda=True):
    D.subtitulo(d, W / 2, y_sub, f('s', 'Bold', 56), 900, 'caja')
    if onda:
        D.onda(d, 120, W - 120, 1800, 64, n=40)


# ------------------------------------------------------------------------------------
def v1a_bloque_verde():
    """Titular en negro sobre un bloque verde de marca; las palabras clave en blanco."""
    im = D.fondo_borroso(W, H)
    d = ImageDraw.Draw(im, 'RGBA')
    BOX_Y = 860
    d.rectangle([0, 0, W, BOX_Y], fill=VERDE)
    lg = logo_negro(230)
    im.alpha_composite(lg, ((W - lg.width) // 2, 80))
    D.chip(d, 70, 220, TEMA, f('s', 'Bold', 28), fondo=NEGRO, color=VERDE)
    titular(d, 70, 310, f('u', 'ExtraBold', 70), 92, 940, color=NEGRO, acento=BLANCO)
    hv = poner_video(im, d, BOX_Y, filetes=False)
    d.rectangle([0, BOX_Y + hv, W, BOX_Y + hv + 7], fill=VERDE)
    insignia(im, d, 60, BOX_Y - 92)
    cierre(d, BOX_Y + hv + 70)
    return im.convert('RGB')


def v1b_foto_grande():
    """La foto del invitado a sangre arriba y el titular encima, sobre el degradado."""
    im = Image.new('RGBA', (W, H), (12, 12, 12, 255))
    alto_f = 880
    ft = FOTO.resize((W, W), Image.LANCZOS).crop((0, 0, W, alto_f)).convert('RGBA')
    im.alpha_composite(ft, (0, 0))
    g = np.zeros((alto_f, W, 4), np.uint8)
    a = np.clip((np.linspace(0, 1, alto_f) - 0.25) / 0.75, 0, 1) ** 1.3
    g[..., 3] = (a[:, None] * 250).astype(np.uint8)
    g[..., :3] = 12
    im.alpha_composite(Image.fromarray(g, 'RGBA'))
    g2 = np.zeros((200, W, 4), np.uint8)
    g2[..., 3] = np.linspace(140, 0, 200)[:, None].astype(np.uint8)
    im.alpha_composite(Image.fromarray(g2, 'RGBA'))
    d = ImageDraw.Draw(im, 'RGBA')
    im.alpha_composite(D.logo(210), (60, 60))
    D.chip(d, 60, 440, TEMA, f('s', 'Bold', 26))
    alto = titular(d, 60, 500, f('u', 'ExtraBold', 60), 80, 960)
    d.text((62, 500 + alto + 22), f'{NOMBRE}  ·  {CARGO}', font=f('s', 'Medium', 27), fill=(215, 215, 215))
    BOX_Y = 960
    hv = poner_video(im, d, BOX_Y)
    cierre(d, BOX_Y + hv + 70)
    return im.convert('RGB')


def v1c_cita():
    """Tarjeta de cita: titular centrado entre comillas, firmado por el invitado."""
    im = D.fondo_borroso(W, H)
    d = ImageDraw.Draw(im, 'RGBA')
    lg = D.logo(220)
    im.alpha_composite(lg, ((W - lg.width) // 2, 80))
    fq = f('u', 'Black', 170)
    q = '«'
    d.text(((W - d.textlength(q, font=fq)) / 2, 150), q, font=fq, fill=VERDE)
    alto = titular(d, W / 2, 360, f('u', 'ExtraBold', 58), 80, 920, centrar=True)
    # firma
    y = 360 + alto + 30
    fc = D.foto_circulo(84, aro=4)
    fn, fcg = f('u', 'Bold', 30), f('s', 'Medium', 23)
    ancho = 92 + 22 + max(d.textlength(NOMBRE, font=fn), d.textlength(CARGO, font=fcg))
    x = (W - ancho) / 2
    im.alpha_composite(fc, (int(x), int(y)))
    d.text((x + 114, y + 10), NOMBRE, font=fn, fill=BLANCO)
    d.text((x + 114, y + 54), CARGO, font=fcg, fill=(200, 200, 200))
    BOX_Y = 900
    hv = poner_video(im, d, BOX_Y)
    D.chip(d, 40, BOX_Y + 28, TEMA, f('s', 'Bold', 24))
    cierre(d, BOX_Y + hv + 70)
    return im.convert('RGB')


def v1d_marcador():
    """Titular tipo recorte de diario: cada línea sobre una franja blanca, la clave en verde."""
    im = D.fondo_borroso(W, H)
    d = ImageDraw.Draw(im, 'RGBA')
    im.alpha_composite(D.logo(230), ((W - 230) // 2, 80))
    D.chip(d, 70, 220, TEMA, f('s', 'Bold', 28), fondo=NEGRO, color=VERDE, radio=6)
    fnt = f('u', 'ExtraBold', 58)
    lineas, esp = armar(d, fnt, 900)
    asc, desc = fnt.getmetrics()
    y = 300
    for l in lineas:
        ancho = sum(a for *_, a in l) + esp * (len(l) - 1)
        d.rectangle([60, y, 60 + ancho + 36, y + asc + desc + 12], fill=BLANCO)
        cx = 78
        for pal, verde, a in l:
            if verde:
                d.rectangle([cx - 8, y, cx + a + 8, y + asc + desc + 12], fill=VERDE)
            d.text((cx, y + 8), pal, font=fnt, fill=NEGRO)
            cx += a + esp
        y += asc + desc + 24
    BOX_Y = 860
    hv = poner_video(im, d, BOX_Y)
    insignia(im, d, 60, BOX_Y - 92)
    cierre(d, BOX_Y + hv + 70)
    return im.convert('RGB')


def v1e_titular_abajo():
    """El video arriba y el titular grande debajo; el invitado presentado en la cabecera."""
    im = D.fondo_borroso(W, H)
    d = ImageDraw.Draw(im, 'RGBA')
    im.alpha_composite(D.logo(210), ((W - 210) // 2, 70))
    insignia(im, d, 60, 170)
    BOX_Y = 400
    hv = poner_video(im, d, BOX_Y)
    D.subtitulo(d, W / 2, BOX_Y + hv + 50, f('s', 'Bold', 50), 940, 'caja')
    y = BOX_Y + hv + 250
    d.rectangle([70, y, 76, y + 330], fill=VERDE)
    D.chip(d, 100, y, TEMA, f('s', 'Bold', 26))
    titular(d, 100, y + 70, f('u', 'ExtraBold', 60), 82, 900)
    D.onda(d, 120, W - 120, 1810, 60, n=40)
    return im.convert('RGB')


def main():
    piezas = [('V1a-bloque-verde', v1a_bloque_verde), ('V1b-foto-grande', v1b_foto_grande),
              ('V1c-cita', v1c_cita), ('V1d-marcador', v1d_marcador), ('V1e-titular-abajo', v1e_titular_abajo)]
    ims = [('V1-original', Image.open(os.path.join(D.AQUI, 'salida', 'V1-titular.png')))]
    for nombre, fn in piezas:
        im = fn()
        im.save(os.path.join(D.AQUI, 'salida', nombre + '.png'))
        ims.append((nombre, im))
        print('ok', nombre)
    alto = 820
    ancho_c = int(1080 * alto / 1920)
    cols = 3
    hoja = Image.new('RGB', (40 + cols * (ancho_c + 40), 2 * (alto + 90) + 40), (24, 24, 24))
    dh = ImageDraw.Draw(hoja)
    for k, (nombre, im) in enumerate(ims):
        x = 40 + (k % cols) * (ancho_c + 40)
        y = 40 + (k // cols) * (alto + 90)
        hoja.paste(im.resize((ancho_c, alto), Image.LANCZOS), (x, y))
        dh.text((x, y + alto + 10), nombre, font=f('s', 'Bold', 26), fill=VERDE)
    hoja.save(os.path.join(D.AQUI, 'salida', 'comparativa-v1.png'))
    print('ok comparativa-v1')


if __name__ == '__main__':
    main()
