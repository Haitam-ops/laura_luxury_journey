"""Apply the English editorial copy without changing routes, media or booking data."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import json
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))
def write(path, value, compact=False):
    path.write_text(json.dumps(value, ensure_ascii=False, **({'separators': (',', ':')} if compact else {'indent': 2})) + '\n', encoding='utf-8')

editorial = read(ROOT / 'data/editorial-copy.json')
interface = read(ROOT / 'data/editorial-interface.json')
hero = read(ROOT / 'data/editorial-hero.json')
notes = read(ROOT / 'data/editorial-notes.json')
aliases = read(ROOT / 'data/editorial-aliases.json') if (ROOT / 'data/editorial-aliases.json').exists() else {}
aliases.update(interface)

def remember(old, new):
    if isinstance(old, str) and isinstance(new, str) and old != new:
        aliases[old] = new
    elif isinstance(old, list) and isinstance(new, list):
        for a, b in zip(old, new):
            remember(a, b)

def replace_fields(target, values):
    for key, value in values.items():
        if key in target:
            remember(target[key], value)
        target[key] = copy.deepcopy(value)

def update_trip(trip):
    changes = copy.deepcopy(editorial['trips'][trip['id']])
    steps = changes.pop('steps', None)
    if steps:
        assert len(steps) == len(trip['itinerary']), trip['id']
        changes['itinerary'] = [[row[0], paragraph] for row, paragraph in zip(trip['itinerary'], steps)]
    replace_fields(trip, changes)
    if 'cover' not in changes:
        cover = {
            'journeys': ['Comfortable, air-conditioned transport and where to meet your driver', 'Your accommodation for each night of the journey', 'The breakfasts and desert-camp dinners included in your stay', 'Local assistance, entrance tickets and camp transfers, clearly listed'],
            'daytrips': ['Your own driver and comfortable, air-conditioned transport', 'Where and when to meet, and your return arrangements', 'Local assistance, meals and entrance tickets, clearly listed'],
            'experiences': ['Your chosen activity and how long to allow', 'Your host or activity team and preferred language', 'Equipment, transport and any extras, clearly listed']
        }[trip['category']]
        replace_fields(trip, {'cover': cover})
    if 'extras' not in changes:
        replace_fields(trip, {'extras': 'Your proposal will show any additional meals, activities and other extras separately. Personal shopping and tips are not included. We’ll agree the final inclusions and cancellation terms with you before booking.'})
    return trip

with sqlite3.connect(ROOT / '.local/requests.sqlite3') as con:
    with con:
        for kind, identity, raw in con.execute("SELECT kind,id,data FROM documents WHERE kind IN ('trip','site')").fetchall():
            value = json.loads(raw)
            if kind == 'trip':
                update_trip(value)
            else:
                replace_fields(value, editorial['site'])
            if value != json.loads(raw):
                con.execute('UPDATE documents SET data=?,revision=revision+1,updated_at=? WHERE kind=? AND id=?',
                            (json.dumps(value, ensure_ascii=False, separators=(',', ':')), datetime.now(timezone.utc).isoformat(), kind, identity))

for prefix in ['data', 'dist/data']:
    folder = ROOT / prefix
    seed = read(folder / 'trips.seed.json')
    for trip in seed:
        update_trip(trip)
    write(folder / 'trips.seed.json', seed)
    for name in ['stories.json', 'marketing-copy.json']:
        path = folder / name
        data = read(path)
        if name == 'stories.json':
            for identity, fields in editorial['trips'].items():
                data[identity] = fields['story']
        else:
            replace_fields(data['site'], editorial['site'])
            for identity, fields in editorial['trips'].items():
                replace_fields(data['trips'][identity], {key: fields[key] for key in ['title', 'summary', 'story', 'fit']})
        write(path, data)
    for path in folder.glob('content*.json'):
        data = read(path)
        if data['language']['code'] != 'en':
            continue
        replace_fields(data['site'], editorial['site'])
        for trip in data['trips']:
            update_trip(trip)
        write(path, data, compact=True)

# Keep the previous day-trip update compatible with this editorial revision.
path = ROOT / 'data/daytrip-itineraries.json'
daytrips = read(path)
for identity, fields in daytrips.items():
    for key in list(fields):
        if key in editorial['trips'][identity]:
            fields[key] = editorial['trips'][identity][key]
write(path, daytrips)

# Source text also appears in templates and the CMS's fresh-install defaults.
base_site = read(ROOT / '.local/editorial-before-20260926/data/content.json')['site']
for key, value in editorial['site'].items():
    remember(base_site[key], value)
for prefix in ['', 'dist/']:
    for name in ['index.html', 'app.js', 'boot.js', 'gallery.js', 'route-map.js']:
        path = ROOT / (prefix + name)
        source = path.read_text(encoding='utf-8')
        if name == 'index.html':
            source = source.replace('<option value="Shared">Shared with other travelers</option>', '')
            source = source.replace('<option value="Flexible">Help me decide</option>', '')
            # These headings contain line breaks, so their visible text is not contiguous.
            source = source.replace('Plan with<br><em>more confidence.</em>', 'A little insight<br><em>before you go.</em>')
            source = source.replace('Before<br><em>you enquire.</em>', 'Before<br><em>we begin.</em>')
            source = source.replace('Let’s plan<br><em>your Morocco.</em>', 'Where would you<br><em>love to go?</em>')
            source = source.replace('Your Morocco.<br><em>At your pace.</em>', 'Come closer<br><em>to Morocco.</em>')
            source = source.replace('Find the journey<br><em>that fits you.</em>', 'Where will Morocco<br><em>take you?</em>')
        for old, new in sorted(aliases.items(), key=lambda item: len(item[0]), reverse=True):
            if name.endswith('.js'):
                # Curly apostrophes keep replacements safe inside existing JS string literals.
                new = new.replace("'", '’')
            source = source.replace(old, new)
        if name == 'app.js':
            begin = source.index(' en:', source.index('const heroEditorial='))
            end = source.index(' fr:{common:', begin)
            source = source[:begin] + ' en:' + json.dumps(hero, ensure_ascii=False) + ',\n' + source[end:]
            for key, note in notes.items():
                pattern = re.compile(r'^' + key + r":\{.*?\},$", re.M)
                replacement = key + ':' + json.dumps(note, ensure_ascii=False) + ','
                source, count = pattern.subn(lambda _: replacement, source)
                assert count == 1, (path, key, count)
        path.write_text(source, encoding='utf-8')

# Retain the legacy catalog constructor and IDs; update only its public content.
for prefix in ['', 'dist/']:
    path = ROOT / (prefix + 'trips.js')
    source = path.read_text(encoding='utf-8')
    for old, new in sorted(aliases.items(), key=lambda item: len(item[0]), reverse=True):
        source = source.replace(old, new.replace("'", '’'))
    path.write_text(source, encoding='utf-8')
path = ROOT / 'cms.py'
source = path.read_text(encoding='utf-8')
for key, value in editorial['site'].items():
    source = source.replace(repr(base_site[key]), repr(value))
path.write_text(source, encoding='utf-8')

# Keep existing language editions working by carrying forward their translations
# for equivalent source text. This is an English editorial pass, not a new machine translation.
def alias_translations(strings, english=False):
    for old, new in aliases.items():
        if english:
            strings[new] = new
        elif old in strings and strings[old] != old and new not in strings:
            strings[new] = strings[old]

for path in (ROOT / 'data/locales').glob('*.json'):
    if path.stem not in {'fr', 'es', 'de', 'it', 'pt', 'nl'}:
        continue
    data = read(path)
    alias_translations(data['strings'], path.stem == 'en')
    write(path, data)
for prefix in ['data', 'dist/data']:
    for path in (ROOT / prefix).glob('content*.json'):
        data = read(path)
        alias_translations(data['strings'], data['language']['code'] == 'en')
        write(path, data, compact=True)
strings = set(read(ROOT / 'data/source-strings.json'))
strings.update(aliases.values())
write(ROOT / 'data/source-strings.json', sorted(strings))
write(ROOT / 'data/editorial-aliases.json', aliases)
print(f'Applied English editorial copy to {len(editorial["trips"])} trips, all five hero slides, templates and travel notes.')
