---
name: loop-viaje-sin-rumbo
description: "Loop de fondo de 60 s (avatar de Valentina) para el stream de \"Viaje sin Rumbo\" — lápiz pasta azul, 16:9, sin sonido"
metadata:
  type: project
---

Proyecto en `Desktop\claude code\viaje-sin-rumbo-loop\` (creado 2026-10-04), derivado de [[promo-viaje-sin-rumbo]] (copia propia del motor de trazo y del personaje). El programa va por stream **sin cámara**: este loop es el avatar de Valentina a pantalla completa. Para [[radio-emerge-fm]].

- Entregables: `viaje-sin-rumbo-loop.html` y `salida/viaje-sin-rumbo-loop-16x9.mp4` (60 s, 1920×1080, 30 fps, sin audio, ~59 MB).
- Guion aprobado, 10 escenas de 6 s: vinilo → caminando por la calle con el quiltro → micro → disquería → guitarra en la plaza → cantando → lista de canciones → llega al estudio (AL AIRE) → al micrófono → sube la música. Cada escena se dibuja y se desdibuja; una línea punteada cruza la hoja en cada cambio; el empalme 60→0 es hoja en blanco con la línea.
- Decisiones del usuario: solo horizontal, sin sonido, sello chico fijo «Viaje sin Rumbo · Emerge FM 105.5» arriba a la izquierda, letreros genéricos.
- Fuente: `src/js/35-poses.js` (caminata, quiltro, guitarra), `40-scenes.js` (escenas), `60-render.js` (entrada/salida, ruta, sello). `python tools/build.py`; servidor config "viaje-loop" puerto 8772.

**Why:** el usuario puede pedir cambiar escenas, ritmo o agregar otras acciones al loop.
**How to apply:** editar src/js, reconstruir, exportar con Chrome headless `viaje-sin-rumbo-loop.html?save=1&autoexport=1` vía devserver. Cada escena debe durar 6 s exactos (SCENE) para que el loop cierre.

