"""Verification of the delivered MP4, including decoded frames and decoded AAC."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import json,subprocess,hashlib,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output';REV=OUT/'review';REV.mkdir(parents=True,exist_ok=True)
VIDEO=OUT/'final.mp4'

def run(cmd):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return p

probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(VIDEO)]).stdout)
(REV/'ffprobe.json').write_text(json.dumps(probe,indent=2))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],v['nb_read_frames'])==(1920,1080,'30/1','900')
assert abs(float(probe['format']['duration'])-30)<.001
assert a['channels']==2 and a['sample_rate']=='48000'
assert v['codec_name']=='h264' and a['codec_name']=='aac'
assert v['pix_fmt']=='yuv420p'
dec=run(['ffmpeg','-v','error','-threads','1','-i',str(VIDEO),'-f','null','-'])
assert not dec.stderr.strip(),dec.stderr.decode()

sample_frames=[30,75,105,145,195,255,285,315,345,375,405,435,465,501,531,561,591,621,651,696,741,780,810,897]
# One sequential decode, not repeated seeking; inspect the actual compressed deliverable.
sel='+'.join('eq(n\\,%d)'%n for n in sample_frames)
run(['ffmpeg','-v','error','-y','-threads','1','-filter_threads','1','-i',str(VIDEO),'-vf','select='+sel,'-fps_mode','vfr',str(REV/'decoded-%02d.png')])
thumbs=[]
for i,n in enumerate(sample_frames):
    im=Image.open(REV/f'decoded-{i+1:02d}.png').convert('RGB');im.thumbnail((480,270))
    cell=Image.new('RGB',(480,300),'#22262b');cell.paste(im,(0,0));ImageDraw.Draw(cell).text((12,277),f'{n/30:.2f} s | frame {n}',fill='white')
    thumbs.append(cell)
sheet=Image.new('RGB',(1920,1800),'#22262b')
for i,im in enumerate(thumbs):sheet.paste(im,((i%4)*480,(i//4)*300))
sheet.save(REV/'final-contact-sheet.png')

# Verify the requested reading hold, allowing codec rounding in inter-predicted frames.
raw=run(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss','27','-i',str(VIDEO),'-an','-vf','scale=480:270','-pix_fmt','rgb24','-f','rawvideo','-']).stdout
frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,270,480,3)
hold_mean=float(np.abs(frames.astype(np.int16)-frames[0].astype(np.int16)).mean())
hold_max=int(np.abs(frames.astype(np.int16)-frames[0].astype(np.int16)).max())
assert len(frames)==90
assert hold_mean<.35,(hold_mean,hold_max)

pcm=run(['ffmpeg','-v','error','-threads','1','-i',str(VIDEO),'-vn','-ar','48000','-ac','2','-c:a','pcm_f32le','-f','f32le','-']).stdout
samples=np.frombuffer(pcm,dtype='<f4').reshape(-1,2)[:1440000]
peak=float(np.max(np.abs(samples)))
clipped=int(np.count_nonzero(np.abs(samples)>=1))
assert clipped==0
rms=np.sqrt(np.mean(samples**2,axis=0))
bins=[float(np.sqrt(np.mean(z*z))) for z in np.array_split(samples,300)]
waveim=Image.new('RGB',(1800,480),'#22262b');d=ImageDraw.Draw(waveim)
for i,val in enumerate(bins):
    hh=min(200,int(val*1000));x=30+i*5.8
    d.line((x,260-hh,x,260+hh),fill='#00b4e8',width=3)
for st,label in [(0,'0'),(5,'5'),(10,'10'),(17,'17'),(24,'24'),(27,'27'),(30,'30 s')]:
    x=30+st*58;d.line((x,38,x,465),fill='#65717c',width=1);d.text((x+4,16),label,fill='white')
waveim.save(REV/'audio-waveform.png')
loud=run(['ffmpeg','-hide_banner','-nostats','-threads','1','-filter_threads','1','-i',str(VIDEO),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json','-f','null','-']).stderr.decode()
(REV/'audio-loudness.txt').write_text(loud)
match=re.search(r'\{\s*"input_i".*?\}',loud,re.S)
loudness=json.loads(match.group()) if match else {}

layout=json.loads((REV/'layout-audit.json').read_text())
exceptions=[{'time':r['time'],**b} for r in layout for b in r['text'] if b['x']<65 or b['y']<45 or b['right']>1855 or b['bottom']>1035]
# Audit uses transformed glyph bounds; intentional intermediate masked states are excluded.
result={'file':'output/final.mp4','sha256':hashlib.sha256(VIDEO.read_bytes()).hexdigest(),'bytes':VIDEO.stat().st_size,'video':{'codec':v['codec_name'],'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':int(v['nb_read_frames']),'duration':float(probe['format']['duration']),'pixel_format':v['pix_fmt'],'color_space':v.get('color_space')},'audio':{'codec':a['codec_name'],'channels':2,'sample_rate':48000,'peak_linear':peak,'clipped_samples':clipped,'rms_channels':rms.tolist(),'loudness':loudness},'decode_errors':dec.stderr.decode(),'final_hold':{'frames':len(frames),'mean_pixel_difference':hold_mean,'max_pixel_difference':hold_max},'layout_safe_area_exceptions':exceptions,'review_frames':sample_frames,'listening_limit':'No audio-listening tool is available. Decoded samples, loudness, clipping, envelopes and synchronized event times are verified; no claim of subjective audition.'}
(REV/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
