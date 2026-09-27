"""Real browser playback check of the completed MP4; standalone headless Chrome."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/home/hermes/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--autoplay-policy=no-user-gesture-required','--disable-background-networking'])
    page=b.new_page(viewport={'width':960,'height':540})
    page.goto((ROOT/'output/final.mp4').as_uri(),wait_until='load')
    page.wait_for_function("document.querySelector('video') && document.querySelector('video').readyState>=2",timeout=30000)
    initial=page.evaluate("""async () => {let v=document.querySelector('video');v.muted=true;v.playbackRate=2;await v.play();return {duration:v.duration,width:v.videoWidth,height:v.videoHeight,readyState:v.readyState};}""")
    page.wait_for_function("document.querySelector('video').ended",timeout=45000)
    result=page.evaluate("""() => {let v=document.querySelector('video'),q=v.getVideoPlaybackQuality();return {ended:v.ended,currentTime:v.currentTime,error:v.error?{code:v.error.code,message:v.error.message}:null,quality:{totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,corruptedVideoFrames:q.corruptedVideoFrames}};}""")
    assert result['ended'] and result['error'] is None
    (ROOT/'output/review/browser-playback.json').write_text(json.dumps({'initial':initial,'playback':result,'note':'Muted 2x playback exercises the browser decoder; not a subjective audio audition.'},indent=2))
    print(json.dumps({'initial':initial,'playback':result},indent=2))
    b.close()
