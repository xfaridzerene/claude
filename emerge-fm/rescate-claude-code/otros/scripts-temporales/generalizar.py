import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b)


i1 = s.index('def fuente(')
cab = r'''# Reels verticales ENEO 2026 (Pro O'Higgins, Monticello, 18-11-2026): gancho corto con la mejor frase
# y luego la entrevista completa. Video vertical propio a pantalla completa + logo arriba + GC +
# subtítulos en seco (palabra activa en Verde Señal) + destello blanco breve entre gancho y completo.
#   python build.py IMG_0184                 -> salida/<salida>-9x16.mp4
#   python build.py IMG_0184 --fotos 1,10    -> revision/IMG_0184_foto_<t>.png
import os, sys, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
FFMPEG = r'C:\Program Files\Shutter Encoder\app\Library\ffmpeg.exe'
EFM = r'C:\Users\farid\Desktop\EMERGE FM'
F_UNB = os.path.join(EFM, 'Fuentes', 'Unbounded', 'static', 'Unbounded-{}.ttf')
F_SG = os.path.join(EFM, 'Fuentes', 'Space_Grotesk', 'static', 'SpaceGrotesk-{}.ttf')
LOGO_H = os.path.join(EFM, 'LOGO', 'Logo 105.5', 'PNG', 'emerge-fm-105.5-horizontal-color-transparente.png')

# Cada reel: gancho y tramo completo (segundos de la fuente 1080×1920 30 fps en fuentes/),
# GC (segundos desde que parte el tramo completo) y nombre del archivo de salida.
REELS = {
    'IMG_0184': dict(gancho=(43.40, 49.75), tramo=(0.55, 55.60), salida='eneo-raul-pro-ohiggins',
                     gcs=[(0.5, 7.5, 'Raúl [APELLIDO]', "[CARGO] · Pro O'Higgins")]),
    'IMG_0188': dict(gancho=(16.95, 23.50), tramo=(0.55, 26.50), salida='eneo-gobernador-pablo-silva',
                     gcs=[(0.3, 7.5, 'Pablo Silva Amaya', "Gobernador Regional de O'Higgins")]),
    'IMG_0196': dict(gancho=(72.40, 76.35), tramo=(0.0, 86.00), salida='eneo-hernan-garces',
                     gcs=[(0.5, 7.5, 'Hernán Garcés', 'Presidente · Garcés Fruit')]),
    'IMG_0203': dict(gancho=(120.35, 126.45), tramo=(0.0, 126.60), salida='eneo-seremi-mineria',
                     gcs=[(0.5, 7.5, 'Carla Ortiz', "Seremi de Minería de O'Higgins")]),
}
CLAVE = next((a for a in sys.argv[1:] if a in REELS), 'IMG_0184')
CFG = REELS[CLAVE]
ORIGINAL = os.path.join(AQUI, 'fuentes', CLAVE + '.mov')
FUENTE_VIDEO = os.path.join(AQUI, 'salida', f'_editado_{CLAVE}.mov')
TRAMOS = [CFG['gancho'], CFG['tramo']]
CORTES = [CFG['gancho'][1] - CFG['gancho'][0]]
T_COMPLETO = CORTES[0]
GCS = [(T_COMPLETO + a, T_COMPLETO + b, n, c) for a, b, n, c in CFG['gcs']]

W, H, FPS = 1080, 1920, 30
VERDE = (0, 230, 171)       # Verde Señal
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
OSCURO = (10, 14, 20)

Y_LOGO = 70
Y_GC = 1215
Y_SUB = 1440

# Correcciones de la transcripción (se aplican en todas las apariciones)
EDITS = [(['ProHiggins,'], ["ProO'Higgins,"]), (['Provo', 'Higgins'], ["ProO'Higgins"]),
         (['Provo', 'Higgins,'], ["ProO'Higgins,"]), (['O', "'Higgins."], ["O'Higgins."]),
         (['O', "'Higgins,"], ["O'Higgins,"]), (['Garcet'], ['Garcés']), (['pan', 'de', 'meses'], ['par', 'de', 'meses']),
         (['Maya,'], ['Amaya,']), (['dolor', 'de', 'éxito'], ['de', 'los', 'éxitos']), (['Windsurf'], ['windsurf']),
         (['Código', 'de', 'División', 'del', 'Teniente,'], ['Codelco', 'División', 'El', 'Teniente,']),
         (['Cernagio', 'Min,'], ['Sernageomin,']), (['Eremia.'], ['seremi.']), (['los', 'robles,'], ['Los', 'Robles,'])]
CORTAR_ANTES = []
UNIR = [['emerge', 'fm'], ['emerge', 'fm.'], ['emerge', 'fm,']]


'''
s = cab + s[i1:]
rep("for s in d['audio1']:", "for s in d[CLAVE]:")
rep('''    for viejo, nuevo in EDITS:
        txt = [w['p'] for w in out]
        for i in range(len(txt) - len(viejo) + 1):
            if txt[i:i + len(viejo)] == viejo:
                ini, fin = out[i]['ini'], out[i + len(viejo) - 1]['fin']
                paso = (fin - ini) / len(nuevo)
                out[i:i + len(viejo)] = [dict(p=p, ini=ini + j * paso, fin=ini + (j + 1) * paso)
                                         for j, p in enumerate(nuevo)]
                break''', '''    for viejo, nuevo in EDITS:
        i = 0
        while i <= len(out) - len(viejo):
            if [w['p'] for w in out[i:i + len(viejo)]] == viejo:
                ini, fin, nv = out[i]['ini'], out[i + len(viejo) - 1]['fin'], out[i].get('nuevo')
                paso = (fin - ini) / len(nuevo)
                out[i:i + len(viejo)] = [dict(p=p, ini=ini + j * paso, fin=ini + (j + 1) * paso,
                                              nuevo=bool(nv) and j == 0) for j, p in enumerate(nuevo)]
                i += len(nuevo)
            else:
                i += 1''')
rep("                # 0.35 s de margen al inicio: whisper adelanta el «Bueno,» de Fabián (38.0 vs 38.4 real)\n", "")
rep("if a - 0.35 <= w['ini'] and w['fin'] <= b + 0.12:", "if a - 0.12 <= w['ini'] and w['fin'] <= b + 0.12:")
rep("""        if i and out[i - 1]['p'][-1] in '.?!' and w['p'][0].islower():""",
    """        if (w.get('nuevo') or (i and out[i - 1]['p'][-1] in '.?!')) and w['p'][0].islower():""")
# sin video de apoyo
i0 = s.index('def mascara_franja():')
i1 = s.index('def componer(')
s = s[:i0] + s[i1:]
i0 = s.index('def componer(')
i1 = s.index('    fr = fr * OSCURECER')
s = s[:i0] + 'def componer(t, lector, subs, dur):\n    fr = lector.cuadro(int(t * FPS)).astype(np.float32)\n' + s[i1:]
i0 = s.index('    if 0 <= ta < APOYO_DUR:\n        a = min(clamp(ta / 0.2)')
i1 = s.index('    for a, b, im in FICHAS:')
s = s[:i0] + s[i1:]
rep("""        lector = Lector(FUENTE_VIDEO)
        apoyo = Lector(APOYO, APOYO_W, APOYO_H)
        for t in ts:
            componer(t, lector, subs, 218, apoyo).save(os.path.join(AQUI, 'revision', f'foto_{t:06.2f}.png'))""",
    """        lector = Lector(FUENTE_VIDEO)
        for t in ts:
            componer(t, lector, subs, 999).save(os.path.join(AQUI, 'revision', f'{CLAVE}_foto_{t:06.2f}.png'))""")
rep("""    lector = Lector(FUENTE_VIDEO)
    apoyo = Lector(APOYO, APOYO_W, APOYO_H)
    for i in range(n):
        enc.stdin.write(componer(i / FPS, lector, subs, dur, apoyo).tobytes())""",
    """    lector = Lector(FUENTE_VIDEO)
    for i in range(n):
        enc.stdin.write(componer(i / FPS, lector, subs, dur).tobytes())""")
rep("salida = os.path.join(AQUI, 'salida', 'rengo-ciclistas-atropellados-9x16.mp4')",
    "salida = os.path.join(AQUI, 'salida', CFG['salida'] + '-9x16.mp4')")
rep("with open(os.path.join(AQUI, 'revision', 'subtitulos.txt')",
    "with open(os.path.join(AQUI, 'revision', f'{CLAVE}_subtitulos.txt')")
rep("wav = os.path.join(AQUI, 'salida', '_audio.wav')", "wav = os.path.join(AQUI, 'salida', f'_audio_{CLAVE}.wav')")
rep("tmp = FUENTE_VIDEO.replace('.mp4', '_tmp.mov')", "tmp = FUENTE_VIDEO.replace('.mov', '_tmp.mov')")
rep("    if os.path.exists(FUENTE_VIDEO) and os.path.getmtime(FUENTE_VIDEO) > os.path.getmtime(__file__):\n        return\n", "")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
