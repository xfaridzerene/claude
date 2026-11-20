# emerge-lamina/tools/build.py (parcial)

Ruta original: `C:/Users/farid/Desktop/claude code/emerge-lamina/tools/build.py`

## Cambios hechos sin conocer el archivo completo

### 2026-11-06T16:11

Antes:
```
        objetos.append(b"<< /N 4 /Alternate /DeviceCMYK /Length %d /Filter /FlateDecode >>
stream
" % len(icc)
                       + icc + b"
endstream")
```
Después:
```
        objetos.append(b"<< /N 4 /Alternate /DeviceCMYK /Length %d /Filter /FlateDecode >>\nstream\n" % len(icc)
                       + icc + b"\nendstream")
```
