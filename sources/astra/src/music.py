"""Original electronic instrumental / 120 BPM / D minor / exactly 30 seconds.
All sounds synthesized here from oscillators and seeded noise. No samples, no API,
no third-party composition, no voice. Music and sound-design stems are saved.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import json,wave
import numpy as np
from scipy.signal import butter,sosfilt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/audio';OUT.mkdir(parents=True,exist_ok=True)
SR=48000;DUR=30;N=SR*DUR;BEAT=.5
rng=np.random.default_rng(220526)
music=np.zeros((N,2),np.float64); fx=np.zeros_like(music)
notes=[];cues=[]

def hz(n):return 440*2**((n-69)/12)
def tt(d):return np.arange(round(SR*d))/SR

def filt(x,f=3000,kind='lowpass',order=2):
    return sosfilt(butter(order,f,btype=kind,fs=SR,output='sos'),x,axis=0)
def env(t,d,attack=.01,release=.2):
    return (1-np.exp(-t/max(attack,.0001)))*np.minimum(1,np.maximum(0,(d-t)/release))**1.6

def put(bus,s,start,amp=1,pan=0):
    at=round(start*SR)
    if at>=N:return
    s=np.asarray(s)
    if s.ndim==1:
        theta=(pan+1)*np.pi/4;s=np.column_stack((s*np.cos(theta),s*np.sin(theta)))
    if at<0:s=s[-at:];at=0
    ln=min(len(s),N-at)
    bus[at:at+ln]+=s[:ln]*amp

def pluck(note,d=.9,vel=1):
    t=tt(d);f=hz(note)
    s=(np.sin(2*np.pi*f*t+1.15*np.sin(2*np.pi*f*2*t)*np.exp(-t*7))+.15*np.sin(2*np.pi*f*3*t)*np.exp(-t*5))
    return s*np.exp(-t*5.5)*env(t,d,.006,.19)*vel

def bass(note,d=.4):
    t=tt(d);f=hz(note);s=np.sin(2*np.pi*f*t)
    for k in [2,3,4,5]:s+=np.sin(2*np.pi*f*k*t)*(.22/k)
    return filt(s,380)*env(t,d,.008,.1)*np.exp(-t*1.3)

def kick():
    t=tt(.40);phase=2*np.pi*(48*t+(105-48)*.021*(1-np.exp(-t/.021)))
    body=np.sin(phase)*np.exp(-t*11)
    click=filt(rng.normal(0,1,len(t)),5000,'highpass')*np.exp(-t*190)*.17
    return (body+click)*(1-np.exp(-t*1500))

def hat(open_=False):
    d=.21 if open_ else .075;t=tt(d)
    n=filt(rng.normal(size=len(t)),[7000,15500],'bandpass')
    return n*np.exp(-t*(20 if open_ else 72))*(1-np.exp(-t*1700))

def snare():
    t=tt(.19);n=filt(rng.normal(size=len(t)),[1300,8800],'bandpass')
    return (n*.65+np.sin(2*np.pi*189*t)*.18)*np.exp(-t*25)*(1-np.exp(-t*1000))

# Harmonic voicings deliberately leave space in the low mids.
chords=[(0,[50,57,60,64,69]),(5,[46,53,57,60,65]),(10,[41,53,57,60,67]),(14,[48,55,62,64,67]),(17,[50,57,60,64,69]),(21,[46,53,57,60,65]),(24,[50,57,60,64,69])]
for j,(st,ns) in enumerate(chords):
    nxt=chords[j+1][0] if j+1<len(chords) else 30
    d=min(30-st,nxt-st+1.3);t=tt(d);s=np.zeros((len(t),2))
    for k,n in enumerate(ns):
        f=hz(n)
        for side,det in [(0,.9990),(1,1.0010)]:
            voice=np.sin(2*np.pi*f*det*t+k*.57)+.26*np.sin(2*np.pi*f*2*det*t+.3)+.08*np.sin(2*np.pi*f*3*det*t)
            s[:,side]+=voice
    s=filt(s,2100)/len(ns)
    attack=.48 if st else .95
    e=env(t,d,attack,min(1.4,d/2))
    # Gentle sidechain creates pulse, but pad remains airy and restrained.
    glob=t+st
    pump=1-.22*np.exp(-((glob%BEAT)/.065))
    s*=e[:,None]*pump[:,None]
    put(music,s,st,.24 if st<24 else .29)
    notes.append({'time':st,'kind':'pad','midi':ns,'duration':d})

roots=[(0,38),(5,34),(10,41),(14,36),(17,38),(21,34),(24,38)]
def root(st):return next(n for t,n in reversed(roots) if st>=t)
# Restrained bass syncopation. Percussion recedes as the close resolves.
for beat in range(54):
    st=beat*BEAT
    if st<1.5:continue
    section=.48 if st<5 else .83 if st<10 else 1.0 if st<17 else .76 if st<24 else .62
    if beat%4 in [0,2] or (st>=10 and st<17):
        put(music,kick(),st,.39*section)
    if beat%4 in [1,3] and st<24:
        put(music,snare(),st,.083*section,pan=.04)
    if beat%4 in [0,2,3] and st>=3:
        pos=st+(.25 if beat%4==3 else 0)
        put(music,bass(root(st),.37),pos,.25*section)
        notes.append({'time':pos,'kind':'bass','midi':[root(st)],'duration':.37})
    if 5<=st<26:
        for sub in [0,.25]:
            put(music,hat(False),st+sub,.056*section*(.7 if sub==0 else 1),pan=-.22 if sub==0 else .24)
        if beat%4==3:put(music,hat(True),st+.375,.03*section,.37)

# A minimal, original 16-step melodic cell with sparse variations.
cell=[(0,74),(1.5,69),(3,72),(4.5,76),(6,69),(7.5,65)]
for bar,st in enumerate([1,5,9,13,17,21]):
    for step,n in cell:
        when=st+step*.5
        if when>=24:continue
        if st<5 and step not in [0,3,6]:continue
        transpose=-2 if st in [5,21] else 0
        n+=transpose
        vel=.068 if when<5 else .087 if when<17 else .060
        pan=[-.22,.15,.28,-.15,0,.2][int(step/1.5)]
        p=pluck(n)
        put(music,p,when,vel,pan)
        put(music,p,when+.375,vel*.25,-pan)
        put(music,p,when+.750,vel*.10,pan)
        notes.append({'time':when,'kind':'pluck','midi':[n],'duration':.9})
# Final tonic: not a jingle. A suspended major ninth settles into the reading hold.
for n,a,st in [(62,.085,24),(69,.060,24),(74,.066,24.5),(76,.041,25),(62,.061,26.5),(69,.047,26.5),(74,.039,26.5)]:
    t=tt(3.3);s=(np.sin(2*np.pi*hz(n)*t)+.17*np.sin(2*np.pi*hz(n)*2*t))*np.exp(-t*1.45)*env(t,3.3,.015,1.3)
    put(music,s,st,a,pan=(n-69)*.025)

# Sound design: narrow-band air, connection ticks, and human checkpoint dyads.
def whoosh(st,d=.55,amp=.08,pan=0):
    t=tt(d);n=filt(rng.normal(size=len(t)),[650,6500],'bandpass')
    e=np.sin(np.pi*t/d)**2
    s=n*e*(.6+.4*np.sin(2*np.pi*1.3*t))
    put(fx,s,st,amp,pan);cues.append({'time':st,'type':'shape transition','duration':d})
def tick(st,kind='connect',pan=0):
    t=tt(.26)
    freq=880 if kind=='connect' else 660
    s=(np.sin(2*np.pi*freq*t)+.36*np.sin(2*np.pi*freq*1.5*t))*np.exp(-t*29)*env(t,.26,.002,.09)
    put(fx,s,st,.068 if kind=='connect' else .08,pan)
    cues.append({'time':st,'type':kind,'duration':.26})
for st,d,a in [(2.68,.46,.043),(4.28,.76,.065),(9.15,1.05,.074),(16.18,.85,.065),(24.00,1.0,.073),(25.65,.54,.033)]:whoosh(st,d,a)
for i in range(6):tick(4.9+i*.085,'connect',(i-2.5)*.08)
for i in range(5):
    tick(10.5+i,'role',(i-2)*.13)
for st in [8.0,11.4,13.4,15.4,18.56,20.66]:tick(st,'human checkpoint',-.1)
for st in [18.1,19.35,20.3,21.25]:tick(st,'evidence',.12)

# Short deterministic stereo room, kept behind the dry transients.
wet=np.zeros_like(music)
for delay,gain in [(.083,.055),(.137,.043),(.233,.039),(.389,.031),(.577,.022)]:
    k=round(delay*SR);wet[k:]+=music[:-k,::-1]*gain
music+=filt(wet,4500)
# Global ramps and gentle analog-style saturation, then measured mastering in ffmpeg.
global_t=np.arange(N)/SR
fade=np.minimum(1,global_t/.05)*np.minimum(1,np.maximum(0,(30-global_t)/1.0))**1.2
music*=fade[:,None];fx*=fade[:,None]
mix=music+fx
mix=np.tanh(mix*1.10)/1.10
peak=np.max(np.abs(mix));scale=.83/max(peak,1e-6)

def save(name,a):
    a=np.asarray(np.clip(a,-.999,.999)*32767,dtype='<i2')
    with wave.open(str(OUT/name),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(a.tobytes())

save('music-original.wav',music*scale)
save('sound-design.wav',fx*scale)
save('mix-premaster.wav',mix*scale)
(OUT/'score.json').write_text(json.dumps({'bpm':120,'duration':30,'sample_rate':SR,'key':'D minor','random_seed':220526,'notes':notes,'sound_cues':cues},ensure_ascii=False,indent=2))
print('Original score:',len(notes),'note events;',len(cues),'sound cues; peak premaster:',round(float(np.max(np.abs(mix*scale))),5))
