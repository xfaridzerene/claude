import sys
from faster_whisper import WhisperModel
try:
    m = WhisperModel("small", device="cuda", compute_type="float16")
except Exception as e:
    print("cpu", e); m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(sys.argv[1], language="es", word_timestamps=True)
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
    for w in s.words: print(f"    {w.start:6.2f} {w.end:6.2f} {w.word}")
