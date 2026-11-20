# -*- coding: utf-8 -*-
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100

def lp(sig, cutoff, order=2):
    b, a = butter(order, cutoff / (SR / 2), btype="low")
    return lfilter(b, a, sig)

# ---------- soft acoustic-piano tone (plain natural decay, no tremolo) ----------
def piano_tone(freq, dur, amp=1.0, attack=0.006, decay_rate=1.1):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    sig = np.sin(2 * np.pi * freq * t)
    sig += 0.35 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-1.4 * t)
    sig += 0.16 * np.sin(2 * np.pi * freq * 3.0 * t) * np.exp(-2.8 * t)
    sig += 0.08 * np.sin(2 * np.pi * freq * 4.01 * t) * np.exp(-4.4 * t)
    sig += 0.04 * np.sin(2 * np.pi * freq * 5.0 * t) * np.exp(-6.0 * t)
    env = np.exp(-decay_rate * t)
    a_n = max(1, int(SR * attack))
    env[:a_n] *= np.linspace(0, 1, a_n)
    return amp * sig * env

def place_stereo(bufL, bufR, sig, start_time, pan=0.5):
    s = int(round(start_time * SR))
    e = s + len(sig)
    for buf, w in ((bufL, 1 - pan), (bufR, pan)):
        if s >= len(buf):
            continue
        seg = sig * w
        ee = e
        if ee > len(buf):
            seg = seg[: len(buf) - s]
            ee = len(buf)
        buf[s:ee] += seg

# ---------- arrangement: solo piano, calm, sparse ----------
BPM = 68.0
beat = 60.0 / BPM
bar = beat * 4
N_BARS = 4
TOTAL = bar * N_BARS + 2.8
n_total = int(SR * TOTAL)
L = np.zeros(n_total)
R = np.zeros(n_total)

# G - Em - C - D : warm, familiar, calm progression
chords = [
    ("G", [196.00, 246.94, 293.66, 392.00], 98.00),    # G3 B3 D4 G4 | low G2
    ("Em", [164.81, 196.00, 246.94, 329.63], 82.41),   # E3 G3 B3 E4 | low E2
    ("C", [130.81, 164.81, 196.00, 261.63], 65.41),    # C3 E3 G3 C4 | low C2
    ("D", [146.83, 185.00, 220.00, 293.66], 73.42),    # D3 F#3 A3 D4 | low D2
]

for bar_i in range(N_BARS):
    bar_start = bar_i * bar
    name, tones, low_root = chords[bar_i % len(chords)]
    root, third, fifth, octave = tones

    # left hand: one soft low note anchoring the bar
    low = piano_tone(low_root, bar * 1.0, amp=0.16, decay_rate=0.9)
    place_stereo(L, R, low, bar_start, pan=0.5)

    # right hand: gentle quarter-note arpeggio, slightly varied each bar for a lullaby feel
    pattern = [root, fifth, octave, third]
    for slot, f in enumerate(pattern):
        amp = 0.22 if slot == 0 else 0.15
        note = piano_tone(f, beat * 2.0, amp=amp, decay_rate=1.05)
        pan = 0.42 if slot % 2 == 0 else 0.58
        place_stereo(L, R, note, bar_start + slot * beat, pan=pan)

    # a soft held top note on the last half of the bar, for a touch of melody
    top = piano_tone(octave * 2, beat * 1.6, amp=0.07, decay_rate=1.3)
    place_stereo(L, R, top, bar_start + beat * 2.5, pan=0.5)

mix = np.stack([L, R], axis=1)
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.85

fade_in_n = int(SR * 0.15)
mix[:fade_in_n] *= np.linspace(0, 1, fade_in_n)[:, None]

fade_out_dur = 2.6
fo_n = int(SR * fade_out_dur)
fade = np.ones(n_total)
fade[-fo_n:] = np.linspace(1, 0, fo_n) ** 1.2
mix *= fade[:, None]

pcm = np.clip(mix, -1, 1)
pcm16 = (pcm * 32767).astype(np.int16)

out_wav = r"C:\Users\farid\Desktop\claude code\jingle_emerge_fm_v5.wav"
wavfile.write(out_wav, SR, pcm16)
print("wrote", out_wav, "duration", TOTAL, "bpm", BPM)
