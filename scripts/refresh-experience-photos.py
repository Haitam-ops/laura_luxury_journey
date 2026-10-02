"""Import visually reviewed activity photos into local CMS and static content."""
from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import sqlite3
import sys
import requests
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cms


def main():
    manifest = json.loads((ROOT / 'scripts/experience-photos.json').read_text(encoding='utf-8'))
    cache = ROOT / '.local/experience-photo-review'
    cache.mkdir(exist_ok=True)
    media = {m['id']: m for m in json.loads((ROOT / 'data/media.seed.json').read_text(encoding='utf-8'))}
    imported = []
    for photo in manifest['photos']:
        identity = photo['id']
        original = ROOT / photo['local_file'] if photo.get('local_file') else cache / (identity + '.original')
        if not original.exists() and not photo.get('local_file'):
            response = requests.get(photo['url'], timeout=45)
            response.raise_for_status()
            original.write_bytes(response.content)
        image = ImageOps.exif_transpose(Image.open(original)).convert('RGB')
        variants = []
        for width in sorted(set([w for w in [320, 640, 960, 1600, 2400] if w <= image.width] + [min(image.width, 2400)])):
            resized = image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
            relative = f'/assets/{identity}-{width}.webp'
            target = ROOT / relative.lstrip('/')
            resized.save(target, 'WEBP', quality=88, method=6)
            shutil.copy2(target, ROOT / 'dist' / relative.lstrip('/'))
            variants.append(dict(path=relative, width=resized.width, height=resized.height))
        default = min(variants, key=lambda v: abs(v['width'] - 1600))
        entry = dict(id=identity, name=photo.get('name', photo['caption']), alt=photo.get('alt', photo['caption']), caption=photo['caption'],
                     **default, variants=variants, source=photo['source'], source_url=photo.get('url', photo['source']),
                     author=photo['author'], credit=photo['author'], license=photo['license'],
                     original_width=image.width, original_height=image.height, focal_point=photo['focal_point'])
        if photo['license'] == 'Pexels License':
            entry['license_url'] = 'https://www.pexels.com/license/'
        elif photo['license'] == 'Unsplash License':
            entry['license_url'] = 'https://unsplash.com/license'
        elif photo['license'] != 'User supplied':
            entry['reuse_permission_verified'] = False
        media[identity] = entry
        imported.append(entry)
    database = ROOT / '.local/requests.sqlite3'
    with sqlite3.connect(database) as connection:
        backup = ROOT / '.local' / ('before-experience-photos-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.sqlite3')
        with sqlite3.connect(backup) as saved:
            connection.backup(saved)
        for entry in imported:
            current = cms.document(connection, 'media', entry['id'])
            cms.save(connection, 'media', entry['id'], entry, current['revision'] if current else 0)
        for identity, gallery in manifest['galleries'].items():
            current = cms.document(connection, 'trip', identity)
            updated = dict(current['document'], gallery=gallery, image=gallery[0])
            cms.save(connection, 'trip', identity, updated, current['revision'])
    seeds = json.loads((ROOT / 'data/trips.seed.json').read_text(encoding='utf-8'))
    for trip in seeds:
        if trip['id'] in manifest['galleries']:
            trip['gallery'] = manifest['galleries'][trip['id']]
            trip['image'] = trip['gallery'][0]
    for name, value in [('media.seed.json', list(media.values())), ('trips.seed.json', seeds)]:
        target = ROOT / 'data' / name
        target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        shutil.copy2(target, ROOT / 'dist/data' / name)
    print(f'Imported {len(imported)} photos; updated {len(manifest["galleries"])} experience galleries. Backup: {backup.name}')


if __name__ == '__main__':
    main()
