---
name: viaje-sin-rumbo-programa
description: Armado del programa completo de Viaje sin Rumbo desde pauta PDF + audios sueltos; script armar_programa.py; menciones vs frases
metadata:
  type: project
---

2026-11-09: armado el programa 1 (lunes 09-11) en `viaje-sin-rumbo/programa-09-11/armar_programa.py` (corre con audio-env python). Salida WAV 24 bit + MP3 320 + minutaje.txt en `salida/`. Quedó en 56:00, faltan ~4 min para la hora (se le preguntó al usuario cómo rellenar).

Vocabulario de la radio: **mención** = el locutor lee al auspiciador en vivo → es locución, va sobre cortina. **Frase** = cuña comercial grabada (Restaurante Molen 0:25, Valhalla Gym 0:28) → suena sola, sin cortina, en el corte comercial.
Cortina de fondo bajo locución: "Nicole - Viaje Infinito (Instrumental)". Cortinas de inicio/cierre: Presentacion/Despedida Viaje sin Rumbo.wav (0:40). Locuciones de Valentina vienen como "N. LOCUCION-esv2-50p-bg-10p-music-10p.wav".

**How to apply:** para programas siguientes, copiar el script y cambiar la lista de canciones/locuciones según la pauta del día. Relacionado: [[promo-viaje-sin-rumbo]], [[audio-mejora]], [[radio-emerge-fm]].
2026-11-12 (jueves, Los Irreverentes): `programa-12-11/`, mismo tratamiento -18 LUFS. El usuario pidió **solo el archivo final** (sin pistas separadas) → WAV + MP3 de la mezcla + minutaje. Quedó 48:20. Ojo: en Descargas conviven voces viejas (`-esv2-50p`) con las del día (`-esv2-90p/91p`): copiar por fecha/nombre exacto, no por el primer prefijo que calce.
2026-11-13 (viernes, Los Jaivas cantan a Violeta Parra): `programa-13-11/`, solo mezcla final, 54:53. Las voces y canciones del día son **las últimas descargadas** (los nombres se repiten con días anteriores, a veces con «(1)»); las voces crudas del zip (sin `-esv2`) no se usan. Una canción puede venir en .wav (Run Run «express»). Si falta algo, preguntar y esperar el archivo con un loop en segundo plano.
2026-11-16 (lunes, Desenchufados): las carpetas programa-09..13 ya no existían (las borró el usuario); script reconstruido en `viaje-sin-rumbo/programa-16-11/armar_programa.py` (solo mezcla final, `--check` lista las canciones). Pauta vino en .docx; formato nuevo con 13 canciones y voces 1,4,7,10,"11 Y 12",15,18,21 (21 = cierre + menciones). Quedó 65:02, 5 min sobre la hora.
2026-11-17 (martes, Amistades): `programa-17-11/` (copia del 16-11), 65:45. El usuario avisó de silencio al inicio en Pillanes y Dënver → función `cut_head` (RMS en ventana de 1 s vs sonoridad de la canción) por canción: Dënver parte en 10,9 s del original (intro casi muda), Pillanes en 10,2 s (ruidos sueltos de video antes del golpe). Ojo: no usar np.convolve con ventanas largas sobre la canción entera (tarda >10 min); usar uniform_filter1d.
2026-11-18 (miércoles, El sonido del sur): `programa-18-11/` (copia del 17-11), 61:51. Ahora todas las canciones pasan por cut_head(-35 dB, 1 s) para cortar intros casi mudas; hoy ninguna lo necesitó. Las voces de hoy venían con «(1)» y había un «4.» -50p duplicado: tomar la -90p más reciente.
2026-11-19 (jueves, El ritmo / cumpleaños Juanita Parra): `programa-19-11/`, 60:04. **No vino pauta** → el orden se sacó transcribiendo las locuciones (cada una dice qué sonó y qué viene; script scratch txall.py con faster-whisper). Ahora el script corta silencio y aire casi mudo al inicio y al final de cada canción e imprime cuánto (Gepe traía 33 s de silencio al final, Papa Negro 4,8 s al inicio).
2026-11-20 (viernes, Canciones de madres): `programa-20-11/`, 54:37. El usuario pasa las canciones por MP3Gain a 89 dB antes (quedan ~-18 LUFS); cuando no puede (hoy Pedropiedra «Mi mamá» y «Cariñar», venían a -8,4 LUFS) el script igual normaliza todo a -18 LUFS. Verificación útil: medir LUFS de cada canción dentro de la mezcla final usando minutaje.txt, y transcribir las locuciones para cruzarlas con la pauta.
