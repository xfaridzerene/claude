# -*- coding: utf-8 -*-
"""Lámina Emerge FM 60×120 cm — idea 2 «Dial vertical».

El alto de la lámina es el dial de FM (108 arriba, 88 abajo) y la aguja verde se clava en 105.5.
Usa el mismo motor que la placa (build.py): CMYK, textos en curvas, 5 mm de excedente.

Genera en salida/:
  emerge-fm-lamina-dial-60x120-imprenta.pdf                      fondo negro (la idea elegida)
  emerge-fm-lamina-dial-verde-60x120-imprenta (segunda opcion).pdf   fondo Verde Señal, como el imán
  y sus vistas SVG/PNG.

Uso:  python tools/dial.py
"""
import os
import shutil
import subprocess

import build
from build import (ANCHO, BLANCO, GRIS, GRIS_SUPERFICIE, NEGRO, SALIDA, VERDE, Fuente, anillo, caja,
                   isotipo, rectangulo)

# ---------- textos ----------
TXT_FRECUENCIA = "105.5"
TXT_FM = "FM"
TXT_DIAL = ("Rancagua", "en frecuencia.")   # identificación en el dial (manual, pág. 5)

# ---------- dial (mm, origen arriba-izquierda del formato final) ----------
MHZ_ARRIBA, MHZ_ABAJO = 108, 88
DIAL_Y0, MM_POR_MHZ = 80.0, 48.0           # 108 MHz a 8 cm del borde; 88 MHz a 104 cm
SINTONIA = 105.5
LOMO_X, LOMO_GROSOR = 120.0, 4.0           # línea vertical de la regla
RAYA_MAYOR, RAYA_MENOR = 56.0, 30.0        # largo de las rayas (cada 2 MHz / cada 0,5 MHz)
GROSOR_MAYOR, GROSOR_MENOR = 4.0, 2.5
ETIQUETA_X, ETIQUETA_CUERPO = 102.0, 30.0  # números alineados a la derecha, junto al lomo
AGUJA_X0, AGUJA_GROSOR, AGUJA_PUNTA = 104.0, 6.0, 13.0

# ---------- columna de texto ----------
COL_X = 210.0                              # borde izquierdo de la tinta
FREC_BASE, FREC_ANCHO = 352.0, 350.0
FM_BASE, FM_CUERPO = 418.0, 62.0
DIAL_BASES, DIAL_ANCHO = (676.0, 728.0), 330.0   # el ancho manda sobre «en frecuencia.»
LOGO_CY, ISO_TINTA, LOGO_ESPACIO, MARCA_ANCHO = 1000.0, 75.0, 22.0, 253.0

# ---------- ondas de fondo: nacen donde la aguja sale por el borde derecho ----------
ONDAS_CENTRO = (ANCHO, DIAL_Y0 + (MHZ_ARRIBA - SINTONIA) * MM_POR_MHZ)
ONDAS_RADIOS = (110.0, 200.0, 290.0, 380.0)
ONDAS_GROSOR = 34.0

# ---------- versiones ----------
GRIS_RAYA = ((0, 0, 0, 0.70), "#5C5C5C")
NEGRO_SOBRE_VERDE = ((0.60, 0.40, 0.40, 1.00), "#000000")
VERDE_OSCURO = ((0.71, 0, 0.51, 0.03), "#00D29C")    # ondas sobre el verde (igual que el imán)
RAYA_SOBRE_VERDE = ((0, 0, 0, 0.60), "#0B7A5C")

VERSIONES = {
    "negro": dict(fondo=NEGRO, ondas=GRIS_SUPERFICIE, principal=BLANCO, rayas=GRIS_RAYA, etiquetas=GRIS,
                  aguja=VERDE, fm=VERDE, emerge=BLANCO, marca_fm=VERDE, disco=None,
                  archivo="emerge-fm-lamina-dial-60x120-{}",
                  titulo="Emerge FM - Lamina 60x120 cm - Dial vertical"),
    "verde": dict(fondo=VERDE, ondas=VERDE_OSCURO, principal=NEGRO_SOBRE_VERDE, rayas=RAYA_SOBRE_VERDE,
                  etiquetas=NEGRO_SOBRE_VERDE, aguja=BLANCO, fm=BLANCO, emerge=NEGRO_SOBRE_VERDE,
                  marca_fm=NEGRO_SOBRE_VERDE, disco=NEGRO,
                  archivo="emerge-fm-lamina-dial-verde-60x120-{} (segunda opcion)",
                  titulo="Emerge FM - Lamina 60x120 cm - Dial vertical en verde"),
}


def y_mhz(f):
    return DIAL_Y0 + (MHZ_ARRIBA - f) * MM_POR_MHZ


def linea(fuente, partes, base, x, ancho=None, cuerpo=None, alinear="izq"):
    """Una línea en curvas alineada por su tinta. partes = [(texto, color)]; manda ancho o cuerpo."""
    completo = "".join(t for t, _ in partes)
    todos = fuente.contornos(completo)
    x0, _, x1, _ = caja(todos)
    escala = ancho / (x1 - x0) if ancho else cuerpo / fuente.upm
    dx = {"izq": x - x0 * escala, "der": x - x1 * escala, "centro": x - (x0 + x1) / 2 * escala}[alinear]
    capas, inicio = [], 0
    for i, (_, color) in enumerate(partes):
        fin = len(fuente.contornos("".join(p for p, _ in partes[:i + 1])))
        capas.append((build.transformar(todos[inicio:fin], escala, dx, base), color))
        inicio = fin
    return capas, escala * fuente.upm


def componer(v):
    negra = Fuente("Unbounded-Black.ttf")
    semi = Fuente("Unbounded-SemiBold.ttf")
    grotesk = Fuente("SpaceGrotesk-Bold.ttf")
    cap = grotesk.tt["OS/2"].sCapHeight / grotesk.upm
    capas, informe = [], []

    capas.append((rectangulo(-build.EXCEDENTE, -build.EXCEDENTE, ANCHO + 2 * build.EXCEDENTE,
                             build.ALTO + 2 * build.EXCEDENTE), v["fondo"]))
    capas.append(([c for r in ONDAS_RADIOS for c in anillo(*ONDAS_CENTRO, r, ONDAS_GROSOR)], v["ondas"]))

    # regla: lomo + rayas cada 0,5 MHz + números cada 2 MHz
    arriba, abajo = y_mhz(MHZ_ARRIBA), y_mhz(MHZ_ABAJO)
    mayores = rectangulo(LOMO_X - LOMO_GROSOR / 2, arriba - GROSOR_MAYOR / 2, LOMO_GROSOR,
                         abajo - arriba + GROSOR_MAYOR)
    menores = []
    pasos = int((MHZ_ARRIBA - MHZ_ABAJO) * 2)
    for i in range(pasos + 1):
        f = MHZ_ABAJO + i * 0.5
        y = y_mhz(f)
        if i % 4 == 0:
            mayores += rectangulo(LOMO_X, y - GROSOR_MAYOR / 2, RAYA_MAYOR, GROSOR_MAYOR)
            num, _ = linea(grotesk, [(str(int(f)), v["etiquetas"])], y + ETIQUETA_CUERPO * cap / 2,
                           ETIQUETA_X, cuerpo=ETIQUETA_CUERPO, alinear="der")
            capas += num
        else:
            menores += rectangulo(LOMO_X, y - GROSOR_MENOR / 2, RAYA_MENOR, GROSOR_MENOR)
    capas += [(menores, v["rayas"]), (mayores, v["principal"])]
    informe.append(("Números del dial", ETIQUETA_CUERPO))

    # aguja: cruza la regla y sale por el borde derecho
    ya = y_mhz(SINTONIA)
    aguja = rectangulo(AGUJA_X0, ya - AGUJA_GROSOR / 2, ANCHO + build.EXCEDENTE - AGUJA_X0, AGUJA_GROSOR)
    aguja += [anillo(AGUJA_X0, ya, AGUJA_PUNTA / 2, AGUJA_PUNTA)[0]]   # disco: solo el círculo exterior
    capas.append((aguja, v["aguja"]))

    frec, cuerpo = linea(negra, [(TXT_FRECUENCIA, v["principal"])], FREC_BASE, COL_X, ancho=FREC_ANCHO)
    capas += frec
    informe.append(("105.5", cuerpo))
    fm, cuerpo = linea(negra, [(TXT_FM, v["fm"])], FM_BASE, COL_X, cuerpo=FM_CUERPO)
    capas += fm
    informe.append(("FM", cuerpo))

    # «Rancagua / en frecuencia.»: mismo cuerpo, que calza el ancho de la línea más larga
    _, cuerpo = linea(semi, [(TXT_DIAL[1], v["principal"])], 0, COL_X, ancho=DIAL_ANCHO)
    for texto, base in zip(TXT_DIAL, DIAL_BASES):
        capas += linea(semi, [(texto, v["principal"])], base, COL_X, cuerpo=cuerpo)[0]
    informe.append(("Rancagua en frecuencia.", cuerpo))

    # logo horizontal: isotipo + EMERGE FM, centrados en LOGO_CY
    caja_iso = ISO_TINTA * 360 / 277          # la tinta del isotipo ocupa 277 de las 360 unidades
    iso_cx = COL_X + ISO_TINTA / 2
    if v["disco"]:
        disco = anillo(iso_cx, LOGO_CY, caja_iso / 4, caja_iso / 2)[0]
        capas.append(([disco], v["disco"]))
    capas += isotipo(iso_cx, LOGO_CY, caja_iso)
    marca_x = COL_X + ISO_TINTA + LOGO_ESPACIO + (caja_iso - ISO_TINTA) / 2 * bool(v["disco"])
    marca, cuerpo = linea(negra, [("EMERGE ", v["emerge"]), ("FM", v["marca_fm"])], 0, marca_x,
                          ancho=MARCA_ANCHO - (caja_iso - ISO_TINTA) / 2 * bool(v["disco"]))
    cap_unb = negra.tt["OS/2"].sCapHeight / negra.upm * cuerpo
    capas += linea(negra, [("EMERGE ", v["emerge"]), ("FM", v["marca_fm"])], LOGO_CY + cap_unb / 2,
                   marca_x, cuerpo=cuerpo)[0]
    informe.append(("Logotipo", cuerpo))
    return capas, informe


def vista_png(svg, png):
    chrome = shutil.which("chrome") or r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome):
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1000,2000",
                        f"--screenshot={png}", "file:///" + svg.replace("\\", "/").replace(" ", "%20")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    for nombre, v in VERSIONES.items():
        capas, informe = componer(v)
        pdf = os.path.join(SALIDA, v["archivo"].format("imprenta") + ".pdf")
        svg = os.path.join(SALIDA, v["archivo"].format("vista") + ".svg")
        build.escribir_pdf(capas, pdf, v["titulo"])
        build.escribir_svg(capas, svg)
        vista_png(svg, svg[:-4] + ".png")
        print(f"[{nombre}]", os.path.basename(pdf))
        for texto, cuerpo in informe:
            print(f"   {texto:<24} cuerpo {cuerpo:6.1f} mm")
