# Transcribe las dos partes con faster-whisper large-v3 (GPU) con tiempos por palabra.
# Correr con: C:\Users\farid\audio-env\Scripts\python.exe transcribir.py
import json, os, sys
from faster_whisper import WhisperModel

AQUI = os.path.dirname(os.path.abspath(__file__))
modelo = WhisperModel('large-v3', device='cuda', compute_type='float16')
salida = {}
for parte in ('audio1', 'audio2'):
    segs, info = modelo.transcribe(os.path.join(AQUI, 'revision', parte + '.wav'), language='es',
                                   word_timestamps=True, vad_filter=False, beam_size=5,
                                   initial_prompt="Emerge Noticias, Roberto Rojas. Camilo Jiménez, vocero de la Asociación Gremial Rengo O'Higgins, ASGRO. Camioneros, Rengo.")
    lista = []
    for s in segs:
        lista.append({'ini': s.start, 'fin': s.end, 'texto': s.text.strip(),
                      'palabras': [{'p': w.word, 'ini': w.start, 'fin': w.end} for w in s.words]})
        print(f'[{parte} {s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}', flush=True)
    salida[parte] = lista
json.dump(salida, open(os.path.join(AQUI, 'transcripcion.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
