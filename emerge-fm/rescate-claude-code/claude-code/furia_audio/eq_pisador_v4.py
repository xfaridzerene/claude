# -*- coding: utf-8 -*-
import subprocess

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

src = r"E:\Pisadores iniciales\01 - Toma 2.mp3"
out = r"C:\Users\farid\Desktop\claude code\furia_audio\01 - Toma 2 (ecualizada).mp3"

BASE = "bass=g=2:f=100:w=0.5,treble=g=1.8:f=7000:w=0.5,aecho=0.9:0.4:35|55:0.15|0.10,extrastereo=m=1.1"

hero_windows = [(1.38, 2.66), (6.36, 6.6)]

# trim the stray "e" sound at the very end of the raw take (starts ~9.065s)
TRIM_END = 9.04

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
       "-acodec", "libmp3lame", "-q:a", "2", out]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("ERROR")
    print(r.stderr[-1500:])
else:
    print("OK", out)
