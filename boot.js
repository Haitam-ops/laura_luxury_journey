'use strict';
// Translations are stored on this server. Visitor text is never sent to a translation service.
(async()=>{
 const url=new URL(location.href);let preference='en';try{preference=localStorage.getItem('desertgate.language')||'en'}catch{}
 const requested=(url.searchParams.get('lang')||preference||'en').toLowerCase();
 let response;
 let cms;
 try {
   response=await fetch('/api/content?lang='+encodeURIComponent(requested));
   if(!response.ok||!response.headers.get('content-type')?.includes('application/json'))throw Error('api');
   cms=await response.json();
 } catch {
   const language=/^[a-z]{2,3}(?:-[a-z]{2,4})?$/i.test(requested)?requested:'en';
   response=await fetch('/data/content.'+encodeURIComponent(language)+'.json?v=hero-20260926');
   if(!response.ok&&language!=='en')response=await fetch('/data/content.en.json?v=hero-20260926');
   if(!response.ok)response=await fetch('/data/content.json?v=hero-20260926');
   if(!response.ok)throw Error('The trip collection could not be loaded.');
   cms=await response.json();window.STATIC_FRONTEND=true;
 }
 cms.site.whatsapp=cms.site.whatsapp||'212667687763';window.CMS=cms;window.TRIPS=cms.trips;
 document.documentElement.lang=cms.language.code;document.documentElement.dir=cms.language.dir;
 if(url.searchParams.has('lang')&&url.searchParams.get('lang')!==cms.language.code){url.searchParams.set('lang',cms.language.code);history.replaceState({},'',url)}
 try{localStorage.setItem('desertgate.language',cms.language.code)}catch{}
 window.tr=(source,values={})=>{let result=cms.strings[source]||source;for(const [key,value]of Object.entries(values))result=result.split('{'+key+'}').join(String(value));return result};
 const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 // Share responsive photography across the hero, cards, galleries and static sections.
 const mediaByPath=new Map();
 for(const m of Object.values(cms.media)){
   mediaByPath.set(m.path,m);mediaByPath.set('/assets/'+m.id+'.webp',m);
   for(const variant of m.variants||[])mediaByPath.set(variant.path,m);
 }
 const photoSizes=image=>image.closest('.hero')?'100vw':image.closest('.gallery-filmstrip,.lightbox-thumbs')?'100px':image.closest('.photo-viewer')?'(max-width:700px) 100vw, 85vw':image.closest('.gallery-collage')?'(max-width:700px) 100vw, 65vw':'(max-width:620px) 100vw, (max-width:1000px) 50vw, 33vw';
 window.setCMSPhoto=(image,m,sizes=photoSizes(image))=>{
   if(image.closest('.hero'))image.style.objectPosition=m.id==='hero-quad-20260926'?'75% 50%':m.id==='hq-medina'?'50% 28%':m.id==='hero-ouzoud-user'?'75% 50%':'50% 50%';
   const attributes={src:m.path,alt:m.alt,width:m.width,height:m.height,decoding:'async'};
   if(m.variants?.length){attributes.srcset=m.variants.map(v=>v.path+' '+v.width+'w').join(', ');attributes.sizes=sizes;}
   else{image.removeAttribute('srcset');image.removeAttribute('sizes');}
   for(const [key,value]of Object.entries(attributes))if(value!=null&&image.getAttribute(key)!==String(value))image.setAttribute(key,String(value));
 };
 const improvePhoto=image=>{const m=mediaByPath.get(new URL(image.getAttribute('src')||'',location.href).pathname);if(m)setCMSPhoto(image,m);};
 document.querySelectorAll('img').forEach(improvePhoto);
 new MutationObserver(records=>{for(const record of records){if(record.type==='attributes')improvePhoto(record.target);else for(const node of record.addedNodes){if(node.nodeType!==1)continue;if(node.tagName==='IMG')improvePhoto(node);node.querySelectorAll('img').forEach(improvePhoto);}}}).observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['src']});
 const seen=new WeakMap();
 window.translateDOM=(root=document.body)=>{
   const process=node=>{const current=node.nodeValue;if(!current?.trim()||node.parentElement?.closest('script,style,textarea,[data-no-translate]'))return;const prior=seen.get(node);if(prior===current)return;const original=current.trim();const translated=cms.strings[original];if(translated&&translated!==original)node.nodeValue=current.replace(original,translated);seen.set(node,node.nodeValue)};
   if(root.nodeType===3)process(root);else{const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;while(node=walker.nextNode())process(node)}
   const elements=root.querySelectorAll?.('[placeholder],[aria-label],[title],[alt]')||[];
   for(const el of elements){if(el.closest('[data-no-translate]'))continue;for(const key of ['placeholder','aria-label','title','alt']){const value=el.getAttribute(key);if(value&&cms.strings[value])el.setAttribute(key,cms.strings[value])}}
 };
 const s=cms.site;
 document.querySelectorAll('.brand>[data-brand-text]').forEach(el=>{el.textContent=s.brand});
 document.querySelectorAll('.brand').forEach(el=>{el.setAttribute('aria-label',s.brand);el.setAttribute('data-no-translate','');el.href='/?lang='+cms.language.code});
 document.querySelector('.hero-content>.eyebrow').innerHTML='<span class="tiny-sun">✳</span> '+escape(s.hero_eyebrow);
 document.querySelector('#hero-title').innerHTML=escape(s.hero_title)+'<br><em>'+escape(s.hero_emphasis)+'</em>';
 document.querySelector('.hero-copy').textContent=s.hero_copy;
 document.querySelector('#journeys-title').innerHTML=escape(s.collection_title)+'<br><em>'+escape(s.collection_emphasis)+'</em>';
 document.querySelector('#journeys .section-heading>p').textContent=s.collection_copy;
 document.querySelector('.approach-intro h2').textContent=s.about_title;
 document.querySelector('.approach-intro>p:not(.eyebrow)').textContent=s.about_copy;
 document.querySelector('.footer-main>div:first-child>p').textContent=s.tagline;
 const footerCredit=document.querySelector('.footer-bottom>span');
 if(footerCredit)footerCredit.innerHTML='© <span id="year">'+new Date().getFullYear()+'</span> '+escape(tr(s.brand+'. See Morocco your way.'));
 const firstPhoto=cms.media[s.hero_images[0]];if(firstPhoto){const hero=document.querySelector('.hero-image');setCMSPhoto(hero,firstPhoto,'100vw');const preload=document.querySelector('link[rel=preload][as=image]');preload.href=firstPhoto.path;if(firstPhoto.variants){preload.imageSrcset=firstPhoto.variants.map(v=>v.path+' '+v.width+'w').join(', ');preload.imageSizes='100vw';}}
 document.title=s.brand+' — '+s.hero_title+' '+s.hero_emphasis;
 document.querySelector('meta[name=description]').content=s.collection_copy;
 const contact=document.createElement('div');contact.className='public-contact';contact.setAttribute('data-no-translate','');
 if(s.email){const link=document.createElement('a');link.href='mailto:'+s.email;link.textContent=s.email;contact.append(link)}
 if(s.phone){const link=document.createElement('a');link.href='tel:'+s.phone.replace(/[^+\d]/g,'');link.textContent=s.phone;link.dir='ltr';contact.append(link)}
 if(s.address){const line=document.createElement('span');line.textContent=s.address;contact.append(line)}
 document.querySelector('.footer-main>div:first-child').append(contact);
 const social=document.createElement('div');social.className='social-links';social.setAttribute('data-no-translate','');
 for(const [key,label,mark] of [['instagram','Instagram','◎'],['facebook','Facebook','f'],['tiktok','TikTok','♪'],['youtube','YouTube','▷']]){if(!s[key])continue;const link=document.createElement('a');link.href=s[key];link.target='_blank';link.rel='noopener noreferrer';link.setAttribute('aria-label',label);link.title=label;link.textContent=mark;social.append(link)}
 if(social.childElementCount)contact.after(social);
 const whatsapp=document.createElement(s.whatsapp?'a':'button');whatsapp.className='whatsapp-contact';
 whatsapp.innerHTML='<svg viewBox="0 0 32 32" aria-hidden="true"><path fill="currentColor" d="M16.04 3A12.8 12.8 0 0 0 5 22.37L3.2 29l6.8-1.78A12.8 12.8 0 1 0 16.04 3m0 23.45a10.6 10.6 0 0 1-5.4-1.48l-.39-.23-4.04 1.06 1.08-3.94-.26-.4a10.62 10.62 0 1 1 9.01 4.99m5.83-7.95c-.32-.16-1.89-.93-2.18-1.04-.29-.1-.5-.16-.72.16-.21.32-.82 1.04-1 1.25-.19.21-.37.24-.69.08-.32-.16-1.35-.5-2.58-1.6-.95-.85-1.6-1.9-1.78-2.22-.18-.32-.02-.49.14-.65l.48-.56c.16-.19.21-.32.32-.53.1-.22.05-.4-.03-.56-.08-.16-.71-1.73-.97-2.37-.25-.61-.51-.52-.71-.53h-.61c-.21 0-.56.08-.85.4-.29.32-1.11 1.09-1.11 2.66s1.14 3.1 1.3 3.31c.16.22 2.26 3.46 5.47 4.85.77.33 1.36.53 1.83.68.77.24 1.47.21 2.02.13.62-.1 1.89-.77 2.16-1.52.26-.74.26-1.38.18-1.52-.08-.13-.29-.21-.61-.37"/></svg><span>WhatsApp</span>';
 whatsapp.setAttribute('aria-label',tr('Talk about your trip')+' · WhatsApp');
 if(s.whatsapp){whatsapp.href='https://wa.me/'+s.whatsapp.replace(/\D/g,'');whatsapp.target='_blank';whatsapp.rel='noopener noreferrer'}else{whatsapp.setAttribute('aria-disabled','true');whatsapp.title=tr('WhatsApp will be available soon.');whatsapp.addEventListener('click',()=>{if(window.CMS&&typeof toast==='function')toast(tr('WhatsApp will be available soon.'));});}
 if(s.whatsapp)document.body.append(whatsapp);
 // Fixed values keep the request contract stable while option labels are translated.
 document.querySelectorAll('option:not([value])').forEach(option=>option.value=option.textContent.trim());
 document.querySelectorAll('[data-category]').forEach(b=>{const count=b.querySelector('small');if(count)count.textContent=cms.trips.filter(t=>t.category===b.dataset.category).length});
 const control=document.createElement('div');control.className='language-switch';
 const globe='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 7h14M5 17h14"/></svg>';
 control.innerHTML=`<button class="language-trigger" id="site-language" type="button" aria-expanded="false" aria-controls="language-panel" aria-label="${escape(tr('Choose your language'))}: ${escape(cms.language.native)}">${globe}<span class="language-current" data-no-translate>${escape(cms.language.native)}</span><span class="language-code" data-no-translate>${escape(cms.language.code.toUpperCase())}</span><svg class="language-chevron" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="m4 6 4 4 4-4"/></svg></button><div class="language-panel" id="language-panel" hidden><p class="language-heading">${escape(tr('Choose your language'))}</p><nav aria-label="${escape(tr('Choose your language'))}">${cms.languages.map(l=>{const next=new URL(location.href);next.searchParams.set('lang',l.code);const active=l.code===cms.language.code;return `<a class="language-option${active?' selected':''}" href="${escape(next.href)}" hreflang="${escape(l.code)}" lang="${escape(l.code)}" data-language="${escape(l.code)}" data-no-translate ${active?'aria-current="true"':''}><span class="language-monogram">${escape(l.code.toUpperCase())}</span><span><strong>${escape(l.native)}</strong><small>${escape(l.name)}</small></span><span class="language-check" aria-hidden="true">${active?'✓':''}</span></a>`}).join('')}</nav></div>`;
 document.querySelector('.header-actions').prepend(control);
 const languageTrigger=control.querySelector('.language-trigger'),languagePanel=control.querySelector('.language-panel');
 const languageLinks=[...control.querySelectorAll('[data-language]')];
 const toggleLanguage=open=>{if(open)languageLinks.forEach(link=>{const next=new URL(location.href);next.searchParams.set('lang',link.dataset.language);link.href=next.href;});languagePanel.hidden=!open;languageTrigger.setAttribute('aria-expanded',String(open));};
 languageTrigger.addEventListener('click',()=>toggleLanguage(languagePanel.hidden));
 control.addEventListener('keydown',e=>{
   if(e.key==='Escape'&&!languagePanel.hidden){e.preventDefault();e.stopPropagation();toggleLanguage(false);languageTrigger.focus();}
   if(['ArrowDown','ArrowUp','Home','End'].includes(e.key)){e.preventDefault();toggleLanguage(true);const i=languageLinks.indexOf(document.activeElement);const next=e.key==='Home'?0:e.key==='End'?languageLinks.length-1:(i+(e.key==='ArrowUp'?-1:1)+languageLinks.length)%languageLinks.length;languageLinks[next].focus();}
 });
 document.addEventListener('click',e=>{if(!control.contains(e.target))toggleLanguage(false);});
 control.addEventListener('focusout',()=>{setTimeout(()=>{if(!control.contains(document.activeElement))toggleLanguage(false);},0);});
 languageLinks.forEach(link=>link.addEventListener('click',()=>{try{localStorage.setItem('desertgate.language',link.dataset.language)}catch{}}));
 for(const lang of cms.languages){const link=document.createElement('link');link.rel='alternate';link.hreflang=lang.code;const other=new URL(location.href);other.searchParams.set('lang',lang.code);link.href=other.href;document.head.append(link)}
 translateDOM();
 new MutationObserver(records=>{for(const record of records){if(record.type==='characterData')translateDOM(record.target);else for(const node of record.addedNodes)if(node.nodeType===1||node.nodeType===3)translateDOM(node)}}).observe(document.body,{subtree:true,childList:true,characterData:true});
 const script=document.createElement('script');script.src='/app.js?v=hero-20260926';script.onload=()=>{translateDOM();document.body.classList.add('content-ready')};script.onerror=()=>showError();const mapScript=document.createElement('script');mapScript.src='/route-map.js?v=editorial-20260926';mapScript.onload=()=>document.head.append(script);mapScript.onerror=()=>showError();const gallery=document.createElement('script');gallery.src='/gallery.js?v=editorial-20260926';gallery.onload=()=>document.head.append(mapScript);gallery.onerror=()=>showError();document.head.append(gallery);
 function showError(){const grid=document.querySelector('#trip-grid');grid.innerHTML='<div class="empty-state"><h3>'+escape(tr('The collection could not be loaded.'))+'</h3><p>'+escape(tr('Please refresh the page to try again.'))+'</p></div>'}
})().catch(()=>{document.querySelector('#trip-grid').innerHTML='<div class="empty-state"><h3>The collection could not be loaded.</h3><p>Please refresh the page to try again.</p></div>';});
