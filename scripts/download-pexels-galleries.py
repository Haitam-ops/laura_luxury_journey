import json, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
ids=[13811710,19056100,38112369,30369940,25748808,38132378,38112400,25254713,6655418,13811591,13811658,19190929,34142488,39035434,17417129,35816095,29595717,5527300,25945757,35186871,39160958,8925105,37700545,18742776,24407130,29107889,30462449,18348736,37424044,35752250]
folder=ROOT/'.local/pexels-tour-originals';folder.mkdir(exist_ok=True)
def download(n):
 path=folder/(str(n)+'.jpg')
 try:
  if not path.exists():path.write_bytes(urllib.request.urlopen('https://images.pexels.com/photos/'+str(n)+'/pexels-photo-'+str(n)+'.jpeg?w=2400&auto=compress&cs=tinysrgb',timeout=25).read())
  img=Image.open(path);img.load();print(n,img.size,flush=True)
  return n
 except Exception as e:print(n,str(e),flush=True)
with ThreadPoolExecutor(max_workers=4) as pool: good=[n for n in pool.map(download,ids) if n]
for start in range(0,len(good),16):
 batch=good[start:start+16];sheet=Image.new('RGB',(1200,((len(batch)+3)//4)*235),'white');draw=ImageDraw.Draw(sheet)
 for i,n in enumerate(batch):
  img=ImageOps.contain(Image.open(folder/(str(n)+'.jpg')).convert('RGB'),(295,205));x=i%4*300;y=i//4*235
  sheet.paste(img,(x,y));draw.text((x+5,y+211),str(n),fill='black')
 sheet.save(folder/('sheet-'+str(start//16+1)+'.jpg'))
