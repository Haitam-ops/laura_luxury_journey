"""Generate discovery files from the published language catalogues; no database needed."""
from pathlib import Path
import json
import html
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, urlsplit
from build_pages import render_pages, page_url

ROOT = Path(__file__).resolve().parents[1]


def resolve_origin(config):
    origin = (config.get('customDomain') or config['fallbackOrigin']).strip().rstrip('/')
    parts = urlsplit(origin)
    if parts.scheme != 'https' or not parts.hostname or parts.path or parts.query or parts.fragment or parts.username or parts.password or parts.port:
        raise ValueError('SEO domain must be an HTTPS origin without a path, port, credentials or query.')
    return origin


def main():
    config = json.loads((ROOT / 'data/seo.json').read_text('utf-8'))
    origin = resolve_origin(config)
    config['origin'] = origin
    english = json.loads((ROOT / 'dist/data/content.en.json').read_text('utf-8'))
    codes = [x['code'] for x in english['languages'] if x.get('enabled')]
    catalogues = {code: json.loads((ROOT / f'dist/data/content.{code}.json').read_text('utf-8')) for code in codes}
    trips = {code: {t['id'] for t in c['trips']} for code, c in catalogues.items()}
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    xhtml = 'http://www.w3.org/1999/xhtml'
    ET.register_namespace('', ns)
    ET.register_namespace('xhtml', xhtml)
    root = ET.Element(f'{{{ns}}}urlset')

    for folder in [ROOT, ROOT / 'dist']:
        index = folder / 'index.html'
        markup = index.read_text('utf-8')
        markup = re.sub(r'<title>.*?</title>', '<title>Laura Luxury Journeys | Morocco Tours, Day Trips &amp; Experiences</title>', markup, flags=re.S)
        index.write_text(markup, 'utf-8')
    home_alternates = {code: page_url(origin, code) for code in codes}
    home_alternates['x-default'] = page_url(origin, 'en')
    pages = [(page_url(origin, code), home_alternates) for code in codes]
    pages += render_pages(config, catalogues)
    for url, alternates in pages:
        item = ET.SubElement(root, f'{{{ns}}}url')
        ET.SubElement(item, f'{{{ns}}}loc').text = url
        for code, target in alternates.items():
            ET.SubElement(item, f'{{{xhtml}}}link', rel='alternate', hreflang=code, href=target)
    ET.indent(root)
    xml = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    robots = 'User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /api/\n\nSitemap: ' + origin + '/sitemap.xml\n'
    config['availableTrips'] = {code: sorted(ids) for code, ids in trips.items()}
    for folder in [ROOT, ROOT / 'dist']:
        index = folder / 'index.html'
        markup = index.read_text('utf-8')
        markup = re.sub(r'\s*<meta name="google-site-verification"[^>]*>', '', markup)
        if config.get('googleSiteVerification'):
            token = html.escape(config['googleSiteVerification'], quote=True)
            markup = markup.replace('</head>', f'  <meta name="google-site-verification" content="{token}">\n</head>')
        index.write_text(markup, 'utf-8')
        (folder / 'sitemap.xml').write_bytes(xml)
        (folder / 'robots.txt').write_text(robots, 'utf-8')
        (folder / 'seo-config.js').write_text('window.SITE_SEO=' + json.dumps(config, ensure_ascii=False) + ';\n', 'utf-8')
    print(f'SEO: {len(root)} URLs, {len(codes)} languages; origin {origin}')


if __name__ == '__main__':
    main()
