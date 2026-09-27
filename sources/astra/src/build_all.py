"""Reproduce the delivered artifact from frozen inputs, with serialized CPU renders."""
from pathlib import Path
import os,sys,subprocess,json,re
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
PY=sys.executable
LOCK='/home/hermes/entregas/t2s-pods-model-comparison/render.lock'
def run(cmd):
    print(' '.join(str(x) for x in cmd),flush=True)
    subprocess.run(cmd,check=True)
run([PY,'src/prepare.py'])
run([PY,'src/music.py'])
measure=subprocess.run(['ffmpeg','-hide_banner','-nostats','-threads','1','-filter_threads','1','-i','build/audio/mix-premaster.wav','-af','loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json','-f','null','-'],capture_output=True,check=True,text=True)
m=json.loads(re.search(r'\{\s*"input_i".*?\}',measure.stderr,re.S).group())
af=f"loudnorm=I=-16:TP=-1.5:LRA=8:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset=0:linear=true:print_format=json"
run(['ffmpeg','-hide_banner','-y','-loglevel','warning','-threads','1','-filter_threads','1','-i','build/audio/mix-premaster.wav','-af',af,'-ar','48000','-c:a','pcm_s24le','build/audio/master.wav'])
run(['flock',LOCK,PY,'src/render.py','--preview'])
run(['flock',LOCK,PY,'src/render.py'])
run(['ffmpeg','-hide_banner','-y','-loglevel','warning','-threads','1','-filter_threads','1','-i','build/master-video.mp4','-i','build/audio/master.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-ar','48000','-ac','2','-t','30','-movflags','+faststart','-metadata','title=T2S Tech — AI-Native Delivery Pods','-metadata','comment=Original vector motion graphics and programmatic instrumental; official T2S brand assets.','output/final.mp4'])
run(['flock',LOCK,PY,'src/verify.py'])
run([PY,'src/manifest.py'])
