import os, glob, torch
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), 'lib'))
os.environ['PATH'] = os.path.join(os.path.dirname(torch.__file__), 'lib') + os.pathsep + os.environ['PATH']
from faster_whisper import WhisperModel
for nombre in ['medium', 'large-v3']:
    m = WhisperModel(nombre, device='cuda', compute_type='float16')
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corte_*.wav'))):
        segs, _ = m.transcribe(f, language='es', beam_size=5, condition_on_previous_text=False,
                               initial_prompt='Gobernador regional de O\'Higgins, Pro O\'Higgins, Sernatur, ProChile, INDAP, proyectos detonantes.')
        print(nombre, os.path.basename(f), ' '.join(s.text.strip() for s in segs), flush=True)
