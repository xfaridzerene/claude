# -*- coding: utf-8 -*-
"""Láminas grandes 80×200 cm: «Placa institucional» en negro y «Dial vertical» en verde.

Es el mismo diseño de build.py y dial.py, recompuesto para el formato 1:2,5 (más alto que el 1:2 de 60×120):
los anchos crecen en proporción al ancho (×4/3) y el alto extra se reparte en el isotipo, el aire y el dial.
Excedente de 10 mm, que es lo habitual en gran formato.

Genera en salida/:
  emerge-fm-lamina-placa-80x200-negro-imprenta.pdf   y su vista SVG/PNG
  emerge-fm-lamina-dial-80x200-verde-imprenta.pdf    y su vista SVG/PNG

Uso:  python tools/grande.py
"""
import os
import shutil
import subprocess

import build
import dial

ANCHO, ALTO, EXCEDENTE = 800.0, 2000.0, 10.0
K = ANCHO / 600.0          # escala de los anchos respecto de la lámina de 60 cm


def formato():
    """Cambia el formato del motor compartido (build.py lo lee al escribir cada PDF/SVG)."""
    build.ANCHO, build.ALTO, build.EXCEDENTE, build.CX = ANCHO, ALTO, EXCEDENTE, ANCHO / 2
    dial.ANCHO = ANCHO


def placa():
    build.PIE_REDES = ()                                # el pie de redes es solo del 60×120 negro
    build.COLUMNA = 472.0 * K
    build.ISO_CAJA = {"negro": 790.0}                  # anillos de 608 mm: el isotipo toma el alto extra
    build.ESPACIOS = (150.0, 100.0, 100.0, 80.0)        # isotipo→logotipo, logotipo→filete, filete→105.5, 105.5→eslogan
    build.FILETE_ANCHO, build.FILETE_GROSOR = 160.0 * K, 2.0 * K
    build.ONDAS_X = 560.0 * K
    build.ONDAS_RADIOS = tuple(r * K for r in (120.0, 210.0, 300.0, 390.0))
    build.ONDAS_GROSOR = 34.0 * K
    build.ONDAS_AIRE = 26.0 * K
    build.ONDAS_Y_MIN = ALTO - 100.0 * K
    return build.componer("negro")


def dial_verde():
    d = dial
    d.MHZ_ARRIBA, d.MHZ_ABAJO = 108, 88
    d.DIAL_Y0, d.MM_POR_MHZ = 100.0, 90.0               # 108 MHz a 10 cm de arriba; 88 MHz a 10 cm de abajo
    d.LOMO_X, d.LOMO_GROSOR = 120.0 * K, 4.0 * K
    d.RAYA_MAYOR, d.RAYA_MENOR = 56.0 * K, 30.0 * K
    d.GROSOR_MAYOR, d.GROSOR_MENOR = 4.0 * K, 2.5 * K
    d.ETIQUETA_X, d.ETIQUETA_CUERPO = 102.0 * K, 30.0 * K
    d.AGUJA_X0, d.AGUJA_GROSOR, d.AGUJA_PUNTA = 113.0 * K, 8.0 * K, 16.0 * K

    ya = d.y_mhz(d.SINTONIA)                           # aguja a 32,5 cm del borde superior
    d.COL_X = 210.0 * K
    d.FREC_BASE, d.FREC_ANCHO = ya + 152.0 * K, 350.0 * K
    d.FM_BASE, d.FM_CUERPO = ya + 218.0 * K, 62.0 * K
    # logo vertical (isotipo sobre el nombre), apoyado en la raya de 88 MHz: más grande y sin aire de sobra
    d.LOGO_VERTICAL = True
    d.LOGO_V_CAJA, d.LOGO_V_ESPACIO, d.LOGO_V_BASE = 320.0, 45.0, None
    # ondas: las mismas cuatro del 60×120, sin llegar a la regla
    d.ONDAS_CENTRO = (ANCHO, ya)
    d.ONDAS_RADIOS = tuple(r * K for r in (110.0, 200.0, 290.0, 380.0))
    d.ONDAS_GROSOR = 34.0 * K

    # el eslogan, al ancho del 105.5, centrado en el aire entre la última onda y el logo
    d.ESLOGAN_ANCHO = d.FREC_ANCHO
    pie_ondas = ya + d.ONDAS_RADIOS[-1] + d.ONDAS_GROSOR / 2
    _, cy_logo, _, radio_logo = d.logo_vertical(d.VERSIONES["verde"])
    techo_logo = cy_logo - radio_logo
    centro = (pie_ondas + techo_logo) / 2
    interlinea = 76.0 * K
    d.ESLOGAN_BASES = (centro - 37.0, centro - 37.0 + interlinea)   # 37 mm ≈ (interlínea + descendente − mayúscula) / 2
    return d.componer(d.VERSIONES["verde"])


def vista_png(svg, png):
    chrome = shutil.which("chrome") or r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome):
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=800,2000",
                        f"--screenshot={png}", "file:///" + svg.replace("\\", "/").replace(" ", "%20")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


if __name__ == "__main__":
    os.makedirs(build.SALIDA, exist_ok=True)
    formato()
    for nombre, componer, titulo in (
            ("placa-80x200-negro", placa, "Placa institucional negro"),
            ("dial-80x200-verde", dial_verde, "Dial vertical verde")):
        capas, informe = componer()
        base = os.path.join(build.SALIDA, f"emerge-fm-lamina-{nombre}")
        build.escribir_pdf(capas, base + "-imprenta.pdf", f"Emerge FM - Lamina 80x200 cm - {titulo}")
        build.escribir_svg(capas, base + "-vista.svg")
        vista_png(base + "-vista.svg", base + "-vista.png")
        print(f"[{nombre}]")
        for texto, valor in informe:
            print(f"   {texto:<24}", f"{valor:6.1f} mm" if isinstance(valor, float) else
                  "arriba %.0f mm, abajo %.0f mm" % valor)

