# GC de «La Ciudad de la Furia» para OBS

Generador de caracteres con la estética cómic del promocional: rojo con trama de puntos, contorno de tinta y
sombra dura, franja blanca, logo blanco con sombra en rojo oscuro (#7a0a13) y los rayos del propio logo.
Es el mismo sistema del GC de «Emerge tu mañana»: misma placa, mismo panel, mismos parámetros.
Funciona sin internet: las fuentes van en `fuentes/` y el logo en `img/`.

| Archivo | Qué es |
|---|---|
| `gc-furia.html` | La placa. Va en OBS como **Fuente de navegador** de 1920 × 1080, fondo transparente |
| `panel-furia.html` | El panel de control. Va en OBS como **acoplable de navegador** (o en cualquier navegador) |
| `img/` | Letras del logo y los rayos, recortados de `CDF blanco.png` |
| `fuentes/` | Unbounded y Space Grotesk (variables) |

## Placas

- **Invitado**: nombre + cargo.
- **Tema**: antetítulo (etiqueta blanca) + título.
- **Cita**: frase de dos o tres líneas + autor.
- **Redes**: Instagram, YouTube y web (el que quede vacío no se muestra).
- **Mosca** (aparte): logo, EN VIVO y la hora, arriba a la derecha.

Si un texto no cabe en pantalla, se achica solo.

## Instalación en OBS

1. **Fuente de navegador** → Archivo local → `gc-furia.html`, ancho 1920, alto 1080.
   Desmarca «Apagar la fuente cuando no sea visible».
2. Opcional, para la mosca: otra fuente de navegador con la URL `file:///…/gc/gc-furia.html?modo=mosca`.
3. **Acoplables → Acoplables de navegador personalizados**: nombre «Control GC Furia», URL `file:///…/gc/panel-furia.html`.
4. **Herramientas → Configuración del servidor WebSocket → Habilitar servidor**. Copia la contraseña.
5. En el panel: pega la contraseña y pulsa **Conectar**. El panel solo ve las fuentes que apuntan a
   `gc-furia.html`: no toca el GC de «Emerge tu mañana» (`gc.html`) ni otras fuentes como el marcador.

Con el **Modo Estudio**, la placa se prende y se apaga en todas las escenas donde esté la fuente; sale al aire
cuando esa escena está en Programa.

## Uso al aire

- **Mostrar al aire**: la placa azota desde la izquierda, destello, sacudón, el texto se estampa y saltan los rayos.
- **Ocultar**: la placa sale hacia la izquierda y luego se apaga la fuente.
- **Actualizar texto**: corrige una placa que ya está al aire sin repetir la entrada.
- **Guardados**: Kaco y los invitados del día; un clic los carga.
- **Rayos chispeando al lado**: los rayos parpadean de vez en cuando; se pueden quitar.
- **En espera**: mientras la placa está al aire sigue viva: la trama de puntos avanza, un brillo la cruza
  cada 6,5 s, el logo da un golpe cada 4,8 s, las chispas titilan y la pestaña late. La mosca también tiene
  el brillo y el golpe del logo.

## Sin el panel

| Parámetro | Valores |
|---|---|
| `placa` | `nombre`, `tema`, `cita`, `redes` |
| `nombre`, `cargo` · `temaKicker`, `tema` · `cita`, `citaAutor` · `redIg`, `redYt`, `redWeb` | textos |
| `programa` | texto de la pestaña sobre la placa (por defecto no hay pestaña) |
| `anim=0` | aparece sin animación · `salir=1` sale animada · `visible=0` no muestra nada |
| `duracion` | segundos de la entrada (0.4 a 2.5) |
| `pos` | `izq` o `centro` · `margen` en px · `escala` 0.7 a 1.3 · `rayos=0` sin rayos |
| `modo=mosca` | solo la mosca; `vivo=0` sin EN VIVO, `reloj=0` sin hora, `moscaPos=izq` |
| `fondo` | `foto`, `cuadros`, `negro`: solo para probar fuera de OBS |

Ejemplo: `gc-furia.html?placa=nombre&nombre=Kaco%20L%C3%B3pez&cargo=Conductor`

