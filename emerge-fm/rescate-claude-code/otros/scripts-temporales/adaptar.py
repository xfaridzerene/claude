import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b)


rep(r"""# Reel vertical de la cuña de Camilo Jiménez (ASGRO) en Emerge Noticias.
# Arriba: foto de Camilo en un cuadro + nombre/cargo + onda de audio en vivo.
# Al medio: Roberto Rojas (16:9 a ancho completo, GC intacto). Abajo: subtítulos con
# la palabra que suena resaltada. Parte 1 (.mov, 39 s) y luego parte 2 (.mp4, 28 s).
#   python build.py                 -> salida/cuna-asgro-camilo-jimenez-9x16.mp4""",
    r"""# Reel vertical de la cuña de José Cepeda (dirigente agricultor, Chépica) en Emerge Noticias.
# Arriba: foto de José en un cuadro + nombre/cargo + onda de audio en vivo.
# Al medio: Roberto Rojas (16:9 a ancho completo, GC intacto). Abajo: subtítulos en seco
# (sin fundido ni subida) con la palabra que suena resaltada.
# Plantilla: copia de emerge-cuna-asgro con PARTES de largo variable.
#   python build.py                 -> salida/cuna-chepica-jose-cepeda-9x16.mp4""")
rep(r"PARTES = [('parte1.mov', 0.0, 38.92), ('parte2.mp4', 0.0, 27.1)]",
    r"PARTES = [('cuna.mp4', 11.72, 129.95)]  # desde «Hay una gran cantidad de agricultores…» hasta «…lo que está pasando.»")
rep(r"""EDITS = [
    (['combustibles', 'a', 'hacer', 'este', 'tema.'], ['combustibles.']),  # tramo poco claro en el audio
]""", "EDITS = []")
rep(r"""NOMBRE = 'Camilo Jiménez'
CARGO = ['Vocero de la Asociación', 'Gremial Rengo O\'Higgins', '(ASGRO)']""",
    r"""NOMBRE = ('José', 'Cepeda')
CARGO = ['Dirigente agricultor', 'Comuna de Chépica']
FOTO = 'jose.jpg'""")
rep(r"""    filt.append(f'[a0][a1]acrossfade=d={XFADE}:c1=tri:c2=tri,highpass=f=70,'
                'loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[out]')""",
    r"""    cadena = '[a0]'
    for k in range(1, len(PARTES)):
        filt.append(f'{cadena}[a{k}]acrossfade=d={XFADE}:c1=tri:c2=tri[x{k}]')
        cadena = f'[x{k}]'
    filt.append(f'{cadena}highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[out]')""")
rep("for k, clave in enumerate(('audio1', 'audio2')):",
    "for k, clave in enumerate(f'audio{j + 1}' for j in range(len(PARTES))):")
rep("off += (z - a) - (XFADE if k == 0 else 0)", "off += (z - a) - XFADE")
rep(r"""    e = ease((t - b['ini']) / 0.12)
    d = ImageDraw.Draw(capa)
    alto = 70
    y0 = Y_SUB + 10 * (1 - e)""", r"""    e = 1.0  # en seco: aparece de golpe, sin fundido ni subida
    d = ImageDraw.Draw(capa)
    alto = 70
    y0 = Y_SUB""")
rep(r"""    foto = Image.open(os.path.join(AQUI, 'fuentes', 'camilo.png')).convert('RGB')
    # recorte 3:4 con la cara arriba
    fw, fh = foto.size
    ch = int(fw * h / w)
    foto = foto.crop((0, 18, fw, 18 + ch)).resize((w, h), Image.LANCZOS)""",
    r"""    foto = Image.open(os.path.join(AQUI, 'fuentes', FOTO)).convert('RGB')
    # recorte 3:4 de la foto cuadrada, centrado en la cara (x≈178 de 335)
    fw, fh = foto.size
    cw = int(fh * w / h)
    x0 = max(0, min(fw - cw, 178 - cw // 2))
    foto = foto.crop((x0, 0, x0 + cw, fh)).resize((w, h), Image.LANCZOS)""")
rep("N1 = texto('Camilo',", "N1 = texto(NOMBRE[0],")
rep("N2 = texto('Jiménez',", "N2 = texto(NOMBRE[1],")
rep("C_ASGRO = texto('ASGRO', fuente('s', 'Bold', 34), VERDE)\n", "")
rep(r"""def componer(t, lector, env, subs, dur, t_cambio):
    k = 0 if t < t_cambio else 1
    tl = t - (0 if k == 0 else t_cambio)""", r"""def componer(t, lector, env, subs, dur, cambios):
    k = sum(1 for c in cambios if t >= c)
    tl = t - ([0.0] + cambios)[k]""")
rep(r"""    if 0 <= t - t_cambio < 0.16:""", r"""    t_cambio = max([c for c in cambios if c <= t], default=-9)
    if 0 <= t - t_cambio < 0.16:""")
rep(r"""    t_cambio = (PARTES[0][2] - PARTES[0][1]) - XFADE
""", r"""    cambios, acc = [], 0.0
    for f, a, z in PARTES[:-1]:
        acc += (z - a) - XFADE
        cambios.append(acc)
""")
rep("cambio de parte en {t_cambio:.2f} s'", "cambios de parte en {cambios}'")
s = s.replace("subs, dur, t_cambio)", "subs, dur, cambios)")
rep("'cuna-asgro-camilo-jimenez-9x16.mp4'", "'cuna-chepica-jose-cepeda-9x16.mp4'")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
