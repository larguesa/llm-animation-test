from pathlib import Path
import json, hashlib, re
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'build'
(B/'fonts').mkdir(parents=True,exist_ok=True)
(ROOT/'output/review').mkdir(parents=True,exist_ok=True)
for family, weights in [('montserrat',[500,600,700,800]),('rubik',[400,500])]:
    source=next((ROOT/'input/fonts').glob(f'{family}__*wght*.ttf'))
    if 'Italic' in str(source):
        source=next(p for p in (ROOT/'input/fonts').glob(f'{family}__*wght*.ttf') if 'Italic' not in p.name)
    for weight in weights:
        dest=B/'fonts'/f'{family}-{weight}.ttf'
        if not dest.exists():
            font=TTFont(source)
            instance=instantiateVariableFont(font,{'wght':weight},inplace=True)
            instance.save(dest)
        print(dest.relative_to(ROOT))
css=(ROOT/'input/assets/_next__static__chunks__23njtp8mlj1pv.css').read_text()
palette=dict(re.findall(r'--([\w-]+):(#[0-9a-fA-F]{3,8})',css.split('}')[0]))
(B/'palette.json').write_text(json.dumps(palette,indent=2))
print('Palette:',palette)
print('Fonts prepared. Official SVGs will be rendered directly, unmodified.')
