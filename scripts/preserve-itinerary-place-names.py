"""Repair and audit every itinerary paragraph before exporting public content."""
from pathlib import Path
import json
import shutil
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cms
from place_names import protect
from trip_editorial import route_heading


def main():
    with sqlite3.connect(ROOT / '.local/requests.sqlite3') as con:
        trips = cms.documents(con, 'trip')
        codes = [l['code'] for l in cms.document(con, 'languages', 'main')['document'] if l['enabled']]
    results, repaired = [], {}
    for code in codes:
        path = ROOT / 'data/locales' / (code + '.json')
        data = json.loads(path.read_text('utf-8')) if path.exists() else {'strings': {}}
        strings = data['strings']
        for trip in trips:
            for step, (heading, source) in enumerate(trip['itinerary'], 1):
                if '→' in heading:
                    strings[heading] = route_heading(heading, code)
                translated = source if code == 'en' else strings.get(source, source)
                source_parts, translated_parts = source.split('\n\n'), translated.split('\n\n')
                if len(source_parts) != len(translated_parts):
                    raise ValueError(f'Paragraph structure differs: {code}/{trip["id"]}/{step}')
                fixed_parts = []
                for paragraph, (original, target) in enumerate(zip(source_parts, translated_parts), 1):
                    fixed, expected, found = protect(original, target, code)
                    if expected != found:
                        raise ValueError(f'Unresolved places: {code}/{trip["id"]}/{step}/{paragraph}: {expected - found}; extra: {found - expected}')
                    if protect(original, fixed, code)[0] != fixed:
                        raise ValueError('Place normalization is not idempotent')
                    results.append(dict(language=code, trip=trip['id'], status=trip['status'], step=step,
                                        paragraph=paragraph, places=dict(expected), passed=True))
                    fixed_parts.append(fixed)
                strings[source] = '\n\n'.join(fixed_parts)
        repaired[path] = data
    # Validate the full set before writing any dictionary.
    for path, data in repaired.items():
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
        shutil.copy2(path, ROOT / 'dist/data/locales' / path.name)
    report = ROOT / '.local/itinerary-place-name-audit.json'
    report.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print(f'Passed {len(results)} individual paragraph checks across {len(trips)} itineraries and {len(codes)} languages.')
    print(f'Audit: {report}')


if __name__ == '__main__':
    main()
