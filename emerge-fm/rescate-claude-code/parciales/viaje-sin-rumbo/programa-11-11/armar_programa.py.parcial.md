# viaje-sin-rumbo/programa-11-11/armar_programa.py (parcial)

Ruta original: `C:/Users/farid/Desktop/claude code/viaje-sin-rumbo/programa-11-11/armar_programa.py`

## Cambios hechos sin conocer el archivo completo

### 2026-11-11T13:15

Antes:
```
# Las voces del martes se pisaron en Descargas con las del miércoles (mismos nombres).
# Estas son las mismas, extraídas sin cambios de la pista de voz del primer armado;
# la 18 ya viene sin las partes (QUITAR).
VOCES
```
Después:
```
# Copia de las voces del día (en Descargas se pisan con los mismos nombres cada día).
VOCES
```

### 2026-11-11T13:15

Antes:
```
    A[k] = norm(trim(load(MUS / f), -50, 0.02), SONG_LUFS)
for k, f in voices.items():
    x = load(f)  # sin tocar
    if k == "18" and not str(f).endswith("voces\\18.wav"):  # voces/18.wav ya viene cortada
        print(" locución 18: quitando las partes (QUITAR) de Chico Trujillo")
        x = splice(x, [(20.20, 21.10, 41.95, 43.10),   # "Para despedirnos… cruza generaciones."
                       (56.65, 57.25, 61.15, 62.10)])  # "Te quedas con Chico Trujillo y su canción loca."
        sf.write(OUT / "18. LOCUCIÓN (sin partes QUITAR).wav", x[:, 0].astype(np.float32), SR, subtype="PCM_24")
    raw
```
Después:
```
    A[k] = norm(trim(load(f), -50, 0.02), SONG_LUFS)
for k, f in voices.items():
    x = load(f)
    raw
```

### 2026-11-11T13:15

Antes:
```
songs = {
    "01 La Ley – El Duelo": "La ley - El duelo.mp3",
    "02 Cinema – Locos Rayados": "Locos Rayados - Cinema.mp3",
    "03 Electrodomésticos – Has Sabido Sufrir": "Electrodomesticos - Has Sabido Sufrir.mp3",
    "04 Los Tetas – Papi, ¿dónde está el funk?": "Los Tetas - Papi ¿Dónde Esta El Funk.mp3",
    "05 Chancho en Piedra – Guach Perry": "Guach Perry - Chancho En Piedra.mp3",
    "06 Gepe – Por la Ventana": "Por La Ventana - Gepe - Audiovisión (2010).mp3",
    "07 Valija Diplomática – Tú lo Sabes Bien": "Tú Lo Sabes Bien (Remaster 2002) - Valija Diplomatica.mp3",
    "08 Aparato Raro – Calibraciones": "Aparato Raro  - Calibraciones 1985.mp3",
    "09 Los Tres – Moizéfala": "Moizefala - Los Tres.mp3",
    "10 Dënver – Revista de Gimnasia": "Revista De Gimnasia - Dënver.mp3",
}
```
Después:
```
def find(prefix):
    """Busca el archivo por el comienzo del nombre (los acentos vienen en NFD)."""
    for d in (DL, MUS):
        hit = sorted(p for p in d.glob("*.mp3") if p.name.startswith(prefix))
        if hit: return hit[0]
    raise FileNotFoundError(prefix)

songs = {
    "01 Myriam Hernández – Huele a Peligro": find("Myriam Hern"),
    "02 Javiera Mena – Hasta la Verdad": find("Javiera Mena - Hasta"),
    "03 Saiko – Lo que Mereces": find("Lo Que Mereces"),
    "04 Ana Tijoux – 1977": find("Ana Tijoux - 1977"),
    "05 Nicole – Solo el Mar": find("Solo El Mar - Nicole"),
    "06 Princesa Alba – Tus Estaciones": find("Princesa Alba"),
    "07 Paloma Mami – Cosas de la Vida": find("Paloma Mami"),
    "08 Mamma Soul – Eternamente": find("MAMMA SOUL"),
    "09 Javiera y Los Imposibles – Y Esperaré": find("Y Esper"),
    "10 Francisca Valenzuela – Qué Sería": find("Que Ser"),
    "11 Camila Moreno – Millones": find("Camila Moreno - Millones"),
}
```

### 2026-11-11T13:15

Antes:
```
locucion("1", "1  Saludo, editorial y presentación de La Ley")
song("01 La Ley – El Duelo")
song("02 Cinema – Locos Rayados")
locucion("4", "4  Historia: Electrodomésticos")
song("03 Electrodomésticos – Has Sabido Sufrir")
song("04 Los Tetas – Papi, ¿dónde está el funk?")
locucion("7", "7  Artista / disco: Chancho en Piedra")
song("05 Chancho en Piedra – Guach Perry")
song("06 Gepe – Por la Ventana")
```
Después:
```
locucion("1", "1  Saludo, editorial y presentación de Myriam Hernández")
song("01 Myriam Hernández – Huele a Peligro")
song("02 Javiera Mena – Hasta la Verdad")
locucion("4", "4  Historia: Saiko")
song("03 Saiko – Lo que Mereces")
song("04 Ana Tijoux – 1977")
locucion("7", "7  Artista / disco: Nicole, Esperando Nada")
song("05 Nicole – Solo el Mar")
song("06 Princesa Alba – Tus Estaciones")
```

### 2026-11-11T13:15

Antes:
```
locucion("12", "11 + 12  Regreso de tanda · Especial Nuevo Pop", bed_overlap=0.0)
song("07 Valija Diplomática – Tú lo Sabes Bien")
song("08 Aparato Raro – Calibraciones")
locucion("15", "15  Algo que me guste: Los Tres")
song("09 Los Tres – Moizéfala")
song("10 Dënver – Revista de Gimnasia")
locucion("18", "18 + 19  Cierre y MENCIONES finales (sin Chico Trujillo)",
         tipo="LOCUCIÓN + MENCIONES (con cortina)", post=1.6)
add("CORTINA DE CIERRE – Despedida Viaje sin Rumbo", "despedida", overlap=0.4, fin=0.4, tipo="CORTINA")
```
Después:
```
locucion("12", "11 + 12  Regreso de tanda · Cumpleaños de Paloma Mami", bed_overlap=0.0)
song("07 Paloma Mami – Cosas de la Vida")
song("08 Mamma Soul – Eternamente")
locucion("15", "15  Algo que me guste: Javiera y Los Imposibles")
song("09 Javiera y Los Imposibles – Y Esperaré")
song("10 Francisca Valenzuela – Qué Sería")
locucion("18", "18 + 19  Cierre y MENCIONES finales", tipo="LOCUCIÓN + MENCIONES (con cortina)")
song("11 Camila Moreno – Millones")
add("CORTINA DE CIERRE – Despedida Viaje sin Rumbo", "despedida", overlap=0.5, fin=0.5, tipo="CORTINA")
```

### 2026-11-11T13:15

Antes:
```
name = "Viaje sin Rumbo - 10-11-2026 - Nuevo Pop"
```
Después:
```
name = "Viaje sin Rumbo - 11-11-2026 - Reinas del Pop"
```

### 2026-11-11T13:15

Antes:
```
lines = [f"VIAJE SIN RUMBO – MARTES 10-11-2026 – EL NUEVO POP CHILENO DE LOS 80 (duración {fmt(total)})", ""]
```
Después:
```
lines = [f"VIAJE SIN RUMBO – MIÉRCOLES 11-11-2026 – REINAS DEL POP: LAS MUJERES DE LA MÚSICA CHILENA (duración {fmt(total)})", ""]
```

### 2026-11-11T13:15

Antes:
```
# Viaje sin Rumbo – martes 10-11-2026 – "El Nuevo Pop chileno de los 80".
# Correr con: C:\Users\farid\audio-env\Scripts\python.exe armar_programa.py
#
# Reglas de este programa:
#  - La VOZ se nivela solo con ganancia (sin EQ, compresor ni limpieza) y un
#    limitador con anticipación para los picos sueltos. En la locución 18 se sacan las dos
#    partes marcadas (QUITAR) de la pauta (lo de Chico Trujillo), cortando en silencio.
#  - "Loca" de Chico Trujillo no va: después del "Chao" entra la cortina de cierre.
```
Después:
```
# Viaje sin Rumbo – miércoles 11-11-2026 – "Reinas del pop: las mujeres de la música chilena".
# Correr con: C:\Users\farid\audio-env\Scripts\python.exe armar_programa.py
#
# Reglas de este programa (igual que el martes):
#  - La VOZ se nivela solo con ganancia (sin EQ, compresor ni limpieza) y un
#    limitador con anticipación para los picos sueltos. Todo parejo a -18 LUFS.
```

### 2026-11-11T13:18

Antes:
```
music = np.zeros((s(66 * 60), 2))
```
Después:
```
music = np.zeros((s(66 * 60), 2), np.float32)
```
