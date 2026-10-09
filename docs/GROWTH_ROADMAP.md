# Laura Luxury Journeys — release and growth roadmap

9 October 2026, UTC. This roadmap uses the verified baseline in [WEBSITE_AUDIT.md](WEBSITE_AUDIT.md). Reviews and social integration are later owner-directed work. Seven languages stay supported; countries, strongest trips and commercial terms still need actual business evidence.

## Decisions that come first

1. Approve the reviewed code release and the separate Cloudflare HTTPS correction. A GitHub push may trigger production automatically; treat it as deployment, not just backup.
2. Name the actual operator and choose three trips you can reliably deliver and sell profitably. Candidate focus: 3-day Sahara, 4-day Marrakech–Fes and 5-day slower Sahara. These are recommendations based on existing content and search-result competition, not confirmed best sellers.
3. Supply real accommodation/transport standards, a quote basis and booking/cancellation terms for those trips. A credible “luxury” promise needs specifics. Reviews are not a prerequisite for writing these facts.
4. Agree a simple lead ledger and analytics account/configuration. No analytics destination or customer database was created without those details.

## Scored backlog

Scores: **B** business impact, **S** SEO/UX impact, **C** confidence in the finding, **E** effort, **R** implementation risk, each 1–5 (5 highest). Confidence in a defect is not confidence in a traffic forecast. Priorities use judgment, not a misleading numerical revenue model. Status “local” means implemented but not released.

| ID / priority | Observed issue and evidence | B/S/C/E/R | Action / current status | Dependency and trade-off | Verification and outcome measurement |
|---|---|---|---|---|---|
| 01 P0 | HTTP root 200 and Google-selected HTTP canonical; HTTPS stored 403 | 5/5/5/1/2 | Enable Always Use HTTPS; pending approval | Correct zone; preserve path/query; do not introduce a redirect loop | HTTP→HTTPS 301 then 200; inspect Google-selected canonical after recrawl, not immediately |
| 02 P1 | Sitemap report Couldn't fetch; live trip fetch succeeds | 5/5/5/2/1 | Check sitemap processing after access/HTTPS correction; pending | Google's reporting/crawl schedule; do not repeatedly resubmit unchanged files | Successful last-read, discovered URLs, representative indexed pages; investigate fresh failures with timestamped logs |
| 03 P1 | Trip mobile LCP 21.8s; oversized logos/duplicate photography loads | 4/5/5/2/2 | Small logos, initial responsive images; local | Keep visual quality/design; some hidden-homepage work remains | Local bytes 4,015→1,382KiB; final local LCP 3.2s, earlier after-runs 6.9s; retest production and collect field data |
| 04 P1 | Trip article only noscript; initial home language depends on JS | 4/5/5/3/3 | Visible fallback, localized HTML, language fix; local | Preserve dialog/history and all seven languages; fallback briefly appears before enhancement | 217 raw pages one H1; actual trip content without JS; final interaction/mobile regression required |
| 05 P1 | Production boot fetches nonexistent CMS API | 3/4/5/1/1 | Explicit static-export mode; local | Local CMS remains API-backed | Static page requests JSON directly; production network has no startup API404 |
| 06 P1 | Business identity and luxury standards not supplied; competitors specify them | 5/4/4/3/2 | Publish real operator/offer facts on priority pages; pending owner | Facts, operating model, supplier agreements; no fabricated licence/price | Customer can identify operator and understand quote; fewer clarification loops; qualified enquiry/quote acceptance rates |
| 07 P1 | No measured lead→quote→booking funnel | 5/3/5/2/2 | Select analytics and implement minimal events; keep manual lead ledger | Account, privacy decisions, consistent sales logging; clicks alone overstate leads | Reconcile WhatsApp enquiries received with quotes/bookings; exclude internal/test traffic |
| 08 P1 | FAQ promises a request reference, but flow only prepares WhatsApp | 4/3/5/1/1 | Honest wording and optional email; local | No change to actual booking/terms; email may still be supplied voluntarily | Submit-handler assertions pass; user must press Send; no fake successful booking |
| 09 P1 | Public source metadata/files contradict requested photo presentation | 3/2/5/2/1 | Public media allowlist, neutral captions and export cleanup; local | Owner declared ownership; retain editorial originals outside dist | Public output has no source/credit/license/vendor-reference payloads; all image paths resolve |
| 10 P2 | Catalogue previously only titles/durations; guides shallow | 4/4/4/3/2 | Grouped catalogue + summaries local; improve 3/4/5-day guide next | Owner itinerary expertise; avoid repetitive or generic pages | Guide→relevant itinerary navigation; impressions by intent; qualified leads referencing guide |
| 11 P2 | Seven languages but native commercial review unconfirmed | 4/4/4/4/2 | Review priority trip/booking copy in all seven | Native reviewers and real service-language capability; don't infer spoken guide languages from UI | Review checklist per locale; enquiries and quote acceptance by language |
| 12 P2 | Low contrast and trip heading/name defects in Lighthouse | 3/3/5/2/2 | Targeted CSS/heading/gallery fixes local | Retain visual hierarchy; automated score is partial evidence | Final local trip accessibility100; manual keyboard/zoom/readout still required |
| 13 P2 | No reliable backlink/brand baseline; no partner attribution | 4/3/3/3/2 | Relevant riad/travel-planner partnerships and useful first-hand route material | Real relationships; owner approves outreach; no messages sent by this audit | Referred qualified leads/bookings and earned relevant mentions; GSC Links when populated |
| 14 P2 | Root/www static responses not fully normalized | 2/3/5/2/2 | Zone-level www→root redirect covering assets if approved | Coordinate with existing Worker redirect; avoid chains | Test root/trip/sitemap/asset on both hosts, preserve queries |
| 15 P2 | Domain mail unavailable in visible configuration | 3/1/4/2/2 | Choose provider, add verified mail DNS and publish actual address | Owner/provider/required DNS approval; do not invent inbox | Send/receive test by owner, SPF/DKIM/DMARC as provider requires |
| 16 P3 | Some legacy local inbox/UI code unused in public flow | 1/1/5/2/2 | Separate/retire later after regression coverage | Preserve local admin feature requirements | No fake reference promise visible; no production dependency on local DB |
| 17 P3 | Need public-page rich-result validation after release | 1/2/5/1/1 | Run Rich Results Test; correct truthful issues only | Live approved release; incomplete LocalBusiness address is not fixed by fabrication | Breadcrumb syntax/visible content agree; no expectation of rich-result display |
| 18 P3 | Higher-cost advertising not yet attributable | 3/2/3/3/3 | Small search experiment only after offer/funnel works | Explicit spend/market approval, genuine margin and lead handling | Cost per received qualified enquiry and confirmed booking against contribution margin |

No paid backlinks, mass directory submissions, fake reviews, traffic purchases or generic city-page generation. No security deactivation to entice crawlers. Do not spend money on a framework migration or “perfect SEO score” while offer clarity and attribution remain unresolved.

## First 24 hours

| Priority / task | Owner and effort estimate | Dependency | Success / verification |
|---|---|---|---|
| P0 HTTPS correction | Site engineer, 15–30min | Owner production approval | HTTP root/trip/maps redirect to HTTPS and final responses succeed |
| P1 Release reviewed local changes | Engineer, 1–2h including final interaction checks | Approve auto-deploy push; full local mobile/keyboard retest when browser access works | All checks in IMPLEMENTATION_LOG pass; correct GitHub build deployed; real-domain smoke test |
| P1 Capture release baseline | Engineer, 30min | Deployment | Commit/build ID, exact timestamp, Lighthouse production home+trip, canonical/robots/sitemap snapshots |
| P1 Fill commercial facts | Owner, 60–90min | Actual business records | Operator name/contact, three priority trips, accommodation standard, quote components, response capacity and booking terms ready for writing |

Do not rebuild XML merely because GSC has not refreshed. Check stored versus live results separately. Leave previously submitted URLs alone unless a material fix warrants an authorized inspection/request.

## First 7 days

| Priority / task | Owner and effort estimate | Dependency | Success / verification |
|---|---|---|---|
| P1 Recheck GSC sitemap and canonicals | Engineer, 30–60min on a few chosen checks | Access and HTTPS fixed | Fresh successful crawl records; sitemap last-read/discovery populated or a specific current failure to investigate |
| P1 Finish three commercial pages | Owner/editor, 4–8h plus locale review | Confirmed offer facts | Clear route/drive time/accommodation/price basis/terms/pickup/CTA; no invented claims |
| P1 Minimal measurement + sales ledger | Engineer/owner, 3–5h | Analytics choice and privacy configuration | Test events appear once; leads received can be reconciled to quote and booking stages |
| P1 Remaining mobile critical path | Frontend engineer, 2–4h | Stable release baseline | Remove hidden-homepage image work where practical; repeat same lab setup and observe real traffic as data arrives |
| P2 Check translation priorities | Native reviewers, 1–2h per language for the priority excerpts | Owner terms finalized | Each of seven languages has reviewed CTA/terms/inclusions; no promise of unsupported guide languages |

## First 30 days

| Priority / task | Owner and effort estimate | Dependency | Success / verification |
|---|---|---|---|
| P2 Upgrade existing planning guide | Owner/editor, 4–6h + translation | First-hand route knowledge | Useful 3/4/5-day comparison including real drive burden and trade-offs; links to existing trips |
| P2 Original photo-led trip material | Owner, 2h/week | Owner-owned photos and actual trip facts | A small set of useful route/camp/vehicle examples with descriptive captions; no external credits; no fabricated venue guarantee |
| P2 Relevant partner pilot | Owner, 2–3h/week | Real riad/concierge/travel-planner contacts; approved outreach | A small initial shortlist (e.g. five relevant contacts), attributable referrals and feedback, not arbitrary backlink totals |
| P2 Monthly demand review | Owner/analyst, 1–2h | GSC/lead data populated | Compare non-brand queries, pages and languages; distinguish near-position gains from irrelevant impressions |
| P2 Evaluate local profile eligibility | Owner, 30–60min | Confirm actual in-person customer contact/operating location | Create only if eligible and correctly represented; no virtual-office or invented-address claim |

Google Business Profile representation must match actual operations. A service-area business may qualify under the rules; a purely online operation does not qualify merely by owning a domain. [Official eligibility and representation guidance](https://support.google.com/business/answer/3038177?hl=en).

Reviews and social integration remain later work per the owner's direction. Do not hold the release hostage to them, and do not manufacture substitutes. Partner outreach is a recommended owner action, not authorization for the agent to contact people.

## First 90 days

| Priority / task | Owner and effort estimate | Dependency | Success / verification |
|---|---|---|---|
| P2 Follow the evidenced demand | Owner/editor, 3–5h/week | GSC query/lead trends | Improve the pages bringing suitable travellers; pause content that attracts no relevant intent |
| P2 One conversion experiment at a time | Engineer/owner, 2–4h per experiment | Sufficient visits and actual lead records | Compare clearer quote CTA/price guidance, maintaining offer and attribution; report uncertainty with small samples |
| P2 Strengthen operational proof | Owner, ongoing | Actual completed trips, permissions and future integration decision | Real business introduction, trip photos, precise standards; later genuine reviews/social links when ready |
| P3 Consider a capped search campaign | Owner/marketer, 4–6h setup | Stable funnel, approved budget, known margins | Qualified enquiry and booking acquisition cost, not cheap clicks; stop if lead quality/economics fail |
| P2 Commercial decision review | Owner, 2h monthly | Complete lead→quote→booking ledger | Evidence of repeatable profitable bookings from search/referrals; allocation by actual language/route performance |

Efforts are planning estimates, not promised delivery dates or Google indexing timelines. Local-code work already performed is recorded separately.

## Measurement specification

Use an analytics service only after choosing a real account and appropriate privacy configuration. Suggested event contract: `view_trip`, `open_enquiry`, `open_whatsapp`, with `trip_id`, `language`, entry page and consent-appropriate source. Avoid names, email, dates, messages or WhatsApp text in event payloads/URLs. Track neither background carousel changes nor polling as engagement. Count one intentional action per event.

Maintain an access-controlled lead ledger: internal lead ID, enquiry received date, language, trip, source if known, qualified yes/no and reason, quote sent date, quoted amount/currency, booked yes/no, margin once known. Keep personal contact information in the appropriate business system, not public reports or analytics.

Definitions: received enquiry = a real incoming WhatsApp conversation; qualified = service/date/budget match using the owner's criteria; booking = confirmed under actual terms. Quote acceptance = confirmed bookings / quotes sent. Website handoff rate = WhatsApp opens / relevant visits, explicitly **not** lead conversion. Attribution is partial if visitors change devices or open the standalone WhatsApp button; log unknown rather than guessing.

Once available, export GSC queries/pages/countries/devices for 7/28 days and compare with prior periods; use 3/6/12 months only when real history exists. Segment brand/non-brand and language. Average position is aggregated and context-dependent. Examine the same query-page pairs to identify cannibalization; similar itinerary topics alone do not prove it. Do not call something an SEO quick win until impressions and intent support that label.

## Post-release verification and approval checklist

* **Approve separately:** production auto-deploy push and Always Use HTTPS. Optional www redirect/mail DNS/analytics configuration need their concrete setup reviewed when ready.
* Verify the production deployment commit matches the approved diff and `dist` is the assets directory. Do not deploy the repository root or the separate Sites remote.
* HTTP root and trip → HTTPS, no loops; www behavior checked; all canonical targets 200; unknown route still 404; private admin/API remain excluded.
* Verify all seven home/trip canonicals and alternates, sitemap XML counts (217 total, 31 per language), robots access, assets and MIME types.
* Inspect home, the three chosen trips, one non-English trip and one guide in GSC. Compare live fetch/rendered content with stored record and selected canonical. A live pass is eligibility, not indexing.
* Use Rich Results Test for syntax/eligibility after deployment; do not add ratings, offers or credentials to eliminate warnings without real facts.
* Check sitemap last-read and discovered pages once reporting updates. If fresh failures persist, match timestamp/path with security events and verify crawler identity; no blanket UA allow.
* Repeat production mobile Lighthouse under comparable conditions, then inspect CWV field data only when sufficient real usage exists. A lab score is not a field pass.
* Confirm enquiry flow on phone/desktop, optional email validation, language switching, closing/back history, keyboard focus, saved/compare/gallery/map behavior. Prepare only a clearly labelled test message; never infer that it was sent.

**Decision rule:** keep investing when relevant non-brand discovery leads to received qualified enquiries, quotes and confirmed profitable bookings. If impressions rise but no relevant enquiries arrive, reassess intent/offer. If enquiries arrive but quotes do not close, investigate service/price/trust and sales response before publishing more content.
