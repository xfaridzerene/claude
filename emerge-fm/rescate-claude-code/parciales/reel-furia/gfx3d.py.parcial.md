# reel-furia/gfx3d.py (parcial)

Ruta original: `C:/Users/farid/Desktop/claude code/reel-furia/gfx3d.py`

## Líneas leídas en alguna sesión

Número de línea del archivo original, luego el texto.

```
  140          A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
  141          A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
  142      return np.linalg.solve(np.array(A, float), np.array(b, float))
  143  
  144  
  145  def draw(tex, pos, rot=(0, 0, 0), scale=1.0, opacity=1.0):
  146      """Devuelve (rgba premultiplicado uint8 [h,w,4], (x0,y0)) o None si queda fuera de cuadro.
  147  
  148      pos = (x, y, z) en píxeles de pantalla del centro de la cara; z > 0 se aleja de la cámara.
  149      """
  150      if opacity <= 0.003 or scale <= 0.01:
  151          return None
  152      R = _rot(*rot)
  153      hw, hh = tex.w / 2, tex.h / 2
  154      tw, th = tex.mask.size
  155      src = [(0, 0), (tw, 0), (tw, th), (0, th)]
  156  
  157      def quad(d):
  158          loc = np.array([[-hw, -hh, d], [hw, -hh, d], [hw, hh, d], [-hw, hh, d]], float)
  159          return _project(loc, R, pos, scale)
  160  
  161      q0, q1 = quad(0.0), quad(tex.depth)
  162      allp = np.vstack([q0, q1])
  163      x0, y0 = np.floor(allp.min(0)).astype(int) - 2
  164      x1, y1 = np.ceil(allp.max(0)).astype(int) + 2
  165      x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
  166      if x1 - x0 < 2 or y1 - y0 < 2:
  167          return None
  168      size = (int(x1 - x0), int(y1 - y0))
  169      off = np.array([x0, y0], float)
  170      disp = np.abs(q1 - q0).max()
  171      n = int(min(30, max(2, math.ceil(disp / 1.9))))
  172      canvas = Image.new("RGBA", size, (0, 0, 0, 0))
  173      for j in range(n, 0, -1):                      # del fondo hacia la cara
  174          d = tex.depth * j / n
  175          c = _coeffs(quad(d) - off, src)
  176          layer = tex.side_rgba.transform(size, Image.PERSPECTIVE, tuple(c), Image.BILINEAR)
  177          shade = 0.50 + 0.50 * (1 - j / n) ** 1.3   # más oscuro hacia atrás
  178          rgb = layer.convert("RGB").point(lambda v, s=shade: int(v * s))
  179          canvas.paste(rgb, (0, 0), layer.getchannel("A"))
  180      c = _coeffs(q0 - off, src)
  181      layer = tex.face_rgba.transform(size, Image.PERSPECTIVE, tuple(c), Image.BICUBIC)
  182      canvas.paste(layer.convert("RGB"), (0, 0), layer.getchannel("A"))
  183      out = np.asarray(canvas, np.float32)
  184      if opacity < 0.999:
  185          out = out * opacity
  186      # la capa quedó premultiplicada: color*alpha se fue acumulando con cada paste
  187      return out, (int(x0), int(y0))
  188  
  189  
  190  def merge(dst, layer):
  191      """Compone una capa premultiplicada sobre el lienzo premultiplicado (float32 HxWx4)."""
  192      if layer is None:
  193          return
  194      img, (x0, y0) = layer
  195      h, w = img.shape[:2]
  196      reg = dst[y0:y0 + h, x0:x0 + w]
  197      reg *= (1 - img[..., 3:4] / 255.0)
  198      reg += img
  199  
  200  
  201  # ---------- curvas de animación ----------
  202  
  203  def clamp(x, a=0.0, b=1.0):
  204      return a if x < a else b if x > b else x
  205  
  206  
  207  def ease_out(x):
  208      x = clamp(x); return 1 - (1 - x) ** 3
  209  
  210  
  211  def ease_in(x):
  212      x = clamp(x); return x ** 3
  213  
  214  
  215  def back_out(x, s=1.9):
  216      x = clamp(x) - 1; return x * x * ((s + 1) * x + s) + 1
  217  
```
