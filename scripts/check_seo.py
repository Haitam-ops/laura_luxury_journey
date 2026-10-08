"""Check published discovery files and future-domain configuration before release."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, urlsplit
from build_seo import resolve_origin

ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT / 'data/seo.json').read_text('utf-8'))
origin = resolve_origin(config)
assert resolve_origin({'customDomain': '', 'fallbackOrigin': 'https://example.org'}) == 'https://example.org'
assert resolve_origin({'customDomain': 'https://travel.example.org/', 'fallbackOrigin': origin}) == 'https://travel.example.org'
for invalid in ['http://example.org', 'https://example.org/trips', 'https://example.org?test=1', 'https://user:password@example.org']:
    try:
        resolve_origin({'customDomain': invalid, 'fallbackOrigin': origin})
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid domain was accepted')
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'x': 'http://www.w3.org/1999/xhtml'}
tree = ET.parse(ROOT / 'dist/sitemap.xml').getroot()
urls = [row.find('s:loc', ns).text for row in tree]
assert len(urls) == len(set(urls))
payload = json.loads((ROOT / 'dist/data/content.en.json').read_text('utf-8'))
codes = [l['code'] for l in payload['languages'] if l.get('enabled')]
expected = 0
for code in codes:
    c = json.loads((ROOT / f'dist/data/content.{code}.json').read_text('utf-8'))
    expected += len(c['trips']) + 5
assert len(urls) == expected
for row in tree:
    loc = row.find('s:loc', ns).text
    assert loc.startswith(origin + '/')
    query = parse_qs(urlsplit(loc).query)
    assert set(query) <= {'lang', 'trip'}
    if urlsplit(loc).path != '/':
        page = ROOT / 'dist' / urlsplit(loc).path.strip('/') / 'index.html'
        markup = page.read_text('utf-8')
        assert f'<link rel="canonical" href="{loc}">' in markup
        assert 'property="og:url"' in markup
        assert 'site-structured-data' in markup
        assert 'workers.dev' not in markup
    links = row.findall('x:link', ns)
    assert len({l.attrib['hreflang'] for l in links}) == len(links)
    assert any(l.attrib['href'] == loc for l in links)
    for link in links:
        assert link.attrib['href'] in urls
        assert parse_qs(urlsplit(link.attrib['href']).query).get('trip') == query.get('trip')
        if urlsplit(loc).path != '/':
            assert urlsplit(link.attrib['href']).path.split('/')[2:] == urlsplit(loc).path.split('/')[2:]
        target_language = link.attrib['hreflang'] if link.attrib['hreflang'] != 'x-default' else 'en'
        assert (urlsplit(link.attrib['href']).path.split('/')[1] or parse_qs(urlsplit(link.attrib['href']).query)['lang'][0]) == target_language
for file in ['seo.js', 'seo-config.js', 'sitemap.xml', 'robots.txt']:
    assert (ROOT / file).read_bytes() == (ROOT / 'dist' / file).read_bytes(), file
assert f'Sitemap: {origin}/sitemap.xml' in (ROOT / 'dist/robots.txt').read_text('utf-8')
if not config.get('googleSiteVerification'):
    assert 'name="google-site-verification"' not in (ROOT / 'dist/index.html').read_text('utf-8')
print(f'PASS: {expected} published URLs; language targets, domain switch, blank verification and deployment files checked.')
