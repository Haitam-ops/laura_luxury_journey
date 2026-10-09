# Laura Luxury Journeys — website and commercial audit

**Audit date:** 9 October 2026, UTC. **Production baseline:** `eb76fbf`, branch `main`. **Scope:** production observations plus reviewed local changes; no deployment, push, DNS, WAF, SSL or cache changes made during this audit. The site remains at its earlier production version until an approved release.

## Executive decision

This is a viable enquiry website for private Morocco travel, with substantial itinerary material and a working WhatsApp handoff. It is not yet a proven acquisition business. Invest in a focused launch and measurement; do not invest first in a redesign, another framework, hundreds of articles or broad advertising.

The immediate search problem is inconsistent HTTP/HTTPS indexing after a recent access failure. Google indexed the **HTTP homepage** and selected it as canonical despite the declared HTTPS canonical. The HTTPS homepage and priority Sahara trip have older 403 records. A new Google live test of the trip succeeds. These are different observations: access has improved, but indexing has not yet caught up, and the sitemap report still says it could not fetch.

The next commercial constraint is confidence in the actual offer: who operates the business, what “luxury” means for each trip, how a price is determined, and what terms apply. Reviews and social profiles are deliberately deferred by the owner. Photography is treated as owner-owned on the owner's explicit declaration. Neither deferral prevents the technical work; neither supplies the missing operational information.

| Dimension | Production assessment /10 | Evidence and limit |
|---|---:|---|
| Technical SEO readiness | 6 | 217 valid 200 routes and coherent HTTPS metadata; HTTP canonical conflict, stale Google errors and rendering dependencies remain |
| Current organic visibility | 2, provisional | HTTP homepage indexed; no usable GSC performance history; this is not a measured traffic score |
| Content and search intent | 6 | 26 differentiated itineraries with practical details; brief guides and incomplete commercial decision information |
| Competitive positioning | 4, provisional | Attractive private-travel proposition; comparable competitors specify operator identity, accommodation and price basis more clearly |
| Conversion readiness | 6 | Working enquiry design and clear no-payment wording; WhatsApp handoff is not a received lead; no conversion measurement |
| Performance and UX | 5 | Mobile production home LCP 4.9s; trip LCP 21.8s in one lab run; no CWV field data |
| Overall marketability | 5, provisional | Credible starting product, but no verified demand, bookings, economics or acquisition evidence |

These scores measure different things. They are engineering/commercial judgments, not Google scores or forecasts. Local improvements do not retroactively improve the production baseline.

## Evidence register and limits

All evidence lives in [`evidence/2026-10-09`](evidence/2026-10-09). `baseline.json`/CSV record the 217-page inventory and production GET results; `http-infrastructure.json` records selected response behavior. Dashboard snapshots are in `gsc-dashboard.json` and `cloudflare-dashboard.json`, with emails, visitor IPs and account identifiers redacted. `google-trip-live.png` records Google's successful live fetch. Lighthouse JSON files contain timestamps, environment and lab findings. `local-after.json`/CSV and `local-route-checks.json` describe the local release, not production.

The route audit parses local generated HTML and separately GETs the equivalent production URLs. It does not claim that all remote response bodies were byte-identical to local HTML. Remote status checking uses an ordinary audit user agent, not a verified Googlebot identity. Its total request duration is **not TTFB**. No private customer inbox, credentials or revenue records were accessed.

Browser-based final retesting was interrupted by a browser policy rejection when reopening the local preview. Earlier production/UI observations and the initial local static fallback were inspected; final checks use release assertions, HTTP tests, an isolated submit-handler test and Lighthouse. Full final interactive/mobile/keyboard regression remains a release gate. A first post-interruption Lighthouse attempt failed while the local server was stopped; the server was restarted and successful runs followed.

## What exists and who it serves

Laura Luxury Journeys offers 26 Morocco itineraries: 8 multi-day journeys, 6 day trips and 12 experiences. Visitors browse/filter, compare up to three trips, save favorites locally, inspect galleries, itineraries and optional maps, and request a tailored proposal via WhatsApp. There is no public checkout, payment, live inventory, automatic reservation or supplier confirmation.

The target language markets are **English, French, Spanish, German, Italian, Portuguese and Dutch**, confirmed by the owner. Countries and actual customer mix are unknown; language alone is not evidence of nationality, residence or demand. Customer segments suggested by the copy include private couples/families/friends, Marrakech visitors and people planning multi-city holidays. Those segments are positioning hypotheses, not measured customer cohorts.

### Route inventory

| Route family | Count | Purpose / indexability |
|---|---:|---|
| `/?lang={en,fr,es,de,it,pt,nl}` | 7 | Canonical language homepages |
| `/{language}/journeys/` | 7 | Full trip catalogue; discover all 26 routes |
| `/{language}/journeys/{trip-id}/` | 182 | Main commercial landing pages; 26 × 7 |
| `/{language}/travel-notes/{time,stays,seasons}/` | 21 | Planning guides linked to trips |
| `/`, `/index.html`, `/{language}/` | aliases | Return homepage content, canonical points to query-language homepage |
| `/?trip={id}&lang={language}` | legacy | 301 to clean trip route, retaining other query parameters |
| `/api/*`, `/admin`, `/admin/*` in production | excluded | 404 with `X-Robots-Tag: noindex`; local CMS only |
| Unknown route or unknown trip | excluded | Tested 404; not a homepage soft-404 |
| `robots.txt`, sitemap index, seven language sitemaps, legacy sitemap | discovery | XML/robots assets; not search landing pages |

See the complete URL/title/description inventory in `baseline.csv`, and the page-by-page commercial plan in [SEO_OPPORTUNITIES.md](SEO_OPPORTUNITIES.md). No pagination/faceted URL system exists: filters are client-side. All trip routes are linked by the catalogue, so the tested static inventory has no orphan trips.

### Architecture and deployment

Vanilla HTML/CSS/JavaScript, Python standard-library build scripts and a separate local Python/SQLite CMS. Pillow handles images. No frontend framework or package manifest is required. `scripts/build_pages.py` emits HTML; `build_seo.py` emits 217 URLs, language alternates, metadata and nine XML discovery files (one full sitemap, one index, seven children).

`worker.js` serves `dist` through Cloudflare Workers Static Assets. `wrangler.jsonc` correctly limits the asset directory to `./dist`. Root/language routes run through the Worker; some static assets bypass it, explaining the observed `www/sitemap.xml` duplicate. Worker binding is `ASSETS`; no D1/R2 production datastore is configured here. GitHub remote `github` is the custom-domain deployment source. Remote `origin` is a separate ChatGPT Sites project; publishing there would not update this domain.

`server.py` and `cms.py` are local administration infrastructure, not the public production backend. The CMS uses hashed passwords, hashed sessions, revision checks and CSRF protection, and listens on localhost. The current public form prepares a WhatsApp message instead of writing to SQLite. Old local-inbox code and dormant reference/download UI exist; the misleading visible FAQ claim was corrected. Dormant code is low priority and should not be confused with a live enquiry database.

### Rendering findings

Production homepages depend on a large language JSON payload; the initial non-English homepage body was English before enhancement. The boot loader tried the unavailable production `/api/content` before fetching static JSON. Saved browser language could also override a root URL. Direct `/{language}/` was not properly respected by the boot loader.

Production trip pages contained full itinerary text only inside `noscript`, while JavaScript rendered the detail modal over the homepage. This is weaker progressive rendering than a normal visible article, although Google's JavaScript renderer can still process the site. Two raw H1s were present on 182 trip pages; the count itself is not a ranking penalty, but the page purpose and accessible hierarchy were unclear.

**Implemented locally:** visible static trip article with itinerary, practical details, FAQs, breadcrumbs and WhatsApp link; remove it only after the enhanced trip dialog opens successfully. One raw H1 per published URL; trip dialog uses the trip title as H1. Localized initial homepage UI, explicit static-mode payload loading, path-language handling and consistent language-switch destinations. The original modal design is retained after successful enhancement. Further work could remove hidden homepage loading on direct trip visits; a framework rewrite is unnecessary.

## Google Search Console — observed facts

Inspected around 00:20–00:27 UTC, 9 October. Available properties: `sc-domain:lauraluxuryjourneys.com` and `https://lauraluxuryjourneys.com/`. The domain property is the primary reporting property and was added 8 October.

| Report | Observation | Interpretation |
|---|---|---|
| Search performance, 3-month selection | Processing; update approximately 10 hours old; query/page/country/device tables unavailable | Clicks, impressions, CTR, average position and trends **unavailable**, not zero |
| 7/28-day, 6/12-month comparisons | No populated history to compare | Cannot identify page-two gains, declining queries, irrelevant demand or cannibalization from actual data yet |
| Page indexing / crawl stats | Processing / no usable data | Cannot quantify indexed totals or exclusion categories |
| Links | Processing | No reliable backlink baseline or authority score |
| CWV mobile and desktop | Insufficient usage data over preceding 90 days | No field LCP/INP/CLS conclusion |
| Manual actions / security issues | No issues detected | No reported penalty or security issue in these reports |
| Sitemaps, submitted 9 October | Full sitemap and index: Unknown type, Couldn't fetch, 0 discovered, blank last-read | Still unresolved in the stored report; local XML validity is not successful Google processing |
| Settings robots report | No robots file shown | Reporting lag/unpopulated record; the actual public robots URL exists and responds |

**Individual URLs:**

* `https://lauraluxuryjourneys.com/`: not on Google in stored inspection; last crawl 8 October 17:47:37, smartphone Googlebot, robots allowed, fetch 403.
* `http://lauraluxuryjourneys.com/`: on Google; last crawl 8 October 19:19:22, successful fetch. Declared canonical `https://lauraluxuryjourneys.com/?lang=en`; Google's selected canonical was the inspected HTTP URL.
* `https://lauraluxuryjourneys.com/en/journeys/sahara-marrakech-3-days/`: stored crawl 8 October 17:49:39, 403, not indexed. **Live test 9 October approximately 00:26: available to Google, successful fetch, indexing allowed.** This does not prove it is now indexed.

Previous manual brand searching found the HTTP homepage for a brand-plus-domain query while the plain brand phrase did not show it in the observed first results. This is one contextual search observation, not a universal rank or market-wide visibility measurement. Do not keep treating repeated personal searches as an SEO KPI.

## Cloudflare and HTTP

Zone `lauraluxuryjourneys.com`, Free plan, Full DNS setup. Root and www point to the `laura-luxury-journey` Worker. Google verification TXT exists. No mail MX/SPF/DKIM/DMARC records were visible in the DNS list; no domain email is configured on the site. Choose a mail provider before adding records or publishing an address.

During the 8–9 October 24-hour overview: **270 edge “unique visitors”, 3.13k requests, 92.07% cached, 248 MB served and 229 MB cached**. These include bots and developer/audit traffic; they are not customers, sessions, organic visits or leads. Later security counts increased during this audit. Sampled logs were dominated by developer traffic and are insufficient to attribute the older Google 403 to a specific rule.

TLS mode Full; TLS 1.3 and Automatic HTTPS Rewrites on. **Always Use HTTPS off**, corroborated by HTTP homepage returning 200. Minimum TLS is 1.0. Successful HTTPS requests validate that the tested endpoint certificate is accepted by the client; certificate expiry details were not captured. Do not make unverified certificate-expiry claims. No external origin exists in this Worker architecture, so a generic origin-TLS recommendation is inappropriate.

Bot Fight Mode and Under Attack Mode off. One active custom rule blocks eight specified AI-training user agents; it excludes robots.txt. Googlebot is not in its described blocked list. No global security disablement or spoofable Googlebot allow-rule was introduced. Zero custom Cache Rules and zero Cache Response Rules. Caching Standard, browser TTL UI 4 hours; actual Worker responses use `public, max-age=0, must-revalidate`. Development Mode off. Rules overview showed templates; this is not evidence that all possible account-level redirect mechanisms were exhaustively enumerated. Runtime behavior is the decisive evidence below.

| URL / request | Result |
|---|---|
| 217 sitemap URLs over HTTPS | All 200 in bounded production crawl |
| `http://lauraluxuryjourneys.com/` | **200; should normalize to HTTPS** |
| `https://www.lauraluxuryjourneys.com/` | 301 to HTTPS root |
| `https://www.lauraluxuryjourneys.com/sitemap.xml` | 200; static route bypasses hostname redirect |
| Legacy French trip parameters | 301 to clean French trip URL |
| Trip without trailing slash | 307 to trailing slash |
| Unknown trip/page | 404 |
| `/api/content`, `/admin` | 404, noindex |
| JSON / PNG assets | Correct MIME types, 200 |
| HTML/JSON with compression negotiation | Brotli observed; HTTP/2 measured in lab, HTTP/3 advertised |

### Concrete external fix, not yet applied

Enable **SSL/TLS → Edge Certificates → Always Use HTTPS** for this zone. This redirects HTTP requests to HTTPS while preserving path/query. Verify root, a language homepage, a trip and sitemap afterward; check no loops and final 200. Optional separate hostname redirect should cover www static paths as well. No cache purge, nameserver move, WAF weakening or HSTS rollout is needed for this correction. Approval is required by the supplied mission's production-change rule.

## SEO, content and schema

Strengths: distinct metadata for all 217 URLs; no duplicate full titles; self-canonical URLs matching sitemap; reciprocal seven-language/x-default targets; real `a[href]` discovery; sensible robots; no fake rating, availability or price schema; genuine 404s. Historical workers.dev canonical references were already repaired before this audit and are not newly claimed fixes.

Weaknesses: HTTP canonical conflict; uncertain sitemap processing; dynamic initial language/body consistency; literary headings provide less commercial clarity than the already descriptive SEO titles; category catalogue previously lacked summaries/grouping; short guides have limited decision value; translations still require native-speaker commercial review. Do not infer geographic targeting from language and do not add country hreflang variants without genuinely different regional content.

Local changes add a useful grouped catalogue, proper guide heading hierarchy, responsive guide images and BreadcrumbList alongside visible navigation. JSON syntax and required breadcrumb shape are checked locally. TravelAgency with a city-only address is not a complete Google LocalBusiness rich-result implementation. No Product/Offer/Review/FAQ rich-result claims are made. A successful Google Rich Results Test was **not** obtained; perform it on the deployed release. Eligibility and rendering do not guarantee display or rankings.

Canonical hints, redirects and sitemap signals have different strengths; consolidate consistently and then inspect Google's selected canonical after recrawl. Google may rewrite titles/descriptions, so CTR improvement must be measured once meaningful query data exists. [Google canonical guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).

Initial visible content and crawlable links improve resilience; JavaScript can be rendered but depends on fetch/render success. [JavaScript SEO](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics), [crawlable links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable). Language must be evident in visible content, not merely an HTML attribute. [Multilingual sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites).

## Performance and UX

Lighthouse 13.5.0, local Windows Chrome, default simulated mobile throttling or desktop preset. Single-run diagnostic measurements, not field data and not guarantees. PageSpeed public API attempts returned 429; the audit used local Lighthouse instead.

| Production baseline | Performance | Accessibility | SEO diagnostic | FCP | LCP | TBT | CLS |
|---|---:|---:|---:|---:|---:|---:|---:|
| Home mobile | 72 | 96 | 100 | 3.4s | 4.9s | 0ms | .003 |
| Home desktop | 82 | 96 | 100 | 1.3s | 2.2s | 0ms | .051 |
| Sahara trip mobile | 58 | 95 | 100 | see JSON | 21.8s | 30ms | .001 |

Home mobile transferred approximately 5,007 KiB. Header logo 1.32 MB, footer logo .82 MB, oversized favicon; photography originals were followed by responsive replacements after boot. Large image savings were the dominant measured opportunity; negligible TBT does not justify replacing the framework. Font CSS and the stylesheet also blocked initial rendering. Root lab server response was about 221ms; that is not an origin-only measurement or real-user percentile.

**Local changes:** display-sized transparent branding assets total 57,762 bytes versus 2,678,575 bytes originally; responsive photography is present at HTML/insertion time; production no longer deliberately incurs an API 404; public payload media provenance is removed. The initial local trip comparison reduced transfer from approximately 4,015 to 1,382 KiB and LCP from 20.1 to 6.9s. A final run after accessibility corrections is recorded in IMPLEMENTATION_LOG. Lab variability and concurrent work limit attribution; these are not deployed gains. LCP still needs work. No INP field measurement is available; TBT is not INP.

Initial accessibility defects included low contrast on small rust/category/tab text, heading jumps and accessible names not reflecting visible gallery text. Targeted local fixes address these. Automated scores do not replace keyboard, zoom, screen-reader or final mobile interaction testing.

## Conversion and commercial competitiveness

The flow is `search result → trip → Plan this trip → details → WhatsApp → visitor presses Send → human quote → booking`. Only the first four stages occur on the website. Opening WhatsApp does not establish receipt, a quote or a booking. No revenue attribution, analytics integration or consent platform is configured. Do not claim a conversion rate or install an invented account ID.

Local form changes make email optional because the enquiry proceeds through WhatsApp; name and party size remain required. An invalid non-empty email is still rejected by native input validation. The FAQ now says that the visitor must send the prepared message. The isolated test exercises the actual submit handler for empty/non-empty email, correct trip/number and popup fallback, without sending a message.

The site's calm design, route-specific driving warnings, inclusion/exclusion detail, seven languages and ability to compare trips are useful. They do not, by themselves, differentiate a luxury operator. Add an accurate operator introduction, actual contact/response hours, a sample proposal, accommodation standards/examples, transport details, and actual booking terms when supplied. Avoid invented names, licensing claims, guaranteed response times and prices. An enquiry model does not require online payment to launch.

### Competitors observed in relevant search results

Searches concerned private 3-day Marrakech–Merzouga travel, 4-day Marrakech–Fes travel and Agafay dinner. Observed 9 October; no search volumes, traffic estimates, backlink counts or exact ranks inferred.

| Competitor / page | Type and observed strength | Action for Laura |
|---|---|---|
| [Marrakech Desert Trips, 3 days](https://www.marrakech-desert-trips.com/tours/marrakech-desert-tours-3-days/) | Direct operator; day-by-day itinerary, camp facilities, group-size price basis, long return-drive disclosure | Describe real camp standard and quote basis; retain the existing long-drive warning |
| [Visit Kingdom of Morocco, 4 days](https://visitkingdomofmorocco.com/circuit/4-day-desert-tour-marrakech-to-fes/) | Direct operator; visible price table by party size, inclusions and WhatsApp proposal path | Explain what changes the quote and whether transport/accommodation is private; do not copy their price |
| [Marrakech Eye Tours, 4 days](https://marrakecheyetours.com/en/tours/marrakech-to-fes-4-days/) | Direct operator; named guide, stated credential and explicit explanation of the fourth day | Introduce the actual operator and explain the itinerary's trade-offs; competitor credential is their claim, not independently verified |
| [GetYourGuide Agafay listing](https://www.getyourguide.com/en-gb/morocco-l169143/agafay-desert-private-sunset-camel-ride-with-atlas-views-t1262497/) | Marketplace/search competitor; duration, pickup, meal and availability details | Specify private transfer versus shared venue, meal/diet arrangements and exact proposal inclusions |

Competitor display claims are observations, not endorsed quality or audited performance. Underserved positioning to test: a transparent comparison of 3/4/5-day desert routes, realistic driving expectations, and useful multilingual pre-trip guidance. This is a differentiation hypothesis; “private luxury Morocco” alone is crowded and not uniquely defensible.

## Priority conclusions

Five biggest problems: (1) HTTP/HTTPS canonical inconsistency and unresolved Google reporting; (2) commercial identity/standards insufficiently evidenced; (3) mobile landing load; (4) no lead-to-booking measurement; (5) catalogue breadth exceeds demonstrated focus and guides need decision value.

Five opportunities: (1) consolidate HTTPS and validate Google recrawl; (2) concentrate on three strong, operationally confirmed itineraries; (3) explain 3/4/5-day and Agafay/Sahara trade-offs using first-hand material; (4) turn existing contacts with riads/travel planners into attributable referrals; (5) measure enquiries, quotes and bookings by landing page and language, improving the complete sales process.

The scored backlog, dependencies, verification plan and 24-hour/7/30/90-day tasks are in [GROWTH_ROADMAP.md](GROWTH_ROADMAP.md). Detailed changes, executed checks, limitations and rollback are in [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md).

### Documentation used

In addition to sources linked above: [helpful, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content), [sitemap report](https://support.google.com/webmasters/answer/7451001?hl=en), [structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies), [breadcrumb implementation](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb), [Workers asset headers](https://developers.cloudflare.com/workers/static-assets/headers/). Guidance supports implementation choices; none promises discovery, indexing or ranking on a timetable.
