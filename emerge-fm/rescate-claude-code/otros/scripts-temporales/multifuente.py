import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b)


rep('''    'IMG_0188': dict(gancho=(16.95, 23.50), tramo=(0.55, 26.50), salida='eneo-gobernador-pablo-silva',
                     gcs=[(0.3, 7.5, 'Pablo Silva Amaya', "Gobernador Regional de O'Higgins")]),''',
    '''    # Gobernador: IMG_0188 (presentación + pregunta por el mundial de windsurf) sigue en IMG_0189
    # («…que es maravilloso, que coloca a la región…»). El saludo de 0188 se omite porque 0189 cierra
    # con otro. Gancho: los $20.000 millones para los 33 municipios.
    'GOBERNADOR': dict(tramos=[('IMG_0189', 29.40, 35.75), ('IMG_0188', 0.55, 16.25), ('IMG_0189', 0.0, 144.10)],
                       salida='eneo-gobernador-pablo-silva',
                       gcs=[(0.3, 7.5, 'Pablo Silva Amaya', "Gobernador Regional de O'Higgins")]),''')
rep('''CLAVE = next((a for a in sys.argv[1:] if a in REELS), 'IMG_0184')
CFG = REELS[CLAVE]
ORIGINAL = os.path.join(AQUI, 'fuentes', CLAVE + '.mov')
FUENTE_VIDEO = os.path.join(AQUI, 'salida', f'_editado_{CLAVE}.mov')
TRAMOS = [CFG['gancho'], CFG['tramo']]
CORTES = [CFG['gancho'][1] - CFG['gancho'][0]]
T_COMPLETO = CORTES[0]''',
    '''CLAVE = next((a for a in sys.argv[1:] if a in REELS), 'IMG_0184')
CFG = REELS[CLAVE]
# TRAMOS: (video, desde, hasta). El primero es el gancho; el GC se cuenta desde el segundo.
TRAMOS = CFG.get('tramos') or [(CLAVE,) + CFG['gancho'], (CLAVE,) + CFG['tramo']]
FUENTE_VIDEO = os.path.join(AQUI, 'salida', f'_editado_{CLAVE}.mov')
CORTES = []
_acc = 0.0
for _v, _a, _b in TRAMOS[:-1]:
    _acc += _b - _a
    CORTES.append(_acc)
T_COMPLETO = CORTES[0]''')
# edición multi-fuente
rep('''    f, etiquetas = [], ''
    for k, (a, b) in enumerate(TRAMOS):
        d = b - a
        f.append(f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS}[v{k}]')
        f.append(f'[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d - 0.03}:d=0.03[a{k}]')
        etiquetas += f'[v{k}][a{k}]'
''', '''    f, etiquetas = [], ''
    videos = sorted({v for v, _, _ in TRAMOS})
    entradas = []
    for v in videos:
        entradas += ['-i', os.path.join(AQUI, 'fuentes', v + '.mov')]
    for k, (v, a, b) in enumerate(TRAMOS):
        d = b - a
        j = videos.index(v)
        f.append(f'[{j}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS}[v{k}]')
        f.append(f'[{j}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d - 0.03}:d=0.03[a{k}]')
        etiquetas += f'[v{k}][a{k}]'
''')
rep("subprocess.run([FFMPEG, '-y', '-v', 'error', '-i', ORIGINAL, '-filter_complex', ';'.join(f),",
    "subprocess.run([FFMPEG, '-y', '-v', 'error', *entradas, '-filter_complex', ';'.join(f),")
rep('''    for a, b in TRAMOS:
        primera = True
        for s in d[CLAVE]:''', '''    for v, a, b in TRAMOS:
        primera = True
        for s in d[v]:''')
rep("(['Cernagio', 'Min,'], ['Sernageomin,']),",
    "(['Cernagio', 'Min,'], ['Sernageomin,']), (['20', '.000'], ['20.000']), (['en', 'el', 'Centro', 'Tur'], ['en', 'Sernatur']),\n"
    "         (['de', 'donantes,'], ['detonantes,']), (['Cordillera', 'Mar.'], ['cordillera', 'a', 'mar.']),\n"
    "         (['donde', 'están', 'la', 'educación'], ['donde', 'está', 'Pro', \"O'Higgins,\", 'donde', 'está', 'la', 'educación']),\n"
    "         (['éxitos', 'siempre'], ['éxitos,', 'siempre']), (['radio', 'así'], ['radio,', 'así']),")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
