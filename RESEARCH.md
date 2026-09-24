# DesertGate — research and design decisions

Reviewed 13 September 2026. This is an implementation reference, not an endorsement or a verification of supplier operations.

## Benchmarks

| Website reviewed | Useful pattern | DesertGate implementation |
| --- | --- | --- |
| [Morocco Shiny Days](https://moroccoshinydays.com/) | Clear private-trip positioning, personal planning and separate destination collections | Distinct journeys, day trips and experiences; itinerary request instead of an unsupported instant booking promise |
| [Morocco Tours Agency — Fes excursions](https://moroccotours.agency/fr/excursion-dune-journee-au-depart-de-fes/) | Departure city matters; clear geographic grouping | Chefchaouen day trip starts from Fes, not Marrakech; start and finish displayed on every card |
| [Marrakech Desert Trips](https://marrakechdeserttrips.com/) | Separate shared/private categories and dedicated trip details | Travel-style preference, full details and direct links to each trip |
| [GetYourGuide — Sahara product](https://www.getyourguide.com/marrakesh-l208/from-marrakech-3-day-sahara-tour-with-private-tent-meals-t712934/) | Duration, pickup, transport, inclusions and restrictions help a visitor decide | Structured facts, practical context, itinerary, meeting-point notes and clear request status |
| [Civitatis — Marrakech](https://www.civitatis.com/en/marrakech/) | Differentiate short activities, day excursions and overnight tours | Three browsable collections, duration sorting and a comparison table |

The competitors' transaction systems were not tested. Their displayed reviews, certifications, guarantees, fulfillment and company claims were not independently verified. No such claims were transferred to DesertGate.

## Route and editorial references

The pre-existing user-provided tour material was rewritten, clarified and reorganized, with additional geographic and product checks against these pages:

- [Marrakech to Fes via Erg Chebbi](https://moroccoshinydays.com/sahara/marrakech-to-fes-via-erg-chebbi-desert): one-way four-day route and a second desert night.
- [Imperial Cities & Desert](https://moroccoshinydays.com/journeys/morocco-imperial-cities-and-desert-tour): nine-day route through the imperial cities and south.
- [Grand Morocco tour](https://moroccoshinydays.com/journeys/grand-morocco-tour): longer Morocco circuit as a reference; the site's final route is an original planning proposal with an Essaouira extension.
- [Marrakech desert route](https://marrakechdeserttrips.com/tour/excursion-to-the-merzouga-desert-from-marrakech/): conventional Marrakech–southern valleys–Merzouga route.
- [Ourika day excursion](https://marrakechdeserttrips.com/tour/ourika-valley-day-trip-from-marrakech/): valley and Setti Fatma outing.
- [Fes day excursions](https://moroccotours.agency/fr/excursion-dune-journee-au-depart-de-fes/): Chefchaouen and Volubilis/Meknes departures from Fes.
- [Marrakech cooking experience](https://moroccoshinydays.com/experiences/marrakech-private-cooking-class): participatory cooking rather than generic sightseeing.
- [Official Marrakech road trips](https://www.visitmarrakech.com/en/road-trips/): Atlas, ocean and Agafay distinctions.
- [Official Morocco tourism](https://www.visitmorocco.com/en): destination context.

Descriptions are original; competitors' paragraphs were not copied. Route schedules are illustrative and require the actual operator's validation. No supplier inventory, availability, private vehicle, named accommodation or included activity is represented as contracted. Photos are destination inspiration, not promised properties.

## User-directed presentation

- No prices or ratings.
- No departure/duration search block.
- Full-screen photography, transparent header over the image, larger text, subtle image motion and scroll animation.
- Local destination assets replace broken image URLs and incorrect geography.
- Every trip opens its own itinerary. Shortlisting, comparison and request context preserve the selected trip.
- No invented reviews, accreditation badges, staff history, telephone numbers or live booking guarantees.

## Validation

Browser checks cover all 26 trip/detail mappings, itinerary lengths, categories, text filtering, saved-trip persistence, comparison, mobile navigation, 360/390-pixel layouts, request error preservation and confirmed local request storage. API checks cover input validation, idempotent retries, changed-body conflicts, cross-origin submissions and non-public data paths. Tests use an isolated temporary inbox.

The local Python server stores actual requests and returns a reference only after committing them. It does not send email/WhatsApp or reserve supplier inventory. The real company identity, contact channel, operational approval of routes and public deployment remain separate handoff items.


## September 13: studio, languages and galleries

The user selected [Moroccan Holidays Experiences](https://moroccanholidaysexperiences.com/) as the visual reference and explicitly requested its photographs. Its specific activity photography, direct contact actions and image-led collections informed the new galleries. The reference also displays zero-value prices and repeated collections; those elements were not reproduced. Source URLs for 32 imported photographs are recorded in `data/imported-media.json`.

DesertGate now includes a local owner dashboard, editable trip and homepage content, image uploads, publication statuses, a request inbox, ten editable languages and right-to-left Arabic. The original English marketing stories are in `data/stories.json`. Longer translations are local OPUS/Argos machine drafts with authored interface overrides; native linguistic review is not claimed.

Implementation references: [MDN text direction](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/dir), [OWASP upload validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html), [Argos Translate](https://github.com/argosopentech/argos-translate), [CTranslate2](https://opennmt.net/CTranslate2/python/ctranslate2.Translator.html).


The user subsequently removed Arabic, Russian and Chinese. The current configured list is English, French, Spanish, German, Italian, Portuguese and Dutch. Removed-language links fall back to English.
