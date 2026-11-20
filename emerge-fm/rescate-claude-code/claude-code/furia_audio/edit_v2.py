# -*- coding: utf-8 -*-
import subprocess, os

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
ROOT = r"C:\Users\farid\Desktop\EMERGE FM\La Ciudad de la Furia\FRASES"
OUT = r"C:\Users\farid\Desktop\claude code\furia_audio\editadas_v2"
os.makedirs(OUT, exist_ok=True)

# base "color" - lighter than before since the hero windows add their own extra boost on top
BASE = "bass=g=2.5:f=110:w=0.6,treble=g=2:f=7000:w=0.6,extrastereo=m=1.15"

def build_filter(hero_windows, lead_in=0.35):
    """hero_windows: list of (start, end) in seconds to emphasize."""
    parts = [BASE]
    for (a, b) in hero_windows:
        dip_a = max(0.0, a - lead_in)
        # tiny pull-back right before the hero word, then lift during it
        parts.append(f"volume=0.90:enable='between(t,{dip_a:.3f},{a:.3f})'")
        parts.append(f"volume=1.18:enable='between(t,{a:.3f},{b:.3f})'")
        parts.append(f"treble=g=3:f=6500:w=0.5:enable='between(t,{a:.3f},{b:.3f})'")
        parts.append(f"bass=g=2:f=100:w=0.5:enable='between(t,{a:.3f},{b:.3f})'")
    colored = ",".join(parts)

    n_heroes = len(hero_windows)
    graph = [f"[0:a]{colored},apad=pad_dur=0.6[coloured]"]
    split_labels = "".join(f"[dry]" if i == 0 else f"[w{i}]" for i in range(n_heroes + 1))
    graph.append(f"[coloured]asplit={n_heroes + 1}{split_labels}")

    mix_inputs = ["[dry]"]
    for i, (a, b) in enumerate(hero_windows, start=1):
        delay_ms = int(round(a * 1000))
        graph.append(
            f"[w{i}]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,"
            f"aecho=0.8:0.6:40|70:0.22|0.14,volume=0.38,"
            f"adelay={delay_ms}|{delay_ms}[wet{i}]"
        )
        mix_inputs.append(f"[wet{i}]")

    graph.append(
        "".join(mix_inputs)
        + f"amix=inputs={len(mix_inputs)}:duration=longest:dropout_transition=0[mixed]"
    )
    graph.append("[mixed]loudnorm=I=-17:TP=-1.3:LRA=11,alimiter=limit=0.95[out]")
    return ";".join(graph)

examples = [
    ("01 - Hacemos una pausa y ya vuelve Kaco López con", "01 - Frase.mp3", [(2.20, 2.88), (3.90, 5.36)]),
    ("07 - La tarde es más entretenida escuchando La", "07 - Frase.mp3", [(2.90, 4.62)]),
    ("18 - Fueron dos horas de música, diversión y", "18 - Frase.mp3", [(5.52, 6.26), (10.28, 12.18)]),
]

for folder, fname, heroes in examples:
    src = os.path.join(ROOT, folder, fname)
    out_name = fname.replace("Frase", "Frase_EDITADA_v2")
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
