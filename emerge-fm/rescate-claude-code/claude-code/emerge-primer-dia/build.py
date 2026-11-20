# Reel vertical «Gracias por el primer día» — Emerge FM 105.5
# Une 5 grabaciones de pantalla de la transmisión (sin su audio), cada una a ancho
# completo para que los GC se lean, sobre fondo desenfocado del mismo clip.
#   python build.py                 -> salida/emerge-primer-dia-9x16.mp4
#   python build.py --fotos 1,5,20  -> revision/foto_<t>.png (cuadros sueltos)
import os, sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
FFMPEG = r'C:\Program Files\Shutter Encoder\app\Library\ffmpeg.exe'
EFM = r'C:\Users\farid\Desktop\EMERGE FM'
F_UNB = os.path.join(EFM, 'Fuentes', 'Unbounded', 'static', 'Unbounded-{}.ttf')
F_SG = os.path.join(EFM, 'Fuentes', 'Space_Grotesk', 'static', 'SpaceGrotesk-{}.ttf')
LOGO_V = os.path.join(EFM, 'LOGO', 'Logo 105.5', 'PNG', 'emerge-fm-105.5-vertical-color-transparente.png')
LOGO_H = os.path.join(EFM, 'LOGO', 'Logo 105.5', 'PNG', 'emerge-fm-105.5-horizontal-color-transparente.png')

W, H, FPS = 1080, 1920, 30
CROP = 'crop=2080:1170:226:0'          # el 16:9 dentro de la grabación del iPhone
BOX_Y, BOX_H = 640, 608                 # clip a 1080×608
VERDE = (0, 230, 171)

# (archivo, inicio en la fuente, programa, conductor, color de acento)
CLIPS = [
    ('clip1.mov', 0.5, 'El primer «hola»', 'Farid Zerené · Director', VERDE),
    ('clip4.mov', 1.0, 'Emerge tu mañana', 'con Gabriel Figueroa', (255, 107, 53)),
    ('clip2.mp4', 2.0, 'La Ciudad de la Furia', 'con Kaco López', (232, 50, 43)),
    ('clip3.mov', 1.0, 'Viaje sin Rumbo', 'con Valentina Sepúlveda', (123, 140, 255)),
    ('clip5.mp4', 3.0, 'Emerge Noticias', 'con Roberto Rojas', VERDE),
]
T_INTRO, T_CLIP, T_OUTRO = 3.2, 4.6, 4.6
T_TOTAL = T_INTRO + T_CLIP * len(CLIPS) + T_OUTRO
N = int(round(T_TOTAL * FPS))


def fuente(familia, peso, tam):
    ruta = (F_UNB if familia == 'u' else F_SG).format(peso)
    if not os.path.exists(ruta):  # algunas carpetas no traen /static
        ruta = ruta.replace(os.sep + 'static', '')
    return ImageFont.truetype(ruta, tam)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):  # easeOutCubic
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


# ---------- capas de texto pre-renderizadas ----------
def capa_texto(txt, fnt, color, espaciado=0):
    """RGBA ajustada al texto (con espaciado de letras opcional)."""
    tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    if espaciado:
        anchos = [tmp.textlength(c, font=fnt) for c in txt]
        ancho = int(sum(anchos) + espaciado * (len(txt) - 1)) + 4
    else:
        ancho = int(tmp.textlength(txt, font=fnt)) + 4
    asc, desc = fnt.getmetrics()
    im = Image.new('RGBA', (ancho, asc + desc + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if espaciado:
        x = 0
        for c, a in zip(txt, anchos):
            d.text((x, 0), c, font=fnt, fill=color)
            x += a + espaciado
    else:
        d.text((0, 0), txt, font=fnt, fill=color)
    return im


def chip(txt, fnt, fondo, color, padx=22, pady=12, espaciado=4):
    t = capa_texto(txt, fnt, color, espaciado)
    asc, _ = fnt.getmetrics()
    bbox = t.getbbox()
    alto_txt = bbox[3] - bbox[1]
    im = Image.new('RGBA', (t.width + padx * 2, alto_txt + pady * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=im.height // 2, fill=fondo)
    im.alpha_composite(t, (padx, pady - bbox[1]))
    return im


def con_alpha(im, a):
    if a >= 1:
        return im
    im = im.copy()
    al = im.getchannel('A').point(lambda v: int(v * a))
    im.putalpha(al)
    return im


def pegar(base, capa, x, y, a=1.0):
    if a <= 0.003:
        return
    capa = con_alpha(capa, a)
    x, y = int(round(x)), int(round(y))
    # recortar si se sale del lienzo
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(capa.width, W - x), min(capa.height, H - y)
    if x1 <= x0 or y1 <= y0:
        return
    base.alpha_composite(capa.crop((x0, y0, x1, y1)), (x + x0, y + y0))


def centro_x(capa):
    return (W - capa.width) / 2


# Textos fijos
f_chip = fuente('s', 'Bold', 30)
CHIP_DIA = chip('DÍA 1 · LUNES 9 NOV', f_chip, VERDE, (0, 0, 0))
GRACIAS = capa_texto('¡GRACIAS!', fuente('u', 'Black', 112), (255, 255, 255))
SUB1 = capa_texto('por acompañarnos en nuestro', fuente('s', 'Medium', 40), (235, 235, 235))
SUB2 = capa_texto('primer día al aire', fuente('s', 'Medium', 40), (235, 235, 235))

f_prog = fuente('u', 'ExtraBold', 58)
f_cond = fuente('s', 'Medium', 38)
PROG = [capa_texto(c[2], f_prog, (255, 255, 255)) for c in CLIPS]
COND = [capa_texto(c[3], f_cond, (210, 210, 210)) for c in CLIPS]

# intro
I_FECHA = capa_texto('LUNES 9 DE NOVIEMBRE', fuente('s', 'Bold', 38), VERDE, espaciado=8)
I_DIA = capa_texto('DÍA 1', fuente('u', 'Black', 250), (255, 255, 255))
I_L1 = capa_texto('Así sonó y se vio', fuente('s', 'Medium', 52), (235, 235, 235))
I_L2 = capa_texto('nuestro primer día al aire', fuente('s', 'Medium', 52), (235, 235, 235))

# cierre
O_GR = capa_texto('GRACIAS', fuente('u', 'Black', 150), (255, 255, 255))
O_L1 = capa_texto('por ser parte de', fuente('s', 'Medium', 50), (235, 235, 235))
O_L2 = capa_texto('nuestro primer día', fuente('s', 'Medium', 50), (235, 235, 235))
O_EMP = capa_texto('Esto recién empieza.', fuente('u', 'ExtraBold', 60), VERDE)
O_ESL = capa_texto('LO QUE SUENA, EMERGE.', fuente('s', 'Bold', 34), (200, 200, 200), espaciado=6)

_lv = Image.open(LOGO_V).convert('RGBA')
_lv = _lv.crop(_lv.getbbox())  # sin el margen transparente del PNG
LOGO_VERT = _lv.resize((300, int(_lv.height * 300 / _lv.width)), Image.LANCZOS)
_lh = Image.open(LOGO_H).convert('RGBA')
LOGO_HOR = _lh.resize((300, int(_lh.height * 300 / _lh.width)), Image.LANCZOS)


# ---------- lectura de clips ----------
def leer_clip(nombre, inicio, dur):
    ruta = os.path.join(AQUI, 'fuentes', nombre)
    cmd = [FFMPEG, '-v', 'error', '-ss', str(inicio), '-t', str(dur + 0.2), '-i', ruta, '-an',
           '-vf', f'{CROP},fps={FPS},scale=1080:{BOX_H}:flags=lanczos,format=rgb24',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    tam = 1080 * BOX_H * 3
    n = len(raw) // tam
    return [np.frombuffer(raw[i * tam:(i + 1) * tam], np.uint8).reshape(BOX_H, 1080, 3) for i in range(n)]


def fondo_de(frame, oscuro=0.42):
    """Fondo 9:16 desenfocado a partir del cuadro 16:9."""
    im = Image.fromarray(frame)
    ancho = int(BOX_H * W / H)  # 342
    x = (1080 - ancho) // 2
    im = im.crop((x, 0, x + ancho, BOX_H)).resize((54, 96), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BICUBIC)
    a = np.asarray(im).astype(np.float32) * oscuro
    return a


VIÑETA = None


def vineta():
    global VIÑETA
    if VIÑETA is None:
        yy = np.linspace(-1, 1, H)[:, None]
        xx = np.linspace(-1, 1, W)[None, :]
        v = 1 - 0.55 * np.clip((xx ** 2 * 0.6 + yy ** 2), 0, 1)
        VIÑETA = v[..., None].astype(np.float32)
    return VIÑETA


def anillos(t, alpha):
    """Anillos de señal verdes de fondo (intro y cierre)."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W / 2, H * 0.47
    for k in range(7):
        r = ((t * 140 + k * 170) % 1190) + 60
        a = int(alpha * 70 * (1 - r / 1250))
        if a > 0:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=VERDE + (a,), width=6)
    return im


# ---------- composición ----------
def cuadro(t, clips):
    lienzo = np.zeros((H, W, 3), np.float32)
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fin_clips = T_INTRO + T_CLIP * len(CLIPS)

    if t < T_INTRO:
        _intro(t, capa)
        base = Image.new('RGBA', (W, H), (8, 8, 8, 255))
        base.alpha_composite(anillos(t, 1.0))
        base.alpha_composite(capa)
        return base.convert('RGB')

    # índice de clip y tiempo local
    if t < fin_clips:
        i = int((t - T_INTRO) // T_CLIP)
        tl = t - T_INTRO - i * T_CLIP
    else:
        i = len(CLIPS) - 1
        tl = T_CLIP + (t - fin_clips)
    frames = clips[i]
    fr = frames[min(int(tl * FPS), len(frames) - 1)]

    # fondo desenfocado
    lienzo[:] = fondo_de(fr) * vineta()
    # clip a ancho completo
    lienzo[BOX_Y:BOX_Y + BOX_H] = fr
    base = Image.fromarray(lienzo.astype(np.uint8)).convert('RGBA')

    acento = CLIPS[i][4]
    d = ImageDraw.Draw(capa)
    # filetes de acento arriba y abajo del clip
    d.rectangle([0, BOX_Y - 8, W, BOX_Y - 1], fill=acento + (255,))
    d.rectangle([0, BOX_Y + BOX_H, W, BOX_Y + BOX_H + 7], fill=acento + (255,))

    # cabecera fija
    tc = t - T_INTRO
    pegar(capa, LOGO_HOR, centro_x(LOGO_HOR), 150, ease(tc / 0.5))
    pegar(capa, CHIP_DIA, centro_x(CHIP_DIA), 300 + 30 * (1 - ease(tc / 0.5)), ease(tc / 0.5))
    e = ease((tc - 0.1) / 0.6)
    pegar(capa, GRACIAS, centro_x(GRACIAS), 372 + 40 * (1 - e), e)
    e2 = ease((tc - 0.3) / 0.6)
    pegar(capa, SUB1, centro_x(SUB1), 512 + 20 * (1 - e2), e2)
    pegar(capa, SUB2, centro_x(SUB2), 560 + 20 * (1 - e2), e2)

    # ficha del programa (entra al inicio del clip, sale al final)
    if t < fin_clips:
        ent = ease((tl - 0.25) / 0.45)
        sal = 1 - ease_io((tl - (T_CLIP - 0.35)) / 0.3) if i < len(CLIPS) - 1 else 1
        a = min(ent, sal)
        y = BOX_Y + BOX_H + 60 + 50 * (1 - ent)
        # barra de color a la izquierda del nombre
        x0 = 70
        barra = Image.new('RGBA', (12, 150), acento + (255,))
        pegar(capa, barra, x0, y + 4, a)
        pegar(capa, PROG[i], x0 + 40, y, a)
        pegar(capa, COND[i], x0 + 42, y + 88, a)
        # contador de programas
        for k in range(len(CLIPS)):
            col = acento + (255,) if k == i else (255, 255, 255, 90)
            cx = W / 2 + (k - 2) * 46
            d.ellipse([cx - 9, 1530 - 9, cx + 9, 1530 + 9], fill=col)

    base.alpha_composite(capa)

    # barrido de transición entre clips (banda diagonal verde)
    for k in range(1, len(CLIPS)):
        tcorte = T_INTRO + k * T_CLIP
        _barrido(base, (t - tcorte + 0.22) / 0.44, CLIPS[k][4])

    # cierre: oscurece y monta textos
    if t >= fin_clips - 0.3:
        to = t - fin_clips
        _cierre(base, to)

    return base.convert('RGB')


def _barrido(base, p, color):
    if p <= 0 or p >= 1:
        return
    p = ease_io(p)
    d = ImageDraw.Draw(base)
    ancho = 520
    x = -ancho - 300 + p * (W + ancho + 600)
    y0, y1 = BOX_Y - 8, BOX_Y + BOX_H + 8
    sesgo = 160
    d.polygon([(x, y1), (x + sesgo, y0), (x + sesgo + ancho, y0), (x + ancho, y1)], fill=color + (255,))
    d.polygon([(x - 70, y1), (x - 70 + sesgo, y0), (x - 40 + sesgo, y0), (x - 40, y1)], fill=(255, 255, 255, 255))


def _intro(t, capa):
    e0 = ease(t / 0.5)
    pegar(capa, I_FECHA, centro_x(I_FECHA), 600 + 30 * (1 - e0), e0)
    e1 = ease((t - 0.25) / 0.7)
    s = 0.7 + 0.3 * e1
    if e1 > 0:
        dia = I_DIA.resize((int(I_DIA.width * s), int(I_DIA.height * s)), Image.LANCZOS)
        pegar(capa, dia, centro_x(dia), 720 + (I_DIA.height - dia.height) / 2, e1)
    e2 = ease((t - 1.1) / 0.6)
    pegar(capa, I_L1, centro_x(I_L1), 1090 + 30 * (1 - e2), e2)
    e3 = ease((t - 1.35) / 0.6)
    pegar(capa, I_L2, centro_x(I_L2), 1160 + 30 * (1 - e3), e3)
    # salida: todo sube y se apaga en los últimos 0.35 s
    sal = clamp((t - (T_INTRO - 0.35)) / 0.35)
    if sal > 0:
        capa.putalpha(capa.getchannel('A').point(lambda v: int(v * (1 - sal))))


def _cierre(base, to):
    # velo negro que cubre el último clip
    k = ease_io((to + 0.3) / 0.7)
    velo = Image.new('RGBA', (W, H), (8, 8, 8, int(255 * k)))
    base.alpha_composite(velo)
    if k > 0.5:
        base.alpha_composite(anillos(to, (k - 0.5) * 2))
    e = ease((to - 0.2) / 0.6)
    s = 0.85 + 0.15 * e
    if e > 0:
        gr = O_GR.resize((int(O_GR.width * s), int(O_GR.height * s)), Image.LANCZOS)
        pegar(base, gr, centro_x(gr), 470 + (O_GR.height - gr.height) / 2, e)
    e2 = ease((to - 0.6) / 0.6)
    pegar(base, O_L1, centro_x(O_L1), 690 + 25 * (1 - e2), e2)
    pegar(base, O_L2, centro_x(O_L2), 752 + 25 * (1 - e2), e2)
    e3 = ease((to - 1.3) / 0.6)
    pegar(base, O_EMP, centro_x(O_EMP), 880 + 25 * (1 - e3), e3)
    e4 = ease((to - 2.0) / 0.7)
    pegar(base, LOGO_VERT, centro_x(LOGO_VERT), 1050 + 30 * (1 - e4), e4)
    e5 = ease((to - 2.5) / 0.6)
    pegar(base, O_ESL, centro_x(O_ESL), 1060 + LOGO_VERT.height + 50, e5)


def cargar_clips():
    out = []
    for nombre, ini, *_ in CLIPS:
        dur = T_CLIP + (T_OUTRO if nombre == CLIPS[-1][0] else 0)
        fr = leer_clip(nombre, ini, dur)
        print(f'  {nombre}: {len(fr)} cuadros', flush=True)
        out.append(fr)
    return out


def main():
    os.makedirs(os.path.join(AQUI, 'salida'), exist_ok=True)
    os.makedirs(os.path.join(AQUI, 'revision'), exist_ok=True)
    print('Leyendo clips…', flush=True)
    clips = cargar_clips()

    if '--fotos' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--fotos') + 1].split(',')]
        for t in ts:
            cuadro(t, clips).save(os.path.join(AQUI, 'revision', f'foto_{t:05.2f}.png'))
        print('Fotos listas.')
        return

    salida = os.path.join(AQUI, 'salida', 'emerge-primer-dia-9x16.mp4')
    enc = subprocess.Popen([FFMPEG, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
                            '-profile:v', 'high', '-movflags', '+faststart', salida], stdin=subprocess.PIPE)
    for n in range(N):
        enc.stdin.write(cuadro(n / FPS, clips).tobytes())
        if n % 60 == 0:
            print(f'  {n}/{N}', flush=True)
    enc.stdin.close()
    enc.wait()
    print('Listo:', salida, f'({T_TOTAL:.1f} s)')


if __name__ == '__main__':
    main()
