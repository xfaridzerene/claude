# -*- coding: utf-8 -*-
import subprocess, os

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
ROOT = r"C:\Users\farid\Desktop\EMERGE FM\La Ciudad de la Furia\FRASES"
OUT = r"C:\Users\farid\Desktop\claude code\furia_audio\editadas_v4"
os.makedirs(OUT, exist_ok=True)

# gentler base: less bass/treble boost, shorter/quieter echo, much lighter stereo widening
BASE = "bass=g=2:f=100:w=0.5,treble=g=1.8:f=7000:w=0.5,aecho=0.9:0.4:35|55:0.15|0.10,extrastereo=m=1.1"

def build_filter(hero_windows):
    graph = [f"[0:a]{BASE},apad=pad_dur=0.6[coloured]"]
    n = len(hero_windows)
    split_labels = "".join(("[dry]" if i == 0 else f"[w{i}]") for i in range(n + 1))
    graph.append(f"[coloured]asplit={n + 1}{split_labels}")

    mix_inputs = ["[dry]"]
    for i, (a, b) in enumerate(hero_windows, start=1):
        delay_ms = int(round(a * 1000))
        # subtler accent echo, just on the hero word, well below the dry signal
        graph.append(
            f"[w{i}]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,"
            f"aecho=0.85:0.5:70|120:0.22|0.15,volume=0.32,"
            f"adelay={delay_ms}|{delay_ms}[wet{i}]"
        )
        mix_inputs.append(f"[wet{i}]")

    graph.append("".join(mix_inputs) + f"amix=inputs={len(mix_inputs)}:duration=longest:dropout_transition=0[mixed]")
    # more headroom: lower integrated target, more true-peak margin, gentler limiter
    graph.append("[mixed]loudnorm=I=-19:TP=-2.0:LRA=9,alimiter=limit=0.9[out]")
    return ";".join(graph)

examples = [
    ("01 - Hacemos una pausa y ya vuelve Kaco López con", "01 - Frase.mp3", [(2.20, 2.88), (3.90, 5.36)]),
    ("07 - La tarde es más entretenida escuchando La", "07 - Frase.mp3", [(2.90, 4.62)]),
    ("18 - Fueron dos horas de música, diversión y", "18 - Frase.mp3", [(5.52, 6.26), (10.28, 12.18)]),
]

for folder, fname, heroes in examples:
    src = os.path.join(ROOT, folder, fname)
    out_name = fname.replace("Frase", "Frase_EDITADA_v4")
    out_path = os.path.join(OUT, out_name)
    fc = build_filter(heroes)
    cmd = [FFMPEG, "-y", "-i", src, "-filter_complex", fc, "-map", "[out]",
           "-acodec", "libmp3lame", "-q:a", "2", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR", out_path)
        print(r.stderr[-1500:])
    else:
        print("OK", out_path)
