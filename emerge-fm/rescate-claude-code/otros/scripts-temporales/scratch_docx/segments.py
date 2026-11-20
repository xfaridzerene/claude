# -*- coding: utf-8 -*-
import subprocess, os

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
SRC = r"C:\Users\farid\scratch_docx\audio\master.mp3"
OUT_ROOT = r"E:\EMERGE FM 1\FRASES"

frases = [
    "Estás escuchando Emerge FM, ciento cinco punto cinco… Lo que suena, emerge.",
    "En el auto, en la pega o en la casa… tu radio es Emerge FM… 105.5.",
    "Donde estés, súbele… 105.5, Emerge FM.",
    "Escúchanos también en streaming… Emerge FM se escucha y también se ve.",
    "Síguenos en Facebook, búscanos como… Radio Emerge FM Rancagua.",
    "Síguenos en Instagram, búscanos como… arroba Radio Emerge FM.",
    "Síguenos también en YouTube… búscanos como Emerge FM.",
    "¿Te perdiste el programa? Revívelo en nuestro canal de YouTube. Emerge FM: se escucha, se ve.",
    "Llévanos contigo… Escúchanos en línea en www.emergefm.cl. Emerge FM, 105.5.",
    "Los ochenta y los noventa nunca se fueron: suenan en el 105.5. Emerge FM.",
    "Las canciones que te sabes de memoria. Emerge FM, 105.5. Lo que suena, emerge.",
    "Escucha esos clásicos que no pasan de moda. Emerge FM, 105.5.",
    "Música, noticias y programas en vivo, todos los días. Emerge FM, 105.5. Lo que suena, emerge.",
    "Gracias por estar al otro lado. Seguimos juntos en Emerge FM, 105.5.",
    "El tiempo avanza... Pero la música no se detiene… Una pausa y luego más... Emerge FM.",
    "La espera valió la pena...sigues escuchando... Emerge FM, siempre en el 105.5.",
    "Cada mañana te acompañamos donde estés...105.5 Emerge FM.",
    "En la casa o en el trabajo...donde estés… Siempre Emerge FM.",
]

# (start, end) in seconds for toma1 and toma2, per frase index 1..18
toma1 = [
    (29.33, 38.94), (38.94, 48.39), (48.39, 56.45), (56.45, 64.66),
    (64.66, 72.09), (72.09, 79.97), (79.97, 87.55), (91.62, 102.15),
    (102.15, 115.64), (115.68, 125.54), (130.18, 141.47), (141.47, 150.22),
    (150.22, 166.85), (183.92, 196.37), (204.58, 214.33), (214.33, 225.26),
    (225.26, 233.76), (236.41, 247.60),
]
toma2 = [
    (299.46, 308.49), (308.49, 318.70), (318.70, 327.34), (331.68, 340.73),
    (351.13, 358.63), (358.63, 365.70), (365.70, 372.97), (389.09, 400.79),
    (400.79, 414.41), (423.49, 434.09), (434.09, 445.63), (445.63, 454.97),
    (472.46, 482.50), (488.83, 498.37), (509.50, 520.49), (520.49, 530.74),
    (541.39, 550.66), (550.66, 559.90),
]

START_PAD = 0.08
END_PAD = 0.06

def sanitize(s, maxlen=40):
    bad = '<>:"/\\|?*'
    for c in bad:
        s = s.replace(c, "")
    s = s.strip()
    if len(s) > maxlen:
        s = s[:maxlen].rsplit(" ", 1)[0]
    return s.strip()

os.makedirs(OUT_ROOT, exist_ok=True)

for i, frase in enumerate(frases, start=1):
    folder_name = f"{i:02d} - {sanitize(frase)}"
    folder = os.path.join(OUT_ROOT, folder_name)
    os.makedirs(folder, exist_ok=True)

    # clean phrase text file
    with open(os.path.join(folder, "frase.txt"), "w", encoding="utf-8") as f:
        f.write(frase + "\n")

    for toma_num, segs in ((1, toma1), (2, toma2)):
        start, end = segs[i - 1]
        s = max(0, start - START_PAD)
        dur = (end + END_PAD) - s
        out_path = os.path.join(folder, f"{i:02d} - Toma {toma_num}.mp3")
        cmd = [
            FFMPEG, "-y", "-i", SRC,
            "-ss", f"{s:.3f}", "-t", f"{dur:.3f}",
            "-acodec", "libmp3lame", "-q:a", "2",
            out_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("ERROR", out_path, r.stderr[-500:])
        else:
            print("OK", out_path)

print("DONE")
