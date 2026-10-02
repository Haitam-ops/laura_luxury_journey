"""Translate only the new coastal copy with installed local models.

Long descriptions follow the site's existing machine-draft translation policy.
Customer-facing titles and card summaries below are authored explicitly.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from importlib import import_module

activities = import_module('add-coastal-activities').TRIPS
spec = importlib.util.spec_from_file_location('local_translations', ROOT / 'scripts/local-translations.py')
translator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(translator)
strings = set()
def collect(value):
    if isinstance(value, str):
        strings.add(value)
    elif isinstance(value, list):
        for item in value:
            collect(item)
for trip in activities:
    for field in import_module('cms').LOCALE_FIELDS:
        collect(trip[field])
for photo in import_module('add-coastal-activities').PHOTOS:
    strings.add(photo[-1])
translator.SOURCES = sorted(strings)

CARDS = {
    'fr': ['Essaouira : surf & kitesurf', 'Taghazout : surf & kitesurf',
           'Quittez les ruelles de la médina pour respirer l’air du large. Prenez vos premières vagues ou découvrez la traction d’un kite, lors d’une séance adaptée à votre niveau et aux conditions de l’Atlantique.',
           'Découvrez la vie surf à Taghazout : une séance dans l’océan, les pieds dans le sable et le temps de profiter du bord de mer. Choisissez un cours de surf, ou demandez une séance de kitesurf selon le vent et les disponibilités.', 'Une demi-journée'],
    'es': ['Essaouira: surf y kitesurf', 'Taghazout: surf y kitesurf',
           'Cambia las callejuelas de la medina por la brisa del océano. Atrapa tus primeras olas o descubre la fuerza de una cometa, con una sesión adaptada a tu nivel y a las condiciones del Atlántico.',
           'Vive el ambiente surfero de Taghazout: sesiones en el océano, pies en la arena y tiempo para disfrutar del mar. Elige clases de surf o solicita una sesión de kitesurf si el viento y la disponibilidad lo permiten.', 'Experiencia de medio día'],
    'de': ['Essaouira: Surfen & Kitesurfen', 'Taghazout: Surfen & Kitesurfen',
           'Tausche die Gassen der Medina gegen frische Meeresluft. Reite deine ersten Wellen oder entdecke die Kraft eines Kites, bei einer Einheit passend zu deinem Können und den Bedingungen auf dem Atlantik.',
           'Erlebe das Surferleben in Taghazout: Zeit im Ozean, Sand unter den Füßen und entspannte Stunden am Meer. Wähle Surfunterricht oder frage nach einer Kite-Einheit, wenn Wind und Verfügbarkeit es erlauben.', 'Halbtägiges Erlebnis'],
    'it': ['Essaouira: surf e kitesurf', 'Taghazout: surf e kitesurf',
           'Lascia i vicoli della medina per respirare l’aria dell’oceano. Prendi le tue prime onde o scopri la forza di un kite, con una sessione adatta al tuo livello e alle condizioni dell’Atlantico.',
           'Entra nella vita surf di Taghazout: sessioni nell’oceano, piedi sulla sabbia e tempo per rilassarti al mare. Scegli lezioni di surf o richiedi una sessione di kitesurf, se vento e disponibilità lo consentono.', 'Esperienza di mezza giornata'],
    'pt': ['Essaouira: surf e kitesurf', 'Taghazout: surf e kitesurf',
           'Troque as ruelas da medina pela brisa do oceano. Apanhe as suas primeiras ondas ou descubra a força de um kite, numa sessão adaptada ao seu nível e às condições do Atlântico.',
           'Descubra a vida do surf em Taghazout: sessões no oceano, pés na areia e tempo para relaxar à beira-mar. Escolha aulas de surf ou peça uma sessão de kitesurf, se o vento e a disponibilidade permitirem.', 'Experiência de meio dia'],
    'nl': ['Essaouira: surfen & kitesurfen', 'Taghazout: surfen & kitesurfen',
           'Verruil de steegjes van de medina voor frisse zeelucht. Pak je eerste golven of ontdek de kracht van een kite, tijdens een sessie afgestemd op jouw niveau en de omstandigheden op de Atlantische Oceaan.',
           'Beleef het surfleven van Taghazout: sessies in de oceaan, zand onder je voeten en tijd om te ontspannen aan zee. Kies surflessen of vraag een kitesurfsessie aan als de wind en beschikbaarheid het toelaten.', 'Een halve dag'],
}
SHORT_SOURCES = ['Surf or kitesurf', 'Coaching for your level', 'Time on the Atlantic',
                 'Taghazout surf life', 'Kitesurf by request', 'Active · tailored to your level',
                 'Active · with a relaxed coastal finish', 'Choose your ocean adventure',
                 'Meet, prepare & practice', 'Find your rhythm', 'Slow down by the sea',
                 'Plan your coastal session', 'Pick the beach & prepare',
                 'Build confidence on the water', 'Enjoy the village rhythm']
SHORT_COPY = {
    'fr': ['Surf ou kitesurf', 'Cours adaptés à votre niveau', 'Un moment sur l’Atlantique',
           'L’esprit surf de Taghazout', 'Kitesurf sur demande', 'Actif · adapté à votre niveau',
           'Actif · puis détente au bord de mer', 'Choisissez votre aventure sur l’océan',
           'Rencontre, préparation et premiers essais', 'Trouvez votre rythme', 'Détendez-vous au bord de mer',
           'Préparez votre séance sur la côte', 'Choix de la plage et préparation',
           'Prenez confiance sur l’eau', 'Profitez de la vie du village'],
    'es': ['Surf o kitesurf', 'Clases para tu nivel', 'Tiempo en el Atlántico',
           'El ambiente surfero de Taghazout', 'Kitesurf bajo petición', 'Activo · adaptado a tu nivel',
           'Activo · con tiempo para relajarte junto al mar', 'Elige tu aventura en el océano',
           'Encuentro, preparación y práctica', 'Encuentra tu ritmo', 'Relájate junto al mar',
           'Planifica tu sesión en la costa', 'Elección de la playa y preparación',
           'Gana confianza en el agua', 'Disfruta del ritmo del pueblo'],
    'de': ['Surfen oder Kitesurfen', 'Unterricht für dein Niveau', 'Zeit auf dem Atlantik',
           'Das Surferleben in Taghazout', 'Kitesurfen auf Anfrage', 'Aktiv · passend zu deinem Können',
           'Aktiv · danach Entspannung am Meer', 'Wähle dein Abenteuer auf dem Ozean',
           'Treffen, Vorbereitung und Übungen', 'Finde deinen Rhythmus', 'Entspanne am Meer',
           'Plane deine Einheit an der Küste', 'Strandwahl und Vorbereitung',
           'Gewinne Sicherheit auf dem Wasser', 'Genieße das Dorfleben'],
    'it': ['Surf o kitesurf', 'Lezioni per il tuo livello', 'Tempo sull’Atlantico',
           'La vita surf di Taghazout', 'Kitesurf su richiesta', 'Attivo · adatto al tuo livello',
           'Attivo · poi relax in riva al mare', 'Scegli la tua avventura sull’oceano',
           'Incontro, preparazione e pratica', 'Trova il tuo ritmo', 'Rilassati in riva al mare',
           'Organizza la tua sessione sulla costa', 'Scelta della spiaggia e preparazione',
           'Acquista fiducia in acqua', 'Goditi il ritmo del villaggio'],
    'pt': ['Surf ou kitesurf', 'Aulas para o seu nível', 'Tempo no Atlântico',
           'A vida do surf em Taghazout', 'Kitesurf a pedido', 'Ativo · adaptado ao seu nível',
           'Ativo · seguido de descanso à beira-mar', 'Escolha a sua aventura no oceano',
           'Encontro, preparação e prática', 'Encontre o seu ritmo', 'Relaxe à beira-mar',
           'Planeie a sua sessão na costa', 'Escolha da praia e preparação',
           'Ganhe confiança na água', 'Desfrute do ritmo da aldeia'],
    'nl': ['Surfen of kitesurfen', 'Lessen voor jouw niveau', 'Tijd op de Atlantische Oceaan',
           'Het surfleven van Taghazout', 'Kitesurfen op aanvraag', 'Actief · afgestemd op jouw niveau',
           'Actief · daarna ontspannen aan zee', 'Kies je avontuur op de oceaan',
           'Kennismaken, voorbereiden en oefenen', 'Vind je ritme', 'Ontspan aan zee',
           'Plan je sessie aan de kust', 'Strandkeuze en voorbereiding',
           'Bouw vertrouwen op het water op', 'Geniet van het dorpsleven'],
}
for code, copy in CARDS.items():
    translator.compile(code)
    path = ROOT / 'data/locales' / (code + '.json')
    data = json.loads(path.read_text(encoding='utf-8'))
    data['strings'].update({activities[0]['title']: copy[0], activities[1]['title']: copy[1],
                            activities[0]['summary']: copy[2], activities[1]['summary']: copy[3],
                            'Half-day experience': copy[4], 'Essaouira': 'Essaouira', 'Taghazout': 'Taghazout'})
    data['strings'].update(dict(zip(SHORT_SOURCES, SHORT_COPY[code], strict=True)))
    if code == 'fr':
        for source in strings:
            data['strings'][source] = data['strings'][source].replace('l’enquête', 'votre demande').replace("l'enquête", 'votre demande')
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    shutil.copy2(path, ROOT / 'dist/data/locales' / path.name)
