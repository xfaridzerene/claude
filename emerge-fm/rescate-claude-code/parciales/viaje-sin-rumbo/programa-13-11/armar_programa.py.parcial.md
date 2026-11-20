# viaje-sin-rumbo/programa-13-11/armar_programa.py (parcial)

Ruta original: `C:/Users/farid/Desktop/claude code/viaje-sin-rumbo/programa-13-11/armar_programa.py`

## Líneas leídas en alguna sesión

Número de línea del archivo original, luego el texto.

```
   95  def find(prefix):
   96      """Busca el archivo por el comienzo del nombre (los acentos vienen en NFD)."""
   97      for d in (DL, MUS):
   98          hit = sorted(p for p in d.glob("*.mp3") if p.name.startswith(prefix))
   99          if hit: return hit[0]
  100      raise FileNotFoundError(prefix)
  101  
  102  songs = {
  103      "01 Glup! – Free-bola": find("Glup!"),
  104      "02 Bronko Yotte – Lumbre": find("Bronko Yotte"),
  105      "03 Los Prisioneros – No Necesitamos Banderas": find("No Necesitamos"),
  106      "04 Emociones Clandestinas – Mi Nuevo Estilo de Baile": find("Un Nuevo Baile"),
  107      "05 Fiskales Ad-Hok – El Cóndor": next(DL.glob("El C*- Fiskales Ad-Hok.mp3")),
  108      "06 La Floripondio – Bailando como Mono": find("Bailando Como Mono"),
  109      "07 Sinergia – Síndrome Camboya": next(DL.glob("*- Sinergia.mp3")),
  110      "08 Los Ex – La Corbata de mi Tío": find("La Corbata"),
  111      "09 Álex Anwandter – Siempre es Viernes en mi Corazón": find("Alex Anwandter"),
  112      "10 Tiro de Gracia – El Juego Verdadero": find("Tiro De Gracia"),
  113      "11 Difuntos Correa – El Tiempo en las Bastillas": find("El Tiempo En Las"),
  114  }
  115  # Copia de las voces del día (en Descargas se pisan con los mismos nombres cada día).
  116  VOCES = Path(__file__).resolve().parent / "voces"
  117  voices = {k: VOCES / f"{k}.wav" for k in ["1", "4", "7", "10", "12", "15", "18"]}
  118  
  119  print("cargando…", flush=True)
```
