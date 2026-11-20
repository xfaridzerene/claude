---
name: reel-despacho-rengo-ciclistas
description: "Reel 3:38 vertical del despacho en terreno de Roberto en Rengo (Fabián Cofré, 7 ciclistas atropellados en Apalta): logo arriba, GC al inicio, subtítulos en seco verdes; carpeta emerge-despacho-roberto"
metadata:
  type: project
---

Creado el 2026-11-16 en `Desktop\claude code\emerge-despacho-roberto\` para [[radio-emerge-fm]]. Fuente: video vertical 1080×1920 del celular (Descargas\20261116_161729~2.mp4), completo, sin cortes.

- Pedido: «subtítulos, la marca de Emerge FM y GC al inicio»; periodista = Roberto Rojas-Connell. Hice GC de Roberto (0,6–8 s, «Periodista · Emerge Noticias», chips EMERGE NOTICIAS + EN TERRENO · RENGO) y otro de Fabián Cofré cuando empieza a hablar (38,3 s, «Ciclista atropellado en Apalta, Rengo»).
- build.py autónomo (no depende de las carpetas de reels de entrevistas que ya no están, ver [[reel-cuna-chepica]]): video a pantalla completa con degradados arriba/abajo, subtítulos karaoke con palabra activa en Verde Señal, EDITS/CORTAR_ANTES/UNIR y mayúscula automática tras punto.
- Plantilla para próximos despachos verticales en terreno: cambiar FUENTE_VIDEO, GCS, LUGAR y EDITS.
- Versión final < 3 min (2:55) para IG/FB: el usuario pidió cortar las preguntas intermedias de Roberto y dejar su inicio y su cierre. TRAMOS en build.py arma `salida/_editado.mp4`; subtítulos se remapean por tramo con corte forzado; destello blanco breve en cada corte. La completa de 3:38 quedó como revision/build_completo_218s.py. IG/FB: preferir reels < 3 min.
