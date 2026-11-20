# -*- coding: utf-8 -*-
"""Voz limpia + efectos sintetizados (whooshes e impactos) -> audio.m4a"""
import subprocess, sys, wave
import numpy as np
from scipy.signal import butter, sosfilt
import render_nov9 as r

SR = 48000
DUR = r.N1 / r.FPS
rng = np.random.default_rng(9)


def load_voice():
    cmd = [r.FF, "-hide_banner", "-loglevel", "error", "-i", r.SRC, "-vn", "-ac", "2", "-ar", str(SR),
           "-af", "highpass=f=75,afftdn=nr=6:nf=-45,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2",
           "-f", "f32le", "-"]
    a = np.frombuffer(subprocess.run(cmd, stdout=subprocess.PIPE).stdout, np.float32).reshape(-1, 2).copy()
    n = int(DUR * SR)
    return np.pad(a, ((0, max(0, n - len(a))), (0, 0)))[:n]


def speech_rms(x):
    hop = SR // 50
    m = len(x) // hop
    e = np.sqrt((x[:m * hop, 0].reshape(m, hop) ** 2).mean(1))
    return float(np.percentile(e, 80))


def whoosh(dur, up=0.7, f0=250, f1=5500, pan=0.5):
    """Ruido con filtro que sube hasta el `up` de la duración y luego baja."""
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    bands = [(f0 * (f1 / f0) ** (k / 5), f0 * (f1 / f0) ** ((k + 1) / 5)) for k in range(5)]
    x = np.zeros(n)
    t = np.linspace(0, 1, n)
    env = np.where(t < up, (t / up) ** 2.4, ((1 - t) / (1 - up)) ** 1.6)
    pos = env * 4.0                                  # banda activa según intensidad
    for k, (lo, hi) in enumerate(bands):
        b = sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), noise)
        x += b * np.clip(1 - np.abs(pos - k) / 1.3, 0, 1)
    x *= env
    x /= np.abs(x).max() + 1e-9
    p = 0.5 + pan * (t - up) * 0.9                   # recorre de lado a lado
    return np.stack([x * np.sqrt(1 - np.clip(p, 0, 1)), x * np.sqrt(np.clip(p, 0, 1))], 1)


def thump(dur=0.45, f0=110, f1=42):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = f1 + (f0 - f1) * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.13)
    click = sosfilt(butter(2, 1800, btype="low", fs=SR, output="sos"), rng.standard_normal(n)) * np.exp(-t / 0.008) * 0.5
    x = x + click
    x /= np.abs(x).max()
    return np.stack([x, x], 1)


def add(mix, sig, t, gain):
    i = int(t * SR)
    if i < 0:
        sig = sig[-i:]; i = 0
    j = min(len(mix), i + len(sig))
    if j > i:
        mix[i:j] += sig[:j - i] * gain


voice = load_voice()
c = int(r.T_CUT * SR)
ra, rb = speech_rms(voice[:c]), speech_rms(voice[c:])
print("voz exterior/estudio dB:", round(20 * np.log10(ra), 1), round(20 * np.log10(rb), 1))
ref = (ra + rb) / 2
g = np.ones(len(voice))
g[:c] = ref / ra; g[c:] = ref / rb                    # el corte cae en una pausa de la voz
voice = voice * g[:, None]

sfx = np.zeros_like(voice)
L = ref * 3.2                                         # pico de un efecto fuerte, relativo a la voz
for (t, i) in r.HITS:
    add(sfx, whoosh(0.30, up=0.8, pan=0.4 * (1 if i % 2 else -1)), t - 0.24, L * 0.30)
    add(sfx, thump(), t, L * 0.42)
for e in r.EVENTS:
    if e[6] == "rise":
        add(sfx, whoosh(0.32, up=0.55, f0=500, f1=7000, pan=0.3), e[1] - 0.04, L * 0.20)
# transición central y cierre
add(sfx, whoosh(0.62, up=0.62, f0=180, f1=8000), r.T_CUT - 0.30, L * 0.95)
add(sfx, thump(0.7, 95, 36), r.T_CUT + 0.22, L * 0.75)
add(sfx, whoosh(0.30, up=0.8, f0=300, f1=6000), r.N1 / r.FPS - 0.30, L * 0.55)
add(sfx, whoosh(0.28, up=0.3, f0=300, f1=6000), 0.0, L * 0.30)

mix = (voice + sfx).astype(np.float32)
fade = int(0.08 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))[:, None]
pc = np.clip(mix, -1, 1)
with wave.open("mix.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((pc * 32767).astype(np.int16).tobytes())
print("pico mezcla", round(float(np.abs(mix).max()), 3), "pico voz", round(float(np.abs(voice).max()), 3), "pico fx", round(float(np.abs(sfx).max()), 3))
out = subprocess.run([r.FF, "-hide_banner", "-y", "-i", "mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=summary",
                      "-ar", str(SR), "-c:a", "aac", "-b:a", "192k", "audio.m4a"], capture_output=True, text=True, errors="replace").stderr
print("\n".join(l for l in out.splitlines() if "Integrated" in l or "True Peak" in l))
