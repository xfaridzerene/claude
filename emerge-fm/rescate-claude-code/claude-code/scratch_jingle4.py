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
def pluck(freq, dur, decay=0.9968, damping=0.54, brightness=4200, pick_amp=1.0):
    N = max(4, int(round(SR / freq)))
    buf = np.random.uniform(-1, 1, N).astype(np.float64)
    buf = lp(buf, brightness)
    buf *= pick_amp
    n_samples = int(SR * dur)
    out = np.zeros(n_samples)
    b = buf.tolist()
    idx = 0
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

# ---------- soft acoustic-piano-like tone (plain decay, no tremolo) ----------
def piano_tone(freq, dur, amp=1.0, attack=0.006, decay_rate=1.35):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    sig = np.sin(2 * np.pi * freq * t)
    sig += 0.35 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-1.6 * t)
    sig += 0.15 * np.sin(2 * np.pi * freq * 3.0 * t) * np.exp(-3.2 * t)
    sig += 0.07 * np.sin(2 * np.pi * freq * 4.01 * t) * np.exp(-5.0 * t)
    env = np.exp(-decay_rate * t)
    a_n = max(1, int(SR * attack))
    env[:a_n] *= np.linspace(0, 1, a_n)
    return amp * sig * env

# ---------- soft sustained pad / air ----------
def pad_tone(freq, dur, amp=1.0, attack=1.1, release=1.6):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    sig = 0.5 * np.sin(2 * np.pi * freq * t)
    sig += 0.3 * np.sin(2 * np.pi * freq * 1.003 * t)
    sig += 0.2 * np.sin(2 * np.pi * freq * 0.997 * t)
    env = np.ones(n)
    a_n = min(n, int(SR * attack))
    env[:a_n] = np.linspace(0, 1, a_n) ** 1.5
    r_n = min(n, int(SR * release))
    if r_n > 0:
        env[-r_n:] *= np.linspace(1, 0, r_n) ** 1.5
    return amp * sig * env

# ---------- barely-there warm bass, one soft note per bar ----------
def bass_tone(freq, dur, amp=1.0):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    sig = np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(2 * np.pi * freq * 2 * t)
    sig = lp(sig, 450)
    env = np.ones(n)
    a_n = int(SR * 0.03)
    env[:a_n] = np.linspace(0, 1, a_n)
    r_n = min(n, int(SR * min(1.2, dur * 0.6)))
    if r_n > 0:
        env[-r_n:] *= np.linspace(1, 0, r_n)
    return amp * sig * env

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

# ---------- arrangement: calm guitar + piano bed, very sparse, no percussion ----------
BPM = 70.0
beat = 60.0 / BPM
bar = beat * 4
N_BARS = 4
TOTAL = bar * N_BARS + 2.6
n_total = int(SR * TOTAL)
L = np.zeros(n_total)
R = np.zeros(n_total)

# G - Em - C - D : warm, calm, familiar
chords = [
    ("G", [196.00, 246.94, 293.66, 392.00], 98.00),
    ("Em", [164.81, 196.00, 246.94, 329.63], 82.41),
    ("C", [130.81, 164.81, 196.00, 261.63], 65.41),
    ("D", [146.83, 185.00, 220.00, 293.66], 73.42),
]

for bar_i in range(N_BARS):
    bar_start = bar_i * bar
    name, tones, bass_root = chords[bar_i % len(chords)]
    root, third, fifth, octave = tones

    # soft piano: one gentle chord hit on beat 1, left to ring through the bar
    for f in (root, third, fifth):
        p = piano_tone(f, bar * 1.05, amp=0.11)
        place_mono(L, R, p, bar_start, pan=0.5)

    # faint sustained air under everything, very quiet
    pad = pad_tone(root * 2, bar * 1.0, amp=0.02)
    place_mono(L, R, pad, bar_start, pan=0.5)

    # calm guitar: just 3 unhurried notes per bar (beats 1, 2.5, 3.5), lots of space
    guitar_events = [
        (0.0, root, 0.20),
        (beat * 1.5, fifth, 0.15),
        (beat * 2.5, octave, 0.17),
        (beat * 3.25, third, 0.13),
    ]
    for off, freq, amp in guitar_events:
        gl, gr = clean_guitar_note(freq, beat * 1.6, amp=amp)
        place_stereo(L, R, gl * 0.6, gl * 0.4, bar_start + off)
        place_stereo(L, R, gr * 0.4, gr * 0.6, bar_start + off)

    # one soft, long bass note per bar - just a quiet anchor
    place_mono(L, R, bass_tone(bass_root, beat * 3.6, amp=0.14), bar_start, pan=0.5)

mix = np.stack([L, R], axis=1)
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.85

fade_in_n = int(SR * 0.3)
mix[:fade_in_n] *= np.linspace(0, 1, fade_in_n)[:, None]

fade_out_dur = 2.4
fo_n = int(SR * fade_out_dur)
fade = np.ones(n_total)
fade[-fo_n:] = np.linspace(1, 0, fo_n) ** 1.2
mix *= fade[:, None]

pcm = np.clip(mix, -1, 1)
pcm16 = (pcm * 32767).astype(np.int16)

out_wav = r"C:\Users\farid\Desktop\claude code\jingle_emerge_fm_v4.wav"
wavfile.write(out_wav, SR, pcm16)
print("wrote", out_wav, "duration", TOTAL, "bpm", BPM)
