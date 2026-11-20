# Viaje sin Rumbo: patrones de armado del programa

Recuperado de la sesión «Programa de radio Viaje sin Rumbo» (9 al 20 de noviembre de 2026).
Programa: **Viaje sin Rumbo**, música chilena, con **Valentina Sepúlveda**, lunes a viernes de 15:00 a 16:00, en Emerge FM 105.5.

Archivos de esta carpeta:

| Archivo | Qué es |
|---|---|
| `armar_programa.py` | El script en su última versión (programa del viernes 20-11, «Canciones de madres»). Reconstruido aplicando, en orden, cada cambio que se le hizo desde el 16-11. |
| `transcribir_locuciones.py` | Transcribe las locuciones con faster-whisper. Se usa cuando no llega la pauta, para sacar el orden de las canciones. |
| `nota-de-memoria-viaje-sin-rumbo-programa.md` | La nota de memoria que Claude fue escribiendo día a día, completa. |

---

## 1. Qué entrega Valentina cada día (todo en Descargas)

- **Pauta** del día en `.docx` o `.pdf` («PAUTA 10-11 MARTES VIAJE SIN RUMBO.docx»). Si no llega, el orden se saca de las locuciones (ver punto 6).
- **Locuciones** ya procesadas, con nombres como `1. SALUDO-esv2-90p-bg-10p-music-10p.wav`, `4. LOCUCIÓN-esv2-90p-…wav`, `10. MENCIONES-…wav` y `11 Y 12. REGRESO DE TANDA Y LOCUCION-…wav`.
  - Los nombres **se repiten todos los días**: siempre se toma **la más reciente**, y de las procesadas con `-esv2-90p` (o `91p`), no las viejas `-50p` ni las crudas del zip.
  - A veces vienen con «(1)» o «(2)» en el nombre; vale la misma regla.
- **Canciones** en MP3 (a veces un WAV). Ella las pasa antes por MP3Gain a 89 dB, aunque el script igual las nivela.
- Fijos de todos los días: `Presentacion Viaje sin Rumbo.wav`, `Despedida Viaje sin Rumbo.wav`, `Restaurante Molen.wav`, `Valhala Gym.wav` y la cortina `Música Vale (normalizada)\Nicole - Viaje Infinito (Instrumental).mp3`.

## 2. Estructura de la hora (formato vigente desde el 16-11)

13 canciones y 8 locuciones. Los números de las locuciones son las líneas de la pauta.

**Bloque 1**
1. CORTINA DE INICIO: Presentación Viaje sin Rumbo
2. **Locución 1**: saludo, editorial y tema del día
3. Canciones 01 y 02
4. **Locución 4**: historia
5. Canciones 03 y 04
6. **Locución 7**: artista o disco
7. Canciones 05 y 06
8. **Locución 10**: MENCIONES (Molen, Valhalla), sobre la cortina
9. CORTE COMERCIAL: frase Restaurante Molen y frase Valhalla Gym, solas, con 0,4 s entre piezas

**Bloque 2**

10. **Locución 11 + 12**: regreso de tanda y el especial del día
11. Canciones 07 y 08
12. **Locución 15**: dato o curiosidad
13. Canciones 09 y 10
14. **Locución 18**: «algo que me guste»
15. Canciones 11 y 12
16. **Locución 21**: cierre y menciones finales
17. Canción 13
18. CORTINA DE CIERRE: Despedida Viaje sin Rumbo

Duraciones obtenidas: de 54:37 a 65:45. Con 13 canciones suele pasarse de la hora; si hay que acortar, se saca una canción de 4 a 5 minutos.

## 3. Vocabulario de la radio (importante)

- **Mención**: el locutor lee al auspiciador en vivo. Es locución y **va sobre la cortina**.
- **Frase**: la cuña comercial grabada (Restaurante Molen, 0:25; Valhalla Gym, 0:28). **Suena sola, sin cortina**, en el corte comercial.
- **Cortina de fondo**: «Nicole – Viaje Infinito (Instrumental)», bajo todas las locuciones.

## 4. Reglas de audio

| Elemento | Tratamiento |
|---|---|
| **Todo** | Parejo a **−18 LUFS**. |
| **Voz** | Solo ganancia hasta −18 LUFS, **sin EQ, compresor ni limpieza**, más un limitador con anticipación (techo −1 dBFS) para picos sueltos. Normalmente actúa menos de 1 dB y menos del 0,5 % del tiempo. El archivo de voz entra completo, tal cual. |
| **Canciones** | Se normalizan a −18 LUFS con ganancia simple. Se corta el silencio digital (−50 dB) del inicio y del final, y el aire casi mudo (ventana de 1 s a −35 dB de la sonoridad de la canción) al inicio y al final, con un fade de entrada de 0,3 s (y de salida de 1 s cuando se corta cola). El script imprime cuánto cortó en cada una. |
| **Cortina bajo la voz** | Sola, antes y después de la voz: −6 dB respecto de −18 LUFS. Bajo la voz: 18,5 dB por debajo de esa locución. Entra 2,5 s antes de la voz, sube 1,2 s después y hace fundidos de 1,5 s de entrada y 2 s de salida. El día 1 se pidió bajarla porque se oía muy fuerte; estos valores vienen de ese ajuste. |
| **Enlaces** | Las canciones se encadenan con 0,3 s de traslape; la despedida, con 0,5 s y un fade de entrada de 0,5 s. |
| **Música y cortinas** | Un limitador suave de picos a −1,5 dBFS (la voz ya trae el suyo). |
| **Salida** | WAV de 24 bit a 48 kHz, MP3 de 320 kbps y `minutaje.txt` con la hora de cada pieza y su tipo. |

Historia de la voz: el martes 10-11 se pidió primero «no tocar la voz» (se entregaron pistas separadas) y esa misma tarde «nivelar como antes sin perder calidad». Desde entonces rige solo ganancia más limitador. Desde el 12-11 se entrega **solo la mezcla final**, sin pistas separadas.

## 5. Rutina diaria

1. Crear `viaje-sin-rumbo\programa-DD-11\` con `voces\` y `salida\`.
2. Copiar las voces del día, siempre la más reciente de cada número (en Descargas se pisan con los mismos nombres):
   ```bash
   cd /c/Users/farid/Downloads && P="C:/Users/farid/Desktop/claude code/viaje-sin-rumbo/programa-DD-11"
   mkdir -p "$P/voces" "$P/salida"
   for n in 1 4 7 10 15 18 21; do f=$(ls -t ${n}.\ *-esv2-90p*.wav | head -1); cp "$f" "$P/voces/$n.wav"; echo "$n <- $f"; done
   f=$(ls -t 11\ Y\ 12.*-esv2-90p*.wav | head -1); cp "$f" "$P/voces/12.wav"
   cp "<programa del día anterior>/armar_programa.py" "$P/"
   ```
3. En el script, cambiar tres cosas:
   - el diccionario `songs` (las 13 canciones). Se buscan **por el comienzo del nombre** con `find("...")`, o con comodines con `newest("...")`, porque los acentos vienen en NFD y el nombre exacto falla;
   - el bloque de `locucion(...)` y `song(...)` con los temas del día;
   - el nombre del archivo y el título del minutaje.
4. `python armar_programa.py --check` lista qué archivo tomó para cada canción. Después, `python armar_programa.py` arma la hora (se corre con `C:\Users\farid\audio-env\Scripts\python.exe -X utf8`).
5. Revisar en el minutaje la duración y en qué minuto parten el corte comercial y el bloque 2.
6. **Verificar contra la pauta**: transcribir las locuciones (`transcribir_locuciones.py`) y confirmar que cada una nombre la canción que acaba de sonar y presente la que viene. Si no llegó pauta, el orden se arma así.
7. Medir los LUFS de cada canción dentro de la mezcla final usando los tiempos del minutaje; todas deben quedar entre −17,8 y −18,0.
8. Si falta algo, preguntar y esperar el archivo.

## 6. Video con el loop (para YouTube)

El loop animado de Valentina está en `viaje-sin-rumbo-loop\salida\viaje-sin-rumbo-loop-16x9-liviano.mp4` (60 s, 4 Mbps). Se repite bajo el audio del programa sin volver a codificar el video:

```bash
D=$(python -c "import soundfile as sf;print(sf.info('PROGRAMA.wav').duration)")
ffmpeg -stream_loop -1 -i viaje-sin-rumbo-loop-16x9-liviano.mp4 -i PROGRAMA.wav \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -ar 48000 -t $D -movflags +faststart "PROGRAMA (video loop).mp4"
```

Resultado: 1920×1080 a 30 fps, con la duración exacta del audio (unos 1,8 GB por hora con la versión liviana del loop).

## 7. Cosas que ya pasaron y conviene recordar

- Canciones bajadas de video traen silencio o ruido: Gepe «Bacán tu Casa» traía 33 s de silencio al final, Papa Negro 4,8 s al inicio, Dënver unos 11 s casi mudos y Pillanes unos 10 s de ruidos antes de la banda.
- Algunos MP3 vienen mucho más fuertes (Pedropiedra «Mi mamá» y «Cariñar», a −8,4 LUFS): el script los baja igual a −18.
- Desde mono, `ffmpeg -ac 2` baja 3 dB (es solo ganancia, se compensa al normalizar).
- Usar buffers en float32 para no quedarse sin RAM, y `uniform_filter1d` en vez de `np.convolve` con ventanas largas (tardaba más de 10 minutos).
- faster-whisper corre en CPU con int8; en GPU falla por falta de cuBLAS.
- Las carpetas `programa-09` a `programa-13` las borró el usuario; el script se reconstruyó el 16-11.

## 8. Programas armados

| Fecha | Tema | Duración |
|---|---|---|
| Lun 09-11 | (primer programa) | 56:00 |
| Mar 10-11 | Nuevo Pop | 50:40 |
| Mié 11-11 | Reinas del Pop | 52:24 |
| Jue 12-11 | Los Irreverentes | 48:20 |
| Vie 13-11 | Los Jaivas cantan a Violeta Parra | 54:53 |
| Lun 16-11 | Desenchufados | 65:02 |
| Mar 17-11 | Amistades | 65:45 |
| Mié 18-11 | El sonido del sur | 61:51 |
| Jue 19-11 | El ritmo (cumpleaños de Juanita Parra) | 60:04 |
| Vie 20-11 | Canciones de madres | 54:37 |
