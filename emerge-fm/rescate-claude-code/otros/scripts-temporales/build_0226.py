# Arma render_0226.py reutilizando bloques de nov9/render_nov9.py
import sys
BASE = r"C:\Users\farid\Desktop\claude code\reel-furia"
src = open(BASE + r"\nov9\render_nov9.py", encoding="utf-8").read()


def between(a, b):
    i = src.index(a); j = src.index(b, i); return src[i:j]


draw_ev = between("def draw_events(ts, canvas):", "# ------------------------------------------------------------------ ondas")
rings_wipe = between("def draw_rings(ts, bg):", "# ------------------------------------------------------------------ subtítulos")
subs_code = between("def build_subs():", "# ------------------------------------------------------------------ máscara")
matte_code = between("def _infer_live(img1080):", "# ------------------------------------------------------------------ etalonaje")
lut_code = between("def _lut():", "# Cielo de la toma exterior")

rings_wipe = rings_wipe.replace("(RING_Y_A if ts < T_CUT else RING_Y_B)", "RING_Y")
old = """        i = n - N0
        acc"""
assert old in matte_code
matte_code = matte_code.replace(old, """        i = IDX[n]
        acc""")
old = """            if (j < CUT - N0) != (i < CUT - N0):      # no mezclar máscaras entre las dos tomas
                j = i
"""
assert old in matte_code
matte_code = matte_code.replace(old, "")
assert "1 / FPS" in subs_code
subs_code = subs_code.replace("1 / FPS", "1 / OFPS")

parts = open(BASE + r"\nov2-0226\_partes.py", encoding="utf-8").read().split("#@@\n")
head, mid, subs, matte_hdr, tail = parts
code = head + draw_ev + mid + rings_wipe + subs + subs_code + matte_hdr + matte_code + tail.replace("@@LUT@@", lut_code)
open(BASE + r"\nov2-0226\render_0226.py", "w", encoding="utf-8").write(code)
print("ok", len(code))
