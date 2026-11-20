# Reel vertical: Gabriel Figueroa da en Emerge tu mañana la noticia del estudio Ipsos–AMMPE World
# («la radio sigue siendo el medio más confiable de Chile»). Paleta de Emerge tu mañana
# (violeta, naranja, ámbar) en vez del verde de Emerge Noticias.
# Arriba: la noticia (titular + datos que se animan cuando Gabriel los dice). Al medio: la
# transmisión con inserts breves de radio. Abajo: subtítulos en seco y onda de audio.
#   python build.py                 -> salida/radio-medio-mas-confiable-9x16.mp4
#   python build.py --fotos 1,20    -> revision/foto_<t>.png
import os, sys, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.io import wavfile

AQUI = os.path.dirname(os.path.abspath(__file__))
FFMPEG = r'C:\Program Files\Shutter Encoder\app\Library\ffmpeg.exe'
EFM = r'C:\Users\farid\Desktop\EMERGE FM'
F_UNB = os.path.join(EFM, 'Fuentes', 'Unbounded', 'static', 'Unbounded-{}.ttf')
F_SG = os.path.join(EFM, 'Fuentes', 'Space_Grotesk', 'static', 'SpaceGrotesk-{}.ttf')
LOGO_H = os.path.join(EFM, 'LOGO', 'Logo 105.5', 'PNG', 'emerge-fm-105.5-horizontal-color-transparente.png')

W, H, FPS = 1080, 1920, 30
VIOLETA = (123, 97, 255)
NARANJA = (255, 107, 53)
AMBAR = (255, 201, 60)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Tramo de la transmisión (segundos de la fuente)
INI, FIN = 6.45, 71.42   # «Oye, y tenemos una noticia…» → «…confiable todos los días.»
CROP = 'crop=690:384:73:0'  # imagen del programa dentro de la grabación de pantalla

# Inserts: (archivo, segundo del insert donde parte, tiempo del reel, duración)
INSERTS = [
    ('insert1.mp4', 2.0, 3.9, 2.4),    # consola — «lo que hablábamos el lunes en nuestro primer programa»
    ('insert3.mp4', 1.5, 15.0, 2.6),   # dial — «la radio sigue siendo el medio más confiable»
    ('insert4.mp4', 4.5, 23.4, 2.6),   # estudio — «las noticias de la radio son muy creíbles»
    ('insert2.mp4', 26.0, 40.2, 2.6),  # periodista al micrófono — «las y los periodistas de radio»
    ('insert5.mp4', 3.0, 58.7, 2.6),   # radio antigua — «ese espacio cercano y confiable»
]

# Diseño (y en px)
Y_LOGO = 78
BOX_Y, BOX_H = 850, 600
Y_SUB = BOX_Y + BOX_H + 56
Y_ONDA, H_ONDA = 1800, 64

TITULAR = 'La radio sigue siendo el medio [más confiable] de Chile'
FUENTE = 'Fuente: Claves Ipsos N°56 · Ipsos y AMMPE World · nov. 2026'
# barras: (etiqueta, valor, tiempo del reel en que Gabriel lo dice)
BARRAS = [('Radio', 52, 22.9), ('Diarios', 41, 29.3), ('TV abierta', 35, 33.4)]
T_78 = 47.6  # «porque el 78% de las personas…»

EDITS = [(['primer...'], ['primer', 'programa.']), (['Chile.', 'Chile.'], ['Chile.'])]
CORTAR_ANTES = [['la', 'radio', 'sigue']]
UNIR = []


def fuente(f, peso, tam):
    return ImageFont.truetype((F_UNB if f == 'u' else F_SG).format(peso), tam)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def texto(txt, fnt, color, esp=0):
    tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    anchos = [tmp.textlength(c, font=fnt) for c in txt] if esp else None
    ancho = int(sum(anchos) + esp * (len(txt) - 1)) + 4 if esp else int(tmp.textlength(txt, font=fnt)) + 4
    asc, desc = fnt.getmetrics()
    im = Image.new('RGBA', (ancho, asc + desc + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if esp:
        x = 0
        for c, a in zip(txt, anchos):
            d.text((x, 0), c, font=fnt, fill=color)
            x += a + esp
    else:
        d.text((0, 0), txt, font=fnt, fill=color)
    return im


def chip(txt, fnt, fondo, color, padx=20, pady=11, esp=4):
    t = texto(txt, fnt, color, esp)
    bb = t.getbbox()
    im = Image.new('RGBA', (t.width + padx * 2, bb[3] - bb[1] + pady * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=im.height // 2, fill=fondo)
    im.alpha_composite(t, (padx, pady - bb[1]))
    return im


def con_alpha(im, a):
    if a >= 1:
        return im
    im = im.copy()
    im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    return im


def pegar(base, capa, x, y, a=1.0):
    if a > 0.003:
        base.alpha_composite(con_alpha(capa, a), (int(round(x)), int(round(y))))


# ---------- audio ----------
def preparar_audio():
    wav = os.path.join(AQUI, 'salida', '_audio.wav')
    subprocess.run([FFMPEG, '-y', '-v', 'error', '-i', os.path.join(AQUI, 'fuentes', 'transmision.mp4'),
                    '-af', f'atrim={INI}:{FIN},asetpts=PTS-STARTPTS,aresample=48000,highpass=f=70,'
                           'afade=t=in:d=0.08,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000',
                    '-ac', '2', '-c:a', 'pcm_s16le', wav], check=True)
    sr, x = wavfile.read(wav)
    m = x.astype(np.float32).mean(1) / 32768
    paso = sr // 120
    n = len(m) // paso
    env = np.sqrt((m[:n * paso].reshape(n, paso) ** 2).mean(1))
    env = env / (np.percentile(env, 98) + 1e-9)
    return wav, len(m) / sr, np.clip(env, 0, 1.2)


# ---------- pista de video del recuadro (transmisión + inserts) ----------
def pista_video(dur):
    """Arma con ffmpeg el video del recuadro 1080×600: transmisión con los inserts encima."""
    out = os.path.join(AQUI, 'salida', '_recuadro.mp4')
    ins = ['-ss', str(INI), '-t', str(dur), '-i', os.path.join(AQUI, 'fuentes', 'transmision.mp4')]
    filt = [f'[0:v]{CROP},scale={W}:{BOX_H}:flags=lanczos,setsar=1,fps={FPS},format=yuv420p[b0]']
    ult = 'b0'
    for k, (f, a, t, d) in enumerate(INSERTS, start=1):
        ins += ['-ss', str(a), '-t', str(d), '-i', os.path.join(AQUI, 'fuentes', f)]
        filt.append(f'[{k}:v]scale={W}:{BOX_H}:force_original_aspect_ratio=increase:flags=lanczos,'
                    f'crop={W}:{BOX_H},setsar=1,fps={FPS},format=yuva420p,'
                    f'fade=t=in:st=0:d=0.15:alpha=1,fade=t=out:st={d - 0.15}:d=0.15:alpha=1,'
                    f'setpts=PTS-STARTPTS+{t}/TB[i{k}]')
        filt.append(f'[{ult}][i{k}]overlay=eof_action=pass:enable=\'between(t,{t},{t + d})\'[b{k}]')
        ult = f'b{k}'
    subprocess.run([FFMPEG, '-y', '-v', 'error', *ins, '-filter_complex', ';'.join(filt),
                    '-map', f'[{ult}]', '-an', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast',
                    '-t', str(dur), out], check=True)
    return out


class Lector:
    def __init__(self, ruta):
        self.proc = subprocess.Popen([FFMPEG, '-v', 'error', '-i', ruta, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                     stdout=subprocess.PIPE)
        self.n = 0
        self.ultimo = np.zeros((BOX_H, W, 3), np.uint8)

    def cuadro(self, idx):
        tam = W * BOX_H * 3
        while self.n <= idx:
            raw = self.proc.stdout.read(tam)
            if len(raw) < tam:
                break
            self.ultimo = np.frombuffer(raw, np.uint8).reshape(BOX_H, W, 3)
            self.n += 1
        return self.ultimo


# ---------- subtítulos ----------
def palabras():
    d = json.load(open(os.path.join(AQUI, 'transcripcion.json'), encoding='utf-8'))
    out = [dict(p=w['p'].strip(), ini=max(w['ini'] - INI, 0.02), fin=w['fin'] - INI)
           for s in d['audio1'] for w in s['palabras'] if INI - 0.15 <= w['ini'] and w['fin'] <= FIN + 0.15]
    for viejo, nuevo in EDITS:
        txt = [w['p'] for w in out]
        for i in range(len(txt) - len(viejo) + 1):
            if txt[i:i + len(viejo)] == viejo:
                ini, fin = out[i]['ini'], out[i + len(viejo) - 1]['fin']
                paso = (fin - ini) / len(nuevo)
                out[i:i + len(viejo)] = [dict(p=p, ini=ini + j * paso, fin=ini + (j + 1) * paso)
                                         for j, p in enumerate(nuevo)]
                break
    for i, w in enumerate(out):
        sig = out[i + 1]['ini'] if i + 1 < len(out) else w['fin']
        w['fin'] = min(max(w['fin'], sig), w['ini'] + 0.9)
    return out


F_SUB = fuente('s', 'Bold', 54)
MAX_LINEA = 900
DEBIL = {'a', 'al', 'de', 'del', 'el', 'la', 'los', 'las', 'un', 'una', 'con', 'en', 'se', 'es', 'y', 'que',
         'por', 'para', 'su', 'sus', 'lo', 'le', 'nos', 'no', 'va', 'muy', 'más', 'san', 'ya', 'este', 'esta'}


def bloques(ws):
    tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    esp = tmp.textlength(' ', font=F_SUB)
    txt = [w['p'].lower() for w in ws]
    pegadas = set()
    for u in UNIR:
        for i in range(len(txt) - len(u) + 1):
            if txt[i:i + len(u)] == u:
                pegadas.update(range(i, i + len(u) - 1))
    res, actual, lineas, ancho = [], [], 1, 0
    for i, w in enumerate(ws):
        a = tmp.textlength(w['p'], font=F_SUB)
        if actual and ancho + esp + a > MAX_LINEA:
            if lineas == 2:
                res.append(actual); actual, lineas, ancho = [], 1, 0
            else:
                lineas, ancho = 2, 0
        forzar = any(txt[i:i + len(c)] == c for c in CORTAR_ANTES)
        if forzar and actual:
            res.append(actual); actual, lineas, ancho = [], 1, 0
        actual.append(w)
        ancho += (esp if ancho else 0) + a
        if i in pegadas:
            continue
        pausa = i + 1 < len(ws) and ws[i + 1]['ini'] - w['fin'] > 0.45 and len(actual) >= 2
        cola = any(ws[j]['p'][-1] in '.?!,' for j in range(i + 1, min(i + 3, len(ws))))
        largo = (len(actual) >= 7 and w['p'].lower() not in DEBIL and not (cola and len(actual) < 9)) \
            or (len(actual) >= 6 and i + 1 < len(ws) and ws[i + 1]['p'] in ('que', 'y', 'porque', 'donde', 'para', 'mientras'))
        coma = w['p'][-1] == ',' and len(actual) >= 3 and not (i + 1 < len(ws) and ws[i + 1]['p'][-1] in '.?!')
        if w['p'][-1] in '.?!' or coma or pausa or largo:
            res.append(actual); actual, lineas, ancho = [], 1, 0
    if actual:
        res.append(actual)
    out = []
    for k, b in enumerate(res):
        fin = res[k + 1][0]['ini'] if k + 1 < len(res) else b[-1]['fin'] + 0.6
        out.append(dict(ini=b[0]['ini'], fin=min(fin, b[-1]['fin'] + 1.2), ws=b))
    return out


def dibujar_sub(capa, b, t):
    tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    esp = tmp.textlength(' ', font=F_SUB)
    lin, act, ancho = [], [], 0
    for w in b['ws']:
        a = tmp.textlength(w['p'], font=F_SUB)
        if act and ancho + esp + a > MAX_LINEA:
            lin.append(act); act, ancho = [], 0
        act.append((w, a))
        ancho += (esp if ancho else 0) + a
    lin.append(act)
    d = ImageDraw.Draw(capa)
    for j, l in enumerate(lin):
        ancho = sum(a for _, a in l) + esp * (len(l) - 1)
        x = (W - ancho) / 2
        y = Y_SUB + j * 70
        for w, a in l:
            activa = w['ini'] <= t < w['fin']
            if activa:
                d.rounded_rectangle([x - 10, y + 2, x + a + 10, y + 66], radius=12, fill=AMBAR + (255,))
                col = NEGRO
            else:
                d.text((x + 2, y + 3), w['p'], font=F_SUB, fill=(0, 0, 0, 170))
                col = BLANCO if t >= w['ini'] else (185, 180, 200)
            d.text((x, y), w['p'], font=F_SUB, fill=col + (255,))
            x += a + esp


# ---------- piezas fijas ----------
_lh = Image.open(LOGO_H).convert('RGBA')
_lh = _lh.crop(_lh.getbbox())
LOGO = _lh.resize((240, int(_lh.height * 240 / _lh.width)), Image.LANCZOS)
CHIP_PROG = chip('EMERGE TU MAÑANA', fuente('s', 'Bold', 26), NARANJA, NEGRO)
CHIP_EST = chip('ESTUDIO IPSOS', fuente('s', 'Bold', 26), VIOLETA, BLANCO)
F_TIT = fuente('u', 'ExtraBold', 64)


def capa_titular():
    im = Image.new('RGBA', (W, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    esp = d.textlength(' ', font=F_TIT)
    x, y, verde = 0, 0, False
    for k, pal in enumerate(TITULAR.split(' ')):
        if pal.startswith('['):
            verde, pal = True, pal[1:]
        cierra = ']' in pal
        pal = pal.replace(']', '')
        a = d.textlength(pal, font=F_TIT)
        if k and x + esp + a > 960:
            x, y = 0, y + 82
        elif k:
            x += esp
        d.text((x, y), pal, font=F_TIT, fill=AMBAR if verde else BLANCO)
        x += a
        if cierra:
            verde = False
    return im.crop((0, 0, W, y + 90))


TITULAR_IM = capa_titular()
F_ETQ = fuente('s', 'SemiBold', 32)
F_VAL = fuente('u', 'Bold', 36)
F_CAP = fuente('s', 'Medium', 27)
F_FUENTE = fuente('s', 'Medium', 22)
F_78 = fuente('u', 'Black', 150)


def fondo(fr):
    im = Image.fromarray(fr)
    ancho = int(BOX_H * W / H)
    x = (W - ancho) // 2
    im = im.crop((x, 0, x + ancho, BOX_H)).resize((54, 96), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BICUBIC)
    a = np.asarray(im).astype(np.float32) * 0.22
    # tinte violeta oscuro de Emerge tu mañana
    a = a + np.array([26, 16, 52], np.float32) * 0.9
    yy = np.linspace(-1, 1, H)[:, None, None]
    return a * (1 - 0.35 * np.clip(yy ** 2, 0, 1))


def panel_datos(capa, t):
    """Fase 1: barras de credibilidad (cada una se destaca cuando Gabriel la dice). Fase 2: el 78%."""
    d = ImageDraw.Draw(capa)
    y0 = 560
    f2 = ease((t - T_78) / 0.35)
    a1 = 1 - f2
    if a1 > 0.01:
        aa = int(255 * a1)
        d.text((60, y0 - 4), 'Consideran muy creíbles las noticias de…', font=F_CAP, fill=(200, 195, 225, aa))
        for j, (et, val, tv) in enumerate(BARRAS):
            y = y0 + 52 + j * 62
            crece = ease((t - 0.4 - j * 0.15) / 0.8)
            foco = clamp(1 - abs(t - tv - 0.9) / 1.6) if t >= tv - 0.3 else 0
            col = AMBAR if j == 0 else VIOLETA
            d.text((60, y + 6), et, font=F_ETQ, fill=BLANCO + (aa,))
            x0, x1 = 270, 270 + 620 * val / 60 * crece
            d.rounded_rectangle([x0, y + 8, 270 + 620, y + 44], radius=18, fill=(255, 255, 255, int(22 * a1)))
            if crece > 0.02:
                d.rounded_rectangle([x0, y + 8 - 4 * foco, x1, y + 44 + 4 * foco], radius=18, fill=col + (aa,))
            txt = f'{val}%' if j < 2 else f'~{val}%'
            d.text((x1 + 16, y + 2), txt, font=F_VAL, fill=(AMBAR if foco > 0.2 else BLANCO) + (aa,))
    if f2 > 0.01:
        aa = int(255 * f2)
        d.text((52, y0 - 30 + 16 * (1 - f2)), '78%', font=F_78, fill=AMBAR + (aa,))
        lineas = ['cree que las redes sociales hacen', 'más difícil distinguir una noticia', 'real de una falsa']
        for j, l in enumerate(lineas):
            d.text((510, y0 + 4 + j * 44 + 16 * (1 - f2)), l, font=fuente('s', 'SemiBold', 33), fill=BLANCO + (aa,))
    d.text((60, 790), FUENTE, font=F_FUENTE, fill=(165, 160, 190, 255))


def onda(capa, t, env, activo):
    d = ImageDraw.Draw(capa)
    n, gap = 40, 8
    x0, x1 = 120, W - 120
    bw = (x1 - x0 - gap * (n - 1)) / n
    cy = Y_ONDA + H_ONDA / 2
    i_t = int(t * 120)
    for k in range(n):
        j = i_t - (n - 1 - k) * 3
        v = env[j] if 0 <= j < len(env) else 0
        v = max(0.06, min(1.0, v)) * activo
        h = max(6, v * H_ONDA)
        x = x0 + k * (bw + gap)
        u = k / (n - 1)
        col = tuple(int(NARANJA[c] * (1 - u) + AMBAR[c] * u) for c in range(3))
        d.rounded_rectangle([x, cy - h / 2, x + bw, cy + h / 2], radius=bw / 2, fill=col + (255,))


def componer(t, lector, env, subs, dur):
    fr = lector.cuadro(int(t * FPS))
    lienzo = fondo(fr)
    lienzo[BOX_Y:BOX_Y + BOX_H] = fr
    base = Image.fromarray(lienzo.clip(0, 255).astype(np.uint8)).convert('RGBA')
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    e0 = ease(t / 0.5)
    pegar(capa, LOGO, (W - LOGO.width) / 2, Y_LOGO, e0)
    e1 = ease((t - 0.1) / 0.5)
    pegar(capa, CHIP_PROG, 60, 186, e1)
    pegar(capa, CHIP_EST, 60 + CHIP_PROG.width + 14, 186, e1)
    e2 = ease((t - 0.2) / 0.5)
    pegar(capa, TITULAR_IM, 60 + 30 * (1 - e2), 252, e2)
    panel_datos(capa, t)
    # filetes del recuadro
    d.rectangle([0, BOX_Y - 8, W, BOX_Y - 1], fill=VIOLETA + (255,))
    d.rectangle([0, BOX_Y + BOX_H, W, BOX_Y + BOX_H + 7], fill=VIOLETA + (255,))
    for b in subs:
        if b['ini'] <= t < b['fin']:
            dibujar_sub(capa, b, t)
            break
    onda(capa, t, env, ease(t / 0.4))
    base.alpha_composite(capa)
    fade = min(clamp(t / 0.25), clamp((dur - t) / 0.5))
    if fade < 1:
        base.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - fade)))))
    return base.convert('RGB')


def main():
    os.makedirs(os.path.join(AQUI, 'salida'), exist_ok=True)
    os.makedirs(os.path.join(AQUI, 'revision'), exist_ok=True)
    wav, dur, env = preparar_audio()
    subs = bloques(palabras())
    with open(os.path.join(AQUI, 'revision', 'subtitulos.txt'), 'w', encoding='utf-8') as f:
        for b in subs:
            f.write(f"{b['ini']:6.2f}-{b['fin']:6.2f}  {' '.join(w['p'] for w in b['ws'])}\n")
    print(f'Audio {dur:.2f} s, {len(subs)} subtítulos', flush=True)
    recuadro = pista_video(dur)

    if '--fotos' in sys.argv:
        ts = sorted(float(x) for x in sys.argv[sys.argv.index('--fotos') + 1].split(','))
        lector = Lector(recuadro)
        for t in ts:
            componer(t, lector, env, subs, dur).save(os.path.join(AQUI, 'revision', f'foto_{t:05.2f}.png'))
        print('Fotos listas.')
        return

    salida = os.path.join(AQUI, 'salida', 'radio-medio-mas-confiable-9x16.mp4')
    n = int(dur * FPS)
    enc = subprocess.Popen([FFMPEG, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                            '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-maxrate', '8M', '-bufsize', '16M',
                            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart', salida],
                           stdin=subprocess.PIPE)
    lector = Lector(recuadro)
    for i in range(n):
        enc.stdin.write(componer(i / FPS, lector, env, subs, dur).tobytes())
        if i % 300 == 0:
            print(f'  {i}/{n}', flush=True)
    enc.stdin.close()
    enc.wait()
    print('Listo:', salida, f'({dur:.1f} s)')


if __name__ == '__main__':
    main()
