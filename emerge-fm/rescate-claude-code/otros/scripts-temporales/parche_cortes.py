import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b)


rep(r"FUENTE_VIDEO = r'C:\Users\farid\Downloads\20261116_161729~2.mp4'",
r"""ORIGINAL = r'C:\Users\farid\Downloads\20261116_161729~2.mp4'
FUENTE_VIDEO = os.path.join(AQUI, 'salida', '_editado.mp4')
# Versión < 3 min para IG/FB: fuera las preguntas intermedias de Roberto (se mantienen su
# presentación y su cierre). Tramos que se conservan, en segundos del original:
TRAMOS = [(0.0, 33.85),      # presentación … «Estoy con Fabián Cofré.»
          (38.30, 100.42),   # «Bueno, el día de ayer…» … «…nos ayudaron en ese momento.»
          (115.27, 137.25),  # «los vecinos fueron la primera línea…» … «…bomberos y ambulancia.»
          (149.80, 172.12),  # «Las siete bicicletas se quebraron…» … «…una sentencia.»
          (183.62, 218.45)]  # «Justicia, que esta persona…» … cierre de Roberto
# (versión completa de 3:38: revision/build_completo_218s.py)
CORTES = []
_acc = 0.0
for _a, _b in TRAMOS[:-1]:
    _acc += _b - _a
    CORTES.append(_acc)""")
rep("(38.3, 45.5, 'Fabián Cofré',", "(34.1, 41.3, 'Fabián Cofré',")
rep("# ---------- audio ----------", r'''# ---------- edición ----------
def armar_editado():
    if os.path.exists(FUENTE_VIDEO) and os.path.getmtime(FUENTE_VIDEO) > os.path.getmtime(__file__):
        return
    f, etiquetas = [], ''
    for k, (a, b) in enumerate(TRAMOS):
        d = b - a
        f.append(f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS}[v{k}]')
        f.append(f'[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d - 0.03}:d=0.03[a{k}]')
        etiquetas += f'[v{k}][a{k}]'
    f.append(f'{etiquetas}concat=n={len(TRAMOS)}:v=1:a=1[v][a]')
    tmp = FUENTE_VIDEO.replace('.mp4', '_tmp.mov')
    subprocess.run([FFMPEG, '-y', '-v', 'error', '-i', ORIGINAL, '-filter_complex', ';'.join(f),
                    '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast',
                    '-c:a', 'pcm_s16le', tmp], check=True)
    os.replace(tmp, FUENTE_VIDEO)


# ---------- audio ----------''')
rep("""    out = [dict(p=w['p'].strip(), ini=max(w['ini'], 0.02), fin=w['fin']) for s in d['audio1'] for w in s['palabras']]""",
"""    out, base = [], 0.0
    for a, b in TRAMOS:
        primera = True
        for s in d['audio1']:
            for w in s['palabras']:
                if a - 0.12 <= w['ini'] and w['fin'] <= b + 0.12:
                    out.append(dict(p=w['p'].strip(), ini=max(base + w['ini'] - a, base + 0.02),
                                    fin=min(base + w['fin'] - a, base + b - a), nuevo=primera))
                    primera = False
        base += b - a""")
rep("""        forzar = any(txt[i:i + len(c)] == c for c in CORTAR_ANTES)""",
"""        forzar = any(txt[i:i + len(c)] == c for c in CORTAR_ANTES) or w.get('nuevo')""")
rep("""    fade = min(clamp(t / 0.2), clamp((dur - t) / 0.6))""",
"""    for tc in CORTES:  # destello blanco breve en cada corte
        f = clamp(1 - abs(t - tc) / 0.1) * 0.55
        if f > 0.01:
            base.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * f))))
    fade = min(clamp(t / 0.2), clamp((dur - t) / 0.6))""")
rep("""    subs = bloques(palabras())""", """    armar_editado()
    subs = bloques(palabras())""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
