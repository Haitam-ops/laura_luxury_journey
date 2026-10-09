"""Pre-render published trip, catalogue and guide pages from existing reviewed copy."""
import html
import json
import re
from pathlib import Path
from render_html import localize_html, photo_attributes, attributes

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ('time', 'stays', 'seasons')


def notes():
    source = (ROOT / 'app.js').read_text('utf-8')
    return {key: json.loads(value) for key, value in re.findall(
        r'^(time|stays|seasons):(\{.*\}),$', source, re.M)}


def page_url(origin, code, trip=None, guide=None, catalogue=False):
    if guide:
        return f'{origin}/{code}/travel-notes/{guide}/'
    if catalogue:
        return f'{origin}/{code}/journeys/'
    if trip:
        return f'{origin}/{code}/journeys/{trip}/'
    return f'{origin}/?lang={code}'


def metadata(config, payload, title, description, url, alternates, photo, article=False):
    e = lambda value: html.escape(str(value), quote=True)
    origin = config['origin']
    contact = config.get('businessContact', {})
    site = payload['site']
    business = {'@type': 'TravelAgency', '@id': origin + '/#business',
                'name': site['brand'], 'url': page_url(origin, 'en'),
                'logo': origin + config['logo']}
    for field, value in [('telephone', site.get('phone') or contact.get('telephone')),
                         ('address', site.get('address') or contact.get('address')),
                         ('email', site.get('email'))]:
        if value:
            business[field] = value
    graph = [business, {'@type': 'WebSite', '@id': origin + '/#website',
                       'url': page_url(origin, 'en'), 'name': site['brand'],
                       'publisher': {'@id': business['@id']}},
             {'@type': 'Article' if article else 'WebPage', '@id': url + '#page',
              'url': url, 'name': title, 'description': description,
              'inLanguage': payload['language']['code'],
              'isPartOf': {'@id': origin + '/#website'},
              'about': {'@id': business['@id']}}]
    code = payload['language']['code']
    if '/journeys/' in url or '/travel-notes/' in url:
        crumbs = [(site['brand'], page_url(origin, code))]
        if '/journeys/' in url and url != page_url(origin, code, catalogue=True):
            crumbs.append((payload['strings'].get('Explore all', 'Explore all'), page_url(origin, code, catalogue=True)))
        crumbs.append((title, url))
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': name, 'item': target}
            for i, (name, target) in enumerate(crumbs)]})
    image = origin + photo['path']
    lines = [f'<title>{e(title)}</title>',
             f'<meta name="description" content="{e(description)}">',
             f'<link rel="canonical" href="{e(url)}">']
    for code, target in alternates.items():
        lines.append(f'<link rel="alternate" hreflang="{code}" href="{e(target)}">')
    for key, value in {'og:type': 'article' if article else 'website',
                       'og:site_name': site['brand'], 'og:title': title,
                       'og:description': description, 'og:url': url,
                       'og:image': image, 'og:image:alt': photo.get('alt', site['brand'])}.items():
        lines.append(f'<meta property="{key}" content="{e(value)}">')
    for key, value in {'twitter:card': 'summary_large_image', 'twitter:title': title,
                       'twitter:description': description, 'twitter:image': image,
                       'twitter:image:alt': photo.get('alt', site['brand'])}.items():
        lines.append(f'<meta name="{key}" content="{e(value)}">')
    schema = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('<', '\\u003c')
    lines.append(f'<script type="application/ld+json" id="site-structured-data">{schema}</script>')
    if config.get('googleSiteVerification'):
        lines.append(f'<meta name="google-site-verification" content="{e(config["googleSiteVerification"])}">')
    return '\n'.join(lines)


def render_pages(config, catalogues):
    origin = config['origin']
    codes = list(catalogues)
    note_copy = notes()
    assert set(note_copy) == set(GUIDES)
    urls = []
    template = (ROOT / 'index.html').read_text('utf-8')
    template = re.sub(r'<title>.*?</title>|<meta name="description"[^>]*>', '', template, flags=re.S)
    template = re.sub(r'<!-- SEO HEAD START -->.*?<!-- SEO HEAD END -->', '', template, flags=re.S)
    template = re.sub(r'\s*<meta name="google-site-verification"[^>]*>', '', template)
    template = re.sub(r'\n{3,}', '\n\n', template)
    template = re.sub(r'^ +$', '', template, flags=re.M)
    template = re.sub(r'(src|href)="assets/', r'\1="/assets/', template)
    template = re.sub(r'(src|href)="(styles\.css|seo-config\.js|seo\.js|boot\.js)', r'\1="/\2', template)
    e = lambda value: html.escape(str(value), quote=True)
    for code, payload in catalogues.items():
        localized_template = localize_html(template, payload)
        localized_template = localized_template.replace(f'<html lang="{code}">', f'<html lang="{code}" data-static-site>')
        tr = lambda value: payload['strings'].get(value, value)
        brand = payload['site']['brand']
        home = page_url(origin, code)
        available = lambda trip=None, guide=None, catalogue=False: {
            **{lang: page_url(origin, lang, trip, guide, catalogue) for lang, cat in catalogues.items()
               if not trip or any(t['id'] == trip for t in cat['trips'])},
            'x-default': page_url(origin, 'en', trip, guide, catalogue)}
        home_head = metadata(config, payload, brand + ' | ' + config['homeTitles'][code],
                             payload['site']['collection_copy'], home, available(),
                             payload['media'][payload['site']['hero_images'][0]])
        home_markup = localized_template.replace('</head>', f'<!-- SEO HEAD START -->{home_head}<!-- SEO HEAD END -->\n</head>')
        home_markup = home_markup.replace('<html lang="en">', f'<html lang="{code}">')
        home_target = ROOT / 'dist' / code / 'index.html'
        home_target.parent.mkdir(parents=True, exist_ok=True)
        home_target.write_text(home_markup, 'utf-8')
        if code == 'en':
            for folder in [ROOT, ROOT / 'dist']:
                (folder / 'index.html').write_text(home_markup.replace(' data-static-site', '') if folder == ROOT else home_markup, 'utf-8')
        def write(path, content, url, alternates):
            target = ROOT / 'dist' / path / 'index.html'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(re.sub(r'[ \t]+$', '', content, flags=re.M), 'utf-8')
            urls.append((url, alternates))

        def standalone(title, description, body, url, alternates, photo, article=False):
            langs = ' '.join(f'<a href="{e(target)}" lang="{lang}" hreflang="{lang}"'
                             f'{" aria-current=\"page\"" if lang == code else ""}>{lang.upper()}</a>'
                             for lang, target in alternates.items() if lang != 'x-default')
            head = metadata(config, payload, title + ' | ' + brand, description, url, alternates, photo, article)
            return f'''<!doctype html><html lang="{code}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">{head}
<link rel="icon" href="/assets/branding/laura-icon-96.png"><link rel="stylesheet" href="/styles.css?v=audit-20261009">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Playfair+Display:ital,wght@0,400;1,400&display=swap" rel="stylesheet">
</head><body class="guide-page"><header class="guide-header container"><a class="brand" href="{e(home)}"><img src="/assets/branding/laura-emblem-192.webp" alt="" width="64" height="64"><strong>{e(brand)}</strong></a><nav aria-label="{e(tr('Choose your language'))}">{langs}</nav></header>
<main class="guide-main container"><a class="text-link" href="{e(home)}#fieldnotes">← {e(tr('Back to exploring'))}</a><h1>{e(title)}</h1>{body}</main>
<footer class="guide-footer container"><a href="{e(home)}#journeys">{e(tr('Plan your journey'))}</a><a href="https://wa.me/212667687763" rel="noopener noreferrer" target="_blank">WhatsApp +212 667 687 763</a><span>© 2026 {e(brand)}</span></footer></body></html>'''

        trip_links = ''.join(f'<li><a href="{e(page_url(origin, code, t["id"]))}">{e(t["title"])}</a> — {e(t["duration"])}</li>' for t in payload['trips'])
        for trip in payload['trips']:
            url = page_url(origin, code, trip['id'])
            alternates = available(trip['id'])
            head = metadata(config, payload, trip['seoTitle'] + ' | ' + brand,
                            trip['seoDescription'], url, alternates, trip['photos'][0])
            markup = localized_template.replace('</head>', f'<!-- SEO HEAD START -->{head}<!-- SEO HEAD END -->\n</head>')
            markup = markup.replace('<html lang="en">', f'<html lang="{code}">')
            itinerary = ''.join(f'<li><h3>{e(title)}</h3><p>{e(text).replace(chr(10), "<br>")}</p></li>' for title, text in trip['itinerary'])
            faqs = ''.join(f'<details><summary>{e(f["question"])}</summary><p>{e(f.get("answer", ""))}</p><ul>{"".join("<li>"+e(item)+"</li>" for item in f.get("items", []))}</ul></details>' for f in trip.get('faqs', []))
            photo = attributes(photo_attributes(trip['photos'][0], '(max-width:1000px) 100vw, 1000px'))
            fallback = f'<article id="trip-static" class="trip-static container" aria-labelledby="trip-static-title"><nav class="trip-breadcrumbs"><a href="{e(home)}">{e(brand)}</a><a href="{e(page_url(origin, code, catalogue=True))}">{e(tr("Explore all"))}</a><span>{e(trip["title"])}</span></nav><h1 id="trip-static-title">{e(trip["title"])}</h1><p>{e(trip["summary"])}</p><p>{e(trip["duration"])} · {e(trip["start"])} → {e(trip["end"])}</p><a class="button button-rust" href="https://wa.me/212667687763">WhatsApp +212 667 687 763</a><img class="guide-photo" {photo} fetchpriority="high"><p>{e(trip["story"]).replace(chr(10), "<br>")}</p><h2>{e(tr("Itinerary"))}</h2><ol>{itinerary}</ol><h2>{e(tr("Good to know"))}</h2><p>{e(trip["practical"])}</p><ul>{"".join("<li>"+e(x)+"</li>" for x in trip["cover"])}</ul><p>{e(trip["extras"])}</p>{faqs}<p><a class="text-link" href="{e(page_url(origin, code, catalogue=True))}">{e(tr("Explore all"))}</a></p></article>'
            markup = re.sub(r'<link rel="preload"[^>]*as="image"[^>]*>', '', markup)
            markup = markup.replace('fetchpriority="high"', 'loading="lazy" fetchpriority="low"')
            markup = markup.replace('<h1 id="hero-title"', '<h2 id="hero-title"').replace('</em></h1>', '</em></h2>')
            markup = markup.replace('<body>', '<body class="trip-pending">' + fallback)
            write(f'{code}/journeys/{trip["id"]}', markup, url, alternates)
        url = page_url(origin, code, catalogue=True)
        alternates = available(catalogue=True)
        body = f'<p>{e(payload["site"]["collection_copy"])}</p>'
        for category, label in [('journeys', 'Multi-day journeys'), ('daytrips', 'Day trips'), ('experiences', 'Local experiences')]:
            body += f'<h2>{e(tr(label))}</h2><ul class="guide-catalogue">'
            body += ''.join(f'<li><h3><a href="{e(page_url(origin, code, t["id"]))}">{e(t["title"])}</a></h3><p>{e(t["duration"])} · {e(t["start"])} → {e(t["end"])}</p><p>{e(t["summary"])}</p><a class="text-link" href="{e(page_url(origin, code, t["id"]))}">{e(tr("View itinerary"))}</a></li>' for t in payload['trips'] if t['category'] == category)
            body += '</ul>'
        write(f'{code}/journeys', standalone(tr('Explore all'), payload['site']['collection_copy'], body, url, alternates, payload['trips'][0]['photos'][0]), url, alternates)
        for key, note in note_copy.items():
            url = page_url(origin, code, guide=key)
            alternates = available(guide=key)
            body = re.sub(r'<(h3|p)>(.*?)</\1>', lambda m: f'<{m[1]}>{e(tr(m[2]))}</{m[1]}>', note['html'])
            body = body.replace('<h3>', '<h2>').replace('</h3>', '</h2>')
            description = re.search(r'<p>(.*?)</p>', body)[1]
            media_id = {'time': 'oasis', 'stays': 'marrakech', 'seasons': 'atlas'}[key]
            photo = payload['media'][media_id]
            related = {'time': ['sahara-marrakech-3-days', 'slow-sahara-5-days', 'marrakech-fes-sahara-4-days'],
                       'stays': ['slow-sahara-5-days', 'southern-morocco-7-days'],
                       'seasons': ['essaouira-day', 'imlil-atlas-day', 'sahara-marrakech-3-days']}[key]
            links = ''.join(f'<li><a href="{e(page_url(origin, code, t["id"]))}">{e(t["title"])}</a></li>' for t in payload['trips'] if t['id'] in related)
            other_notes = ''.join(f'<li><a href="{e(page_url(origin, code, guide=k))}">{e(tr(n["title"]))}</a></li>' for k, n in note_copy.items() if k != key)
            body = f'<img class="guide-photo" {attributes(photo_attributes(photo, "(max-width:1000px) 100vw, 1000px"))}>' + body
            body += f'<nav class="guide-related"><h2>{e(tr("Explore the journeys"))}</h2><ul>{links}</ul><ul>{other_notes}</ul></nav><a class="button button-rust" href="{e(home)}#journeys">{e(tr("Plan your journey"))}</a>'
            write(f'{code}/travel-notes/{key}', standalone(tr(note['title']), html.unescape(description), body, url, alternates, photo, True), url, alternates)
    return urls
