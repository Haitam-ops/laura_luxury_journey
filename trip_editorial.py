"""Shared editorial data for API and static exports, with FAQs drawn from trip facts."""
import json
from pathlib import Path
from place_names import protect

ROOT = Path(__file__).parent / 'data'


def copy_overrides(code):
    return json.loads((ROOT / 'reviewed-trip-copy.json').read_text('utf-8')).get(code, {})


def route_heading(heading, code):
    if code == 'en':
        return heading
    routes = json.loads((ROOT / 'route-labels.json').read_text('utf-8'))
    index = routes['codes'].index(code)
    return ' → '.join(routes['labels'][part.strip()][index] if part.strip() in routes['labels']
                      else protect(part.strip(), part.strip(), code)[0] for part in heading.split('→'))


LABELS = {
    'en': ['How much time should I allow?', 'Where will we stay?', 'What arrangements are included?', 'What costs extra?', 'What should I know before booking?'],
    'fr': ['Combien de temps faut-il prévoir ?', 'Où passerons-nous les nuits ?', 'Quelles prestations sont prévues ?', 'Quels frais sont à prévoir en supplément ?', 'Que faut-il savoir avant de réserver ?'],
    'es': ['¿Cuánto tiempo debo reservar?', '¿Dónde nos alojaremos?', '¿Qué servicios están previstos?', '¿Qué se paga aparte?', '¿Qué debo saber antes de reservar?'],
    'de': ['Wie viel Zeit sollte ich einplanen?', 'Wo übernachten wir?', 'Welche Leistungen sind vorgesehen?', 'Welche Kosten kommen hinzu?', 'Was sollte ich vor der Buchung wissen?'],
    'it': ['Quanto tempo devo prevedere?', 'Dove pernotteremo?', 'Quali servizi sono previsti?', 'Quali costi sono a parte?', 'Cosa devo sapere prima di prenotare?'],
    'pt': ['Quanto tempo devo reservar?', 'Onde vamos ficar alojados?', 'Que serviços estão previstos?', 'Que custos são cobrados à parte?', 'O que devo saber antes de reservar?'],
    'nl': ['Hoeveel tijd moet ik rekenen?', 'Waar overnachten we?', 'Welke voorzieningen zijn gepland?', 'Welke kosten komen erbij?', 'Wat moet ik weten voordat ik boek?'],
}


def enrich_trip(trip, code):
    titles = json.loads((ROOT / 'trip-search-titles.json').read_text('utf-8'))
    if trip['id'] in titles['titles']:
        trip['seoTitle'] = titles['titles'][trip['id']][titles['codes'].index(code)]
    else:
        trip['seoTitle'] = trip['title']
    trip['seoDescription'] = trip['summary']
    labels = LABELS[code]
    # Keep factual answers in sync with the itinerary instead of duplicating promises.
    faqs = [{'question': labels[0], 'answer': trip['duration']}]
    if trip['overnights']:
        faqs.append({'question': labels[1], 'answer': '', 'items': trip['overnights'], 'ordered': True})
    faqs.extend([
        {'question': labels[2], 'answer': '', 'items': trip['cover']},
        {'question': labels[3], 'answer': trip['extras']},
        {'question': labels[4], 'answer': trip['practical']},
    ])
    trip['faqs'] = faqs
