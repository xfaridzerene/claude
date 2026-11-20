# -*- coding: utf-8 -*-
import subprocess, os

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
SRC = r"C:\Users\farid\Desktop\EMERGE FM\La Ciudad de la Furia\Frases en bruto.mp3"
OUT_ROOT = r"C:\Users\farid\Desktop\EMERGE FM\La Ciudad de la Furia\FRASES"

frases = {
    8: "Envíanos tu audio de WhatsApp, +56 9 5932 9020.",
    9: "Comunícate con nosotros, +56 9 5932 9020.",
    10: "De lunes a viernes te invitamos a conectarte a través de la 92.5, porque a las 17:00 horas llega Kaco López con... La Ciudad de la Furia.",
    14: "Les recordamos que desde las 17:00 La Ciudad de la Furia está autorizada para transmitir programas solo para ochenteros y noventeros, mayores de... no importaaaa, lo importante es que te guste la música de verdad.",
    15: "Señoras y señores..., ladies and gentleman, día miércoles y llega a La Ciudad de la Furia el máster de los dog... con ustedes... Andrés Becerra.",
    16: "A esta hora, la mujer más divertida, simpática... amorosa, diosa, divina, apolínea, fantástica, y lengua desatada... llega a La Ciudad de la Furia... la Sole Romero...",
    17: "Llegó la hora más esperada del día, porque nos conectamos para transportarnos al pasado... para hacer un viaje en el tiempo, y recordar los mejores años de tu vida... ochenteros y noventeros, bienvenidos, porque aquí comienza... La Ciudad de la Furia, con Mr. Kaco López.",
    21: "La Ciudad de la Furia, por Bonita FM y www.bonitafm.cl",
}

segments = {
    8: [(49.46, 55.50)],
    9: [(55.50, 61.10)],
    10: [(61.10, 70.90)],
    14: [(83.75, 99.83)],
    15: [(99.83, 111.10)],
    16: [(111.10, 124.46)],
    17: [(124.54, 143.18)],
    21: [(167.30, 173.38)],
}

START_PAD = 0.08
END_PAD = 0.06

def sanitize(s, maxlen=45):
    bad = '<>:"/\\|?*'
    for c in bad:
        s = s.replace(c, "")
    s = s.strip()
    if len(s) > maxlen:
        s = s[:maxlen].rsplit(" ", 1)[0]
    return s.strip()

for i, frase in frases.items():
    folder_name = f"{i:02d} - {sanitize(frase)}"
    folder = os.path.join(OUT_ROOT, folder_name)
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, "frase.txt"), "w", encoding="utf-8") as f:
        f.write(frase + "\n")

    start, end = segments[i][0]
    s = max(0, start - START_PAD)
    dur = (end + END_PAD) - s
    out_path = os.path.join(folder, f"{i:02d} - Frase.mp3")
    cmd = [
        FFMPEG, "-y", "-i", SRC,
        "-ss", f"{s:.3f}", "-t", f"{dur:.3f}",
        "-acodec", "libmp3lame", "-q:a", "2",
        out_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR", out_path, r.stderr[-400:])
    else:
        print("OK", out_path)

print("DONE")
