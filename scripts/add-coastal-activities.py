"""Add the two coastal activities to the seed catalog and the existing local CMS."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
import json
import shutil
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cms

PHOTOS = [
    ('essaouira-kitesurf', '1636556767886-b4dc35bec5fe', 'JEkSxhq5juQ',
     'Andreea Munteanu', 'Kites above the beach in Essaouira'),
    ('taghazout-surf', '1706007472172-0a9a8fb1f990', 'P3rTRtR2Fc4',
     'Jarno Colijn', 'A surfer riding a wave at Anchor Point, Taghazout'),
    ('taghazout-coast', '1674227055590-85b99a24b69b', 'a7J_32Ee7AM',
     'sander traa', 'The beach and Atlantic coastline at Taghazout'),
]

TRIPS = [
    dict(
        id='essaouira-surf-kitesurf', title='Essaouira Surf & Kitesurf',
        category='experiences', days=0.17, duration='Half-day experience',
        start='Essaouira', end='Essaouira', image='essaouira-kitesurf',
        region='ESSAOUIRA · ATLANTIC COAST',
        summary='Trade the medina lanes for ocean air. Catch your first waves or discover the pull of a kite, with a coastal session shaped around your level and the Atlantic conditions.',
        story='Salt in the air, sand beneath your feet and the Atlantic stretching ahead: Essaouira invites you to experience Morocco from the water. Choose the rhythm of surfing or the energy of kitesurfing, then leave room for a relaxed stroll back through the medina.\n\nNew to the sport? Start with the basics on the beach and build confidence step by step. Already comfortable on the water? Tell us what you enjoy and we will help plan a session suited to your experience. Your chosen sport, lesson format and beach are agreed before booking, with wind and waves guiding the final plan.',
        fit='For travelers staying in Essaouira who want an active coastal escape, from a first lesson to a session tailored to existing experience. Participants need to be comfortable swimming in the sea.',
        pace='Active · tailored to your level',
        highlights=['Surf or kitesurf', 'Coaching for your level', 'Time on the Atlantic'],
        itinerary=[
            ['Choose your ocean adventure', 'Tell us whether you prefer surfing or kitesurfing, your swimming ability and any previous experience. Agree the lesson format, meeting point and equipment in advance. Allow a half day for preparation, your session and a little time to unwind.'],
            ['Meet, prepare & practice', 'Meet the activity team at the confirmed beach. Review the sea conditions, fit your equipment and begin with a briefing. Surf lessons introduce paddling and standing up; a first kitesurf lesson starts with kite control and the steps appropriate to your level.'],
            ['Find your rhythm', 'Follow your instructor through a session adapted to the conditions and your progress. Beginners build confidence gradually; experienced participants work on the goals agreed with their instructor. The amount of water time depends on the chosen sport and the weather.'],
            ['Slow down by the sea', 'Return your equipment and take a moment beside the ocean. Continue with a beach walk or head back to Essaouira for lunch and the medina at your own pace. Meals and any onward transport are separate.'],
        ],
        practical='This activity starts in Essaouira. Choose surf or kitesurf when enquiring; both sports are not automatically included in one session. The exact beach, lesson length, instructor language, equipment, participant requirements and weather cancellation terms are confirmed in your proposal. Bring swimwear, a towel, sun protection and water. A first kitesurf lesson may focus on land-based kite control rather than riding a board. Transfers from Marrakech and accommodation are arranged separately.',
        cover=['Your selected surf or kitesurf session and its agreed duration', 'Lesson format, instructor language and equipment specified in your proposal', 'Confirmed meeting point and any agreed local beach transfer'],
        extras='Meals, drinks, personal purchases, tips, accommodation and intercity transfers are separate. Additional lessons, a second sport, private coaching or equipment rental beyond your session can be requested and priced separately. Your proposal confirms the final inclusions.',
        overnights=[], gallery=['essaouira-kitesurf', 'route--leOF2nzJQ8', 'essaouira'],
    ),
    dict(
        id='taghazout-surf-kitesurf', title='Taghazout Surf & Kitesurf',
        category='experiences', days=0.17, duration='Half-day experience',
        start='Taghazout', end='Taghazout', image='taghazout-surf',
        region='TAGHAZOUT · ATLANTIC COAST',
        summary='Step into Taghazout’s surf life: ocean sessions, sandy feet and time to slow down by the sea. Choose surf coaching, or request a kitesurf session when local wind and availability allow.',
        story='Wake up to the ocean and make the coast part of your Morocco story. In Taghazout, a session in the waves pairs beautifully with an easy afternoon by the water. Whether you are learning to stand on a board or returning for another ride, the pleasure is in finding your own rhythm.\n\nSurfing is the heart of this experience, with the beach and coaching chosen for your level. If kitesurfing is what draws you to the coast, let us know: we will check suitable local conditions and an available activity team before confirming a session. Keep the rest of your day open for a seaside lunch, a village stroll or simply watching the waves.',
        fit='For travelers staying in Taghazout or nearby who want a first surf lesson or coaching suited to their experience. Kitesurfing is available by request and subject to local conditions and operator availability. Participants need to be comfortable swimming in the sea.',
        pace='Active · with a relaxed coastal finish',
        highlights=['Taghazout surf life', 'Coaching for your level', 'Kitesurf by request'],
        itinerary=[
            ['Plan your coastal session', 'Share your preferred sport, swimming ability and experience. Agree the lesson format and meeting point with the activity team. Surfing and kitesurfing have different requirements; kitesurf availability and the suitable beach are checked before confirmation.'],
            ['Pick the beach & prepare', 'Meet your activity team and review the day’s conditions. The session may take place at a suitable beach near Taghazout rather than directly in the village. Fit the agreed equipment and begin with a briefing and beach practice.'],
            ['Build confidence on the water', 'For surfing, practice the techniques appropriate to your level with your instructor’s guidance. For a confirmed kitesurf session, follow a progression based on your experience and the wind, beginning with kite control if you are new to the sport. A particular break or riding milestone is not guaranteed.'],
            ['Enjoy the village rhythm', 'Finish at the agreed point, return your equipment and leave time to enjoy the coast. A seaside lunch, a walk through Taghazout or a quiet hour watching the waves makes an easy finish. Meals and any extra transport are separate.'],
        ],
        practical='This is a local experience starting in Taghazout, not a day trip from Marrakech. Allow a half day; exact lesson length and any local transfers are confirmed before booking. Surf sessions depend on swell and tides; kitesurf sessions also require suitable wind, a suitable launch beach and an available operator. Your proposal specifies equipment, instructor language, participant requirements and weather cancellation terms. Bring swimwear, a towel, sun protection and water. A beginner kitesurf session does not promise independent board riding.',
        cover=['Your selected surf session, or a kitesurf session confirmed by arrangement', 'Lesson format, instructor language and equipment specified in your proposal', 'Confirmed meeting point and any agreed local beach transfer'],
        extras='Meals, drinks, personal purchases, tips, accommodation and transfers from Agadir or Marrakech are separate unless included in your proposal. A second sport, extra lessons, private coaching and extended equipment rental are optional additions priced separately.',
        overnights=[], gallery=['taghazout-surf', 'taghazout-coast'],
    ),
]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    from PIL import Image, ImageOps

    database = ROOT / '.local/requests.sqlite3'
    with sqlite3.connect(database) as con:
        backup = ROOT / '.local' / ('before-coastal-activities-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.sqlite3')
        with sqlite3.connect(backup) as saved:
            con.backup(saved)
        media_seed = json.loads((ROOT / 'data/media.seed.json').read_text(encoding='utf-8'))
        media_by_id = {m['id']: m for m in media_seed}
        originals = ROOT / '.local/coastal-photo-originals'
        originals.mkdir(exist_ok=True)
        for identity, photo, page, author, caption in PHOTOS:
            source = 'https://images.unsplash.com/photo-' + photo
            original = originals / (identity + '.jpg')
            if not original.exists():
                original.write_bytes(urlopen(Request(source + '?auto=format&fit=max&w=2400&q=90', headers={'User-Agent': 'LauraLuxuryJourneys-content'}), timeout=40).read())
            image = ImageOps.exif_transpose(Image.open(original)).convert('RGB')
            variants = []
            for width in [320, 640, 960, 1600, 2400]:
                if width > image.width:
                    continue
                resized = image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
                path = '/assets/' + identity + '-' + str(width) + '.webp'
                resized.save(ROOT / path.lstrip('/'), 'WEBP', quality=84, method=6)
                shutil.copy2(ROOT / path.lstrip('/'), ROOT / 'dist' / path.lstrip('/'))
                variants.append(dict(path=path, width=resized.width, height=resized.height))
            default = next((v for v in variants if v['width'] == 1600), variants[-1])
            media = dict(id=identity, name=caption, alt=caption, caption=caption, **default,
                         variants=variants, author=author, credit=author + ' / Unsplash',
                         source='https://unsplash.com/photos/' + page, source_url=source,
                         license='Unsplash License', license_url='https://unsplash.com/license')
            current = cms.document(con, 'media', identity)
            if not current or current['document'] != media:
                cms.save(con, 'media', identity, media, current['revision'] if current else 0)
            media_by_id[identity] = media
        write_json(ROOT / 'data/media.seed.json', list(media_by_id.values()))
        shutil.copy2(ROOT / 'data/media.seed.json', ROOT / 'dist/data/media.seed.json')
        seed = json.loads((ROOT / 'data/trips.seed.json').read_text(encoding='utf-8'))
        known = {t['id'] for t in seed}
        for offset, trip in enumerate(TRIPS):
            if trip['id'] not in known:
                seed.append(trip)
            current = cms.document(con, 'trip', trip['id'])
            if not current:
                published = dict(trip, status='published', order=26 + offset, translations={})
                cms.save(con, 'trip', trip['id'], cms.clean_trip(con, published), 0)
        write_json(ROOT / 'data/trips.seed.json', seed)
        shutil.copy2(ROOT / 'data/trips.seed.json', ROOT / 'dist/data/trips.seed.json')
    for name in ['stories.json', 'marketing-copy.json']:
        path = ROOT / 'data' / name
        data = json.loads(path.read_text(encoding='utf-8'))
        for trip in TRIPS:
            if name == 'stories.json':
                data[trip['id']] = trip['story']
            else:
                data.setdefault('trips', {})[trip['id']] = {key: trip[key] for key in ['title', 'summary', 'fit', 'story']}
        write_json(path, data)
        shutil.copy2(path, ROOT / 'dist/data' / name)
    strings_path = ROOT / 'data/source-strings.json'
    strings = set(json.loads(strings_path.read_text(encoding='utf-8')))
    def collect(value):
        if isinstance(value, str):
            strings.add(value)
        elif isinstance(value, list):
            for item in value:
                collect(item)
    for trip in TRIPS:
        for field in cms.LOCALE_FIELDS:
            collect(trip[field])
    for photo in PHOTOS:
        strings.add(photo[-1])
    write_json(strings_path, sorted(strings))
    print('Added Essaouira and Taghazout activities with three sourced photographs.')


if __name__ == '__main__':
    main()
