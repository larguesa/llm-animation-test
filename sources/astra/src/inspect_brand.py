from pathlib import Path
import json,re,hashlib
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'review'
OUT.mkdir(parents=True,exist_ok=True)
css=(ROOT/'input/assets/_next__static__chunks__23njtp8mlj1pv.css').read_text()
selected=[]
for rule in css.split('}'):
    if any(k in rule.split('{')[0] for k in ['page-hero','detail','eyebrow','h1','h2','h3','pod','signal','logo','service-body','approach-step','engagement','role-card']):
        selected.append(rule+'}')
print('BRAND CSS RULES\n'+'\n'.join(selected))
for name in ['dark','light']:
    svg=(ROOT/f'input/assets/assets__t2s-logo-{name}.svg').read_text()
    print('LOGO',name,'COLORS',sorted(set(re.findall(r'fill="([^"]+)"',svg))))
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/home/hermes/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking'])
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    page.goto('https://t2stech.com/services/ai-native-delivery-pods',wait_until='networkidle',timeout=45000)
    page.screenshot(path=str(OUT/'official-page.png'),full_page=True)
    data=page.evaluate('''() => ({title:document.title,fonts:[...document.querySelectorAll('h1,h2,h3,p,.eyebrow')].map(e=>({tag:e.tagName,text:e.textContent,font:getComputedStyle(e).fontFamily,weight:getComputedStyle(e).fontWeight,color:getComputedStyle(e).color})).slice(0,45),images:[...document.images].map(e=>({src:e.src,alt:e.alt})),svgCount:document.querySelectorAll('svg').length})''')
    (OUT/'brand-reference.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    print(json.dumps(data,ensure_ascii=False,indent=2))
    browser.close()
