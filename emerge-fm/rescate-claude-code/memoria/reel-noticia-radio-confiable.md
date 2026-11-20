---
name: reel-noticia-radio-confiable
description: Reel 65 s de Gabriel (Emerge tu mañana) dando la noticia Ipsos–AMMPE «la radio, medio más confiable»; paleta del matinal, panel de datos animado e inserts; carpeta emerge-noticia-reel
metadata:
  type: project
---

Creado el 2026-11-13 en `Desktop\claude code\emerge-noticia-reel\` para [[radio-emerge-fm]]. Fuente: grabación de WhatsApp 832×384 de la transmisión (programa en `crop=690:384:73:0`) + 5 inserts de stock de radio (`fuentes/insert1..5`).

- Pedido: «similar» a los reels de entrevistas ([[reel-cuna-chepica]]), pero con OTROS colores (usé la paleta de Emerge tu mañana: violeta #7B61FF, naranja #FF6B35, ámbar #FFC93C sobre violeta oscuro) y, en vez de la ficha del invitado, LA NOTICIA: titular + barras de credibilidad (Radio 52 / Diarios 41 / TV abierta ~35) que se destacan cuando Gabriel dice cada cifra, y luego el 78 % (redes sociales). Fuente en pantalla: Claves Ipsos N°56, Ipsos y AMMPE World, nov. 2026.
- Corte: desde «Oye, y tenemos una noticia que nos toca de cerca…» (6,45 s) hasta antes de la 2.ª vez que dice «nos toca de cerca» (71,42 s).
- Inserts de 2,4–2,6 s dentro del recuadro, con fundido de 0,15 s, en momentos que calzan con lo dicho (INSERTS en build.py); se arma primero `salida/_recuadro.mp4` con ffmpeg.
- Transcripción: con initial_prompt el large-v3 alucinaba el inicio; transcribir.py va sin prompt y transcribe aparte la ventana 6–14 s.
- Ojo: el 2026-11-13 ya no estaban en `claude code` las carpetas emerge-cuna-*, emerge-larenas*, emerge-rengo (el usuario las movió o borró); este build.py es autónomo.
