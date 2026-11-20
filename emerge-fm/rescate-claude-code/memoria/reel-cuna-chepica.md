---
name: reel-cuna-chepica
description: Reel vertical ~118 s de la cuña de José Cepeda (dirigente agricultor, Chépica) en Emerge Noticias con Roberto; misma plantilla que ASGRO pero subtítulos en seco; carpeta emerge-cuna-chepica
metadata:
  type: project
---

Creado el 2026-11-12 en `Desktop\claude code\emerge-cuna-chepica\` para [[radio-emerge-fm]], copiando la plantilla de [[reel-cuna-asgro]]. José Cepeda = dirigente agricultor de la comuna de Chépica; tema: agricultores se suman al paro de camioneros (rumbo a San Fernando), costos, petróleo, lluvias/cambio climático, ley del grano. Foto en `fuentes/jose.jpg` (335×335, también en `Desktop\claude code\fotos\jose-cepeda-chepica.jpg`).

- Corte pedido: empieza cuando Roberto dice «Hay una gran cantidad de agricultores…» (11,72 s de la fuente). Lo terminé en «…lo que está pasando.» (129,95 s) porque la grabación se corta a mitad de la frase de cierre de Roberto.
- **Preferencia nueva del usuario:** subtítulos «en seco», sin fundido ni subida al aparecer (`e = 1.0` en `dibujar_sub`). Usar así en las próximas cuñas.
- build.py ahora acepta cualquier cantidad de PARTES; `bloques()` evita cortar tras artículos/preposiciones (DEBIL) y dejar palabras sueltas.

**How to apply:** para la próxima cuña, copiar esta carpeta (no la de ASGRO), cambiar PARTES, NOMBRE/CARGO/FOTO y el recorte x de la foto, ajustar el prompt de transcribir.py y transcribir.
