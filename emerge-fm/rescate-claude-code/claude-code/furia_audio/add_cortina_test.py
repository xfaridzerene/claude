# -*- coding: utf-8 -*-
import subprocess, os, re

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
MUSIC = r"C:\Users\farid\Downloads\maqueta 1 cortina emerge solo musica.mp3.mpeg"
ROOT = r"E:\EMERGE FM 1\FRASES"
OUT_DIR = r"C:\Users\farid\Desktop\claude code\furia_audio\pruebas_cortina"
os.makedirs(OUT_DIR, exist_ok=True)

SAMPLES = [
    (r"01 - Estás escuchando Emerge FM, ciento", "01 - Toma 1 (ecualizada).mp3"),
    (r"09 - Llévanos contigo… Escúchanos en línea", "09 - Toma 1 (ecualizada).mp3"),
    (r"13 - Música, noticias y programas en vivo,", "13 - Toma 1 (ecualizada).mp3"),
]

def get_duration(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)

for folder, fname in SAMPLES:
    voice = os.path.join(ROOT, folder, fname)
    dur = get_duration(voice)
    fade_start = max(0.0, dur - 1.0)
    fc = (
        f"[1:a]volume=0.3,afade=t=out:st={fade_start:.3f}:d=1[music];"
        f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mixed];"
        f"[mixed]alimiter=limit=0.95[out]"
    )
    out_name = fname.replace("(ecualizada)", "(ecualizada + cortina)")
    out_path = os.path.join(OUT_DIR, f"{folder[:2]} - {out_name}")
    cmd = [FFMPEG, "-y", "-i", voice, "-stream_loop", "-1", "-i", MUSIC,
           "-filter_complex", fc, "-map", "[out]",
           "-acodec", "libmp3lame", "-q:a", "2", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR", out_path)
        print(r.stderr[-1200:])
    else:
        print("OK", out_path, "dur:", dur)
