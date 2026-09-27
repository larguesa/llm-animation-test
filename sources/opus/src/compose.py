#!/usr/bin/env python3
"""compose.py — ORIGINAL programmatic score + SFX for the 30 s T2S spot.
120 BPM (beat = 0.5 s = 15 frames), D minor -> D major resolution. Every sound is synthesized here
(oscillators + noise, see audio_synth.py). No samples, loops or third-party music.
Writes build/music.wav, build/sfx.wav, build/mix.wav, build/audio_events.json"""
import json, os, wave
import numpy as np
from audio_synth import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUR = 30.0; N = int(DUR * SR)
pads, bass, drums, keys, sfx, verb = (np.zeros((2, N)) for _ in range(6))
EV = []
px = lambda x: float(np.clip((x / 1920 * 2 - 1) * 0.65, -1, 1))
def ev(t, kind, note=''): EV.append({'t': round(float(t), 3), 'kind': kind, 'note': note})

# ---------- harmony: (t0, t1, bass midi, pad voicing) ----------
CH = [(0.0, 2.0, 38, [50, 57, 62, 63]),        # D pedal + Eb cluster: controlled tension (scattered demands)
      (2.0, 6.0, 38, [50, 57, 62, 64, 69]),    # Eb resolves to E as cards align (Dsus2)
      (6.0, 8.0, 38, [50, 53, 57, 60, 64]),    # Dm9   — drop / "AI-Native Delivery Pods"
      (8.0, 10.0, 34, [46, 50, 53, 57, 60]),   # Bbmaj9
      (10.0, 12.0, 31, [43, 46, 50, 53, 57]),  # Gm9   — five roles
      (12.0, 14.0, 29, [41, 45, 48, 52, 55]),  # Fmaj9
      (14.0, 16.0, 34, [46, 50, 53, 57, 60]),  # Bbmaj9
      (16.0, 18.0, 38, [50, 53, 57, 60, 64]),  # Dm9   — flow Contexto -> Entrega -> Qualidade
      (18.0, 20.0, 34, [46, 50, 53, 57, 60]),  # Bbmaj9
      (20.0, 22.0, 31, [43, 46, 50, 53, 57]),  # Gm9
      (22.0, 23.0, 33, [45, 50, 52, 55, 59]),  # A7sus4
      (23.0, 24.5, 33, [45, 49, 52, 55, 58]),  # A7(b9) dominant tension
      (24.5, 30.0, 38, [50, 54, 57, 61, 64])]  # Dmaj9 — logo / resolution
def chord(t):
    for c in CH:
        if c[0] <= t < c[1]: return c
    return CH[-1]

for t0, t1, bm, notes in CH:
    last = t0 == 24.5; d = (DUR - t0) if last else (t1 - t0 + 0.8)
    p = supersaw_pad(mtof(notes), d, 0.22 if t0 < 2 else 0.13, 5, int(t0 * 10))
    e = env_adsr(p.shape[1], 1.6 if t0 == 0 else (0.012 if last else 0.05), 0.5, 0.85, 1.5 if last else 0.7, hold=(28.3 - t0) if last else (t1 - t0))
    place(pads, p * e, t0, 0.55)
CUT = [(0, 320), (2, 650), (4.4, 1500), (5.95, 3000), (6.0, 1900), (9.5, 2700), (10.0, 2100), (15.9, 3300), (16.25, 650),
       (17.0, 1700), (22.0, 3200), (24.45, 7500), (24.5, 4600), (27.0, 2500), (30, 1300)]
ct, cv_ = np.array([c[0] for c in CUT]), np.log(np.array([c[1] for c in CUT], float))
fc = lambda tc: np.exp(np.interp(tc, ct, cv_))
for ch in range(2):
    pads[ch] = tv_filter(pads[ch], lambda f, tc: g_lp(f, fc(tc), 0.6) * g_hp(f, 110))

# ---------- drums ----------
KICKS = [(t, 0.45) for t in (2.0, 3.0, 4.0, 5.0)] + [(t, 1.0) for t in np.arange(6.0, 16.0, 0.5)] + \
        [(t, 1.0) for t in np.arange(17.0, 23.5, 0.5)] + [(24.5, 1.25)]
for t, g in KICKS: place(drums, kick(0.5, g), t, 0.85 * g)
for t in list(np.arange(8.5, 16.0, 1.0)) + list(np.arange(17.5, 23.5, 1.0)): place(drums, pan(clap(), 0.05), t, 0.42)
for t in list(np.arange(6.25, 16.0, 0.5)) + list(np.arange(17.25, 23.5, 0.5)): place(drums, pan(hat(), 0.25), t, 0.22)
for t in np.arange(18.125, 23.5, 0.25): place(drums, pan(hat(), -0.3), t, 0.07)
for t in (7.75, 9.75, 11.75, 13.75, 15.75, 19.75, 21.75): place(drums, pan(hat(True), 0.3), t, 0.12)
for k in range(8): place(drums, pan(clap(0.25), (-1) ** k * 0.2), 23.5 + k * 0.125, 0.1 + 0.05 * k)  # roll into the logo
for k, t in enumerate(np.arange(25.25, 27.5, 0.5)): place(drums, pan(hat(), 0.25), t, 0.13 * (1 - k / 5))
crash = lambda d=1.6: fft_filter(RNG.standard_normal(int(d * SR)), lambda f: g_hp(f, 4500) * g_lp(f, 14000)) * env_exp(int(d * SR), 0.5, 0.001) * 0.35
for t, g in ((6.0, 0.6), (17.0, 0.35), (24.5, 0.8)): place(drums, pan(crash(), 0.1), t, g)
sc = np.ones(N)  # sidechain envelope from kicks
for t, g in KICKS:
    i = int(t * SR); seg = 1 - 0.55 * min(g, 1) * np.exp(-np.arange(int(0.45 * SR)) / SR / 0.1)
    j = min(N, i + len(seg)); sc[i:j] = np.minimum(sc[i:j], seg[:j - i])

# ---------- bass ----------
def bassnote(f, d=0.24):
    t = tvec(d); s = saw(f, d) * 0.5 + np.sin(2 * np.pi * f * t) * 0.9 + np.sin(np.pi * f * t) * 0.25
    return fft_filter(s, lambda fr: g_lp(fr, 650, 0.5)) * env_adsr(len(t), 0.004, 0.09, 0.55, 0.06)
for t in np.arange(2.0, 4.5, 0.25): place(bass, bassnote(mtof(38 - 12), 0.2), t, 0.22 + 0.2 * (t - 2) / 2.5)
for t in list(np.arange(6.25, 16.0, 0.5)) + list(np.arange(17.25, 23.5, 0.5)): place(bass, bassnote(mtof(chord(t)[2] - 12 if chord(t)[2] > 35 else chord(t)[2])), t, 0.62)
for t0, t1, bm, _ in CH[2:12]:  # sustained sub under each chord
    if t0 >= 16 and t0 < 17: t0 = 17.0
    d = t1 - t0; tt = tvec(d); f = mtof(bm - 12 if bm > 35 else bm)
    place(bass, np.sin(2 * np.pi * f * tt) * env_adsr(len(tt), 0.02, 0.3, 0.8, 0.08), t0, 0.28)
place(bass, sub_boom(4.0, 70, 36.7), 24.5, 0.9)  # resolution boom (D1)
pads *= sc; bass[:, :] *= sc

# ---------- keys: alignment plucks, arps, role bells, chimes ----------
ORDER = [4, 6, 1, 0, 2, 3, 5, 7, 8]; GX = [660 + (i % 3) * 300 for i in range(9)]
for j, ci in enumerate(ORDER):  # each card snapping into the grid = one note of an ascending Dsus2/9 arpeggio
    t = 2.0 + j * 0.25; n = [62, 64, 69, 74, 76, 81, 86, 88, 93][j]
    place(keys, pan(pluck(mtof(n), 0.7, 0.9), px(GX[ci])), t, 0.2); ev(t, 'card aligns', f'midi {n}')
ARP = [0, 2, 4, 1, 3, 2, 4, 3]
for k, t in enumerate(list(np.arange(10.0, 16.0, 0.25)) + list(np.arange(18.0, 23.5, 0.25))):
    nn = chord(t)[3]; n = nn[ARP[k % 8] % len(nn)] + 12
    place(keys, pan(pluck(mtof(n), 0.35, 0.8), 0.35 * (-1) ** k), t, 0.075 if t < 16 else 0.09)
ROLE = ['Prototyper', 'Builder', 'Sweeper', 'Grower', 'Maintainer']; MID = [300 + i * 330 for i in range(5)]
for i, n in enumerate([81, 84, 86, 88, 89]):
    t = 10.5 + i; place(keys, pan(bell(mtof(n), 1.6), px(MID[i])), t, 0.34); ev(t, 'role appears', ROLE[i])
def chime(t, x, g=0.2, what='checkpoint'):  # "confirmed" dyad A5 -> D6 + click (used for every human checkpoint / check)
    place(sfx, pan(tick(3600, 0.05), px(x)), t, g * 0.7)
    for k, n in enumerate((81, 86)): place(sfx, pan(bell(mtof(n), 0.6, 1.2, 2.0), px(x)), t + 0.06 * k, g)
    ev(t, what)
for i in range(4): chime(11.0 + i + 0.15, (MID[i] + MID[i + 1]) / 2, 0.22, 'human checkpoint')
for k, n in enumerate([74, 77, 81]): place(keys, pan(bell(mtof(n), 1.2, 1.6), px([400, 960, 1520][k])), 17.25 + 0.5 * k, 0.24); ev(17.25 + 0.5 * k, 'flow node', ['Contexto', 'Entrega', 'Qualidade'][k])
for n, g in ((86, 0.3), (90, 0.22), (81, 0.18)): place(keys, bell(mtof(n), 3.0, 1.8), 24.5, g)
place(keys, bell(mtof(81), 1.8, 1.4), 26.0, 0.18)

# ---------- SFX: connections, transitions ----------
R = np.random.default_rng(5); SX = [330, 800, 1480, 240, 1140, 1700, 620, 1330, 940]
for i in range(9): place(sfx, pan(tick(1700 + 1500 * R.random(), 0.05), px(SX[i])), 0.05 + i * 0.07, 0.16)  # scattered demands pop in
place(sfx, pan(whoosh(0.7, 5000, 700, 0.35, 2.5), -0.3), 4.3, 0.25); ev(4.35, 'headline exits')
place(sfx, riser(1.5, 180, 2200), 4.5, 0.35); place(sfx, whoosh(0.8, 400, 4000, 0.55), 4.7, 0.3); ev(5.0, 'cards morph into pod core')
place(sfx, sub_boom(1.8), 6.0, 0.5); ev(6.0, 'DROP: core + title')
for i in range(9):  # spokes connect to the core
    t = 5.9 + i * 0.06 + 0.2; a = -np.pi / 2 + i * 2 * np.pi / 9
    place(sfx, pan(tick(2000 + i * 180, 0.07), px(1330 + np.cos(a) * 205)), t, 0.1)
ev(6.1, 'connections to core')
place(sfx, pan(whoosh(0.55, 4000, 600, 0.4), -0.4), 8.9, 0.22); ev(9.0, 'title exits')
place(sfx, whoosh(0.65, 300, 5000, 0.8), 9.45, 0.34); place(sfx, sub_boom(0.9, 80, 45), 10.0, 0.35); ev(10.0, 'core expands into 5 roles')
for i in range(5): place(sfx, pan(whoosh(0.35, 700, 4500, 0.5, 3), px(MID[i])), 10.5 + i - 0.05, 0.12)
place(sfx, whoosh(0.7, 5000, 400, 0.35), 16.2, 0.28); ev(16.3, 'roles collapse into track')
place(sfx, sub_boom(0.8, 90, 50), 17.05, 0.3); ev(17.05, 'track locks')
for i in range(4):
    a = 18.5 + i * 0.75
    place(sfx, pan(pluck(mtof(93), 0.25, 1.4), px(400)), a, 0.12); ev(a, 'artifact enters', ['Protótipo', 'Incremento de software', 'Teste', 'Revisão'][i])
    for k, x in ((1, 960), (2, 1520)): place(sfx, pan(tick(2600 + 300 * k, 0.05), px(x)), a + 0.75 * k, 0.1)
    chime(a + 1.65, 1600, 0.16, 'artifact verified')
    tt = tvec(0.16); place(sfx, pan(np.sin(2 * np.pi * np.cumsum(140 * np.exp(-tt / 0.05) + 55) / SR) * env_exp(len(tt), 0.05), px([390, 770, 1150, 1530][i])), a + 2.15, 0.3)
tt = tvec(0.6); place(sfx, np.vstack([np.linspace(0.9, 0.3, len(tt)), np.linspace(0.3, 0.9, len(tt))]) * sine_sweep(400 * 4 ** (tt / 0.6)) * np.sin(np.pi * tt / 0.6) * 0.3, 22.4, 0.3); ev(22.4, 'evidence track completes')
place(sfx, whoosh(0.6, 4500, 600, 0.35), 23.45, 0.24)
place(sfx, riser(1.2, 250, 3000), 23.3, 0.35); place(sfx, whoosh(1.0, 800, 9000, 0.98, 1.6), 23.5, 0.3)
for k in range(6): place(sfx, pan(tick(1800 + k * 250, 0.06), 0.3 * (k % 3 - 1)), 24.35 + k * 0.03, 0.1)
ev(24.5, 'RESOLUTION: official logo'); ev(25.5, 'CTA button'); ev(26.0, 't2stech.com')
tt = tvec(0.2); place(sfx, np.sin(2 * np.pi * 95 * tt) * env_exp(len(tt), 0.06), 25.55, 0.3); place(sfx, tick(2800, 0.05), 25.9, 0.1)

# ---------- mix / master ----------
dry = pads * 0.9 + bass * 1.0 + drums * 0.9 + keys * 1.0
wet = reverb(pads * 0.25 + keys * 0.8 + sfx * 0.35 + drums * 0.06, 2.6, 2.2) * 0.5 + pingpong(keys * 0.6, 0.375, 0.4) * 0.5
music = dry + wet; sfxb = sfx * 1.0
mix = music + sfxb
for ch in range(2): mix[ch] = fft_filter(mix[ch], lambda f: g_hp(f, 28))
tt = np.arange(N) / SR; fade = np.where(tt > 28.6, np.cos(np.clip((tt - 28.6) / 1.4, 0, 1) * np.pi / 2) ** 2, 1.0)
fade *= np.clip(tt / 0.01, 0, 1)
def master(x):
    x = x * fade; x = x / (np.max(np.abs(x)) + 1e-9) * 1.25
    x = np.tanh(x) / np.tanh(1.25); return x * 10 ** (-1.0 / 20)
def wav(fn, x):
    x = np.clip(x, -1, 1); d = (x.T * 32767).astype('<i2')
    with wave.open(fn, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
pk = np.max(np.abs(mix * fade)) + 1e-9
wav(os.path.join(ROOT, 'build', 'music.wav'), music * fade / pk)
wav(os.path.join(ROOT, 'build', 'sfx.wav'), sfxb * fade / pk)
wav(os.path.join(ROOT, 'build', 'mix.wav'), master(mix))
json.dump(sorted(EV, key=lambda e: e['t']), open(os.path.join(ROOT, 'build', 'audio_events.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', len(EV), 'events; peak before master', round(float(pk), 3))
