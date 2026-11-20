import sys, soundfile as sf
sys.stdout.reconfigure(encoding='utf-8')
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in sys.argv[1:]:
    print("==", f, round(sf.info(f).duration,1), "s")
    segs,_ = m.transcribe(f, language="es")
    for sg in segs: print(f"  {sg.start:6.1f} {sg.text}")
