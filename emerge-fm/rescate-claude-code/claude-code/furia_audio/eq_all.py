# -*- coding: utf-8 -*-
import subprocess, os, re, json, unicodedata
import numpy as np
from scipy.io import wavfile
from faster_whisper import WhisperModel

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
ROOT = r"C:\Users\farid\Desktop\EMERGE FM\La Ciudad de la Furia\FRASES"
WORKDIR = r"C:\Users\farid\Desktop\claude code\furia_audio\eq_work"
os.makedirs(WORKDIR, exist_ok=True)

BASE = "bass=g=2:f=100:w=0.5,treble=g=1.8:f=7000:w=0.5,aecho=0.9:0.4:35|55:0.15|0.10,extrastereo=m=1.1"

def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]", "", s)
    return s

TARGETS = [
    ["la", "ciudad", "de", "la", "furia"],
    ["caco", "lopez"],
    ["kaco", "lopez"],
    ["cacolopez"],
    ["kacolopez"],
]

def find_hero_windows(words):
    """words: list of [start,end,text]. Returns list of (start,end) merged windows."""
    norm_words = [norm(w[2]) for w in words]
    windows = []
    for target in TARGETS:
        tlen = len(target)
        i = 0
        while i <= len(norm_words) - tlen:
            if norm_words[i:i+tlen] == target:
                windows.append((words[i][0], words[i+tlen-1][1]))
                i += tlen
            else:
                i += 1
    windows.sort()
    merged = []
    for a, b in windows:
        if merged and a <= merged[-1][1] + 0.05:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged

def get_words(path, model):
    tmp = os.path.join(WORKDIR, "tmp16k.wav")
    subprocess.run([FFMPEG, "-y", "-i", path, "-ar", "16000", "-ac", "1", tmp], capture_output=True)
    sr, data = wavfile.read(tmp)
    audio = data.astype(np.float32) / 32768.0
    segments, info = model.transcribe(audio, language="es", word_timestamps=True)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append([round(w.start, 3), round(w.end, 3), w.word.strip()])
    return words

def build_filter(hero_windows):
    if not hero_windows:
        return f"[0:a]{BASE},apad=pad_dur=0.3[out]"
    graph = [f"[0:a]{BASE},apad=pad_dur=0.6[coloured]"]
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
    graph.append("[mixed]loudnorm=I=-19:TP=-2.0:LRA=9,alimiter=limit=0.9[out]")
    return ";".join(graph)

def main():
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    folders = sorted(
        d for d in os.listdir(ROOT)
        if os.path.isdir(os.path.join(ROOT, d))
    )
    report = []
    for d in folders:
        num = d[:2]
        src = os.path.join(ROOT, d, f"{num} - Frase.mp3")
        if not os.path.exists(src):
            print("SKIP (no src):", d)
            continue
        words = get_words(src, model)
        heroes = find_hero_windows(words)
        fc = build_filter(heroes)
        out_path = os.path.join(ROOT, d, f"{num} - Frase (ecualizada).mp3")
        cmd = [FFMPEG, "-y", "-i", src, "-filter_complex", fc, "-map", "[out]",
               "-acodec", "libmp3lame", "-q:a", "2", out_path]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("ERROR", d)
            print(r.stderr[-1000:])
            report.append((d, "ERROR", heroes))
        else:
            print("OK", d, "heroes:", heroes)
            report.append((d, "OK", heroes))

    with open(os.path.join(WORKDIR, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
