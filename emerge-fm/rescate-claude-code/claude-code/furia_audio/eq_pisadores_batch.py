# -*- coding: utf-8 -*-
import subprocess, os, re, json, unicodedata
import numpy as np
from scipy.io import wavfile
from faster_whisper import WhisperModel

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
ROOT = r"E:\EMERGE FM 1\FRASES"
WORKDIR = r"C:\Users\farid\Desktop\claude code\furia_audio\eq_work_emerge"
os.makedirs(WORKDIR, exist_ok=True)

BASE = "bass=g=2:f=100:w=0.5,treble=g=1.8:f=7000:w=0.5,aecho=0.9:0.4:35|55:0.15|0.10,extrastereo=m=1.1"

TARGETS = [
    ["emerge", "fm"],
    ["emerge"],
]

def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]", "", s)
    return s

def find_hero_windows(words):
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

def get_audio_and_words(path, model, tmp):
    r = subprocess.run([FFMPEG, "-y", "-i", path, "-ar", "16000", "-ac", "1", tmp], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:])
    sr, data = wavfile.read(tmp)
    audio = data.astype(np.float32) / 32768.0
    segments, info = model.transcribe(audio, language="es", word_timestamps=True)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append([round(w.start, 3), round(w.end, 3), w.word.strip()])
    return audio, sr, words

def detect_trailing_artifact(audio, sr, last_word_end):
    """Looks for: speech ends -> real silence gap -> a stray burst near/at file end.
    Returns a trim point (seconds) to cut right before the stray burst, or None if
    there's nothing to trim (file just ends in silence/reverb decay)."""
    win = int(0.02 * sr)
    n = len(audio)
    dbs = []
    t = 0.0
    times = []
    i = 0
    while i < n:
        chunk = audio[i:i+win]
        if len(chunk) == 0:
            break
        rms = np.sqrt(np.mean(chunk.astype(np.float64) ** 2))
        db = 20 * np.log10(rms + 1e-9)
        dbs.append(db)
        times.append(t)
        i += win
        t += 0.02

    start_idx = int(last_word_end / 0.02)
    i = start_idx
    silence_start = None
    while i < len(dbs):
        if dbs[i] < -55 and all(d < -50 for d in dbs[i:i+15]) and i + 15 <= len(dbs):
            silence_start = i
            break
        i += 1
    if silence_start is None:
        return None

    j = silence_start + 15
    while j < len(dbs):
        if dbs[j] > -45:
            return max(last_word_end, times[j] - 0.03)
        j += 1
    return None

def build_filter(hero_windows, trim_end):
    pre = f"atrim=start=0:end={trim_end:.3f},asetpts=PTS-STARTPTS," if trim_end is not None else ""
    graph = [f"[0:a]{pre}{BASE},apad=pad_dur=0.6[coloured]"]
    n = len(hero_windows)
    if n == 0:
        graph.append("[coloured]loudnorm=I=-19:TP=-2.0:LRA=9,alimiter=limit=0.9,adelay=2000|2000[out]")
        return ";".join(graph)
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
    return ";".join(graph)

def main():
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    folders = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    tmp = os.path.join(WORKDIR, "tmp16k.wav")
    report = []
    for d in folders:
        num = d[:2]
        folder_path = os.path.join(ROOT, d)
        for take in ("Toma 1", "Toma 2"):
            fname = f"{num} - {take}.mp3"
            src = os.path.join(folder_path, fname)
            if not os.path.exists(src):
                print("SKIP (no src):", d, take)
                continue
            try:
                audio, sr, words = get_audio_and_words(src, model, tmp)
            except Exception as e:
                print("ERROR transcribe", d, take, e)
                report.append((d, take, "ERROR_TRANSCRIBE", str(e)))
                continue
            heroes = find_hero_windows(words)
            last_word_end = words[-1][1] if words else 0.0
            trim_end = detect_trailing_artifact(audio, sr, last_word_end)
            fc = build_filter(heroes, trim_end)
            out_name = f"{num} - {take} (ecualizada).mp3"
            out_path = os.path.join(folder_path, out_name)
            cmd = [FFMPEG, "-y", "-i", src, "-filter_complex", fc, "-map", "[out]",
                   "-acodec", "libmp3lame", "-q:a", "2", out_path]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                print("ERROR render", d, take)
                print(r.stderr[-1000:])
                report.append((d, take, "ERROR_RENDER", heroes, trim_end))
            else:
                print("OK", d, take, "heroes:", heroes, "trim_end:", trim_end)
                report.append((d, take, "OK", heroes, trim_end))

    with open(os.path.join(WORKDIR, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
