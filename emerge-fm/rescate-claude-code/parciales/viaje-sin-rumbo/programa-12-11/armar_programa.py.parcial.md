# viaje-sin-rumbo/programa-12-11/armar_programa.py (parcial)

Ruta original: `C:/Users/farid/Desktop/claude code/viaje-sin-rumbo/programa-12-11/armar_programa.py`

## Cambios hechos sin conocer el archivo completo

### 2026-11-12T14:32

Antes:
```
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
Después:
```
songs = {
    "01 Glup! – Free-bola": find("Glup!"),
    "02 Bronko Yotte – Lumbre": find("Bronko Yotte"),
    "03 Los Prisioneros – No Necesitamos Banderas": find("No Necesitamos"),
    "04 Emociones Clandestinas – Mi Nuevo Estilo de Baile": find("Un Nuevo Baile"),
    "05 Fiskales Ad-Hok – El Cóndor": find("El C"),
    "06 La Floripondio – Bailando como Mono": find("Bailando Como Mono"),
    "07 Sinergia – Síndrome Camboya": find("Sındrome") if False else next(p for p in DL.glob("*Sinergia.mp3")),
    "08 Los Ex – La Corbata de mi Tío": find("La Corbata"),
    "09 Álex Anwandter – Siempre es Viernes en mi Corazón": find("Alex Anwandter"),
    "10 Tiro de Gracia – El Juego Verdadero": find("Tiro De Gracia"),
    "11 Difuntos Correa – El Tiempo en las Bastillas": find("El Tiempo En Las"),
}
```

### 2026-11-12T14:32

Antes:
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
Después:
```
locucion("1", "1  Saludo, editorial y presentación de Glup!")
song("01 Glup! – Free-bola")
song("02 Bronko Yotte – Lumbre")
locucion("4", "4  Historia: No Necesitamos Banderas")
song("03 Los Prisioneros – No Necesitamos Banderas")
song("04 Emociones Clandestinas – Mi Nuevo Estilo de Baile")
locucion("7", "7  Artista / disco: Fiskales Ad-Hok")
song("05 Fiskales Ad-Hok – El Cóndor")
song("06 La Floripondio – Bailando como Mono")
```

### 2026-11-12T14:32

Antes:
```
locucion("12", "11 + 12  Regreso de tanda · Cumpleaños de Paloma Mami", bed_overlap=0.0)
song("07 Paloma Mami – Cosas de la Vida")
song("08 Mamma Soul – Eternamente")
locucion("15", "15  Algo que me guste: Javiera y Los Imposibles")
song("09 Javiera y Los Imposibles – Y Esperaré")
song("10 Francisca Valenzuela – Qué Sería")
locucion("18", "18 + 19  Cierre y MENCIONES finales", tipo="LOCUCIÓN + MENCIONES (con cortina)")
song("11 Camila Moreno – Millones")
```
Después:
```
locucion("12", "11 + 12  Regreso de tanda · Especial: Sinergia y Los Ex", bed_overlap=0.0)
song("07 Sinergia – Síndrome Camboya")
song("08 Los Ex – La Corbata de mi Tío")
locucion("15", "15  Algo que me guste: Álex Anwandter")
song("09 Álex Anwandter – Siempre es Viernes en mi Corazón")
song("10 Tiro de Gracia – El Juego Verdadero")
locucion("18", "18 + 19  Cierre y MENCIONES finales", tipo="LOCUCIÓN + MENCIONES (con cortina)")
song("11 Difuntos Correa – El Tiempo en las Bastillas")
```

### 2026-11-12T14:32

Antes:
```
name = "Viaje sin Rumbo - 11-11-2026 - Reinas del Pop"
sf.write(OUT / f"{name}.wav", mix, SR, subtype="PCM_24")
sf.write(OUT / f"{name} - PISTA VOZ.wav", voice, SR, subtype="PCM_24")
sf.write(OUT / f"{name} - PISTA MUSICA Y CORTINAS.wav", music, SR, subtype="PCM_24")
```
Después:
```
name = "Viaje sin Rumbo - 12-11-2026 - Los Irreverentes"
sf.write(OUT / f"{name}.wav", mix, SR, subtype="PCM_24")   # solo el programa final, sin pistas separadas
```

### 2026-11-12T14:32

Antes:
```
lines = [f"VIAJE SIN RUMBO – MIÉRCOLES 11-11-2026 – REINAS DEL POP: LAS MUJERES DE LA MÚSICA CHILENA (duración {fmt(total)})", ""]
```
Después:
```
lines = [f"VIAJE SIN RUMBO – JUEVES 12-11-2026 – LOS IRREVERENTES (duración {fmt(total)})", ""]
```

### 2026-11-12T14:32

Antes:
```
# Viaje sin Rumbo – miércoles 11-11-2026 – "Reinas del pop: las mujeres de la música chilena".
```
Después:
```
# Viaje sin Rumbo – jueves 12-11-2026 – "Los irreverentes". Entrega solo la mezcla final.
```
