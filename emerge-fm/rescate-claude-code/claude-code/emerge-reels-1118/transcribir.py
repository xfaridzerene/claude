# Transcribe los videos del 18-11 con faster-whisper large-v3 (GPU), con tiempos por palabra.
# Correr con: C:\Users\farid\audio-env\Scripts\python.exe transcribir.py [IMG_0184 ...]
import json, os, sys
import torch  # trae las DLL de CUDA 12 (cublas) que ctranslate2 necesita
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), 'lib'))
os.environ['PATH'] = os.path.join(os.path.dirname(torch.__file__), 'lib') + os.pathsep + os.environ['PATH']
from faster_whisper import WhisperModel

AQUI = os.path.dirname(os.path.abspath(__file__))
NOMBRES = sys.argv[1:] or ['IMG_0184', 'IMG_0187', 'IMG_0188', 'IMG_0196', 'IMG_0203']
RUTA = os.path.join(AQUI, 'transcripcion.json')
todo = json.load(open(RUTA, encoding='utf-8')) if os.path.exists(RUTA) else {}

modelo = WhisperModel('large-v3', device='cuda', compute_type='float16')
for n in NOMBRES:
    segs, info = modelo.transcribe(os.path.join(AQUI, 'revision', n + '.wav'), language='es',
                                   word_timestamps=True, vad_filter=False, beam_size=5,
                                   condition_on_previous_text=False)
    lista = []
    for s in segs:
        lista.append({'ini': s.start, 'fin': s.end, 'texto': s.text.strip(),
                      'palabras': [{'p': w.word, 'ini': w.start, 'fin': w.end} for w in s.words]})
    todo[n] = lista
    json.dump(todo, open(RUTA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(os.path.join(AQUI, 'revision', n + '_transcripcion.txt'), 'w', encoding='utf-8') as f:
        for s in lista:
            f.write(f"[{s['ini']:6.2f}-{s['fin']:6.2f}] {s['texto']}\n")
    print(n, len(lista), 'segmentos', flush=True)
