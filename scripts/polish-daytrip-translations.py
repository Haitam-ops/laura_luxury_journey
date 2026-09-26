"""Editorial corrections to the local translation drafts for the new schedules."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parents[1]
updates = json.loads((ROOT / 'data/daytrip-itineraries.json').read_text(encoding='utf-8'))
# Each entry replaces a complete itinerary paragraph by its stable trip and step.
corrections = {
 'fr': {
  'ourika-valley': {
   0: "Retrouvez votre chauffeur à votre hébergement ou au point accessible le plus proche. Partez vers le sud en véhicule privé, en direction des contreforts de l'Atlas.",
   1: "Faites une halte dans une coopérative féminine pour découvrir la fabrication de l'huile d'argan. Vous pouvez regarder les produits avant de reprendre la route de la vallée.",
   2: "Longez la rivière entre cultures en terrasses, noyers et villages à flanc de colline. Le lundi, le parcours comprend le marché hebdomadaire de Tnin Ourika.",
   3: "Rejoignez la première cascade par un sentier rocheux, avec environ 45 minutes de marche dans chaque sens. Vous pouvez aussi rester au village et dans les cafés au bord de l'eau. Indiquez-nous votre préférence pour organiser l'accompagnement.",
   4: "Installez-vous sous les arbres dans un restaurant au bord de la rivière pour un tajine ou des grillades. Le déjeuner et les boissons sont à régler sur place, sauf mention contraire dans votre devis.",
   5: "Parcourez les étals d'artisanat ou détendez-vous au bord de l'eau. Par temps chaud, demandez conseil à votre guide avant d'entrer dans les bassins naturels de la rivière.",
   6: "Retrouvez votre chauffeur privé pour redescendre la vallée et rejoindre votre hébergement ou le lieu de retour convenu."
  },
  'ouzoud-waterfalls': {
   0: "Votre chauffeur-guide vous retrouve à votre hébergement ou au point accessible le plus proche. Prenez la direction du nord-est à bord de votre véhicule privé climatisé.",
   1: "Comptez environ trois heures de route à travers les terres agricoles et les oliveraies vers les contreforts du Moyen Atlas, avec une pause en chemin.",
   2: "Arrivez au village de Tanaghmeilt et découvrez les premières vues sur les cascades. Choisissez le parcours de marche avec votre chauffeur-guide avant de descendre dans les gorges.",
   3: "Prévoyez quatre à cinq heures sur place, déjeuner compris. Suivez les sentiers entre points de vue et bosquets ombragés, en observant les macaques dans les arbres. Une promenade en bateau est proposée en option au pied des cascades.",
   6: "Reprenez la route de Marrakech avec une pause en chemin. Le retour à votre hébergement est prévu entre 19:00 et 20:00, selon la circulation."
  },
  'essaouira-day': {
   1: "Faites une pause-café à Chichaoua, puis visitez une coopérative féminine pour découvrir l'extraction traditionnelle de l'huile d'argan. Poursuivez à travers les arganeraies jusqu'à Essaouira.",
   2: "Votre chauffeur vous dépose près de la médina. Profitez d'environ quatre heures pour explorer la ville ; une visite guidée peut être organisée sur demande.",
   4: "Rejoignez le port et ses barques bleues. Choisissez du poisson grillé près du port ou un restaurant dans la médina. Le déjeuner est à votre charge, sauf s'il figure dans votre devis.",
   6: "Retrouvez votre chauffeur privé près de l'entrée de la médina. Reprenez la route avec des pauses et rejoignez votre hébergement entre 19:00 et 20:00."
  },
  'ait-ben-haddou-day': {
   3: "Poursuivez vers Ouarzazate. Si vous choisissez la visite des studios Atlas, découvrez les décors avant de rejoindre la kasbah de Taourirt. L'entrée aux studios est une option payante.",
   5: "Reprenez la route de montagne vers Marrakech. Une halte dans une coopérative d'argan peut être ajoutée sur demande, si le temps disponible le permet."
  },
  'imlil-atlas-day': {
   0: "Quittez votre hébergement à Marrakech en 4×4 privé et prenez la direction d'Agafay. Faites des pauses photo lorsque les terres agricoles cèdent la place aux paysages désertiques.",
   4: "Retrouvez votre guide de montagne à Imlil. Marchez pendant une à deux heures entre noyers, hameaux et ruisseaux en direction des cascades, à un rythme adapté à votre groupe.",
   5: "Déjeunez chez une famille berbère avec vue sur la vallée : salade, tajine ou couscous, puis fruits et thé à la menthe."
  }
 },
 'de': {
  'ourika-valley': {
   0: "Ihr Fahrer holt Sie an Ihrer Unterkunft oder am nächsten mit dem Fahrzeug erreichbaren Treffpunkt ab. Im privaten Fahrzeug fahren Sie nach Süden in die Ausläufer des Atlasgebirges.",
   1: "Besuchen Sie eine Frauenkooperative und erfahren Sie, wie Arganöl hergestellt wird. Bei Interesse können Sie die Produkte ansehen, bevor es weiter ins Tal geht.",
   2: "Folgen Sie dem Fluss vorbei an Terrassenfeldern, Walnussbäumen und Bergdörfern. Montags gehört der Wochenmarkt von Tnin Ourika zum Programm.",
   3: "Wandern Sie auf dem felsigen Pfad zum ersten Wasserfall; rechnen Sie mit etwa 45 Minuten pro Strecke. Alternativ bleiben Sie im Dorf und in den Cafés am Fluss. Teilen Sie uns Ihre Wahl mit, damit wir die Begleitung organisieren können.",
   4: "Genießen Sie Tajine oder Gegrilltes in einem Restaurant unter den Bäumen am Fluss. Mittagessen und Getränke zahlen Sie separat, sofern sie nicht im Angebot enthalten sind.",
   5: "Schauen Sie sich die Kunsthandwerksstände an oder entspannen Sie am Wasser. Fragen Sie bei warmem Wetter Ihren Guide nach den Bedingungen, bevor Sie die natürlichen Flussbecken betreten.",
   6: "Ihr privater Fahrer bringt Sie auf der Talstraße zurück nach Marrakesch, zu Ihrer Unterkunft oder zum vereinbarten Ausstiegspunkt."
  },
  'ouzoud-waterfalls': {
   0: "Ihr Fahrer-Guide holt Ihre Reisegruppe an der Unterkunft oder am nächsten erreichbaren Treffpunkt ab. Im privaten klimatisierten Fahrzeug geht es nach Nordosten.",
   1: "Die etwa dreistündige Fahrt führt durch Ackerland und Olivenhaine zu den Ausläufern des Mittleren Atlas. Unterwegs legen Sie eine Pause ein.",
   2: "Sie erreichen das Dorf Tanaghmeilt und beginnen Ihren Besuch der Wasserfälle. Besprechen Sie den Fußweg mit Ihrem Fahrer-Guide, bevor Sie in die Schlucht hinabsteigen.",
   3: "Vor Ort bleiben etwa vier bis fünf Stunden einschließlich Mittagessen. Entdecken Sie Aussichtspunkte und schattige Haine und beobachten Sie die Makaken in den Bäumen. Eine optionale Bootsfahrt führt näher an die Wasserfälle.",
   5: "Planen Sie 20–30 Minuten für den Aufstieg ins Dorf ein. Vor dem Treffen mit Ihrem Fahrer bleibt Zeit für die Verkaufsstände.",
   6: "Fahren Sie mit einer Pause unterwegs zurück nach Marrakesch. Je nach Verkehr erreichen Sie Ihre Unterkunft zwischen 19:00 und 20:00."
  },
  'essaouira-day': {
   2: "Ihr Fahrer setzt Sie nahe der Altstadt ab. Sie haben etwa vier Stunden für Erkundungen; eine Führung kann auf Wunsch organisiert werden.",
   3: "Spazieren Sie durch die Gassen mit ihren Werkstätten und entlang der Skala-Befestigung mit Blick auf den Atlantik. Entdecken Sie Thuja-Holzarbeiten, Silberschmuck und kleine Galerien.",
   6: "Treffen Sie Ihren privaten Fahrer am Eingang der Medina. Mit Pausen unterwegs erreichen Sie Ihre Unterkunft in Marrakesch zwischen 19:00 und 20:00."
  },
  'ait-ben-haddou-day': {
   0: "Ihr Fahrer holt Sie an der Unterkunft ab. Die Bergstraße führt in den Hohen Atlas, vorbei an Dörfern am Hang und bewirtschafteten Terrassen.",
   1: "Halten Sie an Aussichtspunkten rund um den 2.260 Meter hohen Pass. Fotografieren Sie Gipfel, Täler und Serpentinen, bevor die Fahrt ins Land der Kasbahs weitergeht.",
   2: "Erkunden Sie das befestigte Lehmdorf zu Fuß und steigen Sie durch seine Gassen zum Speicher auf dem Hügel. Entdecken Sie die Architektur, den Talblick und bekannte Filmkulissen.",
   3: "Weiterfahrt nach Ouarzazate. Auf Wunsch besichtigen Sie die Kulissen der Atlas Film Studios, bevor Sie zur Kasbah Taourirt fahren. Der Studioeintritt ist ein optionaler Zusatz.",
   5: "Fahren Sie über die Bergstraße zurück nach Marrakesch. Auf Wunsch und bei ausreichender Zeit ist unterwegs ein Besuch einer Argankooperative möglich."
  },
  'imlil-atlas-day': {
   0: "Fahren Sie von Ihrer Unterkunft in Marrakesch im privaten Geländewagen nach Südwesten Richtung Agafay. Halten Sie für Fotos, während das Ackerland in Steinwüste übergeht.",
   4: "Treffen Sie Ihren örtlichen Bergführer in Imlil. Wandern Sie ein bis zwei Stunden an Walnusshainen, Weilern und Bächen vorbei zu den Wasserfällen, im passenden Tempo für Ihre Gruppe."
  }
 },
 'es': {
  'ourika-valley': {
   0: "Su conductor le recoge en el alojamiento o en el punto accesible más cercano. Viaje hacia el sur en vehículo privado, rumbo a las estribaciones del Atlas.",
   3: "Siga el sendero rocoso hasta la primera cascada, con unos 45 minutos de marcha por trayecto. También puede quedarse en el pueblo y sus cafés junto al río. Indíquenos su preferencia para organizar el acompañamiento.",
   4: "Disfrute de un tajín o de platos a la parrilla en un restaurante bajo los árboles junto al río. El almuerzo y las bebidas se pagan aparte, salvo que estén incluidos en su presupuesto."
  },
  'ouzoud-waterfalls': {
   0: "Su conductor-guía recoge a su grupo en el alojamiento o en el punto accesible más cercano. Salga hacia el noreste en su vehículo privado con aire acondicionado.",
   1: "El trayecto dura unas tres horas entre campos y olivares hacia las estribaciones del Atlas Medio. Se realiza una parada de descanso durante el viaje.",
   3: "Disponga de cuatro a cinco horas en la zona, incluido el almuerzo. Recorra miradores y senderos con sombra y observe los macacos en los árboles. Un paseo en barca opcional le acerca a las cascadas.",
   6: "Regrese por carretera con una parada de descanso. La llegada a su alojamiento en Marrakech está prevista entre las 19:00 y las 20:00, según el tráfico."
  },
  'essaouira-day': {
   3: "Pasee por callejuelas y talleres artesanales y siga las murallas de la Skala con vistas al Atlántico. Descubra trabajos en madera de tuya, joyas de plata y pequeñas galerías."
  },
  'ait-ben-haddou-day': {
   1: "Pare en los miradores del puerto de Tizi n'Tichka, a 2.260 metros de altitud. Fotografíe las cumbres, los valles y las curvas antes de descender hacia la región de las kasbahs.",
   2: "Explore a pie el pueblo fortificado de adobe y recorra sus callejuelas hasta el granero de la colina. Descubra su arquitectura, las vistas al valle y los escenarios de cine y televisión.",
   5: "Regrese a Marrakech por la carretera de montaña. Si lo solicita y queda tiempo, puede añadirse una visita a una cooperativa de argán."
  },
  'imlil-atlas-day': {
   0: "Salga de su alojamiento en Marrakech en un 4×4 privado hacia Agafay. Haga paradas para fotografiar el paisaje mientras los campos dejan paso al desierto pedregoso.",
   4: "Reúnase con su guía de montaña en Imlil. Camine una o dos horas entre nogales, aldeas y arroyos hacia las cascadas, a un ritmo adaptado a su grupo.",
   6: "Regrese a Marrakech por la carretera del desfiladero, pasando por la zona de Asni. El trayecto de vuelta dura aproximadamente una hora y media."
  }
 },
 'it': {
  'ourika-valley': {
   3: "Seguite il sentiero roccioso fino alla prima cascata, calcolando circa 45 minuti per tratta. In alternativa, restate nel villaggio e nei caffè sul fiume. Comunicateci la vostra scelta per organizzare l'accompagnamento.",
   6: "Ritrovate il vostro autista privato e percorrete la valle verso Marrakech, fino all'alloggio o al punto di rientro concordato."
  },
  'ouzoud-waterfalls': {
   0: "Il vostro autista-guida vi incontra all'alloggio o nel punto accessibile più vicino. Partite verso nord-est nel vostro veicolo privato con aria condizionata.",
   1: "Il viaggio dura circa tre ore, attraverso campi e uliveti verso le pendici del Medio Atlante. È prevista una sosta lungo il percorso.",
   3: "Dedicate alla zona circa quattro o cinque ore, pranzo compreso. Passeggiate tra punti panoramici e boschetti ombreggiati, osservando i macachi sugli alberi. Un giro in barca facoltativo permette di avvicinarsi alle cascate.",
   6: "Ripartite verso Marrakech con una sosta lungo il percorso. L'arrivo all'alloggio è previsto tra le 19:00 e le 20:00, secondo il traffico."
  },
  'essaouira-day': {
   1: "Fate una pausa caffè a Chichaoua, poi visitate una cooperativa femminile per scoprire l'estrazione tradizionale dell'olio di argan. Proseguite tra gli alberi di argan verso Essaouira.",
   3: "Passeggiate tra vicoli e botteghe artigiane, poi seguite i bastioni della Skala con vista sull'Atlantico. Scoprite oggetti in legno di tuia, gioielli d'argento e piccole gallerie."
  },
  'ait-ben-haddou-day': {
   2: "Esplorate a piedi il villaggio fortificato in terra cruda, salendo attraverso i vicoli fino al granaio sulla collina. Ammirate l'architettura, la valle e le ambientazioni note al cinema e alla televisione.",
   5: "Ripercorrete la strada di montagna verso Marrakech. Su richiesta, e se il tempo lo consente, è possibile fermarsi in una cooperativa di argan."
  },
  'imlil-atlas-day': {
   0: "Lasciate il vostro alloggio a Marrakech in 4×4 privato verso Agafay. Fermatevi per fotografare il paesaggio mentre i campi lasciano spazio al deserto roccioso.",
   4: "Incontrate la guida di montagna a Imlil. Camminate per una o due ore tra terrazze con alberi di noce, villaggi e ruscelli verso le cascate, al ritmo adatto al vostro gruppo.",
   5: "Fermatevi in una casa berbera per un pranzo di tre portate con vista sulla valle: insalata, tajine o couscous, poi frutta e tè alla menta.",
   6: "Seguite la strada della gola attraverso la zona di Asni fino a Marrakech. Il viaggio di ritorno dura circa un'ora e mezza."
  }
 },
 'pt': {
  'ourika-valley': {
   3: "Siga o trilho rochoso até à primeira cascata, contando com cerca de 45 minutos em cada sentido. Em alternativa, explore a aldeia e os cafés junto ao rio. Indique a sua preferência para organizarmos o acompanhamento."
  },
  'ouzoud-waterfalls': {
   0: "O seu motorista-guia encontra o seu grupo no alojamento ou no ponto acessível mais próximo. Siga para nordeste no seu veículo privado com ar condicionado.",
   1: "A viagem demora cerca de três horas, atravessando campos e olivais até às encostas do Médio Atlas. Faça uma pausa para descansar pelo caminho.",
   3: "Reserve quatro a cinco horas na zona, incluindo o almoço. Passeie entre miradouros e árvores de sombra e observe os macacos. Um passeio de barco opcional permite aproximar-se das cascatas.",
   6: "Regresse a Marrakech com uma pausa pelo caminho. A chegada ao alojamento está prevista entre as 19:00 e as 20:00, consoante o trânsito."
  },
  'essaouira-day': {
   1: "Faça uma pausa para café em Chichaoua e visite uma cooperativa feminina para conhecer a extração tradicional do óleo de argão. Continue entre arganais até Essaouira.",
   3: "Passeie pelas ruelas e oficinas de artesanato e siga as muralhas da Skala com vista para o Atlântico. Descubra peças em madeira de tuia, joias de prata e pequenas galerias."
  },
  'ait-ben-haddou-day': {
   2: "Explore a pé a aldeia fortificada de terra, seguindo as ruelas até ao celeiro no alto da colina. Aprecie a arquitetura, a vista sobre o vale e os cenários de cinema e televisão.",
   5: "Regresse a Marrakech pela estrada de montanha. Pode acrescentar uma visita a uma cooperativa de argão, mediante pedido e se houver tempo."
  },
  'imlil-atlas-day': {
   0: "Saia do seu alojamento em Marrakech num 4×4 privado em direção a Agafay. Pare para fotografar a paisagem à medida que os campos dão lugar ao deserto rochoso.",
   4: "Encontre o seu guia de montanha em Imlil. Caminhe durante uma a duas horas entre nogueiras, aldeias e ribeiros até às cascatas, a um ritmo adaptado ao seu grupo.",
   5: "Almoce numa casa berbere com vista para o vale: salada, tajine ou cuscuz, seguidos de fruta e chá de hortelã."
  }
 },
 'nl': {
  'ourika-valley': {
   2: "Volg de rivier langs terrasvelden, walnotenbomen en bergdorpen. Op maandag bezoekt u ook de weekmarkt van Tnin Ourika.",
   3: "Volg het rotsachtige pad naar de eerste waterval; reken op ongeveer 45 minuten per richting. U kunt ook in het dorp en bij de cafés aan de rivier blijven. Geef uw voorkeur door zodat we de begeleiding kunnen regelen.",
   6: "Rijd met uw privéchauffeur door de vallei terug naar uw accommodatie in Marrakech of het afgesproken uitstappunt."
  },
  'ouzoud-waterfalls': {
   0: "Uw chauffeur-gids haalt uw gezelschap op bij de accommodatie of het dichtstbijzijnde bereikbare ontmoetingspunt. Rijd naar het noordoosten in uw privévoertuig met airconditioning.",
   1: "De rit duurt ongeveer drie uur, door landbouwgebied en olijfgaarden naar de uitlopers van de Midden-Atlas. Onderweg maakt u een ruststop.",
   3: "U heeft ongeveer vier tot vijf uur ter plaatse, inclusief lunch. Wandel langs uitzichtpunten en schaduwrijke bomen en kijk uit naar makaken. Een optionele boottocht brengt u dichter bij de watervallen.",
   5: "Reken op 20–30 minuten voor de wandeling omhoog naar het dorp. Houd tijd over om de kraampjes te bekijken voordat u uw chauffeur ontmoet."
  },
  'essaouira-day': {
   3: "Wandel door de steegjes met ambachtswerkplaatsen en langs de Skala-muren met uitzicht op de Atlantische Oceaan. Ontdek thuja-houtwerk, zilveren sieraden en kleine galeries."
  },
  'ait-ben-haddou-day': {
   2: "Verken het ommuurde dorp van leem te voet en volg de steegjes naar de graanschuur boven op de heuvel. Bekijk de architectuur, het dal en de bekende film- en televisielocaties."
  },
  'imlil-atlas-day': {
   4: "Ontmoet uw lokale berggids in Imlil. Wandel een tot twee uur langs walnotenbomen, gehuchten en beekjes naar de watervallen, in een tempo dat bij uw gezelschap past."
  }
 }
}
headings = {
 'fr': {('essaouira-day',2): 'Vers 12:00 · Arrivée à la médina', ('ourika-valley',5): 'Après-midi · Temps libre dans la vallée', ('imlil-atlas-day',6): 'Vers 17:00 · Retour par Moulay Brahim', ('ait-ben-haddou-day',1): "Matin · Col du Tizi n'Tichka", ('essaouira-day',3): 'Midi · Médina et remparts'},
 'de': {('imlil-atlas-day',0): '09:00 · Abholung im privaten Geländewagen', ('imlil-atlas-day',2): 'Lalla Takerkoust · Halt am See'},
 'es': {('essaouira-day',1): 'Mañana · Chichaoua y arganales', ('ait-ben-haddou-day',6): 'Alrededor de las 19:00 · Regreso a Marrakech', ('ouzoud-waterfalls',3): 'Final de la mañana y tarde · Senderos de las cascadas'},
 'it': {('imlil-atlas-day',0): '09:00 · Partenza in 4×4 privato', ('ait-ben-haddou-day',3): 'Pomeriggio · Ouarzazate e studios facoltativi', ('ait-ben-haddou-day',6): 'Intorno alle 19:00 · Rientro a Marrakech', ('essaouira-day',3): 'Mezzogiorno · Medina e bastioni'},
 'pt': {('imlil-atlas-day',0): '09:00 · Partida em 4×4 privado', ('imlil-atlas-day',2): 'Lalla Takerkoust · Paragem junto ao lago', ('ait-ben-haddou-day',6): 'Por volta das 19:00 · Regresso a Marrakech', ('ouzoud-waterfalls',3): 'Final da manhã e tarde · Trilhos das cascatas'},
 'nl': {('ourika-valley',6): '17:00–18:00 · Terug in Marrakech', ('imlil-atlas-day',2): 'Lalla Takerkoust · Stop bij het meer', ('ait-ben-haddou-day',3): "Middag · Ouarzazate en optionele filmstudio's", ('imlil-atlas-day',1): 'Ochtend · Kamelenrit in Agafay'}
}
for code, trips in corrections.items():
    file = ROOT / 'data/locales' / (code + '.json')
    data = json.loads(file.read_text(encoding='utf-8'))
    for trip in updates.values():
        for row in trip['itinerary']:
            for source in row:
                data['strings'][source] = html.unescape(data['strings'][source])
    for identity, steps in trips.items():
        for index, description in steps.items():
            data['strings'][updates[identity]['itinerary'][index][1]] = description
    for (identity, index), heading in headings[code].items():
        data['strings'][updates[identity]['itinerary'][index][0]] = heading
    file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print('Corrected translation meaning, headings and clock formats in six languages.')
