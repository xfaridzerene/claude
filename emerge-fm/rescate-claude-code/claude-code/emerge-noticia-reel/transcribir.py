# Transcribe la transmisión con faster-whisper large-v3 (GPU) con tiempos por palabra.
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
                               initial_prompt="Emerge tu mañana, Gabriel Figueroa. Emerge FM 105.5, radio.")
lista = []
for s in segs:
    lista.append({'ini': s.start, 'fin': s.end, 'texto': s.text.strip(),
                  'palabras': [{'p': w.word, 'ini': w.start, 'fin': w.end} for w in s.words]})
json.dump({'audio1': lista}, open(os.path.join(AQUI, 'transcripcion.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# El modelo se salta el arranque (6–14 s): se transcribe esa ventana aparte y se antepone.
import subprocess
FF = r'C:\Program Files\Shutter Encoder\app\Library\ffmpeg.exe'
A, Z = 6.0, 13.85
ven = os.path.join(AQUI, 'revision', 'ventana_inicio.wav')
subprocess.run([FF, '-v', 'error', '-y', '-ss', str(A), '-to', str(Z), '-i',
                os.path.join(AQUI, 'revision', 'audio1.wav'), ven], check=True)
segs, _ = modelo.transcribe(ven, language='es', word_timestamps=True, beam_size=5, condition_on_previous_text=False)
extra = [{'ini': s.start + A, 'fin': s.end + A, 'texto': s.text.strip(),
          'palabras': [{'p': w.word, 'ini': w.start + A, 'fin': w.end + A} for w in s.words]} for s in segs]
lista = extra + [s for s in lista if s['ini'] >= Z - 0.1]
json.dump({'audio1': lista}, open(os.path.join(AQUI, 'transcripcion.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for s in lista[:4]:
    print(f"[{s['ini']:6.2f}] {s['texto']}")
