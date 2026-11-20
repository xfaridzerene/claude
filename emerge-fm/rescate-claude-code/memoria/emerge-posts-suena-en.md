---
name: emerge-posts-suena-en
description: Serie Instagram «Suena en ___ y en Emerge» (canciones que aparecen en TikTok/GTA/etc. y suenan en la radio); guiones en emerge-posts-suena-en/guiones.md
metadata:
  node_type: memory
  type: project
  originSessionId: 2843c7dd-5cf9-44e2-a0c2-14250f5d41a4
  modified: 2026-10-15T15:54:42.197Z
---

Serie de posts de Instagram de [[radio-emerge-fm]], iniciada el 2026-10-14. Guiones en `C:\Users\farid\Desktop\claude code\emerge-posts-suena-en\guiones.md`.

Decisiones del usuario: nombre «Suena en ___ y en Emerge»; carrusel de 5 láminas 1080×1350 (portada, historia, en la plataforma, dato, cierre); series TikTok, GTA, Halloween, Netflix/cine, RCP/memes, hora loca chilena. *I'm Still Standing* no estaba en la biblioteca y decidió agregarla a la radio.

El 14 oct el usuario pidió **no limitarse a la biblioteca**: valen clásicos 80/90 que *podrían* sonar en Emerge (marcar ✅ ya está / ➕ por sumar). La serie GTA v2 (`guiones-gta.md`) es una cuenta regresiva de 14 posts hasta el lanzamiento de GTA VI (19 nov 2026), con los temas de sus trailers (Tom Petty, Pointer Sisters).

Diseño (14 oct): plantilla `diseno/carrusel.html` + un archivo de datos por post en `diseno/posts/<id>.js`; `python diseno/exportar.py gta-01` exporta los 5 PNG con Chrome headless a `diseno/salida/<id>/` (más una hoja de contacto). Estilo: fondo negro, anillos #141414 de textura, títulos Unbounded Black ajustados al ancho, color de serie naranja, cuenta regresiva en ámbar y un dial FM que sigue de lámina en lámina (87–107 MHz) y termina con la aguja verde en 105.5. Cuidado: medir el texto con la lámina visible y cargar las fuentes con `document.fonts.load`; el navegador de la app no ejecuta el JS de archivos locales, por eso se revisa con el PNG exportado.

Formato aprobado por el usuario el 14 oct (#01 y #02 diseñados):
- La portada lleva gigante «SUENA EN / GTA / Y EN EMERGE» y abajo la carátula oficial (iTunes, 1200 px) junto al título.
- Las láminas 2–4 son un **relato cronológico**: año en recuadro naranja sobre una imagen (foto real · televisor con un cuadro de época · captura del juego) y una frase final en naranja que lleva a la siguiente.
- Imágenes en `diseno/imagenes/<post>/` con su `FUENTES.md` (licencia y crédito). Las capturas de Steam de Vice City están en `imagenes/gta-vice-city/`; se usaron la 3317 (#01) y la 3320 (#02), y se evitan las que muestran armas.
- Cada lote de descargas se le pide aprobar antes, indicando archivo, fuente y tamaño.

Otras series:
- **Especial Halloween** (`posts/halloween.js`): un solo carrusel con 3 canciones, color violeta. El nombre de cada canción va como titular sobre su imagen, sin etiqueta «Canción N».
- **Cine** (`propuesta-cine.md`): el usuario eligió 5 canciones (Eye of the Tiger, Take My Breath Away, Don't You Forget About Me, I Will Always Love You, My Heart Will Go On), una por carrusel, **atemporales** (sin fechas ni calendario), en color azul. Netflix quedó fuera.

Plantilla para Canva (15 oct): `plantilla-canva/plantilla-suena-en-emerge.pptx`, 7 láminas editables (portada, foto, TV, imagen a todo el ancho, cierre, sala de cine, gráfico de texto), con su guía `COMO-USAR-EN-CANVA.md` y los fondos sueltos. Se genera con `diseno/medir.py` (mide el HTML en Chrome con `?medir=1`) y `diseno/plantilla_pptx.py` (python-pptx, instalado el 15 oct). Para la revisión se renderiza con el PowerPoint del usuario vía COM; en este PC no hay LibreOffice ni Node. No se probó la importación dentro de Canva.

Color de GTA (15 oct): rosado neón **#FF6EC7**, inspirado en GTA VI. El usuario pidió «el rosado del manual», pero el manual no trae rosado. Se probaron dos (fucsia #FF2E7E y neón #FF6EC7) y eligió el neón. Va en `color` de cada `posts/gta-*.js`; el naranja #FF6B35 es solo el valor por defecto. La plantilla de Canva todavía muestra GTA en naranja.

Sin cuenta regresiva (15 oct): el usuario la quitó de los posts GTA. La etiqueta amarilla se mantiene, pero ahora lleva **un gancho de la historia** en mayúsculas (#01 «El primer video de MTV», #02 «La del moonwalk», #03 «Suena en el desierto», #04 «La de los 99 globos»). Está en el campo `cuentaRegresiva` de cada post; el nombre del campo quedó por compatibilidad. Los posts GTA ya no dependen del lanzamiento de GTA VI.

Serie **memes** (15 oct, propuesta en `propuesta-memes.md`): **los 4 carruseles ya están diseñados** (`posts/memes-01..04.js`); el #03 lleva una lámina de video. Color ámbar #FFC93C; por eso la etiqueta de la portada va en blanco en esta serie. Lleva 4 carruseles:
- M1 *Never Gonna Give You Up*: el rickroll nació en 2007 de un falso link al trailer de GTA IV.
- M2 *All Star*: no se hizo para Shrek.
- M3 *Take On Me*: el primer «video literal», de 2008.
- M4 *Running in the 90s* ➕: Initial D y los derrapes.

Quedaron fuera *What Is Love* y *Careless Whisper*; Sandstorm y The Final Countdown, de reserva. *Total Eclipse of the Heart* se excluyó porque Bonnie Tyler murió el 8 jul 2026; queda la opción de un post de homenaje aparte.

Lámina de video (15 oct): un post puede llevar `video: { despues: N, etiqueta, grande, sigue, credito }` y queda en 6 láminas (TOTAL y el dial se recalculan solos). La lámina muestra una caja 4:3 (CAJA_VIDEO en carrusel.html y en video_lamina.py). Con `python diseno/video_lamina.py <post> <video>` se monta el MP4 1080×1350 con audio, de hasta 60 s.

Se usó en Memes #03 para el video literal de Take On Me. No se descargó de YouTube (condiciones de uso y derechos): el usuario debe conseguir el archivo, idealmente con permiso del autor.

Serie **hora loca** (15 oct, `propuesta-hora-loca.md`, sin diseñar). Color naranja #FF6B35, el único libre. Son 5 carruseles, todos con la canción en la radio:
1. *Pump Up the Jam*: la cara del video no era la voz.
2. *Gonna Make You Sweat*: Martha Wash.
3. *Rhythm Is a Dancer*: el rapero no la quería.
4. *Jump Around*: Cypress Hill no pudo rapearla; el salto de Wisconsin.
5. *Lambada*: era *Llorando se fue* de Los Kjarkas.

*Macarena* ➕ queda de reserva.

**Why:** las canciones tienen que calzar con la línea editorial 80/90; la primera versión se verificó contra `emerge-musicoteca/datos/biblioteca.json` ([[emerge-musicoteca]]).
**How to apply:** el flujo fue primero guiones y después diseño; al diseñar, usar la paleta y tipografías de [[emerge-manual-marca]] y no usar logos ni arte oficial de TikTok o Rockstar. Fandom bloquea WebFetch (402); para las listas de canciones de GTA sirven gtabase.com y gta.wiki.

