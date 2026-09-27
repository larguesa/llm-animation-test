#!/usr/bin/env python3
"""Render driver: serves ./ over localhost, drives headless Chromium (Playwright) to draw
each frame on a 1920x1080 canvas (src/index.html) and pipes PNG frames into ffmpeg.
Usage:
  render.py preview T1 T2 ...     -> build/preview/*.png + build/preview/sheet.png (single-sample frames)
  render.py full [N_SUB]          -> build/video.mp4 (900 frames, temporal supersampling N_SUB, default 4)
"""
import base64, functools, http.server, io, os, subprocess, sys, threading, time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = '/home/hermes/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome'
FPS, NFRAMES = 30, 900


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    h.log_message = lambda *a, **k: None
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def open_page(p, port):
    b = p.chromium.launch(executable_path=CHROME, headless=True,
                          args=['--disable-gpu', '--force-color-profile=srgb', '--font-render-hinting=none',
                                '--disable-lcd-text', '--renderer-process-limit=1'])
    pg = b.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: m.type in ('error', 'warning') and errs.append(m.text))
    pg.goto(f'http://127.0.0.1:{port}/src/index.html')
    ok = pg.evaluate('() => window.ready')
    if not ok:
        raise SystemExit('FONTS NOT LOADED')
    return b, pg, errs


def png_bytes(url):
    return base64.b64decode(url.split(',', 1)[1])


def preview(ts):
    from PIL import Image, ImageDraw
    out = os.path.join(ROOT, 'build', 'preview'); os.makedirs(out, exist_ok=True)
    srv = serve()
    with sync_playwright() as p:
        b, pg, errs = open_page(p, srv.server_address[1])
        thumbs = []
        for t in ts:
            u = pg.evaluate("t => { renderAt(t); return document.getElementById('c').toDataURL('image/png'); }", t)
            fn = os.path.join(out, f't_{t:06.2f}.png'); open(fn, 'wb').write(png_bytes(u)); thumbs.append((t, fn))
        b.close()
    if errs: print('PAGE ERRORS:', errs[:10])
    cols = 3; tw_, th_ = 640, 360; rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw_, rows * (th_ + 24)), (0, 0, 0)); d = ImageDraw.Draw(sheet)
    for i, (t, fn) in enumerate(thumbs):
        im = Image.open(fn).convert('RGB').resize((tw_, th_), Image.LANCZOS)
        x, y = (i % cols) * tw_, (i // cols) * (th_ + 24); sheet.paste(im, (x, y + 24)); d.text((x + 6, y + 5), f't={t:.2f}s', fill=(255, 255, 0))
    sheet.save(os.path.join(out, 'sheet.png')); print('sheet', os.path.join(out, 'sheet.png'), len(thumbs))


def full(nsub):
    os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
    dst = os.path.join(ROOT, 'build', 'video.mp4')
    ff = subprocess.Popen(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS),
                           '-c:v', 'png', '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
                           '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-tune', 'animation', '-threads', '1',
                           '-x264-params', 'threads=1:lookahead-threads=1', '-colorspace', 'bt709', '-color_primaries', 'bt709',
                           '-color_trc', 'bt709', '-r', str(FPS), '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
    srv = serve(); t0 = time.time()
    with sync_playwright() as p:
        b, pg, errs = open_page(p, srv.server_address[1])
        for f in range(NFRAMES):
            u = pg.evaluate('([f, n]) => renderFrame(f, n, 0.5)', [f, nsub])
            ff.stdin.write(png_bytes(u))
            if f % 60 == 0: print(f'frame {f}/{NFRAMES} {time.time() - t0:.0f}s', flush=True)
        b.close()
    ff.stdin.close(); rc = ff.wait()
    if errs: print('PAGE ERRORS:', errs[:10])
    print('done rc', rc, f'{time.time() - t0:.0f}s', dst)


if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        preview([float(x) for x in sys.argv[2:]])
    else:
        full(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
