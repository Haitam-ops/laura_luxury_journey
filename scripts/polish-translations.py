"""Apply editorial UI translations after generating the machine drafts."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
manual=json.loads((ROOT/'data/manual-translations.json').read_text(encoding='utf-8'))
manual['phrases']+=json.loads((ROOT/'data/hero-translations.json').read_text(encoding='utf-8'))['phrases']
manual['phrases']+=json.loads((ROOT/'data/form-translations.json').read_text(encoding='utf-8'))['phrases']
manual['phrases']+=json.loads((ROOT/'data/detail-translations.json').read_text(encoding='utf-8'))['phrases']
for i,code in enumerate(manual['codes']):
    path=ROOT/'data/locales'/(code+'.json')
    if not path.exists():
        continue
    data=json.loads(path.read_text(encoding='utf-8'))
    data['strings']={k:v.replace('▁',' ').strip() for k,v in data['strings'].items()}
    for row in manual['phrases']:
        data['strings'][row[0]]=row[i+1]
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
marketing=json.loads((ROOT/'data/marketing-translations.json').read_text(encoding='utf-8'))
for i,code in enumerate(marketing['codes']):
    path=ROOT/'data/locales'/(code+'.json')
    if not path.exists():
        continue
    data=json.loads(path.read_text(encoding='utf-8'))
    for row in marketing['phrases']:
        data['strings'][row[0]]=row[i+1]
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Editorial interface and marketing translations applied.')
