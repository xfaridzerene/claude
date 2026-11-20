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

def bp(sig, low, high, order=2):
    b, a = butter(order, [low / (SR / 2), high / (SR / 2)], btype="band")
    return lfilter(b, a, sig)

# ---------- warm electric-piano chord tone (Rhodes-ish) ----------
def ep_tone(freq, dur, amp=1.0, attack=0.02, release=0.35, tremolo_rate=5.0, tremolo_depth=0.12):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    sig = np.sin(2 * np.pi * freq * t)
    sig += 0.25 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-2.0 * t)
    sig += 0.12 * np.sin(2 * np.pi * freq * 4.0 * t) * np.exp(-4.0 * t)
    trem = 1.0 - tremolo_depth + tremolo_depth * np.sin(2 * np.pi * tremolo_rate * t)
    sig *= trem
    env = np.exp(-1.1 * t)
    a_n = max(1, int(SR * attack))
    env[:a_n] *= np.linspace(0, 1, a_n)
    r_n = max(1, int(SR * release))
    if r_n < n:
        env[-r_n:] *= np.linspace(1, 0, r_n)
    return amp * sig * env

# ---------- warm analog bass ----------
def bass_tone(freq, dur, amp=1.0):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    saw_ish = 2 * (t * freq - np.floor(t * freq + 0.5))  # crude triangle via sawtooth-like
    tri = 0.6 * np.sin(2 * np.pi * freq * t) + 0.4 * saw_ish
    sig = np.tanh(tri * 1.6)
    env = np.ones(n)
    a_n = int(SR * 0.01)
    env[:a_n] = np.linspace(0, 1, a_n)
    r_n = int(SR * min(0.08, dur * 0.3))
    if r_n > 0:
        env[-r_n:] *= np.linspace(1, 0, r_n)
    sig = lp(sig, 900)
    return amp * sig * env

# ---------- friendly mid-register lead (not bell-like) ----------
def lead_tone(freq, dur, amp=1.0):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    vibrato = 1.0 + 0.006 * np.sin(2 * np.pi * 5.0 * t)
    sig = 0.55 * np.sin(2 * np.pi * freq * vibrato * t)
    sig += 0.35 * (2 * (t * freq - np.floor(t * freq + 0.5)))  # soft triangle-ish layer
    sig = lp(sig, 2600)
    env = np.ones(n)
    a_n = int(SR * 0.04)
    env[:a_n] = np.linspace(0, 1, a_n) ** 1.3
    r_n = int(SR * min(0.25, dur * 0.4))
    if r_n > 0:
        env[-r_n:] *= np.linspace(1, 0, r_n) ** 1.3
    return amp * sig * env

# ---------- drums ----------
def kick(amp=1.0):
    dur = 0.22
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    f0, f1 = 130, 45
    freq = f1 + (f0 - f1) * np.exp(-28 * t)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    sig = np.sin(phase)
    env = np.exp(-16 * t)
    sig = lp(sig, 220)
    return amp * sig * env

def snare(amp=1.0):
    dur = 0.18
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    noise = np.random.uniform(-1, 1, n)
    noise = bp(noise, 800, 6000)
    tone = np.sin(2 * np.pi * 180 * t) * 0.5
    env = np.exp(-20 * t)
    sig = (noise * 0.75 + tone) * env
    return amp * sig

def hihat(amp=1.0, open_=False):
    dur = 0.16 if open_ else 0.06
    n = int(SR * dur)
    noise = np.random.uniform(-1, 1, n)
    noise = hp(noise, 7000)
    t = np.linspace(0, dur, n, endpoint=False)
    env = np.exp(-(10 if open_ else 35) * t)
    return amp * noise * env

def place(buf, sig, start_time):
    s = int(round(start_time * SR))
    e = s + len(sig)
    if s >= len(buf):
        return
    if e > len(buf):
        sig = sig[: len(buf) - s]
        e = len(buf)
    buf[s:e] += sig

# ---------- arrangement ----------
BPM = 108.0
beat = 60.0 / BPM
eighth = beat / 2.0
bar = beat * 4
N_BARS = 6
TOTAL = bar * N_BARS + 2.2  # tail for fade/decay
n_total = int(SR * TOTAL)
mix = np.zeros(n_total)

# chord per bar: alternate Fmaj9 / Cmaj9 (warm I-IV shuttle)
F_CHORD = [174.61, 220.00, 261.63, 329.63]   # F3 A3 C4 E4
C_CHORD = [130.81, 261.63, 329.63, 392.00]   # C3 C4 E4 G4
bass_F, bass_C = 87.31, 65.41                # F2, C2

for bar_i in range(N_BARS):
    bar_start = bar_i * bar
    chord = F_CHORD if bar_i % 2 == 0 else C_CHORD
    bass_root = bass_F if bar_i % 2 == 0 else bass_C

    # EP chord stab on beat 1, held
    for f in chord:
        place(mix, ep_tone(f, bar * 0.95, amp=0.075), bar_start + 0.01)

    # syncopated bass groove: root on 1, fifth/octave push on the "and of 2"
    place(mix, bass_tone(bass_root, beat * 0.9, amp=0.5), bar_start)
    place(mix, bass_tone(bass_root * 2, eighth * 0.9, amp=0.3), bar_start + beat * 1.5)
    place(mix, bass_tone(bass_root, beat * 0.9, amp=0.45), bar_start + beat * 2.0)
    place(mix, bass_tone(bass_root * 1.5, eighth * 0.9, amp=0.28), bar_start + beat * 3.5)

    # drums: kick on 1 & 3 (+ pushed 8th before next bar), snare on 2 & 4, hats on every 8th
    place(mix, kick(amp=0.9), bar_start + 0 * eighth)
    place(mix, kick(amp=0.8), bar_start + 4 * eighth)
    place(mix, kick(amp=0.55), bar_start + 7 * eighth)
    place(mix, snare(amp=0.55), bar_start + 2 * eighth)
    place(mix, snare(amp=0.55), bar_start + 6 * eighth)
    for slot in range(8):
        is_offbeat = slot % 2 == 1
        place(mix, hihat(amp=0.16 if not is_offbeat else 0.22, open_=(slot == 7)), bar_start + slot * eighth)

    # friendly lead hook every other bar (mid register, warm, not piercing)
    if bar_i % 2 == 1:
        hook = [(293.66, 0), (349.23, eighth * 2), (392.00, eighth * 4), (349.23, eighth * 6)]  # D4 F4 G4 F4
        for f, off in hook:
            place(mix, lead_tone(f, eighth * 1.8, amp=0.14), bar_start + off)

# gentle intro swell: fade whole mix in over first 0.3s, fade out tail
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.92

fade_in_n = int(SR * 0.05)
mix[:fade_in_n] *= np.linspace(0, 1, fade_in_n)

fade_out_dur = 1.8
fo_n = int(SR * fade_out_dur)
fade = np.ones(n_total)
fade[-fo_n:] = np.linspace(1, 0, fo_n) ** 1.2
mix *= fade

stereo = np.stack([mix, mix], axis=1)
pcm = np.clip(stereo, -1, 1)
pcm16 = (pcm * 32767).astype(np.int16)

out_wav = r"C:\Users\farid\Desktop\claude code\jingle_emerge_fm_v2.wav"
wavfile.write(out_wav, SR, pcm16)
print("wrote", out_wav, "duration", TOTAL, "bpm", BPM)
