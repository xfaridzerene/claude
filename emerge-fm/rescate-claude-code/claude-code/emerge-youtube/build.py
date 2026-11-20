"""Genera salida/Emerge-FM-YouTube-En-Vivo.pdf desde youtube.html con Chrome headless.

Encima de cada título, descripción y lista de etiquetas pone un campo de texto invisible con el
contenido exacto: en el PDF se hace clic en el recuadro, Ctrl+A y Ctrl+C, y se pega con los saltos
de línea y los emojis intactos (copiar el texto impreso de un PDF los pierde).

Uso: python build.py  [--png]  (--png también deja una imagen por página en salida/_paginas)"""
import html, json, pathlib, re, subprocess, sys
import pymupdf

RAIZ = pathlib.Path(__file__).resolve().parent
HTML = RAIZ / "youtube.html"
PDF = RAIZ / "salida" / "Emerge-FM-YouTube-En-Vivo.pdf"
CHROMES = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
           r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
chrome = next(c for c in CHROMES if pathlib.Path(c).exists())
BASE = [chrome, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
        "--no-pdf-header-footer", "--virtual-time-budget=4000"]
PDF.parent.mkdir(exist_ok=True)

# 1) Textos exactos, tal como los arma el script de la página
dom = subprocess.run(BASE + ["--dump-dom", HTML.as_uri()], capture_output=True, check=True).stdout.decode("utf-8")
m = re.search(r'<script type="application/json" id="copias">(.*?)</script>', dom, re.S)
copias = {int(k): v for k, v in json.loads(html.unescape(m.group(1))).items()}

# 2) PDF base
crudo = PDF.with_name("_base.pdf")
subprocess.run(BASE + [f"--print-to-pdf={crudo}", HTML.as_uri()], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 3) Campos de texto encima de cada recuadro (ubicados por las marcas QQa<k>Z / QQb<k>Z)
doc = pymupdf.open(crudo)
puestos = 0
for pag in doc:
    for k, texto in copias.items():
        a = pag.search_for(f"QQa{k}Z"); b = pag.search_for(f"QQb{k}Z")
        if not (a and b):
            continue
        r = pymupdf.Rect(a[0].x0 - 1, a[0].y0 - 1, b[0].x1 + 1, b[0].y1 + 1)
        w = pymupdf.Widget()
        w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
        w.field_name = f"copiar_{k}"
        w.field_value = texto
        w.field_flags = pymupdf.PDF_TX_FIELD_IS_MULTILINE | pymupdf.PDF_TX_FIELD_IS_DO_NOT_SPELL_CHECK
        w.rect = r
        w.text_font = "Helv"; w.text_fontsize = 1      # el texto del campo no se ve: lo que se lee es lo impreso
        w.text_color = (0.957, 0.957, 0.957); w.fill_color = None
        w.border_width = 0; w.border_color = None
        w.field_label = "Clic, Ctrl+A y Ctrl+C para copiar"
        pag.add_widget(w)
        puestos += 1
faltan = len(copias) - puestos
doc.save(PDF, garbage=3, deflate=True)
doc.close(); crudo.unlink()
print("PDF:", PDF, f"· {puestos} campos para copiar" + (f" · FALTAN {faltan}" if faltan else ""))

if "--png" in sys.argv:
    out = PDF.parent / "_paginas"; out.mkdir(exist_ok=True)
    for f in out.glob("*.png"): f.unlink()
    doc = pymupdf.open(PDF)
    for i, p in enumerate(doc, 1):
        p.get_pixmap(dpi=80).save(out / f"p{i}.png")
    print(len(doc), "paginas en", out)
