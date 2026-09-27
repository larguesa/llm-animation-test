#!/usr/bin/env python3
"""audio_synth.py — tiny numpy synth/DSP toolkit (original programmatic composition, no samples).
All sounds are generated from oscillators and noise; nothing is sampled or downloaded."""
import numpy as np

SR = 48000
RNG = np.random.default_rng(20260927)


def mtof(m):
    return 440.0 * 2 ** ((np.asarray(m, float) - 69) / 12)


def tvec(dur):
    return np.arange(int(dur * SR)) / SR


def polyblep(ph, dt):
    y = np.zeros_like(ph); dt = np.broadcast_to(dt, ph.shape)
    m = ph < dt; x = ph[m] / dt[m]; y[m] = x + x - x * x - 1
    m = ph > 1 - dt; x = (ph[m] - 1) / dt[m]; y[m] = x * x + x + x + 1
    return y


def saw(freq, dur, phase0=0.0):
    f = np.broadcast_to(np.asarray(freq, float), (int(dur * SR),)) if np.ndim(freq) == 0 else np.asarray(freq, float)
    ph = (phase0 + np.cumsum(f) / SR) % 1.0
    return 2 * ph - 1 - polyblep(ph, f / SR)


def sine_sweep(f, n=None):
    f = np.asarray(f, float)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def env_exp(n, tau, attack=0.002):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / tau)


def env_adsr(n, a, d, s, r, hold=None):
    """hold = time at which release starts (defaults to n - r)"""
    t = np.arange(n) / SR
    hold = (n / SR - r) if hold is None else hold
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip(1 - (t - hold) / max(r, 1e-4), 0, 1) ** 2
    return e * np.where(t > hold, rel, 1.0)


# ---------------- filters (zero-phase, frequency domain) ----------------
def g_lp(f, fc, q=0.0):
    g = 1 / np.sqrt(1 + (f / fc) ** 4)
    if q:
        g = g * (1 + q * np.exp(-(np.log2(np.maximum(f, 1) / fc) ** 2) / (2 * 0.18 ** 2)))
    return g


def g_hp(f, fc):
    return 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** 4)


def fft_filter(x, gain_fn):
    n = len(x); m = 1 << int(np.ceil(np.log2(n + 1)))
    X = np.fft.rfft(x, m); f = np.fft.rfftfreq(m, 1 / SR)
    return np.fft.irfft(X * gain_fn(f), m)[:n]


def tv_filter(x, gain_fn, bs=2048):
    """time-varying filter: gain_fn(f[None,:], t[:,None]) -> (blocks, bins); 50% OLA of periodic Hann"""
    hop = bs // 2; n = len(x)
    pad = np.concatenate([np.zeros(hop), x, np.zeros(bs)])
    nb = (len(pad) - bs) // hop + 1
    win = np.hanning(bs + 1)[:-1]
    idx = np.arange(bs)[None, :] + hop * np.arange(nb)[:, None]
    F = np.fft.rfft(pad[idx] * win, axis=1)
    f = np.fft.rfftfreq(bs, 1 / SR)
    tc = (np.arange(nb) * hop + bs / 2 - hop) / SR
    y = np.fft.irfft(F * gain_fn(f[None, :], tc[:, None]), n=bs, axis=1)
    out = np.zeros(len(pad))
    for i in range(nb):
        out[i * hop:i * hop + bs] += y[i]
    return out[hop:hop + n]


# ---------------- instruments (mono unless noted) ----------------
def kick(dur=0.5, punch=1.0):
    t = tvec(dur); f = 44 + 120 * np.exp(-t / 0.032) + 30 * np.exp(-t / 0.004)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
    click = fft_filter(RNG.standard_normal(len(t)) * np.exp(-t / 0.0025), lambda f: g_hp(f, 2500)) * 0.35
    return np.tanh(1.6 * punch * (body + click)) * 0.9


def clap(dur=0.45):
    t = tvec(dur); n = RNG.standard_normal(len(t))
    e = sum(np.where(t >= o, np.exp(-(t - o) / 0.008), 0) for o in (0, 0.011, 0.022)) * 0.6 + np.where(t >= 0.03, np.exp(-(t - 0.03) / 0.13), 0)
    s = fft_filter(n * e, lambda f: g_hp(f, 900) * g_lp(f, 7000, 0.8))
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.045) * 0.3
    return (s + tone) * 0.8


def hat(open_=False):
    dur = 0.35 if open_ else 0.08; t = tvec(dur)
    s = fft_filter(RNG.standard_normal(len(t)), lambda f: g_hp(f, 7500) * g_lp(f, 15000))
    return s * np.exp(-t / (0.09 if open_ else 0.018)) * 0.5


def pluck(freq, dur=0.6, bright=1.0, tau0=0.55):
    t = tvec(dur); y = np.zeros(len(t))
    for k in range(1, 26):
        fk = freq * k * (1 + 0.0004 * k * k)
        if fk > 16000: break
        y += np.sin(2 * np.pi * fk * t + k) / k ** (1.25 / bright) * np.exp(-t * (1 + 0.55 * k) / tau0)
    return y * np.clip(t / 0.002, 0, 1) * 0.5


def bell(freq, dur=1.6, idx=2.4, ratio=3.0):
    t = tvec(dur); I = idx * np.exp(-t / 0.18)
    y = np.sin(2 * np.pi * freq * t + I * np.sin(2 * np.pi * freq * ratio * t))
    y += 0.25 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t / 0.25)
    return y * env_exp(len(t), 0.55, 0.001) * 0.35


def tick(freq=2400, dur=0.06):
    t = tvec(dur)
    return (np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.012) + 0.25 * RNG.standard_normal(len(t)) * np.exp(-t / 0.002)) * 0.3


def sub_boom(dur=2.2, f0=62, f1=38):
    t = tvec(dur); f = f1 + (f0 - f1) * np.exp(-t / 0.25)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(len(t), 0.75, 0.004) * 0.9


def whoosh(dur=0.8, f0=300, f1=5000, peak=0.6, q=2.5):
    """band-passed noise sweeping f0->f1; envelope peaks at `peak` fraction of dur"""
    t = tvec(dur); n = RNG.standard_normal(len(t))
    def gf(f, tc):
        u = np.clip(tc / dur, 0, 1); fc = f0 * (f1 / f0) ** u
        return np.exp(-(np.log2(np.maximum(f, 1) / fc) ** 2) / (2 * (1 / q) ** 2))
    y = tv_filter(n, gf, 1024)
    u = t / dur; e = np.where(u < peak, (u / peak) ** 2.2, np.exp(-(u - peak) / (1 - peak) * 4.0))
    return y * e * 0.5


def riser(dur=1.0, f0=200, f1=2400):
    t = tvec(dur); u = t / dur
    tone = saw(f0 * (f1 / f0) ** u, dur) * 0.15 + saw(f0 * 1.007 * (f1 / f0) ** u, dur) * 0.15
    tone = tv_filter(tone, lambda f, tc: g_lp(f, 300 + 5000 * np.clip(tc / dur, 0, 1) ** 2, 1.5), 1024)
    return (tone + whoosh(dur, 500, 9000, 0.97, 1.5) * 0.8) * u ** 2.5


def supersaw_pad(freqs, dur, detune=0.12, voices=5, seed=0):
    """stereo detuned-saw chord (returns 2xN)"""
    r = np.random.default_rng(seed); n = int(dur * SR); out = np.zeros((2, n))
    for fr in freqs:
        for v in range(voices):
            c = (v - (voices - 1) / 2) / ((voices - 1) / 2) * detune  # semitones
            s = saw(fr * 2 ** (c / 12), dur, r.random())
            p = 0.5 + 0.45 * (v - (voices - 1) / 2) / ((voices - 1) / 2)
            out[0] += s * np.cos(p * np.pi / 2); out[1] += s * np.sin(p * np.pi / 2)
    return out / (len(freqs) * voices) ** 0.5


def pan(x, p):  # p in [-1, 1]
    a = (p + 1) * np.pi / 4
    return np.vstack([x * np.cos(a), x * np.sin(a)])


def place(buf, sig, t, gain=1.0):
    """add mono (N) or stereo (2,N) sig into stereo buf at time t"""
    i = int(round(t * SR))
    if sig.ndim == 1: sig = np.vstack([sig, sig]) * 0.7071
    j = min(buf.shape[1], i + sig.shape[1])
    if j > i >= 0: buf[:, i:j] += sig[:, :j - i] * gain


def reverb(x, length=2.4, decay=0.9, damp=5500, seed=3, predelay=0.018):
    """stereo convolution reverb with synthetic decaying-noise IR; x is 2xN"""
    r = np.random.default_rng(seed); n = int(length * SR); t = np.arange(n) / SR
    out = np.zeros_like(x)
    for ch in range(2):
        ir = r.standard_normal(n) * np.exp(-t / (decay / 6.9 * 2.3))
        ir = fft_filter(ir, lambda f: g_lp(f, damp) * g_hp(f, 160))
        ir = np.concatenate([np.zeros(int(predelay * SR)), ir]); ir /= np.sqrt(np.sum(ir ** 2))
        m = 1 << int(np.ceil(np.log2(x.shape[1] + len(ir))))
        out[ch] = np.fft.irfft(np.fft.rfft(x[ch], m) * np.fft.rfft(ir, m), m)[:x.shape[1]]
    return out


def pingpong(x, d, fb=0.42, taps=6, damp=4000):
    """stereo ping-pong delay of 2xN signal; returns wet"""
    n = x.shape[1]; k = int(d * SR); w = np.zeros_like(x); m = (x[0] + x[1]) * 0.5
    m = fft_filter(m, lambda f: g_lp(f, damp) * g_hp(f, 250))
    for i in range(1, taps + 1):
        if i * k >= n: break
        ch = i % 2; w[ch, i * k:] += m[:n - i * k] * fb ** i
    return w
