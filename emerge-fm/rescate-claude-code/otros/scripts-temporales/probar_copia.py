# Simula lo que hace Chrome/Edge (PDFium): clic en el campo, Ctrl+A (SelectAllText) y Ctrl+C (GetSelectedText).
import ctypes, sys
import pypdfium2 as pdfium, pypdfium2.raw as R
sys.stdout.reconfigure(encoding="utf-8")
pdf = pdfium.PdfDocument(sys.argv[1])
pdf.init_forms()
env = pdf.formenv.raw
for ip, (x, y) in [(0, (150, 520)), (1, (150, 450)), (0, (150, 760))]:
    page = pdf[ip]
    h = page.get_height()
    # coordenadas de página PDF (origen abajo-izquierda)
    R.FORM_OnLButtonDown(env, page.raw, 0, x, y); R.FORM_OnLButtonUp(env, page.raw, 0, x, y)
    print("pag", ip+1, "foco:", R.FORM_GetFocusedAnnot.__name__ if hasattr(R,'FORM_GetFocusedAnnot') else '')
    R.FORM_SelectAllText(env, page.raw)
    n = R.FORM_GetSelectedText(env, page.raw, None, 0)
    buf = ctypes.create_string_buffer(n)
    R.FORM_GetSelectedText(env, page.raw, buf, n)
    t = buf.raw.decode("utf-16-le").rstrip("\x00")
    print(len(t), "chars | líneas en blanco:", t.replace("\r\n","\n").replace("\r","\n").count("\n\n"))
    print(repr(t[:110])); print(repr(t[-60:])); print("emoji inicial:", hex(ord(t[0])) if t else None); print()
