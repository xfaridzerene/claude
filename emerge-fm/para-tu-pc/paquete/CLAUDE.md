# Contexto: Farid y Radio Emerge FM 105.5

Usa esto como contexto base en cualquier tarea. Responde siempre en español de Chile, claro y directo.

## Quién es el usuario
- **Farid Zerené Alcaíno**, Director de Radio de **Emerge Comunicaciones SpA**, dueña de **Radio Emerge FM 105.5** (Rancagua, Región de O'Higgins, Chile).
- Vende los auspicios él mismo, con dedicación completa; además produce gráficas, reels, GC para OBS y programas.
- Trabaja en Windows. Sus proyectos con Claude están en `C:\Users\farid\Desktop\claude code\`. El material de la radio (manual, logos, fuentes, GC anterior) está en `C:\Users\farid\Desktop\EMERGE FM\`. Python para audio y video: `C:\Users\farid\audio-env\` (ffmpeg en `audio-env\bin`, faster-whisper en CPU).

## La radio
- Música de los 80 y 90 en inglés y español, noticias regionales y programas en vivo. Audiencia: adultos de 30 a 60 años de Rancagua y Machalí.
- Estudio: Héctor Zamorano 481, población El Manzanal, Rancagua.
- Redes oficiales: web **emergefm.cl** · Instagram **@radioemergefm** · Facebook **Radio Emerge FM Rancagua** · WhatsApp de la radio **+56 9 5703 1055** · **publicidad@emergefm.cl**. El nombre del canal de YouTube no está confirmado.
- Frases: eslogan **«Lo que suena, emerge.»** · dial «Rancagua en frecuencia.» · redes «Emerge FM: se escucha, se ve.»

### Parrilla (lunes a viernes)
| Hora | Programa | Color |
|---|---|---|
| 08:00–09:00 | Emerge Noticias, Primera Edición | ámbar |
| 10:00–12:00 | Emerge tu mañana, con Gabriel Figueroa | violeta |
| 12:00–13:00 | Emerge Noticias, Edición Mediodía (no 13–14) | ámbar |
| 15:00–16:00 | Viaje sin Rumbo, con Valentina Sepúlveda (música chilena) | verde |
| 18:00–20:00 | La Ciudad de la Furia, con Kaco López (80 y 90) | naranja |
| 20:00–21:00 | Emerge Noticias, Edición Central (lunes, miércoles y viernes) | ámbar |
| Sáb–dom 08:00–10:00 | Emerge Noticias, Edición Fin de Semana | ámbar |
| 24/7 | Señal continua 80 y 90 (streaming) | azul |

## Marca (manual v1.0, agosto 2026)
- Colores: **Verde Señal #00E6AB** (firma), negro #000000, blanco #FFFFFF, Gris Superficie #161616, Gris Medio #8C8C8C. Secundarios por tipo de contenido: violeta #7B61FF (conversación), naranja #FF6B35 (música y 80s), ámbar #FFC93C (anuncios y noticias), azul #00AEEF (streaming y redes).
- Imprenta: el #00E6AB no existe en CMYK; usar **C80 M0 Y60 K0** con perfil SWOP (o C68 M0 Y50 K0). Negro enriquecido C60 M40 Y40 K100. Pedir siempre prueba de color.
- Tipografía: **Unbounded** ExtraBold/Black para titulares y logotipo, SemiBold para subtítulos; **Space Grotesk** para texto y captions.
- Isotipo: cuatro anillos concéntricos. Nunca recolorearlo, deformarlo ni rotarlo. Sobre fondos que no son negros va sobre su disco negro. El SVG original y todas las versiones están en `C:\Users\farid\.claude\emerge-fm\logo-svg\`.
- Tono: cercano, con energía sin gritar, orgullo local.

## Reglas que el usuario ya dio (respetarlas siempre)
- **Nunca escribir «cuña»** en reels, gráficas, descripciones ni publicaciones; tampoco rótulos como «DESTACADO». Es jerga interna.
- **No tocar un diseño ya aprobado** ni extender a todas las piezas un cambio pedido para una sola: preguntar el alcance.
- Reels de entrevistas: gancho de 4 a 7 s con la frase más fuerte, destello y la entrevista completa (unos 2 min); subtítulos con la palabra activa en verde; chip EMERGE NOTICIAS.
- Descripciones de redes: cerrar con «📻 Emerge FM 105.5: se escucha, se ve.» más los hashtags.
- No inventar cifras, nombres, cargos ni citas: marcar `[VERIFICAR: dato]`.
- Audio de los programas: todo a −18 LUFS; a la voz solo se le sube el volumen y se le pone un limitador de picos. Mención = la lee el locutor sobre la cortina; frase = la grabación comercial, que suena sola en el corte.

## Comercial
- Tarifas de la cotización de septiembre de 2026 (mensuales, netas más IVA): 300 frases $500.000 · 150 frases $300.000 · lunes a viernes 100 frases $200.000 · auspicio de programa en vivo $150.000 · Barrio $100.000 · Vitrina $50.000 · canje (máximo 3 activos). Hay una cotización posterior de $75.000 a $450.000: confirmar cuál está vigente.
- Auspicio por programa (plan del 21 de septiembre): Noticias $336.000 · La Ciudad de la Furia $300.000 · Matinal $250.000 · Noticias tarde y fin de semana $200.000 · Viaje sin Rumbo $100.000.

## Dónde está todo en este PC
Todo lo rescatado está copiado en `C:\Users\farid\.claude\emerge-fm\` (y también en el repositorio de GitHub xfaridzerene/claude):
- `logo-svg\`: logos en SVG (isotipo original `emerge-fm-avatar-ORIGINAL.svg` y 25 versiones con texto en curvas).
- `Emerge-FM-dossier.pdf`: dossier completo de la radio.
- `viaje-sin-rumbo\`: patrones de armado del programa y su script.
- `rescate-claude-code\`: lo rescatado de la carpeta `claude code`. Empieza por `CATALOGO-DE-PROYECTOS.md` (52 proyectos); `memoria\` resume cada proyecto y `claude-code\` trae los scripts y HTML recuperados.
- La skill `nota-estilo-bbcl` (notas de Emerge Noticias estilo BioBioChile) está instalada en `C:\Users\farid\.claude\skills\`.

Antes de retomar un proyecto en `Desktop\claude code`, revisa su nota en la memoria del proyecto (`C:\Users\farid\.claude\projects\C--Users-farid-Desktop-claude-code\memory\`). Si una carpeta o archivo falta en el PC, busca su copia en `C:\Users\farid\.claude\emerge-fm\rescate-claude-code\`.
