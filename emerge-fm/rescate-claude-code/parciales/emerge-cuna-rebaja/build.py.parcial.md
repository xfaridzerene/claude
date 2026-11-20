# emerge-cuna-rebaja/build.py (parcial)

Ruta original: `C:/Users/farid/Desktop/claude code/emerge-cuna-rebaja/build.py`

## Líneas leídas en alguna sesión

Número de línea del archivo original, luego el texto.

```
  225  # ---------- piezas fijas ----------
  226  def tarjeta_foto():
  227      x, y, w, h = CARD
  228      foto = Image.open(os.path.join(AQUI, 'fuentes', FOTO)).convert('RGB')
  229      # recorte 3:4 de la foto cuadrada, centrado en la cara (x≈178 de 335)
  230      fw, fh = foto.size
  231      cw = int(fh * w / h)
  232      x0 = max(0, min(fw - cw, 178 - cw // 2))
  233      foto = foto.crop((x0, 0, x0 + cw, fh)).resize((w, h), Image.LANCZOS)
  234      tarjeta = Image.new('RGBA', (w + 16, h + 16), (0, 0, 0, 0))
  235      d = ImageDraw.Draw(tarjeta)
  236      d.rounded_rectangle([0, 0, w + 15, h + 15], radius=30, fill=VERDE + (255,))
  237      mascara = Image.new('L', (w, h), 0)
  238      ImageDraw.Draw(mascara).rounded_rectangle([0, 0, w - 1, h - 1], radius=24, fill=255)
  239      tarjeta.paste(foto, (8, 8), mascara)
  240      return tarjeta
  241  
  242  
  243  TARJETA = tarjeta_foto()
  244  _lh = Image.open(LOGO_H).convert('RGBA')
  245  _lh = _lh.crop(_lh.getbbox())
  246  LOGO = _lh.resize((250, int(_lh.height * 250 / _lh.width)), Image.LANCZOS)
  247  X_COL = CARD[0] + CARD[2] + 16 + 44
  248  CHIP_CUNA = chip('EN EMERGE NOTICIAS', fuente('s', 'Bold', 26), VERDE, (0, 0, 0))
  249  N1 = texto(NOMBRE[0], fuente('u', 'ExtraBold', 70), (255, 255, 255))
  250  N2 = texto(NOMBRE[1], fuente('u', 'ExtraBold', 70), (255, 255, 255))
  251  C_LINEAS = [texto(c, fuente('s', 'Medium', 34), (215, 215, 215)) for c in CARGO]
  252  
  253  
  254  # ---------- video ----------
  255  class Lector:
  256      """Lee cuadros de cada parte en secuencia desde ffmpeg (sin cargar todo en memoria)."""
  257      def __init__(self):
  258          self.k, self.proc, self.n = -1, None, 0
  259          self.ultimo = np.zeros((BOX_H, 1080, 3), np.uint8)
  260  
  261      def abrir(self, k):
  262          if self.proc:
  263              self.proc.kill()
  264          f, a, z = PARTES[k]
  265          self.proc = subprocess.Popen([FFMPEG, '-v', 'error', '-ss', str(a), '-t', str(z - a), '-i',
  266                                        os.path.join(AQUI, 'fuentes', f), '-an',
  267                                        '-vf', f'{CROP},fps={FPS},scale=1080:{BOX_H}:flags=lanczos',
  268                                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
  269          self.k, self.n = k, 0
  270  
  271      def cuadro(self, k, idx):
  272          if k != self.k:
  273              self.abrir(k)
  274          tam = 1080 * BOX_H * 3
  275          while self.n <= idx:
  276              raw = self.proc.stdout.read(tam)
  277              if len(raw) < tam:
  278                  break
  279              self.ultimo = np.frombuffer(raw, np.uint8).reshape(BOX_H, 1080, 3)
  280              self.n += 1
  281          return self.ultimo
  282  
  283  
  284  def fondo_de(fr):
  285      im = Image.fromarray(fr)
  286      ancho = int(BOX_H * W / H)
  287      x = (1080 - ancho) // 2
  288      im = im.crop((x, 0, x + ancho, BOX_H)).resize((54, 96), Image.BILINEAR)
  289      im = im.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BICUBIC)
  290      yy = np.linspace(-1, 1, H)[:, None]
  291      v = (1 - 0.5 * np.clip(yy ** 2, 0, 1))[..., None]
  292      return (np.asarray(im).astype(np.float32) * 0.36 * v)
  293  
  294  
  295  def onda(capa, t, env, activo):
  296      """Barras simétricas: historia reciente de la voz que avanza hacia la izquierda."""
  297      d = ImageDraw.Draw(capa)
  298      n, gap = 46, 8
  299      x0, x1 = 60, W - 60
  300      bw = (x1 - x0 - gap * (n - 1)) / n
  301      cy = Y_ONDA + H_ONDA / 2
  302      i_t = int(t * 120)
  303      for k in range(n):
  304          # cada barra = 3 muestras (25 ms) hacia atrás; la de la derecha es «ahora»
  305          j = i_t - (n - 1 - k) * 3
  306          v = env[j] if 0 <= j < len(env) else 0
  307          v = max(0.05, min(1.0, v)) * activo
  308          h = max(6, v * H_ONDA)
  309          x = x0 + k * (bw + gap)
  310          a = int(110 + 145 * (k / (n - 1)))
  311          d.rounded_rectangle([x, cy - h / 2, x + bw, cy + h / 2], radius=bw / 2, fill=VERDE + (a,))
  312  
  313  
  314  def componer(t, lector, env, subs, dur, cambios):
  315      k = sum(1 for c in cambios if t >= c)
  316      tl = t - ([0.0] + cambios)[k]
  317      fr = lector.cuadro(k, int(tl * FPS))
  318      lienzo = fondo_de(fr)
  319      lienzo[BOX_Y:BOX_Y + BOX_H] = fr
  320      base = Image.fromarray(lienzo.astype(np.uint8)).convert('RGBA')
  321      capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
  322      d = ImageDraw.Draw(capa)
  323  
  324      e0 = ease(t / 0.5)
  325      # cabecera
  326      pegar(capa, LOGO, (W - LOGO.width) / 2, Y_LOGO, e0)
  327      # tarjeta con foto
  328      pegar(capa, TARJETA, CARD[0] - 8 - 30 * (1 - e0), CARD[1] - 8, e0)
  329      # columna de texto
  330      y = CARD[1] + 18
  331      pegar(capa, CHIP_CUNA, X_COL, y, ease((t - 0.1) / 0.5))
  332      e1 = ease((t - 0.2) / 0.5)
  333      pegar(capa, N1, X_COL + 30 * (1 - e1), y + 74, e1)
  334      pegar(capa, N2, X_COL + 30 * (1 - e1), y + 160, e1)
  335      e2 = ease((t - 0.35) / 0.5)
  336      for j, c in enumerate(C_LINEAS):
  337          pegar(capa, c, X_COL + 20 * (1 - e2), y + 280 + j * 46, e2)
  338      # línea verde bajo el bloque
  339      d.rectangle([X_COL, CARD[1] + CARD[3] - 6, X_COL + 120 * e2, CARD[1] + CARD[3] - 1], fill=VERDE + (255,))
  340  
  341      # onda de audio
  342      onda(capa, t, env, ease(t / 0.4))
  343  
  344      # filetes del clip
  345      d.rectangle([0, BOX_Y - 8, W, BOX_Y - 1], fill=VERDE + (255,))
  346      d.rectangle([0, BOX_Y + BOX_H, W, BOX_Y + BOX_H + 7], fill=VERDE + (255,))
  347      # destello en el cambio de parte
  348      t_cambio = max([c for c in cambios if c <= t], default=-9)
  349      if 0 <= t - t_cambio < 0.16:
  350          a = int(140 * (1 - (t - t_cambio) / 0.16))
  351          capa.alpha_composite(Image.new('RGBA', (W, BOX_H), (255, 255, 255, a)), (0, BOX_Y))
  352  
  353      # subtítulo vigente
  354      for b in subs:
  355          if b['ini'] <= t < b['fin']:
  356              dibujar_sub(capa, b, t)
  357              break
  358  
  359      base.alpha_composite(capa)
```
