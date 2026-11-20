# -*- coding: utf-8 -*-
"""Entrega a imprenta del pendón 80×200 cm: placa en negro (principal) y dial en verde.

Mismo diseño que grande.py, con dos cambios pensados para imprimir:
  · Colores calibrados con un perfil de imprenta (SWOP): el Verde Señal pasa de C68 Y50 a C80 Y60, que
    conserva el tono de la marca y sale más vivo en papel/lona. El PDF lleva ese perfil incrustado.
  · Además del PDF vectorial, imágenes a 300 ppp en tamaño final: TIFF CMYK (para imprimir) y
    PNG RGB que simula el color impreso (para ver cómo va a quedar).

Genera la carpeta «Pendon Emerge FM 80x200» (y su .zip) junto a la carpeta del proyecto.

Uso:  python tools/pendon.py [ppp]        (ppp = 300 por defecto)
"""
import os
import shutil
import struct
import sys
import zipfile
import zlib

import numpy as np
import pymupdf
from PIL import Image, ImageCms

import build
import dial
import grande

RAIZ = build.RAIZ
ENTREGA = os.path.join(RAIZ, "Pendon Emerge FM 80x200")
PERFIL = r"C:\Windows\System32\spool\drivers\color\RSWOP.icm"   # SWOP estuco, el que trae Windows
PERFIL_NOMBRE = "SWOP (Agfa Swop Standard)"
PPP = int(sys.argv[1]) if len(sys.argv) > 1 else 300
BANDA = 512                       # filas por franja al rasterizar (memoria acotada)

# Colores recalibrados para imprenta: (CMYK de grande.py) → (CMYK del pendón)
RECALIBRADO = {
    (0.68, 0, 0.50, 0): (0.80, 0, 0.60, 0),          # Verde Señal: mismo tono, más croma con SWOP
    (0.71, 0, 0.51, 0.03): (0.84, 0, 0.63, 0.04),    # ondas sobre el verde: un punto más oscuro que el fondo
    (0.68, 0, 0.50, 0.60): (0.80, 0, 0.60, 0.60),    # rayitas del dial: verde + K60
}

PIEZAS = [  # (carpeta, archivo, título, función de grande.py)
    ("1 Negro (principal)", "Emerge FM pendon 80x200 - 1 negro", "Placa institucional negro", grande.placa),
    ("2 Verde", "Emerge FM pendon 80x200 - 2 verde", "Dial vertical verde", grande.dial_verde),
]


def recalibrar(capas):
    return [(contornos, (RECALIBRADO.get(tuple(color[0]), color[0]), color[1])) for contornos, color in capas]


# =====================================================================
# Escritores por franjas (la imagen completa a 300 ppp no cabe cómoda en memoria)
# =====================================================================
class PNGPorFranjas:
    """PNG RGB 8 bits, filtro Sub por fila, con sRGB y resolución (pHYs) declaradas."""

    def __init__(self, ruta, ancho, alto, ppp):
        self.f = open(ruta, "wb")
        self.f.write(b"\x89PNG\r\n\x1a\n")
        self._chunk(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0))
        self._chunk(b"sRGB", b"\x00")
        ppm = round(ppp / 0.0254)
        self._chunk(b"pHYs", struct.pack(">IIB", ppm, ppm, 1))
        self.z = zlib.compressobj(6)

    def _chunk(self, tipo, datos):
        self.f.write(struct.pack(">I", len(datos)) + tipo + datos)
        self.f.write(struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF))

    def filas(self, rgb):
        d = rgb.copy()
        d[:, 1:] -= rgb[:, :-1]                       # filtro Sub (aritmética módulo 256)
        crudo = np.concatenate([np.ones((d.shape[0], 1), np.uint8), d.reshape(d.shape[0], -1)], axis=1)
        datos = self.z.compress(crudo.tobytes())
        if datos:
            self._chunk(b"IDAT", datos)

    def cerrar(self):
        self._chunk(b"IDAT", self.z.flush())
        self._chunk(b"IEND", b"")
        self.f.close()


class TIFFPorFranjas:
    """TIFF CMYK 8 bits (Photometric = Separated), Deflate + predictor horizontal, perfil ICC incrustado."""

    def __init__(self, ruta, ancho, alto, ppp, icc):
        self.f = open(ruta, "wb")
        self.f.write(b"II*\x00\x00\x00\x00\x00")       # el puntero al IFD se completa al cerrar
        self.ancho, self.alto, self.ppp, self.icc = ancho, alto, ppp, icc
        self.offsets, self.cuentas, self.filas_tira = [], [], None

    def _alinear(self):
        if self.f.tell() % 2:
            self.f.write(b"\x00")

    def filas(self, cmyk):
        if self.filas_tira is None:
            self.filas_tira = cmyk.shape[0]
        d = cmyk.copy()
        d[:, 1:] -= cmyk[:, :-1]                      # predictor 2: diferencia con el píxel de la izquierda
        datos = zlib.compress(d.tobytes(), 6)
        self._alinear()
        self.offsets.append(self.f.tell())
        self.cuentas.append(len(datos))
        self.f.write(datos)

    def cerrar(self):
        n = len(self.offsets)

        def bloque(datos):
            self._alinear()
            pos = self.f.tell()
            self.f.write(datos)
            return pos

        bits = bloque(struct.pack("<4H", 8, 8, 8, 8))
        offs = bloque(struct.pack(f"<{n}I", *self.offsets))
        cnts = bloque(struct.pack(f"<{n}I", *self.cuentas))
        res = bloque(struct.pack("<II", self.ppp, 1))
        icc = bloque(self.icc)
        SHORT, LONG, RATIONAL, UNDEF = 3, 4, 5, 7
        campos = [
            (256, LONG, 1, self.ancho), (257, LONG, 1, self.alto), (258, SHORT, 4, bits),
            (259, SHORT, 1, 8), (262, SHORT, 1, 5), (273, LONG, n, offs), (277, SHORT, 1, 4),
            (278, LONG, 1, self.filas_tira), (279, LONG, n, cnts), (282, RATIONAL, 1, res),
            (283, RATIONAL, 1, res), (284, SHORT, 1, 1), (296, SHORT, 1, 2), (317, SHORT, 1, 2),
            (332, SHORT, 1, 1), (34675, UNDEF, len(self.icc), icc),
        ]
        self._alinear()
        ifd = self.f.tell()
        self.f.write(struct.pack("<H", len(campos)))
        for tag, tipo, cuenta, valor in campos:
            if tipo == SHORT and cuenta == 1:
                self.f.write(struct.pack("<HHIHH", tag, tipo, cuenta, valor, 0))
            else:   # LONG de un valor, o puntero a los datos
                self.f.write(struct.pack("<HHII", tag, tipo, cuenta, valor))
        self.f.write(struct.pack("<I", 0))
        self.f.seek(4)
        self.f.write(struct.pack("<I", ifd))
        self.f.close()


# =====================================================================
# Rasterizado
# =====================================================================
def rasterizar(pdf, tif, png, ppp, a_rgb, icc):
    """Renderiza el corte final (sin excedente) a ppp, en franjas, directo a TIFF CMYK y PNG de prueba."""
    pymupdf.TOOLS.set_icc(False)                     # que MuPDF no toque los números CMYK
    z = ppp / 72
    ancho = round(grande.ANCHO / 25.4 * ppp)
    alto = round(grande.ALTO / 25.4 * ppp)
    x0 = round(grande.EXCEDENTE / 25.4 * ppp)        # el corte empieza tras el excedente
    t = TIFFPorFranjas(tif, ancho, alto, ppp, icc)
    p = PNGPorFranjas(png, ancho, alto, ppp)
    with pymupdf.open(pdf) as doc:
        pag = doc[0]
        for y in range(0, alto, BANDA):
            h = min(BANDA, alto - y)
            clip = pymupdf.Rect((x0 - 1) / z, (x0 + y - 1) / z, (x0 + ancho + 1) / z, (x0 + y + h + 1) / z)
            pix = pag.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip, colorspace=pymupdf.csCMYK, alpha=False)
            a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 4)
            dx, dy = x0 - pix.x, x0 + y - pix.y
            franja = np.ascontiguousarray(a[dy:dy + h, dx:dx + ancho])
            assert franja.shape == (h, ancho, 4), (franja.shape, pix.irect)
            t.filas(franja)
            rgb = ImageCms.applyTransform(Image.frombuffer("CMYK", (ancho, h), franja.tobytes(), "raw", "CMYK", 0, 1), a_rgb)
            p.filas(np.asarray(rgb, np.uint8))
    t.cerrar()
    p.cerrar()
    return ancho, alto


def vista(pdf, png, a_rgb, ppp=30):
    pymupdf.TOOLS.set_icc(False)
    with pymupdf.open(pdf) as doc:
        pag = doc[0]
        b = grande.EXCEDENTE / 25.4 * 72
        r = pag.rect
        pix = pag.get_pixmap(dpi=ppp, colorspace=pymupdf.csCMYK, alpha=False,
                             clip=pymupdf.Rect(b, b, r.width - b, r.height - b))
        img = Image.frombytes("CMYK", (pix.width, pix.height), pix.samples)
        ImageCms.applyTransform(img, a_rgb).save(png)


LEEME = """EMERGE FM — PENDÓN 80 × 200 cm
Archivos para imprenta
==============================================================

Medida final: 80 cm de ancho × 200 cm de alto (vertical).
Dos diseños: 1 Negro (principal) y 2 Verde. Cada carpeta trae el mismo diseño en tres formatos:

1) PDF  — EL ARCHIVO RECOMENDADO PARA IMPRIMIR
   · Vectorial: no tiene resolución fija, se imprime nítido a cualquier tamaño.
   · CMYK, textos convertidos a curvas (no necesita fuentes).
   · Incluye 1 cm de excedente por lado (el PDF mide 82 × 202 cm). La línea de corte (TrimBox) está
     marcada en el archivo a 80 × 200 cm.
   · Perfil de salida incrustado: {perfil}.

2) TIF  — IMAGEN CMYK EN ALTA RESOLUCIÓN
   · {ppp} ppp a tamaño final 80 × 200 cm ({ancho} × {alto} píxeles), sin excedente.
   · CMYK con los mismos valores del PDF y el perfil incrustado.
   · Úsenlo si su equipo trabaja con imágenes en vez de PDF.

3) PNG  — IMAGEN RGB EN ALTA RESOLUCIÓN (simulación de color impreso)
   · {ppp} ppp a tamaño final 80 × 200 cm ({ancho} × {alto} píxeles).
   · Muestra cómo se verán los colores IMPRESOS (convertidos desde el CMYK), no los colores de pantalla.
   · Sirve como referencia de color o si su equipo solo acepta PNG.

COLORES (CMYK)
   Verde Señal (fondo del verde, detalles del negro) ... C80  M0  Y60  K0
   Negro de fondo (negro enriquecido) ................. C60  M40 Y40  K100
   Blanco ............................................... sin tinta
   Ondas grises sobre negro ............................. K95
   Ondas sobre verde .................................... C84  M0  Y63  K4
   Rayitas del dial (verde oscuro) ...................... C80  M0  Y60  K60
   Línea fina bajo el nombre (negro) .................... K76

RECOMENDACIONES
   · Usar los valores CMYK tal como vienen (sin volver a convertir los colores).
   · Antes de imprimir el pendón completo, hacer una prueba de color de un trozo, sobre todo del verde.
   · Todos los textos y el logo quedan a 5 cm o más del borde, así que hay espacio para bolsillos
     de bastón u ojetillos.

Emerge FM 105.5 — Lo que suena, emerge.
"""


if __name__ == "__main__":
    icc = open(PERFIL, "rb").read()
    swop = ImageCms.ImageCmsProfile(PERFIL)
    a_rgb = ImageCms.buildTransform(swop, ImageCms.createProfile("sRGB"), "CMYK", "RGB",
                                    ImageCms.Intent.RELATIVE_COLORIMETRIC,
                                    flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
    if os.path.exists(ENTREGA):
        shutil.rmtree(ENTREGA)
    grande.formato()
    for carpeta, archivo, titulo, componer in PIEZAS:
        destino = os.path.join(ENTREGA, carpeta)
        os.makedirs(destino)
        capas, _ = componer()
        base = os.path.join(destino, archivo)
        build.escribir_pdf(recalibrar(capas), base + ".pdf", f"Emerge FM - Pendon 80x200 cm - {titulo}",
                           perfil=(PERFIL, PERFIL_NOMBRE))
        ancho, alto = rasterizar(base + ".pdf", base + f" - CMYK {PPP}ppp.tif", base + f" - {PPP}ppp.png",
                                 PPP, a_rgb, icc)
        vista(base + ".pdf", os.path.join(build.SALIDA, os.path.basename(base) + " - vista.png"), a_rgb)
        print(f"[{carpeta}] {ancho}×{alto} px")
        for f in sorted(os.listdir(destino)):
            print(f"   {f:<52} {os.path.getsize(os.path.join(destino, f)) / 1e6:7.1f} MB")
    with open(os.path.join(ENTREGA, "LEEME - para la imprenta.txt"), "w", encoding="utf-8-sig") as f:
        f.write(LEEME.format(perfil=PERFIL_NOMBRE, ppp=PPP, ancho=ancho, alto=alto))
    zip_ruta = ENTREGA + ".zip"
    with zipfile.ZipFile(zip_ruta, "w", zipfile.ZIP_STORED) as zf:   # PDF/PNG/TIF ya vienen comprimidos
        for raiz, _, archivos in os.walk(ENTREGA):
            for a in archivos:
                ruta = os.path.join(raiz, a)
                zf.write(ruta, os.path.relpath(ruta, os.path.dirname(ENTREGA)))
    print("zip", f"{os.path.getsize(zip_ruta) / 1e6:.1f} MB")
