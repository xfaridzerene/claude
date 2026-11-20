# Reel vertical: despacho en terreno de Roberto Rojas-Connell (Emerge Noticias) desde Rengo,
# entrevista a Fabián Cofré, uno de los 7 ciclistas atropellados en Apalta.
# Video vertical propio a pantalla completa + logo arriba + GC al inicio + subtítulos en seco.
#   python build.py                 -> salida/rengo-ciclistas-atropellados-9x16.mp4
#   python build.py --fotos 1,40    -> revision/foto_<t>.png
import os, sys, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
FFMPEG = r'C:\Program Files\Shutter Encoder\app\Library\ffmpeg.exe'
EFM = r'C:\Users\farid\Desktop\EMERGE FM'
F_UNB = os.path.join(EFM, 'Fuentes', 'Unbounded', 'static', 'Unbounded-{}.ttf')
F_SG = os.path.join(EFM, 'Fuentes', 'Space_Grotesk', 'static', 'SpaceGrotesk-{}.ttf')
LOGO_H = os.path.join(EFM, 'LOGO', 'Logo 105.5', 'PNG', 'emerge-fm-105.5-horizontal-color-transparente.png')
ORIGINAL = r'C:\Users\farid\Downloads\20261116_161729~2.mp4'
FUENTE_VIDEO = os.path.join(AQUI, 'salida', '_editado.mp4')
# Versión < 3 min para IG/FB: fuera las preguntas intermedias de Roberto (se mantienen su
# presentación y su cierre). Tramos que se conservan, en segundos del original:
TRAMOS = [(0.0, 33.85),      # presentación … «Estoy con Fabián Cofré.»
          (38.30, 100.42),   # «Bueno, el día de ayer…» … «…nos ayudaron en ese momento.»
          (115.27, 137.25),  # «los vecinos fueron la primera línea…» … «…bomberos y ambulancia.»
          (149.80, 172.12),  # «Las siete bicicletas se quebraron…» … «…una sentencia.»
          (183.62, 218.45)]  # «Justicia, que esta persona…» … cierre de Roberto
# (versión completa de 3:38: revision/build_completo_218s.py)
CORTES = []
_acc = 0.0
for _a, _b in TRAMOS[:-1]:
    _acc += _b - _a
    CORTES.append(_acc)

W, H, FPS = 1080, 1920, 30
VERDE = (0, 230, 171)       # Verde Señal
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
OSCURO = (10, 14, 20)

# GC: (inicio, fin, nombre, cargo) en segundos del video
GCS = [
    (0.6, 8.0, 'Roberto Rojas-Connell', 'Periodista · Emerge Noticias'),
    (34.1, 41.3, 'Fabián Cofré', 'Ciclista atropellado en ruta H-50, Rengo'),
]

# Video de apoyo (cámara de seguridad, publicado por Rengonotas): se muestra una sola vez,
# a pantalla completa, recortado a 9:16 siguiendo la acción y con desenfoque leve en el impacto.
APOYO = os.path.join(AQUI, 'fuentes', 'apoyo.mp4')
APOYO_T, APOYO_DUR = 8.8, 7.0           # «lamentable noticia, un atropello…» → «…en Rosario.»
APOYO_W, APOYO_H = 764, 720
# encuadre: (segundo del apoyo, centro x, ancho del recorte 9:16) — sigue a los ciclistas, luego a la
# segunda camioneta (la que los atropella) y se acerca levemente al punto del impacto (lejos, x≈295)
ENCUADRE = [(0.0, 561, 405), (0.9, 561, 405), (2.1, 402, 405), (3.4, 402, 405), (4.6, 300, 330), (7.0, 300, 330)]
IMPACTO = (4.55, 99)                    # desenfoque leve desde el impacto hasta que sale el apoyo
BLUR_MAX = 9
CREDITO = 'Video: Rengonotas'

Y_LOGO = 70
Y_GC = 1215
Y_SUB = 1440

EDITS = [(['Aparta.'], ['Apalta.']), (['quiebraron'], ['quebraron']), (['quiebraron'], ['quebraron']),
         (['tec'], ['TEC']), (['105', '.5?'], ['105.5?']), (['llevar', 'ver'], ['llevar,', 'ver']),
         (['siete', 'deportistas', 'por'], ['siete', 'deportistas.', 'Por']), (['Exactamente'], ['Exactamente,']),
         (['señalar', 'ellos'], ['señalar.', 'Ellos']), (['accidente', 'el', 'chofer'], ['accidente,', 'el', 'chofer']),
         (['nosotros', 'llevaron'], ['nosotros.', 'Llevaron']), (['vendas', 'nos'], ['vendas,', 'nos']),
         (['sol', 'fueron'], ['sol,', 'fueron']), (['tránsito', 'y'], ['tránsito,', 'y']), (['llegó', 'Llegó'], ['llegó']),
         (['nosotros', 'Fabián,'], ['nosotros.', 'Fabián,']), (['Bueno', 'ahí'], ['Bueno,', 'ahí']),
         (['Rengo', 'Emerge', 'FM,'], ['Rengo,', 'Emerge', 'FM,']), (['este', 'accidente'], ['este', 'accidente.'])]
CORTAR_ANTES = [['y', 'en', 'un', 'segundo'], ['a', 'los', 'siete', 'deportistas.'], ['ellos', 'como', 'que'], ['esto', 'va', 'a', 'seguir'], ['el', 'cual', 'esa']]
UNIR = [['emerge', 'fm'], ['emerge', 'fm.'], ['emerge', 'fm,'], ['arraigar', 'cárcel'],
        ['pasando', 'una', 'y', 'una', 'y', 'otra', 'vez']]


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


# ---------- edición ----------
def armar_editado():
    if os.path.exists(FUENTE_VIDEO) and os.path.getmtime(FUENTE_VIDEO) > os.path.getmtime(__file__):
        return
    f, etiquetas = [], ''
    for k, (a, b) in enumerate(TRAMOS):
        d = b - a
        f.append(f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS}[v{k}]')
        f.append(f'[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d - 0.03}:d=0.03[a{k}]')
        etiquetas += f'[v{k}][a{k}]'
    f.append(f'{etiquetas}concat=n={len(TRAMOS)}:v=1:a=1[v][a]')
    tmp = FUENTE_VIDEO.replace('.mp4', '_tmp.mov')
    subprocess.run([FFMPEG, '-y', '-v', 'error', '-i', ORIGINAL, '-filter_complex', ';'.join(f),
                    '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast',
                    '-c:a', 'pcm_s16le', tmp], check=True)
    os.replace(tmp, FUENTE_VIDEO)


# ---------- audio ----------
def preparar_audio():
    wav = os.path.join(AQUI, 'salida', '_audio.wav')
    subprocess.run([FFMPEG, '-y', '-v', 'error', '-i', FUENTE_VIDEO,
                    '-af', 'aresample=48000,highpass=f=70,afade=t=in:d=0.08,'
                           'loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000',
                    '-ac', '2', '-c:a', 'pcm_s16le', wav], check=True)
    out = subprocess.run([FFMPEG, '-v', 'error', '-i', wav, '-f', 'null', '-'], capture_output=True)
    from scipy.io import wavfile
    sr, x = wavfile.read(wav)
    return wav, len(x) / sr


class Lector:
    def __init__(self, ruta, w=W, h=H):
        self.w, self.h = w, h
        self.proc = subprocess.Popen([FFMPEG, '-v', 'error', '-i', ruta, '-vf', f'scale={w}:{h},fps={FPS}',
                                      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.n = 0
        self.ultimo = np.zeros((h, w, 3), np.uint8)

    def cuadro(self, idx):
        w, h = self.w, self.h
        tam = w * h * 3
        while self.n <= idx:
            raw = self.proc.stdout.read(tam)
            if len(raw) < tam:
                break
            self.ultimo = np.frombuffer(raw, np.uint8).reshape(h, w, 3)
            self.n += 1
        return self.ultimo


# ---------- subtítulos ----------
def palabras():
    d = json.load(open(os.path.join(AQUI, 'transcripcion.json'), encoding='utf-8'))
    out, base = [], 0.0
    for a, b in TRAMOS:
        primera = True
        for s in d['audio1']:
            for w in s['palabras']:
                # 0.35 s de margen al inicio: whisper adelanta el «Bueno,» de Fabián (38.0 vs 38.4 real)
                if a - 0.35 <= w['ini'] and w['fin'] <= b + 0.12:
                    ini = max(base + w['ini'] - a, base + 0.08)
                    fin = max(min(base + w['fin'] - a, base + b - a), ini + 0.25)
                    out.append(dict(p=w['p'].strip(), ini=ini, fin=fin, nuevo=primera))
                    primera = False
        base += b - a
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
        if i and out[i - 1]['p'][-1] in '.?!' and w['p'][0].islower():
            w['p'] = w['p'][0].upper() + w['p'][1:]
        sig = out[i + 1]['ini'] if i + 1 < len(out) else w['fin']
        w['fin'] = min(max(w['fin'], sig), w['ini'] + 0.9)
    return out


F_SUB = fuente('s', 'Bold', 56)
MAX_LINEA = 920
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
        forzar = any(txt[i:i + len(c)] == c for c in CORTAR_ANTES) or w.get('nuevo')
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
        y = Y_SUB + j * 74
        for w, a in l:
            if w['ini'] <= t < w['fin']:
                d.rounded_rectangle([x - 10, y + 3, x + a + 10, y + 69], radius=12, fill=VERDE + (255,))
                col = NEGRO
            else:
                for dx, dy in ((2, 3), (0, 2), (2, 0)):
                    d.text((x + dx, y + dy), w['p'], font=F_SUB, fill=(0, 0, 0, 190))
                col = BLANCO
            d.text((x, y), w['p'], font=F_SUB, fill=col + (255,))
            x += a + esp


# ---------- piezas fijas ----------
_lh = Image.open(LOGO_H).convert('RGBA')
_lh = _lh.crop(_lh.getbbox())
LOGO = _lh.resize((300, int(_lh.height * 300 / _lh.width)), Image.LANCZOS)
F_NOM = fuente('u', 'Bold', 46)
F_CARGO = fuente('s', 'Medium', 32)
CHIP_NOT = chip('EMERGE NOTICIAS', fuente('s', 'Bold', 26), VERDE, NEGRO)


def ficha(nombre, cargo):
    """GC: chips arriba, y placa oscura con filete verde, nombre y cargo."""
    tn = texto(nombre, F_NOM, BLANCO)
    tc = texto(cargo, F_CARGO, (205, 245, 232))
    ancho = max(tn.width, tc.width) + 36 + 44
    alto = 150
    im = Image.new('RGBA', (max(ancho, CHIP_NOT.width), alto + CHIP_NOT.height + 12), (0, 0, 0, 0))
    im.alpha_composite(CHIP_NOT, (0, 0))
    y0 = CHIP_NOT.height + 12
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, y0, ancho, y0 + alto], radius=18, fill=OSCURO + (228,))
    d.rounded_rectangle([0, y0, 12, y0 + alto], radius=6, fill=VERDE + (255,))
    im.alpha_composite(tn, (36, y0 + 20))
    im.alpha_composite(tc, (38, y0 + 90))
    return im


FICHAS = [(a, b, ficha(n, c)) for a, b, n, c in GCS]


def degradados():
    """Oscurece arriba (logo) y abajo (GC + subtítulos) para que se lea sobre la calle."""
    y = np.arange(H, dtype=np.float32)
    arriba = clamp_arr(1 - y / 330) ** 1.6 * 0.55
    abajo = clamp_arr((y - 1080) / 600) ** 1.4 * 0.62
    return (1 - np.maximum(arriba, abajo))[:, None, None]


def clamp_arr(a):
    return np.clip(a, 0, 1)


OSCURECER = degradados()


def suave(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def mascara_franja():
    """Franja del texto quemado del video original («CICLISTAS DEL TEAM RENGO…»), en px de la fuente."""
    y = np.arange(APOYO_H, dtype=np.float32)
    m = np.minimum(np.clip((y - 455) / 30, 0, 1), np.clip((655 - y) / 30, 0, 1))
    return Image.fromarray((m[:, None] * np.ones((1, APOYO_W)) * 255).astype(np.uint8), 'L')


MASCARA_FRANJA = mascara_franja()


def encuadre(ta):
    for (t0, x0, w0), (t1, x1, w1) in zip(ENCUADRE, ENCUADRE[1:]):
        if ta <= t1:
            k = suave((ta - t0) / (t1 - t0))
            return x0 + (x1 - x0) * k, w0 + (w1 - w0) * k
    return ENCUADRE[-1][1], ENCUADRE[-1][2]


def cuadro_apoyo(lector, ta):
    """Recorte 9:16 que sigue la acción, con la franja del texto quemado esmerilada (queda tras los
    subtítulos) y desenfoque leve en el impacto."""
    im = Image.fromarray(lector.cuadro(int(ta * FPS)))
    im = Image.composite(im.filter(ImageFilter.GaussianBlur(11)), im, MASCARA_FRANJA)
    cx, cw = encuadre(ta)
    ch = cw * 16 / 9
    x0 = min(max(cx - cw / 2, 0), APOYO_W - cw)
    im = im.resize((W, H), Image.LANCZOS, box=(x0, 0, x0 + cw, ch))
    a, b = IMPACTO
    k = min(suave((ta - a) / 0.3), suave((b - ta) / 0.3))
    if k > 0.01:
        im = im.filter(ImageFilter.GaussianBlur(BLUR_MAX * k))
    return np.asarray(im).astype(np.float32)


F_CRED = fuente('s', 'SemiBold', 26)



def componer(t, lector, subs, dur, apoyo=None):
    fr = lector.cuadro(int(t * FPS)).astype(np.float32)
    ta = t - APOYO_T
    if apoyo is not None and 0 <= ta < APOYO_DUR:
        mezcla = min(clamp(ta / 0.15), clamp((APOYO_DUR - ta) / 0.15))
        fr = fr * (1 - mezcla) + cuadro_apoyo(apoyo, ta) * mezcla
    fr = fr * OSCURECER
    base = Image.fromarray(fr.astype(np.uint8)).convert('RGBA')
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pegar(capa, LOGO, (W - LOGO.width) / 2, Y_LOGO, ease(t / 0.5))
    if 0 <= ta < APOYO_DUR:
        a = min(clamp(ta / 0.2), clamp((APOYO_DUR - ta) / 0.2))
        ImageDraw.Draw(capa).text((W / 2, Y_LOGO + LOGO.height + 22), CREDITO, font=F_CRED,
                                  fill=(255, 255, 255, int(215 * a)), anchor='mt')
    for a, b, im in FICHAS:
        if a - 0.05 <= t < b + 0.5:
            e_in = ease((t - a) / 0.45)
            e_out = 1 - ease((t - b) / 0.4)
            e = min(e_in, e_out)
            pegar(capa, im, 60 - 80 * (1 - e), Y_GC - im.height, e)
    for b in subs:
        if b['ini'] <= t < b['fin']:
            dibujar_sub(capa, b, t)
            break
    base.alpha_composite(capa)
    for tc in CORTES:  # destello blanco breve en cada corte
        f = clamp(1 - abs(t - tc) / 0.1) * 0.55
        if f > 0.01:
            base.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * f))))
    fade = min(clamp(t / 0.2), clamp((dur - t) / 0.6))
    if fade < 1:
        base.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - fade)))))
    return base.convert('RGB')


def main():
    os.makedirs(os.path.join(AQUI, 'salida'), exist_ok=True)
    os.makedirs(os.path.join(AQUI, 'revision'), exist_ok=True)
    armar_editado()
    subs = bloques(palabras())
    with open(os.path.join(AQUI, 'revision', 'subtitulos.txt'), 'w', encoding='utf-8') as f:
        for b in subs:
            f.write(f"{b['ini']:6.2f}-{b['fin']:6.2f}  {' '.join(w['p'] for w in b['ws'])}\n")

    if '--fotos' in sys.argv:
        ts = sorted(float(x) for x in sys.argv[sys.argv.index('--fotos') + 1].split(','))
        lector = Lector(FUENTE_VIDEO)
        apoyo = Lector(APOYO, APOYO_W, APOYO_H)
        for t in ts:
            componer(t, lector, subs, 218, apoyo).save(os.path.join(AQUI, 'revision', f'foto_{t:06.2f}.png'))
        print('Fotos listas.')
        return

    wav, dur = preparar_audio()
    print(f'Audio {dur:.2f} s, {len(subs)} subtítulos', flush=True)
    salida = os.path.join(AQUI, 'salida', 'rengo-ciclistas-atropellados-9x16.mp4')
    n = int(dur * FPS)
    enc = subprocess.Popen([FFMPEG, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                            '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-maxrate', '6M', '-bufsize', '12M',
                            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart', salida],
                           stdin=subprocess.PIPE)
    lector = Lector(FUENTE_VIDEO)
    apoyo = Lector(APOYO, APOYO_W, APOYO_H)
    for i in range(n):
        enc.stdin.write(componer(i / FPS, lector, subs, dur, apoyo).tobytes())
        if i % 600 == 0:
            print(f'  {i}/{n}', flush=True)
    enc.stdin.close()
    enc.wait()
    print('Listo:', salida, f'({dur:.1f} s)')


if __name__ == '__main__':
    main()

