#!/usr/bin/env python3
"""Rasterize the official T2S SVG logos (from ./input/assets) to PNG with alpha
using the bundled headless Chrome. No AI-generated art: exact vector render."""
import subprocess, sys, pathlib

WORK = pathlib.Path(__file__).resolve().parent.parent
SRC = WORK / "input" / "assets"
BUILD = WORK / "build"
CHROME = "/home/hermes/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"
PX_W = 1400  # raster width; logo aspect ~2.798

JOBS = [
    ("assets__t2s-logo-dark.svg",  "logo_on_light.png"),  # blue wordmark, for light bg
    ("assets__t2s-logo-light.svg", "logo_on_dark.png"),   # white wordmark, for dark bg
]

def main():
    from PIL import Image
    for svg, out in JOBS:
        html = BUILD / f"_logo_{out}.html"
        html.write_text(
            "<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
            "html,body{margin:0;padding:0;background:transparent}"
            f"img{{width:{PX_W}px;display:block}}"
            "</style></head><body>"
            f"<img src='{(SRC / svg).as_uri()}'>"
            "</body></html>", encoding="utf-8")
        raw = BUILD / f"_logo_{out}.png"
        cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
               f"--default-background-color=00000000", f"--screenshot={raw}",
               f"--window-size={PX_W},{PX_W}", html.as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if not raw.exists():
            print("chrome failed:", r.stderr[-2000:]); sys.exit(1)
        im = Image.open(raw).convert("RGBA")
        bbox = im.split()[3].getbbox()
        im = im.crop(bbox)
        im.save(BUILD / out)
        print(out, im.size, "<- trimmed from", raw.name)

if __name__ == "__main__":
    main()
