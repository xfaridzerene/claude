# Extiende el fondo de la foto circular de Nicolás Larenas para dejarla cuadrada.
# El círculo (ajustado sobre los bordes) se conserva intacto; las esquinas se rellenan
# prolongando radialmente el borde del círculo y difuminándolo, con grano suave.
import os
import numpy as np
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
CX, CY, R = 561.35, 402.42, 385.74       # círculo medido en larenas_original.jpg
src = np.asarray(Image.open(os.path.join(AQUI, 'fuentes', 'larenas_original.jpg')).convert('RGB')).astype(np.float32)
H, W, _ = src.shape

lado = int(2 * R)
x0, y0 = CX - R, CY - R
yy, xx = np.mgrid[0:lado, 0:lado].astype(np.float32)
gx, gy = xx + x0, yy + y0
dx, dy = gx - CX, gy - CY
dist = np.sqrt(dx ** 2 + dy ** 2) + 1e-6

def muestra(px, py):
    px = np.clip(px, 0, W - 1); py = np.clip(py, 0, H - 1)
    x_, y_ = np.floor(px).astype(int), np.floor(py).astype(int)
    x1, y1 = np.minimum(x_ + 1, W - 1), np.minimum(y_ + 1, H - 1)
    fx, fy = (px - x_)[..., None], (py - y_)[..., None]
    return (src[y_, x_] * (1 - fx) * (1 - fy) + src[y_, x1] * fx * (1 - fy)
            + src[y1, x_] * (1 - fx) * fy + src[y1, x1] * fx * fy)

orig = muestra(gx, gy)
# borde: promedio de un anillo un poco hacia adentro (evita el antialias del círculo)
ext = np.zeros_like(orig)
for k, rr in enumerate((R - 8, R - 12, R - 16, R - 20)):
    ext += muestra(CX + dx / dist * rr, CY + dy / dist * rr)
ext /= 4
# difuminar la extensión, más mientras más lejos del círculo
e1 = np.asarray(Image.fromarray(ext.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))).astype(np.float32)
e2 = np.asarray(Image.fromarray(ext.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))).astype(np.float32)
lejos = np.clip((dist - R) / 120, 0, 1)[..., None]
relleno = e1 * (1 - lejos) + e2 * lejos
rng = np.random.default_rng(3)
relleno += rng.normal(0, 2.2, relleno.shape[:2])[..., None]
# mezcla: dentro del círculo la foto original, con un borde suave de 6 px
m = np.clip((R - 6 - dist) / 6, 0, 1)[..., None]
out = orig * m + relleno * (1 - m)
im = Image.fromarray(out.clip(0, 255).astype(np.uint8))
im.save(os.path.join(AQUI, 'fuentes', 'larenas.png'))
im.save(os.path.join(AQUI, '..', 'fotos', 'nicolas-larenas-agricultores-unidos.png'))
print('ok', im.size)
