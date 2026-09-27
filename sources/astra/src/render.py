"""Single-thread CPU raster + ffmpeg. Run the render under the shared flock."""
import os
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('MKL_NUM_THREADS','1')
import sys,json,time,argparse,subprocess
from pathlib import Path
import bootstrap
import numpy as np
import skia
from PIL import Image,ImageDraw,ImageFont
from graphics import ROOT,W,H
from film import render

SAMPLE_TIMES=[.8,2.2,3.55,4.7,5.7,7.5,9.6,10.8,11.75,12.75,13.75,14.75,15.85,16.7,17.75,18.7,19.6,20.5,21.7,23.25,24.6,25.8,27.0,29.8]

def surface(w,h):
    return skia.Surface.MakeRaster(skia.ImageInfo.Make(w,h,skia.ColorType.kRGBA_8888_ColorType,skia.AlphaType.kPremul_AlphaType))

def snap(s,t,scale=1,audit=False):
    c=s.getCanvas();c.save();c.scale(scale,scale)
    bounds=render(c,t,audit);c.restore()
    return s.makeImageSnapshot(),bounds

def preview():
    out=ROOT/'output/review';out.mkdir(parents=True,exist_ok=True)
    s=surface(W,H); thumbs=[]; audit=[]
    for t in SAMPLE_TIMES:
        img,b=snap(s,t,audit=True)
        p=out/f'frame-{t:05.2f}.png';img.save(str(p),skia.kPNG)
        im=Image.open(p).convert('RGB');im.thumbnail((480,270))
        label=Image.new('RGB',(480,304),'#22262b');label.paste(im,(0,0))
        d=ImageDraw.Draw(label);d.text((12,276),f'{t:05.2f} s',fill='white')
        thumbs.append(label);audit.append({'time':t,'text':b})
    sheet=Image.new('RGB',(480*4,304*((len(thumbs)+3)//4)),'#22262b')
    for i,im in enumerate(thumbs):sheet.paste(im,((i%4)*480,(i//4)*304))
    sheet.save(out/'contact-sheet.png')
    (out/'layout-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
    print('Preview frames:',len(thumbs),'contact-sheet.png',flush=True)

def encode(dest,fps=30,width=1920,height=1080,crf=17,preset='medium'):
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    s=surface(width,height)
    cmd=['ffmpeg','-hide_banner','-y','-loglevel','warning','-threads','1','-filter_threads','1','-filter_complex_threads','1',
         '-f','rawvideo','-pixel_format','rgba','-video_size',f'{width}x{height}','-framerate',str(fps),'-i','-',
         '-an','-c:v','libx264','-threads','1','-preset',preset,'-crf',str(crf),'-pix_fmt','yuv420p',
         '-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv',
         '-r',str(fps),'-frames:v',str(30*fps),'-movflags','+faststart',str(dest)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    start=time.monotonic()
    # 3 subframes over 120 degrees only during large transforms. Reading holds stay sharp.
    intervals=[(2.50,5.70),(9.15,10.65),(16.10,17.40),(18.12,19.24),(19.6,20.31),(20.48,21.3),(23.88,26.50)]
    hold=None
    for f in range(30*fps):
        t=f/fps
        if t>=27 and hold is not None: data=hold
        else:
            blur=any(a<=t<=b for a,b in intervals)
            if blur:
                samples=[]
                for off in [-1/180,0,1/180]:
                    im,_=snap(s,t+off,width/W)
                    samples.append(im.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType).astype(np.uint16))
                arr=((samples[0]+2*samples[1]+samples[2])//4).astype(np.uint8)
            else:
                im,_=snap(s,t,width/W);arr=im.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
            data=arr.tobytes()
            if t>=27:hold=data
        p.stdin.write(data)
        if f%90==0: print(f'frame {f}/{30*fps}  time={t:.2f}s  elapsed={time.monotonic()-start:.1f}s',flush=True)
    p.stdin.close(); rc=p.wait()
    if rc:raise RuntimeError(f'ffmpeg exited {rc}')
    print('Encoded',dest,'elapsed',round(time.monotonic()-start,2),'seconds',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');ap.add_argument('--draft',action='store_true');ap.add_argument('--dest')
    args=ap.parse_args()
    if args.preview:preview()
    elif args.draft:encode(args.dest or ROOT/'build/draft-video.mp4',30,1280,720,20,'fast')
    else:encode(args.dest or ROOT/'build/master-video.mp4')
