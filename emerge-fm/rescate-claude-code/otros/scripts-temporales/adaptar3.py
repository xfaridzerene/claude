import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b)
rep("""# Reel vertical de la cuña de Camilo Jiménez (ASGRO): rebaja de $300 en combustibles.
# Abre con un DESTACADO (la frase de los 300 pesos) y luego la cuña completa.
# Arriba: foto de Camilo""", """# Reel vertical: Nicolás Larenas (Asociación Agricultores Unidos) en Emerge Noticias.
# Dos tramos elegidos por el usuario, unidos con un destello.
# Arriba: foto de Nicolás (fuentes/larenas.png, hecha cuadrada con foto_cuadrada.py)""")
rep("cuna-rebaja-300-camilo-jimenez-9x16.mp4", "larenas-agricultores-unidos-9x16.mp4")
rep("""PARTES = [('cuna.mp4', 29.80, 38.00),   # DESTACADO: «Estamos pidiendo una reducción de 300 pesos… negociaciones»
          ('cuna.mp4', 0.0, 77.0)]      # cuña completa""",
"""PARTES = [('cuna.mp4', 19.32, 59.10),    # «lo que nosotros queremos es primero plantearle al gobierno…» → «…al mundo agrícola en general.»
          ('cuna.mp4', 71.42, 113.92)]   # «Hoy día no tenemos para salir a trabajar…» → «…hoy día no vamos a avanzar.»""")
rep("EDITS = []", """EDITS = [
    (['prestador', 'que', 'se', 'va', 'a', 'comprar.', 'Al', 'servicio,'], ['prestador', 'de', 'servicios,']),  # verificado con 2 modelos
    (['exportas'], ['ad', 'portas']),
    (['apalear'], ['paliar']),
    (['fermas'], ['bermas']),
]""")
rep("""NOMBRE = ('Camilo', 'Jiménez')
CARGO = ['Vocero de la Asociación', "Gremial Rengo O'Higgins", '(ASGRO)']
FOTO = 'camilo.png'
FOTO_CX, FOTO_Y = None, 18""", """NOMBRE = ('Nicolás', 'Larenas')
CARGO = ['Dirigente Asociación', 'Agricultores Unidos']
FOTO = 'larenas.png'
FOTO_CX, FOTO_Y = 385, 0""")
rep("""                rep = [dict(p=p, ini=ini, fin=fin) for p in nuevo]""",
"""                paso = (fin - ini) / len(nuevo)  # repartir el tramo entre las palabras nuevas
                rep = [dict(p=p, ini=ini + j * paso, fin=ini + (j + 1) * paso) for j, p in enumerate(nuevo)]
                if out[i].get('nuevo'):
                    rep[0]['nuevo'] = True""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
