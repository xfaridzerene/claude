# Transcribe el despacho con faster-whisper large-v3 (GPU) con tiempos por palabra.
# Correr con: C:\Users\farid\audio-env\Scripts\python.exe transcribir.py
import json, os
import torch  # trae las DLL de CUDA 12 (cublas) que ctranslate2 necesita
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), 'lib'))
os.environ['PATH'] = os.path.join(os.path.dirname(torch.__file__), 'lib') + os.pathsep + os.environ['PATH']
from faster_whisper import WhisperModel

AQUI = os.path.dirname(os.path.abspath(__file__))
modelo = WhisperModel('large-v3', device='cuda', compute_type='float16')
segs, info = modelo.transcribe(os.path.join(AQUI, 'revision', 'audio1.wav'), language='es',
                               word_timestamps=True, vad_filter=False, beam_size=5,
                               condition_on_previous_text=False)
lista = []
for s in segs:
    lista.append({'ini': s.start, 'fin': s.end, 'texto': s.text.strip(),
                  'palabras': [{'p': w.word, 'ini': w.start, 'fin': w.end} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}", flush=True)
json.dump({'audio1': lista}, open(os.path.join(AQUI, 'transcripcion.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
