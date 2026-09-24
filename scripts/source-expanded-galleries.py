"""Retrieve reusable destination photographs and source/license metadata."""
import json, re, html, time, urllib.request, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
queries=['Ait Ben Haddou panorama','Merzouga camel caravan','Dades valley','Skoura Amerhidil','Fes medina','Bou Inania Fes','Chefchaouen street','Tangier kasbah','Essaouira port','Essaouira beach','Marrakech Bahia palace','Marrakech souk','Taroudant walls','Ifrane cedar','Draa valley','Volubilis ruins','Hassan II Mosque']
queries += ['Ait Benhaddou', 'Erg Chebbi camels', 'Merzouga dunes', 'Rissani market', 'Khamlia', 'Tizi Tichka']
out={}
path=ROOT/'.local/expanded-photo-candidates.json'
if path.exists(): out=json.loads(path.read_text(encoding='utf-8'))
for query in queries:
    if query in out: continue
    params=dict(action='query',generator='search',gsrsearch=query+' filetype:bitmap',gsrnamespace=6,gsrlimit=12,prop='imageinfo',iiprop='url|size|extmetadata',format='json')
    try:
        req=urllib.request.Request('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params),headers={'User-Agent':'DesertGatePhotoResearch/1.0'})
        data=json.load(urllib.request.urlopen(req,timeout=45))
        rows=[]
        for p in data.get('query',{}).get('pages',{}).values():
            i=p['imageinfo'][0]; e=i.get('extmetadata',{})
            clean=lambda k: html.unescape(re.sub('<[^>]+>','',e.get(k,{}).get('value',''))).strip()
            license=clean('LicenseShortName')
            if max(i['width'],i['height'])<2400 or license not in ['CC BY-SA 4.0','CC BY-SA 3.0','CC BY-SA 2.0','CC BY 4.0','CC BY 3.0','CC BY 2.0','CC0','Public domain']: continue
            rows.append(dict(title=p['title'],url=i['url'].split('?')[0],page=i['descriptionurl'],width=i['width'],height=i['height'],author=clean('Artist'),license=license,license_url=clean('LicenseUrl'),description=clean('ImageDescription')))
        out[query]=rows
        path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
        print(query,len(rows),flush=True)
    except Exception as e: print(query,str(e),flush=True)
    time.sleep(1)
