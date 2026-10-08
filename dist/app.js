'use strict';
const ICONS={arrow:'M4 12h15m-6-6 6 6-6 6',heart:'M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z',pin:'M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z M15 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0',clock:'M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0 M12 6v6l4 2',search:'M20 20l-5-5 M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0',close:'m6 6 12 12M6 18 18 6',menu:'M3 6h18M3 12h18M3 18h18',route:'M5 3v4m0 4v4m0 4v2M19 3v2m0 4v4m0 4v4M5 3c0 6 14 12 14 18',sun:'M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1 M17 12a5 5 0 1 1-10 0 5 5 0 0 1 10 0',sparkles:'m12 2 3 7 7 3-7 3-3 7-3-7-7-3 7-3Z',sliders:'M4 7h16M4 17h16M8 4v6M16 14v6','check-circle':'M22 11v1a10 10 0 1 1-6-9 M22 4 12 14l-3-3',info:'M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0 M12 11v6M12 7h.01',compass:'M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0 M16 8l-3 5-5 3 3-5Z',plus:'M12 5v14M5 12h14',compare:'M8 3v18M16 3v18M4 7h8M12 17h8',lock:'M5 10h14v11H5Z M8 10V6a4 4 0 0 1 8 0v4',download:'M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5',check:'m5 12 4 4L19 6',share:'M8 12h12m-5-5 5 5-5 5M10 4H4v16h6',bed:'M3 18V6M21 18V9H3M3 15h18M7 9V6h5v3',users:'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0M22 21v-2a4 4 0 0 0-3-4M17 3a4 4 0 0 1 0 8'};
const icon=name=>`<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONS[name]||ICONS.compass}"/></svg>`;
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function hydrate(root=document){root.querySelectorAll('[data-icon]').forEach(e=>{e.innerHTML=icon(e.dataset.icon)});}
const readStore=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key))??fallback}catch{return fallback}};
const writeStore=(key,data)=>{try{localStorage.setItem(key,JSON.stringify(data));return true}catch{return false}};
const validIds=new Set(TRIPS.map(t=>t.id));
const pageSize=()=>innerWidth<=620?3:6;
let saved=new Set((Array.isArray(readStore('desertgate.saved',[]))?readStore('desertgate.saved',[]):[]).filter(id=>validIds.has(id)));
let compared=[],category='journeys',onlySaved=false,limit=pageSize(),search='',sort='shortest',planTrip=null,lastRequest=null,submitBusy=false,toastTimer;
const descriptions={journeys:'Discover the places you could wake up tomorrow.',daytrips:'A change of scene, with your own driver for the day.',experiences:'A few hours can become a favorite part of your stay.',all:'From a morning out to a journey across the country.'};
function toast(message){$('#toast').textContent=message;$('#toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').hidden=true,3200)}
function updateSaved(){ $('#saved-count').textContent=saved.size;$('#saved-toggle').setAttribute('aria-pressed',String(onlySaved));$('#saved-toggle').setAttribute('aria-label',tr('Show {count} saved trips',{count:saved.size}));}
function toggleSaved(id){saved.has(id)?saved.delete(id):saved.add(id);writeStore('desertgate.saved',[...saved]);updateSaved();$$(`[data-save="${id}"]`).forEach(b=>{b.setAttribute('aria-pressed',String(saved.has(id)));b.setAttribute('aria-label',tr(saved.has(id)?'Unsave {trip}':'Save {trip}',{trip:TRIPS.find(t=>t.id===id).title}))});if(onlySaved)render();}
function card(t,i){return `<article class="trip-card"><div class="card-image-wrap"><a href="${esc(window.sitePageURL(CMS.language.code,t.id))}" data-trip="${t.id}" aria-label="${esc(tr('Explore {trip}',{trip:t.title}))}"><img src="${esc(t.photos?.[0]?.path||'/assets/sahara.webp')}" alt="${esc(t.photos?.[0]?.alt||t.region)}" width="800" height="530" loading="lazy"></a><span class="card-tag ${i===0&&category==='journeys'?'terracotta':''}">${t.category==='journeys'?(i===0?'Into the Sahara':'Time to explore'):t.category==='daytrips'?'A day away':'A local experience'}</span><button class="save-trip" data-save="${t.id}" aria-pressed="${saved.has(t.id)}" aria-label="${esc(tr(saved.has(t.id)?'Unsave {trip}':'Save {trip}',{trip:t.title}))}">${icon('heart')}</button><span class="card-duration">${icon('clock')}${esc(t.duration)}</span>${cardGalleryControls(t)}</div><div class="card-body"><p class="card-region">${esc(t.region)}</p><h3><a href="${esc(window.sitePageURL(CMS.language.code,t.id))}" data-trip="${t.id}">${esc(t.title)}</a></h3><p class="card-route">${icon('pin')}${esc(t.start===t.end?tr('From {start} · returns to {end}',{start:t.start,end:t.end}):t.start+' → '+t.end)}</p><p class="card-description">${esc(t.summary)}</p><div class="card-features">${t.highlights.map(s=>`<span>${esc(s)}</span>`).join('')}</div><div class="card-bottom"><div class="card-price"><strong>Planned for your dates</strong><small>Tell us what you have in mind</small></div><a class="text-link" href="${esc(window.sitePageURL(CMS.language.code,t.id))}" data-trip="${t.id}">View itinerary ${icon('arrow')}</a></div></div><div class="card-compare"><label><input type="checkbox" data-compare="${t.id}" ${compared.includes(t.id)?'checked':''}> Compare this trip</label><span>${t.category==='journeys'?'Multi-day journey':t.category==='daytrips'?'Day trip':'Local experience'}</span></div></article>`}
function filtered(){let list=TRIPS.filter(t=>(category==='all'||t.category===category)&&(!onlySaved||saved.has(t.id))&&(!search||`${esc(t.title)} ${esc(t.region)} ${esc(t.summary)} ${esc(t.start)} ${esc(t.end)} ${t.highlights.join(' ')} ${t.itinerary.map(s=>s[0]).join(' ')}`.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').includes(search.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,''))));if(sort!=='curated')list.sort((a,b)=>sort==='shortest'?a.days-b.days:b.days-a.days);return list}
function render(){$('#sort').value=sort;const list=filtered();$('#trip-grid').innerHTML=list.slice(0,limit).map(card).join('');$('#result-count').textContent=tr(onlySaved?'{count} trips saved':list.length===1?'{count} trip':'{count} trips',{count:list.length});$('#results-description').textContent=onlySaved?'The trips you keep coming back to.':descriptions[category];$('#empty-state').hidden=!!list.length;$('#show-more').hidden=list.length<=limit;$('#show-more').innerHTML=`${esc(tr('Explore {count} more',{count:list.length-limit}))} ${icon('arrow')}`;$('#active-filters').innerHTML=onlySaved?`<button class="filter-chip" id="clear-saved-filter">Saved journeys ${icon('close')}</button>`:'';$$('[data-category]').forEach(b=>{const active=b.dataset.category===category;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});updateSaved();}
function browse(next='all',term='',savedOnly=false){if(next!==category)sort=next==='journeys'?'shortest':'curated';category=next;search=term;onlySaved=savedOnly;limit=pageSize();$('#search').value=term;render();$('#journeys').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
function syncCompare(){ $('#compare-tray').hidden=compared.length===0;$('#compare-count').textContent=compared.length;$('#open-compare').disabled=compared.length<2;$$('[data-compare]').forEach(i=>i.checked=compared.includes(i.dataset.compare));document.body.classList.toggle('has-comparison',compared.length>0); }
function compare(id,input){if(compared.includes(id))compared=compared.filter(x=>x!==id);else if(compared.length===3){if(input)input.checked=false;toast('Choose up to three trips. Remove one to add another.');return}else compared.push(id);syncCompare()}
function showComparison(){const list=compared.map(id=>TRIPS.find(t=>t.id===id));if(list.length<2)return;const row=(name,fn)=>`<tr><th scope="row">${name}</th>${list.map(t=>`<td>${fn(t)}</td>`).join('')}</tr>`;$('#comparison-content').innerHTML=`<div class="comparison-scroll" tabindex="0" aria-label="Trip comparison; scroll horizontally on small screens"><table class="compare-table"><caption class="sr-only">Compare trip durations, routes, pace and suitability</caption><thead><tr><th scope="col">Your shortlist</th>${list.map(t=>`<th scope="col"><img src="${esc(t.photos?.[0]?.path||'/assets/sahara.webp')}" alt="${esc(t.region.toLowerCase())}" width="260" height="125"><h3>${esc(t.title)}</h3></th>`).join('')}</tr></thead><tbody>${row('Time',t=>esc(t.duration))}${row('Starts / ends',t=>`${esc(t.start)} → ${esc(t.end)}`)}${row('The pace',t=>esc(t.pace))}${row('A good fit for',t=>esc(t.fit))}${row('Keep in mind',t=>esc(t.practical))}${row('Next step',t=>`<button class="button button-rust" data-trip="${t.id}">Explore this trip ${icon('arrow')}</button>`)}</tbody></table></div>`;$('#compare-dialog').showModal();}
function placeText(text,t){const names=t.placeNames||[];const value=String(text);let at=0,out='';while(at<value.length){let best=null;for(const name of names){const index=value.indexOf(name,at);if(index<0)continue;const before=value[index-1]||'',after=value[index+name.length]||'';if(/[\p{L}\p{N}_]/u.test(before)||/[\p{L}\p{N}_]/u.test(after))continue;if(!best||index<best.index||(index===best.index&&name.length>best.name.length))best={index,name};}if(!best){out+=esc(value.slice(at));break;}out+=esc(value.slice(at,best.index))+`<strong class="place-name" data-no-translate>${esc(best.name)}</strong>`;at=best.index+best.name.length;}return out;}
function tripFAQ(t){if(!t.faqs?.length)return '';return `<section class="trip-faq" aria-labelledby="trip-faq-title" data-no-translate><h3 id="trip-faq-title">${esc(tr('Frequently asked questions'))}</h3>${t.faqs.map(f=>`<details><summary>${esc(f.question)}</summary>${f.answer?`<p>${placeText(f.answer,t)}</p>`:''}${f.items?.length?`<${f.ordered?'ol':'ul'}>${f.items.map(item=>`<li>${placeText(item,t)}</li>`).join('')}</${f.ordered?'ol':'ul'}>`:''}</details>`).join('')}</section>`;}
function detail(t){const itineraryTitle=t.category==='journeys'?'Your journey, day by day':'How your day unfolds',hasMore=t.itinerary.length>4;return `${galleryMarkup(t)}<div class="detail-layout"><div class="detail-main"><header class="detail-intro"><p class="eyebrow rust">${placeText(t.region,t)}</p><h2 id="detail-title">${placeText(t.title,t)}</h2><p class="detail-summary">${placeText(t.summary,t)}</p><div class="detail-facts" aria-label="Trip at a glance"><div>${icon('pin')}<span><small>Starts in</small><strong>${placeText(t.start,t)}</strong></span></div><div>${icon('route')}<span><small>Finishes in</small><strong>${placeText(t.end,t)}</strong></span></div><div>${icon('clock')}<span><small>Time to allow</small><strong>${esc(t.duration)}</strong></span></div><div>${icon('compass')}<span><small>The pace</small><strong>${esc(t.pace)}</strong></span></div></div></header><div class="detail-tabs" role="tablist" aria-label="Trip details"><button role="tab" id="detail-tab-overview" aria-controls="detail-panel-overview" aria-selected="true" data-detail-tab="overview">Overview</button><button role="tab" id="detail-tab-itinerary" aria-controls="detail-panel-itinerary" aria-selected="false" data-detail-tab="itinerary">Itinerary <span>${t.itinerary.length}</span></button><button role="tab" id="detail-tab-practical" aria-controls="detail-panel-practical" aria-selected="false" data-detail-tab="practical">Good to know</button></div><section class="detail-panel" id="detail-panel-overview" role="tabpanel" aria-labelledby="detail-tab-overview" data-detail-panel="overview">${t.story?`<div class="trip-story"><p class="eyebrow rust">A CLOSER LOOK</p>${t.story.split(/\n\s*\n/).filter(Boolean).map(p=>`<p>${placeText(p,t)}</p>`).join('')}</div>`:''}<div class="detail-audience"><div><p class="eyebrow rust">IS THIS YOUR KIND OF TRIP?</p><h3>A good match for you?</h3><p class="fit-text">${placeText(t.fit,t)}</p></div><div class="detail-warning"><strong>A few useful details</strong><p>${placeText(t.practical,t)}</p></div></div></section><section class="detail-panel" id="detail-panel-itinerary" role="tabpanel" aria-labelledby="detail-tab-itinerary" data-detail-panel="itinerary" hidden><div class="panel-heading"><div><p class="eyebrow rust">ALONG THE WAY</p><h3>${itineraryTitle}</h3></div><p>${esc(t.duration)} · ${placeText(t.start,t)} → ${placeText(t.end,t)}</p></div><ol class="itinerary${hasMore?' itinerary-collapsed':''}">${t.itinerary.map(([title,text],i)=>`<li ${i>=4?'data-itinerary-extra':''}><span class="itinerary-number">${String(i+1).padStart(2,'0')}</span><div><h4>${t.category==='journeys'?esc(tr('Day {count}',{count:i+1}))+' · ':''}${placeText(title,t)}</h4>${text.split(/\n\s*\n/).filter(Boolean).map(paragraph=>`<p>${placeText(paragraph,t)}</p>`).join('')}${t.overnights[i]?`<span class="overnight">${icon('bed')}${esc(tr('Overnight stop:'))} ${placeText(t.overnights[i],t)}</span>`:''}</div></li>`).join('')}</ol>${hasMore?`<button class="itinerary-toggle" data-itinerary-toggle aria-expanded="false"><span>${esc(tr('View full itinerary'))}</span>${icon('arrow')}</button>`:''}</section><section class="detail-panel" id="detail-panel-practical" role="tabpanel" aria-labelledby="detail-tab-practical" data-detail-panel="practical" hidden><div class="panel-heading"><div><p class="eyebrow rust">THE PRACTICAL DETAILS</p><h3>Before you go</h3></div></div><div class="practical-grid"><article><span>${icon('check-circle')}</span><div><h4>${(t.id==='agafay-evening'||t.category==='journeys')?"What's Included?":'Your trip arrangements'}</h4>${(t.id==='agafay-evening'||t.category==='journeys')?'':'<p>Your proposal will set out the details of:</p>'}<ul class="detail-list">${t.cover.map(s=>`<li>${icon('check')}${placeText(s,t)}</li>`).join('')}</ul></div></article><article><span>${icon('sparkles')}</span><div><h4>Extras & booking details</h4><p>${placeText(t.extras,t)}</p></div></article><article><span>${icon('pin')}</span><div><h4>Meeting your driver or host</h4><p>We’ll agree where and when to meet before your trip. If your riad is on a pedestrian street, we may use a nearby gate. Let us know where you’re staying and whether you need help with access or luggage.</p></div></article></div><p class="detail-bottom-note">We’ll confirm availability, timings and inclusions for your dates. Your proposal will name any accommodation and local assistance arranged for you; photographs show the character of the destination.</p></section>${tripFAQ(t)}</div><aside class="detail-side"><p class="eyebrow rust">IMAGINE YOURSELF HERE</p><h3>Shall we make<br>a plan?</h3><p>Tell us when you’d like to go and who’s coming. We’ll talk through your plans and put together an itinerary and price for you.</p><button class="button button-rust" data-plan-trip="${t.id}">Plan this trip ${icon('arrow')}</button><p class="form-note">${icon('lock')}No payment now. No commitment to book.</p><div class="side-facts"><div>${icon('route')}A route that suits your time</div><div>${icon('users')}Arranged for you and your companions</div><div>${icon('sliders')}The details, talked through together</div></div><div class="detail-share"><button class="text-link" data-save="${t.id}" aria-pressed="${saved.has(t.id)}" aria-label="${esc(tr('Save {trip}',{trip:t.title}))}">${icon('heart')} Save</button><button class="text-link" data-share="${t.id}">${icon('share')} Share trip</button></div></aside></div><div class="detail-mobile-action"><div><strong>${esc(t.duration)}</strong><small>${placeText(t.start,t)} → ${placeText(t.end,t)}</small></div><button class="button button-rust" data-plan-trip="${t.id}">Plan this trip ${icon('arrow')}</button></div>`}
let navigating=false,activeDetailTrip=null;
function openTrip(id,push=true){const t=TRIPS.find(t=>t.id===id);if(!t)return;activeDetailTrip=t;if($('#compare-dialog').open)$('#compare-dialog').close();$('#trip-detail').innerHTML=detail(t);const itineraryToggle=$('#trip-dialog [data-itinerary-toggle]');if(itineraryToggle)itineraryToggle.querySelector('span').textContent=tr('View full itinerary');if(!$('#trip-dialog').open)$('#trip-dialog').showModal();$('#trip-dialog').scrollTop=0;document.title=`${t.title} — ${CMS.site.brand}`;if(push){const url=new URL(window.sitePageURL(CMS.language.code,id));url.host=location.host;url.protocol=location.protocol;history.pushState({trip:id},'',url)} window.updateSiteSEO?.(t); }
$('#trip-dialog').addEventListener('close',()=>{if(navigating)return;const url=new URL(window.sitePageURL(CMS.language.code));url.host=location.host;url.protocol=location.protocol;history.replaceState({},'',url);document.title=CMS.site.brand+' — '+CMS.site.hero_title+' '+CMS.site.hero_emphasis;window.updateSiteSEO?.();});
window.addEventListener('popstate',()=>{navigating=true;const id=window.siteTripID(new URL(location.href));if(id)openTrip(id,false);else if($('#trip-dialog').open)$('#trip-dialog').close();navigating=false;window.updateSiteSEO?.(TRIPS.find(t=>t.id===id)||null);});
function openPlan(id){if($('#note-dialog').open)$('#note-dialog').close();id=id||window.siteTripID(new URL(location.href));const pending=readStore('desertgate.pending',null);planTrip=TRIPS.find(t=>t.id===id)||(!id&&pending?.payload?TRIPS.find(t=>t.id===pending.payload.trip_id):null)||null;$('#duration-base').textContent=planTrip?tr('{count} days',{count:planTrip.days}):tr('Keep the suggested duration');$('#duration-field').hidden=!!planTrip&&planTrip.category!=='journeys';$('#plan-form').elements.duration_flexibility.value='same';$('#plan-context').innerHTML=planTrip?`<span>Interested journey:</span><br><strong>${esc(planTrip.title)}</strong><br>${esc(planTrip.duration)} · ${esc(planTrip.start)} → ${esc(planTrip.end)}`:`<strong>What do you have in mind?</strong><br>Tell us what brings you to Morocco. We can help you choose the places and pace that suit you.`;$('#plan-form').hidden=false;$('#request-success').hidden=true;$('#form-error').hidden=true;if(!$('#plan-dialog').open)$('#plan-dialog').showModal();}
const NOTES={
time:{"title": "How much of Morocco feels right for you?", "html": "<h3>Start with the feeling</h3><p>A quiet courtyard breakfast. Salt air in Essaouira. The last light on the dunes at Merzouga. Start with the moments you most want to experience, then give them room in your itinerary. Morocco rewards a little time to linger.</p><h3>A day away, or a few days further?</h3><p>From Marrakech, a day in the Atlas foothills or an evening in Agafay brings a welcome change of scene. Essaouira and Ouzoud mean longer drives. For the Sahara, a three-day Marrakech–Merzouga return is possible, with full road days. Four or five days can make space for a gentler pace and more time around the dunes, depending on the route.</p><h3>Let a longer journey breathe</h3><p>With a week or two, choose a few places to know well. An extra night can mean a morning without packing, time for a walk or another dinner at a place you love. Arriving in one city and leaving from another may reduce backtracking. We’ll help you balance the places on your wish list with realistic driving times and your flights.</p>"},
stays:{"title": "A stay that becomes part of the journey", "html": "<h3>Picture your morning</h3><p>In a riad, the pleasure might be breakfast beside a courtyard and stepping straight into the life of the medina. A hotel or lodge outside the centre may suit you better if you value easier access or more space. Choose for the way you like to spend your day, as well as the photographs.</p><h3>Make the desert night your own</h3><p>A night near Merzouga gives you time to watch the dunes change colour and enjoy the evening after the day’s drive. Camps differ in location, tent layout and facilities. A camel ride and a 4×4 transfer feel quite different; talk through the option that suits you, along with bathrooms, hot water, power and seasonal heating or cooling.</p><h3>Comfort is personal</h3><p>A beautiful room should work for you. Tell us about stairs, walking distances, bed preferences or family arrangements. Before you confirm, we’ll agree the named stays, meals, access and booking terms, including any proposed alternatives. You should be able to picture your evenings as clearly as your days.</p>"},
seasons:{"title": "Find the Morocco of your season", "html": "<h3>Spring and autumn: room to roam</h3><p>If your wish list brings together city streets, mountain scenery and the Sahara, spring or autumn is often a good starting point. The desert is generally more comfortable than in high summer. Pack layers: a sunny afternoon and a cool evening can belong to the same day.</p><h3>Summer: follow the coast</h3><p>Long days invite time by the Atlantic, with sea air in Essaouira and coastal stays around Taghazout. Inland cities and the desert can be very hot. Plan outings early, leave the hottest hours for rest and check cooling arrangements before choosing a desert night. Coastal wind is part of the experience, too.</p><h3>Winter: enjoy the quieter hours</h3><p>City walks and southern routes can be rewarding in winter, with warm layers for evenings and desert nights. In the High Atlas, snow can affect roads and walks, so keep mountain plans flexible and confirm heating at your stays. Tell us what you want to see and when you can travel; we’ll help you choose a route, then check conditions as departure approaches.</p>"},
privacy:{"title": "Your information, treated with care", "html": "<h3>Your enquiry</h3><p>Tell us your name, email, travel dates, preferences and anything that would help us shape your journey. The form prepares a WhatsApp message; press Send in WhatsApp to share it with Laura Luxury Journeys. We use the details you share to respond and discuss your travel plans.</p><h3>Your choices while browsing</h3><p>Saved journeys and your language preference stay in your browser. You can remove them through your browser settings. Making an enquiry does not automatically subscribe you to marketing.</p><h3>External services</h3><p>WhatsApp handles messages under its own privacy terms. Interactive maps may connect to external map services, which receive the information needed to display the map.</p><h3>Questions about your details</h3><p>Contact us through your WhatsApp conversation to ask about information you have shared or request a correction or deletion. Please keep passport numbers, card details and other sensitive information out of your initial enquiry.</p>"},
booking:{"title": "Your journey, planned around you", "html": "<h3>Start with a conversation</h3><p>The itineraries are inspiration for your own Morocco journey. Share your dates, interests and preferred pace, and we’ll discuss the arrangements that suit you. An enquiry is free of commitment and does not reserve a stay, transfer or activity.</p><h3>A proposal with the details that matter</h3><p>Before you decide, agree the route, accommodation, transport, meeting points, meals and activities, together with the total price and any optional extras. Payment schedules, cancellation terms and arrangements for changes should be clear in your proposal.</p><h3>Confirm with confidence</h3><p>Your booking is confirmed only after the agreed confirmation steps have been completed. This website takes no payment. Wait for written confirmation of your arrangements before making non-refundable onward plans; weather, road conditions and availability can affect the final schedule.</p>"}
};
function openNote(key){const n=NOTES[key];if(!n)return;const article=['time','stays','seasons'].includes(key);const title=article?placeText(tr(n.title),TRIPS[0]||{}):n.title;const body=article?n.html.replace(/<(h3|p)>(.*?)<\/\1>/g,(_,tag,text)=>`<${tag}>${placeText(tr(text),TRIPS[0]||{})}</${tag}>`):n.html;$('#note-content').innerHTML=`<div ${article?'data-no-translate':''}><h2 id="note-title">${title}</h2>${body}${article?`<button class="button button-rust" data-plan>${esc(tr('Let’s talk about your Morocco'))} ${icon('arrow')}</button>`:''}</div>`;$('#note-dialog').showModal();$('#note-dialog').scrollTop=0;}
function selectDetailTab(name,focus=false){const dialog=$('#trip-dialog');dialog.querySelectorAll('[data-detail-tab]').forEach(button=>{const active=button.dataset.detailTab===name;button.setAttribute('aria-selected',String(active));button.tabIndex=active?0:-1;if(active&&focus)button.focus()});dialog.querySelectorAll('[data-detail-panel]').forEach(panel=>panel.hidden=panel.dataset.detailPanel!==name);if(name==='itinerary'&&activeDetailTrip)mountRouteMap(activeDetailTrip)}
$('#trip-dialog').addEventListener('click',e=>{const tab=e.target.closest('[data-detail-tab]');if(tab){selectDetailTab(tab.dataset.detailTab);return}const toggle=e.target.closest('[data-itinerary-toggle]');if(toggle){const list=toggle.previousElementSibling,expanded=toggle.getAttribute('aria-expanded')==='true';toggle.setAttribute('aria-expanded',String(!expanded));list.classList.toggle('itinerary-collapsed',expanded);toggle.querySelector('span').textContent=expanded?tr('View full itinerary'):tr('Show less');}});
$('#trip-dialog').addEventListener('keydown',e=>{const tab=e.target.closest('[data-detail-tab]');if(!tab||!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const tabs=[...$('#trip-dialog').querySelectorAll('[data-detail-tab]')],index=tabs.indexOf(tab),next=e.key==='Home'?0:e.key==='End'?tabs.length-1:(index+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;selectDetailTab(tabs[next].dataset.detailTab,true)});
document.addEventListener('click',async e=>{const b=e.target.closest('button,a');if(!b)return;if(b.dataset.trip){e.preventDefault();openTrip(b.dataset.trip)}else if(b.dataset.save){e.preventDefault();toggleSaved(b.dataset.save)}else if(b.dataset.category){category=b.dataset.category;limit=pageSize();onlySaved=false;render()}else if(b.hasAttribute('data-plan')||b.dataset.planTrip){e.preventDefault();openPlan(b.dataset.planTrip)}else if(b.hasAttribute('data-close'))b.closest('dialog').close();else if(b.dataset.note)openNote(b.dataset.note);else if(b.dataset.place)browse('all',b.dataset.place);else if(b.dataset.footerCategory)browse(b.dataset.footerCategory);else if(b.dataset.share){const url=new URL(window.sitePageURL(CMS.language.code,b.dataset.share));try{await navigator.clipboard.writeText(url.href);const original=b.innerHTML;b.innerHTML=icon('check')+' Link copied';setTimeout(()=>b.innerHTML=original,2200)}catch{toast('Copy the trip address from your browser.')}}else if(b.id==='clear-saved-filter'){onlySaved=false;render()}});
document.addEventListener('change',e=>{if(e.target.dataset.compare)compare(e.target.dataset.compare,e.target)});
$('#search').addEventListener('input',e=>{search=e.target.value.trim();limit=pageSize();render()});$('#sort').addEventListener('change',e=>{sort=e.target.value;render()});$('#show-more').addEventListener('click',()=>{limit+=pageSize();render()});$('#reset-filters').addEventListener('click',()=>browse());$('#saved-toggle').addEventListener('click',()=>browse('all','',!onlySaved));$('#footer-saved').addEventListener('click',()=>browse('all','',true));$('#clear-compare').addEventListener('click',()=>{compared=[];syncCompare()});$('#open-compare').addEventListener('click',showComparison);$('#compare-deserts').addEventListener('click',()=>{compared=['agafay-evening','sahara-marrakech-3-days'].filter(id=>validIds.has(id));syncCompare();showComparison()});
$('#menu-toggle').addEventListener('click',()=>{const open=$('#mobile-nav').hidden;$('#mobile-nav').hidden=!open;$('#menu-toggle').setAttribute('aria-expanded',String(open));$('#menu-toggle').setAttribute('aria-label',tr(open?'Close navigation':'Open navigation'));$('#menu-toggle').innerHTML=icon(open?'close':'menu');});$('#mobile-nav').addEventListener('click',e=>{if(e.target.closest('a,button')){$('#mobile-nav').hidden=true;$('#menu-toggle').setAttribute('aria-expanded','false');$('#menu-toggle').setAttribute('aria-label',tr('Open navigation'));$('#menu-toggle').innerHTML=icon('menu')}});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('#mobile-nav').hidden)$('#menu-toggle').click()});
$$('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target!==d)return;const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()}));

// Native validation follows the selected site language, not the browser language.
const validationForm=document.querySelector('#plan-form');
validationForm.addEventListener('invalid',event=>{
 const input=event.target;input.setCustomValidity('');
 if(input.validity.valueMissing)input.setCustomValidity(tr('Please fill in this field.'));
 else if(input.validity.typeMismatch)input.setCustomValidity(tr('Please enter a valid email address.'));
 else if(input.validity.rangeUnderflow||input.validity.rangeOverflow)input.setCustomValidity(tr('Please enter a number between 1 and 30.'));
},true);
validationForm.addEventListener('input',event=>event.target.setCustomValidity?.(''));

const dateInput=$('#plan-form input[name=date]');const today=new Date();dateInput.min=`${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;
$('#plan-form').addEventListener('submit',e=>{
 e.preventDefault();const form=e.currentTarget;if(!form.reportValidity())return;
 const r=Object.fromEntries(new FormData(form));
 if(!r.name.trim()){form.elements.name.setCustomValidity(tr('Please enter your name.'));form.elements.name.reportValidity();return;}
 const journey=planTrip?`${planTrip.title} — ${planTrip.duration}`:tr('A personal Morocco journey');
 const flexibility=$('#duration-field').hidden?tr('Not applicable'):form.elements.duration_flexibility.selectedOptions[0].textContent;
 const message=[tr('Hello Laura Luxury Journeys, I would like to plan a trip.'),`${tr('Interested journey')}: ${journey}`,`${tr('Trip ID')}: ${planTrip?.id||'custom'}`,`${tr('Name')}: ${r.name.trim()}`,`${tr('Email')}: ${r.email.trim()}`,`${tr('Preferred start date')}: ${r.date||tr('Flexible')}`,`${tr('Travelers')}: ${r.travelers}`,`${tr('Travel arrangements')}: ${tr(r.style)}`,`${tr('Accommodation preference')}: ${r.comfort}`,`${tr('Trip duration flexibility')}: ${flexibility}`,`${tr('What would make the trip special')}: ${r.message.trim()||tr('Not specified')}`,tr('No payment now, and no commitment to book.')].join('\n');
 const link='https://wa.me/'+CMS.site.whatsapp.replace(/\D/g,'')+'?text='+encodeURIComponent(message);
 window.open(link,'_blank','noopener,noreferrer');
 const status=$('#form-error');status.hidden=false;status.replaceChildren(document.createTextNode('Your message is ready. Send it in WhatsApp to complete your enquiry. '));
 const retry=document.createElement('a');retry.href=link;retry.target='_blank';retry.rel='noopener noreferrer';retry.textContent='Open WhatsApp';status.append(retry);
});
$('#plan-form input[name=name]').addEventListener('input',e=>e.target.setCustomValidity(''));
$('#download-request').addEventListener('click',()=>{if(!lastRequest)return;const r=lastRequest;const content=`${tr('LAURA LUXURY JOURNEYS · TRIP REQUEST')}\n${tr('Reference')}: ${r.reference}\n${tr('Trip')}: ${r.trip_title}\n${tr('Name')}: ${r.name}\n${tr('Email')}: ${r.email}\n${tr('Date')}: ${r.date||tr('Flexible')}\n${tr('Travelers')}: ${r.travelers}\n${tr('Style')}: ${tr(r.style)}\n${tr('Stays')}: ${tr(r.comfort)}\n${tr('Notes')}: ${r.message||tr('None')}\n\n${tr('This is a saved planning request, not a confirmed booking. No payment was taken.')}\n`;const url=URL.createObjectURL(new Blob([content],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`Laura-Luxury-Journeys-${r.reference}.txt`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});
const header=$('.site-header');function updateHeader(){header.classList.toggle('scrolled',window.scrollY>70)};window.addEventListener('scroll',updateHeader,{passive:true});updateHeader();
hydrate();render();syncCompare();$('#year').textContent=new Date().getFullYear();
const currentUrl=new URL(location.href);currentUrl.searchParams.delete('departure');currentUrl.searchParams.delete('duration');history.replaceState({},'',currentUrl);const initialTrip=window.siteTripID(currentUrl);if(initialTrip)openTrip(initialTrip,false);
const pendingRequest=readStore('desertgate.pending',null);if(pendingRequest?.payload&&pendingRequest.key){const p=pendingRequest.payload;Object.entries(p).forEach(([key,value])=>{if($('#plan-form').elements[key])$('#plan-form').elements[key].value=value});if(validIds.has(p.trip_id))planTrip=TRIPS.find(t=>t.id===p.trip_id);}
if(!matchMedia('(prefers-reduced-motion: reduce)').matches){const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target)}}),{threshold:.08});$$('.section-heading,.desert-story-copy,.approach-intro,.steps article,.note-card,.closing-cta').forEach(el=>{el.classList.add('reveal');observer.observe(el)});}

// Five photographed chapters; each image carries its own marketing story in every public language.
const heroEditorial={
  "en": {
    "common": {
      "eyebrow": "MOROCCO WITH LAURA LUXURY JOURNEYS",
      "cta": "Plan my journey",
      "footnote": "Your interests. Your company. Your pace."
    },
    "slides": [
      {
        "title": "Marrakech,",
        "emphasis": "yours to explore.",
        "copy": "Follow the garden paths towards Koutoubia, then wander into the medina. Leave room for a courtyard café and whatever catches your eye.",
        "label": "MARRAKECH",
        "line": "Palm-lined paths and the warmth of Marrakech."
      },
      {
        "title": "Chase the light.",
        "emphasis": "Enjoy the ride.",
        "copy": "Head out on a quad as the landscape turns gold. Open tracks, a wide horizon and a little adventure bring a different rhythm to your time in Morocco.",
        "label": "QUAD",
        "line": "Desert tracks in the evening light."
      },
      {
        "title": "A change of pace,",
        "emphasis": "beside the dunes.",
        "copy": "Trade the city for open sand and a slower afternoon. Watch the camels rest at the edge of the dunes as the Sahara stretches into the distance.",
        "label": "SAHARA",
        "line": "Camels, golden dunes and room to breathe."
      },
      {
        "title": "Take your time.",
        "emphasis": "The dunes can wait.",
        "copy": "Walk a little further across the sand and find a view of your own. Out here, the changing light is reason enough to linger.",
        "label": "SAHARA",
        "line": "Footsteps across the Sahara."
      },
      {
        "title": "Blue streets,",
        "emphasis": "mountain air.",
        "copy": "Spend time among Chefchaouen’s blue lanes, small squares and hillside views. A pause on a café terrace is as much a part of the day as the exploring.",
        "label": "CHEFCHAOUEN",
        "line": "Chefchaouen beneath the Rif Mountains."
      }
    ]
  },
  "fr": {
    "common": {
      "eyebrow": "VOYAGES PRIVÉS SUR MESURE À TRAVERS LE MAROC",
      "cta": "Imaginer mon voyage",
      "footnote": "Itinéraires soignés · Adresses choisies · Expertise locale"
    },
    "slides": [
      {
        "title": "Marrakech,",
        "emphasis": "à votre rythme.",
        "copy": "Suivez les allées des jardins jusqu’à la Koutoubia, puis entrez dans la médina. Gardez du temps pour un café dans un patio et les découvertes en chemin.",
        "label": "MARRAKECH",
        "line": "Palmiers et douceur de Marrakech."
      },
      {
        "title": "Suivez la lumière.",
        "emphasis": "Savourez la balade.",
        "copy": "Partez en quad tandis que le paysage se pare d’or. Des pistes ouvertes, un vaste horizon et un peu d’aventure donnent un autre rythme au voyage.",
        "label": "QUAD",
        "line": "Les pistes du désert dans la lumière du soir."
      },
      {
        "title": "Ralentissez,",
        "emphasis": "au pied des dunes.",
        "copy": "Quittez la ville pour le sable et un après-midi tranquille. Les chameaux se reposent au pied des dunes, face à l’immensité du Sahara.",
        "label": "SAHARA",
        "line": "Chameaux, dunes dorées et grands espaces."
      },
      {
        "title": "Prenez le temps.",
        "emphasis": "Les dunes vous attendent.",
        "copy": "Marchez un peu plus loin sur le sable pour trouver votre point de vue. Ici, la lumière qui change invite à s’attarder.",
        "label": "SAHARA",
        "line": "Quelques pas dans le Sahara."
      },
      {
        "title": "Ruelles bleues,",
        "emphasis": "air des montagnes.",
        "copy": "Découvrez les ruelles bleues, les petites places et les panoramas de Chefchaouen. Une pause en terrasse fait pleinement partie de la journée.",
        "label": "CHEFCHAOUEN",
        "line": "Chefchaouen au pied du Rif."
      }
    ]
  },
  "es": {
    "common": {
      "eyebrow": "VIAJES PRIVADOS A MEDIDA POR MARRUECOS",
      "cta": "Diseñar mi viaje",
      "footnote": "Rutas cuidadas · Alojamientos elegidos · Experiencia local"
    },
    "slides": [
      {
        "title": "Marrakech,",
        "emphasis": "a tu ritmo.",
        "copy": "Recorre los jardines hacia la Kutubía y adéntrate en la medina. Deja tiempo para un café en un patio y para lo que despierte tu curiosidad.",
        "label": "MARRAKECH",
        "line": "Palmeras y la calidez de Marrakech."
      },
      {
        "title": "Sigue la luz.",
        "emphasis": "Disfruta del camino.",
        "copy": "Sal en quad mientras el paisaje se tiñe de oro. Caminos abiertos, un horizonte amplio y un poco de aventura dan otro ritmo a tu viaje.",
        "label": "QUAD",
        "line": "Rutas por el desierto al caer la tarde."
      },
      {
        "title": "Baja el ritmo,",
        "emphasis": "junto a las dunas.",
        "copy": "Cambia la ciudad por la arena y una tarde tranquila. Los camellos descansan al pie de las dunas mientras el Sáhara se extiende a lo lejos.",
        "label": "SAHARA",
        "line": "Camellos, dunas doradas y espacio para respirar."
      },
      {
        "title": "Tómate tu tiempo.",
        "emphasis": "Las dunas te esperan.",
        "copy": "Camina un poco más sobre la arena y encuentra tu propia vista. Aquí, la luz cambiante invita a quedarse.",
        "label": "SAHARA",
        "line": "Huellas sobre la arena del Sáhara."
      },
      {
        "title": "Calles azules,",
        "emphasis": "aire de montaña.",
        "copy": "Explora las callejuelas azules, las plazas y las vistas de Chefchaouen. Una pausa en una terraza forma parte del placer de descubrirla.",
        "label": "CHEFCHAOUEN",
        "line": "Chefchaouen al pie de las montañas del Rif."
      }
    ]
  },
  "de": {
    "common": {
      "eyebrow": "MASSGESCHNEIDERTE PRIVATREISEN DURCH MAROKKO",
      "cta": "Meine Reise gestalten",
      "footnote": "Sorgfältige Routen · Ausgewählte Unterkünfte · Lokale Expertise"
    },
    "slides": [
      {
        "title": "Marrakesch,",
        "emphasis": "in Ihrem Tempo.",
        "copy": "Spazieren Sie durch die Gärten zur Koutoubia und weiter in die Medina. Lassen Sie Zeit für ein Café im Innenhof und kleine Entdeckungen unterwegs.",
        "label": "MARRAKECH",
        "line": "Palmenwege und die Wärme von Marrakesch."
      },
      {
        "title": "Dem Licht entgegen.",
        "emphasis": "Die Fahrt genießen.",
        "copy": "Fahren Sie mit dem Quad hinaus, wenn die Landschaft golden wird. Offene Wege, ein weiter Horizont und etwas Abenteuer bringen Abwechslung in Ihre Reise.",
        "label": "QUAD",
        "line": "Wüstenwege im Abendlicht."
      },
      {
        "title": "Ein ruhigerer Tag,",
        "emphasis": "am Rand der Dünen.",
        "copy": "Tauschen Sie die Stadt gegen Sand und einen entspannten Nachmittag. Kamele ruhen vor den Dünen, dahinter erstreckt sich die Sahara.",
        "label": "SAHARA",
        "line": "Kamele, goldene Dünen und Raum zum Durchatmen."
      },
      {
        "title": "Lassen Sie sich Zeit.",
        "emphasis": "Die Dünen warten.",
        "copy": "Gehen Sie ein Stück weiter über den Sand und finden Sie Ihren eigenen Ausblick. Das wechselnde Licht lädt zum Verweilen ein.",
        "label": "SAHARA",
        "line": "Spuren im Sand der Sahara."
      },
      {
        "title": "Blaue Gassen,",
        "emphasis": "frische Bergluft.",
        "copy": "Entdecken Sie die blauen Gassen, kleinen Plätze und Ausblicke von Chefchaouen. Eine Pause auf der Caféterrasse gehört zum Tag dazu.",
        "label": "CHEFCHAOUEN",
        "line": "Chefchaouen am Fuß des Rifgebirges."
      }
    ]
  },
  "it": {
    "common": {
      "eyebrow": "VIAGGI PRIVATI SU MISURA IN MAROCCO",
      "cta": "Disegna il mio viaggio",
      "footnote": "Itinerari curati · Soggiorni selezionati · Esperienza locale"
    },
    "slides": [
      {
        "title": "Marrakech,",
        "emphasis": "con i tuoi tempi.",
        "copy": "Attraversa i giardini verso la Koutoubia, poi entra nella medina. Lascia spazio a un caffè in un cortile e alle scoperte lungo il cammino.",
        "label": "MARRAKECH",
        "line": "Palme e il calore di Marrakech."
      },
      {
        "title": "Segui la luce.",
        "emphasis": "Goditi il percorso.",
        "copy": "Parti in quad mentre il paesaggio si tinge d’oro. Piste aperte, un ampio orizzonte e un po’ di avventura danno un altro ritmo al viaggio.",
        "label": "QUAD",
        "line": "Piste nel deserto alla luce della sera."
      },
      {
        "title": "Rallenta,",
        "emphasis": "accanto alle dune.",
        "copy": "Lascia la città per la sabbia e un pomeriggio tranquillo. I cammelli riposano ai piedi delle dune, mentre il Sahara si estende in lontananza.",
        "label": "SAHARA",
        "line": "Cammelli, dune dorate e spazio per respirare."
      },
      {
        "title": "Prenditi il tuo tempo.",
        "emphasis": "Le dune ti aspettano.",
        "copy": "Cammina ancora un po’ sulla sabbia e trova il tuo panorama. Qui, la luce che cambia è un invito a fermarsi.",
        "label": "SAHARA",
        "line": "Passi sulla sabbia del Sahara."
      },
      {
        "title": "Vicoli blu,",
        "emphasis": "aria di montagna.",
        "copy": "Scopri i vicoli blu, le piazzette e i panorami di Chefchaouen. Anche una pausa sulla terrazza di un caffè fa parte della giornata.",
        "label": "CHEFCHAOUEN",
        "line": "Chefchaouen ai piedi delle montagne del Rif."
      }
    ]
  },
  "pt": {
    "common": {
      "eyebrow": "VIAGENS PRIVADAS À MEDIDA POR MARROCOS",
      "cta": "Desenhar a minha viagem",
      "footnote": "Rotas cuidadas · Estadias escolhidas · Experiência local"
    },
    "slides": [
      {
        "title": "Marraquexe,",
        "emphasis": "ao seu ritmo.",
        "copy": "Percorra os jardins até à Koutoubia e entre na medina. Reserve tempo para um café num pátio e para as descobertas pelo caminho.",
        "label": "MARRAKECH",
        "line": "Palmeiras e o calor de Marraquexe."
      },
      {
        "title": "Siga a luz.",
        "emphasis": "Desfrute do percurso.",
        "copy": "Parta de moto-quatro quando a paisagem se torna dourada. Trilhos abertos, um horizonte amplo e um pouco de aventura dão outro ritmo à viagem.",
        "label": "QUAD",
        "line": "Trilhos no deserto à luz do entardecer."
      },
      {
        "title": "Abrande o passo,",
        "emphasis": "junto às dunas.",
        "copy": "Troque a cidade pela areia e por uma tarde tranquila. Os camelos descansam junto às dunas, enquanto o Saara se estende ao longe.",
        "label": "SAHARA",
        "line": "Camelos, dunas douradas e espaço para respirar."
      },
      {
        "title": "Demore o tempo que quiser.",
        "emphasis": "As dunas esperam.",
        "copy": "Caminhe um pouco mais pela areia e encontre a sua própria vista. Aqui, a luz que muda convida a ficar.",
        "label": "SAHARA",
        "line": "Passos na areia do Saara."
      },
      {
        "title": "Ruelas azuis,",
        "emphasis": "ar de montanha.",
        "copy": "Descubra as ruelas azuis, as pequenas praças e as vistas de Chefchaouen. Uma pausa numa esplanada também faz parte do dia.",
        "label": "CHEFCHAOUEN",
        "line": "Chefchaouen junto às montanhas do Rif."
      }
    ]
  },
  "nl": {
    "common": {
      "eyebrow": "PRIVÉREIZEN OP MAAT DOOR MAROKKO",
      "cta": "Ontwerp mijn reis",
      "footnote": "Doordachte routes · Geselecteerde verblijven · Lokale expertise"
    },
    "slides": [
      {
        "title": "Marrakech,",
        "emphasis": "in uw eigen tempo.",
        "copy": "Wandel door de tuinen naar de Koutoubia en verder de medina in. Houd tijd vrij voor koffie op een binnenplaats en ontdekkingen onderweg.",
        "label": "MARRAKECH",
        "line": "Palmen en de warmte van Marrakech."
      },
      {
        "title": "Volg het licht.",
        "emphasis": "Geniet van de rit.",
        "copy": "Trek eropuit met een quad terwijl het landschap goud kleurt. Open paden, een wijde horizon en wat avontuur geven uw reis een ander ritme.",
        "label": "QUAD",
        "line": "Woestijnpaden in het avondlicht."
      },
      {
        "title": "Een rustiger tempo,",
        "emphasis": "naast de duinen.",
        "copy": "Verruil de stad voor zand en een rustige middag. Kamelen rusten aan de voet van de duinen, met de Sahara in de verte.",
        "label": "SAHARA",
        "line": "Kamelen, gouden duinen en ruimte om te ademen."
      },
      {
        "title": "Neem de tijd.",
        "emphasis": "De duinen wachten.",
        "copy": "Loop wat verder over het zand en vind uw eigen uitzicht. Het veranderende licht is hier reden genoeg om te blijven.",
        "label": "SAHARA",
        "line": "Voetstappen door de Sahara."
      },
      {
        "title": "Blauwe straatjes,",
        "emphasis": "frisse berglucht.",
        "copy": "Ontdek de blauwe straatjes, kleine pleinen en uitzichten van Chefchaouen. Een pauze op een caféterras hoort net zo goed bij de dag.",
        "label": "CHEFCHAOUEN",
        "line": "Chefchaouen aan de voet van het Rifgebergte."
      }
    ]
  }
};
const heroEdition=heroEditorial[CMS.language.code]||heroEditorial.en;
const heroSlides=CMS.site.hero_images.map((id,i)=>{const m=CMS.media[id],chapter=heroEdition.slides[id==='hero-chefchaouen-20260926'?4:i]||heroEdition.slides[0];return {...chapter,image:id,path:m.path,alt:m.alt}});
function renderHeroContent(slide){const c=heroEdition.common;$('.hero-content>.eyebrow').innerHTML='<span class="tiny-sun">✳</span> '+esc(c.eyebrow);$('#hero-title').innerHTML=esc(slide.title)+'<br><em>'+esc(slide.emphasis)+'</em>';$('.hero-copy').textContent=slide.copy;$('.hero-content>.button').innerHTML=esc(c.cta)+' '+icon('arrow');$('.hero-footnote').innerHTML='<span class="line"></span> '+esc(c.footnote);$('.hero-location>div').innerHTML=`${esc(slide.label)}<small>${esc(slide.line)}</small>`;}
renderHeroContent(heroSlides[0]);
const heroPrimary=$('.hero-image'),heroSecondary=heroPrimary.cloneNode();heroSecondary.classList.remove('is-active');heroSecondary.removeAttribute('fetchpriority');heroSecondary.setAttribute('aria-hidden','true');heroSecondary.alt='';heroPrimary.before(heroSecondary);const heroLayers=[heroPrimary,heroSecondary];let heroIndex=0,heroLayer=0,heroChanging=false,heroPaused=matchMedia('(prefers-reduced-motion: reduce)').matches;let heroTimer;
async function heroSlide(index){if(index===heroIndex||heroChanging)return;heroChanging=true;const target=heroLayers[1-heroLayer],slide=heroSlides[index];setCMSPhoto(target,CMS.media[slide.image],'100vw');try{await target.decode();}catch{heroChanging=false;return}target.alt=slide.alt;target.removeAttribute('aria-hidden');heroLayers[heroLayer].setAttribute('aria-hidden','true');heroLayers[heroLayer].classList.remove('is-active');target.classList.add('is-active');heroLayer=1-heroLayer;heroIndex=index;renderHeroContent(slide);$$('[data-hero-slide]').forEach(b=>{const active=Number(b.dataset.heroSlide)===index;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});setTimeout(()=>heroChanging=false,1300)}
function heroSchedule(){clearInterval(heroTimer);if(!heroPaused)heroTimer=setInterval(()=>{if(!document.hidden&&window.scrollY<$('.hero').offsetHeight*.65)heroSlide((heroIndex+1)%heroSlides.length)},5000);$('#hero-pause').textContent=heroPaused?'▷':'Ⅱ';$('#hero-pause').setAttribute('aria-label',heroPaused?'Play changing photographs':'Pause changing photographs');}
$$('[data-hero-slide]').forEach(b=>b.addEventListener('click',()=>{heroSlide(Number(b.dataset.heroSlide));heroSchedule()}));$('#hero-pause').addEventListener('click',()=>{heroPaused=!heroPaused;heroSchedule()});heroSchedule();

translateDOM();
