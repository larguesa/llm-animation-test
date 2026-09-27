#!/usr/bin/env python3
"""
Original instrumental score, synthesized programmatically (numpy only).
"AI-Native Delivery Pods" 30s bed: 120 BPM electronic, A-minor.
No samples, no third-party recordings, no external assets. See output/music-license.md.
"""
import numpy as np, wave, pathlib

SR = 48000
DUR = 30.0
N = int(SR * DUR)
BEAT = 0.5          # 120 BPM quarter note
BAR = 2.0           # 4/4

rng = np.random.default_rng(7)
mix = np.zeros((2, N), dtype=np.float64)

# ---------------------------------------------------------------- helpers
def add(sig, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    if i >= N or len(sig) == 0:
        return
    n = min(len(sig), N - i)
    l = gain * np.sqrt(0.5 * (1.0 - pan))
    r = gain * np.sqrt(0.5 * (1.0 + pan))
    mix[0, i:i + n] += sig[:n] * l
    mix[1, i:i + n] += sig[:n] * r

def env(n, a, d, s, r, sus=0.7):
    a, d, r = max(int(a * SR), 1), max(int(d * SR), 1), max(int(r * SR), 1)
    s = max(int(s * SR), 0)
    e = np.zeros(n)
    i = 0
    k = min(a, n); e[i:i + k] = np.linspace(0, 1, k)[:k]; i += k
    if i < n:
        k = min(d, n - i); e[i:i + k] = np.linspace(1, sus, k)[:k]; i += k
    if i < n:
        k = min(s, n - i); e[i:i + k] = sus; i += k
    if i < n:
        k = n - i; e[i:i + k] = np.linspace(sus, 0, k)[:k]
    return e

def dexp(n, tau):
    return np.exp(-np.arange(n) / (SR * tau))

def fftconv(x, k):
    L = len(x) + len(k) - 1
    n = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(k, n), n)[:L]
    return y

def fir_lp(cut, taps=255):
    m = (taps - 1) / 2
    k = np.arange(taps) - m
    h = np.sinc(2 * cut / SR * k) * np.hamming(taps)
    return h / h.sum()

def fir_hp(cut, taps=255):
    d = np.zeros(taps); d[taps // 2] = 1.0
    return d - fir_lp(cut, taps)

def saw(f, n, detune=0.0):
    ph = (np.arange(n) * (f * (1 + detune)) / SR) % 1.0
    # band-limited-ish saw: harmonic sum
    out = np.zeros(n)
    h = 1
    while f * (1 + detune) * h < 12000 and h <= 14:
        out += np.sin(2 * np.pi * f * (1 + detune) * h * np.arange(n) / SR) / h
        h += 1
    return out * 0.6

def sq(f, n):
    out = np.zeros(n)
    h = 1
    while f * h < 12000 and h <= 11:
        out += np.sin(2 * np.pi * f * h * np.arange(n) / SR) / h
        h += 2
    return out * 0.7

def note(name):
    names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6,
             'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    n, o = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[n] + (o - 4) * 12 - 9) / 12)

# ---------------------------------------------------------------- drums
def kick(gain=1.0):
    n = int(0.35 * SR)
    e = dexp(n, 0.085)
    f = 120 * np.exp(-np.arange(n) / (SR * 0.018)) + 44
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * e
    click = rng.normal(0, 1, int(0.004 * SR))
    click *= np.linspace(1, 0, len(click)) ** 2
    out = body
    out[:len(click)] += click * 0.35
    return out * gain

def clap(gain=1.0):
    n = int(0.24 * SR)
    nz = rng.normal(0, 1, n)
    nz = fftconv(nz, fir_lp(2600) - fir_lp(700))[:n]
    e = dexp(n, 0.055)
    out = nz * e
    for off, g in ((0, 1), (0.010, 0.8), (0.019, 0.6)):
        i = int(off * SR)
        seg = rng.normal(0, 1, int(0.012 * SR)) * np.linspace(1, 0, int(0.012 * SR)) ** 2
        out[i:i + len(seg)] += fftconv(seg, fir_lp(3000) - fir_lp(900))[:len(seg)] * g
    return out * gain

def hat(open_=False, gain=1.0):
    tau = 0.045 if not open_ else 0.16
    n = int((0.08 if not open_ else 0.35) * SR)
    nz = rng.normal(0, 1, n)
    nz = fftconv(nz, fir_hp(7200))[:n]
    return nz * dexp(n, tau) * gain

def crash(gain=1.0):
    n = int(1.8 * SR)
    nz = rng.normal(0, 1, n)
    nz = fftconv(nz, fir_lp(11000) - fir_lp(2400))[:n]
    e = np.minimum(1, np.arange(n) / (0.004 * SR)) * dexp(n, 0.55)
    return nz * e * gain

def impact(gain=1.0):
    n = int(1.2 * SR)
    f = 90 * np.exp(-np.arange(n) / (SR * 0.05)) + 36
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * dexp(n, 0.28)
    nz = rng.normal(0, 1, n) * dexp(n, 0.05) * 0.25
    return (sub + nz) * gain

# ---------------------------------------------------------------- tonal
def pad(chord, dur, gain=1.0):
    n = int((dur + 0.9) * SR)
    out = np.zeros(n)
    for f in chord:
        for det in (-0.006, 0.0, 0.006):
            out += saw(f, n, det)
    out = fftconv(out, fir_lp(1500))[:n]
    e = env(n, 0.55, 0.4, max(dur - 1.4, 0.1), 0.9, sus=0.75)
    return out * e * gain / max(len(chord) * 2.4, 1)

def bassnote(f, dur, gain=1.0):
    n = int((dur + 0.06) * SR)
    s = 0.7 * np.sin(2 * np.pi * f * np.arange(n) / SR) + 0.35 * sq(f, n)
    s = fftconv(s, fir_lp(420))[:n]
    return s * env(n, 0.006, 0.05, max(dur - 0.11, 0.02), 0.05, sus=0.7) * gain

def pluck(f, dur, gain=1.0, bright=2400):
    n = int((dur + 0.25) * SR)
    s = 0.55 * sq(f, n) + 0.45 * np.sin(2 * np.pi * f * np.arange(n) / SR)
    s = fftconv(s, fir_lp(bright))[:n]
    return s * dexp(n, 0.075) * env(n, 0.003, 0.02, max(dur - 0.05, 0.01), 0.2, sus=0.5) * gain

def lead(f, dur, gain=1.0):
    n = int((dur + 0.3) * SR)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * np.arange(n) / SR)
    s = 0.6 * saw(f, n) + 0.4 * np.sin(2 * np.pi * f * np.arange(n) / SR * vib)
    s = fftconv(s, fir_lp(3200))[:n]
    return s * env(n, 0.02, 0.12, max(dur - 0.2, 0.05), 0.18, sus=0.65) * gain

# ---------------------------------------------------------------- sfx
def whoosh(dur=0.55, gain=1.0, down=True):
    n = int(dur * SR)
    nz = rng.normal(0, 1, n)
    a = fftconv(nz, fir_lp(4500) - fir_lp(1200))[:n]
    b = fftconv(nz, fir_hp(2500))[:n]
    x = np.linspace(0, 1, n)
    cross = x if down else 1 - x
    s = a * (1 - cross) + b * cross
    e = np.sin(np.pi * x) ** 1.5
    return s * e * gain

def tick(gain=1.0):
    n = int(0.05 * SR)
    s = np.sin(2 * np.pi * 2100 * np.arange(n) / SR) * dexp(n, 0.008)
    s += rng.normal(0, 1, n) * dexp(n, 0.003) * 0.4
    return s * gain

def blip(f0=880, gain=1.0):
    n = int(0.09 * SR)
    f = np.linspace(f0, f0 * 1.6, n)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * dexp(n, 0.03)
    return s * gain

def riser(dur=1.0, gain=1.0):
    n = int(dur * SR)
    x = np.linspace(0, 1, n)
    nz = rng.normal(0, 1, n)
    lp = fftconv(nz, fir_lp(400 + 5200))[:n]
    s = lp * (x ** 2.2)
    f = 300 + 900 * x ** 2
    s += 0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR) * (x ** 3)
    return s * gain

# ---------------------------------------------------------------- score
# chord map (A minor world). one chord per 2s bar
Am9 = [note('A3'), note('C4'), note('E4'), note('B4')]
Fm9 = [note('F3'), note('A3'), note('C4'), note('E4')]      # Fmaj9-ish
Cm9 = [note('C4'), note('E4'), note('G4'), note('D5')]      # Cmaj9
Em7 = [note('E3'), note('G3'), note('B3'), note('D4')]
Am9L = [note('A2'), note('E3'), note('A3'), note('C4'), note('E4')]
CHORDS = [Am9, Am9, Fm9, Fm9, Cm9, Cm9, Em7, Em7,
          Am9, Am9, Fm9, Fm9, Cm9, Em7, Am9L]
ROOTS = ['A1', 'A1', 'F1', 'F1', 'C2', 'C2', 'E1', 'E1',
         'A1', 'A1', 'F1', 'F1', 'C2', 'E1', 'A1']

# pads (whole piece)
for b, ch in enumerate(CHORDS):
    t0 = b * BAR
    g = 0.5
    if t0 < 4: g = 0.42
    if 24 <= t0 < 27: g = 0.55
    if t0 >= 27: g = 0.6
    p = pad(ch, BAR, gain=0.34 * g / 0.5)
    add(p, t0, pan=-0.25, gain=0.6)
    add(p, t0, pan=0.25, gain=0.6)

# intro arps (2.0-5.0) then full arp 5.0-24.0
def arp_bar(t0, ch, oct_=0, gain=0.2, step=0.25):
    seq = [ch[0], ch[1], ch[2], ch[3], ch[2], ch[1], ch[2], ch[3]]
    for i, f in enumerate(seq):
        tt = t0 + i * step
        if tt >= DUR: break
        add(pluck(f * 2 ** oct_, step * 0.9, gain=gain), tt,
            pan=-0.35 + 0.7 * ((i % 4) / 3), gain=1.0)

for b in range(1, 15):
    t0 = b * BAR
    ch = CHORDS[b]
    if 2.0 <= t0 < 5.0:
        arp_bar(t0, ch, 0, gain=0.13)
    if 5.0 <= t0 < 24.0:
        arp_bar(t0, ch, 0, gain=0.16)
    if 17.0 <= t0 < 24.0:
        arp_bar(t0, ch, 1, gain=0.075, step=0.25)
    if 24.0 <= t0 < 27.0:
        arp_bar(t0, ch, 1, gain=0.07)

# bass: enters at 5.0 (with the first transition), out after 24.0 (roots only under drop)
for b in range(15):
    t0 = b * BAR
    f = note(ROOTS[b])
    if 5.0 <= t0 < 24.0:
        for i, off in enumerate([0.0, 0.75, 1.0, 1.5]):
            tt = t0 + off
            if tt >= 24.0 or tt < 5.0: continue
            add(bassnote(f, 0.42, gain=0.5), tt)
    if 24.0 <= t0 < 27.0:
        add(bassnote(f, 0.9, gain=0.4), t0)

# drums: four-on-floor 5.0-24.0, thin out 24.0-27.0, final hit 27.0
def drums():
    t = 5.0
    while t < 24.0:
        add(kick(0.95), t)
        t += BEAT
    t = 5.5
    while t < 24.0:
        add(clap(0.42), t, pan=0.05)
        t += 1.0
    t = 5.0
    while t < 24.0:
        add(hat(False, 0.16), t, pan=0.18)
        add(hat(False, 0.10), t + 0.25, pan=-0.2)
        t += 0.5
    for tt in (15.5, 19.5, 23.5):
        add(hat(True, 0.14), tt, pan=0.3)
    # fills into 10.0 and 17.0 and 24.0
    for tt in np.arange(16.5, 17.0, 0.125):
        add(hat(False, 0.12), tt, pan=0.0)
    for tt in np.arange(23.5, 24.0, 0.125):
        add(hat(False, 0.13), tt, pan=0.0)
    for tt in np.arange(9.5, 10.0, 0.25):
        add(clap(0.18), tt, pan=0.0)
    # drop
    for tt in (24.0, 25.0, 26.0):
        add(kick(0.85), tt)
    add(kick(1.0), 27.0)
    add(crash(0.32), 27.0, pan=0.0)
    add(crash(0.3), 5.0, pan=0.1)
    add(crash(0.22), 10.0, pan=-0.1)
    add(crash(0.22), 17.0, pan=0.12)
    add(crash(0.26), 24.0, pan=-0.08)
drums()

# impacts on scene changes
for tt in (5.0, 10.0, 17.0, 24.0, 27.0):
    add(impact(0.75), tt)

# lead motif (from 10.0)
MOTIF = [  # (t, note, dur)
    (10.0, 'E5', 0.5), (10.5, 'D5', 0.5), (11.0, 'C5', 0.75), (12.0, 'A4', 0.5),
    (12.5, 'C5', 0.5), (13.0, 'D5', 1.0), (14.0, 'E5', 0.5), (14.5, 'G5', 0.75),
    (15.5, 'E5', 0.5), (16.0, 'D5', 1.0),
    (17.5, 'A4', 0.5), (18.0, 'C5', 0.5), (18.5, 'E5', 1.0), (19.5, 'D5', 0.5),
    (20.0, 'C5', 0.75), (21.0, 'A4', 0.5), (21.5, 'G4', 0.5), (22.0, 'A4', 2.0),
    (24.5, 'E5', 0.75), (25.5, 'C5', 0.75), (26.5, 'A4', 1.0),
    (27.0, 'A5', 3.0), (27.0, 'E5', 3.0),
]
for tt, nm, d in MOTIF:
    add(lead(note(nm), d, gain=0.2), tt, pan=0.08)

# sfx layer (discrete, low)
for tt in (4.55, 9.55, 16.55, 23.5):
    add(whoosh(0.5, 0.16), tt, pan=0.0)
for i, tt in enumerate([4.0, 4.15, 4.3, 4.45, 4.6]):
    add(blip(760 + 60 * i, 0.12), tt, pan=-0.3 + 0.15 * i)
for tt in (12.4, 12.9, 13.4, 13.9):
    add(tick(0.22), tt, pan=0.1)
for tt in (19.8, 20.6, 21.4, 22.2):
    add(tick(0.2), tt, pan=-0.12)
add(blip(520, 0.16), 25.2, pan=0.0)          # logo pop
add(riser(1.0, 0.1), 4.0, pan=0.0)
add(riser(0.8, 0.08), 23.2, pan=0.0)

# ---------------------------------------------------------------- mix
# gentle sidechain pump under the groove
tt = np.arange(N) / SR
duck = np.ones(N)
m = (tt >= 5.0) & (tt < 24.0)
duck[m] = 1 - 0.28 * np.exp(-((tt[m] % BEAT) / 0.11))
duck[(tt >= 24.0) & (tt < 27.0)] = 1 - 0.15 * np.exp(-(((tt[(tt >= 24.0) & (tt < 27.0)]) % 1.0) / 0.13))
mix *= duck

# simple plate reverb via convolution with decaying noise (fft)
ir_n = int(1.1 * SR)
ir = rng.normal(0, 1, ir_n) * np.exp(-np.arange(ir_n) / (SR * 0.28))
ir[:int(0.012 * SR)] = 0
ir = fftconv(ir, fir_lp(5500))[:ir_n]
ir /= np.abs(ir).max() * 26
wet = np.stack([fftconv(mix[0], ir)[:N], fftconv(mix[1], ir * 0.95)[:N]])
mix = mix * 0.9 + wet * 0.55

# fades + master
fi = int(0.35 * SR)
mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(1.3 * SR)
mix[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
mix = np.tanh(mix * 1.25) * 0.82
mix /= max(np.abs(mix).max() / 0.92, 1e-9)

out = pathlib.Path(__file__).resolve().parent.parent / "build" / "music.wav"
data = (np.clip(mix.T, -1, 1) * 32767).astype('<i2')
with wave.open(str(out), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(data.tobytes())
print("wrote", out, data.shape, "peak", np.abs(mix).max())
