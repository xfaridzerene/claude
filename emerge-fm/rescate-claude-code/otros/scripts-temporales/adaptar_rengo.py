import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b)
# cabecera del archivo
i = s.index('import os, sys')
s = '''# Reel vertical del despacho de Roberto Rojas-Connell desde Rengo (paro de camioneros).
# El video es vertical y va a pantalla completa. Arriba: marca de la radio.
# Abajo: quién habla, onda de audio en vivo y subtítulos en seco con la palabra activa en verde.
#   python build.py                 -> salida/rengo-paro-camioneros-9x16.mp4
#   python build.py --fotos 1,20    -> revision/foto_<t>.png
''' + s[i:]
rep(s[s.index('PARTES = ['):s.index('XFADE')], "PARTES = [('rengo.mp4', 0.0, 135.8)]   # completo; termina ~0,9 s después de «…paro de camioneros.»\nTRANS = ['audio1']\n")
rep("""Y_LOGO = 92
CARD = (60, 175, 360, 480)        # x, y, ancho, alto de la foto
Y_ONDA, H_ONDA = 700, 110
BOX_Y, BOX_H = 850, 608
Y_SUB = BOX_Y + BOX_H + 54""", """Y_LOGO = 96
Y_NOMBRE = 1222                   # bloque inferior: quién habla
Y_ONDA, H_ONDA = 1360, 84
Y_SUB = 1452""")
# quitar ficha del invitado
a = s.index('CORTAR_ANTES'); b = s.index('def fuente(')
s = s[:a] + "CORTAR_ANTES = []\nEDITS = []\n\nHABLA = 'Roberto Rojas-Connell'\nROL = 'Conductor · Emerge Noticias'\n\n\n" + s[b:]
a = s.index('# ---------- piezas fijas'); b = s.index('def main():')
s = s[:a] + '''# ---------- piezas fijas ----------
_lh = Image.open(LOGO_H).convert('RGBA')
_lh = _lh.crop(_lh.getbbox())
LOGO = _lh.resize((300, int(_lh.height * 300 / _lh.width)), Image.LANCZOS)
CHIP = chip('EMERGE NOTICIAS', fuente('s', 'Bold', 26), VERDE, (0, 0, 0))
T_NOMBRE = texto(HABLA, fuente('u', 'Bold', 52), (255, 255, 255))
T_ROL = texto(ROL, fuente('s', 'Medium', 30), (210, 210, 210))


def degradados():
    """Oscurece arriba (logo) y abajo (texto) para que se lea sobre el video."""
    g = np.zeros((H, W, 4), np.uint8)
    y = np.arange(H, dtype=np.float32)
    arriba = np.clip(1 - y / 330, 0, 1) ** 1.5 * 170
    abajo = np.clip((y - 1020) / 420, 0, 1) ** 1.2 * 225
    g[..., 3] = np.maximum(arriba, abajo).astype(np.uint8)[:, None]
    return Image.fromarray(g, 'RGBA')


DEGRADADO = degradados()


# ---------- video ----------
class Lector:
    """Lee los cuadros del video vertical a 1080×1920 desde ffmpeg."""
    def __init__(self):
        self.k, self.proc, self.n = -1, None, 0
        self.ultimo = np.zeros((H, W, 3), np.uint8)

    def abrir(self, k):
        if self.proc:
            self.proc.kill()
        f, a, z = PARTES[k]
        self.proc = subprocess.Popen([FFMPEG, '-v', 'error', '-ss', str(a), '-t', str(z - a), '-i',
                                      os.path.join(AQUI, 'fuentes', f), '-an',
                                      '-vf', f'fps={FPS},scale={W}:{H}:flags=lanczos,setsar=1,unsharp=5:5:0.6',
                                      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.k, self.n = k, 0

    def cuadro(self, k, idx):
        if k != self.k:
            self.abrir(k)
        tam = W * H * 3
        while self.n <= idx:
            raw = self.proc.stdout.read(tam)
            if len(raw) < tam:
                break
            self.ultimo = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
            self.n += 1
        return self.ultimo


def onda(capa, t, env, activo):
    """Barras: historia reciente de la voz que avanza hacia la izquierda."""
    d = ImageDraw.Draw(capa)
    n, gap = 46, 8
    x0, x1 = 60, W - 60
    bw = (x1 - x0 - gap * (n - 1)) / n
    cy = Y_ONDA + H_ONDA / 2
    i_t = int(t * 120)
    for k in range(n):
        j = i_t - (n - 1 - k) * 3
        v = env[j] if 0 <= j < len(env) else 0
        v = max(0.05, min(1.0, v)) * activo
        h = max(6, v * H_ONDA)
        x = x0 + k * (bw + gap)
        a = int(110 + 145 * (k / (n - 1)))
        d.rounded_rectangle([x, cy - h / 2, x + bw, cy + h / 2], radius=bw / 2, fill=VERDE + (a,))


def componer(t, lector, env, subs, dur, cambios):
    k = sum(1 for c in cambios if t >= c)
    tl = t - ([0.0] + cambios)[k]
    base = Image.fromarray(lector.cuadro(k, int(tl * FPS))).convert('RGBA')
    base.alpha_composite(DEGRADADO)
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    e0 = ease(t / 0.5)
    # marca arriba
    pegar(capa, LOGO, (W - LOGO.width) / 2, Y_LOGO, e0)
    # quién habla
    x = 60
    e1 = ease((t - 0.15) / 0.5)
    pegar(capa, CHIP, x, Y_NOMBRE, e1)
    pegar(capa, T_NOMBRE, x + 24 * (1 - e1), Y_NOMBRE + 50, e1)
    d.rectangle([x, Y_NOMBRE + 126, x + 6, Y_NOMBRE + 162], fill=VERDE + (int(255 * e1),))
    pegar(capa, T_ROL, x + 22 + 24 * (1 - e1), Y_NOMBRE + 124, e1)
    # onda
    onda(capa, t, env, ease(t / 0.4))
    # subtítulo vigente
    for b in subs:
        if b['ini'] <= t < b['fin']:
            dibujar_sub(capa, b, t)
            break
    base.alpha_composite(capa)
    fade = min(clamp(t / 0.25), clamp((dur - t) / 0.6))
    if fade < 1:
        base.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - fade)))))
    return base.convert('RGB')


''' + s[b:]
s = s.replace("'larenas-agricultores-unidos-9x16.mp4'", "'rengo-paro-camioneros-9x16.mp4'")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
