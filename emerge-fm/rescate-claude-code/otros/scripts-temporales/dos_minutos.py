import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b)


rep("""    'GOBERNADOR': dict(tramos=[('IMG_0189', 29.40, 35.75), ('IMG_0188', 0.55, 16.25), ('IMG_0189', 0.0, 144.10)],""",
    """    # Versión ~2 min: fuera el «un gusto tenerlo», INDAP/inclusión, la explicación de la organización
    # de gremios, «nos plantearon la posibilidad…» y el agradecimiento del entrevistador.
    'GOBERNADOR': dict(tramos=[('IMG_0189', 29.40, 35.75),   # gancho: $20.000 millones
                               ('IMG_0188', 0.55, 3.20),     # «Pablo Silva Amaya, gobernador…»
                               ('IMG_0188', 8.20, 16.25),    # «La región ha ido avanzando… ¿no?»
                               ('IMG_0189', 0.0, 16.85),     # «…que es maravilloso…» turismo
                               ('IMG_0189', 25.90, 40.45),   # municipios … «mundo público y privado,»
                               ('IMG_0189', 56.07, 68.76),   # «el objetivo es cómo empujamos…» … agricultura
                               ('IMG_0189', 72.55, 96.30),   # «en este momento hay una planta…»
                               ('IMG_0189', 96.70, 123.80),  # ProChile, Sernatur, desempleo
                               ('IMG_0189', 138.20, 144.10)],  # «desear el mayor de los éxitos…»""")
rep("""    'IMG_0203': dict(gancho=(120.62, 127.00), tramo=(0.0, 127.00), salida='eneo-seremi-mineria',""",
    """    # Versión ~2 min: pregunta acortada, fuera «hace muy poco estuvimos» y el párrafo de Coresemin.
    'IMG_0203': dict(tramos=[('IMG_0203', 120.62, 127.00),  # gancho
                             ('IMG_0203', 0.0, 2.65),       # «Bueno, Seremi de Minería,»
                             ('IMG_0203', 9.95, 64.95),     # «preguntarle sobre la cartera…»
                             ('IMG_0203', 66.90, 83.20),    # «estamos fuertemente como desafío…»
                             ('IMG_0203', 94.70, 127.00)],  # pequeña minería … «lo necesitan.»
                     salida='eneo-seremi-mineria',""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
