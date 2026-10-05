"""Local CMS: revisioned documents, owner sessions and validated image uploads."""
from pathlib import Path
from datetime import datetime, timezone
from http.cookies import SimpleCookie
import hashlib
import hmac
import io
import json
import re
import secrets
import time

ROOT = Path(__file__).resolve().parent
LANGUAGES = [
    ('en', 'English', 'English', 'ltr'), ('fr', 'French', 'Français', 'ltr'),
    ('es', 'Spanish', 'Español', 'ltr'),
    ('de', 'German', 'Deutsch', 'ltr'), ('it', 'Italian', 'Italiano', 'ltr'),
    ('pt', 'Portuguese', 'Português', 'ltr'), ('nl', 'Dutch', 'Nederlands', 'ltr')
]
SITE = {'brand': 'Laura Luxury Journeys', 'tagline': 'Morocco, with time for what matters to you.',
        'hero_eyebrow': 'MOROCCO WITH LAURA LUXURY JOURNEYS', 'hero_title': 'Come closer',
        'hero_emphasis': 'to Morocco.',
        'hero_copy': 'A morning in the medina, a road through the Atlas, an evening beside the dunes. Discover Morocco with a little more time for the things you love.',
        'collection_title': 'Where will Morocco', 'collection_emphasis': 'take you?',
        'collection_copy': 'Follow the coast, spend a night in the Sahara or step away from the city for the day. Find a journey that speaks to you, and we’ll help you make it your own.',
        'about_title': 'A lovely trip begins with a conversation.',
        'about_copy': 'Perhaps you have a route in mind. Perhaps it’s a desert evening, a beautiful riad or simply a change of scene. Tell us what draws you to Morocco, and we’ll take it from there.',
        'email': '', 'phone': '', 'whatsapp': '', 'address': '',
        'instagram': '', 'facebook': '', 'tiktok': '', 'youtube': '',
        'hero_images': ['hero-marrakech-20260926', 'hero-quad-20260926', 'hero-sahara-20260926', 'hero-sahara2-20260926', 'hero-chefchaouen-20260926'], 'translations': {}}
CAPTIONS = {'sahara': 'The dunes of the Moroccan Sahara', 'camels': 'A camel caravan near Merzouga',
            'chefchaouen': 'Blue houses in Chefchaouen', 'marrakech': 'Traditional architecture in Marrakech',
            'oasis': 'An oasis village in southern Morocco', 'ouzoud': 'Ouzoud waterfalls',
            'agafay': 'Agafay and the Atlas horizon', 'essaouira': 'Fishing boats in Essaouira harbor',
            'atlas': 'The High Atlas valley at Imlil', 'fes': 'The rooftops of Fes'}
TEXT_FIELDS = {'title', 'duration', 'start', 'end', 'region', 'summary', 'story', 'fit', 'pace', 'practical', 'extras'}
ARRAY_FIELDS = {'highlights', 'cover', 'overnights'}
LOCALE_FIELDS = TEXT_FIELDS | ARRAY_FIELDS | {'itinerary'}
ATTEMPTS = {}


def stamp():
    return datetime.now(timezone.utc).isoformat()


def pack(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def initialize(con):
    con.executescript('''
      CREATE TABLE IF NOT EXISTS documents(kind TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL,
        revision INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL, PRIMARY KEY(kind,id));
      CREATE TABLE IF NOT EXISTS owner(username TEXT PRIMARY KEY, salt TEXT NOT NULL, password_hash TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY, csrf TEXT NOT NULL, username TEXT NOT NULL, expires REAL NOT NULL);
      CREATE TABLE IF NOT EXISTS inquiry_status(reference TEXT PRIMARY KEY, status TEXT NOT NULL);
    ''')
    if not con.execute("SELECT 1 FROM documents WHERE kind='site'").fetchone():
        seed = json.loads((ROOT / 'data/trips.seed.json').read_text(encoding='utf-8'))
        stories = json.loads((ROOT / 'data/stories.json').read_text(encoding='utf-8'))
        for i, trip in enumerate(seed):
            trip.update(status='published', order=i, gallery=trip.get('gallery', [trip['image']]), story=stories.get(trip['id'], ''), translations={})
            con.execute('INSERT OR IGNORE INTO documents VALUES (?,?,?,?,?)', ('trip', trip['id'], pack(trip), 1, stamp()))
        media = json.loads((ROOT / 'data/media.seed.json').read_text(encoding='utf-8')) if (ROOT / 'data/media.seed.json').exists() else []
        if not media:
            media = [{'id': p.stem, 'path': '/assets/' + p.name, 'name': p.stem.replace('-', ' ').title(),
                      'alt': CAPTIONS.get(p.stem, 'Morocco destination photography'),
                      'caption': CAPTIONS.get(p.stem, 'Morocco destination photography'), 'source': 'Unsplash; see assets/sources.txt'}
                     for p in sorted((ROOT / 'assets').glob('*.webp'))]
        for item in media:
            con.execute('INSERT OR IGNORE INTO documents VALUES (?,?,?,?,?)', ('media', item['id'], pack(item), 1, stamp()))
        con.execute('INSERT INTO documents VALUES (?,?,?,?,?)', ('site', 'main', pack(SITE), 1, stamp()))
        languages = [{'code': c, 'name': n, 'native': native, 'dir': direction, 'enabled': True} for c, n, native, direction in LANGUAGES]
        con.execute('INSERT INTO documents VALUES (?,?,?,?,?)', ('languages', 'main', pack(languages), 1, stamp()))
    con.commit()


def document(con, kind, identity):
    row = con.execute('SELECT data,revision,updated_at FROM documents WHERE kind=? AND id=?', (kind, identity)).fetchone()
    return {'document': json.loads(row[0]), 'revision': row[1], 'updated_at': row[2]} if row else None


def documents(con, kind):
    return [{**json.loads(raw), 'revision': rev, 'updated_at': updated}
            for raw, rev, updated in con.execute('SELECT data,revision,updated_at FROM documents WHERE kind=? ORDER BY rowid', (kind,))]


class Conflict(ValueError):
    pass


def save(con, kind, identity, data, revision):
    if type(revision) is not int or revision < 0:
        raise ValueError('A document revision is required. Reload the editor.')
    con.execute('BEGIN IMMEDIATE')
    current = document(con, kind, identity)
    if (current['revision'] if current else 0) != revision:
        con.rollback()
        raise Conflict('Someone saved a newer version. Reload this section before saving again. Your edits have not been overwritten.')
    con.execute('INSERT INTO documents VALUES (?,?,?,?,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data,revision=excluded.revision,updated_at=excluded.updated_at',
                (kind, identity, pack(data), revision + 1, stamp()))
    con.commit()
    return {'revision': revision + 1, 'document': data}


def text_value(value, maximum=5000):
    if not isinstance(value, str) or len(value) > maximum or '\x00' in value:
        raise ValueError('Check the text fields and their length.')
    return value.strip()


def string_list(value, maximum=30):
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError('Too many list items.')
    return [text_value(v, 1200) for v in value if v != '']


def localized_fields(raw, allowed):
    if not isinstance(raw, dict) or len(raw) > 40:
        raise ValueError('Invalid translations.')
    result = {}
    for code, fields in raw.items():
        if not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z]{2,4})?', code) or not isinstance(fields, dict):
            raise ValueError('Invalid language code.')
        result[code] = clean_fields(fields, allowed)
    return result


def clean_fields(raw, allowed):
    out = {}
    for key in allowed:
        if key not in raw:
            continue
        if key in ARRAY_FIELDS:
            out[key] = string_list(raw[key])
        elif key == 'itinerary':
            if not isinstance(raw[key], list) or len(raw[key]) > 40 or any(not isinstance(row, list) or len(row) != 2 for row in raw[key]):
                raise ValueError('Each itinerary step needs a heading and description.')
            out[key] = [[text_value(row[0], 250), text_value(row[1], 5000)] for row in raw[key]]
        else:
            out[key] = text_value(raw[key], 15000 if key == 'story' else 5000)
    return out


def clean_trip(con, raw):
    if not isinstance(raw, dict):
        raise ValueError('A trip is required.')
    identity = raw.get('id', '')
    if not isinstance(identity, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identity) or len(identity) > 100 or identity == 'custom':
        raise ValueError('Use a unique URL slug with lowercase letters, numbers and hyphens.')
    out = clean_fields(raw, LOCALE_FIELDS)
    for key in TEXT_FIELDS:
        out.setdefault(key, '')
    for key in ARRAY_FIELDS | {'itinerary'}:
        out.setdefault(key, [])
    if not out['title'] or not out['start'] or not out['end'] or not out['duration']:
        raise ValueError('Title, start, finish and duration are required.')
    if raw.get('category') not in {'journeys', 'daytrips', 'experiences'} or raw.get('status') not in {'published', 'draft', 'archived'}:
        raise ValueError('Choose a valid category and publication status.')
    if type(raw.get('days')) not in {int, float} or not 0 < raw['days'] <= 365:
        raise ValueError('Duration for sorting must be between 0 and 365 days.')
    gallery = string_list(raw.get('gallery', []), 18)
    if len(set(gallery)) != len(gallery) or any(not document(con, 'media', identity) for identity in gallery):
        raise ValueError('Choose distinct photographs from the media library.')
    if raw['status'] == 'published' and (not gallery or not out['summary'] or not out['itinerary']):
        raise ValueError('Published trips need a cover photo, summary and itinerary.')
    if raw['status'] == 'published' and any(not title or not description for title, description in out['itinerary']):
        raise ValueError('Complete the heading and description for every itinerary step before publishing.')
    order = raw.get('order', 100)
    if type(order) is not int or not 0 <= order <= 10000:
        raise ValueError('Display order must be a whole number from 0 to 10000.')
    out.update(id=identity, category=raw['category'], status=raw['status'], days=raw['days'], order=order,
               gallery=gallery, image=gallery[0] if gallery else '', translations=localized_fields(raw.get('translations', {}), LOCALE_FIELDS))
    return out


def clean_site(con, raw):
    if not isinstance(raw, dict):
        raise ValueError('Site content is required.')
    out = {key: text_value(raw.get(key, default), 5000) for key, default in SITE.items() if key not in {'translations', 'hero_images'}}
    if not out['brand'] or not out['hero_title']:
        raise ValueError('Brand name and hero title are required.')
    if out['email'] and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', out['email']):
        raise ValueError('Enter a valid public email address.')
    for field in ('phone', 'whatsapp'):
        if out[field] and not re.fullmatch(r'[+\d ()-]{6,25}', out[field]):
            raise ValueError('Use a phone number with country code, for example +212…')
    from urllib.parse import urlsplit
    for field, domains in {'instagram': {'instagram.com', 'www.instagram.com'}, 'facebook': {'facebook.com', 'www.facebook.com', 'm.facebook.com'},
                           'tiktok': {'tiktok.com', 'www.tiktok.com'}, 'youtube': {'youtube.com', 'www.youtube.com', 'youtu.be'}}.items():
        if out[field]:
            parsed = urlsplit(out[field])
            if parsed.scheme != 'https' or parsed.hostname not in domains or parsed.username or parsed.password:
                raise ValueError('Use the full HTTPS profile link for ' + field + '.')
    out['hero_images'] = string_list(raw.get('hero_images', SITE['hero_images']), 5)
    if len(out['hero_images']) != 5 or any(not document(con, 'media', identity) for identity in out['hero_images']):
        raise ValueError('Choose five homepage photographs.')
    out['translations'] = localized_fields(raw.get('translations', {}), set(out) - {'hero_images', 'email', 'phone', 'whatsapp', 'address'})
    return out


def translation(con, code):
    saved = document(con, 'locale', code)
    if saved:
        return saved
    path = ROOT / 'data/locales' / (code + '.json')
    data = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {'strings': {}, 'reviewed': code == 'en', 'origin': 'manual'}
    if code == 'en':
        source = ROOT / 'data/source-strings.json'
        data['strings'] = {v: v for v in json.loads(source.read_text(encoding='utf-8'))} if source.exists() else {}
    return {'document': data, 'revision': 0}


def translate_tree(value, strings):
    if isinstance(value, str):
        return strings.get(value) or value
    if isinstance(value, list):
        return [translate_tree(v, strings) for v in value]
    return value


def public_content(con, code):
    langs = document(con, 'languages', 'main')['document']
    active = [v for v in langs if v['enabled']]
    lang = next((v for v in active if v['code'] == code), next(v for v in active if v['code'] == 'en'))
    code = lang['code']
    strings = translation(con, code)['document']['strings']
    def localize(raw, fields):
        out = {key: translate_tree(val, strings) if key in fields else val for key, val in raw.items() if key not in {'translations', 'revision', 'updated_at', 'status'}}
        if code != 'en':
            out.update(raw.get('translations', {}).get(code, {}))
        return out
    media = {item['id']: localize(item, {'alt', 'caption', 'modifications'}) for item in documents(con, 'media')}
    trips = []
    for raw in sorted(documents(con, 'trip'), key=lambda t: t['order']):
        if raw['status'] != 'published':
            continue
        item = localize(raw, LOCALE_FIELDS)
        # Route headings retain the original place names in every language.
        for index, (heading, _) in enumerate(raw.get('itinerary', [])):
            if '→' in heading and index < len(item.get('itinerary', [])):
                item['itinerary'][index] = [heading, item['itinerary'][index][1]]
        item['photos'] = [media[identity] for identity in item['gallery'] if identity in media]
        trips.append(item)
    site = localize(document(con, 'site', 'main')['document'], set(SITE) - {'hero_images', 'email', 'phone', 'whatsapp', 'address', 'brand'})
    return {'trips': trips, 'site': site, 'media': media, 'languages': active, 'language': lang, 'strings': strings}


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 600000).hex()


def session(handler, con):
    try:
        cookie = SimpleCookie(handler.headers.get('Cookie', ''))
        token = cookie['dg_admin'].value if 'dg_admin' in cookie else ''
    except Exception:
        return None
    if not re.fullmatch(r'[a-f0-9]{64}', token):
        return None
    digest = hashlib.sha256(token.encode()).hexdigest()
    row = con.execute('SELECT csrf,username FROM sessions WHERE token_hash=? AND expires>?', (digest, time.time())).fetchone()
    return {'csrf': row[0], 'username': row[1], 'digest': digest} if row else None


def new_session(handler, con, username):
    token, csrf = secrets.token_hex(32), secrets.token_hex(32)
    con.execute('DELETE FROM sessions WHERE expires<?', (time.time(),))
    con.execute('INSERT INTO sessions VALUES (?,?,?,?)', (hashlib.sha256(token.encode()).hexdigest(), csrf, username, time.time() + 28800))
    con.commit()
    handler.extra_headers = {'Set-Cookie': 'dg_admin=' + token + '; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800'}
    return {'authenticated': True, 'username': username, 'csrf': csrf, 'setupRequired': False}


def get(handler, con, path, query):
    if path == '/api/content':
        return handler.reply(200, public_content(con, query.get('lang', ['en'])[0]))
    if path == '/api/admin/session':
        current = session(handler, con)
        return handler.reply(200, {'authenticated': bool(current), 'setupRequired': not bool(con.execute('SELECT 1 FROM owner').fetchone()),
                                   'csrf': current['csrf'] if current else None, 'username': current['username'] if current else None})
    current = session(handler, con)
    if not current:
        return handler.reply(401, {'error': 'Please sign in to the admin dashboard.'})
    if path == '/api/admin/data':
        inquiries = [{'reference': ref, 'created_at': created, **json.loads(payload), 'status': status or 'new'}
                     for ref, created, payload, status in con.execute('SELECT i.reference,i.created_at,i.payload,s.status FROM inquiries i LEFT JOIN inquiry_status s ON i.reference=s.reference ORDER BY i.created_at DESC')]
        return handler.reply(200, {'trips': documents(con, 'trip'), 'media': documents(con, 'media'),
                                  'site': document(con, 'site', 'main'), 'languages': document(con, 'languages', 'main'), 'inquiries': inquiries})
    if path == '/api/admin/locale':
        code = query.get('code', ['en'])[0]
        if not any(v['code'] == code for v in document(con, 'languages', 'main')['document']):
            return handler.reply(404, {'error': 'Language not found.'})
        return handler.reply(200, translation(con, code))
    return handler.reply(404, {'error': 'Page not found.'})


def post(handler, con, path):
    if path in {'/api/admin/setup', '/api/admin/login'}:
        data = handler.read_json(4000)
        username = text_value(data.get('username', ''), 100)
        password = data.get('password', '')
        if not isinstance(password, str) or not 12 <= len(password) <= 200 or not re.fullmatch(r'[A-Za-z0-9@._-]{3,100}', username):
            raise ValueError('Use a username of at least 3 characters and a password of at least 12 characters.')
        attempts = ATTEMPTS.setdefault(handler.client_address[0], [])
        attempts[:] = [t for t in attempts if t > time.time() - 60]
        if len(attempts) >= 6:
            return handler.reply(429, {'error': 'Too many sign-in attempts. Try again in one minute.'})
        attempts.append(time.time())
        if path.endswith('/setup'):
            con.execute('BEGIN IMMEDIATE')
            if con.execute('SELECT 1 FROM owner').fetchone():
                con.rollback()
                return handler.reply(409, {'error': 'An owner already exists. Sign in instead.'})
            salt = secrets.token_hex(16)
            con.execute('INSERT INTO owner VALUES (?,?,?)', (username, salt, password_hash(password, salt)))
            con.commit()
        else:
            row = con.execute('SELECT salt,password_hash FROM owner WHERE username=?', (username,)).fetchone()
            salt = row[0] if row else '00' * 16
            calculated = password_hash(password, salt)
            if not row or not hmac.compare_digest(calculated, row[1]):
                return handler.reply(401, {'error': 'Username or password is incorrect.'})
        attempts.clear()
        return handler.reply(200, new_session(handler, con, username))
    current = session(handler, con)
    if not current:
        return handler.reply(401, {'error': 'Your admin session expired. Sign in again.'})
    if not hmac.compare_digest(handler.headers.get('X-CSRF-Token', ''), current['csrf']):
        return handler.reply(403, {'error': 'Please reload the dashboard before saving.'})
    if path == '/api/admin/logout':
        con.execute('DELETE FROM sessions WHERE token_hash=?', (current['digest'],))
        con.commit()
        handler.extra_headers = {'Set-Cookie': 'dg_admin=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'}
        return handler.reply(200, {'ok': True})
    if path == '/api/admin/upload':
        from PIL import Image, ImageOps, UnidentifiedImageError
        raw = handler.read_body(12 * 1024 * 1024)
        try:
            Image.MAX_IMAGE_PIXELS = 40000000
            with Image.open(io.BytesIO(raw)) as probe:
                if probe.format not in {'JPEG', 'PNG', 'WEBP'} or probe.width * probe.height > 40000000 or min(probe.size) < 160:
                    raise ValueError('Choose a JPG, PNG or WebP photograph, at least 160 pixels wide and high, up to 40 megapixels.')
                probe.verify()
            with Image.open(io.BytesIO(raw)) as source:
                picture = ImageOps.exif_transpose(source).convert('RGB')
                picture.thumbnail((2400, 2400))
                output = io.BytesIO()
                picture.save(output, format='WEBP', quality=86)
                width, height = picture.size
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
            raise ValueError('This file is not a readable JPG, PNG or WebP photograph.')
        encoded = output.getvalue()
        identity = 'upload-' + hashlib.sha256(encoded).hexdigest()[:24]
        existing = document(con, 'media', identity)
        if existing:
            return handler.reply(200, existing)
        directory = ROOT / 'uploads'
        directory.mkdir(exist_ok=True)
        (directory / (identity + '.webp')).write_bytes(encoded)
        from urllib.parse import unquote
        name = text_value(unquote(handler.headers.get('X-Filename', 'New photograph')), 200)
        item = {'id': identity, 'name': name, 'path': '/uploads/' + identity + '.webp', 'alt': name,
                'caption': '', 'source': '', 'width': width, 'height': height}
        return handler.reply(201, save(con, 'media', identity, item, 0))
    data = handler.read_json(1500000)
    if path == '/api/admin/trips':
        value = clean_trip(con, data.get('document'))
        return handler.reply(200, save(con, 'trip', value['id'], value, data.get('revision')))
    if path == '/api/admin/site':
        value = clean_site(con, data.get('document'))
        return handler.reply(200, save(con, 'site', 'main', value, data.get('revision')))
    if path == '/api/admin/media':
        raw = data.get('document', {})
        original = document(con, 'media', raw.get('id', ''))
        if not original:
            raise ValueError('Photograph not found.')
        value = original['document'].copy()
        for field in ('name', 'alt', 'caption', 'source'):
            value[field] = text_value(raw.get(field, ''), 1000)
        if not value['alt']:
            raise ValueError('Describe the photograph for visitors using screen readers.')
        return handler.reply(200, save(con, 'media', value['id'], value, data.get('revision')))
    if path == '/api/admin/languages':
        raw = data.get('document')
        if not isinstance(raw, list) or not 1 <= len(raw) <= 40:
            raise ValueError('Choose between 1 and 40 languages.')
        value, codes = [], set()
        for item in raw:
            code = text_value(item.get('code', ''), 12)
            if not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z]{2,4})?', code) or code in codes or item.get('dir') not in {'rtl', 'ltr'}:
                raise ValueError('Each language needs a unique valid code and text direction.')
            codes.add(code)
            value.append({'code': code, 'name': text_value(item.get('name', ''), 60), 'native': text_value(item.get('native', ''), 60),
                          'dir': item['dir'], 'enabled': bool(item.get('enabled'))})
        if not any(v['code'] == 'en' and v['enabled'] for v in value):
            raise ValueError('Keep English enabled as the source language.')
        return handler.reply(200, save(con, 'languages', 'main', value, data.get('revision')))
    if path == '/api/admin/locale':
        code = data.get('code', '')
        if not any(v['code'] == code for v in document(con, 'languages', 'main')['document']):
            raise ValueError('Choose an existing language.')
        raw = data.get('document', {})
        if not isinstance(raw, dict) or not isinstance(raw.get('strings'), dict) or len(raw['strings']) > 5000:
            raise ValueError('Invalid translation dictionary.')
        value = {'strings': {text_value(k, 15000): text_value(v, 15000) for k, v in raw['strings'].items()},
                 'reviewed': bool(raw.get('reviewed')), 'origin': 'edited locally'}
        return handler.reply(200, save(con, 'locale', code, value, data.get('revision')))
    if path == '/api/admin/inquiry':
        ref, status = data.get('reference'), data.get('status')
        if status not in {'new', 'contacted', 'planned', 'closed'} or not con.execute('SELECT 1 FROM inquiries WHERE reference=?', (ref,)).fetchone():
            raise ValueError('Choose an existing request and a valid status.')
        con.execute('INSERT INTO inquiry_status VALUES (?,?) ON CONFLICT(reference) DO UPDATE SET status=excluded.status', (ref, status))
        con.commit()
        return handler.reply(200, {'ok': True})
    return handler.reply(404, {'error': 'Page not found.'})
