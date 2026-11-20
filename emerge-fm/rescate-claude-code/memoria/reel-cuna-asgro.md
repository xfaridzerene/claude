---
name: reel-cuna-asgro
description: Reel vertical 66 s de la cuña de Camilo Jiménez (vocero ASGRO) en Emerge Noticias con Roberto al medio, foto+onda arriba y subtítulos karaoke abajo; carpeta emerge-cuna-asgro
metadata:
  type: project
---

Creado el 2026-11-11 en `Desktop\claude code\emerge-cuna-asgro\` para [[radio-emerge-fm]]. Camilo Jiménez = vocero de la Asociación Gremial Rengo O'Higgins (ASGRO), transportistas; tema: alza de combustibles desde marzo, oportunismo político. Foto en `fuentes/camilo.png` (copia de `Desktop\claude code\fotos\camionero-san-manuel.png`, 460×741, baja resolución).

- Formato pedido por el usuario (sirve de plantilla para futuras cuñas): arriba foto en cuadro + nombre/cargo + onda de audio en vivo; al medio Roberto con GC (16:9 de grabación de pantalla iPhone, `crop=2080:1170:226:0`, igual que [[reel-primer-dia]]); abajo subtítulos con palabra activa en verde. Audio original de la grabación (es la voz de la cuña), −14 LUFS.
- Orden: parte1.mov (39 s) y luego parte2.mp4 (28 s).
- `transcribir.py` corre con `audio-env` (faster-whisper large-v3 en GPU); necesita las DLL cuBLAS de torch/lib en PATH (ya parchado en el script). `build.py` con Python global; `EDITS` corrige palabras; `--fotos` para cuadros.
- Dudas de transcripción que no confirmó el usuario: quité «a hacer este tema» tras «combustibles»; «que nada hoy en día tenga utilidad» (¿nadie?); cierre «muchos colegas».

**How to apply:** para otra cuña, copiar la carpeta, cambiar PARTES, NOMBRE/CARGO, la foto y transcribir de nuevo.
