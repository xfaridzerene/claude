# Transcribe las locuciones del programa del jueves 12-11 (desde la mezcla al aire).
# Correr con: C:\Users\farid\audio-env\Scripts\python.exe transcribir.py
import json, os, subprocess
import torch
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), 'lib'))
os.environ['PATH'] = os.path.join(os.path.dirname(torch.__file__), 'lib') + os.pathsep + os.environ['PATH']
from faster_whisper import WhisperModel

AQUI = os.path.dirname(os.path.abspath(__file__))
FF = r"C:\Users\farid\audio-env\bin\ffmpeg.exe"
MIX = os.path.join(AQUI, '..', 'viaje-sin-rumbo', 'programa-12-11', 'salida',
                   'Viaje sin Rumbo - 12-11-2026 - Los Irreverentes.wav')
# (nombre, inicio, fin) en segundos de la mezcla — según minutaje.txt
LOC = [('l01_saludo', 38, 126), ('l04_banderas', 494, 572), ('l07_fiskales', 1138, 1211),
       ('l12_especial', 1677, 1763), ('l15_anwandter', 2113, 2195), ('l18_cierre', 2603, 2672)]
modelo = WhisperModel('large-v3', device='cuda', compute_type='float16')
salida = {}
for nom, a, b in LOC:
    wav = os.path.join(AQUI, 'fuentes', nom + '.wav')
    subprocess.run([FF, '-v', 'error', '-y', '-ss', str(a), '-to', str(b), '-i', MIX, '-ac', '1', '-ar', '16000', wav], check=True)
    segs, info = modelo.transcribe(wav, language='es', word_timestamps=True, vad_filter=False, beam_size=5,
        initial_prompt="Viaje sin Rumbo, Emerge FM, Valentina Sepúlveda. Los Prisioneros, Fiskales Ad-Hok, Glup!, Sinergia, Los Ex, Álex Anwandter.")
    lista = []
    for s in segs:
        lista.append({'ini': s.start + a, 'fin': s.end + a, 'texto': s.text.strip(),
                      'palabras': [{'p': w.word, 'ini': w.start + a, 'fin': w.end + a} for w in s.words]})
        print(f'[{nom} {s.start + a:7.2f}-{s.end + a:7.2f}] {s.text.strip()}', flush=True)
    salida[nom] = lista
json.dump(salida, open(os.path.join(AQUI, 'transcripcion.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

