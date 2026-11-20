---
name: reel-primer-dia
description: Reel vertical 31 s agradeciendo el primer día al aire de Emerge FM (9 nov 2026) con 5 grabaciones de pantalla del stream; carpeta emerge-primer-dia
metadata:
  type: project
---

Creado el 2026-11-10 en `Desktop\claude code\emerge-primer-dia\` para [[radio-emerge-fm]]. Salida `salida/emerge-primer-dia-9x16.mp4` (1080×1920, 30 fps, 30,8 s, **sin audio**: el usuario pidió quitar el audio de los clips; la música se pone en la app).

- Fuentes: grabaciones de pantalla del iPhone (HEVC 2532×1170 rotado); el 16:9 está en `crop=2080:1170:226:0`. Copiadas a `fuentes/clip1..5`.
- Orden: Farid (director, «El primer hola») → Emerge tu mañana (Gabriel) → La Ciudad de la Furia (Kaco) → Viaje sin Rumbo (Valentina) → Emerge Noticias (Roberto Rojas). Clip a ancho completo para que los GC se lean, fondo desenfocado del mismo clip, barrido diagonal entre clips.
- `python build.py` (Python global + PIL/numpy, ffmpeg de Shutter Encoder); `--fotos t1,t2` para cuadros sueltos. Inicio de cada tramo y textos en `CLIPS`.

**How to apply:** cambios de textos/orden/tramos en la lista CLIPS y funciones _intro/_cierre de build.py.
