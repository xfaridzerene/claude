# -*- coding: utf-8 -*-
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft

def load(path):
    sr, data = wavfile.read(path)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    if data.ndim == 1:
        data = np.stack([data, data], axis=1)
    return sr, data

def rms_db(x):
    r = np.sqrt(np.mean(np.square(x)) + 1e-12)
    return 20 * np.log10(r + 1e-12)

def peak_db(x):
    p = np.max(np.abs(x)) + 1e-12
    return 20 * np.log10(p)

def crest_factor(x):
    return peak_db(x) - rms_db(x)

def spectral_centroid(sig, sr):
    n = len(sig)
    spec = np.abs(np.fft.rfft(sig * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    return np.sum(freqs * spec) / (np.sum(spec) + 1e-12)

def band_energy_db(sig, sr, lo, hi):
    n = len(sig)
    spec = np.abs(np.fft.rfft(sig * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    mask = (freqs >= lo) & (freqs < hi)
    e = np.sum(spec[mask] ** 2)
    return 10 * np.log10(e + 1e-12)

def stereo_correlation(L, R):
    L = L - L.mean()
    R = R - R.mean()
    num = np.sum(L * R)
    den = np.sqrt(np.sum(L ** 2) * np.sum(R ** 2)) + 1e-12
    return num / den

def mid_side_ratio_db(L, R):
    mid = (L + R) / 2
    side = (L - R) / 2
    return rms_db(mid) - rms_db(side)

def analyze(name, path):
    sr, data = load(path)
    L, R = data[:, 0], data[:, 1]
    mono = (L + R) / 2
    dur = len(mono) / sr
    print(f"=== {name} ===")
    print(f"duration: {dur:.2f}s  sr={sr}")
    print(f"RMS: {rms_db(mono):.1f} dBFS   Peak: {peak_db(mono):.1f} dBFS   Crest factor: {crest_factor(mono):.1f} dB")
    print(f"Stereo correlation (L/R): {stereo_correlation(L, R):.3f}  (1.0=mono-identical, 0=decorrelated, <0=out of phase)")
    print(f"Mid/Side ratio: {mid_side_ratio_db(L, R):.1f} dB  (higher = narrower/more mono)")
    print(f"Spectral centroid: {spectral_centroid(mono, sr):.0f} Hz")
    for lo, hi, label in [(20,150,"sub/low"), (150,500,"low-mid"), (500,2000,"mid"), (2000,6000,"presence"), (6000,16000,"high/air")]:
        print(f"  band {label:10s} [{lo:5d}-{hi:5d}Hz]: {band_energy_db(mono, sr, lo, hi):6.1f} dB")

    # short-time RMS envelope (50ms windows) to see compression/limiting behavior
    win = int(0.05 * sr)
    n_wins = len(mono) // win
    env = np.array([rms_db(mono[i*win:(i+1)*win]) for i in range(n_wins)])
    env_voiced = env[env > -55]
    if len(env_voiced):
        print(f"Loudness envelope (voiced, >-55dB): mean={env_voiced.mean():.1f}dB  std={env_voiced.std():.2f}dB  min={env_voiced.min():.1f}  max={env_voiced.max():.1f}")
    return sr, data, mono, env

sr1, d1, m1, env1 = analyze("RAW (frase 17 en bruto)", "raw_frase17.wav")
print()
sr2, d2, m2, env2 = analyze("PRESENTACION (editada)", "presentacion_full.wav")
