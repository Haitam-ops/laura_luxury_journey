"""Validate published trip metadata, reviewed copy and itinerary place retention."""
from pathlib import Path
import json
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cms
from place_names import protect, matches, PLACES

with sqlite3.connect(ROOT / '.local/requests.sqlite3') as con:
    originals = {t['id']: t for t in cms.documents(con, 'trip') if t['status'] == 'published'}

count = 0
for code in ['en', 'fr', 'es', 'de', 'it', 'pt', 'nl']:
    payload = json.loads((ROOT / f'dist/data/content.{code}.json').read_text('utf-8'))
    titles = set()
    for trip in payload['trips']:
        source = originals[trip['id']]
        assert trip['seoTitle'] and trip['seoTitle'] not in titles, (code, trip['id'], 'title')
        titles.add(trip['seoTitle'])
        assert trip['seoDescription'] == trip['summary'] != payload['site']['collection_copy']
        assert trip['story'] and trip['itinerary'] and len(trip['faqs']) >= 4
        assert len(source['itinerary']) == len(trip['itinerary'])
        assert len(source['overnights']) == len(trip['overnights'])
        assert trip['faqs'][0]['answer'] == trip['duration']
        if trip['overnights']:
            assert trip['faqs'][1]['items'] == trip['overnights']
        for (original_heading, original), (translated_heading, translated) in zip(source['itinerary'], trip['itinerary']):
            for original_text, translated_text in [(original_heading, translated_heading), (original, translated)]:
                normalized, expected, found = protect(original_text, translated_text, code)
                assert normalized == translated_text, (code, trip['id'], 'unstable names')
                assert expected == found, (code, trip['id'], expected - found, found - expected)
                for start, end, name in matches(translated_text, {n: PLACES[n] for n in expected}):
                    assert translated_text[start:end] == name, (code, trip['id'], 'non-original name', name)
            normalized, expected, found = protect(original, translated, code)
            assert normalized == translated, (code, trip['id'], 'unstable names')
            assert expected == found, (code, trip['id'], expected - found, found - expected)
            assert not any('"' in p for p in [translated]), (code, trip['id'], 'quoted place')
        if code == 'fr':
            text = json.dumps({k:v for k,v in trip.items() if k != 'photos'}, ensure_ascii=False)
            for bad in ['Quad vélo', "s’installez", "s'installez", 'Late Après-midi', 'conseil d’administration', 'conseil d\'administration', 'Pick-up privé']:
                assert bad not in text, (trip['id'], bad)
        count += 1
print(f'PASS: {count} trip/language pages; unique titles, introductions, FAQs, overnight counts and itinerary places.')
