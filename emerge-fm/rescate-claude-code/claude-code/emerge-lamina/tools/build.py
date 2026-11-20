# -*- coding: utf-8 -*-
"""Lámina Emerge FM 60×120 cm — «Placa institucional» (motor PDF compartido con dial.py).

Genera en salida/, en negro y en verde:
  emerge-fm-lamina-placa-60x120-{negro,verde}-imprenta.pdf   CMYK, textos en curvas, 5 mm de excedente
  emerge-fm-lamina-placa-60x120-{negro,verde}-vista.svg/png  gemelo RGB (mismo trazado) para revisar

Uso:  python tools/build.py
"""
import math
import os
import zlib

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = os.path.join(RAIZ, "fonts")
SALIDA = os.path.join(RAIZ, "salida")

# ---------- formato (mm) ----------
ANCHO, ALTO = 600.0, 1200.0
EXCEDENTE = 5.0

# ---------- textos ----------
TXT_MARCA = ("EMERGE", "FM")
TXT_FRECUENCIA = "105.5"
TXT_ESLOGAN = "Lo que suena, emerge."

# ---------- color: (CMYK imprenta, RGB pantalla) ----------
NEGRO = ((0.60, 0.40, 0.40, 1.00), "#000000")   # negro enriquecido
BLANCO = ((0, 0, 0, 0), "#FFFFFF")
VERDE = ((0.68, 0, 0.50, 0), "#00E6AB")          # Verde Señal, aproximación CMYK
GRIS = ((0, 0, 0, 0.45), "#8C8C8C")              # Gris Medio
GRIS_OSCURO = ((0, 0, 0, 0.76), "#3D3D3D")
GRIS_SUPERFICIE = ((0, 0, 0, 0.95), "#161616")  # ondas de fondo: solo tinta negra sobre el negro enriquecido
VERDE_OSCURO = ((0.71, 0, 0.51, 0.03), "#00D29C")   # ondas sobre el verde (igual que el imán)
VERDE_FILETE = ((0.68, 0, 0.50, 0.60), "#0B7A5C")   # verde + K60 (lo que daría un K60 sobreimpreso)

# ---------- composición (mm, origen arriba-izquierda del formato final) ----------
# Una sola columna centrada: isotipo · logotipo · filete · 105.5 · eslogan.
# Logotipo, 105.5 y eslogan comparten ancho de tinta, y la columna se centra en el alto
# midiendo la tinta real de cada pieza (un poco más arriba del centro geométrico).
CX = ANCHO / 2
COLUMNA = 472.0
ISO_CAJA = {"negro": 440.0, "verde": 400.0}   # en verde el isotipo lleva su disco negro (= la caja)
ESPACIOS = (104.0, 64.0, 64.0, 58.0)          # isotipo→logotipo, logotipo→filete, filete→105.5, 105.5→eslogan
FILETE_ANCHO, FILETE_GROSOR = 160.0, 2.0
CENTRADO_OPTICO = 0.46                        # parte del aire que va arriba
ONDAS_X, ONDAS_RADIOS, ONDAS_GROSOR = 560.0, (120.0, 210.0, 300.0, 390.0), 34.0
ONDAS_AIRE = 26.0                             # la onda mayor pasa bajo el logotipo sin tocarlo
ONDAS_Y_MIN = 1100.0                          # centro de las ondas: nunca más arriba que esto

# ---------- pie: web y redes (2026-11-19) ----------
# Solo en las versiones listadas; grande.py lo apaga para que el 80×200 y el pendón no cambien.
PIE_REDES = ("negro",)
TXT_WEB = "emergefm.cl"
REDES = (("instagram", "@radioemergefm"), ("facebook", "Radio Emerge FM Rancagua"))
PIE_ARRIBA = 100.0         # con pie, la columna sube: borde superior → tinta del isotipo (antes ~147)
PIE_MARGEN = 54.0          # borde inferior → pie de la tinta del pie
PIE_WEB_ANCHO = 220.0      # ancho de tinta de «emergefm.cl» (Unbounded SemiBold)
PIE_WEB_REDES = 27.0       # web → primera fila de redes
PIE_CUERPO = 22.0          # cuerpo de las redes (Space Grotesk Bold)
PIE_INTERLINEA = 35.0      # línea base a línea base entre redes
PIE_ICONO = 23.0           # lado del ícono
PIE_ICONO_AIRE = 10.0      # ícono → texto

VERSIONES = {
    "negro": dict(fondo=NEGRO, ondas=GRIS_SUPERFICIE, emerge=BLANCO, fm=VERDE, filete=GRIS_OSCURO,
                  frecuencia=BLANCO, eslogan=VERDE, disco=None, web=BLANCO, icono=VERDE, red=BLANCO),
    "verde": dict(fondo=VERDE, ondas=VERDE_OSCURO, emerge=NEGRO, fm=NEGRO, filete=VERDE_FILETE,
                  frecuencia=NEGRO, eslogan=NEGRO, disco=NEGRO, web=NEGRO, icono=NEGRO, red=NEGRO),
}


# =====================================================================
# Tipografía → contornos
# =====================================================================
class PenContornos(BasePen):
    """Recoge contornos como listas de segmentos M/L/C (las cuadráticas llegan ya como cúbicas)."""

    def __init__(self, glyphSet):
        super().__init__(glyphSet)
        self.contornos = []

    def _moveTo(self, pt):
        self.contornos.append([("M", pt)])

    def _lineTo(self, pt):
        self.contornos[-1].append(("L", pt))

    def _curveToOne(self, p1, p2, p3):
        self.contornos[-1].append(("C", p1, p2, p3))

    def _closePath(self):
        self.contornos[-1].append(("Z",))


class Fuente:
    def __init__(self, archivo):
        self.tt = TTFont(os.path.join(FUENTES, archivo))
        self.upm = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.glifos = self.tt.getGlyphSet()
        self.avances = self.tt["hmtx"].metrics
        self.kern = self._tablas_kern()

    def _tablas_kern(self):
        """Subtablas PairPos de la feature 'kern' de GPOS, agrupadas por lookup."""
        if "GPOS" not in self.tt:
            return []
        gpos = self.tt["GPOS"].table
        indices = []
        for rec in gpos.FeatureList.FeatureRecord:
            if rec.FeatureTag == "kern":
                for i in rec.Feature.LookupListIndex:
                    if i not in indices:
                        indices.append(i)
        lookups = []
        for i in sorted(indices):
            subtablas = []
            for st in gpos.LookupList.Lookup[i].SubTable:
                if st.LookupType == 9:
                    st = st.ExtSubTable
                if st.LookupType == 2:
                    subtablas.append(st)
            if subtablas:
                lookups.append(subtablas)
        return lookups

    def kerning(self, izq, der):
        total = 0
        for subtablas in self.kern:
            for st in subtablas:
                cobertura = st.Coverage.glyphs
                if izq not in cobertura:
                    continue
                if st.Format == 1:
                    par = next((p for p in st.PairSet[cobertura.index(izq)].PairValueRecord
                                if p.SecondGlyph == der), None)
                    if par is None:
                        continue
                    total += (par.Value1.XAdvance or 0) if par.Value1 else 0
                else:
                    c1 = st.ClassDef1.classDefs.get(izq, 0)
                    c2 = st.ClassDef2.classDefs.get(der, 0)
                    v = st.Class1Record[c1].Class2Record[c2].Value1
                    total += (v.XAdvance or 0) if v else 0
                break
        return total

    def contornos(self, texto, tracking_em=0.0):
        """Contornos del texto en unidades de fuente (y hacia arriba), con kerning y tracking."""
        nombres = []
        for ch in texto:
            if ord(ch) not in self.cmap:
                raise SystemExit(f"La fuente no trae el carácter {ch!r}")
            nombres.append(self.cmap[ord(ch)])
        salida, x = [], 0.0
        for i, nombre in enumerate(nombres):
            if i:
                x += self.kerning(nombres[i - 1], nombre) + tracking_em * self.upm
            pen = PenContornos(self.glifos)
            self.glifos[nombre].draw(pen)
            for c in pen.contornos:
                salida.append([(s[0],) + tuple((px + x, py) for px, py in s[1:]) for s in c])
            x += self.avances[nombre][0]
        return salida


def muestras(contornos, pasos=24):
    """Puntos sobre el trazo real (no el casco de control) para medir la tinta."""
    for c in contornos:
        actual = None
        for s in c:
            if s[0] in ("M", "L"):
                actual = s[1]
                yield actual
            elif s[0] == "C":
                p0, p1, p2, p3 = actual, s[1], s[2], s[3]
                for k in range(1, pasos + 1):
                    t = k / pasos
                    u = 1 - t
                    yield (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                           u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])
                actual = p3


def caja(contornos):
    xs, ys = zip(*muestras(contornos))
    return min(xs), min(ys), max(xs), max(ys)


def transformar(contornos, escala, dx, base):
    """Unidades de fuente → mm del formato (y hacia abajo)."""
    return [[(s[0],) + tuple((dx + px * escala, base - py * escala) for px, py in s[1:]) for s in c]
            for c in contornos]


def texto_centrado(fuente, partes, base, ancho_tinta, tracking_em=0.0):
    """Compone `partes` [(texto, color)] en una línea cuya tinta mide `ancho_tinta` mm, centrada en CX.

    Devuelve [(contornos_mm, color)] y el cuerpo resultante en mm.
    """
    completo = "".join(t for t, _ in partes)
    todos = fuente.contornos(completo, tracking_em)
    x0, _, x1, _ = caja(todos)
    escala = ancho_tinta / (x1 - x0)
    dx = CX - ancho_tinta / 2 - x0 * escala
    # reparte los contornos por tramo de color según cuántos aporta cada tramo
    capas, inicio = [], 0
    for i, (t, color) in enumerate(partes):
        prefijo = "".join(p for p, _ in partes[:i + 1])
        fin = len(fuente.contornos(prefijo, tracking_em))
        capas.append((transformar(todos[inicio:fin], escala, dx, base), color))
        inicio = fin
    return capas, escala * fuente.upm


# =====================================================================
# Isotipo (geometría exacta de emerge-fm-avatar.svg, caja 360×360)
# =====================================================================
ISO_GROSOR = 17.0
ISO_ARCOS = [  # (radio, punto inicial, punto final, color) — todos en sentido horario
    (130.0, (175.46, 50.08), (50.49, 168.67), BLANCO),
    (102.5, (183.58, 282.44), (282.50, 180.00), VERDE),
    (75.5, (180.00, 104.50), (105.23, 169.49), BLANCO),
]
ISO_ANILLO = (44.5, VERDE)


def arco(cx, cy, r, a0, a1):
    """Segmentos cúbicos de un arco circular de a0 a a1 (radianes, y hacia abajo)."""
    n = max(1, math.ceil(abs(a1 - a0) / (math.pi / 2) - 1e-9))
    paso = (a1 - a0) / n
    k = 4 / 3 * math.tan(paso / 4)
    segs = []
    for i in range(n):
        t0, t1 = a0 + i * paso, a0 + (i + 1) * paso
        p0 = (cx + r * math.cos(t0), cy + r * math.sin(t0))
        p3 = (cx + r * math.cos(t1), cy + r * math.sin(t1))
        p1 = (p0[0] - k * r * math.sin(t0), p0[1] + k * r * math.cos(t0))
        p2 = (p3[0] + k * r * math.sin(t1), p3[1] - k * r * math.cos(t1))
        segs.append((p0, p1, p2, p3))
    return segs


def sector(cx, cy, r, grosor, a0, a1):
    """Arco con grosor convertido a forma cerrada (extremos rectos, como stroke-linecap: butt)."""
    ext = arco(cx, cy, r + grosor / 2, a0, a1)
    inte = arco(cx, cy, r - grosor / 2, a1, a0)
    c = [("M", ext[0][0])] + [("C", s[1], s[2], s[3]) for s in ext]
    c += [("L", inte[0][0])] + [("C", s[1], s[2], s[3]) for s in inte] + [("Z",)]
    return c


def isotipo(cx, cy, lado):
    e = lado / 360.0
    capas = []
    for r, ini, fin, color in ISO_ARCOS:
        a0 = math.atan2(ini[1] - 180, ini[0] - 180)
        a1 = math.atan2(fin[1] - 180, fin[0] - 180)
        while a1 <= a0:
            a1 += 2 * math.pi
        capas.append(([sector(cx, cy, r * e, ISO_GROSOR * e, a0, a1)], color))
    r, color = ISO_ANILLO
    capas.append((anillo(cx, cy, r * e, ISO_GROSOR * e), color))
    return capas


def anillo(cx, cy, r, grosor):
    """Anillo completo como dos círculos de sentido opuesto (hueco con relleno nonzero)."""
    tau = 2 * math.pi
    fuera = arco(cx, cy, r + grosor / 2, 0, tau)
    dentro = arco(cx, cy, r - grosor / 2, tau, 0)
    return [[("M", s[0][0])] + [("C", p[1], p[2], p[3]) for p in s] + [("Z",)] for s in (fuera, dentro)]


def rectangulo(x, y, w, h):
    return [[("M", (x, y)), ("L", (x + w, y)), ("L", (x + w, y + h)), ("L", (x, y + h)), ("Z",)]]


def circulo(cx, cy, r):
    return anillo(cx, cy, r / 2, r)[:1]


def invertir(contorno):
    """Mismo contorno recorrido al revés (para huecos con relleno nonzero)."""
    segs, actual = [], None
    for s in contorno:
        if s[0] == "M":
            actual = s[1]
        elif s[0] == "L":
            segs.append((actual, ("L",), s[1]))
            actual = s[1]
        elif s[0] == "C":
            segs.append((actual, ("C", s[1], s[2]), s[3]))
            actual = s[3]
    salida = [("M", segs[-1][2])]
    for ini, tipo, fin in reversed(segs):
        salida.append(("L", ini) if tipo[0] == "L" else ("C", tipo[2], tipo[1], ini))
    return salida + [("Z",)]


def rect_redondeado(x, y, w, h, r):
    c = [("M", (x + r, y)), ("L", (x + w - r, y))]
    for cx, cy, a0, recta in ((x + w - r, y + r, -math.pi / 2, (x + w, y + h - r)),
                              (x + w - r, y + h - r, 0, (x + r, y + h)),
                              (x + r, y + h - r, math.pi / 2, (x, y + r)),
                              (x + r, y + r, math.pi, None)):
        c += [("C", s[1], s[2], s[3]) for s in arco(cx, cy, r, a0, a0 + math.pi / 2)]
        if recta is not None:
            c.append(("L", recta))
    return c + [("Z",)]


def icono_instagram(x, y, s, color, fondo):
    t = 0.095 * s
    marco = [rect_redondeado(x, y, s, s, 0.29 * s), invertir(rect_redondeado(x + t, y + t, s - 2 * t, s - 2 * t, 0.29 * s - t))]
    return [(marco + anillo(x + s / 2, y + s / 2, 0.215 * s, t) + circulo(x + 0.765 * s, y + 0.235 * s, 0.068 * s), color)]


def icono_facebook(x, y, s, color, fondo):
    """Círculo lleno con la «f» calada de verdad (hueco: deja ver las ondas que pasen detrás).

    La f es un solo contorno: asta que abre el borde inferior, travesaño y gancho superior.
    """
    cx, cy, R = x + s / 2, y + s / 2, s / 2
    xs, hw, yt, rh = x + 0.555 * s, 0.078 * s, y + 0.40 * s, 0.165 * s
    xl, xr = xs - hw, xs + hw
    b0, b1, c0, c1 = x + 0.345 * s, x + 0.735 * s, y + 0.505 * s, y + 0.635 * s
    xe = xs + rh + 0.05 * s
    ro, ri = rh + hw, rh - hw
    borde = lambda px: (px, cy + math.sqrt(R * R - (px - cx) ** 2))
    f = [("M", borde(xl)), ("L", (xl, c1)), ("L", (b0, c1)), ("L", (b0, c0)), ("L", (xl, c0)), ("L", (xl, yt))]
    f += [("C", q[1], q[2], q[3]) for q in arco(xs + rh, yt, ro, math.pi, 1.5 * math.pi)]
    f += [("L", (xe, yt - ro)), ("L", (xe, yt - ri)), ("L", (xs + rh, yt - ri))]
    f += [("C", q[1], q[2], q[3]) for q in arco(xs + rh, yt, ri, 1.5 * math.pi, math.pi)]
    f += [("L", (xr, c0)), ("L", (b1, c0)), ("L", (b1, c1)), ("L", (xr, c1)), ("L", borde(xr))]
    a_r = math.atan2(borde(xr)[1] - cy, xr - cx)
    a_l = math.atan2(borde(xl)[1] - cy, xl - cx)
    f += [("C", q[1], q[2], q[3]) for q in arco(cx, cy, R, a_r, a_l)] + [("Z",)]
    return [(circulo(cx, cy, R) + [invertir(f)], color)]


ICONOS = {"instagram": icono_instagram, "facebook": icono_facebook}


def texto_en(fuente, texto, x, base, cuerpo):
    """Texto con la tinta empezando en x, a un cuerpo dado (mm). Devuelve contornos y ancho de tinta."""
    escala = cuerpo / fuente.upm
    cont = fuente.contornos(texto)
    x0, _, x1, _ = caja(cont)
    return transformar(cont, escala, x - x0 * escala, base), (x1 - x0) * escala


def pie(v):
    """Web centrada y, debajo, las redes en lista (íconos alineados) centrada como bloque. Techo de tinta en y = 0."""
    semi = Fuente("Unbounded-SemiBold.ttf")
    grot = Fuente("SpaceGrotesk-Bold.ttf")
    web, _ = texto_centrado(semi, [(TXT_WEB, v["web"])], 0, PIE_WEB_ANCHO)
    techo, suelo = alto_tinta(web)
    web = mover(web, -techo)
    alto_web = suelo - techo

    mayuscula = grot.tt["OS/2"].sCapHeight / grot.upm * PIE_CUERPO
    anchos = [texto_en(grot, t, 0, 0, PIE_CUERPO)[1] for _, t in REDES]
    ancho = PIE_ICONO + PIE_ICONO_AIRE + max(anchos)
    x0 = CX - ancho / 2
    capas = list(web)
    base = alto_web + PIE_WEB_REDES + mayuscula
    for red, texto in REDES:
        cy = base - mayuscula / 2
        capas += ICONOS[red](x0, cy - PIE_ICONO / 2, PIE_ICONO, v["icono"], v["fondo"])
        cont, _ = texto_en(grot, texto, x0 + PIE_ICONO + PIE_ICONO_AIRE, base, PIE_CUERPO)
        capas.append((cont, v["red"]))
        base += PIE_INTERLINEA
    a, b = alto_tinta(capas)
    return mover(capas, -a), b - a


# =====================================================================
# Composición
# =====================================================================
def mover(capas, dy):
    return [([[(seg[0],) + tuple((x, y + dy) for x, y in seg[1:]) for seg in c] for c in contornos], color)
            for contornos, color in capas]


def alto_tinta(capas):
    ys = [y for contornos, _ in capas for _, y in muestras(contornos)]
    return min(ys), max(ys)


def componer(nombre):
    v = VERSIONES[nombre]
    negra = Fuente("Unbounded-Black.ttf")
    semi = Fuente("Unbounded-SemiBold.ttf")
    informe = []

    # piezas armadas en y = 0; después se apilan según su tinta
    caja_iso = ISO_CAJA[nombre]
    iso = isotipo(CX, 0, caja_iso)
    if v["disco"]:
        iso = [(anillo(CX, 0, caja_iso / 4, caja_iso / 2)[:1], v["disco"])] + iso
    marca, cuerpo = texto_centrado(negra, [(TXT_MARCA[0] + " ", v["emerge"]), (TXT_MARCA[1], v["fm"])], 0, COLUMNA)
    informe.append(("Logotipo", cuerpo))
    filete = [(rectangulo(CX - FILETE_ANCHO / 2, -FILETE_GROSOR / 2, FILETE_ANCHO, FILETE_GROSOR), v["filete"])]
    frec, cuerpo = texto_centrado(negra, [(TXT_FRECUENCIA, v["frecuencia"])], 0, COLUMNA)
    informe.append(("Frecuencia", cuerpo))
    eslogan, cuerpo = texto_centrado(semi, [(TXT_ESLOGAN, v["eslogan"])], 0, COLUMNA)
    informe.append(("Eslogan", cuerpo))

    piezas = [iso, marca, filete, frec, eslogan]
    altos = [alto_tinta(pz) for pz in piezas]
    total = sum(b - a for a, b in altos) + sum(ESPACIOS)
    y, capas_pie = (ALTO - total) * CENTRADO_OPTICO, []
    if nombre in PIE_REDES:
        capas_pie, alto_pie = pie(v)
        techo_pie = ALTO - PIE_MARGEN - alto_pie
        capas_pie = mover(capas_pie, techo_pie)
        y = PIE_ARRIBA
        informe.append(("Pie", alto_pie))
        informe.append(("Aire al pie", techo_pie - (y + total)))
    colocadas, tramos = [], []
    for pz, (a, b), aire in zip(piezas, altos, ESPACIOS + (0,)):
        colocadas.append(mover(pz, y - a))
        tramos.append((y, y + b - a))
        y += b - a + aire

    capas = [(rectangulo(-EXCEDENTE, -EXCEDENTE, ANCHO + 2 * EXCEDENTE, ALTO + 2 * EXCEDENTE), v["fondo"])]
    pie_logotipo = tramos[1][1]
    oy = max(ONDAS_Y_MIN, pie_logotipo + ONDAS_AIRE + ONDAS_RADIOS[-1] + ONDAS_GROSOR / 2)
    capas.append(([c for r in ONDAS_RADIOS for c in anillo(ONDAS_X, oy, r, ONDAS_GROSOR)], v["ondas"]))
    for pz in colocadas:
        capas += pz
    capas += capas_pie
    informe.append(("Márgenes", (tramos[0][0], ALTO - tramos[-1][1])))
    return capas, informe


# =====================================================================
# Salidas
# =====================================================================
PT = 72 / 25.4


def escribir_pdf(capas, ruta, titulo="Emerge FM - Lamina 60x120 cm - Placa institucional", perfil=None, rgb=False):
    """perfil = (ruta del ICC CMYK, nombre): lo incrusta como OutputIntent para declarar qué CMYK es.
    rgb = True: pinta con los colores de pantalla exactos (#00E6AB, etc.) en vez del CMYK de imprenta."""
    w, h = (ANCHO + 2 * EXCEDENTE) * PT, (ALTO + 2 * EXCEDENTE) * PT

    def p(pt):  # mm del formato → puntos PDF (y hacia arriba, origen en la esquina del excedente)
        return f"{(pt[0] + EXCEDENTE) * PT:.3f} {h - (pt[1] + EXCEDENTE) * PT:.3f}"

    ops = [f"0 0 {w:.3f} {h:.3f} re W n"]  # las ondas se salen del formato: recorte al excedente
    for contornos, (cmyk, hexa) in capas:
        if rgb:
            ops.append("%.4f %.4f %.4f rg" % tuple(int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)))
        else:
            ops.append("%.2f %.2f %.2f %.2f k" % cmyk)
        for c in contornos:
            for s in c:
                if s[0] == "M":
                    ops.append(p(s[1]) + " m")
                elif s[0] == "L":
                    ops.append(p(s[1]) + " l")
                elif s[0] == "C":
                    ops.append(" ".join(p(q) for q in s[1:]) + " c")
                else:
                    ops.append("h")
        ops.append("f")  # relleno nonzero
    flujo = zlib.compress("\n".join(ops).encode("ascii"), 9)

    b = EXCEDENTE * PT
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w:.3f} {h:.3f}] "
         f"/BleedBox [0 0 {w:.3f} {h:.3f}] /TrimBox [{b:.3f} {b:.3f} {w - b:.3f} {h - b:.3f}] "
         f"/Resources << >> /Contents 4 0 R >>").encode("ascii"),
        b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(flujo) + flujo + b"\nendstream",
        f"<< /Title ({titulo}) /Author (Emerge FM) /Creator (emerge-lamina/tools) >>".encode("ascii"),
    ]
    if perfil:
        icc_ruta, icc_nombre = perfil
        icc = zlib.compress(open(icc_ruta, "rb").read(), 9)
        objetos[0] = b"<< /Type /Catalog /Pages 2 0 R /OutputIntents [7 0 R] >>"
        objetos[4] = f"<< /Title ({titulo}) /Author (Emerge FM) /Creator (emerge-lamina/tools) /Trapped /False >>".encode("ascii")
        objetos.append(b"<< /N 4 /Alternate /DeviceCMYK /Length %d /Filter /FlateDecode >>\nstream\n" % len(icc)
                       + icc + b"\nendstream")
        objetos.append(f"<< /Type /OutputIntent /S /GTS_PDFX /OutputConditionIdentifier ({icc_nombre}) "
                       f"/Info ({icc_nombre}) /RegistryName (http://www.color.org) /DestOutputProfile 6 0 R >>"
                       .encode("ascii"))
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    posiciones = []
    for i, cuerpo in enumerate(objetos, 1):
        posiciones.append(len(out))
        out += b"%d 0 obj\n" % i + cuerpo + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1)
    for pos in posiciones:
        out += b"%010d 00000 n \n" % pos
    out += b"trailer\n<< /Size %d /Root 1 0 R /Info 5 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objetos) + 1, xref)
    with open(ruta, "wb") as f:
        f.write(out)


def escribir_svg(capas, ruta):
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ANCHO:g} {ALTO:g}">']
    for contornos, (_, rgb) in capas:
        d = []
        for c in contornos:
            for s in c:
                if s[0] == "Z":
                    d.append("Z")
                else:
                    d.append(s[0] + " ".join(f"{x:.3f} {y:.3f}" for x, y in s[1:]))
        partes.append(f'<path fill="{rgb}" d="{"".join(d)}"/>')
    partes.append("</svg>")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(partes))


def vista_png(svg, png):
    import shutil
    import subprocess
    chrome = shutil.which("chrome") or r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome):
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1000,2000",
                        f"--screenshot={png}", "file:///" + svg.replace("\\", "/").replace(" ", "%20")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    for nombre in VERSIONES:
        capas, informe = componer(nombre)
        base = os.path.join(SALIDA, f"emerge-fm-lamina-placa-60x120-{nombre}")
        escribir_pdf(capas, base + "-imprenta.pdf", f"Emerge FM - Lamina 60x120 cm - Placa institucional {nombre}")
        escribir_svg(capas, base + "-vista.svg")
        vista_png(base + "-vista.svg", base + "-vista.png")
        if nombre in PIE_REDES:   # colores tal cual (RGB de pantalla), sin pasar por CMYK
            escribir_pdf(capas, base + "-color.pdf", f"Emerge FM - Lamina 60x120 cm - Placa institucional {nombre}",
                         rgb=True)
            import pymupdf
            pagina = pymupdf.open(base + "-color.pdf")[0]
            pagina.get_pixmap(dpi=150, clip=pagina.trimbox).save(base + "-color.png")
        print(f"[{nombre}]")
        for texto, valor in informe:
            print(f"   {texto:<11}", f"{valor:6.1f} mm" if isinstance(valor, float) else
                  "arriba %.0f mm, abajo %.0f mm" % valor)

