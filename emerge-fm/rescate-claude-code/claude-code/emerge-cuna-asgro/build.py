# Reel vertical de la cuña de Camilo Jiménez (ASGRO) en Emerge Noticias.
# Arriba: foto de Camilo en un cuadro + nombre/cargo + onda de audio en vivo.
# Al medio: Roberto Rojas (16:9 a ancho completo, GC intacto). Abajo: subtítulos con
# la palabra que suena resaltada. Parte 1 (.mov, 39 s) y luego parte 2 (.mp4, 28 s).
#   python build.py                 -> salida/cuna-asgro-camilo-jimenez-9x16.mp4
#   python build.py --fotos 1,20    -> revision/foto_<t>.png
import os, sys, json, subprocess, math, re
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
CROP = 'crop=2080:1170:226:0'
VERDE = (0, 230, 171)
GRIS = (22, 22, 22)

# Partes en orden: (archivo, inicio, fin) en segundos de la fuente
PARTES = [('parte1.mov', 0.0, 38.92), ('parte2.mp4', 0.0, 27.1)]
XFADE = 0.06  # cruce de audio entre partes

# Diseño (y en px)
Y_LOGO = 92
CARD = (60, 175, 360, 480)        # x, y, ancho, alto de la foto
Y_ONDA, H_ONDA = 700, 110
BOX_Y, BOX_H = 850, 608
Y_SUB = BOX_Y + BOX_H + 54

# Correcciones a la transcripción (secuencias de palabras -> reemplazo)
EDITS = [
    (['combustibles', 'a', 'hacer', 'este', 'tema.'], ['combustibles.']),  # tramo poco claro en el audio
]

NOMBRE = 'Camilo Jiménez'
CARGO = ['Vocero de la Asociación', 'Gremial Rengo O\'Higgins', '(ASGRO)']


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
    """Une las dos partes, normaliza a −14 LUFS y devuelve (ruta wav, duración, envolvente)."""
    wav = os.path.join(AQUI, 'salida', '_audio.wav')
    ins, filt = [], []
    for k, (f, a, z) in enumerate(PARTES):
        ins += ['-i', os.path.join(AQUI, 'fuentes', f)]
        filt.append(f'[{k}:a]atrim={a}:{z},asetpts=PTS-STARTPTS,aresample=48000[a{k}]')
    filt.append(f'[a0][a1]acrossfade=d={XFADE}:c1=tri:c2=tri,highpass=f=70,'
                'loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[out]')
    subprocess.run([FFMPEG, '-y', '-v', 'error', *ins, '-filter_complex', ';'.join(filt),
                    '-map', '[out]', '-ac', '2', '-c:a', 'pcm_s16le', wav], check=True)
    sr, x = wavfile.read(wav)
    m = x.astype(np.float32).mean(1) / 32768
    dur = len(m) / sr
    # envolvente RMS a 120 Hz para la onda
    paso = sr // 120
    n = len(m) // paso
    env = np.sqrt((m[:n * paso].reshape(n, paso) ** 2).mean(1))
    env = env / (np.percentile(env, 98) + 1e-9)
    return wav, dur, np.clip(env, 0, 1.2)


# ---------- subtítulos ----------
def palabras():
    d = json.load(open(os.path.join(AQUI, 'transcripcion.json'), encoding='utf-8'))
    out, off = [], 0.0
    for k, clave in enumerate(('audio1', 'audio2')):
        a, z = PARTES[k][1], PARTES[k][2]
        ws = [dict(p=w['p'].strip(), ini=w['ini'] - a + off, fin=w['fin'] - a + off)
              for s in d[clave] for w in s['palabras'] if a <= w['ini'] < z]
        out += ws
        off += (z - a) - (XFADE if k == 0 else 0)
    # correcciones
    for viejo, nuevo in EDITS:
        txt = [w['p'] for w in out]
        for i in range(len(txt) - len(viejo) + 1):
            if txt[i:i + len(viejo)] == viejo:
                ini, fin = out[i]['ini'], out[i + len(viejo) - 1]['fin']
                rep = [dict(p=p, ini=ini, fin=fin) for p in nuevo]
                out[i:i + len(viejo)] = rep
                break
    # fin de cada palabra = inicio de la siguiente (máx. 0,9 s)
    for i, w in enumerate(out):
        sig = out[i + 1]['ini'] if i + 1 < len(out) else w['fin']
        w['fin'] = min(max(w['fin'], sig), w['ini'] + 0.9)
    return out


F_SUB = fuente('s', 'Bold', 54)
MAX_LINEA = 900


def bloques(ws):
    """Agrupa en bloques de hasta 2 líneas; corta en puntuación o pausas."""
    tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    esp = tmp.textlength(' ', font=F_SUB)
    res, actual, lineas, ancho = [], [], 1, 0
    for i, w in enumerate(ws):
        a = tmp.textlength(w['p'], font=F_SUB)
        if actual and ancho + esp + a > MAX_LINEA:
            if lineas == 2:
                res.append(actual); actual, lineas, ancho = [], 1, 0
            else:
                lineas, ancho = 2, 0
        actual.append(w)
        ancho += (esp if ancho else 0) + a
        pausa = i + 1 < len(ws) and ws[i + 1]['ini'] - w['fin'] > 0.45
        largo = len(actual) >= 7 or (len(actual) >= 5 and i + 1 < len(ws) and ws[i + 1]['p'] in ('que', 'y', 'porque', 'donde', 'para', 'mientras'))
        if w['p'][-1] in '.?!' or (w['p'][-1] == ',' and len(actual) >= 3) or pausa or largo:
            res.append(actual); actual, lineas, ancho = [], 1, 0
    if actual:
        res.append(actual)
    out = []
    for k, b in enumerate(res):
        ini = b[0]['ini']
        fin = res[k + 1][0]['ini'] if k + 1 < len(res) else b[-1]['fin'] + 0.6
        fin = min(fin, b[-1]['fin'] + 1.2)
        out.append(dict(ini=ini, fin=fin, ws=b))
    return out


def lineas_de(b):
    tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    esp = tmp.textlength(' ', font=F_SUB)
    lin, actual, ancho = [], [], 0
    for w in b['ws']:
        a = tmp.textlength(w['p'], font=F_SUB)
        if actual and ancho + esp + a > MAX_LINEA:
            lin.append(actual); actual, ancho = [], 0
        actual.append((w, a))
        ancho += (esp if ancho else 0) + a
    lin.append(actual)
    return lin, esp


def dibujar_sub(capa, b, t):
    lin, esp = lineas_de(b)
    e = ease((t - b['ini']) / 0.12)
    d = ImageDraw.Draw(capa)
    alto = 70
    y0 = Y_SUB + 10 * (1 - e)
    for j, l in enumerate(lin):
        ancho = sum(a for _, a in l) + esp * (len(l) - 1)
        x = (W - ancho) / 2
        y = y0 + j * alto
        for w, a in l:
            activa = w['ini'] <= t < w['fin']
            dicha = t >= w['ini']
            if activa:
                d.rounded_rectangle([x - 10, y + 2, x + a + 10, y + 66], radius=12, fill=VERDE + (int(255 * e),))
                col = (0, 0, 0)
            else:
                col = (255, 255, 255) if dicha else (190, 190, 190)
            # sombra suave para legibilidad
            if not activa:
                d.text((x + 2, y + 3), w['p'], font=F_SUB, fill=(0, 0, 0, int(170 * e)))
            d.text((x, y), w['p'], font=F_SUB, fill=col + (int(255 * e),))
            x += a + esp


# ---------- piezas fijas ----------
def tarjeta_foto():
    x, y, w, h = CARD
    foto = Image.open(os.path.join(AQUI, 'fuentes', 'camilo.png')).convert('RGB')
    # recorte 3:4 con la cara arriba
    fw, fh = foto.size
    ch = int(fw * h / w)
    foto = foto.crop((0, 18, fw, 18 + ch)).resize((w, h), Image.LANCZOS)
    tarjeta = Image.new('RGBA', (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(tarjeta)
    d.rounded_rectangle([0, 0, w + 15, h + 15], radius=30, fill=VERDE + (255,))
    mascara = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, w - 1, h - 1], radius=24, fill=255)
    tarjeta.paste(foto, (8, 8), mascara)
    return tarjeta


TARJETA = tarjeta_foto()
_lh = Image.open(LOGO_H).convert('RGBA')
_lh = _lh.crop(_lh.getbbox())
LOGO = _lh.resize((250, int(_lh.height * 250 / _lh.width)), Image.LANCZOS)
X_COL = CARD[0] + CARD[2] + 16 + 44
CHIP_CUNA = chip('EN EMERGE NOTICIAS', fuente('s', 'Bold', 26), VERDE, (0, 0, 0))
N1 = texto('Camilo', fuente('u', 'ExtraBold', 70), (255, 255, 255))
N2 = texto('Jiménez', fuente('u', 'ExtraBold', 70), (255, 255, 255))
C_LINEAS = [texto(c, fuente('s', 'Medium', 34), (215, 215, 215)) for c in CARGO]
C_ASGRO = texto('ASGRO', fuente('s', 'Bold', 34), VERDE)


# ---------- video ----------
class Lector:
    """Lee cuadros de cada parte en secuencia desde ffmpeg (sin cargar todo en memoria)."""
    def __init__(self):
        self.k, self.proc, self.n = -1, None, 0
        self.ultimo = np.zeros((BOX_H, 1080, 3), np.uint8)

    def abrir(self, k):
        if self.proc:
            self.proc.kill()
        f, a, z = PARTES[k]
        self.proc = subprocess.Popen([FFMPEG, '-v', 'error', '-ss', str(a), '-t', str(z - a), '-i',
                                      os.path.join(AQUI, 'fuentes', f), '-an',
                                      '-vf', f'{CROP},fps={FPS},scale=1080:{BOX_H}:flags=lanczos',
                                      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.k, self.n = k, 0

    def cuadro(self, k, idx):
        if k != self.k:
            self.abrir(k)
        tam = 1080 * BOX_H * 3
        while self.n <= idx:
            raw = self.proc.stdout.read(tam)
            if len(raw) < tam:
                break
            self.ultimo = np.frombuffer(raw, np.uint8).reshape(BOX_H, 1080, 3)
            self.n += 1
        return self.ultimo


def fondo_de(fr):
    im = Image.fromarray(fr)
    ancho = int(BOX_H * W / H)
    x = (1080 - ancho) // 2
    im = im.crop((x, 0, x + ancho, BOX_H)).resize((54, 96), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BICUBIC)
    yy = np.linspace(-1, 1, H)[:, None]
    v = (1 - 0.5 * np.clip(yy ** 2, 0, 1))[..., None]
    return (np.asarray(im).astype(np.float32) * 0.36 * v)


def onda(capa, t, env, activo):
    """Barras simétricas: historia reciente de la voz que avanza hacia la izquierda."""
    d = ImageDraw.Draw(capa)
    n, gap = 46, 8
    x0, x1 = 60, W - 60
    bw = (x1 - x0 - gap * (n - 1)) / n
    cy = Y_ONDA + H_ONDA / 2
    i_t = int(t * 120)
    for k in range(n):
        # cada barra = 3 muestras (25 ms) hacia atrás; la de la derecha es «ahora»
        j = i_t - (n - 1 - k) * 3
        v = env[j] if 0 <= j < len(env) else 0
        v = max(0.05, min(1.0, v)) * activo
        h = max(6, v * H_ONDA)
        x = x0 + k * (bw + gap)
        a = int(110 + 145 * (k / (n - 1)))
        d.rounded_rectangle([x, cy - h / 2, x + bw, cy + h / 2], radius=bw / 2, fill=VERDE + (a,))


def componer(t, lector, env, subs, dur, t_cambio):
    k = 0 if t < t_cambio else 1
    tl = t - (0 if k == 0 else t_cambio)
    fr = lector.cuadro(k, int(tl * FPS))
    lienzo = fondo_de(fr)
    lienzo[BOX_Y:BOX_Y + BOX_H] = fr
    base = Image.fromarray(lienzo.astype(np.uint8)).convert('RGBA')
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)

    e0 = ease(t / 0.5)
    # cabecera
    pegar(capa, LOGO, (W - LOGO.width) / 2, Y_LOGO, e0)
    # tarjeta con foto
    pegar(capa, TARJETA, CARD[0] - 8 - 30 * (1 - e0), CARD[1] - 8, e0)
    # columna de texto
    y = CARD[1] + 18
    pegar(capa, CHIP_CUNA, X_COL, y, ease((t - 0.1) / 0.5))
    e1 = ease((t - 0.2) / 0.5)
    pegar(capa, N1, X_COL + 30 * (1 - e1), y + 74, e1)
    pegar(capa, N2, X_COL + 30 * (1 - e1), y + 160, e1)
    e2 = ease((t - 0.35) / 0.5)
    for j, c in enumerate(C_LINEAS):
        pegar(capa, c, X_COL + 20 * (1 - e2), y + 280 + j * 46, e2)
    # línea verde bajo el bloque
    d.rectangle([X_COL, CARD[1] + CARD[3] - 6, X_COL + 120 * e2, CARD[1] + CARD[3] - 1], fill=VERDE + (255,))

    # onda de audio
    onda(capa, t, env, ease(t / 0.4))

    # filetes del clip
    d.rectangle([0, BOX_Y - 8, W, BOX_Y - 1], fill=VERDE + (255,))
    d.rectangle([0, BOX_Y + BOX_H, W, BOX_Y + BOX_H + 7], fill=VERDE + (255,))
    # destello en el cambio de parte
    if 0 <= t - t_cambio < 0.16:
        a = int(140 * (1 - (t - t_cambio) / 0.16))
        capa.alpha_composite(Image.new('RGBA', (W, BOX_H), (255, 255, 255, a)), (0, BOX_Y))

    # subtítulo vigente
    for b in subs:
        if b['ini'] <= t < b['fin']:
            dibujar_sub(capa, b, t)
            break

    base.alpha_composite(capa)
    # fundido de entrada / salida
    fade = min(clamp(t / 0.25), clamp((dur - t) / 0.4))
    if fade < 1:
        negro = Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - fade))))
        base.alpha_composite(negro)
    return base.convert('RGB')


def main():
    os.makedirs(os.path.join(AQUI, 'salida'), exist_ok=True)
    os.makedirs(os.path.join(AQUI, 'revision'), exist_ok=True)
    wav, dur, env = preparar_audio()
    t_cambio = (PARTES[0][2] - PARTES[0][1]) - XFADE
    subs = bloques(palabras())
    with open(os.path.join(AQUI, 'revision', 'subtitulos.txt'), 'w', encoding='utf-8') as f:
        for b in subs:
            f.write(f"{b['ini']:6.2f}-{b['fin']:6.2f}  {' '.join(w['p'] for w in b['ws'])}\n")
    print(f'Audio {dur:.2f} s, {len(subs)} subtítulos, cambio de parte en {t_cambio:.2f} s', flush=True)

    if '--fotos' in sys.argv:
        ts = sorted(float(x) for x in sys.argv[sys.argv.index('--fotos') + 1].split(','))
        lector = Lector()
        for t in ts:
            componer(t, lector, env, subs, dur, t_cambio).save(os.path.join(AQUI, 'revision', f'foto_{t:05.2f}.png'))
        print('Fotos listas.')
        return

    salida = os.path.join(AQUI, 'salida', 'cuna-asgro-camilo-jimenez-9x16.mp4')
    n = int(dur * FPS)
    enc = subprocess.Popen([FFMPEG, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                            '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
                            '-profile:v', 'high', '-movflags', '+faststart', salida], stdin=subprocess.PIPE)
    lector = Lector()
    for i in range(n):
        enc.stdin.write(componer(i / FPS, lector, env, subs, dur, t_cambio).tobytes())
        if i % 150 == 0:
            print(f'  {i}/{n}', flush=True)
    enc.stdin.close()
    enc.wait()
    print('Listo:', salida, f'({dur:.1f} s)')


if __name__ == '__main__':
    main()

