# Arma el programa Viaje sin Rumbo del lunes 09-11-2026 según la pauta.
# Correr con: C:\Users\farid\audio-env\Scripts\python.exe armar_programa.py
#
# Reglas:
#  - LOCUCIÓN y MENCIONES (las lee Valentina) van sobre la cortina de fondo
#    (Nicole - Viaje Infinito, instrumental), con colchón antes y después.
#  - FRASES (cuñas comerciales grabadas: Molen, Valhalla) van solas, sin cortina,
#    en el corte comercial.
#  - Canciones enteras, sin silencios al inicio ni al final, empalmadas.
import subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf
import pyloudnorm as pyln

SR = 48000
DL = Path(r"C:\Users\farid\Downloads")
FF = r"C:\Users\farid\audio-env\bin\ffmpeg.exe"
OUT = Path(__file__).resolve().parent / "salida"
OUT.mkdir(exist_ok=True)
meter = pyln.Meter(SR)

def load(name):
    raw = subprocess.run([FF, "-v", "error", "-i", str(DL / name), "-map", "0:a:0",
                          "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)

def trim(x, thr_db=-48, pad=0.05):
    env = np.abs(x).max(axis=1)
    win = int(0.02 * SR)
    env = np.convolve(env, np.ones(win) / win, "same")
    idx = np.where(env > 10 ** (thr_db / 20))[0]
    a = max(0, idx[0] - int(pad * SR)); b = min(len(x), idx[-1] + int(pad * SR))
    return x[a:b]

def norm(x, lufs):
    l = meter.integrated_loudness(x)
    return x * 10 ** ((lufs - l) / 20)

def fade(x, fin=0.0, fout=0.0):
    x = x.copy()
    if fin:  n = int(fin * SR);  x[:n] *= np.linspace(0, 1, n)[:, None]
    if fout: n = int(fout * SR); x[-n:] *= np.linspace(1, 0, n)[:, None]
    return x

def s(t): return int(round(t * SR))

# ---------- material ----------
SONG_LUFS, VOICE_LUFS, SPOT_LUFS, JINGLE_LUFS = -14.0, -14.5, -14.0, -14.0
songs = {
    "01 Makiza – La Rosa de los Vientos": "Makiza - La Rosa de los Vientos - Seo2.mp3",
    "02 Ases Falsos – Fuerza Especial": "Fuerza Especial - Ases Falsos.mp3",
    "03 Los Prisioneros – Tren al Sur": "Los Prisioneros - Tren Al Sur (Audio) - LosPrisionerosVEVO.mp3",
    "04 Upa! – Cuando Vuelvas": "upa! - cuando vuelvas - centralstone.mp3",
    "05 Lucybell – Cuando Respiro en tu Boca": "Lucybell - Cuando Respiro En Tu Boca (Audio) - LucybellVEVO.mp3",
    "06 Los Bunkers – Noviembre": "Los Bunkers - Noviembre (Lyric Video) - Los Bunkers.mp3",
    "07 Denise Rosenthal – Revolution": "Denise Rosenthal- Revolution [VIDEO OFICIAL] - DeniseRosenthal.mp3",
    "08 Mon Laferte – Flor de Amapola": "Mon Laferte - Flor de amapola ft. Mariel Mariel - Mon Laferte.mp3",
    "09 Pedropiedra – Inteligencia Dormida": "Pedropiedra - Inteligencia Dormida - selloovejanegra.mp3",
    "10 Javiera Mena – Al Siguiente Nivel": "Javiera Mena - Al Siguiente Nivel (Audio Oficial) - Javiera Mena.mp3",
    "11 Joe Vasconcellos – Mágico": "Joe Vasconcellos - Mágico (Audio) - JoeVasconcellosVEVO.mp3",
}
V = lambda n: f"{n}-esv2-50p-bg-10p-music-10p.wav"
voices = {
    "1": V("1.  SALUDO, EDITORIAL Y PRENTACION "), "1.1": V("1.1 CANCION"),
    "4": V("4. LOCUCIÓN"), "7": V("7. LOCUCIÓN"), "10": V("10.MENCIONES"),
    "12": V("12. LOCUCION"), "15": V("15. LOCUCION"), "18": V("18.LOCUCION Y 19. MENCIONES"),
}

print("cargando…", flush=True)
A = {}
for k, f in songs.items():
    A[k] = norm(trim(load(f), -50, 0.02), SONG_LUFS)
for k, f in voices.items():
    A["V" + k] = norm(trim(load(f), -45, 0.10), VOICE_LUFS)
A["presentacion"] = norm(trim(load("Presentacion Viaje sin Rumbo.wav"), -55, 0.0), JINGLE_LUFS)
A["despedida"] = norm(trim(load("Despedida Viaje sin Rumbo.wav"), -55, 0.0), JINGLE_LUFS)
A["molen"] = norm(trim(load("Restaurante Molen.wav"), -55, 0.0), SPOT_LUFS)
A["valhalla"] = norm(trim(load("Valhala Gym.wav"), -55, 0.0), SPOT_LUFS)
BED = norm(trim(load("Nicole - Viaje Infinito (Instrumental).mp3"), -50, 0.0), -14.0)

# ---------- línea de tiempo ----------
prog = np.zeros((s(66 * 60), 2))
cues = []
t = 0.0  # cursor en segundos

def put(x, at, gain_db=0.0):
    a = s(at); prog[a:a + len(x)] += x * 10 ** (gain_db / 20)

def add(label, key, overlap=0.0, fin=0.0, fout=0.0, tipo=""):
    global t
    x = fade(A[key], fin, fout)
    start = max(0.0, t - overlap)
    put(x, start)
    cues.append((start, label, tipo))
    t = start + len(x) / SR

BED_PRE, BED_POST, PRE_DB, UNDER_DB = 2.5, 1.2, -9.0, -19.0
bed_pos = [0.0]

def locucion(items, label, tipo="LOCUCIÓN (con cortina)", bed_overlap=1.0, gap=0.7):
    """items: claves de voz que se leen seguidas sobre la misma cortina."""
    global t
    bed_start = max(0.0, t - bed_overlap)
    v_start = bed_start + bed_overlap + BED_PRE
    v_t = v_start
    spans = []
    for i, k in enumerate(items):
        x = A["V" + k]
        put(x, v_t)
        spans.append((v_t, v_t + len(x) / SR))
        v_t += len(x) / SR + (gap if i < len(items) - 1 else 0)
    v_end = v_t
    total = v_end + BED_POST + 2.0 - bed_start
    off = s(bed_pos[0])
    bed = BED[off:off + s(total)]
    if len(bed) < s(total):
        bed = np.concatenate([bed, BED[:s(total) - len(bed)]])
    bed_pos[0] = 0.0  # la cortina parte siempre desde arriba
    tt = np.arange(len(bed)) / SR + bed_start
    g = np.full(len(bed), PRE_DB)
    g = np.where(tt >= v_start - 0.4, np.interp(tt, [v_start - 0.4, v_start], [PRE_DB, UNDER_DB]), g)
    g = np.where(tt >= v_start, UNDER_DB, g)
    g = np.where(tt >= v_end, np.interp(tt, [v_end, v_end + 0.6], [UNDER_DB, PRE_DB]), g)
    gain = 10 ** (g / 20)
    fi = np.clip((tt - bed_start) / 1.5, 0, 1)
    fo = np.clip((bed_start + total - tt) / 2.0, 0, 1)
    put(bed * (gain * fi * fo)[:, None], bed_start)
    cues.append((bed_start, label, tipo))
    t = v_end + BED_POST  # la canción entra mientras la cortina se va

# BLOQUE 1
add("CORTINA DE INICIO – Presentación Viaje sin Rumbo", "presentacion", tipo="CORTINA")
locucion(["1", "1.1"], "1 + 1.1  Saludo, manifiesto y presentación de Makiza")
add("01 Makiza – La Rosa de los Vientos", "01 Makiza – La Rosa de los Vientos", overlap=0.3, tipo="MÚSICA")
add("02 Ases Falsos – Fuerza Especial", "02 Ases Falsos – Fuerza Especial", overlap=0.3, tipo="MÚSICA")
locucion(["4"], "4  Historia de la canción: Tren al Sur")
add("03 Los Prisioneros – Tren al Sur", "03 Los Prisioneros – Tren al Sur", overlap=0.3, tipo="MÚSICA")
add("04 Upa! – Cuando Vuelvas", "04 Upa! – Cuando Vuelvas", overlap=0.3, tipo="MÚSICA")
locucion(["7"], "7  Artista / disco: Lucybell, Peces")
add("05 Lucybell – Cuando Respiro en tu Boca", "05 Lucybell – Cuando Respiro en tu Boca", overlap=0.3, tipo="MÚSICA")
add("06 Los Bunkers – Noviembre", "06 Los Bunkers – Noviembre", overlap=0.3, tipo="MÚSICA")
locucion(["10"], "10  MENCIONES (Molen, Valhalla) y salida a tanda", tipo="MENCIONES (con cortina)")
t += 0.4
add("CORTE COMERCIAL – Frase Restaurante Molen", "molen", tipo="FRASE (sin cortina)")
t += 0.4
add("CORTE COMERCIAL – Frase Valhalla Gym", "valhalla", tipo="FRASE (sin cortina)")
t += 0.4
fin_b1 = t
# BLOQUE 2
locucion(["12"], "11 + 12  Regreso de tanda · Especial Denise Rosenthal", bed_overlap=0.0)
add("07 Denise Rosenthal – Revolution", "07 Denise Rosenthal – Revolution", overlap=0.3, tipo="MÚSICA")
add("08 Mon Laferte – Flor de Amapola", "08 Mon Laferte – Flor de Amapola", overlap=0.3, tipo="MÚSICA")
locucion(["15"], "15  Algo que me guste: Pedropiedra")
add("09 Pedropiedra – Inteligencia Dormida", "09 Pedropiedra – Inteligencia Dormida", overlap=0.3, tipo="MÚSICA")
add("10 Javiera Mena – Al Siguiente Nivel", "10 Javiera Mena – Al Siguiente Nivel", overlap=0.3, tipo="MÚSICA")
locucion(["18"], "18 + 19  Cierre y MENCIONES finales", tipo="LOCUCIÓN + MENCIONES (con cortina)")
add("11 Joe Vasconcellos – Mágico", "11 Joe Vasconcellos – Mágico", overlap=0.3, tipo="MÚSICA")
add("CORTINA DE CIERRE – Despedida Viaje sin Rumbo", "despedida", overlap=0.5, fin=0.5, tipo="CORTINA")

prog = prog[:s(t)]
# limitador simple de picos a -1 dBFS (sin tocar el resto)
lim = 10 ** (-1 / 20)
pk = np.abs(prog)
over = pk > lim * 0.9
if over.any():
    k = lim * 0.9
    prog = np.where(over, np.sign(prog) * (k + (lim - k) * np.tanh((pk - k) / (lim - k))), prog)

total = len(prog) / SR
print(f"\nDURACIÓN TOTAL: {int(total // 60)}:{total % 60:04.1f}  (bloque 1 hasta {int(fin_b1//60)}:{fin_b1%60:04.1f})")
print(f"Loudness integrado: {meter.integrated_loudness(prog):.1f} LUFS, pico {20*np.log10(np.abs(prog).max()):.2f} dBFS")

name = "Viaje sin Rumbo - 09-11-2026 - Programa 1"
sf.write(OUT / f"{name}.wav", prog.astype(np.float32), SR, subtype="PCM_24")
subprocess.run([FF, "-v", "error", "-y", "-i", str(OUT / f"{name}.wav"), "-b:a", "320k",
                str(OUT / f"{name}.mp3")], check=True)

fmt = lambda x: f"{int(x // 60):02d}:{int(x % 60):02d}"
lines = [f"VIAJE SIN RUMBO – LUNES 09-11-2026 – PROGRAMA 1 (duración {fmt(total)})", ""]
for st, lab, tipo in sorted(cues):
    lines.append(f"{fmt(st)}   {tipo:<36} {lab}")
lines.append(f"{fmt(total)}   FIN")
(OUT / "minutaje.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
