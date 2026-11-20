# -*- coding: utf-8 -*-
import subprocess, os, re

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
MUSIC = r"C:\Users\farid\Downloads\maqueta 1 cortina emerge solo musica.mp3.mpeg"
FOLDER = r"E:\EMERGE FM 1\FRASES\13 - Música, noticias y programas en vivo,"
src = os.path.join(FOLDER, "13 - Toma 1.mp3")
out_eq = os.path.join(FOLDER, "13 - Toma 1 (ecualizada).mp3")
out_cortina = os.path.join(FOLDER, "13 - Toma 1 (ecualizada + cortina).mp3")

BASE = "bass=g=2:f=100:w=0.5,treble=g=1.8:f=7000:w=0.5,aecho=0.9:0.4:35|55:0.15|0.10,extrastereo=m=1.1"
hero_windows = [(4.9, 5.86), (7.14, 8.38), (12.22, 12.46)]
# previous trim_end (16.65) only removed a late stray burst but left ~4s of dead
# air after "emerge." (ends at 12.46) before it -- that's the "se corta / no
# termina bien" the phrase ended up sounding like. Cut shortly after the last
# word instead, keeping a touch of natural reverb tail.
TRIM_END = 13.16

graph = [f"[0:a]atrim=start=0:end={TRIM_END},asetpts=PTS-STARTPTS,{BASE},apad=pad_dur=0.6[coloured]"]
n = len(hero_windows)
split_labels = "".join(("[dry]" if i == 0 else f"[w{i}]") for i in range(n + 1))
graph.append(f"[coloured]asplit={n + 1}{split_labels}")
mix_inputs = ["[dry]"]
for i, (a, b) in enumerate(hero_windows, start=1):
    delay_ms = int(round(a * 1000))
    graph.append(
        f"[w{i}]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,"
        f"aecho=0.85:0.5:70|120:0.22|0.15,volume=0.32,"
        f"adelay={delay_ms}|{delay_ms}[wet{i}]"
    )
    mix_inputs.append(f"[wet{i}]")
graph.append("".join(mix_inputs) + f"amix=inputs={len(mix_inputs)}:duration=longest:dropout_transition=0[mixed]")
graph.append("[mixed]loudnorm=I=-19:TP=-2.0:LRA=9,alimiter=limit=0.9,adelay=2000|2000[out]")
fc = ";".join(graph)

cmd = [FFMPEG, "-y", "-i", src, "-filter_complex", fc, "-map", "[out]",
       "-acodec", "libmp3lame", "-q:a", "2", out_eq]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("ERROR eq"); print(r.stderr[-1500:]); raise SystemExit(1)
print("OK eq:", out_eq)

def get_duration(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)

dur = get_duration(out_eq)
fade_start = max(0.0, dur - 1.0)
fc2 = (
    f"[1:a]volume=0.3,afade=t=out:st={fade_start:.3f}:d=1[music];"
    f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mixed];"
    f"[mixed]alimiter=limit=0.95[out]"
)
cmd2 = [FFMPEG, "-y", "-i", out_eq, "-stream_loop", "-1", "-i", MUSIC,
        "-filter_complex", fc2, "-map", "[out]",
        "-acodec", "libmp3lame", "-q:a", "2", out_cortina]
r2 = subprocess.run(cmd2, capture_output=True, text=True)
if r2.returncode != 0:
    print("ERROR cortina"); print(r2.stderr[-1500:]); raise SystemExit(1)
print("OK cortina:", out_cortina, "dur:", dur)
