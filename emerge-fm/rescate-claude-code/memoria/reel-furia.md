---
name: reel-furia
description: "Reel vertical viral del anuncio de La Ciudad de la Furia (Kaco a cámara): letras y logo 3D detrás de la persona + subtítulos amarillos; pipeline Python en carpeta reel-furia"
metadata:
  node_type: memory
  type: project
  originSessionId: 29ddaa13-c871-4501-8be3-cb79cc08157b
  modified: 2026-10-06T04:52:24.299Z
---

Proyecto en `Desktop\claude code\reel-furia\` (creado 2026-10-06). Edición del clip `E:\GRABACIONES 22-09\DJI_0212.MP4` (4K vertical, 59,94 fps, Kaco López anunciando el estreno de [[intro-ciudad-furia]] el lunes 19 de octubre a las 18:00 por [[radio-emerge-fm]]). En la misma carpeta de grabaciones hay más tomas (DJI_0190 a DJI_0212) que el usuario podría pedir con el mismo tratamiento.

- Entregable: `la-ciudad-de-la-furia-reel.mp4` (1080×1920, 59,94 fps, 22 s, voz normalizada a −14 LUFS, sin música).
- Pedido del usuario: estilo viral, letras 3D detrás de la persona, isotipo Emerge FM 3D detrás, destacar "Emerge FM", "105.5" y "La Ciudad de la Furia", subtítulos amarillos estilo cine.
- Técnica: `work/matte_run.py` segmenta a la persona con `u2net_human_seg` (rembg, ya instalado; ~30 min en CPU con 2 procesos) → `work/matte_*.npy`. `render.py` compone cuadro a cuadro: zooms punch-in, filtro guiado para afinar la máscara, gráficos de `gfx3d.py` (extrusión por capas con homografías PIL), subtítulos. Los textos se ubican solos respecto del tope de la cabeza (`EVENTS`, columna solape).
- Flujo: `python render.py sheet <tiempos fuente>` para revisar; `python render.py render <a> <b> work/seg_k.mp4` en 3 procesos (~11 min), luego concat + `work/audio.m4a` con el ffmpeg de CapCut (`-c copy -frames:v 1322`).
- Transcripción: `faster-whisper` (instalado con pip en esta sesión; en GPU falla por falta de cuBLAS, corre en CPU con modelo medium). Pasar el audio como array numpy: `av` 19 rompe `decode_audio`.
- El aviso "Truncating packet" del ffmpeg de CapCut al recibir rawvideo por pipe es inofensivo.
- Usa el logo del programa `furia-promo\src\logo-programa.png` (ver [[furia-promo]]) y la paleta de [[emerge-manual-marca]].

- Segunda versión (2026-11-02), estreno ya movido al **lunes 9 de noviembre, 18:00**: `la-ciudad-de-la-furia-reel-9-nov.mp4` desde `Desktop\kaco en bruto 9 nov.mp4` (dos tomas, exterior y estudio, corte en cuadro 311; 21,2 s, 30 fps). Código en `nov9\`: `render_nov9.py` (agrega transición atravesando el isotipo `logo_wipe`, apertura/cierre con el mismo efecto, golpe de cámara, ondas de señal, separación RGB, cielo oscurecido en exterior) y `audio_nov9.py` (voz + whooshes/impactos sintetizados). Es la base a reutilizar para el próximo clip. "Efectos" para el usuario incluyó la transición entre las dos tomas del mismo archivo.

**Why:** el usuario puede pedir ajustes (textos, tiempos, música) o repetir el estilo en otras tomas.
**How to apply:** reutilizar `gfx3d.py` y `nov9
ender_nov9.py` (el `FF` de `render.py` apunta a una versión fija de CapCut que se actualiza; `nov9` la busca sola); para otro clip hay que rehacer máscara, transcripción, `EVENTS`, `SUBS` y `ZOOM`.

