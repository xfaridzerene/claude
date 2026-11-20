# -*- coding: utf-8 -*-
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100

def lp(sig, cutoff, order=2):
    b, a = butter(order, cutoff / (SR / 2), btype="low")
    return lfilter(b, a, sig)

def hp(sig, cutoff, order=2):
    b, a = butter(order, cutoff / (SR / 2), btype="high")
    return lfilter(b, a, sig)

# ---------- Karplus-Strong plucked "clean electric guitar" string ----------
def pluck(freq, dur, decay=0.9965, damping=0.52, brightness=4500, pick_amp=1.0):
    N = max(4, int(round(SR / freq)))
    buf = np.random.uniform(-1, 1, N).astype(np.float64)
    buf = lp(buf, brightness)  # softens the initial pick noise -> "clean" tone, not harsh
    buf *= pick_amp
    n_samples = int(SR * dur)
    out = np.zeros(n_samples)
    b = buf.tolist()
    idx = 0
    prev = b[(idx - 1) % N]
    for i in range(n_samples):
        cur = b[idx]
        out[i] = cur
        nxt = b[(idx + 1) % N]
        avg = (damping * cur + (1 - damping) * nxt) * decay
        b[idx] = avg
        idx = (idx + 1) % N
    return out

def clean_guitar_note(freq, dur, amp=1.0, detune_cents=4):
    d = 2 ** (detune_cents / 1200.0)
    left = pluck(freq / d, dur)
    right = pluck(freq * d, dur)
    return amp * left, amp * right

# ---------- soft sustained pad (warm strings) ----------
def pad_tone(freq, dur, amp=1.0, attack=0.9, release=1.4):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    sig = 0.5 * np.sin(2 * np.pi * freq * t)
    sig += 0.3 * np.sin(2 * np.pi * freq * 1.003 * t)
    sig += 0.2 * np.sin(2 * np.pi * freq * 0.997 * t)
    vibrato = 1.0 + 0.003 * np.sin(2 * np.pi * 4.0 * t)
    sig *= vibrato
    env = np.ones(n)
    a_n = min(n, int(SR * attack))
    env[:a_n] = np.linspace(0, 1, a_n) ** 1.5
    r_n = min(n, int(SR * release))
    if r_n > 0:
        env[-r_n:] *= np.linspace(1, 0, r_n) ** 1.5
    return amp * sig * env

# ---------- understated bass ----------
def bass_tone(freq, dur, amp=1.0):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    sig = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 2 * t)
    sig = lp(sig, 500)
    env = np.ones(n)
    a_n = int(SR * 0.02)
    env[:a_n] = np.linspace(0, 1, a_n)
    r_n = int(SR * min(0.6, dur * 0.5))
    if r_n > 0:
        env[-r_n:] *= np.linspace(1, 0, r_n)
    return amp * sig * env

# ---------- barely-there brushed shaker, just for a bit of radio warmth ----------
def soft_shaker(amp=1.0):
    dur = 0.07
    n = int(SR * dur)
    noise = np.random.uniform(-1, 1, n)
    noise = hp(noise, 4000)
    t = np.linspace(0, dur, n, endpoint=False)
    env = np.exp(-22 * t)
    return amp * noise * env

def place_stereo(bufL, bufR, sigL, sigR, start_time):
    s = int(round(start_time * SR))
    for buf, sig in ((bufL, sigL), (bufR, sigR)):
        e = s + len(sig)
        if s >= len(buf):
            continue
        seg = sig
        ee = e
        if ee > len(buf):
            seg = sig[: len(buf) - s]
            ee = len(buf)
        buf[s:ee] += seg

def place_mono(bufL, bufR, sig, start_time, pan=0.5):
    place_stereo(bufL, bufR, sig * (1 - pan), sig * pan, start_time)

# ---------- arrangement: warm 80s/90s AOR radio ballad, clean guitar lead ----------
BPM = 82.0
beat = 60.0 / BPM
eighth = beat / 2.0
bar = beat * 4
N_BARS = 4
TOTAL = bar * N_BARS + 2.4
n_total = int(SR * TOTAL)
L = np.zeros(n_total)
R = np.zeros(n_total)

# G - Em - C - D, classic warm pop-ballad progression
chords = [
    ("G", [196.00, 246.94, 293.66, 392.00], 98.00),   # G3 B3 D4 G4 | bass G2
    ("Em", [164.81, 196.00, 246.94, 329.63], 82.41),  # E3 G3 B3 E4 | bass E2
    ("C", [130.81, 164.81, 196.00, 261.63], 65.41),   # C3 E3 G3 C4 | bass C2
    ("D", [146.83, 185.00, 220.00, 293.66], 73.42),   # D3 F#3 A3 D4 | bass D2
]

# fingerpicked arpeggio pattern across 8 eighth-notes per bar (indices into chord tones)
# tones = [root, third, fifth, octave] -> pattern gives a flowing travis-picking feel
pattern = [0, 2, 3, 1, 2, 3, 1, 2]

for bar_i in range(N_BARS):
    bar_start = bar_i * bar
    name, tones, bass_root = chords[bar_i % len(chords)]

    # soft pad holds the chord underneath (very low, just for sustain/warmth)
    for f in tones:
        pad = pad_tone(f, bar * 1.0, amp=0.035)
        place_mono(L, R, pad, bar_start, pan=0.5)

    # understated bass, root on beat 1, fifth-ish lift on beat 3 for gentle motion
    place_mono(L, R, bass_tone(bass_root, beat * 1.8, amp=0.22), bar_start, pan=0.5)
    place_mono(L, R, bass_tone(bass_root, beat * 1.8, amp=0.16), bar_start + beat * 2, pan=0.5)

    # clean electric guitar arpeggio, fingerpicked 8th notes
    for slot in range(8):
        tone_idx = pattern[slot]
        freq = tones[tone_idx]
        amp = 0.34 if slot == 0 else 0.24
        gl, gr = clean_guitar_note(freq, eighth * 1.9, amp=amp)
        place_stereo(L, R, gl * 0.65, gl * 0.35, bar_start + slot * eighth)   # slight left bias
        place_stereo(L, R, gr * 0.35, gr * 0.65, bar_start + slot * eighth)  # slight right bias

    # barely-there shaker on the backbeat only (2 & 4) to keep it "casi de fondo"
    place_mono(L, R, soft_shaker(amp=0.05), bar_start + beat * 1, pan=0.5)
    place_mono(L, R, soft_shaker(amp=0.05), bar_start + beat * 3, pan=0.5)

mix = np.stack([L, R], axis=1)
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.9

fade_in_n = int(SR * 0.08)
mix[:fade_in_n] *= np.linspace(0, 1, fade_in_n)[:, None]

fade_out_dur = 2.2
fo_n = int(SR * fade_out_dur)
fade = np.ones(n_total)
fade[-fo_n:] = np.linspace(1, 0, fo_n) ** 1.2
mix *= fade[:, None]

pcm = np.clip(mix, -1, 1)
pcm16 = (pcm * 32767).astype(np.int16)

out_wav = r"C:\Users\farid\Desktop\claude code\jingle_emerge_fm_v3.wav"
wavfile.write(out_wav, SR, pcm16)
print("wrote", out_wav, "duration", TOTAL, "bpm", BPM)
