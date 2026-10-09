# Laura Luxury Journeys — public site and local studio

## Production and release

The public domain is `https://lauraluxuryjourneys.com`, served by the Cloudflare Worker `laura-luxury-journey` from **`dist`**. The GitHub remote named `github` is the custom-domain deployment source. The remote named `origin` belongs to a separate Sites deployment. A push may auto-deploy: obtain the requested release approval first. Never publish the repository root, `.local`, private CMS data or audit evidence as website assets.

Production is a static site with seven languages and 26 trips, not the Python CMS backend. `/api/*` and `/admin` return 404/noindex there. The enquiry form prepares a message in WhatsApp; the visitor must press Send. It does not create a local inbox record, take payment, reserve inventory or confirm a booking. Email is optional in this WhatsApp flow.

To regenerate the reviewed static export **without touching the local database**:

```powershell
python scripts/prepare_public_assets.py
python scripts/build_seo.py
python scripts/check_seo.py
python scripts/check_trip_editorial.py
python scripts/check_public_release.py
node scripts/check_whatsapp.cjs
```

`prepare_public_assets.py` creates small branding assets, copies the runtime files, sanitizes the published photography payloads and removes redundant public editorial/source-data copies. The original editorial files outside `dist` are retained. Do not copy the full `data` directory back into `dist` afterward. `build_seo.py` preserves the 217 existing indexable URLs, generates localized HTML and visible trip fallback articles, plus the sitemap index, full map and seven language maps.

After intentional CMS content editing, `python scripts/build_static_content.py` exports the local database and runs the preparation/SEO steps. This command initializes/uses `.local/requests.sqlite3`; do not run it merely for an SEO rebuild. The root HTML remains API-backed for the studio, while generated pages use `data-static-site` and fetch static payloads directly.

For production-like local serving use `wrangler dev --ip 127.0.0.1 --port 8092 --local`, then `python scripts/check_public_release.py --http`. This route check assumes port 8092. Review the audit, opportunities, roadmap and implementation log in `docs/` before approving deployment. Production HTTPS normalization and Google indexing must be verified separately; generated files alone do not fix Cloudflare settings or Google's stored records.

## Local studio

Run from this directory:

```powershell
python -m pip install -r requirements.txt
python server.py
```

- Website: [localhost:8080](http://127.0.0.1:8080/)
- Admin: [localhost:8080/admin](http://127.0.0.1:8080/admin)

No frontend build is needed. Python serves the site and SQLite content; Pillow processes uploaded photos. The server listens on localhost only.

## Your admin

On the first visit to `/admin`, create your own username and password (at least 12 characters). No shared or default owner credentials are installed.

- **Trips & experiences:** create, edit, publish, hide or archive trips; change routes, duration, descriptions, marketing paragraphs, highlights, day-by-day plans and overnight locations.
- **Trip photographs:** select multiple images, reorder them, change the cover or upload new photos. The first image is the cover. Draft trips remain private.
- **Photo library:** upload several JPG, PNG or WebP photos at once; edit their descriptions, captions and credits. Uploads are converted to WebP and stripped of original metadata.
- **Site content:** edit the brand, homepage headings and paragraphs, four hero photographs, business details, WhatsApp number and Instagram/Facebook/TikTok/YouTube links. The hero starts with the medina, followed by Moroccan craftsmanship, Essaouira and Chefchaouen. Configured social links appear in the footer. The floating WhatsApp icon opens your number once it is configured.
- **Languages:** enable/hide languages, review the full wording, edit English interface copy or add another language. Individual trip translations can be edited directly in the trip editor.
- **Trip requests:** legacy local inbox management remains available; the current public WhatsApp form does not submit to it.

Changes persist in the local database. Revision checks prevent an older editor from overwriting a newer save. Owner passwords are hashed; admin writes require a signed-in session and CSRF token.

## Customer experience

The initial collection has 26 itineraries, each with 3–6 photographs. Galleries include card arrows, a thumbnail strip and a full-screen viewer with keyboard and touch controls. The header stays transparent over the animated hero. Reduced-motion preferences are respected.

Every itinerary includes an interactive route map with numbered stops, a fitted route view and an OpenStreetMap link. The map uses Leaflet 1.9.4 and OpenStreetMap tiles with visible attribution. For a public high-traffic deployment, review the [OpenStreetMap tile usage policy](https://operations.osmfoundation.org/policies/tiles/) and choose a suitable tile provider if needed.

English, French, Spanish, German, Italian, Portuguese and Dutch are available. The language remains selected when opening or sharing a trip. The original English copy and key translated interface wording are authored; longer translations are editable machine drafts and have not had a native-speaker review. New wording falls back to English until translated.

Homepage copy and the 26 trip titles, summaries, suitability notes and introductory paragraphs were revised for clearer customer decisions. The editorial snapshot is in `data/marketing-copy.json`; live edits remain in the CMS. Fresh installations use the updated seed catalog, stories and site defaults. `data/marketing-translations.json` supplies authored translations for the main new headings, actions and trip titles through `scripts/polish-translations.py`. Routes, durations and practical conditions are preserved. The WhatsApp button appears only after a number is configured.

No prices, ratings, invented reviews or departure/duration search block are displayed. The trip collection retains category browsing, text filtering, duration sorting, saved trips and comparisons.

## Storage and backup

- `.local/requests.sqlite3`: trips, site settings, translation overrides, owner account, sessions and inquiries.
- `uploads/`: photos added through the admin.
- `data/trips.seed.json`, `data/stories.json`, `data/media.seed.json`: initial content, imported only when the CMS is first initialized.
- `data/locales/`: generated translation dictionaries; admin overrides are stored separately in SQLite.
- Editorial photography records remain outside the public export. The owner confirmed ownership on 9 October 2026; public source URLs, credits and licensing/research metadata are omitted. Descriptive alt text and captions remain. A photograph does not, by itself, specify the venue included in a booking.

Back up both the database and `uploads/`. For a simple file copy, stop the server first. Earlier source versions are preserved under `../.backups/`.

The legacy local API commits requests to SQLite before returning a reference and supports idempotent retries. That is a separate capability from the current public WhatsApp form. No automatic email, WhatsApp message, payment or supplier booking is sent by that form.

## Development checks

Use a separate database and port for tests; never point integration tests at the live local inbox:

```powershell
$env:DESERTGATE_DB = "$env:TEMP\desertgate-test.sqlite3"
python server.py --port 8081
```

`scripts/qa-cms.cjs` verifies the isolated port-8081 site: owner access, trip lifecycle, uploads, gallery controls, all seven active languages, mobile layout, translated form submissions, inbox status, contact settings, revision conflicts and stored-text escaping. It uses the bundled local Playwright runtime.

`scripts/local-translations.py` is a build-time tool using locally downloaded OPUS/Argos translation models and CTranslate2 in `.local/translator`. Models are not loaded by the website or sent to visitors. `scripts/polish-translations.py` applies authored interface wording. Admin translation overrides are never overwritten by these scripts.

Photography originals and the 2026-09-15 upgrade are documented in `PHOTO-SOURCES.md`. Imported high-resolution media use responsive WebP files in the hero, destination cards and tour galleries; source originals remain private in `.local/photo-originals/`.
