import os, glob, torch
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), 'lib'))
os.environ['PATH'] = os.path.join(os.path.dirname(torch.__file__), 'lib') + os.pathsep + os.environ['PATH']
from faster_whisper import WhisperModel
m = WhisperModel('large-v3', device='cuda', compute_type='float16')
for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corte_*.wav'))):
    segs, _ = m.transcribe(f, language='es', beam_size=5, word_timestamps=True, condition_on_previous_text=False)
    print(os.path.basename(f), ' '.join(f"{w.word.strip()}[{w.start:.2f}]" for s in segs for w in s.words))
