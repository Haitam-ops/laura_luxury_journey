'use strict';
// Metadata follows the active journey, including browser Back and dialog closure.
window.updateSiteSEO = function(trip = null) {
  const config = window.SITE_SEO, cms = window.CMS;
  if (!config || !cms) return;
  const origin = config.origin.replace(/\/$/, '');
  const pageURL = (code, id) => {
    const u = new URL('/', origin);
    u.searchParams.set('lang', code);
    if (id) u.searchParams.set('trip', id);
    return u.href;
  };
  const code = cms.language.code, site = cms.site;
  const canonical = pageURL(code, trip?.id);
  const title = trip ? `${trip.seoTitle || trip.title} | ${site.brand}` : `${site.brand} — ${site.hero_title} ${site.hero_emphasis}`;
  const description = trip?.seoDescription || trip?.summary || site.collection_copy;
  const meta = (key, value, property = false) => {
    const attr = property ? 'property' : 'name';
    let el = document.head.querySelector(`meta[${attr}="${key}"]`);
    if (!el) { el = document.createElement('meta'); el.setAttribute(attr, key); document.head.append(el); }
    el.content = value;
  };
  document.title = title;
  meta('description', description);
  let link = document.head.querySelector('link[rel="canonical"]');
  if (!link) { link = document.createElement('link'); link.rel = 'canonical'; document.head.append(link); }
  link.href = canonical;
  document.head.querySelectorAll('link[rel="alternate"][hreflang]').forEach(el => el.remove());
  const available = cms.languages.filter(l => l.enabled && (!trip || config.availableTrips[l.code]?.includes(trip.id)));
  for (const lang of [...available.map(l => l.code), ...(available.some(l => l.code === 'en') ? ['x-default'] : [])]) {
    const el = document.createElement('link'); el.rel = 'alternate'; el.hreflang = lang;
    el.href = pageURL(lang === 'x-default' ? 'en' : lang, trip?.id); document.head.append(el);
  }
  const photo = trip?.photos?.[0]?.path || cms.media[site.hero_images[0]]?.path || config.logo;
  for (const [key, value] of Object.entries({'og:type':'website','og:site_name':site.brand,'og:title':title,'og:description':description,'og:url':canonical,'og:image':new URL(photo, origin).href})) meta(key, value, true);
  meta('twitter:card', 'summary_large_image');
  meta('twitter:title', title);
  meta('twitter:description', description);
  meta('twitter:image', new URL(photo, origin).href);
  const photoAlt = trip?.photos?.[0]?.alt || cms.media[site.hero_images[0]]?.alt || site.brand;
  meta('og:image:alt', photoAlt, true);
  meta('twitter:image:alt', photoAlt);
  if (config.googleSiteVerification) meta('google-site-verification', config.googleSiteVerification);
  const business = {'@type':'TravelAgency','@id':origin+'/#business',name:site.brand,url:pageURL('en'),logo:new URL(config.logo, origin).href};
  if (site.email) business.email = site.email;
  if (site.phone) business.telephone = site.phone;
  if (site.address) business.address = site.address;
  const socials = ['instagram','facebook','tiktok','youtube'].map(k => site[k]).filter(v => /^https:\/\//.test(v || ''));
  if (socials.length) business.sameAs = socials;
  const graph = [business, {'@type':'WebSite','@id':origin+'/#website',url:pageURL('en'),name:site.brand,publisher:{'@id':business['@id']}}, {'@type':'WebPage','@id':canonical+'#page',url:canonical,name:title,description,inLanguage:code,isPartOf:{'@id':origin+'/#website'},about:{'@id':business['@id']}}];
  let schema = document.getElementById('site-structured-data');
  if (!schema) { schema = document.createElement('script'); schema.id = 'site-structured-data'; schema.type = 'application/ld+json'; document.head.append(schema); }
  schema.textContent = JSON.stringify({'@context':'https://schema.org','@graph':graph});
};
