# Rescate de la carpeta `Desktop\claude code`

Hecho el 20 de noviembre de 2026 sin acceso al PC. Revisé todas las sesiones de Claude Code que trabajaron en esa carpeta y llegan a la nube (unas 75 páginas de conversación, 1.600 operaciones con archivos). Reconstruí cada archivo reproduciendo en orden lo que se hizo con él: cuándo se creó, cuándo se leyó completo y cada edición posterior. Así se recupera la **última versión conocida** de cada uno.

## Qué hay aquí

| Carpeta o archivo | Contenido |
|---|---|
| `CATALOGO-DE-PROYECTOS.md` | Los 52 proyectos del índice de memoria, con su descripción, y las 30 carpetas encontradas con cuánto se recuperó de cada una. **Empieza por aquí.** |
| `INVENTARIO-DE-ARCHIVOS.md` | Los 367 archivos que aparecen en las sesiones, uno por uno, con su estado: recuperado, parcial o solo nombre. |
| `claude-code/` | Los 74 archivos recuperados completos, con la misma estructura de carpetas que en el PC. Incluye la skill `.claude/skills/nota-estilo-bbcl`. |
| `parciales/` | Los archivos de los que solo quedaron algunas líneas o cambios sueltos. |
| `memoria/` | 24 notas de memoria completas (el resumen de cada proyecto que Claude guardaba en tu PC) y el índice `MEMORY.md` con las 52. |
| `otros/` | Fragmentos de `Desktop\EMERGE FM\control-de-radio.html` y scripts de apoyo que quedaron en carpetas temporales. |

## Lo más valioso que se recuperó

- **GC de Emerge Noticias** completo: `gc-noticias.html`, `panel-noticias.html`, `base-noticias.html` y el instructivo para OBS.
- **Panel del GC de La Ciudad de la Furia** (`furia-promo/gc/`) con su instructivo.
- **Láminas y pendón**: el motor completo (`emerge-lamina/tools/`: `build.py`, `dial.py`, `grande.py`, `pendon.py`).
- **Viaje sin Rumbo**: el script de armado de cada programa, del 9 al 20 de noviembre (los del 17 al 20, reconstruidos aplicando los cambios de cada día).
- **Reels**: los scripts de La Ciudad de la Furia (`reel-furia/`), ENEO 2026, primer día al aire, despacho de Rengo, noticia «radio confiable», cuña ASGRO y plantillas de entrevista.
- **Frases institucionales**: todo el proceso de limpieza y ecualización (`furia_audio/`), con las listas de frases.
- **YouTube**: `emerge-youtube/youtube.html`, con los textos de cada programa.
- **Skill de notas estilo BioBioChile** y los jingles de prueba (`scratch_jingle*.py`).

## Lo que no se pudo recuperar y por qué

1. **Imágenes, audio, video, PDF y zip.** Las sesiones solo registran texto, así que de esos archivos solo queda el nombre. Están en el inventario como «solo nombre».
2. **Proyectos hechos en sesiones locales de la app de escritorio.** Esas conversaciones viven solo en tu PC y no llegan a la nube. Entre ellas están el tema WordPress (`emerge-tema`, 89 archivos de los que solo se conoce el nombre), la intro y el GC de Emerge tu mañana, la sintonía, el imán, el loop de Viaje sin Rumbo, la musicoteca y el sistema de auspiciadores. Las sesiones locales que alcancé a ver listadas son:

| Última actividad | Sesión local |
|---|---|
| 04-10 | Animación promocional Viaje sin Rumbo |
| 06-10 | Waretrack: almacén como videojuego |
| 09-10 | Juego estilo GTA en Rancagua |
| 11-10 | Corrección de color y estabilidad de viaje |
| 13-10 | Base de datos de canciones para radio |
| 15-10 | Serie de posts Instagram para radio |
| 20-10 | Sistema de auspiciadores para radio |
| 26-10 | Gráfica de cancha para streaming de fútbol |
| 03-11 | Animación para reel de lanzamiento |
| 04-11 | Widget OBS para Radio Boss |
| 06-11 | GC |
| 07-11 | Diseño Claude a tema WordPress |
| 07-11 | Transmitir OBS y audio en la web de Emerge FM |
| 08-11 | Loop emerge para streaming standby |

Probablemente hay más; estas son solo las que aparecieron en una búsqueda.

## Ojo al usar estos archivos

- Es la **última versión que vio Claude**. Si después cambiaste algo a mano en el PC, aquí no está.
- Los scripts tienen rutas de tu PC (`C:\Users\farid\...`, `E:\...`) y usan el entorno de Python `C:\Users\farid\audio-env`. Para correrlos en otro equipo hay que ajustar esas rutas.
- Cuando vuelvas a tener el PC, lo más completo es pedirle a una sesión de la app de escritorio que suba la carpeta `claude code` entera a GitHub, sin los videos.
