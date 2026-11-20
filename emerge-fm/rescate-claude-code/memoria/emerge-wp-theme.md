---
name: emerge-wp-theme
description: "Proyecto tema WordPress para el portal de noticias de Radio Emerge FM, desde un diseño de Claude Design"
metadata: 
  node_type: memory
  type: project
  originSessionId: d76485b1-95ec-4495-8058-276896f3d8e9
  modified: 2026-09-17T16:53:21.267Z
---

Convertir el diseño "Emerge FM news portal.zip" (C:\Users\farid\Desktop\EMERGE FM\) hecho en Claude Design en un tema WordPress instalable. Hosting: HostingPlus (Chile), WordPress. Publicará noticias. Ver [[radio-emerge-fm]].

El archivo fuente legible es `Portal Emerge FM.dc.html` (pantallas: portada, sección, nota, parrilla, en vivo, contacto; reproductor audio + video HLS). El `.export.dc.html` es una versión anterior sin nota/contacto. Trae manual de marca PDF y fuentes Unbounded + Space Grotesk. El diseño no tiene versión móvil (sin @media).

Todas las decisiones del usuario y la lista de progreso están en `C:\Users\farid\Desktop\claude code\emerge-tema\BRIEF.md`: leerlo antes de retomar.

Estado (2026-09-17): tema v1.0.0 construido y probado en WP local; zip en `emerge-tema/emerge-fm.zip`. Falta subirlo a emergefm.cl e instalar WordPress Popular Posts (el usuario autorizó usar Chrome con su sesión). Entorno de prueba local reutilizable: PHP en `Downloads/php-8.5.10-nts-Win32-vs17-x64.zip`, WordPress y plugin SQLite también en Downloads.

**Why:** el usuario quiere poder retomar con otro modelo si se acaban los créditos.
**How to apply:** leer BRIEF.md primero; no repetir preguntas ya respondidas.

