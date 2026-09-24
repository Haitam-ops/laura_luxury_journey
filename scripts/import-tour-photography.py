"""Import the curated multi-day photography; preserve all other CMS fields."""
from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import sqlite3
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / 'data/tour-photography.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
galleries = manifest['galleries']
galleries['southern-morocco-7-days'] = ['hq-ait-ben-haddou', 'oasis', 'tour-dades-road']
galleries['coast-desert-8-days'] = ['essaouira', 'tour-essaouira-walls', 'tour-sahara-evening', 'hq-medina']
galleries['marrakech-fes-sahara-4-days'] = ['fes', 'tour-ziz-valley', 'tour-todra-walk']
galleries['north-sahara-10-days'] = ['chefchaouen', 'hq-tangier', 'hq-chefchaouen-steps']
galleries['grand-morocco-14-days'] = ['marrakech', 'tour-grand-sahara', 'tour-grand-rabat']
ids = [identity for gallery in galleries.values() for identity in gallery]
assert len(ids) == len(set(ids)), 'Multi-day galleries must not share photographs'
manifest['sources'] = [s for s in manifest['sources'] if s['id'] in ids]
captions = {
    'tour-atlas-pass': 'Mountain scenery at the Tizi n’Tichka pass',
    'tour-essaouira-walls': 'The historic city walls of Essaouira',
    'tour-grand-sahara': 'Shadows of a camel caravan across Erg Chebbi',
    'tour-grand-rabat': 'Hassan Tower behind the palms in Rabat',
}
backup = ROOT.parent / '.backups' / ('tour-photography-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
for name in ['data/media.seed.json', 'data/trips.seed.json', 'gallery.js', 'styles.css', 'PHOTO-SOURCES.md']:
    shutil.copy2(ROOT / name, backup / Path(name).name)
con = sqlite3.connect(ROOT / '.local/requests.sqlite3')
with sqlite3.connect(backup / 'requests.sqlite3') as target:
    con.backup(target)
media_seed = json.loads((ROOT / 'data/media.seed.json').read_text(encoding='utf-8'))
media = {m['id']: m for m in media_seed}
new_media = []
for source in manifest['sources']:
    identity = source['id']
    source['caption'] = captions.get(identity, source['caption'])
    original = ImageOps.exif_transpose(Image.open(ROOT / '.local/tour-photo-originals' / (identity + '.jpg'))).convert('RGB')
    assert original.width >= 1920
    variants = []
    for width in sorted(set([320, 640, 960, 1600, min(2400, original.width), min(3200, original.width)])):
        image = original.resize((width, round(original.height * width / original.width)), Image.Resampling.LANCZOS)
        path = '/assets/' + identity + '-' + str(width) + '.webp'
        image.save(ROOT / path.lstrip('/'), 'WEBP', quality=85, method=6)
        variants.append(dict(path=path, width=image.width, height=image.height))
    default = next(v for v in variants if v['width'] == 1600)
    item = dict(id=identity, name=source['caption'], alt=source['caption'], caption=source['caption'],
                **default, variants=variants, original_width=original.width, original_height=original.height,
                source=source['page'], source_original_width=source['width'], source_original_height=source['height'],
                author=source['author'], license=source['license'], license_url=source['license_url'],
                credit_required=True, modifications='Resized; cropped for display')
    new_media.append(item)
    media[identity] = item
    print('Prepared', identity, original.size, flush=True)

stamp = datetime.now(timezone.utc).isoformat()
with con:
    con.execute('BEGIN IMMEDIATE')
    live_ids = {r[0] for r in con.execute("SELECT id FROM documents WHERE kind='media'")}
    assert set(ids) <= live_ids | {m['id'] for m in new_media}
    for identity, gallery in galleries.items():
        row = con.execute("SELECT data,revision FROM documents WHERE kind='trip' AND id=?", (identity,)).fetchone()
        assert row, identity
        trip = json.loads(row[0])
        trip.update(gallery=gallery, image=gallery[0])
        con.execute("UPDATE documents SET data=?,revision=?,updated_at=? WHERE kind='trip' AND id=?",
                    (json.dumps(trip, ensure_ascii=False), row[1]+1, stamp, identity))
    for item in new_media:
        row = con.execute("SELECT revision FROM documents WHERE kind='media' AND id=?", (item['id'],)).fetchone()
        con.execute('INSERT INTO documents VALUES (?,?,?,?,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data,revision=excluded.revision,updated_at=excluded.updated_at',
                    ('media', item['id'], json.dumps(item, ensure_ascii=False), row[0]+1 if row else 1, stamp))
con.close()
trips = json.loads((ROOT / 'data/trips.seed.json').read_text(encoding='utf-8'))
for trip in trips:
    if trip['id'] in galleries:
        trip.update(gallery=galleries[trip['id']], image=galleries[trip['id']][0])
for path, data in [('data/media.seed.json', list(media.values())), ('data/trips.seed.json', trips), ('data/tour-photography.json', manifest)]:
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
with (ROOT / 'PHOTO-SOURCES.md').open('a', encoding='utf-8') as doc:
    doc.write('\n\n## Distinct multi-day tour galleries — September 2026\n\nDestination photographs illustrate the route, not a promise of specific accommodation. These WebP derivatives are resized and may be cropped for display. Each Creative Commons photograph retains its stated license; this does not license the site code.\n\n| Photo | Photographer | Download resolution | License |\n|---|---|---|---|\n')
    for s, m in zip(manifest['sources'], new_media):
        doc.write(f"| [{s['caption']}]({s['page']}) | {s['author']} | {m['original_width']} × {m['original_height']} | [{s['license']}]({s['license_url']}) |\n")
print(f'Imported {len(new_media)} photos; {len(ids)} unique images across {len(galleries)} tours. Backup: {backup}')
