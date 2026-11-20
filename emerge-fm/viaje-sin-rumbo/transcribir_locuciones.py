# Transcribe las locuciones del día para ordenar el programa cuando no viene pauta
# (cada locución dice qué sonó y qué viene). Uso:
#   C:\Users\farid\audio-env\Scripts\python.exe transcribir_locuciones.py voces\1.wav voces\4.wav ...
import sys
sys.stdout.reconfigure(encoding='utf-8')
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in sys.argv[1:]:
    segs,_ = m.transcribe(f, language="es", beam_size=1)
    print("==", f.split("/")[-1], flush=True)
    print(" ".join(s.text.strip() for s in segs), flush=True)
