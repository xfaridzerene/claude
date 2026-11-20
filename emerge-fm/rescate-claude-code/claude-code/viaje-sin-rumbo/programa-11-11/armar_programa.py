# Viaje sin Rumbo – miércoles 11-11-2026 – "Reinas del pop: las mujeres de la música chilena".
# Correr con: C:\Users\farid\audio-env\Scripts\python.exe armar_programa.py
#
# Reglas de este programa (igual que el martes):
#  - La VOZ se nivela solo con ganancia (sin EQ, compresor ni limpieza) y un
#    limitador con anticipación para los picos sueltos. Todo parejo a -18 LUFS.
#  - LOCUCIÓN y MENCIONES van sobre la cortina de fondo (Nicole – Viaje Infinito).
#  - FRASES (cuñas Molen, Valhalla) van solas, sin cortina, en el corte comercial.
#  - Se entrega mezcla + pista de voz sola + pista de música/cortinas, alineadas,
#    para regular la voz después.
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import pyloudnorm as pyln

SR = 48000
DL = Path(r"C:\Users\farid\Downloads")
MUS = DL / "Música Vale (normalizada)"   # canciones y cortina de fondo se movieron aquí
FF = r"C:\Users\farid\audio-env\bin\ffmpeg.exe"
OUT = Path(__file__).resolve().parent / "salida"
OUT.mkdir(exist_ok=True)
meter = pyln.Meter(SR)

def load(name):
    raw = subprocess.run([FF, "-v", "error", "-i", str(DL / name), "-map", "0:a:0",
                          "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)

def envelope(x, win=0.02):
    e = np.abs(x).max(axis=1); w = int(win * SR)
    return np.convolve(e, np.ones(w) / w, "same")

def bounds(x, thr_db):
    idx = np.where(envelope(x) > 10 ** (thr_db / 20))[0]
    return idx[0], idx[-1]

def trim(x, thr_db=-50, pad=0.02):
    a, b = bounds(x, thr_db)
    return x[max(0, a - int(pad * SR)):min(len(x), b + int(pad * SR))]

def norm(x, lufs):
    return x * 10 ** ((lufs - meter.integrated_loudness(x)) / 20)

def fade(x, fin=0.0, fout=0.0):
    x = x.copy()
    if fin:  n = int(fin * SR);  x[:n] *= np.linspace(0, 1, n)[:, None]
    if fout: n = int(fout * SR); x[-n:] *= np.linspace(1, 0, n)[:, None]
    return x

def s(t): return int(round(t * SR))

def quietest(x, a, b, win=0.05):
    """Centro de la ventana más silenciosa entre a y b segundos."""
    seg = x[s(a):s(b)]
    e = np.convolve((seg ** 2).mean(axis=1), np.ones(s(win)) / s(win), "valid")
    return s(a) + int(np.argmin(e)) + s(win) // 2

def splice(x, cuts, xf=0.015):
    """cuts: [(desde_a, desde_b, hasta_a, hasta_b)] -> se elimina del silencio en
    [desde_a, desde_b] hasta el silencio en [hasta_a, hasta_b]."""
    keep, pos = [], 0
    for a1, b1, a2, b2 in cuts:
        c1, c2 = quietest(x, a1, b1), quietest(x, a2, b2)
        keep.append((pos, c1)); pos = c2
        print(f"   corte {c1/SR:6.2f}s → {c2/SR:6.2f}s (se sacan {(c2-c1)/SR:.2f}s)")
    keep.append((pos, len(x)))
    n = s(xf); out = x[keep[0][0]:keep[0][1]].copy()
    for a, b in keep[1:]:
        nxt = x[a:b].copy()
        r = np.linspace(0, 1, n)[:, None]
        out[-n:] = out[-n:] * (1 - r) + nxt[:n] * r
        out = np.concatenate([out, nxt[n:]])
    return out

from scipy.ndimage import minimum_filter1d, uniform_filter1d

def limiter(x, ceil_db=-1.0, look=0.005, hold=0.020, smooth=0.030):
    """Limitador con anticipación: solo baja la ganancia en los picos que pasan
    el techo, con curvas suaves (sin recortar ni saturar la onda)."""
    thr = 10 ** (ceil_db / 20)
    pk = np.abs(x).max(axis=1)
    need = np.minimum(1.0, thr / np.maximum(pk, 1e-9))
    g = minimum_filter1d(need, s(2 * look + hold))
    g = uniform_filter1d(g, s(smooth))
    g = np.minimum(g, minimum_filter1d(need, s(look) * 2 + 1))  # garantía en el pico
    return x * g[:, None], 20 * np.log10(g.min()), 100 * (g < 0.999).mean()

# ---------- material ----------
# Todo el programa queda parejo a -18 LUFS: la voz sube solo con ganancia y la
# música baja. Así el limitador de la voz casi no trabaja (picos sueltos).
TARGET = -18.0
SONG_LUFS, SPOT_LUFS, JINGLE_LUFS = TARGET, TARGET, TARGET
def find(prefix):
    """Busca el archivo por el comienzo del nombre (los acentos vienen en NFD)."""
    for d in (DL, MUS):
        hit = sorted(p for p in d.glob("*.mp3") if p.name.startswith(prefix))
        if hit: return hit[0]
    raise FileNotFoundError(prefix)

songs = {
    "01 Myriam Hernández – Huele a Peligro": find("Myriam Hern"),
    "02 Javiera Mena – Hasta la Verdad": find("Javiera Mena - Hasta"),
    "03 Saiko – Lo que Mereces": find("Lo Que Mereces"),
    "04 Ana Tijoux – 1977": find("Ana Tijoux - 1977"),
    "05 Nicole – Solo el Mar": find("Solo El Mar - Nicole"),
    "06 Princesa Alba – Tus Estaciones": find("Princesa Alba"),
    "07 Paloma Mami – Cosas de la Vida": find("Paloma Mami"),
    "08 Mamma Soul – Eternamente": find("MAMMA SOUL"),
    "09 Javiera y Los Imposibles – Y Esperaré": find("Y Esper"),
    "10 Francisca Valenzuela – Qué Sería": find("Que Ser"),
    "11 Camila Moreno – Millones": find("Camila Moreno - Millones"),
}
# Copia de las voces del día (en Descargas se pisan con los mismos nombres cada día).
VOCES = Path(__file__).resolve().parent / "voces"
voices = {k: VOCES / f"{k}.wav" for k in ["1", "4", "7", "10", "12", "15", "18"]}

print("cargando…", flush=True)
A, VL, VB = {}, {}, {}
for k, f in songs.items():
    A[k] = norm(trim(load(f), -50, 0.02), SONG_LUFS)
for k, f in voices.items():
    x = load(f)
    raw = meter.integrated_loudness(x)
    x, red, pct = limiter(x * 10 ** ((TARGET - raw) / 20))
    print(f"   voz {k:>3}: {raw:6.1f} → {TARGET} LUFS (+{TARGET-raw:.1f} dB); limitador máx {red:.1f} dB, activo {pct:.1f}% del tiempo")
    A["V" + k] = x
    VL[k] = meter.integrated_loudness(x)
    VB[k] = bounds(x, -45)  # dónde empieza/termina el habla (solo para ubicarla)
    print(f"   voz {k:>3}: {VL[k]:6.1f} LUFS, {len(x)/SR:6.2f}s, habla {VB[k][0]/SR:.2f}–{VB[k][1]/SR:.2f}s")
A["presentacion"] = norm(trim(load("Presentacion Viaje sin Rumbo.wav"), -55, 0.0), JINGLE_LUFS)
A["despedida"] = norm(trim(load("Despedida Viaje sin Rumbo.wav"), -55, 0.0), JINGLE_LUFS)
A["molen"] = norm(trim(load("Restaurante Molen.wav"), -55, 0.0), SPOT_LUFS)
A["valhalla"] = norm(trim(load("Valhala Gym.wav"), -55, 0.0), SPOT_LUFS)
BED = norm(trim(load(MUS / "Nicole - Viaje Infinito (Instrumental).mp3"), -50, 0.0), TARGET)

# ---------- línea de tiempo (dos pistas) ----------
music = np.zeros((s(66 * 60), 2), np.float32)
voice = np.zeros_like(music)
cues = []
t = 0.0

def put(buf, x, at, gain_db=0.0):
    a = s(at); buf[a:a + len(x)] += x * 10 ** (gain_db / 20)

def add(label, key, overlap=0.0, fin=0.0, fout=0.0, tipo=""):
    global t
    x = fade(A[key], fin, fout)
    start = max(0.0, t - overlap)
    put(music, x, start)
    cues.append((start, label, tipo))
    t = start + len(x) / SR

BED_PRE, BED_POST = 2.5, 1.2
PRE_LUFS = TARGET - 6.0   # cortina sola, antes y después de la voz
UNDER_REL = -18.5     # cortina bajo la voz: 18,5 dB debajo de esa locución

def locucion(k, label, tipo="LOCUCIÓN (con cortina)", bed_overlap=1.0, post=BED_POST):
    global t
    x = A["V" + k]; a, b = VB[k]
    bed_start = max(0.0, t - bed_overlap)
    speech_start = bed_start + bed_overlap + BED_PRE
    file_start = speech_start - a / SR          # el archivo entra completo, tal cual
    put(voice, x, file_start)
    v_start, v_end = speech_start, file_start + b / SR
    total = v_end + post + 2.0 - bed_start
    bed = BED[:s(total)]
    if len(bed) < s(total):
        bed = np.concatenate([bed, BED[:s(total) - len(bed)]])
    pre_db = PRE_LUFS - TARGET
    under_db = (VL[k] + UNDER_REL) - TARGET
    tt = np.arange(len(bed)) / SR + bed_start
    g = np.full(len(bed), pre_db)
    g = np.where(tt >= v_start - 0.4, np.interp(tt, [v_start - 0.4, v_start], [pre_db, under_db]), g)
    g = np.where(tt >= v_start, under_db, g)
    g = np.where(tt >= v_end, np.interp(tt, [v_end, v_end + 0.6], [under_db, pre_db]), g)
    fi = np.clip((tt - bed_start) / 1.5, 0, 1)
    fo = np.clip((bed_start + total - tt) / 2.0, 0, 1)
    put(music, bed * (10 ** (g / 20) * fi * fo)[:, None], bed_start)
    cues.append((bed_start, label, tipo))
    t = v_end + post

def song(label, **kw):
    add(label, label, overlap=0.3, tipo="MÚSICA", **kw)

# BLOQUE 1
add("CORTINA DE INICIO – Presentación Viaje sin Rumbo", "presentacion", tipo="CORTINA")
locucion("1", "1  Saludo, editorial y presentación de Myriam Hernández")
song("01 Myriam Hernández – Huele a Peligro")
song("02 Javiera Mena – Hasta la Verdad")
locucion("4", "4  Historia: Saiko")
song("03 Saiko – Lo que Mereces")
song("04 Ana Tijoux – 1977")
locucion("7", "7  Artista / disco: Nicole, Esperando Nada")
song("05 Nicole – Solo el Mar")
song("06 Princesa Alba – Tus Estaciones")
locucion("10", "10  MENCIONES (Molen, Valhalla)", tipo="MENCIONES (con cortina)")
t += 0.4
add("CORTE COMERCIAL – Frase Restaurante Molen", "molen", tipo="FRASE (sin cortina)")
t += 0.4
add("CORTE COMERCIAL – Frase Valhalla Gym", "valhalla", tipo="FRASE (sin cortina)")
t += 0.4
fin_b1 = t
# BLOQUE 2
locucion("12", "11 + 12  Regreso de tanda · Cumpleaños de Paloma Mami", bed_overlap=0.0)
song("07 Paloma Mami – Cosas de la Vida")
song("08 Mamma Soul – Eternamente")
locucion("15", "15  Algo que me guste: Javiera y Los Imposibles")
song("09 Javiera y Los Imposibles – Y Esperaré")
song("10 Francisca Valenzuela – Qué Sería")
locucion("18", "18 + 19  Cierre y MENCIONES finales", tipo="LOCUCIÓN + MENCIONES (con cortina)")
song("11 Camila Moreno – Millones")
add("CORTINA DE CIERRE – Despedida Viaje sin Rumbo", "despedida", overlap=0.5, fin=0.5, tipo="CORTINA")

n = s(t); music, voice = music[:n], voice[:n]
# limitador de picos SOLO en la pista de música/cortinas (la voz queda intacta)
lim = 10 ** (-1.5 / 20); k = lim * 0.85
for i in range(0, n, s(30)):
    c = music[i:i + s(30)]
    pk = np.abs(c); over = pk > k
    if over.any():
        c[over] = np.sign(c[over]) * (k + (lim - k) * np.tanh((pk[over] - k) / (lim - k)))
mix = music + voice

total = n / SR
print(f"\nDURACIÓN TOTAL: {int(total // 60)}:{total % 60:04.1f}  (bloque 1 hasta {int(fin_b1//60)}:{fin_b1%60:04.1f})")
mix = mix.astype(np.float32); music = music.astype(np.float32); voice = voice[:, 0].astype(np.float32)
print(f"Mezcla: pico {20*np.log10(np.abs(mix).max()):.2f} dBFS")

name = "Viaje sin Rumbo - 11-11-2026 - Reinas del Pop"
sf.write(OUT / f"{name}.wav", mix, SR, subtype="PCM_24")
sf.write(OUT / f"{name} - PISTA VOZ.wav", voice, SR, subtype="PCM_24")
sf.write(OUT / f"{name} - PISTA MUSICA Y CORTINAS.wav", music, SR, subtype="PCM_24")
subprocess.run([FF, "-v", "error", "-y", "-i", str(OUT / f"{name}.wav"), "-b:a", "320k",
                str(OUT / f"{name}.mp3")], check=True)

fmt = lambda x: f"{int(x // 60):02d}:{int(x % 60):02d}"
lines = [f"VIAJE SIN RUMBO – MIÉRCOLES 11-11-2026 – REINAS DEL POP: LAS MUJERES DE LA MÚSICA CHILENA (duración {fmt(total)})", ""]
for st, lab, tipo in sorted(cues):
    lines.append(f"{fmt(st)}   {tipo:<36} {lab}")
lines.append(f"{fmt(total)}   FIN")
(OUT / "minutaje.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))

