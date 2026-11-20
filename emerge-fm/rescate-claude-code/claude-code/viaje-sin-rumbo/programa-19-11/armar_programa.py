# Viaje sin Rumbo – jueves 19-11-2026 – "El ritmo" (sin pauta: orden sacado de las locuciones). Entrega solo la mezcla final.
# Correr con: C:\Users\farid\audio-env\Scripts\python.exe armar_programa.py
#
# Reglas (iguales a los programas anteriores):
#  - La VOZ se nivela solo con ganancia (sin EQ, compresor ni limpieza) y un
#    limitador con anticipación para los picos sueltos. Todo parejo a -18 LUFS.
#  - LOCUCIÓN y MENCIONES van sobre la cortina de fondo (Nicole – Viaje Infinito).
#  - FRASES (Molen, Valhalla) van solas, sin cortina, en el corte comercial.
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR = 48000
DL = Path(r"C:\Users\farid\Downloads")
MUS = DL / "Música Vale (normalizada)"
FF = r"C:\Users\farid\audio-env\bin\ffmpeg.exe"
HERE = Path(__file__).resolve().parent
OUT = HERE / "salida"
OUT.mkdir(exist_ok=True)
meter = pyln.Meter(SR)

def load(path):
    path = path if isinstance(path, Path) else DL / path
    raw = subprocess.run([FF, "-v", "error", "-i", str(path), "-map", "0:a:0",
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

def limiter(x, ceil_db=-1.0, look=0.005, hold=0.020, smooth=0.030):
    """Limitador con anticipación: solo baja la ganancia en los picos que pasan el techo."""
    thr = 10 ** (ceil_db / 20)
    pk = np.abs(x).max(axis=1)
    need = np.minimum(1.0, thr / np.maximum(pk, 1e-9))
    g = minimum_filter1d(need, s(2 * look + hold))
    g = uniform_filter1d(g, s(smooth))
    g = np.minimum(g, minimum_filter1d(need, s(look) * 2 + 1))
    return x * g[:, None], 20 * np.log10(g.min()), 100 * (g < 0.999).mean()

TARGET = -18.0

def find(prefix):
    """Busca por el comienzo del nombre (los acentos vienen en NFD). Si hay varios, el más reciente."""
    for d in (DL, MUS):
        hit = sorted((p for p in d.glob("*.mp3") if p.name.startswith(prefix)),
                     key=lambda p: p.stat().st_mtime, reverse=True)
        if hit: return hit[0]
    raise FileNotFoundError(prefix)

def newest(pattern):
    hit = sorted(DL.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not hit: raise FileNotFoundError(pattern)
    return hit[0]

songs = {
    "01 Álex Anwandter – Tormenta": find("Alex Anwandter - Tormenta"),
    "02 Saiko – Debilidad": find("Debilidad - Saiko"),
    "03 Supernova – Toda la Noche": find("Supernova - Toda la Noche"),
    "04 Gepe – Bacán tu Casa": newest("Gepe - Bac*n tu Casa*.mp3"),
    "05 Tiro de Gracia – Corsario Universal": find("Tiro De Gracia - Corsario"),
    "06 Pettinellis – Un Hombre Muerto en el Ring": find("Pettinellis - Un Hombre"),
    "07 Los Jaivas – Hijos de la Tierra": find("Los Jaivas - Hijos de la Tierra"),
    "08 Gondwana – Mi Princesa": find("Gondwana - Mi Princesa"),
    "09 Los Miserables – Chile no es una Postal": find("Los Miserables - Chile No Es"),
    "10 Cidtronyck – Slowly": find("Cidtronyck - Slowly"),
    "11 Pedropiedra – Pasajero": find("Pasajero - Pedropiedra"),
    "12 La Floripondio – Y es de Día": find("La Floripondio - Y es de d"),
    "13 Papa Negro – Wokman": find("PapaNegro - Wokman"),
}
# Copia de las voces del día (en Descargas se pisan con los mismos nombres cada día).
VOCES = HERE / "voces"
voices = {k: VOCES / f"{k}.wav" for k in ["1", "4", "7", "10", "12", "15", "18", "21"]}

if __name__ == "__main__" and "--check" in __import__("sys").argv:
    for k, v in songs.items(): print(k, "->", v.name)
    raise SystemExit

print("cargando…", flush=True)
A, VL, VB = {}, {}, {}
def cut_head(x, rel_db, win, fin=0.3):
    """Corta el comienzo hasta la primera ventana cuyo RMS queda a rel_db de la
    sonoridad de la canción (silencio o ruido casi mudo al inicio)."""
    L = meter.integrated_loudness(x); w = s(win)
    m = (x[:s(60)] ** 2).mean(axis=1)              # basta con el primer minuto
    r = 10 * np.log10(uniform_filter1d(m, w) + 1e-12)
    i = int(np.argmax(r > L + rel_db))
    a = max(0, i - s(0.05))
    return fade(x[a:], fin=fin if a > 0 else 0.0), a / SR

for k, f in songs.items():
    raw = load(f)
    x = trim(raw, -50, 0.02)                        # silencio digital al inicio/final
    cut = (len(raw) - len(x)) / SR                  # (aprox., incluye el final)
    hs = (bounds(raw, -50)[0]) / SR                  # silencio digital al inicio
    te = (len(raw) - bounds(raw, -50)[1]) / SR       # silencio digital al final
    x, c = cut_head(x, -35, 1.0, fin=0.3)            # intro casi muda (aire muerto)
    y, c2 = cut_head(x[::-1].copy(), -35, 1.0, fin=0.0)   # cola casi muda
    x = fade(y[::-1].copy(), fout=1.0 if c2 > 0 else 0.0)
    print(f"   {k}: inicio −{hs + c:.1f}s (silencio {hs:.1f} + casi mudo {c:.1f}) · final −{te + c2:.1f}s (silencio {te:.1f} + casi mudo {c2:.1f})")
    A[k] = norm(x, TARGET).astype(np.float32)
for k, f in voices.items():
    x = load(f)
    raw = meter.integrated_loudness(x)
    x, red, pct = limiter(x * 10 ** ((TARGET - raw) / 20))
    print(f"   voz {k:>3}: {raw:6.1f} → {TARGET} LUFS (+{TARGET-raw:.1f} dB); limitador máx {red:.1f} dB, activo {pct:.1f}% del tiempo; {len(x)/SR:.1f}s")
    VL[k] = meter.integrated_loudness(x)
    VB[k] = bounds(x, -45)
    A["V" + k] = x.astype(np.float32)
A["presentacion"] = norm(trim(load("Presentacion Viaje sin Rumbo.wav"), -55, 0.0), TARGET).astype(np.float32)
A["despedida"] = norm(trim(load("Despedida Viaje sin Rumbo.wav"), -55, 0.0), TARGET).astype(np.float32)
A["molen"] = norm(trim(load("Restaurante Molen.wav"), -55, 0.0), TARGET).astype(np.float32)
A["valhalla"] = norm(trim(load("Valhala Gym.wav"), -55, 0.0), TARGET).astype(np.float32)
BED = norm(trim(load(MUS / "Nicole - Viaje Infinito (Instrumental).mp3"), -50, 0.0), TARGET).astype(np.float32)

# ---------- línea de tiempo (dos pistas internas, se entrega solo la mezcla) ----------
music = np.zeros((s(68 * 60), 2), np.float32)
voice = np.zeros_like(music)
cues = []
t = 0.0

def put(buf, x, at, gain_db=0.0):
    a = s(at); buf[a:a + len(x)] += x * np.float32(10 ** (gain_db / 20))

def add(label, key, overlap=0.0, fin=0.0, fout=0.0, tipo=""):
    global t
    x = fade(A[key], fin, fout)
    start = max(0.0, t - overlap)
    put(music, x, start)
    cues.append((start, label, tipo))
    t = start + len(x) / SR

BED_PRE, BED_POST = 2.5, 1.2
PRE_LUFS = TARGET - 6.0   # cortina sola, antes y después de la voz
UNDER_REL = -18.5         # cortina bajo la voz: 18,5 dB debajo de esa locución

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
    put(music, bed * (10 ** (g / 20) * fi * fo).astype(np.float32)[:, None], bed_start)
    cues.append((bed_start, label, tipo))
    t = v_end + post

def song(label, **kw):
    add(label, label, overlap=0.3, tipo="MÚSICA", **kw)

# BLOQUE 1
add("CORTINA DE INICIO – Presentación Viaje sin Rumbo", "presentacion", tipo="CORTINA")
locucion("1", "1  Saludo, editorial y presentación: El ritmo (cumpleaños de Juanita Parra)")
song("01 Álex Anwandter – Tormenta")
song("02 Saiko – Debilidad")
locucion("4", "4  Historia: Supernova")
song("03 Supernova – Toda la Noche")
song("04 Gepe – Bacán tu Casa")
locucion("7", "7  Artista / disco: Tiro de Gracia, Ser Humano")
song("05 Tiro de Gracia – Corsario Universal")
song("06 Pettinellis – Un Hombre Muerto en el Ring")
locucion("10", "10  MENCIONES (Molen, Valhalla)", tipo="MENCIONES (con cortina)")
t += 0.4
add("CORTE COMERCIAL – Frase Restaurante Molen", "molen", tipo="FRASE (sin cortina)")
t += 0.4
add("CORTE COMERCIAL – Frase Valhalla Gym", "valhalla", tipo="FRASE (sin cortina)")
t += 0.4
fin_b1 = t
# BLOQUE 2
locucion("12", "11 + 12  Regreso de tanda · Especial: Juanita Parra y Los Jaivas", bed_overlap=0.0)
song("07 Los Jaivas – Hijos de la Tierra")
song("08 Gondwana – Mi Princesa")
locucion("15", "15  Dato / curiosidad: Los Miserables")
song("09 Los Miserables – Chile no es una Postal")
song("10 Cidtronyck – Slowly")
locucion("18", "18  Algo que me guste: Pedropiedra")
song("11 Pedropiedra – Pasajero")
song("12 La Floripondio – Y es de Día")
locucion("21", "21  Cierre y MENCIONES finales", tipo="LOCUCIÓN + MENCIONES (con cortina)")
song("13 Papa Negro – Wokman")
add("CORTINA DE CIERRE – Despedida Viaje sin Rumbo", "despedida", overlap=0.5, fin=0.5, tipo="CORTINA")

n = s(t); music, voice = music[:n], voice[:n]
# limitador de picos solo en música/cortinas (la voz ya trae el suyo)
lim = 10 ** (-1.5 / 20); kk = lim * 0.85
for i in range(0, n, s(30)):
    c = music[i:i + s(30)]
    pk = np.abs(c); over = pk > kk
    if over.any():
        c[over] = np.sign(c[over]) * (kk + (lim - kk) * np.tanh((pk[over] - kk) / (lim - kk)))
music += voice
mix = music; del voice

total = n / SR
print(f"\nDURACIÓN TOTAL: {int(total // 60)}:{total % 60:04.1f}  (bloque 1 hasta {int(fin_b1//60)}:{fin_b1%60:04.1f})")
print(f"Mezcla: pico {20*np.log10(np.abs(mix).max()):.2f} dBFS")

name = "Viaje sin Rumbo - 19-11-2026 - El Ritmo"
sf.write(OUT / f"{name}.wav", mix, SR, subtype="PCM_24")
subprocess.run([FF, "-v", "error", "-y", "-i", str(OUT / f"{name}.wav"), "-b:a", "320k",
                str(OUT / f"{name}.mp3")], check=True)

fmt = lambda x: f"{int(x // 60):02d}:{int(x % 60):02d}"
lines = [f"VIAJE SIN RUMBO – JUEVES 19-11-2026 – EL RITMO (CUMPLEAÑOS DE JUANITA PARRA) (duración {fmt(total)})", ""]
for st, lab, tipo in sorted(cues):
    lines.append(f"{fmt(st)}   {tipo:<36} {lab}")
lines.append(f"{fmt(total)}   FIN")
(OUT / "minutaje.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
