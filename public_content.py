"""Public photography fields. Source records stay in the private editorial tools."""
import copy
import re

PHOTO_FIELDS = {'id', 'path', 'name', 'alt', 'caption', 'width', 'height', 'variants', 'focal_point'}
PHOTO_REFERENCE = re.compile(r'unsplash|pexels|wikimedia|creativecommons|moroccan holidays experiences|hammam de la rose|amal targa|comptoir darna', re.I)
ENQUIRY = 'The form prepares your enquiry in WhatsApp. Press Send there to start a conversation with us. Your itinerary, stays, transport, total price and cancellation terms are agreed before booking. Enquiring does not reserve a trip, and no payment is taken here.'
ENQUIRY_TRANSLATIONS = {
    'en': ENQUIRY,
    'fr': 'Le formulaire prépare votre demande dans WhatsApp. Appuyez sur Envoyer pour commencer la conversation. Votre itinéraire, vos hébergements, le transport, le prix total et les conditions d’annulation sont convenus avant la réservation. Une demande ne réserve pas un voyage et aucun paiement n’est effectué ici.',
    'es': 'El formulario prepara tu consulta en WhatsApp. Pulsa Enviar para iniciar la conversación. Acordamos el itinerario, los alojamientos, el transporte, el precio total y las condiciones de cancelación antes de reservar. La consulta no reserva un viaje y aquí no se realiza ningún pago.',
    'de': 'Das Formular bereitet Ihre Anfrage in WhatsApp vor. Tippen Sie dort auf Senden, um das Gespräch zu beginnen. Reiseroute, Unterkünfte, Transport, Gesamtpreis und Stornierungsbedingungen werden vor der Buchung vereinbart. Eine Anfrage reserviert keine Reise; hier erfolgt keine Zahlung.',
    'it': 'Il modulo prepara la tua richiesta su WhatsApp. Premi Invia per iniziare la conversazione. Itinerario, alloggi, trasporti, prezzo totale e condizioni di cancellazione vengono concordati prima della prenotazione. La richiesta non riserva un viaggio e qui non viene effettuato alcun pagamento.',
    'pt': 'O formulário prepara o seu pedido no WhatsApp. Prima Enviar para iniciar a conversa. O itinerário, os alojamentos, o transporte, o preço total e as condições de cancelamento são acordados antes da reserva. O pedido não reserva uma viagem e não é efetuado qualquer pagamento aqui.',
    'nl': 'Het formulier zet je aanvraag klaar in WhatsApp. Druk daar op Verzenden om het gesprek te starten. De route, accommodaties, het vervoer, de totaalprijs en de annuleringsvoorwaarden spreken we vóór de boeking af. Een aanvraag reserveert geen reis en hier wordt niets betaald.',
}
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
    payload['strings'][ENQUIRY] = ENQUIRY_TRANSLATIONS.get(code, ENQUIRY)
    return payload
