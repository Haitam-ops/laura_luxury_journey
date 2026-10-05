# Trip copy and search metadata

The API and static build both apply `data/reviewed-trip-copy.json` through
`cms.public_content`. Entries map exact English source strings to reviewed copy.
Changing a source string requires reviewing its translations again. Existing
CMS translations remain the fallback for text without a reviewed entry.

- `data/trip-search-titles.json` contains a title for every published trip in
  all seven languages. The public page title adds the business name.
- Search descriptions use the localized trip introduction, never the homepage
  collection description when a trip is open.
- `data/itinerary-place-names.json` defines the original place names. Localized
  names are recognized only to restore the original spelling. Place names are
  displayed in bold, without quotation marks, and excluded from DOM translation.
  Route descriptions may be translated; their place names must remain original.
- `trip_editorial.py` builds visible FAQs from the same duration, overnight,
  inclusion, exclusion and practical fields used elsewhere on the trip page.
  Update those fields to change an answer; do not duplicate service promises.

The French trip introductions, overviews, suitability, practical information,
itinerary narrative and inclusion wording have received an editorial rewrite.
Other languages have reviewed search titles, introductions, FAQ labels, route
labels and targeted wording repairs. This does not certify every remaining
legacy translation in those languages as editorially reviewed.

After changing content, run:

```powershell
python scripts/build_static_content.py
python scripts/check_trip_editorial.py
python scripts/check_seo.py
```

Publish the generated `dist` files as well as the source changes. Keep source
and static application code separate: their enquiry submission flows differ.
Search Console inspection remains an external check; passing local checks does
not establish Google indexing. The future domain and verification settings
remain in `data/seo.json`.
