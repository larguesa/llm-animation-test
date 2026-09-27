#!/usr/bin/env python3
"""finalize.py — objective QA of output/final.mp4, contact sheets taken from the real MP4, output/manifest.json."""
import datetime, glob, hashlib, json, os, re, shutil, subprocess, sys
from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'output'); QA = os.path.join(OUT, 'qa'); MP4 = os.path.join(OUT, 'final.mp4')
TMP = os.path.join(ROOT, 'build', 'qa_final'); os.makedirs(QA, exist_ok=True); os.makedirs(TMP, exist_ok=True)
CHROME = '/home/hermes/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome'
rel = lambda p: os.path.relpath(p, ROOT)
run = lambda cmd: subprocess.run(cmd, capture_output=True, text=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def frame(t, name):
    fn = os.path.join(TMP, name); run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', MP4, '-frames:v', '1', fn])
    return Image.open(fn).convert('RGB')


pr = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', MP4]).stdout)
v = next(s for s in pr['streams'] if s['codec_type'] == 'video'); a = next(s for s in pr['streams'] if s['codec_type'] == 'audio')
dec = run(['ffmpeg', '-v', 'error', '-i', MP4, '-f', 'null', '-'])
eb = run(['ffmpeg', '-hide_banner', '-nostats', '-i', MP4, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
lufs = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', eb)[-1]); tpk = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', eb)[-1])

T = [0.5, 2.0, 4.2, 5.3, 6.5, 8.5, 10.8, 12.5, 14.5, 16.0, 17.0, 18.0, 19.5, 22.0, 23.3, 24.8, 26.0, 29.5]
ims = [(t, frame(t, f'f_{t:05.2f}.png')) for t in T]
for part in range(2):
    sh = Image.new('RGB', (3 * 640, 3 * 380), (0, 0, 0)); d = ImageDraw.Draw(sh)
    for k, (t, im) in enumerate(ims[part * 9:(part + 1) * 9]):
        x, y = (k % 3) * 640, (k // 3) * 380
        sh.paste(im.resize((640, 360), Image.LANCZOS), (x, y + 20)); d.text((x + 6, y + 4), f'final.mp4 t={t:.2f}s', fill=(255, 220, 0))
    sh.save(os.path.join(QA, f'contact_sheet_{part + 1}.jpg'), quality=85)
ims[-1][1].save(os.path.join(QA, 'end_card_t29.5.png'))
box = (300, 240, 1620, 900)  # logo + title + CTA + URL region
hold = ImageStat.Stat(ImageChops.difference(frame(26.8, 'hold_a.png').crop(box), frame(29.8, 'hold_b.png').crop(box)).convert('L')).mean[0]

qa = {'decodes_without_errors': dec.returncode == 0 and not dec.stderr.strip(), 'video_codec': v['codec_name'], 'width': v['width'],
      'height': v['height'], 'fps': v['r_frame_rate'], 'nb_frames': int(v.get('nb_frames', 0)), 'pix_fmt': v['pix_fmt'],
      'container_duration_s': float(pr['format']['duration']), 'video_duration_s': float(v['duration']),
      'audio_codec': a['codec_name'], 'audio_sample_rate': int(a['sample_rate']), 'audio_channels': a['channels'],
      'audio_duration_s': float(a['duration']), 'integrated_loudness_lufs': lufs, 'true_peak_dbfs': tpk,
      'end_card_hold_mean_abs_pixel_diff_26.8s_vs_29.8s': round(hold, 3),
      'speech': 'none — no voice, TTS or vocal samples; every sound is synthesized in src/compose.py'}
shutil.copy(os.path.join(ROOT, 'build', 'audio_events.json'), os.path.join(OUT, 'audio_events.json'))

ROLE = {'src/index.html': 'page shell: loads the official fonts and scene scripts onto a 1920x1080 canvas',
        'src/logo.js': 'official T2S logo vector paths, extracted verbatim from input/assets/assets__t2s-logo-light.svg',
        'src/lib.js': 'brand tokens from the site CSS :root, easing, kinetic-type masks, specialist/agent/checkpoint glyphs',
        'src/scene1.js': '0-10 s: scattered demands -> aligned grid -> connected pod core; service title',
        'src/scene2.js': '10-17 s: five roles with visual actions + human checkpoints between them',
        'src/scene3.js': '17-24.5 s: Contexto -> Entrega -> Qualidade flow, travelling artifacts, evidence row',
        'src/main.js': 'site-hero background/grid, end card (official logo + title + CTA + URL), motion-blur frame renderer',
        'src/render.py': 'headless Chromium frame renderer piping PNG frames into ffmpeg/libx264',
        'src/audio_synth.py': 'numpy synthesis/DSP toolkit (oscillators, noise, filters, reverb, delay)',
        'src/compose.py': 'original programmatic score + SFX (120 BPM) and audio event log',
        'src/build.sh': 'one-command reproduction: compose -> render -> mux -> finalize',
        'src/finalize.py': 'objective QA, contact sheets from final.mp4, this manifest'}
USE = {'input/assets/assets__t2s-logo-light.svg': 'official logo (dark-background version), drawn from its exact vector paths',
       'input/assets/_next__static__chunks__23njtp8mlj1pv.css': 'palette (:root tokens), letter-spacing, eyebrow/button/check-list/signal-grid/hero styles',
       'input/fonts/montserrat__Montserrat[wght].ttf': 'headline/eyebrow/button typeface (as on the site), SIL OFL 1.1',
       'input/fonts/rubik__Rubik[wght].ttf': 'body/caption typeface (as on the site), SIL OFL 1.1',
       'input/fonts/montserrat__OFL.txt': 'font license', 'input/fonts/rubik__OFL.txt': 'font license',
       'input/t2s-page-text.txt': 'copy source (service name, roles, human checkpoints, Context/Delivery/Quality, CTA)',
       'input/t2s-page.html': 'page structure reference (eyebrow, check-list, service-detail rows, buttons)'}
man = {'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
       'deliverable': {'path': rel(MP4), 'sha256': sha(MP4), 'bytes': os.path.getsize(MP4), 'qa': qa},
       'outputs': [{'path': rel(p), 'sha256': sha(p)} for p in sorted(glob.glob(os.path.join(OUT, '**', '*'), recursive=True))
                   if os.path.isfile(p) and not p.endswith('manifest.json')],
       'sources': [{'path': rel(p), 'sha256': sha(p), 'role': ROLE.get(rel(p), '')} for p in sorted(glob.glob(os.path.join(ROOT, 'src', '*'))) if os.path.isfile(p)],
       'inputs_used': [{'path': k, 'sha256': sha(os.path.join(ROOT, k)), 'use': u} for k, u in USE.items()],
       'inputs_not_used': ['input/assets/assets__t2s-logo-dark.svg (light-background variant)', 'input/assets/font__hero-office-poster.jpg (photo)', 'input/assets/favicon.ico'],
       'intermediates': [{'path': rel(p), 'sha256': sha(p)} for p in [os.path.join(ROOT, 'build', f) for f in ('video.mp4', 'mix.wav', 'music.wav', 'sfx.wav', 'audio_events.json')] if os.path.exists(p)],
       'music': 'original instrumental composed programmatically in src/compose.py (no third-party music, samples or loops); see output/music-license.md',
       'tools': {'ffmpeg': run(['ffmpeg', '-version']).stdout.splitlines()[0], 'chromium': (run([CHROME, '--version']).stdout.strip() or CHROME),
                 'python': sys.version.split()[0]}}
json.dump(man, open(os.path.join(OUT, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(qa, ensure_ascii=False, indent=1))
