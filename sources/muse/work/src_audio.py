#!/usr/bin/env python3
"""Original programmatic instrumental + SFX for the T2S AI-Native Delivery Pods video.

30.0 s, stereo 48 kHz. Every sound is synthesized in this file with numpy:
no samples, no loops, no third-party material. See output/music-license.md.

Structure (120 BPM, beat = 0.5 s):
  0-5   intro: pad + soft pulse, sparse plucks, groove enters ~4 s
  5-10  main groove A (kick/clap/hats/bass + motif A)
  10-17 groove B (arp + 5 role accent hits + checkpoint chimes)
  17-24 rolling flow groove, gate ticks, riser into 24
  24-30 resolve: impact, warm half-time groove, soft landing, tail to 30.0
"""
import wave
import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
BEAT = 0.5
rng = np.random.default_rng(7)

L = np.zeros(N, dtype=np.float64)
R = np.zeros(N, dtype=np.float64)


def place(x, t0, gain=1.0, pan=0.0):
    """Mix mono array x into the stereo master at time t0 (constant-power pan)."""
    if x is None or len(x) == 0:
        return
    i0 = int(round(t0 * SR))
    seg = np.asarray(x, dtype=np.float64) * gain
    if i0 < 0:
        seg = seg[-i0:]
        i0 = 0
    if i0 >= N or len(seg) == 0:
        return
    i1 = min(N, i0 + len(seg))
    seg = seg[: i1 - i0]
    a = (pan + 1.0) * np.pi / 4.0
    gl, gr = np.cos(a), np.sin(a)
    L[i0:i1] += seg * gl
    R[i0:i1] += seg * gr


def place_stereo(xl, xr, t0, gain=1.0):
    i0 = int(round(t0 * SR))
    xl = np.asarray(xl, dtype=np.float64) * gain
    xr = np.asarray(xr, dtype=np.float64) * gain
    if i0 < 0:
        xl, xr = xl[-i0:], xr[-i0:]
        i0 = 0
    if i0 >= N or len(xl) == 0:
        return
    i1 = min(N, i0 + len(xl))
    L[i0:i1] += xl[: i1 - i0]
    R[i0:i1] += xr[: i1 - i0]


def fft_filter(x, fn):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    return np.fft.irfft(X * fn(f), len(x))


def lowpass(x, fc, order=2):
    return fft_filter(x, lambda f: 1.0 / np.sqrt(1.0 + (f / max(fc, 1.0)) ** (2 * order) + 1e-9))


def highpass(x, fc, order=2):
    return fft_filter(x, lambda f: 1.0 / np.sqrt(1.0 + (max(fc, 1.0) / np.maximum(f, 1.0)) ** (2 * order) + 1e-9))


def bandpass(x, f0, f1):
    return fft_filter(x, lambda f: np.exp(-0.5 * ((np.log(np.maximum(f, 1.0)) - np.log(np.sqrt(f0 * f1))) / 0.9) ** 2))


def space(x, dt=0.27, fb=0.32, taps=4, pan_flip=True):
    """Cheap stereo ambience: decaying delayed taps, alternating pan."""
    n = len(x)
    xl = x.copy()
    xr = x.copy()
    for k in range(1, taps + 1):
        d = int(SR * dt * k)
        if d >= n:
            break
        g = fb ** k
        if pan_flip and (k % 2 == 1):
            xr[d:] += x[: n - d] * g
            xl[d:] += x[: n - d] * g * 0.3
        else:
            xl[d:] += x[: n - d] * g
            xr[d:] += x[: n - d] * g * 0.3
    return xl, xr


# ---------------- instruments ----------------
def kick(dur=0.45, f0=160.0, f1=48.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.018)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.10)
    click = rng.standard_normal(n) * np.exp(-t / 0.004) * 0.4
    click = np.diff(click, prepend=0.0)
    return (body + click).astype(np.float64)


def hat(dur=0.05, open_=False):
    n = int(SR * (0.22 if open_ else dur))
    t = np.arange(n) / SR
    x = rng.standard_normal(n) * np.exp(-t / (0.09 if open_ else 0.014))
    return highpass(x, 7200).astype(np.float64)


def clap(dur=0.22):
    n = int(SR * dur)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for dt in (0.0, 0.012, 0.024):
        i = int(SR * dt)
        burst = rng.standard_normal(n - i) * np.exp(-(t[: n - i]) / 0.05)
        x[i:] += burst
    return bandpass(x, 1400, 3200).astype(np.float64)


def shaker(dur=0.03):
    n = int(SR * dur)
    t = np.arange(n) / SR
    return highpass(rng.standard_normal(n) * np.exp(-t / 0.008), 6000)


def tone(midi, dur=0.6, bright=0.6, decay=3.2, det_cents=0.0):
    f = 440.0 * 2 ** ((midi - 69) / 12) * 2 ** (det_cents / 1200)
    n = int(SR * dur)
    t = np.arange(n) / SR
    x = np.zeros(n)
    amps = [1.0, 0.45 * bright + 0.12, 0.22 * bright + 0.05, 0.10 * bright + 0.02]
    for k, a in enumerate(amps, start=1):
        x += a * np.sin(2 * np.pi * f * k * t + 0.05 * k) * np.exp(-t * decay * (0.65 + 0.45 * k))
    x *= 1.0 - np.exp(-t / 0.003)
    return x


def bass_note(midi, dur=0.25):
    f = 440.0 * 2 ** ((midi - 69) / 12)
    n = int(SR * dur)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.05)
    env = (1.0 - np.exp(-t / 0.006)) * np.exp(-t / (dur * 0.9))
    return (x * env * 0.9).astype(np.float64)


def pad_chord(midis, dur=2.4):
    n = int(SR * dur)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in midis:
        f = 440.0 * 2 ** ((m - 69) / 12)
        for det in (-5.0, 4.0):
            fd = f * 2 ** (det / 1200)
            s = np.zeros(n)
            for k in range(1, 7):
                s += np.sin(2 * np.pi * fd * k * t + 0.02 * k) / k
            x += s * 0.10
    a, r = int(SR * 0.45), int(SR * 0.6)
    env = np.ones(n)
    env[:a] = np.linspace(0, 1, a) ** 1.5
    env[-r:] = np.linspace(1, 0, r) ** 1.2
    return lowpass(x * env, 1050)


def noise_swell(dur, f0=500, f1=4500, up=True):
    n = int(SR * dur)
    t = np.linspace(0, 1, n)
    x = rng.standard_normal(n)
    lo = lowpass(x, f0 * 2)
    hi = highpass(x, f1 / 3)
    env = t ** 1.6 if up else (1 - t) ** 1.6
    mix = lo * (1 - env) + hi * env
    amp = np.sin(np.pi * np.clip(t, 0, 1)) ** 1.2 if not up else (t ** 2)
    return (mix * amp * 2.2).astype(np.float64)


def chirp(f0, f1, dur):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (t / dur) ** 1.5
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.linspace(0, 1, n) ** 1.5 * 0.5).astype(np.float64)


def impact():
    n = int(SR * 1.6)
    t = np.arange(n) / SR
    f = 30 + 45 * np.exp(-t / 0.06)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    crash = highpass(rng.standard_normal(n) * np.exp(-t / 0.5), 2800) * 0.8
    sub = np.sin(2 * np.pi * 55 * t) * np.exp(-t / 0.5) * 0.5
    return (boom + crash + sub).astype(np.float64)


def tom(midi=55, dur=0.35):
    f = 440.0 * 2 ** ((midi - 69) / 12)
    n = int(SR * dur)
    t = np.arange(n) / SR
    sweep = f * (1 + 0.8 * np.exp(-t / 0.03))
    body = np.sin(2 * np.pi * np.cumsum(sweep) / SR) * np.exp(-t / 0.12)
    nz = lowpass(rng.standard_normal(n) * np.exp(-t / 0.03), 2500) * 0.4
    return (body + nz).astype(np.float64)


def chime(midis, dur=1.4):
    n = int(SR * dur)
    x = np.zeros(n)
    for i, m in enumerate(midis):
        p = tone(m, dur=dur, bright=0.8, decay=4.5)
        d = int(SR * 0.14 * i)
        x[d:] += p[: n - d] * (0.8 ** i)
    return x


def tick(f=1250.0):
    n = int(SR * 0.09)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012)
    x += rng.standard_normal(n) * np.exp(-t / 0.003) * 0.25
    return highpass(x, 900)


def blip(f0, f1, dur=0.14):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (t / dur)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.05) * 0.7).astype(np.float64)


# ---------------- arrangement ----------------
AM = [57, 60, 64, 67, 71]
F = [53, 57, 60, 65, 69]
C = [55, 60, 64, 67, 72]
G = [55, 59, 62, 67, 74]
DM = [57, 62, 65, 69, 72]
PROG = [  # (t0, chord, bass_root)
    (0.0, AM, 33), (2.0, F, 29), (4.0, C, 36), (6.0, G, 31),
    (8.0, AM, 33), (10.0, F, 29), (12.0, C, 36), (14.0, G, 31),
    (16.0, AM, 33), (18.0, F, 29), (20.0, C, 36), (22.0, G, 31),
    (24.0, AM, 33), (26.0, F, 29), (28.0, AM, 33),
]

for t0, chord, root in PROG:
    dur = 2.5 if t0 < 28 else 2.1
    p = pad_chord(chord, dur=dur)
    xl, xr = space(p, dt=0.31, fb=0.25, taps=3)
    place_stereo(xl, xr, t0 - 0.05, gain=0.5)

# intro soft kicks + shakers
for tk in (0.0, 2.0):
    place(kick(), tk, gain=0.5)
for i in range(int(4.0 / 0.25)):
    place(shaker(), i * 0.25, gain=0.10 if i % 2 else 0.16, pan=0.3 if i % 2 else -0.3)

# intro sparse plucks
for tp, nn, g in ((1.0, 69, 0.22), (2.0, 72, 0.24), (3.0, 71, 0.20), (3.5, 67, 0.16)):
    xl, xr = space(tone(nn, 0.9, bright=0.7, decay=4.0), dt=0.29, fb=0.3, taps=3)
    place_stereo(xl, xr, tp, gain=g)

# main drums 4-24
t = 4.0
while t < 24.0 - 1e-6:
    place(kick(), t, gain=0.95)
    t += BEAT
t = 4.5
while t < 24.0 - 1e-6:
    place(clap(), t, gain=0.5, pan=0.05)
    t += 1.0
t = 4.0
while t < 24.0 - 1e-6:
    on_beat = abs((t / BEAT) - round(t / BEAT)) < 1e-6
    place(hat(), t, gain=0.22 if on_beat else 0.13, pan=-0.25 if on_beat else 0.25)
    t += 0.25
t = 10.5  # open hats offbeat 10-17
while t < 17.0 - 1e-6:
    place(hat(open_=True), t, gain=0.16, pan=0.2)
    t += 1.0
t = 22.0  # 16th build 22-24
while t < 24.0 - 1e-6:
    place(hat(), t, gain=0.10 + 0.10 * (t - 22.0) / 2.0, pan=(t * 7) % 0.6 - 0.3)
    t += 0.125

# bass
BASS_PAT = [0, 0, 0, 12, 0, 0, 7, 12]
for t0, chord, root in PROG:
    if t0 < 4.0 - 1e-6:
        place(bass_note(root, 1.6), t0, gain=0.4)
    elif t0 < 24.0 - 1e-6:
        for k, off in enumerate(BASS_PAT):
            place(bass_note(root + off, 0.24), t0 + k * 0.25, gain=0.5)
    elif t0 < 28.0 - 1e-6:
        place(bass_note(root, 0.9), t0, gain=0.5)
        place(bass_note(root, 0.9), t0 + 1.0, gain=0.4)

# motif A 5-10
MOTIF_A = [69, 72, 76, 74, 72, 69, 67, 69, 72, 74]
for k, nn in enumerate(MOTIF_A):
    xl, xr = space(tone(nn, 0.55, bright=0.7, decay=4.2), dt=0.26, fb=0.3, taps=3)
    place_stereo(xl, xr, 5.0 + k * 0.5, gain=0.30)

# arp B 10-17 (chord tones, two octaves)
for t0, chord, root in PROG:
    if 10.0 - 1e-6 <= t0 < 16.0:
        seq = [chord[1] + 12, chord[2] + 12, chord[3] + 12, chord[4] + 12,
               chord[3] + 24, chord[2] + 24, chord[1] + 24, chord[0] + 24]
        for k, nn in enumerate(seq):
            place(tone(nn, 0.3, bright=0.75, decay=6.0), t0 + k * 0.25,
                  gain=0.20, pan=0.35 if k % 2 else -0.35)

# rolling line 17-24
ROLL = [69, 67, 65, 67, 69, 72, 71, 69, 67, 65, 64, 65, 67, 69, 71, 72]
for k, nn in enumerate(ROLL[:14]):
    place(tone(nn, 0.45, bright=0.65, decay=4.0), 17.0 + k * 0.5, gain=0.26,
          pan=0.15 if k % 2 else -0.15)

# role accent hits (visual reveals at 10.5, 11.5, ... 14.5)
for i, th in enumerate((10.5, 11.5, 12.5, 13.5, 14.5)):
    place(tom(55 - i, 0.4), th, gain=0.65)
    place(blip(880 + i * 130, 1320 + i * 160, 0.22), th + 0.02, gain=0.28,
          pan=0.3 if i % 2 else -0.3)

# checkpoint chimes (visual badges at 15.4, 15.8, 16.2)
for tc in (15.4, 15.8, 16.2):
    xl, xr = space(chime([76, 83], 1.0), dt=0.3, fb=0.3, taps=2)
    place_stereo(xl, xr, tc, gain=0.20)

# S2 connection blips
for tb, f0 in ((6.0, 880), (6.5, 990), (7.0, 1174), (7.5, 1318)):
    place(blip(f0, f0 * 1.3, 0.12), tb, gain=0.12, pan=-0.2)

# S4 gate ticks (artifact mid-passes at 19.9, 20.6, 21.3, 22.0)
for tg in (19.9, 20.6, 21.3, 22.0):
    place(tick(), tg, gain=0.22, pan=0.15)

# transition whooshes
for tw, dd in ((4.6, 0.7), (9.7, 0.6), (16.7, 0.6), (23.4, 0.7)):
    w = noise_swell(dd, up=True)
    place(w, tw, gain=0.35)
    place(w[::-1] * 0.4, tw + dd * 0.4, gain=0.2)

# riser + resolve
place(noise_swell(1.4, f0=600, f1=6000, up=True), 22.6, gain=0.5)
place(chirp(220, 1760, 1.35), 22.6, gain=0.35)
place(impact(), 24.0, gain=1.0)

# resolve half-time drums 24-28
for tk in (24.0, 25.0, 26.0, 27.0):
    if tk > 24.0:
        place(kick(), tk, gain=0.85)
    place(shaker(), tk + 0.5, gain=0.14, pan=0.2)
for tc in (24.5, 25.5, 26.5):
    place(clap(), tc, gain=0.35, pan=0.05)

# resolve motif 24-28 + final stab 28
for tp, nn, dd, g in ((24.2, 69, 1.4, 0.30), (25.2, 67, 1.2, 0.28),
                      (26.2, 64, 1.6, 0.30), (27.4, 76, 1.2, 0.16)):
    xl, xr = space(tone(nn, dd, bright=0.6, decay=3.0), dt=0.32, fb=0.32, taps=4)
    place_stereo(xl, xr, tp, gain=g)
stab = np.zeros(int(SR * 2.0))
for nn in (57, 60, 64, 69):
    stab += tone(nn, 2.0, bright=0.5, decay=2.2)
xl, xr = space(stab * 0.4, dt=0.34, fb=0.3, taps=4)
place_stereo(xl, xr, 28.0, gain=0.5)
place(blip(1568, 2093, 0.5), 27.0, gain=0.10)  # resolve shimmer

# sidechain pump on the full mix driven by main kicks (subtle glue)
mix = np.stack([L, R])
env = np.ones(N)
tk = 4.0
kicks = []
while tk < 24.0 - 1e-6:
    kicks.append(tk)
    tk += BEAT
kicks += [25.0, 26.0, 27.0]
tt = np.arange(N) / SR
for kt in kicks:
    m = tt >= kt
    env[m] *= 1.0 - 0.30 * np.exp(-(tt[m] - kt) / 0.14)
mix *= env

# master: gentle fade edges, true-peak-safe ceiling, normalize to -3 dBFS
# (correction v2: v1 peaked at 1.217 float after AAC decode -> keep headroom)
fade_in = min(int(SR * 0.05), N)
mix[:, :fade_in] *= np.linspace(0, 1, fade_in)
fo = int(SR * 0.6)
mix[:, -fo:] *= np.linspace(1, 0, fo) ** 0.7
mix = np.tanh(mix * 1.1) * 0.85
peak = max(np.abs(mix).max(), 1e-6)
mix *= 0.562 / peak  # -5 dBFS sample peak -> AAC true peak stays < 1.0

with wave.open("work/audio_mix.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1).T.reshape(-1) * 32767).astype(np.int16).tobytes())
print("wrote work/audio_mix.wav", mix.shape, "peak=%.6f" % float(np.abs(mix).max()))
