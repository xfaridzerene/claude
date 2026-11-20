# -*- coding: utf-8 -*-
"""Reel «Emerge tu mañana» (Kaco presenta a Gabriel, estreno lunes 9 de noviembre) — compositor.

Un solo plano: Kaco habla, la cámara gira hacia Gabriel y él sigue. Se descarta la primera
toma fallida (0-2,3 s), el paneo se cubre con el paso a través del isotipo y el final se
congela antes de que se den vuelta, mientras termina la voz.

  python render_0226.py sheet 3.0 5.2 ...       -> pv_sheet.jpg (tiempos de la fuente)
  python render_0226.py frames 0 10 20 ...      -> pv_frames.jpg (cuadros de salida)
  python render_0226.py render <a> <b> <salida> -> video sin audio de los cuadros de salida [a, b)
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
SRC = r"E:\2 de nov\DJI_0226.MP4"
SFPS = 60000 / 1001                    # cuadros de la fuente
OFPS = 30000 / 1001                    # salida: un cuadro fuente de cada dos
FIRST, LAST = 138, 982                 # primer y último cuadro fuente usados (pares)
SRC_FRAMES = list(range(FIRST, LAST + 1, 2))
IDX = {n: i for i, n in enumerate(SRC_FRAMES)}
A_HOLD, B_HOLD = 592, 648              # el paneo entre ambos se reemplaza por la transición
T_A, T_B = A_HOLD / SFPS, B_HOLD / SFPS
FREEZE = 32                            # cuadros de congelado al final (≈1,07 s)
N_OUT = len(SRC_FRAMES) + FREEZE
T_END = LAST / SFPS + FREEZE / OFPS
SW, SH = 2160, 3840
BRAND = r"C:\Users\farid\Desktop\EMERGE FM\Nuevo branding"


def out_map(i):
    """cuadro de salida -> (cuadro fuente, tiempo de animación en segundos de la fuente)"""
    if i < len(SRC_FRAMES):
        n = SRC_FRAMES[i]
        return n, n / SFPS
    return LAST, LAST / SFPS + (i - len(SRC_FRAMES) + 1) / OFPS


# ------------------------------------------------------------------ zoom
ZOOM = [
    (0.00, 1.00, 1.04),
    (4.12, 1.08, 1.11),
    (5.56, 1.00, 1.03),
    (7.30, 1.06, 1.09),
    (8.22, 1.00, 1.02),
    (T_B, 1.00, 1.03),
    (11.66, 1.08, 1.10),
    (12.76, 1.00, 1.02),
    (13.88, 1.10, 1.12),
    (14.72, 1.16, 1.18),
    (15.30, 1.04, 1.06),
    (16.30, 1.00, 1.04),
    (99, 1, 1),
]
ANCHOR_A = (0.50, 0.35)                # Kaco
ANCHOR_B = (0.46, 0.37)                # Gabriel


def zoom_at(ts):
    for i in range(len(ZOOM) - 1):
        t0, a, b = ZOOM[i]; t1 = ZOOM[i + 1][0]
        if t0 <= ts < t1:
            return a + (b - a) * (ts - t0) / (min(t1, T_END) - t0)
    return 1.0


def box_at(ts, shake=False):
    z = zoom_at(ts)
    ax, ay = ANCHOR_A if ts < (T_A + T_B) / 2 else ANCHOR_B
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
VIOLETA, AZUL = (123, 97, 255), (0, 174, 239)


def build_tex():
    Wh, Vd, Am, Nj = g.BLANCO, g.VERDE, g.AMBAR, g.NARANJA
    vd_side, am_side, nj_side, vi_side, az_side = (0, 150, 112), (196, 122, 0), (196, 70, 24), (72, 50, 190), (0, 110, 160)
    TEX["novedad"] = g.text_tex([("¡OTRA TREMENDA", 86, Wh, am_side), ("NOVEDAD!", 168, Am, am_side)], depth=50, gap=0.22)
    TEX["fecha"] = g.text_tex([("LUNES 9", 158, Am, am_side), ("DE NOVIEMBRE", 88, Wh, am_side)], depth=50)
    TEX["hora"] = g.text_tex([("A LAS", 100, Wh, am_side, None, 0.22), ("10:00", 244, Am, am_side)], depth=58, gap=0.2)
    TEX["amigo"] = g.text_tex([("MI AMIGO", 100, Wh, vd_side), ("GABRIEL", 172, Vd, (0, 120, 90))], depth=50)
    TEX["nuevo"] = g.text_tex([("¡NUEVO", 140, Wh, nj_side), ("PROGRAMA!", 140, Nj, nj_side)], depth=50)
    TEX["tuman"] = g.text_tex([("EMERGE", 150, Wh, vi_side), ("TU MAÑANA", 128, Nj, nj_side)], depth=56)
    TEX["horario"] = g.text_tex([("DE", 96, Wh, am_side, None, 0.2), ("10 A 12", 176, Am, am_side)], depth=56, gap=0.18)
    TEX["emerge"] = g.text_tex([("EMERGE FM", 122, Wh, vd_side)], depth=46)
    TEX["iso"] = g.image_tex(_logo(), ISO_W, depth=56, side_mul=0.42)
    TEX["noticias"] = g.text_tex([("NOTICIAS", 176, Wh, az_side)], depth=50)
    TEX["musica"] = g.text_tex([("MÚSICA", 200, Vd, (0, 120, 90))], depth=52)
    TEX["onda"] = g.text_tex([("PURA", 110, Wh, vi_side, None, 0.2), ("BUENA ONDA", 132, Am, am_side)], depth=50)
    TEX["final"] = g.text_tex([("EMERGE", 140, Wh, vi_side), ("TU MAÑANA", 120, Nj, nj_side),
                               ("LUNES 9 · 10:00", 66, Am, am_side, None, 0.08)], depth=54, gap=0.2)


# textura, entra, sale, solape con la cabeza (px), giro base Y, atenúa fondo, estilo (tiempos de la fuente)
EVENTS = [
    ("novedad", 2.46, 4.08, 36, 9, 0.30, "slam"),
    ("fecha", 4.40, 5.54, 30, -9, 0.30, "rise"),
    ("hora", 5.80, 6.98, 85, -8, 0.30, "slam"),
    ("amigo", 7.40, 8.20, 36, -9, 0.30, "rise"),
    ("nuevo", 8.24, 9.40, 36, 9, 0.30, "slam"),
    ("tuman", 10.86, 11.64, 40, 8, 0.45, "slam"),
    ("horario", 11.68, 12.74, 70, -8, 0.30, "slam"),
    ("iso", 12.78, 13.84, 0, 10, 0.45, "spin"),
    ("emerge", 12.88, 13.84, 0, 8, 0.45, "rise"),
    ("noticias", 13.88, 14.70, 40, 8, 0.25, "slam"),
    ("musica", 14.72, 15.28, 50, -8, 0.25, "slam"),
    ("onda", 15.30, 16.28, 36, 9, 0.30, "slam"),
    ("final", 16.30, 99.0, 30, -8, 0.50, "slam"),
]
RING_COLOR = {"hora": g.AMBAR, "fecha": g.AMBAR, "novedad": g.AMBAR, "horario": g.AMBAR, "onda": g.AMBAR,
              "nuevo": g.NARANJA, "tuman": VIOLETA, "final": VIOLETA, "noticias": AZUL}
POS, HEAD = [], []
T_IN, T_OUT = 0.34, 0.18
HITS = [(e[1] + 0.6 * T_IN, i) for i, e in enumerate(EVENTS) if e[6] in ("slam", "spin")]


def impact(ts):
    a = 0.0
    for t, _ in HITS:
        if t <= ts < t + 0.5:
            a = max(a, math.exp(-(ts - t) / 0.09))
    return a


BAND = (int(320 * 0.18), int(320 * 0.80))     # columnas donde buscar la cabeza (evita bordes y manos)


def head_track():
    top = np.full(len(SRC_FRAMES), 480.0); cx = np.full(len(SRC_FRAMES), 540.0)
    if MATTE is not None:
        for i in range(len(MATTE)):
            m = MATTE[i, 1][:, BAND[0]:BAND[1]] > 140
            rows = np.where(m.sum(1) > 6)[0]
            if len(rows):
                r = rows[0]
                cols = np.where(m[r + 12:r + 45].any(0))[0] + BAND[0]
                top[i] = r * 1200 / 320
                if len(cols):
                    cx[i] = (cols[0] + cols[-1]) / 2 * 1080 / 320
    for i, n in enumerate(SRC_FRAMES):
        bx = box_at(n / SFPS)
        top[i] = (top[i] / H - bx[1]) / (bx[3] - bx[1]) * H
        cx[i] = (cx[i] / W - bx[0]) / (bx[2] - bx[0]) * W
    return top, cx


def layout():
    top, cx = head_track()
    times = np.array(SRC_FRAMES) / SFPS
    for name, t0, t1, ov, *_ in EVENTS:
        sel = (times >= t0) & (times < t1)
        if not sel.any():
            sel = np.abs(times - t0) == np.abs(times - t0).min()
        ht, hx = float(np.median(top[sel])), float(np.median(cx[sel]))
        HEAD.append((hx, ht + 195))
        if name == "iso":
            POS.append((hx, ht + 195))
        elif name == "emerge":
            POS.append((540, max(150, ht + 195 - ISO_W / 2 - 62)))
        else:
            y = ht + ov - (TEX[name].h / 2 - TEX[name].pad)
            POS.append((540, max(TEX[name].h / 2 + 20, y)))


#@@

# ------------------------------------------------------------------ ondas de señal detrás de la persona
_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)
DUR_RING = 0.5
RING_Y = np.clip((1500 - np.arange(H, dtype=np.float32)) / 300.0, 0, 1)[:, None, None]
DIM_Y = np.clip((1350 - np.arange(H, dtype=np.float32)) / 400.0, 0, 1)[:, None, None]


#@@
# ------------------------------------------------------------------ subtítulos amarillos estilo cine
SUBS = [
    (2.40, 4.10, "Les tengo otra *tremenda novedad*,"),
    (4.12, 5.55, "porque el *lunes 9 de noviembre*|también,"),
    (5.56, 6.96, "a eso de las *10 de la mañana*,"),
    (7.30, 8.20, "arranca mi amigo *Gabriel*"),
    (8.22, 9.28, "con su *nuevo programa*."),
    (9.30, 10.62, "¡Ven, po', Gabriel! Vamos."),
    (10.88, 11.64, "*Emerge tu mañana*"),
    (11.66, 12.74, "de *10 a 12*,"),
    (12.76, 13.88, "donde los voy a acompañar"),
    (13.88, 15.10, "con *noticias, música*"),
    (15.10, 16.30, "y *pura buena onda*."),
    (16.32, 99.0, "¡Eso! Vamos, Gabriel,|vamos, vamos."),
]
SUB_Y = 1470
SUB_YELLOW = (255, 214, 10)
F_SUB = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 60)
F_SUBB = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 64)
SUBIMG = {}


#@@
# ------------------------------------------------------------------ máscara de la persona
MATTE = None
_sess = None


def _load_matte():
    global MATTE
    parts = [os.path.join(HERE, f"matte_{k}.npy") for k in range(2)]
    if all(os.path.exists(p) for p in parts):
        MATTE = np.concatenate([np.load(p, mmap_mode="r") for p in parts])
        assert len(MATTE) == len(SRC_FRAMES), len(MATTE)


#@@
# ------------------------------------------------------------------ etalonaje
@@LUT@@# Cielo nublado y quemado: se baja a un azul suave para que el texto blanco se lea.
_ky = np.clip(np.arange(H, dtype=np.float32) / 800.0, 0, 1)[:, None, None]
SKY_TINT = np.array([0.42, 0.56, 0.78], np.float32)[None, None] * (1 - _ky) + np.array([0.82, 0.88, 0.96], np.float32)[None, None] * _ky
SKY_Y = np.clip((1000 - np.arange(H, dtype=np.float32)) / 300.0, 0, 1)[:, None, None]


# ------------------------------------------------------------------ composición de un cuadro
def compose(n, src, ts, extra_zoom=1.0):
    """n: cuadro fuente; ts: tiempo de animación (en el congelado avanza aunque n no cambie)."""
    bx = box_at(ts, shake=True)
    if extra_zoom != 1.0:
        cxb, cyb = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2 - 0.05 * (bx[3] - bx[1])
        hw, hh = (bx[2] - bx[0]) / 2 / extra_zoom, (bx[3] - bx[1]) / 2 / extra_zoom
        bx = (cxb - hw, cyb - hh, cxb + hw, cyb + hh)
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
    m = np.clip((luma[..., None] - 0.68) / 0.18, 0, 1) * SKY_Y
    bg = bg * (1 - m * (1 - SKY_TINT))

    canvas = np.zeros((H, W, 4), np.float32)
    dim = draw_events(ts, canvas)
    if dim > 0:
        bg = bg * (1 - dim * DIM_Y)
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
TR_I0 = IDX[A_HOLD]                    # cuadros de salida que ocupa la transición [TR_I0, TR_I1)
TR_I1 = IDX[B_HOLD]
IRIS_IN, IRIS_OUT = 9, 11


def held(n):
    if n not in HELD:
        HELD[n] = compose(n, grab(n), n / SFPS)
    return HELD[n]


def final_frame(i, src):
    """src: PIL del cuadro fuente de out_map(i) (el último real durante el congelado)."""
    n, ts = out_map(i)
    if TR_I0 <= i < TR_I1:
        a, b = held(A_HOLD), held(B_HOLD)
        p = (i - TR_I0 + 1) / (TR_I1 - TR_I0)
        out = logo_wipe(a, b, p ** 1.15, cx=540.0, cy=700.0)
        kk = int(round(12 * math.sin(math.pi * p) ** 2))
        return rgb_split(np.clip(out, 0, 255), kk).astype(np.uint8)
    ez = 1.0
    if i >= len(SRC_FRAMES):                       # congelado: sigue acercándose lento
        ez = 1.0 + 0.07 * ease_out((i - len(SRC_FRAMES) + 1) / FREEZE)
    cur = compose(n, src, ts, ez)
    if i < IRIS_IN:
        p = 0.42 + 0.58 * (i + 1) / IRIS_IN
        return np.clip(logo_wipe(None, cur, p, zoom_b=0.14), 0, 255).astype(np.uint8)
    if i >= N_OUT - IRIS_OUT:
        p = (i - (N_OUT - IRIS_OUT) + 1) / IRIS_OUT
        return np.clip(logo_wipe(cur, None, p, zoom_a=0.25), 0, 255).astype(np.uint8)
    return cur


# ------------------------------------------------------------------ entrada / salida
def grab(n, size=(SW, SH)):
    ss = max(0, (n - 0.5) / SFPS)
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
            if mode == "sheet":
                n_want = int(round(float(t) * SFPS))
                i = min(range(len(SRC_FRAMES)), key=lambda j: abs(SRC_FRAMES[j] - n_want))
            else:
                i = int(t)
            t0 = time.time()
            img = final_frame(i, grab(out_map(i)[0]))
            print(t, "salida", i, "fuente", out_map(i)[0], "máscara", "completa" if MATTE is not None else "en vivo",
                  round(time.time() - t0, 2), "s", flush=True)
            outs.append(Image.fromarray(img).resize((432, 768), Image.LANCZOS))
        cols = min(len(outs), 5 if mode == "sheet" else 6); rows = (len(outs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 432, rows * 768))
        for k, im in enumerate(outs):
            sheet.paste(im, ((k % cols) * 432, (k // cols) * 768))
        sheet.save(os.path.join(HERE, f"pv_{mode}.jpg"), quality=88)
        return
    if mode == "render":
        a, b, out = int(sys.argv[2]), min(int(sys.argv[3]), N_OUT), sys.argv[4]
        real = [SRC_FRAMES[i] for i in range(a, min(b, len(SRC_FRAMES)))]
        dec = None
        if real:
            dec = subprocess.Popen([FF, "-hide_banner", "-loglevel", "error", "-i", SRC,
                                    "-vf", f"select='not(mod(n,2))*between(n,{real[0]},{real[-1]})'",
                                    "-fps_mode", "passthrough", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
                                   stdout=subprocess.PIPE, bufsize=SW * SH * 3)
        enc = subprocess.Popen([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", "30000/1001", "-i", "-",
                                "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                                "-c:v", "h264_nvenc", "-preset", "p7", "-rc", "vbr", "-cq", "20", "-b:v", "12M", "-maxrate", "20M",
                                "-profile:v", "high", "-g", "30", "-bf", "2",
                                "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                                "-movflags", "+faststart", out], stdin=subprocess.PIPE)
        t0 = time.time(); cur = None; frozen = None
        for i in range(a, b):
            if i < len(SRC_FRAMES):
                buf = dec.stdout.read(SW * SH * 3)
                if len(buf) < SW * SH * 3:
                    print("fin de la fuente en", i, flush=True); break
                cur = Image.frombuffer("RGB", (SW, SH), buf)
            else:
                if frozen is None:
                    frozen = grab(LAST)
                cur = frozen
            enc.stdin.write(final_frame(i, cur).tobytes())
            if (i - a) % 30 == 0:
                print(i - a, "/", b - a, round(time.time() - t0), "s", flush=True)
        enc.stdin.close(); enc.wait()
        if dec:
            dec.kill()
        print("listo", out, round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
