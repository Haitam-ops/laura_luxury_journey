# Domain SEO release

The canonical domain is `https://lauraluxuryjourneys.com` in `data/seo.json`.
Published content remains in `dist/data/content.<language>.json`.

`python scripts/build_seo.py` generates 217 sitemap entries: seven homepages,
182 trip pages, seven complete catalogues and 21 travel-note pages. Trips use
`/<language>/journeys/<trip-id>/`; guides use
`/<language>/travel-notes/<time|stays|seasons>/`. The generator uses existing
trip data and the translated travel-note copy in `app.js`; it creates no
prices, reviews, author biographies or accommodation promises.

The Worker in `worker.js` serves language-specific initial homepage metadata,
redirects legacy query-string trip URLs to the corresponding new paths and
redirects the old workers.dev hostname to the canonical domain. Static pages
contain their own title, description, canonical, language alternatives,
social preview and structured data before JavaScript runs. The interactive
trip experience and WhatsApp enquiry flow remain available. Trip fallback
content is readable without JavaScript.

After changes, synchronize edited browser scripts and styles with `dist/`,
then run:

```powershell
python scripts/build_seo.py
python scripts/check_seo.py
python scripts/check_trip_editorial.py
```

The existing Cloudflare Git integration must deploy `main` from the repository
root using `wrangler.jsonc` and its `dist` assets directory. A GitHub push is
not proof that deployment succeeded; check the Cloudflare build and the live
canonical URL. No new GitHub workflow or credential is required by this code.

Search discovery:

- The domain property is verified in Google Search Console through DNS.
- The sitemap index at `https://lauraluxuryjourneys.com/sitemap-index.xml`
  exposes seven small language sitemaps containing the same 217 URLs. The
  original full hreflang sitemap remains available. This provides a fresh
  submission URL after the original reported a fetch failure; Google must
  still confirm successful processing.
- Cloudflare allows shared search crawlers. Dedicated AI training crawlers
  are blocked individually rather than blocking the entire training category,
  which also classified Googlebot and BingBot.

Still requires the business owner's accounts or verified details:

- Confirm sitemap processing and indexing in Google Search Console. A live
  URL test passing is not proof that a page is indexed or a sitemap processed.
- Connect an actual analytics property before claiming measured conversions.
  Count a WhatsApp click as an open, not an enquiry received. Record received
  enquiries, quotes and confirmed bookings separately.
- Supply real team information, a working domain email, actual social links
  and genuine customer reviews. No placeholder business claims are published.
