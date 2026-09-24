"""Import verified originals and update only photography in the local CMS.

Originals stay private in .local/photo-originals; public files are responsive WebP.
"""
from pathlib import Path
import json
import sqlite3
import sys
from datetime import datetime, timezone
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cms

rows = json.loads((ROOT / 'data/high-resolution-sources.json').read_text(encoding='utf-8'))
new_names = {
    'medina': 'Koutoubia above the rooftops of Marrakech',
    'tangier': 'The city and rooftops of Tangier',
    'casablanca': 'Hassan II Mosque on the Casablanca waterfront',
    'ait-ben-haddou': 'Earthen architecture at Ait Ben Haddou',
    'agafay-camp': 'Rocky Agafay hills and a desert camp',
}
replace = {'mhe-koutoubia': 'hq-medina', 'mhe-essaouira': 'essaouira',
           'mhe-ait-ben-haddou': 'hq-ait-ben-haddou', 'mhe-ouzoud': 'ouzoud',
           'mhe-desert': 'camels', 'mhe-dunes': 'sahara', 'mhe-agafay': 'hq-agafay-camp'}
con = sqlite3.connect(ROOT / '.local/requests.sqlite3')
backup = ROOT.parent / '.backups' / 'before-high-resolution-20260915.sqlite3'
if not backup.exists():
    with sqlite3.connect(backup) as target:
        con.backup(target)
seed = json.loads((ROOT / 'data/media.seed.json').read_text(encoding='utf-8'))
media_by_id = {m['id']: m for m in seed}
for row in rows:
    key = row['id']
    identity = 'hq-' + key if key in new_names else key
    current = cms.document(con, 'media', identity)
    media = dict(current['document'] if current else media_by_id.get(identity, {}))
    if not media:
        media = dict(id=identity, name=new_names[key], alt=new_names[key], caption=new_names[key])
    original = ImageOps.exif_transpose(Image.open(ROOT / '.local/photo-originals' / (key + '.jpg'))).convert('RGB')
    variants = []
    for width in [320, 640, 960, 1600, 2400, min(3200, original.width)]:
        if width > original.width or any(v['width'] == width for v in variants):
            continue
        image = original.resize((width, round(original.height * width / original.width)), Image.Resampling.LANCZOS)
        path = '/assets/hq-' + key + '-' + str(width) + '.webp'
        image.save(ROOT / path.lstrip('/'), 'WEBP', quality=84, method=6)
        variants.append(dict(path=path, width=image.width, height=image.height))
    default = next(v for v in variants if v['width'] == 1600)
    media.update(path=default['path'], width=default['width'], height=default['height'],
                 variants=variants, original_width=original.width, original_height=original.height,
                 source=row.get('source', row['url']), license=row['provider'] + ' License')
    cms.save(con, 'media', identity, media, current['revision'] if current else 0)
    media_by_id[identity] = media

def update_trip(trip):
    trip['gallery'] = list(dict.fromkeys(replace.get(i, i) for i in trip['gallery']))
    trip['image'] = trip['gallery'][0]
    extras = {'imperial-cities-sahara-9-days': ['hq-casablanca'],
              'grand-morocco-14-days': ['hq-casablanca', 'chefchaouen'],
              'north-sahara-10-days': ['hq-tangier']}.get(trip['id'], [])
    for identity in extras:
        if identity not in trip['gallery']:
            trip['gallery'].append(identity)
    return trip

for trip in cms.documents(con, 'trip'):
    revision = trip.pop('revision')
    trip.pop('updated_at', None)
    before = json.dumps(trip)
    update_trip(trip)
    if json.dumps(trip) != before:
        cms.save(con, 'trip', trip['id'], trip, revision)
site = cms.document(con, 'site', 'main')
site['document']['hero_images'] = ['hq-medina', 'marrakech', 'essaouira', 'hq-chefchaouen-steps']
cms.save(con, 'site', 'main', site['document'], site['revision'])
con.close()
(ROOT / 'data/media.seed.json').write_text(json.dumps(list(media_by_id.values()), ensure_ascii=False, indent=2), encoding='utf-8')
path = ROOT / 'data/trips.seed.json'
trips = json.loads(path.read_text(encoding='utf-8'))
path.write_text(json.dumps([update_trip(t) for t in trips], ensure_ascii=False, indent=2), encoding='utf-8')
print('Imported', len(rows), 'originals with responsive WebP sizes; site and trip galleries updated.')
