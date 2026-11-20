# emerge-larenas/build.py (parcial)

Ruta original: `C:/Users/farid/Desktop/claude code/emerge-larenas/build.py`

## Líneas leídas en alguna sesión

Número de línea del archivo original, luego el texto.

```
    1  # Reel vertical de la cuña de Camilo Jiménez (ASGRO): rebaja de $300 en combustibles.
    2  # Abre con un DESTACADO (la frase de los 300 pesos) y luego la cuña completa.
    3  # Arriba: foto de Camilo en un cuadro + nombre/cargo + onda de audio en vivo.
    4  # Al medio: Roberto Rojas (16:9 a ancho completo, GC intacto). Abajo: subtítulos en seco
    5  # (sin fundido ni subida) con la palabra que suena resaltada.
    6  # Plantilla: copia de emerge-cuna-asgro con PARTES de largo variable.
    7  #   python build.py                 -> salida/cuna-rebaja-300-camilo-jimenez-9x16.mp4
    8  #   python build.py --fotos 1,20    -> revision/foto_<t>.png
    9  import os, sys, json, subprocess, math, re
   10  import numpy as np
   11  from PIL import Image, ImageDraw, ImageFont, ImageFilter
   12  from scipy.io import wavfile
   13  
   14  AQUI = os.path.dirname(os.path.abspath(__file__))
   15  FFMPEG = r'C:\Program Files\Shutter Encoder\app\Library\ffmpeg.exe'
   16  EFM = r'C:\Users\farid\Desktop\EMERGE FM'
   17  F_UNB = os.path.join(EFM, 'Fuentes', 'Unbounded', 'static', 'Unbounded-{}.ttf')
   18  F_SG = os.path.join(EFM, 'Fuentes', 'Space_Grotesk', 'static', 'SpaceGrotesk-{}.ttf')
   19  LOGO_H = os.path.join(EFM, 'LOGO', 'Logo 105.5', 'PNG', 'emerge-fm-105.5-horizontal-color-transparente.png')
   20  
   21  W, H, FPS = 1080, 1920, 30
   22  CROP = 'crop=2080:1170:226:0'
   23  VERDE = (0, 230, 171)
   24  GRIS = (22, 22, 22)
   25  
   26  # Partes en orden: (archivo, inicio, fin) en segundos de la fuente
   27  PARTES = [('cuna.mp4', 29.80, 38.00),   # DESTACADO: «Estamos pidiendo una reducción de 300 pesos… negociaciones»
   28            ('cuna.mp4', 0.0, 77.0)]      # cuña completa
   29  TRANS = ['audio1', 'audio1']           # clave de transcripcion.json para cada parte
   30  ETIQUETAS = [None, None]               # sin chips: el usuario no quiere «DESTACADO» ni «cuña» en pantalla
   31  DUR_ETIQUETA = [None, 2.5]             # None = toda la parte
   32  XFADE = 0.06  # cruce de audio entre partes
   33  
   34  # Diseño (y en px)
   35  Y_LOGO = 92
   36  CARD = (60, 175, 360, 480)        # x, y, ancho, alto de la foto
   37  Y_ONDA, H_ONDA = 700, 110
   38  BOX_Y, BOX_H = 850, 608
   39  Y_SUB = BOX_Y + BOX_H + 54
   40  
   41  # Correcciones a la transcripción (secuencias de palabras -> reemplazo)
   42  EDITS = []
   43  
   44  NOMBRE = ('Camilo', 'Jiménez')
   45  CARGO = ['Vocero de la Asociación', "Gremial Rengo O'Higgins", '(ASGRO)']
   46  FOTO = 'camilo.png'
   47  FOTO_CX, FOTO_Y = None, 18   # centro x de la cara (None = centro) y recorte superior
   48  
   49  
   50  def fuente(f, peso, tam):
```
