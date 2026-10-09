"""Check the generated release contract, assets, localization and public metadata."""
import concurrent.futures
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from audit_site import Page

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from public_content import PHOTO_FIELDS, PHOTO_REFERENCE, ENQUIRY

urls = [x.text for x in ET.parse(ROOT / 'dist/sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
asset_paths = set()
for url in urls:
    parts = urlsplit(url)
    code = parts.path.split('/')[1] or parse_qs(parts.query)['lang'][0]
    path = ROOT / 'dist' / (parts.path.strip('/') or code) / 'index.html'
    markup = path.read_text('utf-8')
    page = Page(); page.feed(markup)
    assert page.canonicals == [url], (url, page.canonicals)
    assert len([h for h in page.headings if h[0] == 'h1']) == 1, url
    assert len(page.hreflang) == 8, url
    for schema in page.schemas:
        for item in schema.get('@graph', []):
            if item.get('@type') == 'BreadcrumbList':
                crumbs = item['itemListElement']
                assert len(crumbs) >= 2
                assert [c['position'] for c in crumbs] == list(range(1, len(crumbs) + 1))
                assert all(c.get('name') and c.get('item', '').startswith('https://lauraluxuryjourneys.com/') for c in crumbs)
    assert markup.count('name="google-site-verification"') == 1, url
    assert not PHOTO_REFERENCE.search(markup), url
    for src in re.findall(r'(?:src|href)="(/[^"?#]*)', markup):
        if src.startswith('/assets/') or src.endswith(('.js', '.css')):
            assert (ROOT / 'dist' / src.lstrip('/')).is_file(), (url, src)
            asset_paths.add(src)
    if '/journeys/' in parts.path and parts.path.count('/') == 4:
        assert 'id="trip-static"' in markup and '<noscript><style>' not in markup, url
        assert 'data-static-site' in markup and 'class="trip-pending"' in markup, url
        assert 'BreadcrumbList' in markup, url
    if parts.path == '/':
        payload = json.loads((ROOT / f'dist/data/content.{code}.json').read_text('utf-8'))
        assert payload['strings'][ENQUIRY] in markup, code
        assert 'required' not in re.search(r'<input name="email"[^>]+>', markup)[0]

for path in (ROOT / 'dist/data').glob('content.*.json'):
    payload = json.loads(path.read_text('utf-8'))
    assert len(payload['trips']) == 26
    for media in payload['media'].values():
        assert set(media) <= PHOTO_FIELDS, (path, media['id'])
        for photo in [media] + media.get('variants', []):
            assert (ROOT / 'dist' / photo['path'].lstrip('/')).is_file(), photo['path']
    assert not PHOTO_REFERENCE.search(path.read_text('utf-8')), path
assert not (ROOT / 'dist/PHOTO-SOURCES.md').exists()
assert not (ROOT / 'dist/assets/sources.txt').exists()
assert len(list((ROOT / 'dist/data').rglob('*.json'))) == 8
assert 'data-static-site' not in (ROOT / 'index.html').read_text('utf-8')
print(f'PASS: {len(urls)} pages; one H1, canonical, hreflang, schema JSON, localization, photo fields and asset existence.')

if '--http' in sys.argv:
    def fetch(url):
        p = urlsplit(url)
        local = 'http://127.0.0.1:8092' + p.path + ('?' + p.query if p.query else '')
        with urllib.request.urlopen(local, timeout=20) as response:
            assert response.status == 200, local
            return {'url': local, 'status': response.status}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, urls))
    (ROOT / 'docs/evidence/2026-10-09/local-route-checks.json').write_text(json.dumps(results, indent=2), 'utf-8')
    print(f'PASS: {len(results)} local Worker routes return HTTP 200.')
