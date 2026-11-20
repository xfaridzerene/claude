# -*- coding: utf-8 -*-
"""Reel «La Ciudad de la Furia» (estreno 9 de noviembre) — compositor.

Dos tomas en un mismo archivo: exterior (cuadros 0-310) y estudio (311-635).

  python render_nov9.py sheet 8.4 10.2 ...      -> pv_sheet.jpg (tiempos en segundos)
  python render_nov9.py frames 300 305 310 ...  -> pv_frames.jpg (cuadros exactos, 6 columnas)
  python render_nov9.py render <a> <b> <salida> -> video sin audio de los cuadros [a, b)
"""
import os, sys, math, subprocess, time, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import uniform_filter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gfx3d as g
from gfx3d import W, H, clamp, ease_out, ease_in, back_out

FF = sorted(glob.glob(r"C:\Users\farid\AppData\Local\CapCut\Apps\*\ffmpeg.exe"))[-1]
SRC = r"C:\Users\farid\Desktop\kaco en bruto 9 nov.mp4"
FPS = 30.0
N0, N1 = 0, 636
CUT = 311                              # primer cuadro de la toma de estudio
T_CUT = CUT / FPS
TR = 9                                 # la transición dura TR cuadros a cada lado del corte
IRIS = 9                               # apertura y cierre del video
SW, SH = 2160, 3840
BRAND = r"C:\Users\farid\Desktop\EMERGE FM\Nuevo branding"
LOGO_PROG = r"C:\Users\farid\Desktop\claude code\furia-promo\src\logo-programa.png"

# ------------------------------------------------------------------ zoom
ZOOM = [
    (0.00, 1.00, 1.04),
    (1.44, 1.08, 1.11),
    (3.14, 1.00, 1.03),
    (4.76, 1.06, 1.09),
    (6.54, 1.00, 1.03),
    (7.86, 1.04, 1.06),
    (8.62, 1.10, 1.13),
    (T_CUT, 1.00, 1.03),
    (11.34, 1.06, 1.08),
    (12.20, 1.00, 1.02),
    (14.64, 1.08, 1.11),
    (16.00, 1.14, 1.17),
    (17.46, 1.00, 1.03),
    (18.46, 1.08, 1.10),
    (19.40, 1.00, 1.08),
    (99, 1, 1),
]
ANCHOR_A = (0.53, 0.38)                # punto fijo del zoom: la cara en cada toma
ANCHOR_B = (0.50, 0.34)


def zoom_at(ts):
    for i in range(len(ZOOM) - 1):
        t0, a, b = ZOOM[i]; t1 = ZOOM[i + 1][0]
        if t0 <= ts < t1:
            return a + (b - a) * (ts - t0) / (min(t1, N1 / FPS) - t0)
    return 1.0


def box_at(ts, shake=False):
    z = zoom_at(ts)
    ax, ay = ANCHOR_A if ts < T_CUT else ANCHOR_B
    dx = dy = 0.0
    if shake:
        a = impact(ts)
        if a > 0.01:
            z += 0.045 * a
            dx = 0.011 * a * math.sin(ts * 93.0)
            dy = 0.007 * a * math.sin(ts * 71.0 + 1.0)
    x0, y0 = ax * (1 - 1 / z), ay * (1 - 1 / z)
    x0 = clamp(x0 + dx, 0.0, 1 - 1 / z); y0 = clamp(y0 + dy, 0.0, 1 - 1 / z)
    return (x0, y0, x0 + 1 / z, y0 + 1 / z)


# ------------------------------------------------------------------ gráficos 3D detrás de la persona
def _logo():
    return Image.open(os.path.join(BRAND, "emerge-fm-logo-color-transparent.png"))


TEX = {}
ISO_W = 800


def build_tex():
    Wh, Vd, Am = g.BLANCO, g.VERDE, g.AMBAR
    vd_side, am_side, nj_side = (0, 150, 112), (196, 122, 0), (214, 62, 16)
    TEX["nombre"] = g.text_tex([("KACO", 150, Wh, vd_side), ("LÓPEZ", 150, Vd, (0, 120, 90))], depth=46)
    TEX["noticia"] = g.text_tex([("¡TREMENDA", 112, Wh, am_side), ("NOTICIA!", 138, Am, am_side)], depth=46)
    TEX["fecha"] = g.text_tex([("LUNES 9", 158, Am, am_side), ("DE NOVIEMBRE", 88, Wh, am_side)], depth=50)
    TEX["hora"] = g.text_tex([("A LAS", 100, Wh, am_side, None, 0.22), ("18:00", 244, Am, am_side)], depth=58, gap=0.2)
    TEX["vivo"] = g.text_tex([("EN VIVO", 168, Wh, (190, 24, 18))], depth=50)
    TEX["estudios"] = g.text_tex([("DESDE LOS", 92, Wh, vd_side), ("ESTUDIOS", 138, Vd, (0, 120, 90))], depth=46)
    TEX["emerge"] = g.text_tex([("EMERGE FM", 122, Wh, vd_side)], depth=46)
    TEX["dial"] = g.text_tex([("105.5", 270, Vd, (0, 118, 88))], depth=74)
    TEX["dialfm"] = g.text_tex([("FM", 112, Wh, vd_side, None, 0.3), ("105.5", 270, Vd, (0, 118, 88))], depth=74, gap=0.2)
    TEX["iso"] = g.image_tex(_logo(), ISO_W, depth=56, side_mul=0.42)
    TEX["furia"] = g.image_tex(Image.open(LOGO_PROG), 960, depth=62, side_tint=nj_side)


# textura, entra, sale, solape con la cabeza (px), giro base Y, atenúa fondo, estilo
EVENTS = [
    ("nombre", 0.82, 1.84, 36, -10, 0.25, "rise"),
    ("noticia", 2.02, 3.12, 36, 9, 0.25, "slam"),
    ("fecha", 3.24, 4.74, 30, -9, 0.30, "rise"),
    ("hora", 5.26, 6.50, 85, -8, 0.30, "slam"),
    ("furia", 6.60, 7.84, 58, 8, 0.50, "slam"),
    ("iso", 7.86, 8.62, 0, 10, 0.45, "spin"),
    ("emerge", 7.98, 8.62, 0, 8, 0.45, "rise"),
    ("dial", 8.62, 10.05, 95, -9, 0.45, "slam"),
    ("estudios", 11.34, 12.18, 40, -8, 0.30, "slam"),
    ("iso", 12.20, 13.02, 0, -10, 0.45, "spin"),
    ("emerge", 12.30, 13.02, 0, -8, 0.45, "rise"),
    ("dialfm", 13.02, 14.56, 95, 9, 0.45, "slam"),
    ("fecha", 14.96, 15.96, 30, 9, 0.30, "rise"),
    ("hora", 16.00, 17.40, 85, -8, 0.30, "slam"),
    ("vivo", 18.46, 19.36, 48, 8, 0.25, "slam"),
    ("furia", 19.40, 99.0, 62, -8, 0.50, "slam"),
]
RING_COLOR = {"hora": g.AMBAR, "fecha": g.AMBAR, "noticia": g.AMBAR, "vivo": (255, 59, 48), "furia": g.NARANJA}
POS = []                                 # centro (x, y) de cada evento
HEAD = []                                # centro de la cabeza durante cada evento
T_IN, T_OUT = 0.34, 0.18
HITS = [(e[1] + 0.6 * T_IN, i) for i, e in enumerate(EVENTS) if e[6] in ("slam", "spin")]


def impact(ts):
    """Golpe de cámara al aterrizar un gráfico: 1 en el impacto y cae rápido."""
    a = 0.0
    for t, _ in HITS:
        if t <= ts < t + 0.5:
            a = max(a, math.exp(-(ts - t) / 0.09))
    return a


def head_track():
    """Punto más alto y centro de la cabeza por cuadro, en coordenadas de salida."""
    top = np.full(N1 - N0, 540.0); cx = np.full(N1 - N0, 560.0)
    if MATTE is not None:
        for i in range(len(MATTE)):
            m = MATTE[i, 1] > 140
            rows = np.where(m.sum(1) > 6)[0]
            if len(rows):
                r = rows[0]
                cols = np.where(m[r + 12:r + 45].any(0))[0]
                top[i] = r * 1200 / 320
                if len(cols):
                    cx[i] = (cols[0] + cols[-1]) / 2 * 1080 / 320
    for i in range(N1 - N0):
        bx = box_at((N0 + i) / FPS)
        top[i] = (top[i] / H - bx[1]) / (bx[3] - bx[1]) * H
        cx[i] = (cx[i] / W - bx[0]) / (bx[2] - bx[0]) * W
    return top, cx


def layout():
    top, cx = head_track()
    for name, t0, t1, ov, *_ in EVENTS:
        a = int(t0 * FPS) - N0; b = max(a + 1, min(int(t1 * FPS) - N0, N1 - N0))
        ht, hx = float(np.median(top[a:b])), float(np.median(cx[a:b]))
        HEAD.append((hx, ht + 195))
        if name == "iso":
            POS.append((hx, ht + 195))
        elif name == "emerge":
            ring_top = ht + 195 - ISO_W / 2
            POS.append((540, max(150, ring_top - 62)))
        else:
            y = ht + ov - (TEX[name].h / 2 - TEX[name].pad)
            POS.append((540, max(TEX[name].h / 2 + 30, y)))


def draw_events(ts, canvas):
    """Dibuja los elementos activos en el lienzo premultiplicado; devuelve la atenuación de fondo."""
    dim = 0.0
    for (name, t0, t1, _ov, ry0, dm, style), (x, y) in zip(EVENTS, POS):
        if not (t0 <= ts < t1 + T_OUT):
            continue
        u = (ts - t0) / T_IN
        v = (ts - t1) / T_OUT
        e = back_out(u, 1.6)
        sway = math.sin((ts - t0) * 1.9)
        ry = ry0 + 5.0 * sway
        rx = 5.0 + 2.5 * math.sin((ts - t0) * 1.3 + 1)
        z = 0.0; dy = 0.0; op = clamp(u * 3.0)
        if style == "rise":
            dy = (1 - e) * 420; ry += (1 - ease_out(u)) * -30 * math.copysign(1, ry0)
        elif style == "slam":
            z = (1 - e) * 1500; ry += (1 - ease_out(u)) * 38 * math.copysign(1, ry0)
        elif style == "spin":
            z = (1 - e) * 900; ry += (1 - ease_out(u)) * 115 * math.copysign(1, ry0)
        if v > 0:
            k = ease_in(v)
            z += k * 1400; op *= 1 - clamp(v) ** 1.5; dy += k * 60
        g.merge(canvas, g.draw(TEX[name], (x, y + dy, z), (rx, ry, 0.0), 1.0, op))
        dim = max(dim, dm * clamp(u * 2.0) * (1 - clamp(v)))
    return dim


# ------------------------------------------------------------------ ondas de señal detrás de la persona
_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)
DUR_RING = 0.5


def draw_rings(ts, bg):
    for t, i in HITS:
        if not (t <= ts < t + DUR_RING + 0.1):
            continue
        hx, hy = HEAD[i]
        d = np.hypot(_XX - hx, _YY - hy)
        col = np.array(RING_COLOR.get(EVENTS[i][0], g.VERDE), np.float32)
        for delay, gain in ((0.0, 0.70), (0.09, 0.42)):
            k = (ts - t - delay) / DUR_RING
            if 0 <= k < 1:
                R = 130 + 1150 * ease_out(k)
                wid = 10 + 34 * k
                a = np.clip(1 - np.abs(d - R) / wid, 0, 1)[..., None] * gain * (1 - k) ** 1.2
                bg = bg * (1 - a) + col * a
    return bg


# ------------------------------------------------------------------ transición: se pasa a través del isotipo
ISO_RGBA = {}
ISO_HOLE = 1.0                           # radio del hueco central, como fracción del ancho del logo


def build_iso():
    global ISO_HOLE
    im = _logo().convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    a = np.asarray(im.getchannel("A"))
    h, w = a.shape
    cy, cx = h // 2, w // 2
    r = np.where(a[cy, cx:] > 128)[0][0]
    ISO_HOLE = r / w
    for s in (4, 1):
        ISO_RGBA[s] = im.resize((w // s, h // s), Image.LANCZOS)
    pm = np.asarray(ISO_RGBA[4], np.float32)
    pm[..., :3] *= pm[..., 3:4] / 255.0
    ISO_RGBA["pm4"] = pm


def _logo_layer(radius, cx, cy, shade=1.0):
    """Isotipo escalado para que su hueco mida `radius`; RGBA premultiplicado float."""
    full_w = ISO_RGBA[1].size[0]
    target_w = radius / ISO_HOLE
    src = ISO_RGBA[4] if target_w < full_w / 4 else ISO_RGBA[1]
    sw, sh = src.size
    k = sw / target_w
    # pantalla -> textura
    coef = (k, 0, sw / 2 - k * cx, 0, k, sh / 2 - k * cy)
    lay = src.transform((W, H), Image.AFFINE, coef, Image.BILINEAR)
    a = np.asarray(lay, np.float32)
    return np.dstack([a[..., :3] * (a[..., 3:4] / 255.0) * shade, a[..., 3]])


def _radial(frame, z, cx, cy, spread, n=5):
    """Zoom z con desenfoque radial: promedia varias copias a escalas cercanas."""
    im = Image.fromarray(frame)
    acc = None
    for j in range(n):
        zz = z * (1 + spread * (j / max(n - 1, 1) - 0.5))
        zz = max(zz, 1.0)
        box = (cx * (1 - 1 / zz), cy * (1 - 1 / zz), cx * (1 - 1 / zz) + W / zz, cy * (1 - 1 / zz) + H / zz)
        c = np.asarray(im.resize((W, H), Image.BILINEAR, box=box), np.float32)
        acc = c if acc is None else acc + c
    return acc / n


def logo_wipe(a, b, p, zoom_a=0.6, zoom_b=0.32, cx=556.0, cy=640.0, r0=6.0, r1=1500.0):
    """a y b uint8. p 0..1: el logo avanza hacia la cámara y por su hueco aparece b."""
    p = clamp(p)
    R = r0 * (r1 / r0) ** p
    A = _radial(a, 1 + zoom_a * p ** 2.2, cx, cy, 0.16 * p ** 1.4) if a is not None else np.zeros((H, W, 3), np.float32)
    B = _radial(b, 1 + zoom_b * (1 - p) ** 1.6, cx, cy, 0.14 * (1 - p)) if b is not None else np.zeros((H, W, 3), np.float32)
    d = np.hypot(_XX - cx, _YY - cy)
    hole = np.clip(R - d + 0.5, 0, 1)[..., None]
    out = A * (1 - hole) + B * hole
    for mul, shade in ((0.90, 0.28), (0.94, 0.38), (0.97, 0.50), (1.0, 1.0)):   # volumen hacia el fondo
        lay = _logo_layer(R * mul, cx, cy, shade)
        out = out * (1 - lay[..., 3:4] / 255.0) + lay[..., :3]
    return out


def rgb_split(img, k):
    if k <= 0:
        return img
    out = img.copy()
    out[:, k:, 0] = img[:, :-k, 0]
    out[:, :-k, 2] = img[:, k:, 2]
    return out


# ------------------------------------------------------------------ subtítulos amarillos estilo cine
SUBS = [
    (0.00, 1.44, "Hola amigos, soy el Kaco López"),
    (1.44, 3.12, "y les tengo una *tremenda noticia*,"),
    (3.14, 4.74, "porque el|*lunes 9 de noviembre*"),
    (4.76, 6.50, "a eso de las *18 horas*,"),
    (6.54, 7.94, "arranca|*La Ciudad de la Furia*"),
    (7.98, 10.06, "por *Emerge FM 105.5*."),
    (10.72, 11.32, "Ya lo sabes,"),
    (11.34, 12.40, "desde acá, desde los estudios"),
    (12.40, 14.44, "de *Emerge FM 105.5*,"),
    (14.64, 15.96, "te espero el|*lunes 9 de noviembre*"),
    (15.98, 17.24, "a eso de las *6 de la tarde*,"),
    (17.46, 18.50, "porque haremos completamente"),
    (18.52, 19.38, "*en vivo*,"),
    (19.42, 21.30, "*La Ciudad de la Furia*."),
]
SUB_Y = 1470
SUB_YELLOW = (255, 214, 10)
F_SUB = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 60)
F_SUBB = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 64)
SUBIMG = {}


def build_subs():
    for i, (_, _, txt) in enumerate(SUBS):
        lines = []
        for raw in txt.split("|"):
            runs, bold = [], False
            for part in raw.split("*"):
                if part:
                    runs.append((part, bold))
                bold = not bold
            lines.append(runs)
        lh = 82
        widths = [sum((F_SUBB if b else F_SUB).getlength(s) for s, b in runs) for runs in lines]
        iw, ih = int(max(widths)) + 80, lh * len(lines) + 60
        assert iw <= W, txt
        txtl = Image.new("L", (iw, ih), 0)
        strk = Image.new("L", (iw, ih), 0)
        dt, dsk = ImageDraw.Draw(txtl), ImageDraw.Draw(strk)
        for j, runs in enumerate(lines):
            x = (iw - widths[j]) / 2
            for s, b in runs:
                f = F_SUBB if b else F_SUB
                yy = 30 + j * lh + lh / 2
                dt.text((x, yy), s, font=f, fill=255, anchor="lm")
                dsk.text((x, yy), s, font=f, fill=255, anchor="lm", stroke_width=5)
                x += f.getlength(s)
        shadow = strk.filter(ImageFilter.GaussianBlur(7))
        st, sk, sh = (np.asarray(a, np.float32) / 255.0 for a in (txtl, strk, shadow))
        a_bg = np.clip(sk + sh * 0.75 * (1 - sk), 0, 1)
        rgb = np.asarray(SUB_YELLOW, np.float32)[None, None] * st[..., None]
        alpha = st + a_bg * (1 - st)
        SUBIMG[i] = (np.dstack([rgb, alpha * 255.0]), iw, ih)


def draw_subs(ts, frame):
    for i, (t0, t1, _) in enumerate(SUBS):
        if t0 <= ts < t1:
            img, iw, ih = SUBIMG[i]
            op = clamp((ts - t0 + 1 / FPS) / 0.07) * clamp((t1 - ts) / 0.05)
            x0, y0 = (W - iw) // 2, SUB_Y - ih // 2
            reg = frame[y0:y0 + ih, x0:x0 + iw]
            reg *= 1 - img[..., 3:4] / 255.0 * op
            reg += img[..., :3] * op
            return


# ------------------------------------------------------------------ máscara de la persona
MATTE = None
_sess = None


def _load_matte():
    global MATTE
    parts = [os.path.join(HERE, f"matte_{k}.npy") for k in range(2)]
    if all(os.path.exists(p) for p in parts):
        MATTE = np.concatenate([np.load(p, mmap_mode="r") for p in parts])


def _infer_live(img1080):
    global _sess
    import onnxruntime as ort
    if _sess is None:
        _sess = ort.InferenceSession(os.path.expanduser("~/.u2net/u2net_human_seg.onnx"), providers=["CPUExecutionProvider"])
    mean = np.array([0.485, 0.456, 0.406], np.float32); std = np.array([0.229, 0.224, 0.225], np.float32)
    out = []
    for im in (img1080, img1080.crop((0, 0, 1080, 1200))):
        x = np.asarray(im.resize((320, 320), Image.LANCZOS), np.float32) / 255.0
        x = (x / max(x.max(), 1e-6) - mean) / std
        o = _sess.run(None, {"input.1": x.transpose(2, 0, 1)[None]})[0][0, 0]
        out.append(((o - o.min()) / (o.max() - o.min() + 1e-6) * 255).astype(np.uint8))
    return np.stack(out)


_FADE = np.clip((1100 - np.arange(1920) * 1.0) / 200.0, 0, 1)[::2, None][:600]


def coarse_matte(n, src_small=None):
    if MATTE is not None:
        i = n - N0
        acc = np.zeros((2, 320, 320), np.float32); wsum = 0
        for d, wgt in ((-1, 0.25), (0, 0.5), (1, 0.25)):
            j = min(max(i + d, 0), len(MATTE) - 1)
            if (j < CUT - N0) != (i < CUT - N0):      # no mezclar máscaras entre las dos tomas
                j = i
            acc += MATTE[j].astype(np.float32) * wgt; wsum += wgt
        m = (acc / wsum).astype(np.uint8)
    else:
        m = _infer_live(src_small)
    full = np.asarray(Image.fromarray(m[0]).resize((540, 960), Image.BICUBIC), np.float32) / 255.0
    top = np.asarray(Image.fromarray(m[1]).resize((540, 600), Image.BICUBIC), np.float32) / 255.0
    full[:600] = top * _FADE + full[:600] * (1 - _FADE)
    return full


def refine(coarse_out, luma):
    r, eps = 5, 1.2e-3
    I = luma[::2, ::2]
    f = lambda x: uniform_filter(x, 2 * r + 1, mode="nearest")
    mI, mp = f(I), f(coarse_out)
    a = (f(I * coarse_out) - mI * mp) / (f(I * I) - mI * mI + eps)
    b = mp - a * mI
    a, b = f(a), f(b)
    up = lambda x: np.asarray(Image.fromarray(x).resize((W, H), Image.BILINEAR))
    m = up(a) * luma + up(b)
    return np.clip((m - 0.30) / 0.52, 0, 1)


# ------------------------------------------------------------------ etalonaje
def _lut():
    x = np.arange(256, dtype=np.float32) / 255.0
    c = 0.5 + (x - 0.5) * 1.07
    c = np.clip(c, 0, 1) ** 1.03
    r = np.clip(c + 0.012 * x, 0, 1)
    b = np.clip(c + 0.018 * (1 - x) - 0.012 * x, 0, 1)
    return [np.clip(v * 255, 0, 255).astype(np.uint8) for v in (r, c, b)]


LUT = _lut()
VIGN = 1 - 0.20 * np.clip((((_XX - W / 2) / (W * 0.80)) ** 2 + ((_YY - H * 0.45) / (H * 0.72)) ** 2) - 0.25, 0, 1)
VIGN = VIGN[..., None].astype(np.float32)
# Cielo de la toma exterior: está quemado y el texto blanco no se leería sobre él.
_ky = np.clip(np.arange(H, dtype=np.float32) / 800.0, 0, 1)[:, None, None]
SKY_TINT = np.array([0.40, 0.56, 0.80], np.float32)[None, None] * (1 - _ky) + np.array([0.82, 0.88, 0.96], np.float32)[None, None] * _ky
SKY_Y = np.clip((1000 - np.arange(H, dtype=np.float32)) / 300.0, 0, 1)[:, None, None]


# ------------------------------------------------------------------ composición de un cuadro
def compose(n, src):
    ts = n / FPS
    bx = box_at(ts, shake=True)
    sw, sh = src.size
    frame = src.resize((W, H), Image.BICUBIC, box=(bx[0] * sw, bx[1] * sh, bx[2] * sw, bx[3] * sh), reducing_gap=2.0)
    small = None
    if MATTE is None:
        small = src if sw == W else src.resize((W, H), Image.BILINEAR, reducing_gap=1.5)
    cm = coarse_matte(n, small)
    cm = np.asarray(Image.fromarray(cm).resize((W // 2, H // 2), Image.BILINEAR,
                                               box=(bx[0] * 540, bx[1] * 960, bx[2] * 540, bx[3] * 960)))
    rgb = np.asarray(frame)
    rgb = np.dstack([LUT[c][rgb[..., c]] for c in range(3)]).astype(np.float32)
    luma = (rgb @ np.array([0.299, 0.587, 0.114], np.float32)) / 255.0
    alpha = refine(cm, luma)[..., None]

    bg = rgb * VIGN
    if n < CUT:
        m = np.clip((luma[..., None] - 0.68) / 0.18, 0, 1) * SKY_Y
        bg = bg * (1 - m * (1 - SKY_TINT))

    canvas = np.zeros((H, W, 4), np.float32)
    dim = draw_events(ts, canvas)
    if dim > 0:
        bg = bg * (1 - dim)
    bg = draw_rings(ts, bg)
    ga = canvas[..., 3]
    if ga.max() > 1:
        ys = np.where(ga.max(1) > 1)[0]; y0, y1 = max(ys[0] - 10, 0), min(ys[-1] + 120, H)
        sh_img = Image.fromarray(ga[y0:y1].astype(np.uint8)).filter(ImageFilter.GaussianBlur(16))
        shd = np.zeros((H, W), np.float32)
        s = np.asarray(sh_img, np.float32) / 255.0
        oy, ox = 30, 20
        shd[y0 + oy:y1, ox:] = s[:y1 - y0 - oy, :W - ox]
        bg = bg * (1 - 0.55 * shd[..., None])
        bg = canvas[..., :3] + bg * (1 - ga[..., None] / 255.0)
    out = rgb * alpha + bg * (1 - alpha)
    out = np.clip(out, 0, 255)
    k = int(round(9 * impact(ts)))
    if k:
        out = rgb_split(out, k)
    draw_subs(ts, out)
    return np.clip(out, 0, 255).astype(np.uint8)


HELD = {}


def held(n):
    """Último cuadro de la toma A / primero de la B, para superponerlas durante la transición."""
    if n not in HELD:
        HELD[n] = compose(n, grab(n))
    return HELD[n]


def final_frame(n, src):
    """Cuadro de salida: composición + transición central + apertura y cierre."""
    if CUT - TR <= n < CUT + TR:
        cur = compose(n, src)
        a = cur if n < CUT else held(CUT - 1)
        b = cur if n >= CUT else held(CUT)
        p = (n - (CUT - TR) + 1) / (2 * TR)
        out = logo_wipe(a, b, p)
        kk = int(round(12 * math.sin(math.pi * p) ** 2))
        out = rgb_split(np.clip(out, 0, 255), kk)
        return out.astype(np.uint8)
    cur = compose(n, src)
    if n < IRIS:
        p = 0.42 + 0.58 * (n + 1) / IRIS
        return np.clip(logo_wipe(None, cur, p, zoom_b=0.14), 0, 255).astype(np.uint8)
    if n >= N1 - IRIS:
        p = (n - (N1 - IRIS) + 1) / IRIS * 0.97 if False else (n - (N1 - IRIS) + 1) / IRIS
        return np.clip(logo_wipe(cur, None, p, zoom_a=0.25), 0, 255).astype(np.uint8)
    return cur


# ------------------------------------------------------------------ entrada / salida
def grab(n, size=(SW, SH)):
    ss = max(0, (n - 0.5) / FPS)
    cmd = [FF, "-hide_banner", "-loglevel", "error", "-ss", f"{ss:.5f}", "-i", SRC, "-frames:v", "1",
           "-vf", f"scale={size[0]}:{size[1]}:flags=bicubic", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]
    buf = subprocess.run(cmd, stdout=subprocess.PIPE).stdout
    return Image.frombuffer("RGB", size, buf)


def main():
    mode = sys.argv[1]
    build_tex(); build_subs(); build_iso(); _load_matte(); layout()
    if mode in ("sheet", "frames"):
        outs = []
        for t in sys.argv[2:]:
            n = int(round(float(t) * FPS)) if mode == "sheet" else int(t)
            t0 = time.time()
            img = final_frame(n, grab(n))
            print(t, "cuadro", n, "máscara", "completa" if MATTE is not None else "en vivo", round(time.time() - t0, 2), "s", flush=True)
            outs.append(Image.fromarray(img).resize((432, 768), Image.LANCZOS))
        cols = min(len(outs), 5 if mode == "sheet" else 6); rows = (len(outs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 432, rows * 768))
        for i, im in enumerate(outs):
            sheet.paste(im, ((i % cols) * 432, (i // cols) * 768))
        sheet.save(os.path.join(HERE, f"pv_{mode}.jpg"), quality=88)
        return
    if mode == "render":
        a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        dec = subprocess.Popen([FF, "-hide_banner", "-loglevel", "error", "-i", SRC, "-vf", f"select='between(n,{a},{b - 1})'",
                                "-fps_mode", "passthrough", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
                               stdout=subprocess.PIPE, bufsize=SW * SH * 3)
        enc = subprocess.Popen([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                                "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                                "-c:v", "h264_nvenc", "-preset", "p7", "-rc", "vbr", "-cq", "20", "-b:v", "12M", "-maxrate", "20M",
                                "-profile:v", "high", "-g", "30", "-bf", "2",
                                "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                                "-movflags", "+faststart", out], stdin=subprocess.PIPE)
        t0 = time.time()
        for n in range(a, b):
            buf = dec.stdout.read(SW * SH * 3)
            if len(buf) < SW * SH * 3:
                print("fin de la fuente en", n, flush=True); break
            enc.stdin.write(final_frame(n, Image.frombuffer("RGB", (SW, SH), buf)).tobytes())
            if (n - a) % 30 == 0:
                print(n - a, "/", b - a, round(time.time() - t0), "s", flush=True)
        enc.stdin.close(); enc.wait(); dec.kill()
        print("listo", out, round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
