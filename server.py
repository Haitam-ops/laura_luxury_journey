"""DesertGate local website and durable trip-request inbox. Python standard library only."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, unquote, parse_qs
from datetime import date, datetime, timezone
import argparse
import hashlib
import json
import os
import re
import sqlite3
import uuid
import cms

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('DESERTGATE_DB', str(ROOT / '.local' / 'requests.sqlite3')))
CATALOG = dict(re.findall(r"trip\('([^']+)','([^']+)'", (ROOT / 'trips.js').read_text(encoding='utf-8')))
CATALOG['custom'] = 'A personal Morocco journey'

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB, timeout=10)
    con.execute('CREATE TABLE IF NOT EXISTS inquiries (reference TEXT PRIMARY KEY, idempotency_key TEXT UNIQUE NOT NULL, body_hash TEXT NOT NULL, created_at TEXT NOT NULL, payload TEXT NOT NULL)')
    con.commit()
    return con

def catalog(con):
    return {t['id']: t['title'] for t in cms.documents(con, 'trip') if t['status'] == 'published'} | {'custom': 'A personal Morocco journey'}

def validate(raw, current_catalog=None):
    if not isinstance(raw, dict):
        raise ValueError('Please send a valid trip request.')
    allowed = {'name', 'email', 'date', 'travelers', 'style', 'comfort', 'message', 'trip_id', 'trip_title'}
    if set(raw) - allowed:
        raise ValueError('The trip request contains unexpected fields.')
    data = {}
    for field, maximum in [('name', 100), ('email', 200), ('date', 10), ('style', 40), ('comfort', 60), ('message', 3000), ('trip_id', 100)]:
        value = raw.get(field, '')
        if not isinstance(value, str) or len(value) > maximum:
            raise ValueError('Please check the length of your request details.')
        data[field] = value.strip()
    if not data['name'] or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', data['email']):
        raise ValueError('Please enter your name and a valid email address.')
    if type(raw.get('travelers')) is not int or not 1 <= raw['travelers'] <= 30:
        raise ValueError('Please choose between 1 and 30 travelers.')
    data['travelers'] = raw['travelers']
    if data['date']:
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', data['date']) or date.fromisoformat(data['date']) < date.today():
                raise ValueError()
        except ValueError:
            raise ValueError('Please choose a future travel date, or leave it open.')
    if data['style'] not in {'Flexible', 'Private', 'Shared'} or data['comfort'] not in {'Help me decide', 'Simple & comfortable', 'Boutique riads & camps', 'Premium stays'}:
        raise ValueError('Please choose one of the listed travel preferences.')
    if current_catalog is None:
        with connect() as con:
            current_catalog = catalog(con)
    if data['trip_id'] not in current_catalog:
        raise ValueError('Please select a trip from the current collection.')
    data['trip_title'] = current_catalog[data['trip_id']]
    return data

class Handler(SimpleHTTPRequestHandler):
    server_version = 'DesertGateLocal/1.0'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('X-Frame-Options', 'DENY')
        for name, value in getattr(self, 'extra_headers', {}).items():
            self.send_header(name, value)
        self.extra_headers = {}
        self.send_header('Cache-Control', 'no-store' if not urlsplit(self.path).path.startswith('/assets/') else 'public, max-age=3600')
        super().end_headers()

    def reply(self, status, data):
        encoded = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def valid_host(self):
        port = self.server.server_port
        return self.headers.get('Host') in {f'127.0.0.1:{port}', f'localhost:{port}'}

    def public_path(self):
        path = unquote(urlsplit(self.path).path)
        if path in {'/', '/index.html', '/styles.css', '/app.js', '/boot.js', '/gallery.js', '/route-map.js', '/seo.js', '/seo-config.js', '/robots.txt', '/sitemap.xml', '/admin.html', '/admin.css', '/admin.js'}:
            return True
        rendered = self.rendered_page_path(path)
        if rendered:
            return (rendered / 'index.html').is_file()
        target = (ROOT / path.lstrip('/')).resolve()
        return ((path.startswith('/assets/') and target.is_relative_to(ROOT / 'assets') and target.suffix.lower() in {'.webp', '.png', '.jpg', '.jpeg', '.svg', '.woff2'}) or
                (path.startswith('/uploads/') and target.is_relative_to(ROOT / 'uploads') and target.suffix.lower() == '.webp')) and target.is_file()

    def rendered_page_path(self, path):
        if re.fullmatch(r'/(en|fr|es|de|it|pt|nl)/(journeys(?:/[a-z0-9-]+)?|travel-notes/(time|stays|seasons))/?', path):
            return ROOT / 'dist' / path.strip('/')
        return None

    def translate_path(self, path):
        rendered = self.rendered_page_path(unquote(urlsplit(path).path))
        return str(rendered) if rendered else super().translate_path(path)

    def read_body(self, maximum):
        try:
            size = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            raise ValueError('Invalid request length.')
        if not 1 <= size <= maximum:
            raise ValueError('The request is empty or too large.')
        self.connection.settimeout(20)
        return self.rfile.read(size)

    def read_json(self, maximum=16000):
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            raise ValueError('Send JSON data.')
        result = json.loads(self.read_body(maximum).decode('utf-8'))
        if not isinstance(result, dict):
            raise ValueError('Invalid request data.')
        return result

    def do_GET(self):
        if not self.valid_host():
            return self.reply(403, {'error': 'This server is available on localhost only.'})
        path = urlsplit(self.path).path
        if path in {'/admin', '/admin/'}:
            self.path = '/admin.html'
        if path == '/api/health':
            with connect() as con:
                return self.reply(200, {'status': 'ok', 'catalog_size': len(catalog(con)) - 1})
        if path == '/api/content' or path.startswith('/api/admin/'):
            with connect() as con:
                return cms.get(self, con, path, parse_qs(urlsplit(self.path).query))
        if not self.public_path():
            return self.reply(404, {'error': 'Page not found.'})
        super().do_GET()

    def do_HEAD(self):
        if not self.valid_host() or not self.public_path():
            self.send_response(404)
            self.end_headers()
            return
        super().do_HEAD()

    def do_POST(self):
        if not self.valid_host():
            return self.reply(403, {'error': 'This server is available on localhost only.'})
        origin = self.headers.get('Origin')
        if origin and origin not in {f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'}:
            return self.reply(403, {'error': 'Please submit your request from this website.'})
        if self.headers.get('Sec-Fetch-Site') == 'cross-site':
            return self.reply(403, {'error': 'Please submit your request from this website.'})
        if urlsplit(self.path).path.startswith('/api/admin/'):
            try:
                with connect() as con:
                    return cms.post(self, con, urlsplit(self.path).path)
            except cms.Conflict as err:
                return self.reply(409, {'error': str(err)})
            except (ValueError, UnicodeError, TypeError, KeyError) as err:
                return self.reply(400, {'error': str(err) if isinstance(err, ValueError) else 'Please check the submitted fields.'})
            except (OSError, sqlite3.Error):
                return self.reply(503, {'error': 'The change could not be saved. Your edits are still here; please retry.'})
        if urlsplit(self.path).path != '/api/inquiries':
            return self.reply(404, {'error': 'Request service not found.'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.reply(415, {'error': 'Please send the form as a JSON request.'})
        key = self.headers.get('Idempotency-Key', '')
        if not re.fullmatch(r'[A-Za-z0-9-]{16,80}', key):
            return self.reply(400, {'error': 'Please reopen the request form and try again.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 1 <= size <= 16000:
                return self.reply(413, {'error': 'Your message is too long. Please shorten it.'})
            self.connection.settimeout(10)
            raw = json.loads(self.rfile.read(size).decode('utf-8'))
            con = connect()
            try:
                con.execute('BEGIN IMMEDIATE')
                previous = con.execute('SELECT reference, body_hash, payload FROM inquiries WHERE idempotency_key=?', (key,)).fetchone()
                if previous:
                    snapshot = json.loads(previous[2])
                    # A later rename/archive must not turn a retry into a second inquiry.
                    data = validate(raw, {snapshot['trip_id']: snapshot['trip_title']})
                else:
                    data = validate(raw, catalog(con))
                encoded = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
                digest = hashlib.sha256(encoded.encode()).hexdigest()
                if previous:
                    if previous[1] != digest:
                        return self.reply(409, {'error': 'This request reference belongs to different details. Please retry your current request.'})
                    return self.reply(200, {'reference': previous[0], 'status': 'received'})
                reference = 'DG-' + uuid.uuid4().hex[:12].upper()
                con.execute('INSERT INTO inquiries VALUES (?, ?, ?, ?, ?)', (reference, key, digest, datetime.now(timezone.utc).isoformat(), encoded))
                con.commit()
            finally:
                con.close()
            self.reply(201, {'reference': reference, 'status': 'received'})
        except (ValueError, UnicodeError, json.JSONDecodeError) as err:
            self.reply(400, {'error': str(err) if isinstance(err, ValueError) and not isinstance(err, json.JSONDecodeError) else 'Please check your request details.'})
        except (OSError, sqlite3.Error):
            self.reply(503, {'error': 'We could not save your request. Your details are still in the form; please retry.'})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--list-requests', action='store_true', help='Read the local inbox from this terminal')
    args = parser.parse_args()
    with connect() as con:
        cms.initialize(con)
    if args.list_requests:
        con = connect()
        try:
            for ref, created, payload in con.execute('SELECT reference, created_at, payload FROM inquiries ORDER BY created_at DESC'):
                print(json.dumps({'reference': ref, 'created_at': created, **json.loads(payload)}, ensure_ascii=False))
        finally:
            con.close()
    else:
        with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
            print(f'DesertGate: http://127.0.0.1:{args.port}', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
