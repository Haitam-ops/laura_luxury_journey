'use strict';
window.siteTripID = url => url.pathname.match(/^\/(?:en|fr|es|de|it|pt|nl)\/journeys\/([a-z0-9-]+)\/?$/)?.[1] || url.searchParams.get('trip');
// Metadata follows the active journey, including browser Back and dialog closure.
window.updateSiteSEO = function(trip = null) {
  const config = window.SITE_SEO, cms = window.CMS;
  if (!config || !cms) return;
  const origin = config.origin.replace(/\/$/, '');
  const pageURL = window.sitePageURL = (code, id) => {
    if (id) return new URL(`/${code}/journeys/${encodeURIComponent(id)}/`, origin).href;
    const u = new URL('/', origin);
    u.searchParams.set('lang', code);
    return u.href;
  };
  const code = cms.language.code, site = cms.site;
  const canonical = pageURL(code, trip?.id);
  const title = trip ? `${trip.seoTitle || trip.title} | ${site.brand}` : `${site.brand} | ${config.homeTitles?.[code] || window.tr('Morocco Tours, Day Trips & Experiences')}`;
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
  if (site.phone || config.businessContact?.telephone) business.telephone = site.phone || config.businessContact.telephone;
  if (site.address || config.businessContact?.address) business.address = site.address || config.businessContact.address;
  const socials = ['instagram','facebook','tiktok','youtube'].map(k => site[k]).filter(v => /^https:\/\//.test(v || ''));
  if (socials.length) business.sameAs = socials;
  const graph = [business, {'@type':'WebSite','@id':origin+'/#website',url:pageURL('en'),name:site.brand,publisher:{'@id':business['@id']}}, {'@type':'WebPage','@id':canonical+'#page',url:canonical,name:title,description,inLanguage:code,isPartOf:{'@id':origin+'/#website'},about:{'@id':business['@id']}}];
  if (trip) graph.push({'@type':'BreadcrumbList',itemListElement:[
    {'@type':'ListItem',position:1,name:site.brand,item:pageURL(code)},
    {'@type':'ListItem',position:2,name:window.tr('Explore all'),item:`${origin}/${code}/journeys/`},
    {'@type':'ListItem',position:3,name:trip.title,item:canonical}
  ]});
  let schema = document.getElementById('site-structured-data');
  if (!schema) { schema = document.createElement('script'); schema.id = 'site-structured-data'; schema.type = 'application/ld+json'; document.head.append(schema); }
  schema.textContent = JSON.stringify({'@context':'https://schema.org','@graph':graph});
};
