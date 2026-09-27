"""Manifest of actual workspace inputs, creative sources, deliverables and review files."""
from pathlib import Path
import hashlib,json,subprocess,platform,importlib.metadata
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'

def entry(p,role):
    return {'path':str(p.relative_to(ROOT)),'role':role,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

inputs=[]
for p in sorted((ROOT/'input').rglob('*')):
    if not p.is_file():continue
    if p.suffix.lower() in ['.svg','.ttf'] or p.name.endswith('OFL.txt') or p.name in ['t2s-page.html','t2s-page-text.txt'] or p.suffix=='.css':
        used=not ('Italic' in p.name)
        inputs.append({**entry(p,'official frozen source'),'used':used})
sources=[entry(p,'creative source / reproducibility') for p in sorted((ROOT/'src').glob('*.py'))]
sources.append(entry(ROOT/'requirements.txt','pinned Python dependencies'))
artifacts=[]
for base in [ROOT/'output',ROOT/'build/audio',ROOT/'build/fonts']:
    for p in sorted(base.rglob('*')):
        if p.is_file() and p.name!='manifest.json':artifacts.append(entry(p,'deliverable' if p.name=='final.mp4' else 'review / documentation / intermediate'))
validation=json.loads((OUT/'review/validation.json').read_text())
manifest={'project':'T2S Tech — AI-Native Delivery Pods','source_url':'https://t2stech.com/services/ai-native-delivery-pods','live_page_consulted':{'http_status':200,'saved_html':'page-live.html','reference_capture':'output/review/official-page.png','capture_is_not_used_as_video_scene':True},'format':validation['video'],'audio':validation['audio'],'brand':{'logo':'Official light/dark SVG rendered directly without editing paths or colors. SVG container size explicitly set from viewBox.','typography':{'headings':'Montserrat','support':'Rubik'},'colors':json.loads((ROOT/'build/palette.json').read_text()),'font_licenses':['input/fonts/montserrat__OFL.txt','input/fonts/rubik__OFL.txt'],'mark_rights':'T2S brand remains its owner’s property; use in the requested authorized service presentation only.'},'music':{'provenance':'Original programmatic composition; no external samples or licensed library track.','declaration':'output/music-license.md','source':'src/music.py','score':'build/audio/score.json','bpm':120},'timeline':[{'seconds':[0,5],'action':'Dispersed demands align and converge'},{'seconds':[5,10],'action':'Outcome-centered pod, specialists and agents'},{'seconds':[10,17],'action':'Five role verbs and human decision checkpoints'},{'seconds':[17,24],'action':'Context, delivery, quality and demonstrable evidence'},{'seconds':[24,30],'action':'Convergence, official brand, CTA; static reading hold 27–30'}],'render':{'renderer':'Skia CPU, HarfBuzz shaping, ffmpeg/libx264','resolution_native':True,'motion_blur':'3 weighted temporal samples across a 120-degree shutter during large transforms; crisp reading holds','threads':1,'lock':'/home/hermes/entregas/t2s-pods-model-comparison/render.lock'},'verification':'output/review/validation.json','limitations':['No subjective audio audition was possible in this CLI: decoded sound, true peak, loudness, waveform, durations and sound-event timing were checked.','No proprietary product screen is depicted: all cards, checkpoints and artifacts are conceptual.','This package is reproducible Python/vector source, not an After Effects project.'],'inputs':inputs,'sources':sources,'artifacts':artifacts,'runtime':{'python':platform.python_version(),'packages':{n:importlib.metadata.version(n) for n in ['skia-python','fonttools','scipy','numpy','uharfbuzz','Pillow']}}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Manifest:',len(inputs),'official inputs;',len(sources),'source files;',len(artifacts),'artifacts.')
print('Final sha256:',validation['sha256'])
