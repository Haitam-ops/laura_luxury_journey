"""Apply reviewed copy and consistent destination/stay terminology to all public locales."""
from pathlib import Path
import json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from place_names import protect
from trip_editorial import route_heading
def read(p):return json.loads(p.read_text('utf-8'))
manual=read(ROOT/'data/reviewed-localization.json')
for i,code in enumerate(manual['codes']):
 p=ROOT/f'data/locales/{code}.json';d=read(p);strings=d['strings']
 for row in manual['phrases']:strings[row[0]]=row[i+1]
 destinations=['Dades Valley','Draa Valley','Rose Valley','Ziz Valley','Todra Gorge','Rif Mountains','High Atlas','Ouzoud Falls','Marrakech palm grove','Diabat coast']
 for source,value in list(strings.items()):
  for place in destinations:
   if place in strings and strings[place]!=place:value=value.replace(place,strings[place])
  strings[source]=value
 # Overnight labels keep each accommodation type explicit.
 templates={
 'Hotel or riad in ':['Hôtel ou riad à ','Hotel o riad en ','Hotel oder Riad in ','Hotel o riad a ','Hotel ou riad em ','Hotel of riad in '],
 'Guesthouse or hotel in ':['Maison d’hôtes ou hôtel à ','Casa de huéspedes u hotel en ','Gästehaus oder Hotel in ','Pensione o hotel a ','Casa de hóspedes ou hotel em ','Pension of hotel in '],
 'Guesthouse or hotel near ':['Maison d’hôtes ou hôtel près de ','Casa de huéspedes u hotel cerca de ','Gästehaus oder Hotel bei ','Pensione o hotel vicino a ','Casa de hóspedes ou hotel perto de ','Pension of hotel bij '],
 'Hotel in ':['Hôtel à ','Hotel en ','Hotel in ','Hotel a ','Hotel em ','Hotel in '],
 'Lodge or hotel near ':['Lodge ou hôtel près de ','Lodge u hotel cerca de ','Lodge oder Hotel bei ','Lodge o hotel vicino a ','Lodge ou hotel perto de ','Lodge of hotel bij '],
 'Desert camp at ':['Campement dans le désert à ','Campamento en el desierto en ','Wüstencamp am ','Campo nel deserto a ','Acampamento no deserto em ','Woestijnkamp bij ']}
 c=read(ROOT/'data/content.json')
 for trip in c['trips']:
  for stay in trip['overnights']:
   for prefix,translations in templates.items():
    if stay.startswith(prefix):
     place=stay[len(prefix):];strings[stay]=translations[i]+strings.get(place,place)
 # Route headings retain the original place names; paragraphs stay translated.
 for trip in c['trips']:
  for title,paragraph in trip['itinerary']:
   if ' → ' in title:
    strings[title]=route_heading(title,code)
   strings[paragraph]=protect(paragraph,strings.get(paragraph,paragraph),code)[0]
 d['reviewed']=False;d['origin']='Current-copy coverage with manually reviewed interface, titles, destinations and accommodation labels'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
 (ROOT/'dist/data/locales').mkdir(parents=True,exist_ok=True);shutil.copy2(p,ROOT/'dist/data/locales'/p.name)
print('Applied reviewed translations to six locales.')
