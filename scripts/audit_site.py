"""Read-only inventory and bounded HTTP crawl of published sitemap URLs."""
import argparse
import collections
import concurrent.futures
import csv
import json
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = collections.Counter()
        self.links = []
        self.canonicals = []
        self.hreflang = []
        self.meta = {}
        self.title = ''
        self.heading = ''
        self.headings = []
        self.schemas = []
        self.capture = None
        self.schema = ''
        self.words = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags[tag] += 1
        if tag in ('script', 'style', 'noscript'):
            self.hidden_depth += 1
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonicals.append(a.get('href'))
        if tag == 'link' and a.get('hreflang'):
            self.hreflang.append((a['hreflang'], a.get('href')))
        if tag == 'meta':
            self.meta[a.get('name') or a.get('property')] = a.get('content')
        if tag == 'title' or tag in ('h1','h2','h3','h4'):
            self.capture = tag
            self.heading = ''
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.capture = 'schema'
            self.schema = ''

    def handle_data(self, data):
        if self.capture == 'schema':
            self.schema += data
        elif self.capture:
            self.heading += data
        if not self.hidden_depth:
            self.words.extend(data.split())

    def handle_endtag(self, tag):
        if tag == self.capture:
            if tag == 'title': self.title = self.heading.strip()
            else: self.headings.append((tag, self.heading.strip()))
            self.capture = None
        if tag == 'script' and self.capture == 'schema':
            self.schemas.append(json.loads(self.schema))
            self.capture = None
        if tag in ('script','style','noscript') and self.hidden_depth:
            self.hidden_depth -= 1


def inspect(url, remote):
    p = urlsplit(url)
    path = ROOT / 'dist' / (p.path.strip('/') or parse_qs(p.query).get('lang', ['en'])[0]) / 'index.html'
    page = Page()
    page.feed(path.read_text('utf-8'))
    item = {'url':url, 'file':str(path.relative_to(ROOT)), 'title':page.title,
            'description':page.meta.get('description'), 'canonical':page.canonicals,
            'hreflang':page.hreflang, 'headings':page.headings,
            'initial_words_excluding_script_style_noscript':len(page.words),
            'schema_types':[n.get('@type') for s in page.schemas for n in s.get('@graph',[s])],
            'internal_links': sorted({urljoin(url, h) for h in page.links if urlsplit(urljoin(url,h)).hostname == p.hostname})}
    if remote:
        start = time.perf_counter()
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (Laura website audit)'})
            with urllib.request.urlopen(req,timeout=25) as response:
                body = response.read()
                item.update(status=response.status, final_url=response.url, bytes=len(body),
                            elapsed_ms=round((time.perf_counter()-start)*1000),
                            headers={k:v for k,v in response.headers.items() if k.lower() in ['content-type','cache-control','cf-cache-status','content-encoding','x-robots-tag','location','etag']})
        except urllib.error.HTTPError as e:
            item.update(status=e.code,error=str(e))
        except Exception as e:
            item.update(error=str(e))
    return item


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--remote',action='store_true')
    parser.add_argument('--output',default='docs/evidence/2026-10-09/baseline.json')
    args=parser.parse_args()
    urls=[n.text for n in ET.parse(ROOT/'dist/sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(lambda u:inspect(u,args.remote),urls))
    result={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'remote':args.remote,'pages':rows,
            'status_counts':dict(collections.Counter(str(r.get('status','not-requested')) for r in rows)),
            'duplicate_titles':[t for t,c in collections.Counter(r['title'] for r in rows).items() if c>1]}
    target=ROOT/args.output
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
    with target.with_suffix('.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=['url','file','title','description','status'])
        writer.writeheader()
        writer.writerows({k:r.get(k,'') for k in writer.fieldnames} for r in rows)
    print(json.dumps({'pages':len(rows),'status_counts':result['status_counts'],'duplicate_titles':result['duplicate_titles'],'saved':str(target)}))


if __name__=='__main__':
    main()
