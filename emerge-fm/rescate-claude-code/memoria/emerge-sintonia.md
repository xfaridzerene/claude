---
name: emerge-sintonia
description: "Animación motion graphics 12 s \"sintonizar 105.5\" de Emerge FM (Canvas + MP4 en 16:9, 9:16, 1:1)"
metadata:
  node_type: memory
  type: project
  originSessionId: c9249912-6c58-48a8-8c52-867e2c87f0dc
  modified: 2026-09-30T00:51:42.262Z
---

Proyecto en `Desktop\claude code\emerge-sintonia\` (creado 2026-09-29) para [[radio-emerge-fm]]. Station ID de 12 s: estática → barrido del dial con espectro y visor odómetro → LOCK en 105.5 (t=4.2) → las 4 ondas se enrollan en los 4 anillos del logo → firma "EMERGE / 105.5 FM" + bajada RDS "RANCAGUA · MACHALÍ · O'HIGGINS" → golpe final t=10.2.

- Entregables: `sintonia.html` (autocontenido, fuentes Unbounded Black + Space Grotesk en base64) y `salida/emerge-fm-sintonia-{16x9,9x16,1x1}.mp4`.
- Fuente en `src/js/*.js`; `python tools/build.py`; servidor `tools/devserver.py` (config "emerge-sintonia", puerto 8767). Sonido 100% sintetizado (WebAudio offline, synth-pop 80s 120 BPM).
- Geometría del logo tomada exacta de `emerge-fm-avatar.svg` (verificada lado a lado).

**Why:** el usuario puede pedir cambios (textos, duración, música real).
**How to apply:** editar src/js y reconstruir; exportar con la tecla E, o con Chrome headless `sintonia.html?f=169&save=1&autoexport=1` (f=916 / f=11). Para verificar un MP4, decodificar muestras con VideoDecoder o reproducirlo (play); en Chrome headless el seek de <video> no se aplica y devuelve el cuadro 0, que aquí es negro por el fundido de entrada.

