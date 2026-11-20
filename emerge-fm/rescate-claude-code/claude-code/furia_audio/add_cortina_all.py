# -*- coding: utf-8 -*-
import subprocess, os, re

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
MUSIC = r"C:\Users\farid\Downloads\maqueta 1 cortina emerge solo musica.mp3.mpeg"
ROOT = r"E:\EMERGE FM 1\FRASES"

def get_duration(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)

def main():
    folders = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    results = []
    for d in folders:
        num = d[:2]
        folder_path = os.path.join(ROOT, d)
        for take in ("Toma 1", "Toma 2"):
            voice = os.path.join(folder_path, f"{num} - {take} (ecualizada).mp3")
            if not os.path.exists(voice):
                print("SKIP (no ecualizada):", d, take)
                continue
            dur = get_duration(voice)
            fade_start = max(0.0, dur - 1.0)
            fc = (
                f"[1:a]volume=0.3,afade=t=out:st={fade_start:.3f}:d=1[music];"
                f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mixed];"
                f"[mixed]alimiter=limit=0.95[out]"
            )
            out_path = os.path.join(folder_path, f"{num} - {take} (ecualizada + cortina).mp3")
            cmd = [FFMPEG, "-y", "-i", voice, "-stream_loop", "-1", "-i", MUSIC,
                   "-filter_complex", fc, "-map", "[out]",
                   "-acodec", "libmp3lame", "-q:a", "2", out_path]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                print("ERROR", d, take)
                print(r.stderr[-1000:])
                results.append((d, take, "ERROR"))
            else:
                print("OK", d, take, "dur:", round(dur, 2))
                results.append((d, take, "OK"))
    ok = sum(1 for r in results if r[2] == "OK")
    print(f"\nTotal OK: {ok}/{len(results)}")

if __name__ == "__main__":
    main()
