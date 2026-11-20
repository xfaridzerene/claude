# -*- coding: utf-8 -*-
"""Reel «La Ciudad de la Furia» — compositor.

  python render.py preview 8.4 10.2 ...   -> work/pv_<t>.jpg (un cuadro por tiempo fuente)
  python render.py sheet 8.4 10.2 ...     -> work/pv_sheet.jpg (hoja de contactos)
  python render.py render                 -> work/video.mp4 (sin audio) ; luego mux.sh
"""
import os, sys, math, subprocess, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import uniform_filter
import gfx3d as g
from gfx3d import W, H, clamp, ease_out, ease_in, back_out

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
FF = r"C:\Users\farid\AppData\Local\CapCut\Apps\9.5.0.4050\ffmpeg.exe"
SRC = r"E:\GRABACIONES 22-09\DJI_0212.MP4"
FPS = 60000 / 1001
N0, N1 = 108, 1464                     # cuadros fuente con máscara [N0, N1); el corte final usa los primeros 1322
SW, SH = 2160, 3840                    # fuente ya rotada
BRAND = r"C:\Users\farid\Desktop\EMERGE FM\Nuevo branding"
LOGO_PROG = r"C:\Users\farid\Desktop\claude code\furia-promo\src\logo-programa.png"

# ------------------------------------------------------------------ zoom
# (t_inicio, zoom_inicio, zoom_fin): cortes "punch-in" al empezar cada frase
ZOOM = [
    (0.00, 1.00, 1.05),
    (4.74, 1.11, 1.14),
    (7.02, 1.00, 1.03),
    (9.50, 1.03, 1.06),
    (10.84, 1.10, 1.12),
    (12.66, 1.17, 1.20),
    (15.72, 1.00, 1.03),
    (19.00, 1.06, 1.08),
    (20.80, 1.00, 1.02),
    (22.24, 1.02, 1.10),
    (99, 1, 1),
]
AX, AY = 0.56, 0.40                    # punto fijo del zoom (la cara)


def zoom_at(ts):
    for i in range(len(ZOOM) - 1):
        t0, a, b = ZOOM[i]; t1 = ZOOM[i + 1][0]
        if t0 <= ts < t1:
            k = (ts - t0) / (min(t1, N1 / FPS) - t0)
            return a + (b - a) * k
    return 1.0


def box_at(ts):
    z = zoom_at(ts)
    return (AX * (1 - 1 / z), AY * (1 - 1 / z), AX * (1 - 1 / z) + 1 / z, AY * (1 - 1 / z) + 1 / z)


# ------------------------------------------------------------------ gráficos 3D detrás de la persona
def _logo():
    return Image.open(os.path.join(BRAND, "emerge-fm-logo-color-transparent.png"))


TEX = {}


def build_tex():
    Wh, Vd, Am, Nj = g.BLANCO, g.VERDE, g.AMBAR, g.NARANJA
    vd_side, am_side, nj_side = (0, 150, 112), (196, 122, 0), (214, 62, 16)
    TEX["nombre"] = g.text_tex([("KACO", 150, Wh, vd_side), ("LÓPEZ", 150, Vd, (0, 120, 90))], depth=46)
    TEX["noticia"] = g.text_tex([("¡TREMENDA", 112, Wh, am_side), ("NOTICIA!", 138, Am, am_side)], depth=46)
    TEX["fecha"] = g.text_tex([("LUNES 19", 150, Am, am_side), ("DE OCTUBRE", 104, Wh, am_side)], depth=50)
    TEX["hora"] = g.text_tex([("A LAS", 100, Wh, am_side, None, 0.22), ("18:00", 244, Am, am_side)], depth=58, gap=0.2)
    TEX["vivo"] = g.text_tex([("EN VIVO", 168, Wh, (190, 24, 18))], depth=50)
    TEX["natural"] = g.text_tex([("100%", 230, Vd, (0, 120, 90)), ("NATURAL", 132, Wh, vd_side)], depth=50)
    TEX["emerge"] = g.text_tex([("EMERGE FM", 122, Wh, vd_side)], depth=46)
    TEX["dial"] = g.text_tex([("105.5", 270, Vd, (0, 118, 88))], depth=74)
    TEX["dialfm"] = g.text_tex([("FM", 112, Wh, vd_side, None, 0.3), ("105.5", 270, Vd, (0, 118, 88))], depth=74, gap=0.2)
    TEX["iso"] = g.image_tex(_logo(), ISO_W, depth=56, side_mul=0.42)
    TEX["furia"] = g.image_tex(Image.open(LOGO_PROG), 960, depth=62, side_tint=nj_side)


# textura, entra, sale, solape con la cabeza (px), giro base Y, atenúa fondo, estilo
# La posición se calcula sola: el borde inferior del texto queda `solape` px por debajo
# del punto más alto de la cabeza durante ese tramo, así siempre lo tapa un poco.
EVENTS = [
    ("nombre", 2.74, 3.86, 36, -10, 0.0, "rise"),
    ("noticia", 3.92, 4.74, 36, 9, 0.0, "slam"),
    ("fecha", 5.30, 7.02, 26, -9, 0.25, "rise"),
    ("iso", 7.04, 8.16, 0, 10, 0.45, "spin"),
    ("emerge", 7.36, 8.16, 0, 8, 0.45, "rise"),
    ("dial", 8.10, 9.48, 95, -9, 0.45, "slam"),
    ("furia", 9.50, 10.86, 58, 8, 0.50, "slam"),
    ("hora", 11.10, 12.62, 85, -8, 0.25, "rise"),
    ("vivo", 12.92, 14.26, 48, 8, 0.20, "slam"),
    ("natural", 14.34, 15.70, 40, -8, 0.20, "slam"),
    ("fecha", 16.46, 18.08, 26, 9, 0.25, "rise"),
    ("hora", 18.08, 19.00, 85, -8, 0.25, "slam"),
    ("dialfm", 19.00, 20.82, 95, 9, 0.45, "slam"),
    ("iso", 20.78, 22.26, 0, -10, 0.45, "spin"),
    ("emerge", 20.96, 22.26, 0, -8, 0.45, "rise"),
    ("furia", 22.22, 99.0, 62, -8, 0.50, "slam"),
]
ISO_W = 800                              # ancho del isotipo en pantalla
POS = []                                 # centro (x, y) de cada evento


def head_track():
    """Punto más alto y centro de la cabeza por cuadro, en coordenadas de salida."""
    top = np.full(N1 - N0, 465.0); cx = np.full(N1 - N0, 600.0)
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
        if name == "iso":
            POS.append((hx, ht + 195))
        elif name == "emerge":
            ring_top = ht + 195 - ISO_W / 2
            POS.append((540, max(150, ring_top - 62)))
        else:
            y = ht + ov - (TEX[name].h / 2 - TEX[name].pad)
            POS.append((540, max(TEX[name].h / 2 + 30, y)))


T_IN, T_OUT = 0.34, 0.18


def draw_events(ts, canvas):
    """Dibuja los elementos activos en el lienzo premultiplicado; devuelve la atenuación de fondo."""
    dim = 0.0
    for (name, t0, t1, _ov, ry0, dm, style), (x, y) in zip(EVENTS, POS):
        if not (t0 <= ts < t1 + T_OUT):
            continue
        u = (ts - t0) / T_IN                      # entrada 0..1
        v = (ts - t1) / T_OUT                     # salida 0..1 (negativo = aún en pantalla)
        e = back_out(u, 1.6)
        sway = math.sin((ts - t0) * 1.9)          # vaivén lento para que se note el volumen
        ry = ry0 + 5.0 * sway
        rx = 5.0 + 2.5 * math.sin((ts - t0) * 1.3 + 1)
        rz = 0.0
        z = 0.0; dy = 0.0; op = clamp(u * 3.0); sc = 1.0
        if style == "rise":                       # emerge desde detrás de los hombros
            dy = (1 - e) * 420; ry += (1 - ease_out(u)) * -30 * math.copysign(1, ry0)
        elif style == "slam":                     # viene desde el fondo y frena
            z = (1 - e) * 1500; ry += (1 - ease_out(u)) * 38 * math.copysign(1, ry0)
        elif style == "spin":                     # el isotipo entra girando como moneda
            z = (1 - e) * 900; ry += (1 - ease_out(u)) * 115 * math.copysign(1, ry0)
            rz = 0.0
        if v > 0:                                 # salida: se hunde hacia el fondo
            k = ease_in(v)
            z += k * 1400; op *= 1 - clamp(v) ** 1.5; dy += k * 60
        g.merge(canvas, g.draw(TEX[name], (x, y + dy, z), (rx, ry, rz), sc, op))
        dim = max(dim, dm * clamp(u * 2.0) * (1 - clamp(v)))
    return dim


# ------------------------------------------------------------------ subtítulos amarillos estilo cine
SUBS = [
    (2.00, 3.42, "Hola amigos, soy Kaco López"),
    (3.42, 4.74, "y les tengo una *tremenda noticia*"),
    (4.74, 7.00, "porque el próximo|*lunes 19 de octubre*"),
    (7.02, 9.46, "arranca por|*Emerge FM 105.5*"),
    (9.50, 10.84, "*La Ciudad de la Furia*"),
    (10.84, 12.62, "a eso de las *6 de la tarde*,"),
    (12.66, 13.84, "completamente *en vivo*,|en directo,"),
    (13.84, 15.66, "en espontáneo|y *100% natural*."),
    (15.72, 16.46, "Ya lo sabes:"),
    (16.50, 18.08, "*lunes 19 de octubre*,"),
    (18.10, 18.98, "*6 de la tarde*,"),
    (19.00, 20.78, "*105.5 FM*,"),
    (20.80, 21.60, "*Emerge FM*,"),
    (21.60, 22.24, "arranca"),
    (22.26, 24.10, "*La Ciudad de la Furia*."),
]
SUB_Y = 1470                            # centro del bloque (zona segura de Reels / TikTok)
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
        txtl = Image.new("L", (iw, ih), 0)      # relleno
        strk = Image.new("L", (iw, ih), 0)      # contorno
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
        a_bg = np.clip(sk + sh * 0.75 * (1 - sk), 0, 1)          # negro: contorno + sombra
        rgb = np.asarray(SUB_YELLOW, np.float32)[None, None] * st[..., None]   # premultiplicado
        alpha = st + a_bg * (1 - st)
        SUBIMG[i] = (np.dstack([rgb, alpha * 255.0]), iw, ih)


def draw_subs(ts, frame):
    for i, (t0, t1, _) in enumerate(SUBS):
        if t0 <= ts < t1:
            img, iw, ih = SUBIMG[i]
            op = clamp((ts - t0) / 0.06) * clamp((t1 - ts) / 0.05)
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
    parts = [os.path.join(WORK, f"matte_{k}.npy") for k in range(2)]
    if all(os.path.exists(p) for p in parts):
        MATTE = np.concatenate([np.load(p, mmap_mode="r") for p in parts])


def _infer_live(img1080):
    """Respaldo para vistas previas mientras no exista la máscara completa."""
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


_FADE = np.clip((1100 - np.arange(1920) * 1.0) / 200.0, 0, 1)[::2, None][:600]   # a media resolución


def coarse_matte(n, src_small=None):
    """Máscara gruesa del cuadro fuente n, 540x960 float 0..1, suavizada en el tiempo."""
    if MATTE is not None:
        i = n - N0
        acc = np.zeros((2, 320, 320), np.float32); wsum = 0
        for d, wgt in ((-1, 0.25), (0, 0.5), (1, 0.25)):
            j = min(max(i + d, 0), len(MATTE) - 1)
            acc += MATTE[j].astype(np.float32) * wgt; wsum += wgt
        m = (acc / wsum).astype(np.uint8)
    else:
        m = _infer_live(src_small)
    full = np.asarray(Image.fromarray(m[0]).resize((540, 960), Image.BICUBIC), np.float32) / 255.0
    top = np.asarray(Image.fromarray(m[1]).resize((540, 600), Image.BICUBIC), np.float32) / 255.0
    full[:600] = top * _FADE + full[:600] * (1 - _FADE)
    return full


def refine(coarse_out, luma):
    """Filtro guiado rápido: ajusta la máscara gruesa a los bordes reales de la imagen."""
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
    c = 0.5 + (x - 0.5) * 1.07                                # un poco más de contraste
    c = np.clip(c, 0, 1) ** 1.03
    r = np.clip(c + 0.012 * x, 0, 1)                          # altas luces cálidas
    b = np.clip(c + 0.018 * (1 - x) - 0.012 * x, 0, 1)        # sombras frías
    return [np.clip(v * 255, 0, 255).astype(np.uint8) for v in (r, c, b)]


LUT = _lut()
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = 1 - 0.20 * np.clip((((_xx - W / 2) / (W * 0.80)) ** 2 + ((_yy - H * 0.45) / (H * 0.72)) ** 2) - 0.25, 0, 1)
VIGN = VIGN[..., None].astype(np.float32)


# ------------------------------------------------------------------ composición de un cuadro
def compose(n, src):
    """n: cuadro fuente; src: PIL RGB de la fuente (cualquier resolución 9:16). -> uint8 HxWx3"""
    ts = n / FPS
    bx = box_at(ts)
    sw, sh = src.size
    frame = src.resize((W, H), Image.BICUBIC, box=(bx[0] * sw, bx[1] * sh, bx[2] * sw, bx[3] * sh), reducing_gap=2.0)
    small = src if sw == W else src.resize((W, H), Image.BILINEAR, reducing_gap=1.5)
    cm = coarse_matte(n, small if MATTE is None else None)
    cm = np.asarray(Image.fromarray(cm).resize((W // 2, H // 2), Image.BILINEAR,
                                               box=(bx[0] * 540, bx[1] * 960, bx[2] * 540, bx[3] * 960)))
    rgb = np.asarray(frame)
    rgb = np.dstack([LUT[c][rgb[..., c]] for c in range(3)]).astype(np.float32)
    luma = (rgb @ np.array([0.299, 0.587, 0.114], np.float32)) / 255.0
    alpha = refine(cm, luma)[..., None]

    canvas = np.zeros((H, W, 4), np.float32)
    dim = draw_events(ts, canvas)
    bg = rgb * VIGN
    ga = canvas[..., 3]
    if ga.max() > 1:
        ys = np.where(ga.max(1) > 1)[0]; y0, y1 = max(ys[0] - 10, 0), min(ys[-1] + 120, H)
        # sombra de los volúmenes sobre el fondo
        sh_img = Image.fromarray(ga[y0:y1].astype(np.uint8)).filter(ImageFilter.GaussianBlur(16))
        shd = np.zeros((H, W), np.float32)
        s = np.asarray(sh_img, np.float32) / 255.0
        oy, ox = 30, 20
        shd[y0 + oy:y1, ox:] = s[:y1 - y0 - oy, :W - ox]
        bg = bg * (1 - dim) * (1 - 0.55 * shd[..., None])
        bg = canvas[..., :3] + bg * (1 - ga[..., None] / 255.0)
    elif dim > 0:
        bg = bg * (1 - dim)
    out = rgb * alpha + bg * (1 - alpha)
    draw_subs(ts, out)
    return np.clip(out, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ entrada / salida
def grab(n, size=(SW, SH)):
    ss = max(0, (n - 0.5) / FPS)
    cmd = [FF, "-hide_banner", "-loglevel", "error", "-ss", f"{ss:.5f}", "-i", SRC, "-frames:v", "1",
           "-vf", f"scale={size[0]}:{size[1]}:flags=bicubic", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]
    buf = subprocess.run(cmd, stdout=subprocess.PIPE).stdout
    return Image.frombuffer("RGB", size, buf)


def main():
    mode = sys.argv[1]
    build_tex(); build_subs(); _load_matte(); layout()
    if mode in ("preview", "sheet"):
        outs = []
        for t in sys.argv[2:]:
            n = int(round(float(t) * FPS)); t0 = time.time()
            img = compose(n, grab(n))
            print(t, "frame", n, "matte", "full" if MATTE is not None else "live", round(time.time() - t0, 2), "s", flush=True)
            if mode == "preview":
                Image.fromarray(img).save(os.path.join(WORK, f"pv_{t}.jpg"), quality=90)
            outs.append(Image.fromarray(img).resize((432, 768), Image.LANCZOS))
        if mode == "sheet":
            cols = min(len(outs), 5); rows = (len(outs) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * 432, rows * 768))
            for i, im in enumerate(outs):
                sheet.paste(im, ((i % cols) * 432, (i // cols) * 768))
            sheet.save(os.path.join(WORK, "pv_sheet.jpg"), quality=88)
        return
    if mode == "render":
        a = int(sys.argv[2]) if len(sys.argv) > 2 else N0
        b = int(sys.argv[3]) if len(sys.argv) > 3 else N1
        out = sys.argv[4] if len(sys.argv) > 4 else os.path.join(WORK, "video.mp4")
        dec = subprocess.Popen([FF, "-hide_banner", "-loglevel", "error", "-i", SRC, "-vf", f"select='between(n,{a},{b - 1})'",
                                "-fps_mode", "passthrough", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
                               stdout=subprocess.PIPE, bufsize=SW * SH * 3)
        enc = subprocess.Popen([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", "60000/1001", "-i", "-",
                                "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                                "-c:v", "h264_nvenc", "-preset", "p7", "-rc", "vbr", "-cq", "20", "-b:v", "12M", "-maxrate", "20M",
                                "-profile:v", "high", "-g", "60", "-bf", "2",
                                "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                                "-movflags", "+faststart", out], stdin=subprocess.PIPE)
        t0 = time.time()
        for n in range(a, b):
            buf = dec.stdout.read(SW * SH * 3)
            if len(buf) < SW * SH * 3:
                print("fin de la fuente en", n, flush=True); break
            enc.stdin.write(compose(n, Image.frombuffer("RGB", (SW, SH), buf)).tobytes())
            if (n - a) % 60 == 0:
                print(n - a, "/", b - a, round(time.time() - t0), "s", flush=True)
        enc.stdin.close(); enc.wait(); dec.kill()
        print("listo", out, round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()

