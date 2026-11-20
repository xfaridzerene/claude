# Base musical original del reel «primer día» (sintetizada, sin derechos de terceros).
# 128 BPM, Do mayor, todo medido en negras (debe calzar con build.py):
#   0–4    intro (G): hats que crecen, redoble, subida
#   4–34   los 5 clips, 6 negras cada uno, un acorde por clip (C G Am F C); crash + destello en cada corte
#   34–38  «GRACIAS» (F): sin bombo, palmas y stabs
#   38–40  subida (G) con redoble
#   40–44  acorde final (C) con el logo, se apaga
#   python musica.py  -> salida/_musica.wav (estéreo 48 kHz, ~−14 LUFS)
import os, subprocess, re
import numpy as np
from scipy import signal
from scipy.io import wavfile

AQUI = os.path.dirname(os.path.abspath(__file__))
FFMPEG = r'C:\Program Files\Shutter Encoder\app\Library\ffmpeg.exe'
SR = 48000
BPM = 128
BEAT = 60 / BPM
N_BEATS = 44
DUR = N_BEATS * BEAT
N = int(DUR * SR) + 1
rng = np.random.default_rng(11)

INTRO, CLIP, N_CLIPS = 4, 6, 5
FIN_CLIPS = INTRO + CLIP * N_CLIPS          # 34
CORTES = [INTRO + CLIP * k for k in range(N_CLIPS)] + [FIN_CLIPS]

ACORDES = {  # voces de los stabs/pad, raíz del bajo
    'C': ([60, 64, 67, 72], 36), 'G': ([59, 62, 67, 71], 43),
    'Am': ([60, 64, 69, 72], 45), 'F': ([60, 65, 69, 72], 41),
}
# (negra de inicio, negra de fin, acorde)
TRAMOS = [(0, 4, 'G')] + [(INTRO + CLIP * k, INTRO + CLIP * (k + 1), c) for k, c in enumerate(['C', 'G', 'Am', 'F', 'C'])] \
    + [(34, 38, 'F'), (38, 40, 'G'), (40, 44, 'C')]


def acorde_en(b):
    for a, z, c in TRAMOS:
        if a <= b < z:
            return c
    return 'C'


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def filtro(x, fc, tipo='low', orden=2):
    return signal.sosfilt(signal.butter(orden, fc, tipo, fs=SR, output='sos'), x)


def saw(f, n, fase=None):
    fase = rng.random() if fase is None else fase
    return 2 * ((fase + f * np.arange(n) / SR) % 1) - 1


def poner(pista, x, beat, gan=1.0):
    i = int(beat * BEAT * SR)
    if 0 <= i < len(pista):
        x = x[:len(pista) - i]
        pista[i:i + len(x)] += x * gan


def tt(n):
    return np.arange(n) / SR


# ---------- instrumentos ----------
def bombo():
    n = int(0.4 * SR); t = tt(n)
    f = 50 + 150 * np.exp(-t / 0.03)
    cuerpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    click = filtro(rng.standard_normal(n), 2500, 'high') * np.exp(-t / 0.004) * 0.4
    return np.tanh(1.8 * (cuerpo + click))


def palma():
    n = int(0.3 * SR); t = tt(n)
    ruido = filtro(rng.standard_normal(n), [900, 4500], 'band')
    e = np.zeros(n)
    for k, d in enumerate([0, 0.01, 0.02]):
        m = t >= d
        e[m] += np.exp(-(t[m] - d) / (0.005 if k < 2 else 0.09))
    return ruido * e


def caja():  # redobles
    n = int(0.18 * SR); t = tt(n)
    tono = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04)
    ruido = filtro(rng.standard_normal(n), 1800, 'high') * np.exp(-t / 0.06)
    return tono * 0.5 + ruido * 0.7


def hat(abierto=False):
    n = int((0.2 if abierto else 0.045) * SR); t = tt(n)
    return filtro(rng.standard_normal(n), 7500, 'high') * np.exp(-t / (0.06 if abierto else 0.011))


def perc():  # golpe de madera
    n = int(0.08 * SR); t = tt(n)
    return (np.sin(2 * np.pi * 820 * t) + 0.5 * np.sin(2 * np.pi * 1630 * t)) * np.exp(-t / 0.018)


def crash(largo=1.6):
    n = int(largo * SR); t = tt(n)
    return filtro(rng.standard_normal(n), 4500, 'high') * np.exp(-t / (largo / 3.2))


def subida(dur):
    n = int(dur * SR); t = tt(n)
    x = rng.standard_normal(n)
    a = filtro(x, 1500) * (1 - t / dur) + filtro(x, 3000, 'high') * (t / dur)
    return a * (t / dur) ** 2.2


def stab(voces, dur=0.16):
    n = int((dur + 0.05) * SR); t = tt(n)
    x = np.zeros(n)
    for m in voces:
        for det in (-0.1, 0, 0.1):
            x += saw(hz(m + det), n)
    x /= len(voces) * 3
    e = np.minimum(1, t / 0.003) * np.where(t < dur, np.exp(-t / 0.12), np.exp(-dur / 0.12) * np.exp(-(t - dur) / 0.015))
    return filtro(x, 3800) * e


def pad(voces, dur):
    n = int((dur + 0.4) * SR); t = tt(n)
    x = np.zeros(n)
    for m in voces:
        for det in (-0.12, -0.05, 0.05, 0.12):
            x += saw(hz(m + det), n)
    x /= len(voces) * 4
    e = np.minimum(1, t / 0.05) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.15))
    return filtro(x, 2200) * e


def bajo(m, dur=0.11):
    n = int((dur + 0.03) * SR); t = tt(n)
    x = saw(hz(m), n, 0) * 0.6 + np.sin(2 * np.pi * hz(m) * t) * 0.7
    e = np.minimum(1, t / 0.003) * np.where(t < dur, np.exp(-t / 0.15), 0.3 * np.exp(-(t - dur) / 0.01))
    return filtro(x, 900) * e


def pluck(m, dur=0.2):
    n = int(dur * SR); t = tt(n)
    x = saw(hz(m), n, 0) * 0.7 + np.sin(2 * np.pi * hz(m + 12) * t) * 0.3
    return filtro(x, 3500) * np.exp(-t / 0.06)


def campana(m, dur=2.5):
    n = int(dur * SR); t = tt(n); f = hz(m)
    x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.08)
         + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t / 0.05))
    return x * np.exp(-t / 0.5) * np.minimum(1, t / 0.003)


def reverb(x, largo=1.6, semilla=3):
    r = np.random.default_rng(semilla)
    n = int(largo * SR); t = tt(n)
    ir = filtro(r.standard_normal(n) * np.exp(-t / (largo / 6.9)), 6000)
    ir[:int(0.01 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    return signal.fftconvolve(x, ir)[:len(x)] * 0.22


# ---------- arreglo ----------
def construir():
    P = {k: np.zeros(N) for k in ('kick', 'clap', 'snare', 'hats', 'perc', 'crash', 'swoosh',
                                    'stab', 'pad', 'bass', 'arp', 'bell')}
    K, CL, SN, HC, HO, PC = bombo(), palma(), caja(), hat(), hat(True), perc()
    bombos = []

    # intro: hats que crecen, bombo en 1 y 3, redoble, pad cerrado que se abre
    for s in range(16):
        poner(P['hats'], HC, s / 4, 0.1 + 0.25 * s / 16)
    for b in (0, 2):
        poner(P['kick'], K, b, 0.8); bombos.append(b)
    for k, s in enumerate(np.arange(2, 4, 0.25)):
        poner(P['snare'], SN, s, 0.25 + 0.6 * k / 8)
    poner(P['swoosh'], subida(4 * BEAT), 0, 1.6)

    # groove de los clips (negras 4–34)
    PATRON_STAB = [0, 0.75, 1.5, 2.0, 2.75, 3.5]           # 3-3-2 sobre cada compás
    PERC_16 = [3, 6, 11, 14]                                 # semicorcheas de la madera
    for b in range(INTRO, FIN_CLIPS):
        voces, raiz = ACORDES[acorde_en(b)]
        rel = (b - INTRO) % 4                                # posición en el compás
        poner(P['kick'], K, b); bombos.append(b)
        if rel in (1, 3):
            poner(P['clap'], CL, b)
        for s in range(4):
            v = (0.55, 0.22, 0.0, 0.3)[s]
            if v:
                poner(P['hats'], HC, b + s / 4, v)
        poner(P['hats'], HO, b + 0.5, 0.42)
        # bajo rodante: corchea a contratiempo + octava en la semicorchea siguiente
        poner(P['bass'], bajo(raiz), b + 0.5, 1.0)
        poner(P['bass'], bajo(raiz + 12, 0.08), b + 0.75, 0.7)
        # arpegio en semicorcheas (desde el 2º clip)
        if b >= INTRO + CLIP:
            orden = [0, 2, 1, 3]
            for s in range(4):
                poner(P['arp'], pluck(voces[orden[s]] + 12), b + s / 4, 0.5 if s == 0 else 0.33)
    # stabs y madera por compás (negras 4–34 y el «GRACIAS»)
    for b0 in np.arange(INTRO, 38, 4):
        for off in PATRON_STAB:
            b = b0 + off
            if b < 38:
                poner(P['stab'], stab(ACORDES[acorde_en(int(b))][0]), b, 0.9)
        for s in PERC_16:
            b = b0 + s / 4
            if b < 38:
                poner(P['perc'], PC, b, 0.35)

    # pad suave de fondo por tramo
    for a, z, c in TRAMOS:
        poner(P['pad'], pad(ACORDES[c][0], (z - a) * BEAT), a, 0.5 if a else 0.8)

    # antes de cada corte: dos golpes de caja + swoosh; en el corte: crash
    for c in CORTES[1:]:
        poner(P['snare'], SN, c - 0.5, 0.45)
        poner(P['snare'], SN, c - 0.25, 0.6)
        poner(P['swoosh'], subida(0.3), c - 0.3 / BEAT, 0.7)
    for c in CORTES:
        poner(P['crash'], crash(), c, 0.85)

    # «GRACIAS» (34–38): sin bombo, palmas en 2 y 4, hats
    for b in range(34, 38):
        if (b - 34) % 2:
            poner(P['clap'], CL, b, 0.8)
        poner(P['hats'], HO, b + 0.5, 0.4)
        poner(P['bass'], bajo(ACORDES['F'][1], 0.3), b, 0.7)
    # subida (38–40): redoble en semicorcheas que crece
    for k, s in enumerate(np.arange(38, 40, 0.25)):
        poner(P['snare'], SN, s, 0.3 + 0.7 * k / 8)
    poner(P['swoosh'], subida(2 * BEAT), 38, 1.4)
    # acorde final (40): golpe con bombo, bajo largo, campanas
    poner(P['kick'], K, 40, 1.1); bombos.append(40)
    poner(P['crash'], crash(3.0), 40, 1.0)
    poner(P['bass'], bajo(ACORDES['C'][1], 1.5), 40, 1.0)
    for m in ACORDES['C'][0] + [72, 76]:
        poner(P['bell'], campana(m + 12), 40, 0.13)
    poner(P['stab'], stab(ACORDES['C'][0], 0.9), 40, 1.0)

    # pad abierto progresivamente en la intro
    i4 = int(4 * BEAT * SR)
    intro = P['pad'][:i4].copy()
    mezcla = np.linspace(0, 1, i4) ** 1.5
    P['pad'][:i4] = filtro(intro, 900) * (1 - mezcla) + intro * mezcla

    # sidechain desde el bombo
    sc = np.ones(N); t = tt(N)
    for b in bombos:
        i = int(b * BEAT * SR); j = min(N, i + int(0.3 * SR))
        sc[i:j] = np.minimum(sc[i:j], 1 - 0.65 * np.exp(-(t[i:j] - b * BEAT) / 0.09))
    for k in ('pad', 'stab', 'arp'):
        P[k] *= sc
    P['bass'] *= 0.45 + 0.55 * sc

    # estéreo: arpegio con delay ping-pong (corchea con puntillo), hats/perc abiertos a los lados
    d = int(0.75 * BEAT * SR)
    arpL, arpR = P['arp'] * 0.8, P['arp'] * 0.8
    eco = P['arp'].copy()
    for k in range(1, 5):
        eco = np.concatenate([np.zeros(d), eco[:-d]]) * 0.4
        if k % 2:
            arpR += eco
        else:
            arpL += eco

    centro = P['kick'] * 1.0 + P['clap'] * 0.45 + P['snare'] * 0.35 + P['bass'] * 0.55 + P['crash'] * 0.16 \
        + P['swoosh'] * 0.12 + P['bell'] * 0.9
    L = centro + P['stab'] * 0.55 + P['pad'] * 0.28 + arpL * 0.26 + P['hats'] * 0.30 + P['perc'] * 0.18
    R = centro + P['stab'] * 0.50 + P['pad'] * 0.30 + arpR * 0.26 + P['hats'] * 0.24 + P['perc'] * 0.30
    envio = P['clap'] * 0.4 + P['snare'] * 0.3 + P['stab'] * 0.5 + P['bell'] * 0.8
    L += reverb(envio + arpL * 0.2, semilla=3)
    R += reverb(envio + arpR * 0.2, semilla=4)
    st = filtro(np.stack([L, R]), 30, 'high').T
    nf = int(2.5 * BEAT * SR)  # fade en las últimas 2,5 negras
    fade = np.ones(N); fade[-nf:] = np.linspace(1, 0, nf) ** 1.5
    return st * fade[:, None]


def lufs(ruta):
    out = subprocess.run([FFMPEG, '-hide_banner', '-nostats', '-i', ruta, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', out)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', out)[-1])


def main():
    os.makedirs(os.path.join(AQUI, 'salida'), exist_ok=True)
    ruta = os.path.join(AQUI, 'salida', '_musica.wav')
    seco = construir()
    seco /= np.max(np.abs(seco))
    gan = 1.0
    for _ in range(4):  # ~−14 LUFS con limitador suave
        st = np.tanh(seco * gan * 1.2) / np.tanh(1.2) * 0.89
        wavfile.write(ruta, SR, (np.clip(st, -1, 1) * 32767).astype(np.int16))
        i, pk = lufs(ruta)
        print(f'  ganancia {gan:.2f} -> {i:.1f} LUFS, pico {pk:.1f} dBTP')
        if abs(i + 14) < 0.4:
            break
        gan *= 10 ** ((-14 - i) / 20)
    print('Música:', ruta, f'{DUR:.2f} s')


if __name__ == '__main__':
    main()
