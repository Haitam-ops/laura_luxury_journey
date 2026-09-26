"""Apply the private day-trip editorial update to the seed and existing local CMS."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
UPDATES = json.loads((ROOT / 'data/daytrip-itineraries.json').read_text(encoding='utf-8'))


def revise(trip):
    changes = UPDATES.get(trip['id'])
    if not changes:
        return trip
    trip.update(changes)
    trip['cover'][0] = 'Private air-conditioned vehicle and driver for your party'
    for translation in trip.get('translations', {}).values():
        for field in changes:
            translation.pop(field, None)
        translation.pop('cover', None)
    return trip


def export_content():
    """Refresh changed fields while preserving unrelated static content."""
    sys.path.insert(0, str(ROOT))
    import cms
    changed_strings = set()
    def collect(value):
        if isinstance(value, str):
            changed_strings.add(value)
        elif isinstance(value, dict):
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
    collect(UPDATES)
    with sqlite3.connect(ROOT / '.local/requests.sqlite3') as con:
        for path in [*ROOT.glob('data/content*.json'), *ROOT.glob('dist/data/content*.json')]:
            payload = json.loads(path.read_text(encoding='utf-8'))
            code = payload['language']['code']
            fresh = cms.public_content(con, code)
            lookup = {t['id']: t for t in fresh['trips']}
            for trip in payload['trips']:
                if trip['id'] in UPDATES:
                    for field in set(UPDATES[trip['id']]) | {'cover'}:
                        trip[field] = lookup[trip['id']][field]
            payload['strings'].update({key: value for key, value in fresh['strings'].items()
                                       if key in changed_strings})
            path.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print('Refreshed existing static language payloads.')


def main():
    database = ROOT / '.local/requests.sqlite3'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = ROOT / '.local' / ('before-daytrip-itineraries-' + stamp + '.sqlite3')
    with sqlite3.connect(database) as con:
        with sqlite3.connect(backup) as saved:
            con.backup(saved)
        with con:
            for identity in UPDATES:
                row = con.execute("SELECT data FROM documents WHERE kind='trip' AND id=?", (identity,)).fetchone()
                if not row:
                    raise ValueError('Missing existing trip: ' + identity)
                before = json.loads(row[0])
                after = revise(json.loads(row[0]))
                if after != before:
                    con.execute("UPDATE documents SET data=?,revision=revision+1,updated_at=? WHERE kind='trip' AND id=?",
                                (json.dumps(after, ensure_ascii=False, separators=(',', ':')),
                                 datetime.now(timezone.utc).isoformat(), identity))
    for seed_file in [ROOT / 'data/trips.seed.json', ROOT / 'dist/data/trips.seed.json']:
        seed = json.loads(seed_file.read_text(encoding='utf-8'))
        seed_file.write_text(json.dumps([revise(t) for t in seed], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for path in [ROOT / prefix / name for prefix in ['data', 'dist/data'] for name in ['stories.json', 'marketing-copy.json']]:
        name = path.name
        data = json.loads(path.read_text(encoding='utf-8'))
        for identity, changes in UPDATES.items():
            if name == 'stories.json' and 'story' in changes:
                data[identity] = changes['story']
            elif name == 'marketing-copy.json':
                entry = data.get('trips', {}).get(identity)
                if isinstance(entry, dict):
                    entry.update({k: v for k, v in changes.items() if k in entry})
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    strings_path = ROOT / 'data/source-strings.json'
    strings = set(json.loads(strings_path.read_text(encoding='utf-8')))
    def collect(value):
        if isinstance(value, str):
            strings.add(value)
        elif isinstance(value, dict):
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
    collect(UPDATES)
    strings_path.write_text(json.dumps(sorted(strings), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Updated five private day trips; CMS backup:', backup.name)


if __name__ == '__main__':
    if '--export-only' not in sys.argv:
        main()
    export_content()
