// Canonical redirects preserve legacy trip links and campaign parameters.
import config from './data/seo.json';
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = new URL(config.customDomain || config.fallbackOrigin);
    if (url.hostname.endsWith('.workers.dev') || url.hostname === 'www.' + origin.hostname) {
      return Response.redirect(origin.origin + url.pathname + url.search, 301);
    }
    if (url.pathname === '/' || url.pathname === '/index.html') {
      const id = url.searchParams.get('trip');
      if (id) {
        if (!/^[a-z0-9-]+$/.test(id)) return new Response('Journey not found', {status: 404});
        const requested = (url.searchParams.get('lang') || 'en').toLowerCase();
        const code = ['en','fr','es','de','it','pt','nl'].includes(requested) ? requested : 'en';
        url.pathname = `/${code}/journeys/${id}/`;
        url.searchParams.delete('lang');
        url.searchParams.delete('trip');
        return Response.redirect(url.href, 301);
      }
      const code = (url.searchParams.get('lang') || 'en').toLowerCase();
      if (['en','fr','es','de','it','pt','nl'].includes(code)) {
        const assetURL = new URL(url);
        assetURL.pathname = `/${code}/`;
        return env.ASSETS.fetch(new Request(assetURL, request));
      }
    }
    if (url.pathname.startsWith('/api/') || url.pathname === '/admin' || url.pathname.startsWith('/admin/')) {
      return new Response('Not found', {status: 404, headers: {'X-Robots-Tag': 'noindex'}});
    }
    return env.ASSETS.fetch(request);
  }
};
