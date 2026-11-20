import os, sys, torch
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), 'lib'))
os.environ['PATH'] = os.path.join(os.path.dirname(torch.__file__), 'lib') + os.pathsep + os.environ['PATH']
from faster_whisper import WhisperModel
for nombre in ('large-v3', 'medium'):
    m = WhisperModel(nombre, device='cuda', compute_type='float16')
    for temp in (0.0,):
        segs, _ = m.transcribe(sys.argv[1], language='es', beam_size=5, word_timestamps=True, condition_on_previous_text=False)
        print(nombre, '|', ' '.join(f"{w.word.strip()}[{w.start+50:.2f}]" for s in segs for w in s.words), flush=True)
