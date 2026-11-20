# -*- coding: utf-8 -*-
import subprocess, os

FFMPEG = r"C:\Users\farid\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
SRC = r"C:\Users\farid\Desktop\EMERGE FM\La Ciudad de la Furia\Frases en bruto.mp3"
OUT_ROOT = r"C:\Users\farid\Desktop\EMERGE FM\La Ciudad de la Furia\FRASES"

frases = [
    "Hacemos una pausa y ya vuelve Kaco López con más de... La Ciudad de la Furia.",
    "Ves, la espera no fue tan larga... ahora sigue disfrutando de la compañía de Kaco López y La Ciudad de la Furia.",
    "Suenan las bocinas en el taco, y tú te relaaaajas... porque escuchas a Kaco López en... La Ciudad de la Furia.",
    "No te desconectes, una pausa y ya vuelve Kaco López a... La Ciudad de la Furia.",
    "Kaco López va por un café, bien cargado... y ya regresa a La Ciudad de la Furia.",
    "Te diviertes... no te separes, una pausa y volvemos.",
    "La tarde es más entretenida escuchando La Ciudad de la Furia.",
    "Envíanos tu audio de WhatsApp, +56 9 5932 9020.",
    "Comunícate con nosotros, +56 9 5932 9020.",
    "De lunes a viernes te invitamos a conectarte a través de la 92.5, porque a las 17:00 horas llega Kaco López con... La Ciudad de la Furia.",
    "Hacemos un viaje al pasado en La Ciudad de la Furia.",
    "www.laciudaddelafuria.cl",
    "En La Ciudad de la Furia... la voz de los 80s.",
    "Les recordamos que desde las 17:00 La Ciudad de la Furia está autorizada para transmitir programas solo para ochenteros y noventeros, mayores de... no importaaaa, lo importante es que te guste la música de verdad.",
    "Señoras y señores..., ladies and gentleman, día miércoles y llega a La Ciudad de la Furia el máster de los dog... con ustedes... Andrés Becerra.",
    "A esta hora, la mujer más divertida, simpática... amorosa, diosa, divina, apolínea, fantástica, y lengua desatada... llega a La Ciudad de la Furia... la Sole Romero...",
    "Llegó la hora más esperada del día, porque nos conectamos para transportarnos al pasado... para hacer un viaje en el tiempo, y recordar los mejores años de tu vida... ochenteros y noventeros, bienvenidos, porque aquí comienza... La Ciudad de la Furia, con Mr. Kaco López.",
    "Fueron dos horas de música, diversión y mucho recuerdo... pero tranquilo, porque [EN EL AUDIO: 'el lunes', no 'mañana'] vuelve Kaco López, con el programa de radio más retro de los últimos tiempos... La Ciudad de la Furia.",
    "La Ciudad de la Furia es presentado por:",
    "La Ciudad de la Furia fue presentado por:",
    "La Ciudad de la Furia, por Bonita FM y www.bonitafm.cl",
]

# (start, end) in seconds. F18 is a list of 2 pieces to concatenate (skips a rejected take).
segments = {
    1: [(0.00, 5.48)],
    2: [(5.48, 12.88)],
    3: [(12.88, 21.18)],
    4: [(21.18, 29.11)],
    5: [(30.26, 35.80)],
    6: [(35.80, 39.90)],
    7: [(44.62, 49.46)],
    8: [(49.46, 55.50)],
    9: [(55.50, 61.10)],
    10: [(61.10, 70.90)],
    11: [(70.90, 76.07)],
    12: [(76.23, 79.95)],
    13: [(79.95, 83.75)],
    14: [(83.75, 99.83)],
    15: [(99.83, 111.10)],
    16: [(111.10, 124.46)],
    17: [(124.54, 143.18)],
    18: [(143.18, 147.22), (150.74, 159.06)],
    19: [(159.06, 163.74)],
    20: [(163.74, 167.30)],
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

os.makedirs(OUT_ROOT, exist_ok=True)

for i, frase in enumerate(frases, start=1):
    folder_name = f"{i:02d} - {sanitize(frase)}"
    folder = os.path.join(OUT_ROOT, folder_name)
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, "frase.txt"), "w", encoding="utf-8") as f:
        f.write(frase + "\n")

    pieces = segments[i]
    out_path = os.path.join(folder, f"{i:02d} - Frase.mp3")

    if len(pieces) == 1:
        start, end = pieces[0]
        s = max(0, start - START_PAD)
        dur = (end + END_PAD) - s
        cmd = [
            FFMPEG, "-y", "-i", SRC,
            "-ss", f"{s:.3f}", "-t", f"{dur:.3f}",
            "-acodec", "libmp3lame", "-q:a", "2",
            out_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
    else:
        # cut each piece to a temp file, then concat
        tmp_files = []
        for j, (start, end) in enumerate(pieces):
            s = max(0, start - START_PAD)
            dur = (end + END_PAD) - s
            tmp = os.path.join(folder, f"_tmp_{j}.mp3")
            subprocess.run([
                FFMPEG, "-y", "-i", SRC,
                "-ss", f"{s:.3f}", "-t", f"{dur:.3f}",
                "-acodec", "libmp3lame", "-q:a", "2",
                tmp,
            ], capture_output=True, text=True)
            tmp_files.append(tmp)
        list_path = os.path.join(folder, "_concat_list.txt")
        with open(list_path, "w", encoding="utf-8") as lf:
            for tf in tmp_files:
                lf.write(f"file '{os.path.basename(tf)}'\n")
        r = subprocess.run([
            FFMPEG, "-y", "-f", "concat", "-safe", "0",
            "-i", list_path, "-acodec", "libmp3lame", "-q:a", "2",
            out_path,
        ], capture_output=True, text=True, cwd=folder)
        for tf in tmp_files:
            os.remove(tf)
        os.remove(list_path)

    if r.returncode != 0:
        print("ERROR", out_path, r.stderr[-400:])
    else:
        print("OK", out_path)

print("DONE")
