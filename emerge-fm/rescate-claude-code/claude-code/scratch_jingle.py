# -*- coding: utf-8 -*-
import numpy as np
from scipy.io import wavfile

SR = 44100

def bell(freq, dur, amp=1.0, decay=3.5, inharm=(1.0, 2.0, 2.4, 3.0), inharm_amp=(1.0, 0.45, 0.25, 0.12)):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    sig = np.zeros_like(t)
    for ratio, a in zip(inharm, inharm_amp):
        sig += a * np.sin(2 * np.pi * freq * ratio * t)
    env = np.exp(-decay * t)
    return amp * sig * env

def pad_tone(freq, dur, amp=1.0, attack=0.6, release=1.2, detune_cents=6):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    detune = 2 ** (detune_cents / 1200.0)
    sig = 0.5 * np.sin(2 * np.pi * freq * t)
    sig += 0.3 * np.sin(2 * np.pi * freq * detune * t)
    sig += 0.2 * np.sin(2 * np.pi * freq / detune * t)
    # slow vibrato for warmth
    vibrato = 1.0 + 0.004 * np.sin(2 * np.pi * 4.5 * t)
    sig *= vibrato
    env = np.ones(n)
    a_n = int(SR * attack)
    r_n = int(SR * release)
    env[:a_n] = np.linspace(0, 1, a_n) ** 1.5
    env[-r_n:] = np.linspace(1, 0, r_n) ** 1.5
    return amp * sig * env

def soft_tick(amp=1.0, dur=0.12):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    noise = np.random.uniform(-1, 1, n)
    # bandpass-ish via simple shaping: high freq shimmer
    tone = np.sin(2 * np.pi * 3200 * t) * 0.4
    sig = (noise * 0.6 + tone) * np.exp(-28 * t)
    return amp * sig

def place(buf, sig, start_time):
    s = int(start_time * SR)
    e = s + len(sig)
    if e > len(buf):
        sig = sig[: len(buf) - s]
        e = len(buf)
    buf[s:e] += sig

TOTAL = 14.0
n_total = int(SR * TOTAL)
mix = np.zeros(n_total)

# --- 1. Intro chime / sonic logo (ascending bell arpeggio) ---
notes = [523.25, 659.25, 783.99, 1046.50]  # C5 E5 G5 C6
times = [0.0, 0.16, 0.32, 0.50]
for f, tm in zip(notes, times):
    place(mix, bell(f, 2.2, amp=0.5), tm)

# --- 2. Sustained pad bed (Cmaj9-ish, warm) starts right under the chime tail ---
pad_notes = [130.81, 261.63, 329.63, 392.00, 493.88]  # C3 C4 E4 G4 B4
pad_start = 0.25
pad_dur = TOTAL - pad_start
for f in pad_notes:
    amp = 0.085 if f < 200 else 0.06
    place(mix, pad_tone(f, pad_dur, amp=amp, attack=0.9, release=2.5), pad_start)

# --- 3. Subtle rhythmic pulse (soft ticks), ~100 BPM (every 0.6s), starts after chime ---
beat = 0.6
t0 = 1.4
tt = t0
while tt < TOTAL - 1.5:
    place(mix, soft_tick(amp=0.09), tt)
    tt += beat

# --- Normalize & gentle master fade out ---
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.9

fade_out_dur = 2.0
fo_n = int(SR * fade_out_dur)
fade = np.ones(n_total)
fade[-fo_n:] = np.linspace(1, 0, fo_n)
mix *= fade

stereo = np.stack([mix, mix], axis=1)
pcm = np.clip(stereo, -1, 1)
pcm16 = (pcm * 32767).astype(np.int16)

out_wav = r"C:\Users\farid\Desktop\claude code\jingle_emerge_fm.wav"
wavfile.write(out_wav, SR, pcm16)
print("wrote", out_wav, "duration", TOTAL)
