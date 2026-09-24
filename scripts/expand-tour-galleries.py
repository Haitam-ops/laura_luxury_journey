"""Publish route-led photo galleries without changing trip copy or services."""
import json,sqlite3,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
R=lambda s:'route-'+s
J=lambda n:'journey-photo-'+str(n).zfill(2)
galleries={
'sahara-marrakech-3-days':['sahara','tour-todra-panorama','tour-atlas-pass',R('kiYzznir-uo'),J(1),J(2),R('pcbSQTQr2-I'),'tour-ouarzazate-kasbah'],
'imperial-cities-sahara-9-days':['hq-casablanca','tour-rabat-tower','tour-meknes-arch',R('mPD9BJ_QGXw'),R('NaY693XXXpY'),R('CFKksjYRSQ8'),R('vjs92g9SAz0'),J(3),R('a_8gEuwgBi8')],
'slow-sahara-5-days':['tour-sahara-sunset','camels','tour-draa-oasis','tour-ouarzazate-kasbah',R('LhVJaRPweJc'),J(5),R('1-Y2Ztxypnc'),R('zdIF9nWyl1A')],
'marrakech-fes-sahara-4-days':['fes','tour-ziz-valley','tour-todra-walk',R('vjs92g9SAz0'),R('SIWYZWNbF5k'),J(6),'tour-atlas-pass',R('a_8gEuwgBi8')],
'southern-morocco-7-days':['hq-ait-ben-haddou','oasis','tour-dades-road',J(7),R('hFHt6MtHn84'),R('0pUZ4vvE9tQ'),'tour-sahara-evening',J(2)],
'coast-desert-8-days':['essaouira','tour-essaouira-walls','tour-sahara-evening','hq-medina',R('No_Y3bn4lNQ'),R('-leOF2nzJQ8'),R('GyIcdvrlY3U'),J(3),R('SQxLsGEdx5s')],
'north-sahara-10-days':['chefchaouen','hq-tangier','hq-chefchaouen-steps',R('CBfUGtVP0QE'),R('mPD9BJ_QGXw'),R('7a_PHX91su8'),'tour-ziz-valley',R('kiYzznir-uo'),R('BeMc6A68Mpg')],
'grand-morocco-14-days':['marrakech','tour-grand-sahara','tour-grand-rabat',R('CMmgfHQiYsc'),R('UIwwV5GlyqY'),R('6xZuPeInEiQ'),R('M9GO4Gsd2SM'),R('ad1FM2Xj0QQ'),R('EUYzrXm1I_s'),R('Dql2_LN5sRg')],
}
captions={
J(1):'Ait Ben Haddou — the earthen village along the old caravan route',
J(2):'Dades Valley — village rooftops beneath sculpted cliffs',
J(3):'Southern valley scenery — palm groves and earthen villages',
J(5):'Dades Valley — a green pause between the red canyon walls',
J(6):'Dades Valley — river gardens below the rocks',
J(7):'Skoura — the towers and earthen walls of Kasbah Amerhidil',
R('kiYzznir-uo'):'Erg Chebbi — camels crossing the open dunes',
R('vjs92g9SAz0'):'Merzouga — a camel caravan in the evening light',
R('mPD9BJ_QGXw'):'Fes — discover the layers of the old medina',
R('NaY693XXXpY'):'Moroccan courtyards — carved arches, lanterns and quiet corners',
R('CFKksjYRSQ8'):'Marrakech — Koutoubia with the Atlas on the horizon',
R('a_8gEuwgBi8'):'Ait Ben Haddou — explore the lanes between earthen walls',
R('pcbSQTQr2-I'):'Ait Ben Haddou — rooftops overlooking the river valley',
R('LhVJaRPweJc'):'Ait Ben Haddou — colorful textiles along the village lanes',
R('1-Y2Ztxypnc'):'Ait Ben Haddou — soft evening colors over the ksar',
R('zdIF9nWyl1A'):'Southern Morocco — palm groves surrounded by dry mountain scenery',
R('SIWYZWNbF5k'):'Ait Ben Haddou — palms and traditional earthen architecture',
R('hFHt6MtHn84'):'Ait Ben Haddou — camels resting below the historic village',
R('0pUZ4vvE9tQ'):'Ait Ben Haddou — fortified towers and oasis greenery',
R('No_Y3bn4lNQ'):'Essaouira — blue fishing boats beneath the harbor tower',
R('-leOF2nzJQ8'):'Essaouira — beach life beside the Atlantic',
R('GyIcdvrlY3U'):'Essaouira — walk the sea-facing ramparts',
R('SQxLsGEdx5s'):'Essaouira — evening light along the waterfront',
R('CBfUGtVP0QE'):'Chefchaouen — follow the blue steps through the medina',
R('7a_PHX91su8'):'Marrakech — Jemaa el-Fnaa comes alive at sunset',
R('BeMc6A68Mpg'):'Marrakech — light and shadow inside historic courtyards',
R('CMmgfHQiYsc'):'Chefchaouen — blue doorways, plants and small discoveries',
R('UIwwV5GlyqY'):'Marrakech — browse the lanterns and textiles of the souks',
R('6xZuPeInEiQ'):'Moroccan architecture — intricate mosaics and carved courtyards',
R('M9GO4Gsd2SM'):'Essaouira — an evening stroll through the medina',
R('ad1FM2Xj0QQ'):'Essaouira — fishing boats and the old harbor gateway',
R('EUYzrXm1I_s'):'Marrakech — carved plasterwork at Ben Youssef Madrasa',
R('Dql2_LN5sRg'):'Marrakech — spices, ceramics and the colors of the market',
}
ids=[i for g in galleries.values() for i in g]
assert all(8<=len(g)<=10 and len(g)==len(set(g)) for g in galleries.values())
assert len({g[0] for g in galleries.values()})==8
from collections import Counter
assert max(Counter(ids).values())<=2
rows=json.loads((ROOT/'.local/expanded-photo-downloads.json').read_text(encoding='utf-8'))+json.loads((ROOT/'.local/unsplash-tour-downloads.json').read_text(encoding='utf-8'))
rows=[r for r in rows if r['id'] in captions]
assert {r['id'] for r in rows}==set(captions)
assert all('error' not in r for r in rows)
backup=ROOT.parent/'.backups'/('expanded-galleries-'+datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
for file in ['data/media.seed.json','data/trips.seed.json','data/tour-photography.json','gallery.js','styles.css','PHOTO-SOURCES.md']:
 shutil.copy2(ROOT/file,backup/Path(file).name)
con=sqlite3.connect(ROOT/'.local/requests.sqlite3')
with sqlite3.connect(backup/'requests.sqlite3') as dest:con.backup(dest)
con.close()
def prepare(row):
 identity=row['id'];folder='unsplash-tour-originals' if identity.startswith('route-') else 'expanded-photo-originals'
 original=ImageOps.exif_transpose(Image.open(ROOT/'.local'/folder/(identity+'.jpg'))).convert('RGB')
 variants=[]
 for width in sorted(set([320,640,960,1600,min(2400,original.width),min(3200,original.width)])):
  if width>original.width:continue
  path='/assets/'+identity+'-'+str(width)+'.webp';im=original.resize((width,round(original.height*width/original.width)),Image.Resampling.LANCZOS)
  im.save(ROOT/path.lstrip('/'),'WEBP',quality=84,method=4);variants.append(dict(path=path,width=im.width,height=im.height))
 default=next(v for v in variants if v['width']==1600)
 caption=captions[identity]
 item=dict(id=identity,name=caption,alt=caption,caption=caption,**default,variants=variants,original_width=original.width,original_height=original.height,source=row['page'],author=row['author'],license=row['license'],license_url=row['license_url'],credit_required=True,modifications='Resized; cropped for display')
 print('Prepared',identity,flush=True);return item
with ThreadPoolExecutor(max_workers=4) as pool:prepared=list(pool.map(prepare,rows))
con=sqlite3.connect(ROOT/'.local/requests.sqlite3');stamp=datetime.now(timezone.utc).isoformat()
with con:
 con.execute('BEGIN IMMEDIATE')
 for item in prepared:
  old=con.execute("SELECT revision FROM documents WHERE kind='media' AND id=?",(item['id'],)).fetchone()
  con.execute('INSERT INTO documents VALUES (?,?,?,?,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data,revision=excluded.revision,updated_at=excluded.updated_at',('media',item['id'],json.dumps(item,ensure_ascii=False),old[0]+1 if old else 1,stamp))
 for identity,gallery in galleries.items():
  data,revision=con.execute("SELECT data,revision FROM documents WHERE kind='trip' AND id=?",(identity,)).fetchone();trip=json.loads(data)
  assert trip['category']=='journeys'
  trip.update(gallery=gallery,image=gallery[0])
  con.execute("UPDATE documents SET data=?,revision=?,updated_at=? WHERE kind='trip' AND id=?",(json.dumps(trip,ensure_ascii=False),revision+1,stamp,identity))
con.close()
media_path=ROOT/'data/media.seed.json';media={m['id']:m for m in json.loads(media_path.read_text(encoding='utf-8'))};media.update({m['id']:m for m in prepared})
media_path.write_text(json.dumps(list(media.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
trips_path=ROOT/'data/trips.seed.json';trips=json.loads(trips_path.read_text(encoding='utf-8'))
for t in trips:
 if t['id'] in galleries:t.update(gallery=galleries[t['id']],image=galleries[t['id']][0])
trips_path.write_text(json.dumps(trips,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest_path=ROOT/'data/tour-photography.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['galleries']=galleries;manifest['expanded_sources']=[dict(r,caption=captions[r['id']]) for r in rows]
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (ROOT/'PHOTO-SOURCES.md').open('a',encoding='utf-8') as doc:
 doc.write('\n\n## Expanded route galleries — September 2026\n\nPhotos are destination illustrations. No stock accommodation image is presented as a contracted stay. Creative Commons derivatives retain their original licenses.\n\n| Photograph | Photographer | License | Download resolution |\n|---|---|---|---|\n')
 for m in prepared:doc.write(f"| [{m['caption']}]({m['source']}) | {m['author']} | [{m['license']}]({m['license_url']}) | {m['original_width']} × {m['original_height']} |\n")
print(json.dumps({'counts':{k:len(v) for k,v in galleries.items()},'total':len(ids),'unique':len(set(ids)),'new':len(prepared),'backup':str(backup)}),flush=True)
