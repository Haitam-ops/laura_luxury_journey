import json,urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
raw='''kiYzznir-uo|1559586616-361e18714958|Carlos Leret
lqkHaP6P6nc|1580761338251-16bfec2343ef|gemmmm
vjs92g9SAz0|1697723831958-63bbdbe09962|Mauro Lima
KdLpF86EL-8|1677836157562-5e24481b6b69|Desert Morocco Adventure
CFKksjYRSQ8|1597212618440-806262de4f6b|Paul Macallan
CMmgfHQiYsc|1564507004663-b6dfb3c824d5|Kyriacos Georgiou
NaY693XXXpY|1559925523-10de9e23cf90|Carlos Leret
7a_PHX91su8|1587974928442-77dc3e0dba72|CALIN STAN
zdIF9nWyl1A|1568241360857-e23e825c4e08|Mari Potter
CBfUGtVP0QE|1538600838042-6a0c694ffab5|Mohammed
LhVJaRPweJc|1536237717235-0acadb345d8c|Frida Aguilar Estrada
NwT-VBe2QF8|1531230689007-0b32d7a7c33e|Macia Serrano
UIwwV5GlyqY|1569440703456-29b9c31765ca|Jean Carlo Emer
pcbSQTQr2-I|1527338611623-4e242563220a|Toa Heftiba
mPD9BJ_QGXw|1696952252983-46cb2c304ad9|Mauro Lima
6xZuPeInEiQ|1719084198651-5ac167cb3e6e|Abdou Faiz
No_Y3bn4lNQ|1624802746702-60ca95bdb605|rigel
-leOF2nzJQ8|1613057157282-cc3cbe630b26|Peter Schulz
M9GO4Gsd2SM|1682019720535-709f0ce910ff|Hamza Omlacho
GyIcdvrlY3U|1743963790208-07ce117cdfc6|Anastasia Dimitri
SQxLsGEdx5s|1624802710884-f7c40598140c|rigel
ad1FM2Xj0QQ|1646590640485-df729f1bcfed|Youssef Aboutaleb
EUYzrXm1I_s|1714141818001-dfa0e5c806a3|Massimiliano Morosinotto
hFHt6MtHn84|1722166909028-d6cde685e080|Sebastiano Corti
a_8gEuwgBi8|1569531955310-c02f71c2ddaf|Alex Azabache
1-Y2Ztxypnc|1553522988-509e7645287d|rigel
0pUZ4vvE9tQ|1664346399419-66548606945f|Polina Kocheva
SIWYZWNbF5k|1722166909000-dd76844751c1|Sebastiano Corti
bzFHhYKdIa0|1653323792487-6ecc6217040b|Rumman Amin
Dql2_LN5sRg|1580746738099-1cb74f972feb|zakariae daoui
OZXMG7bQ-Kc|1640263408299-8972236d0590|Mehdi El marouazi
Di64fgE9vos|1618423205267-e95744f57edf|Esteban Palacios Blanco
BeMc6A68Mpg|1548018560-4cb48a8837c1|Don Fontijn
m3bCfGum88U|1599859725763-4a16c9468890|Oussama sabri
FP9g9fNk9zA|1579283135011-0974a412341a|Selina Bubendorfer
R43GFASFGWo|1569370088252-c26ef022594c|Zakaria Zayane'''
rows=[]
for line in raw.splitlines():
 key,photo,author=line.split('|'); rows.append(dict(id='route-'+key,url='https://images.unsplash.com/photo-'+photo,page='https://unsplash.com/photos/'+key,author=author,license='Unsplash License',license_url='https://unsplash.com/license'))
folder=ROOT/'.local/unsplash-tour-originals';folder.mkdir(exist_ok=True)
def download(row):
 try:
  path=folder/(row['id']+'.jpg')
  if not path.exists():path.write_bytes(urllib.request.urlopen(row['url'],timeout=30).read())
  im=Image.open(path);im.load();row['width'],row['height']=im.size;print(row['id'],im.size,flush=True)
 except Exception as e:row['error']=str(e);print(row['id'],str(e),flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(download,rows))
(ROOT/'.local/unsplash-tour-downloads.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
good=[r for r in rows if 'error' not in r]
for start in range(0,len(good),16):
 batch=good[start:start+16];sheet=Image.new('RGB',(1200,((len(batch)+3)//4)*235),'white');draw=ImageDraw.Draw(sheet)
 for i,row in enumerate(batch):
  img=ImageOps.contain(Image.open(folder/(row['id']+'.jpg')).convert('RGB'),(295,205));x=i%4*300;y=i//4*235;sheet.paste(img,(x,y));draw.text((x+5,y+211),row['id'],fill='black')
 sheet.save(folder/('sheet-'+str(start//16+1)+'.jpg'))
