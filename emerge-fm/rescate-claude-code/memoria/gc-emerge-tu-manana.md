---
name: gc-emerge-tu-manana
description: "GC (zócalos) para OBS del matinal Emerge tu mañana: gc.html + panel.html en emerge-tu-manana/gc, estética riso de la intro; y dónde vive el GC anterior de Emerge FM"
metadata:
  node_type: memory
  type: project
  originSessionId: 9d594e48-6482-4e78-96b0-4470c74d1612
  modified: 2026-10-04T22:42:08.924Z
---

GC editable para OBS de "Emerge tu mañana" en `Desktop\claude code\emerge-tu-manana\gc\` (creado 2026-10-04), con la estética de [[intro-emerge-tu-manana]] para [[radio-emerge-fm]].

- `gc.html` = placa (fuente de navegador 1920×1080 transparente): Invitado, Tema, Cita, Redes y `?modo=mosca` (logo + EN VIVO + hora). `panel.html` = acoplable de control con vista previa, guardados, auto-ocultar y conexión al WebSocket de OBS. `fuentes/` = Unbounded y Space Grotesk variables (offline). HTML/CSS/JS plano, sin build ni CDN.
- Mecanismo heredado del GC anterior del usuario, que vive en `C:\Users\farid\Desktop\EMERGE FM\GC\` (GC-Emerge-FM-v2-OBS.html + GC-Panel-OBS3.html, bundles de Claude Design): el panel se conecta a obs-websocket 5 (puerto 4455, auth SHA-256) y hace `SetInputSettings` cambiando la URL de la fuente; los textos van como parámetros (`placa`, `nombre`, `cargo`, `temaKicker`, `tema`, `cita`, `citaAutor`, `redIg`, `redYt`, `redWeb`, `programa`, `duracion`). Mantuve esos nombres. Nuevos: `anim=0`, `salir=1`, `pos`, `escala`, `margen`, `modo=mosca`.
- Cada cambio de URL recarga la fuente (OBS recrea el navegador), por eso la mosca es una fuente aparte y "Ocultar" manda `salir=1` y apaga el item de escena 1,1 s después.
- Probado solo contra un servidor obs-websocket simulado en Python (auth, listar fuentes, mostrar/ocultar, mosca, contraseña mala) y con capturas en Chrome headless; NO se probó dentro de OBS real.

- Primer uso real (2026-10-04) falló: el panel elegía por defecto la PRIMERA fuente de navegador de OBS y le cambió la URL a «MARCADOR» (scoreleader) en vez de a «GC MAÑANA». Corregido: solo lista fuentes cuya dirección apunta a `gc.html`, se niega a tocar otras, ofrece reparar las que quedaron con parámetros pegados, y prende/apaga el item en todas las escenas que lo tengan (el usuario trabaja con Modo Estudio y muchas fuentes de navegador: MARCADOR, AMUSE, GC EDITABLE, GC general). Para diagnosticar OBS sin pedirle nada: `%APPDATA%\obs-studio\logs\` y `basic\scenes\Sin_Título.json`.

**Why:** el usuario querrá ajustes (más placas, colores, textos por defecto) o el mismo GC para otros programas de la radio.
**How to apply:** editar `gc/gc.html` y `gc/panel.html` directo; para otro programa, copiar la carpeta y cambiar emblema, pestaña y colores. Si pide que el GC anterior y este convivan, comparten nombres de parámetros pero no claves de localStorage (`emergetm.gc.*` aquí).
Shell cwd was reset to C:\Users\farid\Desktop\claude code
