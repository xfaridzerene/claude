---
name: reels-eneo-2026
description: "Reels verticales de entrevistas en ENEO 2026 (Pro O'Higgins, Monticello, 18-11-2026) con formato gancho corto + entrevista completa; carpeta emerge-reels-1118"
metadata:
  type: project
---

Creado el 2026-11-19 en `Desktop\claude code\emerge-reels-1118\` para [[radio-emerge-fm]]. Fuentes: iPhone 4K HEVC 60 fps vertical (Descargas, IMG_0184/0187/0188/0196/0203.MOV) → copias 1080×1920 30 fps en `fuentes/*.mov`; transcripción large-v3 en transcripcion.json (clave = nombre del video).

- **Formato nuevo pedido por el usuario:** abrir con un «highlight» corto como gancho (4–7 s, la frase más fuerte) y después el video completo. Sin etiquetas tipo «DESTACADO» ([[feedback-no-cuna-en-redes]]). Destello blanco breve entre gancho y completo.
- build.py genérico: `python build.py IMG_0184 [--fotos t,t]`; REELS define gancho, tramo, GC y salida por video. Hereda la plantilla vertical de [[reel-despacho-rengo-ciclistas]] (logo arriba, GC con chip EMERGE NOTICIAS, subtítulos en seco con palabra activa verde). EDITS se aplican a todas las apariciones; la última palabra de cada tramo cierra con punto.
- Entrevistados: IMG_0184 «Raúl» de Pro O'Higgins (apellido y cargo sin confirmar), IMG_0188 gobernador Pablo Silva Amaya (solo saluda y da la bienvenida a Emerge FM), IMG_0196 Hernán Garcés (presidente de Garcés Fruit, nueva socia de Pro O'Higgins), IMG_0203 seremi de Minería Carla Ortiz (nombre por búsqueda web). IMG_0187 es una pregunta suelta de 4 s, sin uso.
- 2026-11-19: el usuario pidió que duren ~2 min, cortando preguntas intermedias y partes poco relevantes o redundantes → gobernador 1:58 (9 tramos) y seremi 1:53 (5 tramos); Garcés queda en 1:30 sin cortes. Regla de subtítulos: punto/mayúscula solo al final del gancho y del reel; los cortes internos siguen la frase.
- 2026-11-20: IMG_0201 = seremi del Trabajo Carmen Gloria Manríquez (dato del usuario con su foto oficial; cargo completo «Seremi del Trabajo y Previsión Social»). Flujo que pidió: primero el guion con gancho y cortes para aprobar, después render. Reel 1:58, gancho «segundo lugar en desempleo». «ENADI» sin confirmar.
