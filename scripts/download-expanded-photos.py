import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
new=json.loads((ROOT/'.local/expanded-photo-candidates.json').read_text(encoding='utf-8'))
old=json.loads((ROOT/'.local/tour-photo-candidates.json').read_text(encoding='utf-8'))
picks={'Ait Ben Haddou panorama':[0],'Dades valley':[0,1,2,3,4],'Skoura Amerhidil':[0,2,4,5,6],
       'Fes medina':[0,1,3,4,6,7,8],'Bou Inania Fes':[1,2,3,4,7],
       'Chefchaouen street':[0,8,9,10,11],'Tangier kasbah':[1,3,4,11],
       'Essaouira port':[7,8,9],'Essaouira beach':[0,2,4,5],
       'Marrakech Bahia palace':[3,6,8],'Marrakech souk':[0,1,4,6,7,10],
       'Taroudant walls':[2,5,6],'Ifrane cedar':[0,2,5,7],
       'Draa valley':[1,3],'Volubilis ruins':[0,1,3]}
oldpicks={'Erg Chebbi dunes':[1,2],'Tizi n Tichka':[0,2,3,4],'Ouarzazate kasbah':[1,2,4,5,6]}
rows=[]
for collection,choices in [(new,picks),(old,oldpicks)]:
 for topic,indices in choices.items():
  for n in indices:
   row=dict(collection[topic][n]);row.update(topic=topic,id='journey-photo-'+str(len(rows)+1).zfill(2));rows.append(row)
folder=ROOT/'.local/expanded-photo-originals';folder.mkdir(exist_ok=True)
def download(row):
 target=folder/(row['id']+'.jpg')
 try:
  if not target.exists():
   url=row['url'].split('?')[0]
   width=1920
   url=url.replace('/commons/','/commons/thumb/')+'/'+str(width)+'px-'+url.rsplit('/',1)[-1]
   req=urllib.request.Request(url,headers={'User-Agent':'DesertGatePhotoResearch/1.0'})
   target.write_bytes(urllib.request.urlopen(req,timeout=20).read())
  image=ImageOps.exif_transpose(Image.open(target));image.load()
  row['download_width'],row['download_height']=image.size
  print('OK',row['id'],row['topic'],image.size,flush=True)
 except Exception as e:
  row['error']=str(e);print('SKIP',row['id'],str(e),flush=True)
with ThreadPoolExecutor(max_workers=2) as pool:
 list(pool.map(download,rows))
(ROOT/'.local/expanded-photo-downloads.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
good=[r for r in rows if 'error' not in r]
for start in range(0,len(good),20):
 batch=good[start:start+20];sheet=Image.new('RGB',(1200,((len(batch)+3)//4)*225),'white');draw=ImageDraw.Draw(sheet)
 for n,row in enumerate(batch):
  img=ImageOps.contain(Image.open(folder/(row['id']+'.jpg')).convert('RGB'),(294,195))
  x=(n%4)*300;y=(n//4)*225;sheet.paste(img,(x,y));draw.text((x+4,y+198),row['id']+' '+row['topic'][:20],fill='black')
 sheet.save(folder/('sheet-'+str(start//20+1)+'.jpg'))
print('Downloaded',len(good),'of',len(rows),flush=True)
