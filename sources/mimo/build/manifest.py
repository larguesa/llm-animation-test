#!/usr/bin/env python3
"""Generate output/manifest.json — list of sources/artifacts with SHA-256."""
import hashlib
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha(rel):
    h = hashlib.sha256()
    with open(os.path.join(ROOT, rel), "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sz(rel):
    return os.path.getsize(os.path.join(ROOT, rel))


def entry(rel, kind, desc, extra=None):
    e = {"path": rel, "kind": kind, "bytes": sz(rel), "sha256": sha(rel),
         "description": desc}
    if extra:
        e.update(extra)
    return e


manifest = {
    "title": "AI-Native Delivery Pods — motion graphics 30s (T2S Tech)",
    "generated": "2026-09-27",
    "deliverable": {
        "video": entry("output/final.mp4", "video",
                       "MP4 H.264 1920x1080 30fps 30.0s + AAC 48kHz stereo"),
    },
    "intermediate": [
        entry("build/video.mp4", "video", "vídeo sem áudio (saída de build/render.py --full)"),
        entry("build/music.wav", "audio", "trilha instrumental original (48kHz estéreo PCM)"),
        entry("build/logo_on_light.png", "image",
              "logotipo oficial rasterizado (variante escura) via Chrome headless"),
        entry("build/logo_on_dark.png", "image",
              "logotipo oficial rasterizado (variante clara) via Chrome headless"),
    ],
    "sources": [
        entry("build/render.py", "code", "renderizador de motion graphics (Pillow+numpy)"),
        entry("build/music.py", "code", "sintetizador programático da trilha (numpy)"),
        entry("build/rasterize_logos.py", "code", "rasterização SVG->PNG dos logos oficiais"),
        entry("build/manifest.py", "code", "gerador deste manifesto"),
    ],
    "official_inputs_frozen": [
        entry("input/assets/assets__t2s-logo-dark.svg", "brand-asset",
              "logotipo oficial T2S (variante escura) — rasterizado exatamente, sem IA"),
        entry("input/assets/assets__t2s-logo-light.svg", "brand-asset",
              "logotipo oficial T2S (variante clara)"),
        entry("input/assets/_next__static__chunks__23njtp8mlj1pv.css", "brand-asset",
              "CSS oficial do site — origem da paleta e da tipografia"),
        entry("input/t2s-page.html", "brand-asset", "página oficial congelada (HTML)"),
        entry("input/t2s-page-text.txt", "brand-asset", "texto da página oficial congelada"),
    ],
    "fonts": [
        entry("input/fonts/montserrat__Montserrat[wght].ttf", "font",
              "Montserrat variável — licença OFL em input/fonts/montserrat__OFL.txt"),
        entry("input/fonts/rubik__Rubik[wght].ttf", "font",
              "Rubik variável — licença OFL em input/fonts/rubik__OFL.txt"),
        entry("input/fonts/montserrat__OFL.txt", "license", "licença SIL Open Font License (Montserrat)"),
        entry("input/fonts/rubik__OFL.txt", "license", "licença SIL Open Font License (Rubik)"),
    ],
    "audio_license": {
        "file": "output/music-license.md",
        "statement": "composição instrumental original programática (build/music.py); "
                     "sem samples ou gravações de terceiros; nenhuma licença externa alegada",
    },
    "checks": {
        "resolution": "1920x1080",
        "fps": 30,
        "duration_s": 30.0,
        "frames": 900,
        "audio": "AAC 48000 Hz estéreo, max_volume <= -2 dBFS (sem clipping)",
    },
}

out = os.path.join(ROOT, "output", "manifest.json")
with open(out, "w") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print("wrote", out)
