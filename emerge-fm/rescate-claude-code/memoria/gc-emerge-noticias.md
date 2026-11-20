---
name: gc-emerge-noticias
description: "GC para OBS de Emerge Noticias, estilo canal 24 horas (elegido entre 4 opciones): gc-noticias.html + panel-noticias.html en emerge-noticias-gc"
metadata:
  type: project
---

GC del informativo [[intro-emerge-noticias]] en `Desktop\claude code\emerge-noticias-gc\` (creado 2026-11-05). El usuario pidió «más ancho, más como canal de noticias» y eligió **«Canal 24 horas clásico»** de la hoja `propuesta/opciones-estetica.png` (las otras: formal IG, papel de la intro, minimalista).

- Mismo sistema que [[gc-emerge-tu-manana]] y [[gc-ciudad-furia]] (obs-websocket, datos por URL), pero con DOS fuentes: placa `gc-noticias.html` y base `gc-noticias.html?modo=base` (cintillo con reloj + edición, mosca EN VIVO · 105.5). `modo=todo` = vista previa del panel. El panel distingue por el regex `gc-noticias\.html` y `modo=base`.
- 2026-11-05: en su OBS no aparecían el cintillo ni la hora (la fuente base exigía escribir `?modo=base` en una URL con «Archivo local» desmarcado). Se agregó `base-noticias.html` (redirige a gc-noticias.html?modo=base conservando los parámetros) para elegirla con Examinar; el panel la reconoce y avisa si falta.
- Placas: titular, ultima (pestaña ámbar que late + barrido ámbar), persona. Pestaña de lugar con punto rojo de en vivo. Si el cintillo está oculto, la placa baja (`cintillo=0`).
- Edición automática por hora: finde sáb-dom; <11 h Primera; <17 h Mediodía; si no, Central.
- Isotipo en su color sobre círculo negro (el manual prohíbe recolorearlo). Rojo solo en EN VIVO.
- Entregado también como `GC-Noticias.zip` + `LEEME - instalar en OBS.txt` (ruta sugerida C:\GC-Noticias). Probado en Chrome y contra OBS simulado, no en OBS real.

**Why:** el usuario usa estos GC al aire y los lleva a otro PC por correo.
**How to apply:** cambios de estilo en gc-noticias.html; no tocar la estética aprobada sin preguntar ([[feedback-no-cambiar-aprobado]]).
