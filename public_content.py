"""Public photography fields. Source records stay in the private editorial tools."""
import copy
import re

PHOTO_FIELDS = {'id', 'path', 'name', 'alt', 'caption', 'width', 'height', 'variants', 'focal_point'}
PHOTO_REFERENCE = re.compile(r'unsplash|pexels|wikimedia|creativecommons|moroccan holidays experiences|hammam de la rose|amal targa|comptoir darna', re.I)
ENQUIRY = 'The form prepares your enquiry in WhatsApp or email. Press Send in your chosen app. Your itinerary, stays, transport, total price and cancellation terms are agreed before booking. Enquiring does not reserve a trip, and no payment is taken here.'
ENQUIRY_TRANSLATIONS = {
    'en': ENQUIRY,
    'fr': 'Choisissez WhatsApp ou l’e-mail, puis envoyez votre demande depuis l’application. Votre itinéraire, vos hébergements, le transport, le prix total et les conditions d’annulation sont convenus avant la réservation. Une demande ne réserve pas un voyage et aucun paiement n’est effectué ici.',
    'es': 'Elige WhatsApp o correo electrónico y envía la consulta desde la aplicación. Acordamos el itinerario, los alojamientos, el transporte, el precio total y las condiciones de cancelación antes de reservar. La consulta no reserva un viaje y aquí no se realiza ningún pago.',
    'de': 'Wählen Sie WhatsApp oder E-Mail und senden Sie die Anfrage in der App. Reiseroute, Unterkünfte, Transport, Gesamtpreis und Stornierungsbedingungen werden vor der Buchung vereinbart. Eine Anfrage reserviert keine Reise; hier erfolgt keine Zahlung.',
    'it': 'Scegli WhatsApp o e-mail e invia la richiesta dall’app. Itinerario, alloggi, trasporti, prezzo totale e condizioni di cancellazione vengono concordati prima della prenotazione. La richiesta non riserva un viaggio e qui non viene effettuato alcun pagamento.',
    'pt': 'Escolha WhatsApp ou e-mail e envie o pedido na aplicação. O itinerário, os alojamentos, o transporte, o preço total e as condições de cancelamento são acordados antes da reserva. O pedido não reserva uma viagem e não é efetuado qualquer pagamento aqui.',
    'nl': 'Kies WhatsApp of e-mail en verstuur je aanvraag in de app. De route, accommodaties, het vervoer, de totaalprijs en de annuleringsvoorwaarden spreken we vóór de boeking af. Een aanvraag reserveert geen reis en hier wordt niets betaald.',
}
CONTACT_TRANSLATIONS = {'fr': {'Choose WhatsApp or email, then send your enquiry from the app.': 'Choisissez WhatsApp ou l’e-mail, puis '
                                                                          'envoyez votre demande depuis '
                                                                          'l’application.',
        'Continue by email': 'Continuer par e-mail',
        'Open email draft': 'Ouvrir le brouillon',
        'Review your draft and press Send in your app.': 'Vérifiez votre brouillon, puis envoyez-le depuis votre '
                                                         'application.'},
 'es': {'Choose WhatsApp or email, then send your enquiry from the app.': 'Elige WhatsApp o correo electrónico y '
                                                                          'envía la consulta desde la aplicación.',
        'Continue by email': 'Continuar por correo',
        'Open email draft': 'Abrir borrador',
        'Review your draft and press Send in your app.': 'Revisa el borrador y envíalo desde tu aplicación.'},
 'de': {'Choose WhatsApp or email, then send your enquiry from the app.': 'Wählen Sie WhatsApp oder E-Mail und '
                                                                          'senden Sie die Anfrage in der App.',
        'Continue by email': 'Per E-Mail fortfahren',
        'Open email draft': 'E-Mail-Entwurf öffnen',
        'Review your draft and press Send in your app.': 'Prüfen Sie den Entwurf und senden Sie ihn in Ihrer '
                                                         'App.'},
 'it': {'Choose WhatsApp or email, then send your enquiry from the app.': 'Scegli WhatsApp o e-mail e invia la '
                                                                          'richiesta dall’app.',
        'Continue by email': 'Continua via e-mail',
        'Open email draft': 'Apri la bozza',
        'Review your draft and press Send in your app.': 'Controlla la bozza e inviala dalla tua app.'},
 'pt': {'Choose WhatsApp or email, then send your enquiry from the app.': 'Escolha WhatsApp ou e-mail e envie o '
                                                                          'pedido na aplicação.',
        'Continue by email': 'Continuar por e-mail',
        'Open email draft': 'Abrir rascunho',
        'Review your draft and press Send in your app.': 'Reveja o rascunho e envie-o na aplicação.'},
 'nl': {'Choose WhatsApp or email, then send your enquiry from the app.': 'Kies WhatsApp of e-mail en verstuur je '
                                                                          'aanvraag in de app.',
        'Continue by email': 'Doorgaan per e-mail',
        'Open email draft': 'Concept openen',
        'Review your draft and press Send in your app.': 'Controleer je concept en verstuur het in je app.'}}

CAPTIONS = {
    'en': ('A hammam in Marrakech', 'Moroccan cooking in Marrakech', 'An evening show in Marrakech'),
    'fr': ('Un hammam à Marrakech', 'Cuisine marocaine à Marrakech', 'Un spectacle en soirée à Marrakech'),
    'es': ('Un hammam en Marrakech', 'Cocina marroquí en Marrakech', 'Un espectáculo nocturno en Marrakech'),
    'de': ('Ein Hammam in Marrakech', 'Marokkanische Küche in Marrakech', 'Eine Abendshow in Marrakech'),
    'it': ('Un hammam a Marrakech', 'Cucina marocchina a Marrakech', 'Uno spettacolo serale a Marrakech'),
    'pt': ('Um hammam em Marrakech', 'Cozinha marroquina em Marrakech', 'Um espetáculo noturno em Marrakech'),
    'nl': ('Een hammam in Marrakech', 'Marokkaans koken in Marrakech', 'Een avondshow in Marrakech'),
}


def publish_payload(payload):
    payload = copy.deepcopy(payload)
    code = payload['language']['code']
    # The owner confirmed these are their photographs. Do not export supplier
    # URLs, credits, licensing notes or research metadata with the public media.
    for key, photo in payload['media'].items():
        payload['media'][key] = {k: v for k, v in photo.items() if k in PHOTO_FIELDS}
        for index, prefix in enumerate(('experience-hammam-', 'experience-cook-', 'experience-show-')):
            if key.startswith(prefix):
                for field in ('name', 'alt', 'caption'):
                    payload['media'][key][field] = CAPTIONS.get(code, CAPTIONS['en'])[index]
    for trip in payload['trips']:
        trip['photos'] = [payload['media'][p['id']] for p in trip['photos']]
    payload['strings'] = {key: val for key, val in payload['strings'].items()
                          if not PHOTO_REFERENCE.search(key + ' ' + val)
                          and not key.startswith('You’ll have a reference for your request')}
    payload['strings'].update(CONTACT_TRANSLATIONS.get(code, {}))
    payload['strings'][ENQUIRY] = ENQUIRY_TRANSLATIONS.get(code, ENQUIRY)
    return payload
