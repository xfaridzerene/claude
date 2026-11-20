# -*- coding: utf-8 -*-
import subprocess, os, re, json, unicodedata
import numpy as np
from scipy.io import wavfile
from faster_whisper import WhisperModel

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
MUSIC = r"C:\Users\farid\Downloads\maqueta 1 cortina emerge solo musica.mp3.mpeg"
ROOT = r"E:\EMERGE FM 1\FRASES"
WORKDIR = r"C:\Users\farid\Desktop\claude code\furia_audio\eq_work_emerge_v2"
os.makedirs(WORKDIR, exist_ok=True)

BASE = "bass=g=2:f=100:w=0.5,treble=g=1.8:f=7000:w=0.5,aecho=0.9:0.4:35|55:0.15|0.10,extrastereo=m=1.1"
TAIL_PAD = 2.0  # clean 2s tail after the voice (silence only, or melody-only once mixed)

TARGETS = [["emerge", "fm"], ["emerge"]]

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

def build_filter(hero_windows, trim_end):
    pre = f"atrim=start=0:end={trim_end:.3f},asetpts=PTS-STARTPTS," if trim_end is not None else ""
    graph = [f"[0:a]{pre}{BASE},apad=pad_dur={TAIL_PAD}[coloured]"]
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

def get_duration(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)

def render_cortina(voice_path, out_path):
    dur = get_duration(voice_path)
    fade_dur = min(1.5, TAIL_PAD)
    fade_start = max(0.0, dur - fade_dur)
    fc = (
        f"[1:a]volume=0.3,afade=t=out:st={fade_start:.3f}:d={fade_dur}[music];"
        f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mixed];"
        f"[mixed]alimiter=limit=0.95[out]"
    )
    cmd = [FFMPEG, "-y", "-i", voice_path, "-stream_loop", "-1", "-i", MUSIC,
           "-filter_complex", fc, "-map", "[out]",
           "-acodec", "libmp3lame", "-q:a", "2", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, r.stderr[-1000:] if r.returncode != 0 else None

def main():
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    folders = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    tmp = os.path.join(WORKDIR, "tmp16k.wav")
    report = []
    for d in folders:
        num = d[:2]
        folder_path = os.path.join(ROOT, d)
        for take in ("Toma 1", "Toma 2"):
            src = os.path.join(folder_path, f"{num} - {take}.mp3")
            if not os.path.exists(src):
                print("SKIP (no src):", d, take)
                continue
            try:
                audio, sr, words = get_audio_and_words(src, model, tmp)
            except Exception as e:
                print("ERROR transcribe", d, take, e)
                report.append({"folder": d, "take": take, "status": "ERROR_TRANSCRIBE", "err": str(e)})
                continue
            heroes = find_hero_windows(words)
            last_word_end = words[-1][1] if words else 0.0
            orig_dur = len(audio) / sr
            trim_end = (last_word_end + 0.5) if (orig_dur - last_word_end) > 1.0 else None

            fc = build_filter(heroes, trim_end)
            out_eq = os.path.join(folder_path, f"{num} - {take} (ecualizada).mp3")
            cmd = [FFMPEG, "-y", "-i", src, "-filter_complex", fc, "-map", "[out]",
                   "-acodec", "libmp3lame", "-q:a", "2", out_eq]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                print("ERROR render eq", d, take)
                print(r.stderr[-1000:])
                report.append({"folder": d, "take": take, "status": "ERROR_EQ"})
                continue

            out_cortina = os.path.join(folder_path, f"{num} - {take} (ecualizada + cortina).mp3")
            ok, err = render_cortina(out_eq, out_cortina)
            if not ok:
                print("ERROR render cortina", d, take)
                print(err)
                report.append({"folder": d, "take": take, "status": "ERROR_CORTINA", "heroes": heroes, "trim_end": trim_end})
                continue

            print("OK", d, take, "heroes:", heroes, "trim_end:", trim_end, "orig_dur:", round(orig_dur, 2))
            report.append({"folder": d, "take": take, "status": "OK", "heroes": heroes, "trim_end": trim_end})

    with open(os.path.join(WORKDIR, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    ok_count = sum(1 for r in report if r["status"] == "OK")
    print(f"\nTotal OK: {ok_count}/{len(report)}")

if __name__ == "__main__":
    main()
