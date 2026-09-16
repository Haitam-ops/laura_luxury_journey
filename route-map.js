'use strict';
(()=>{
 const P={
  marrakech:['Marrakech',31.6295,-7.9811],dades:['Dades Valley',31.4500,-5.9700],todra:['Todra Gorge',31.5889,-5.5875],merzouga:['Merzouga',31.0802,-4.0133],erg:['Erg Chebbi',31.1450,-3.9670],
  casablanca:['Casablanca',33.5731,-7.5898],rabat:['Rabat',34.0209,-6.8416],meknes:['Meknes',33.8935,-5.5473],fes:['Fes',34.0181,-5.0078],erfoud:['Erfoud',31.4360,-4.2320],
  ouarzazate:['Ouarzazate',30.9335,-6.9370],ait:['Aït Ben Haddou',31.0470,-7.1290],skoura:['Skoura',31.0620,-6.5550],taroudant:['Taroudant',30.4700,-8.8770],essaouira:['Essaouira',31.5085,-9.7595],
  tangier:['Tangier',35.7595,-5.8340],chefchaouen:['Chefchaouen',35.1688,-5.2636],ouzoud:['Ouzoud Falls',32.0150,-6.7190],setti:['Setti Fatma',31.2250,-7.6750],imlil:['Imlil',31.1360,-7.9190],
  volubilis:['Volubilis',34.0733,-5.5558],moulay:['Moulay Idriss',34.0540,-5.5270],agafay:['Agafay',31.4570,-8.1860],balloon:['Marrakech palm grove',31.7170,-7.9740],brahim:['Moulay Brahim',31.2870,-8.0120],diabat:['Diabat coast',31.4780,-9.7700]
 };
 const ROUTES={
  'sahara-marrakech-3-days':['marrakech','dades','todra','merzouga','marrakech'],
  'imperial-cities-sahara-9-days':['casablanca','rabat','meknes','fes','erfoud','erg','dades','ait','marrakech'],
  'slow-sahara-5-days':['marrakech','dades','merzouga','ouarzazate','marrakech'],
  'marrakech-fes-sahara-4-days':['marrakech','dades','merzouga','fes'],
  'southern-morocco-7-days':['marrakech','ait','skoura','dades','merzouga','ouarzazate','marrakech'],
  'coast-desert-8-days':['marrakech','dades','merzouga','ouarzazate','taroudant','essaouira','marrakech'],
  'north-sahara-10-days':['tangier','chefchaouen','fes','merzouga','dades','ait','marrakech'],
  'grand-morocco-14-days':['casablanca','rabat','chefchaouen','fes','merzouga','dades','ait','marrakech','essaouira','marrakech'],
  'ouzoud-waterfalls':['marrakech','ouzoud'], 'ourika-valley':['marrakech','setti'], 'essaouira-day':['marrakech','essaouira'], 'ait-ben-haddou-day':['marrakech','ait'],
  'agafay-evening':['marrakech','agafay'], 'imlil-atlas-day':['marrakech','imlil'], 'chefchaouen-from-fes':['fes','chefchaouen','fes'], 'volubilis-meknes':['fes','volubilis','moulay','meknes','fes'],
  'marrakech-balloon':['marrakech','balloon'], 'agafay-quad':['marrakech','agafay'], 'merzouga-camel':['merzouga','erg'], 'merzouga-sandboarding':['merzouga','erg'],
  'agafay-buggy':['marrakech','agafay'], 'atlas-paragliding':['marrakech','brahim'], 'marrakech-hammam':['marrakech'], 'marrakech-cooking':['marrakech'],
  'marrakech-dinner-show':['marrakech'], 'essaouira-horse-riding':['essaouira','diabat']
 };
 let leafletPromise;
 function loadLeaflet(){
  if(window.L)return Promise.resolve(window.L);if(leafletPromise)return leafletPromise;
  leafletPromise=new Promise((resolve,reject)=>{
   if(!document.querySelector('link[data-leaflet]')){const css=document.createElement('link');css.rel='stylesheet';css.href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';css.dataset.leaflet='';document.head.append(css)}
   const script=document.createElement('script');script.src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';script.integrity='sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';script.crossOrigin='';script.onload=()=>resolve(window.L);script.onerror=()=>reject(Error('Map library unavailable'));document.head.append(script);
  });return leafletPromise;
 }
 function markup(trip,points){
  const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  return `<section class="route-map-card" aria-labelledby="route-map-title-${escape(trip.id)}"><div class="route-map-top"><div><p class="eyebrow rust">${escape(tr('SEE THE JOURNEY'))}</p><h4 id="route-map-title-${escape(trip.id)}">${escape(tr('Your route across Morocco'))}</h4></div><div><button type="button" data-map-fit>${escape(tr('Fit route'))}</button><a href="https://www.openstreetmap.org/?mlat=${points[0][1]}&mlon=${points[0][2]}#map=7/${points[0][1]}/${points[0][2]}" target="_blank" rel="noopener noreferrer">${escape(tr('Open map'))} ↗</a></div></div><div class="route-map-canvas" data-route-map-canvas role="region" aria-label="${escape(tr('Interactive map of the trip route'))}"><span class="route-map-loader">${escape(tr('Loading map…'))}</span></div><ol class="route-map-stops">${points.map((p,i)=>`<li><span>${i+1}</span>${escape(p[0])}</li>`).join('')}</ol><p class="route-map-note">${escape(tr('Indicative route. Exact roads, stops and pickup points are confirmed for your dates.'))}</p></section>`;
 }
 window.mountRouteMap=async trip=>{
  const panel=document.querySelector('[data-detail-panel="itinerary"]');if(!panel||panel.querySelector('.route-map-card'))return;
  const points=(ROUTES[trip.id]||[]).map(key=>P[key]).filter(Boolean);if(!points.length)return;
  const host=document.createElement('div');host.innerHTML=markup(trip,points);const card=host.firstElementChild;panel.querySelector('.itinerary').before(card);
  try{
   const L=await loadLeaflet();if(!card.isConnected)return;const canvas=card.querySelector('[data-route-map-canvas]');canvas.textContent='';
   const map=L.map(canvas,{zoomControl:false,scrollWheelZoom:false,keyboard:true});L.control.zoom({position:'topright'}).addTo(map);
   L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
   const latlngs=points.map(p=>[p[1],p[2]]);L.polyline(latlngs,{color:'#b44e32',weight:4,opacity:.88,dashArray:'9 9',lineCap:'round'}).addTo(map);
   points.forEach((p,i)=>L.marker([p[1],p[2]],{icon:L.divIcon({className:'route-map-marker-wrap',html:`<span class="route-map-marker">${i+1}</span>`,iconSize:[30,30],iconAnchor:[15,15]})}).addTo(map).bindPopup(`<strong>${i+1}. ${p[0]}</strong>`));
   const fit=()=>points.length===1?map.setView(latlngs[0],11):map.fitBounds(latlngs,{padding:[28,28],maxZoom:9});fit();card.querySelector('[data-map-fit]').addEventListener('click',fit);setTimeout(()=>{map.invalidateSize();fit()},120);if(window.ResizeObserver){let resizeTimer;const observer=new ResizeObserver(()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(card.isConnected){map.invalidateSize();fit()}},80)});observer.observe(canvas);card._routeMapObserver=observer}card._routeMap=map;
  }catch{card.classList.add('map-unavailable');card.querySelector('[data-route-map-canvas]').innerHTML=`<p>${tr('The interactive map could not load. Your complete itinerary remains below.')}</p>`}
 };
})();
