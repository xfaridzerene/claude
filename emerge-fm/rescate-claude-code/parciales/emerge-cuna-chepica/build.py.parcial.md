# emerge-cuna-chepica/build.py (parcial)

Ruta original: `C:/Users/farid/Desktop/claude code/emerge-cuna-chepica/build.py`

## Cambios hechos sin conocer el archivo completo

### 2026-11-12T13:36

Antes:
```
        largo = len(actual) >= 7 or (len(actual) >= 5 and i + 1 < len(ws) and ws[i + 1]['p'] in ('que', 'y', 'porque', 'donde', 'para', 'mientras'))
```
Después:
```
        # no cortar tras artículo/preposición ni dejar 1–2 palabras sueltas antes de un punto
        cola = any(ws[j]['p'][-1] in '.?!,' for j in range(i + 1, min(i + 3, len(ws))))
        largo = (len(actual) >= 7 and w['p'].lower() not in DEBIL and not (cola and len(actual) < 9)) \
            or (len(actual) >= 5 and i + 1 < len(ws) and ws[i + 1]['p'] in ('que', 'y', 'porque', 'donde', 'para', 'mientras'))
```

### 2026-11-12T13:36

Antes:
```
MAX_LINEA = 900

```
Después:
```
MAX_LINEA = 900
DEBIL = {'a', 'al', 'de', 'del', 'el', 'la', 'los', 'las', 'un', 'una', 'con', 'en', 'se', 'es', 'y', 'que',
         'por', 'para', 'su', 'sus', 'lo', 'le', 'nos', 'no', 'va', 'muy', 'más', 'san', 'ya'}

```
