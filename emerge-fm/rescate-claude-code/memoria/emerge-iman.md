---
name: emerge-iman
description: Imán 5×7 cm de Emerge FM para regalar a empresarios + tarjeta comercial 10×15 con QR a WhatsApp; 4 propuestas en emerge-iman
metadata:
  node_type: memory
  type: project
  originSessionId: 5c2fc3ae-53dd-4865-b26e-dc6c4917e025
  modified: 2026-10-21T02:10:39.220Z
---

Proyecto en `Desktop\claude code\emerge-iman\` (creado 2026-10-16) para [[radio-emerge-fm]]: imán para un evento con empresarios (semana del 19-oct-2026). El usuario se encarga de la imprenta y de la cantidad, así que no hay que preguntarle por eso. Tampoco va ninguna mención al evento.

- Decisiones: el imán va limpio de marca (5×7 cm, vertical y horizontal); lo comercial y el QR van en una tarjeta 10×15 donde va pegado el imán. Eslogan «Lo que suena, emerge.». Contacto: Farid Zerené Alcaíno, Director, [teléfono personal omitido]; el QR lleva a wa.me con un mensaje ya escrito.
- El mensaje comercial lo escribió Claude, porque el de ejemplo («Tu marca, en frecuencia…») no le gustó al usuario: frente «Haz que tu marca suene.», reverso «Conversemos.».
- `python tools/propuestas.py` genera propuestas.html (autocontenido, con las fuentes incrustadas): A Placa, B Dial, C Eslogan, D Verde Señal. Usa métricas reales de las fuentes para calzar los anchos; textos y colores son constantes al inicio del archivo.

- Elegida: **B Dial vertical** (2026-10-16). `python tools/imprenta.py` genera en salida/ el imán (PDF CMYK en curvas, 3 mm de excedente) + troquel (esquinas de 3 mm, tinta directa CutContour) y la tarjeta (2 páginas, esquinas rectas). Bajo el imán la tarjeta dice «Ya estamos en tu refri.». Ondas en C50 M35 Y35 K95, porque con K95 solo se veían grises.

- Ronda 2 (2026-10-16): el Dial negro le pareció «soso, poco llamativo». `tools/propuestas2.py` → propuestas-2.html con B1 Dial en verde, B2 Perilla (gauge circular con el isotipo de perilla) y B3 Ondas de colores (anillos con los secundarios del manual). La tarjeta pasó a ser de **presentación clásica 9×5** sin QR (por ahora): frente con la marca, reverso con nombre, «Director de Radio», teléfono, emergefm.cl y la regla del dial. Los PDF de la ronda 1 quedaron archivados en salida/ronda1.
- **Final (2026-10-16): imán B1 «Dial en verde»** + tarjeta 9×5 con correo publicidad@emergefm.cl, web emergefm.cl, IG @radioemergefm y el 105.5 en ambas caras (el usuario lo pidió explícito). `tools/imprenta.py` genera iman-5x7 (imprenta + troquel) y tarjeta-9x5 (2 páginas). El texto negro sobre verde va en K100 sobreimpreso.
- 2026-10-17: la tarjeta pasó a **fondo blanco, estilo muy tradicional** (pedido del usuario). Cara de datos: logotipo arriba a la izquierda, nombre abajo a la izquierda y contacto alineado a la derecha. Cara de marca: logo centrado + 105.5 + eslogan. El isotipo va en la versión oficial para fondo blanco (arcos blancos → negro). La tarjeta negra anterior quedó archivada en salida/tarjeta-negra.
- Ajuste posterior: la tarjeta quedó **de una sola cara** (solo la de datos), con el **logo avatar** (disco negro detrás, pedido explícito) y «RADIO 105.5 · REGIÓN DE O’HIGGINS» en Space Grotesk Bold negro.
- La letra de la 9×5 se veía muy chica impresa. La tarjeta pasó a **10×6 cm** con texto ~30 % más grande (el más chico, 8,2 pt) y margen interior de 6 mm. La hoja oficio quedó en 2×5 = 10 tarjetas, sin pie y con marcas de 3 mm. La 9×5 está archivada en salida/tarjeta-9x5.
- Pliegos para imprimir (`escribir_pliego` en imprenta.py): imanes en **A4 y en carta** (`emerge-fm-imanes-{a4,carta}-imprimir.pdf` y `-impresora-oficina.pdf`; primero pidió A4 y después también carta; 3×3: una fila por versión, separación de 6 mm = excedentes que se tocan) y `emerge-fm-tarjetas-oficio-imprimir.pdf` (oficio chileno 216×330, 2×6, cortes compartidos). Marcas de corte en las 4 tintas, solo en el perímetro.
- El usuario imprime en casa con una **Canon MAXIFY GX7110** (tinta pigmentada) sobre papel imantado fotográfico glossy, y la tinta se corría. Por eso hay `emerge-fm-imanes-a4-impresora-oficina.pdf`: RGB, sin sobreimpresión y con negros aclarados (#262626, ondas #353535; `PALETA_OFICINA` en imprenta.py). Recomendado: papel imantado mate, «Papel fotográfico mate» en el driver, calidad estándar y 24 h de secado.
- 2026-10-20: pidió imanes **más cuadrados y chicos** con la hoja carta optimizada, poco margen y sin pie. Formato **4,6 × 4,9 cm** (`IMAN_C`, funciones `iman_c_*`), 20 por hoja (4×5: 8 Dial verde, 6 Perilla, 6 Ondas), con 2 mm de excedente y 4 mm entre imanes. Archivos: `emerge-fm-imanes-cuadrados-carta-{imprimir,impresora-oficina}.pdf`.
- 2026-10-17: B2 Perilla y B3 Ondas de colores también se exportan a PDF de imprenta, con «(segunda opcion)» en el nombre del archivo (lo pidió el usuario). Usan el mismo troquel que el imán principal.

**Why:** el usuario puede pedir ajustes después de la prueba de imprenta (el verde, los textos chicos del dial, que son de 5,4 pt).
**How to apply:** editar las constantes de imprenta.py y reconstruir; verificar el QR con cv2 sobre la vista PNG. Reglas de marca en [[emerge-manual-marca]]; el motor PDF viene de [[emerge-lamina-puerta]].
