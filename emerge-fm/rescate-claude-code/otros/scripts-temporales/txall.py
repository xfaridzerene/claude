import sys
sys.stdout.reconfigure(encoding='utf-8')
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in sys.argv[1:]:
    segs,_ = m.transcribe(f, language="es", beam_size=1)
    print("==", f.split("/")[-1], flush=True)
    print(" ".join(s.text.strip() for s in segs), flush=True)
