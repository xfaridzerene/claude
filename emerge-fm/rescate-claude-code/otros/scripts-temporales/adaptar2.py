import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b)
rep("# Reel vertical de la cuña de José Cepeda (dirigente agricultor, Chépica) en Emerge Noticias.\n# Arriba: foto de José",
    "# Reel vertical de la cuña de Camilo Jiménez (ASGRO): rebaja de $300 en combustibles.\n# Abre con un DESTACADO (la frase de los 300 pesos) y luego la cuña completa.\n# Arriba: foto de Camilo")
rep("PARTES = [('cuna.mp4', 11.72, 129.95)]  # desde «Hay una gran cantidad de agricultores…» hasta «…lo que está pasando.»",
    "PARTES = [('cuna.mp4', 29.80, 38.00),   # DESTACADO: «Estamos pidiendo una reducción de 300 pesos… negociaciones»\n          ('cuna.mp4', 0.0, 77.0)]      # cuña completa\nTRANS = ['audio1', 'audio1']           # clave de transcripcion.json para cada parte\nETIQUETAS = ['DESTACADO', 'CUÑA COMPLETA']  # chip sobre el video al inicio de cada parte\nDUR_ETIQUETA = [None, 2.5]             # None = toda la parte")
rep("NOMBRE = ('José', 'Cepeda')\nCARGO = ['Dirigente agricultor', 'Comuna de Chépica']\nFOTO = 'jose.jpg'",
    "NOMBRE = ('Camilo', 'Jiménez')\nCARGO = ['Vocero de la Asociación', \"Gremial Rengo O'Higgins\", '(ASGRO)']\nFOTO = 'camilo.png'\nFOTO_CX, FOTO_Y = None, 18   # centro x de la cara (None = centro) y recorte superior")
rep("for k, clave in enumerate(f'audio{j + 1}' for j in range(len(PARTES))):",
    "for k, clave in enumerate(TRANS):")
rep("""    # recorte 3:4 de la foto cuadrada, centrado en la cara (x≈178 de 335)
    fw, fh = foto.size
    cw = int(fh * w / h)
    x0 = max(0, min(fw - cw, 178 - cw // 2))
    foto = foto.crop((x0, 0, x0 + cw, fh)).resize((w, h), Image.LANCZOS)""",
"""    # recorte 3:4: si la foto es más ancha se recorta a lo ancho (centrado en FOTO_CX),
    # si es más alta se recorta abajo dejando la cara arriba (FOTO_Y)
    fw, fh = foto.size
    if fw / fh > w / h:
        cw = int(fh * w / h)
        cx = FOTO_CX if FOTO_CX is not None else fw // 2
        x0 = max(0, min(fw - cw, cx - cw // 2))
        foto = foto.crop((x0, 0, x0 + cw, fh))
    else:
        ch = int(fw * h / w)
        y0 = max(0, min(fh - ch, FOTO_Y))
        foto = foto.crop((0, y0, fw, y0 + ch))
    foto = foto.resize((w, h), Image.LANCZOS)""")
rep("C_LINEAS = [texto(c, fuente('s', 'Medium', 34), (215, 215, 215)) for c in CARGO]\n",
    "C_LINEAS = [texto(c, fuente('s', 'Medium', 34), (215, 215, 215)) for c in CARGO]\nCHIPS_PARTE = [chip(e, fuente('u', 'Bold', 30), VERDE, (0, 0, 0), padx=24, pady=14, esp=3) if e else None for e in ETIQUETAS]\n")
rep("""    # subtítulo vigente""", """    # etiqueta de la parte (en seco)
    ch = CHIPS_PARTE[k]
    if ch is not None and (DUR_ETIQUETA[k] is None or tl < DUR_ETIQUETA[k]):
        pegar(capa, ch, 36, BOX_Y + 28)

    # subtítulo vigente""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
