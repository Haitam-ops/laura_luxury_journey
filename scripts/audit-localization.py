"""Inventory customer-facing copy without launching a browser."""
from pathlib import Path
from html.parser import HTMLParser
import json,re
ROOT=Path(__file__).resolve().parents[1]
phrases=set()
def add(v):
 if isinstance(v,(list,tuple)):
  for x in v:add(x)
 elif isinstance(v,str):
  v=v.strip()
  if v and not any(x in v for x in ["'+", "+'", '(', ')']) and re.search('[A-Za-z]',v) and not any(x in v for x in ['${','=>','document.','http://','https://','/assets/']):phrases.add(v)
class CopyParser(HTMLParser):
 def handle_data(self,d):add(d)
 def handle_starttag(self,t,attrs):
  for k,v in attrs:
   if k in ['alt','placeholder','aria-label','title']:add(v)
parser=CopyParser();parser.feed((ROOT/'index.html').read_text('utf-8'))
for name in ['app.js','boot.js','gallery.js','route-map.js']:
 s=(ROOT/name).read_text('utf-8');s=re.sub(r'const heroEditorial=.*?const heroEdition=', 'const heroEdition=',s,flags=re.S)
 if name=='boot.js':
  s=re.sub(r'const messages=(\{.*?\});',lambda m:'const messages='+json.dumps({'en':json.loads(m[1])['en']})+';',s)
 for m in re.finditer(r"(['\"])((?:\\.|(?!\1).)*?)\1",s):
  v=m[2].replace("\\'","'").replace('\\"','"').replace('\\n','\n')
  if '<' in v and '>' in v:
   try:parser.feed(v)
   except:pass
  elif (re.match(r'^[A-Z{]',v) and (' ' in v or len(v)<25)) and not re.search(r'[=;<>\\]|^[A-Z0-9]+$|^M\d',v):add(v)
 for m in re.finditer(r'>([^<>$`]+)<',s):
  if not re.search(r'[{}=]',m[1]):add(m[1])
c=json.loads((ROOT/'data/content.json').read_text('utf-8'))
fields=['title','duration','start','end','region','summary','story','fit','pace','highlights','itinerary','practical','cover','extras','overnights']
for t in c['trips']:
 for k in fields:add(t.get(k))
for k,v in c['site'].items():
 if k not in ['brand','email','phone','whatsapp','address','hero_images','instagram','facebook','tiktok','youtube']:add(v)
for m in c['media'].values():
 for k in ['alt','caption','modifications']:add(m.get(k))
# Runtime labels, error states and downloaded request headings.
add(['Zoom in','Zoom out','contributors','Source','Reference','Trip','Name','Email','Date','Travelers','Style','Stays','Notes','None','Flexible','LAURA LUXURY JOURNEYS · TRIP REQUEST','LAURA LUXURY JOURNEYS · FIELD NOTES','This is a saved planning request, not a confirmed booking. No payment was taken.'])
# Remove code tokens accidentally caught around markup boundaries.
phrases={v for v in phrases if not re.search(r'querySelector|setAttribute|join\(|\.json|\.js|\.css|\[|\]|^POST$|^GET$|^Content-|^AbortError$|^TypeError$|^SELECT|^INSERT|^UPDATE|^DELETE|^Idempotency|^DOMContent|^OpenStreetMap$',v)}
(ROOT/'data/current-source-strings.json').write_text(json.dumps(sorted(phrases),ensure_ascii=False,indent=2)+'\n','utf-8')
old=set(json.loads((ROOT/'data/source-strings.json').read_text('utf-8')));old.update(phrases)
(ROOT/'data/source-strings.json').write_text(json.dumps(sorted(old),ensure_ascii=False,indent=2)+'\n','utf-8')
for code in ['fr','es','de','it','pt','nl']:
 d=json.loads((ROOT/f'data/locales/{code}.json').read_text('utf-8'))['strings'];missing=[s for s in phrases if s not in d];print(code,len(phrases),'current strings;',len(missing),'missing')
(ROOT/'.local/missing-current.json').write_text(json.dumps([s for s in sorted(phrases) if s not in d],ensure_ascii=False,indent=2),'utf-8')
