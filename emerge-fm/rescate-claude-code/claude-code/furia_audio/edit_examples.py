# -*- coding: utf-8 -*-
import subprocess, os

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
ROOT = r"C:\Users\farid\Desktop\EMERGE FM\La Ciudad de la Furia\FRASES"
OUT = r"C:\Users\farid\Desktop\claude code\furia_audio\editadas"
os.makedirs(OUT, exist_ok=True)

# lighter "secondary promo" chain: subtle smile EQ, short room reverb, mild stereo width,
# normalize a touch under the main presentation's loudness, gentle limiter for safety.
FILTER = (
    "bass=g=4:f=110:w=0.6,"
    "treble=g=3:f=7000:w=0.6,"
    "aecho=0.85:0.55:45|70:0.18|0.12,"
    "extrastereo=m=1.3,"
    "loudnorm=I=-18:TP=-1.5:LRA=11,"
    "alimiter=limit=0.95"
)

examples = [
    ("01 - Hacemos una pausa y ya vuelve Kaco López con", "01 - Frase.mp3"),
    ("07 - La tarde es más entretenida escuchando La", "07 - Frase.mp3"),
    ("10 - De lunes a viernes te invitamos a conectarte", "10 - Frase.mp3"),
]

for folder, fname in examples:
    src = os.path.join(ROOT, folder, fname)
    out_name = fname.replace("Frase", "Frase_EDITADA")
    out_path = os.path.join(OUT, out_name)
    cmd = [FFMPEG, "-y", "-i", src, "-af", FILTER, "-acodec", "libmp3lame", "-q:a", "2", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR", out_path, r.stderr[-800:])
    else:
        print("OK", out_path)
