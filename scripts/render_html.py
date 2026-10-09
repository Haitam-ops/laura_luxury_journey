"""Render translated UI and responsive image attributes before browser execution."""
import html
from html.parser import HTMLParser


def photo_attributes(photo, sizes):
    values = {'src': photo['path'], 'alt': photo.get('alt', ''),
              'width': photo['width'], 'height': photo['height'], 'decoding': 'async'}
    if photo.get('variants'):
        values['srcset'] = ', '.join(f'{v["path"]} {v["width"]}w' for v in photo['variants'])
        values['sizes'] = sizes
    return values


def attributes(values):
    return ' '.join(k if v is None else f'{k}="{html.escape(str(v), quote=True)}"' for k, v in values.items())


class LocalizedHTML(HTMLParser):
    def __init__(self, payload):
        super().__init__(convert_charrefs=True)
        self.payload = payload
        self.output = []
        self.stack = []
        self.in_body = False
        self.media = {}
        for photo in payload['media'].values():
            for path in [photo['path'], f'/assets/{photo["id"]}.webp'] + [v['path'] for v in photo.get('variants', [])]:
                self.media[path] = photo

    def handle_starttag(self, tag, pairs):
        values = dict(pairs)
        if tag == 'html':
            values.update(lang=self.payload['language']['code'])
        if tag == 'body':
            self.in_body = True
        protected = any(x[1] for x in self.stack) or tag in {'script', 'style', 'textarea'} or 'data-no-translate' in values
        if self.in_body and not protected:
            for name in ('alt', 'title', 'placeholder', 'aria-label'):
                if values.get(name):
                    values[name] = self.payload['strings'].get(values[name], values[name])
        if tag == 'img' and values.get('src') in self.media:
            sizes = '100vw' if 'hero-image' in values.get('class', '') else '(max-width:620px) 100vw, (max-width:1000px) 50vw, 33vw'
            values.update(photo_attributes(self.media[values['src']], sizes))
        if tag == 'a':
            code = self.payload['language']['code']
            if values.get('href') == './' or ('brand' in values.get('class', '').split() and values.get('href', '').startswith('/?lang=')):
                values['href'] = '/?lang=' + code
            if 'data-guide' in values:
                values['href'] = f'/{code}/travel-notes/{values["data-guide"]}/'
            if 'data-catalogue' in values:
                values['href'] = f'/{code}/journeys/'
        self.output.append('<' + tag + (' ' + attributes(values) if values else '') + '>')
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append((tag, protected))

    def handle_endtag(self, tag):
        self.output.append(f'</{tag}>')
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        if tag == 'body':
            self.in_body = False

    def handle_data(self, data):
        raw = any(tag in {'script', 'style'} for tag, _ in self.stack)
        if self.in_body and not any(x[1] for x in self.stack) and data.strip():
            source = data.strip()
            translated = self.payload['strings'].get(source)
            if translated:
                data = data.replace(source, translated)
        self.output.append(data if raw else html.escape(data, quote=False))

    def handle_entityref(self, name):
        self.output.append(f'&{name};')

    def handle_charref(self, name):
        self.output.append(f'&#{name};')

    def handle_comment(self, data):
        self.output.append(f'<!--{data}-->')

    def handle_decl(self, data):
        self.output.append(f'<!{data}>')


def localize_html(markup, payload):
    parser = LocalizedHTML(payload)
    parser.feed(markup)
    return ''.join(parser.output)
