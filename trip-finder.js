'use strict';

window.tripFinder = (() => {
  const themes = [
    ['sahara', 'Sahara dunes', 'sahara-marrakech-3-days'],
    ['atlas', 'Atlas mountains', 'imlil-atlas-day'],
    ['culture', 'Medinas & traditions', 'imperial-cities-sahara-9-days'],
    ['coast', 'Atlantic coast', 'essaouira-day'],
    ['food', 'Moroccan food', 'marrakech-cooking'],
    ['evening', 'Evenings & shows', 'agafay-evening'],
  ];
  const themesByTrip = {
    'sahara-marrakech-3-days': 'sahara atlas', 'marrakech-fes-sahara-4-days': 'sahara atlas culture',
    'slow-sahara-5-days': 'sahara atlas', 'southern-morocco-7-days': 'sahara atlas culture',
    'coast-desert-8-days': 'coast sahara culture', 'imperial-cities-sahara-9-days': 'culture sahara',
    'north-sahara-10-days': 'culture sahara atlas', 'grand-morocco-14-days': 'culture sahara coast atlas',
    'ouzoud-waterfalls': 'atlas', 'ourika-valley': 'atlas culture', 'essaouira-day': 'coast culture food',
    'ait-ben-haddou-day': 'atlas culture', 'imlil-atlas-day': 'atlas', 'agafay-evening': 'evening food',
    'marrakech-balloon': 'atlas', 'agafay-quad': 'adventure', 'agafay-buggy': 'adventure',
    'merzouga-camel': 'sahara', 'merzouga-sandboarding': 'sahara', 'atlas-paragliding': 'atlas',
    'marrakech-hammam': 'culture', 'marrakech-cooking': 'food culture', 'marrakech-dinner-show': 'evening food',
    'essaouira-horse-riding': 'coast', 'essaouira-surf-kitesurf': 'coast', 'taghazout-surf-kitesurf': 'coast',
  };
  const active = new Set(['ouzoud-waterfalls','imlil-atlas-day','agafay-quad','agafay-buggy','merzouga-sandboarding','atlas-paragliding','essaouira-horse-riding','essaouira-surf-kitesurf','taghazout-surf-kitesurf']);
  const relaxed = new Set(['slow-sahara-5-days','essaouira-day','agafay-evening','marrakech-hammam','marrakech-cooking','marrakech-dinner-show','marrakech-balloon']);
  const steps = [
    {title:'How much time do you have?', hint:'Choose the time you’d like us to plan for.', options:[
      ['hours','A few hours','agafay-evening'], ['day','One full day','essaouira-day'], ['short','2–4 days','sahara-marrakech-3-days'],
      ['week','5–7 days','southern-morocco-7-days'], ['long','8+ days','grand-morocco-14-days'], ['any','I’m flexible','imperial-cities-sahara-9-days'],
    ]},
    {title:'What draws you to Morocco?', hint:'Pick up to two things you’d love to experience.', options:themes},
    {title:'What pace feels right?', hint:'Choose how you’d like your time in Morocco to feel.', options:[
      ['active','Active & adventurous','agafay-quad'], ['relaxed','Slow & relaxed','essaouira-day'],
      ['mixed','A bit of both','southern-morocco-7-days'], ['any','Surprise me','agafay-evening'],
    ]},
  ];
  const duration = {
    hours: days => days < 1,
    day: days => days <= 1,
    short: days => days >= 2 && days <= 4,
    week: days => days >= 5 && days <= 7,
    long: days => days >= 8,
    any: () => true,
  };
  const dialog = document.querySelector('#trip-finder');
  const view = dialog.querySelector('.finder-view');
  const artwork = [...dialog.querySelectorAll('.finder-art img')];
  const byId = id => window.TRIPS.find(trip => trip.id === id);
  const tr = (text, values) => window.tr(text, values);
  let choices, step, onChoose, frame = 0, photoRequest = 0, requestedPhoto = '';
  let opener;
  let photoTimer;
  const node = (tag, className, text) => {
    const element = document.createElement(tag);
    if(className)element.className=className;
    if(text)element.textContent=text;
    return element;
  };
  function button(label, className, action){
    const element=node('button',className,label);
    element.type='button';
    element.addEventListener('click',action);
    return element;
  }
  function photoFor(id){
    return byId(id)?.photos?.[0];
  }
  function showPhoto(id){
    const photo=photoFor(id);
    const path=photo?.variants?.find(variant=>variant.width>=640)?.path||photo?.path;
    if(!path||requestedPhoto===path)return;
    requestedPhoto=path;
    const request=++photoRequest;
    const incoming=artwork[1-frame];
    incoming.onload=()=>{
      if(request!==photoRequest)return;
      artwork[frame].classList.remove('is-current');
      incoming.classList.add('is-current');
      frame=1-frame;
    };
    incoming.src=path;
  }
  function chosenPhoto(){
    if(step===3)return recommendations()[0]?.trip.id||'sahara-marrakech-3-days';
    return steps[step].options.find(([key])=>choices[step].includes(key))?.[2]
      ||(step===0?'sahara-marrakech-3-days':step===1?'ait-ben-haddou-day':'essaouira-day');
  }
  function answers(){
    const values=steps.map((question,index)=>question.options.filter(([key])=>choices[index].includes(key)).map(([,label])=>tr(label)).join(', '));
    return [['Time in Morocco',values[0]],['Interests',values[1]],['Preferred pace',values[2]]].filter(([,value])=>value);
  }
  function recommendations(){
    const time=choices[0][0]||'any';
    const pace=choices[2][0];
    return window.TRIPS.filter(trip=>duration[time](trip.days)).map(trip=>{
      const tags=(themesByTrip[trip.id]||'').split(' ');
      const matched=choices[1].filter(theme=>tags.includes(theme));
      const tripPace=active.has(trip.id)?'active':relaxed.has(trip.id)?'relaxed':'mixed';
      const score=matched.length*5+(tripPace===pace?2:0)+(time==='day'&&trip.days===1?1:0);
      return {trip,matched,score};
    }).sort((a,b)=>b.score-a.score).slice(0,2);
  }
  function updateContact(){
    const details=answers().map(([label,value])=>tr(label)+': '+value);
    const message=[tr('Hello Many Stars Travel, I would like to plan a trip.'),...details].join('\n');
    const email=document.querySelector('#footer-email').href;
    dialog.querySelector('[data-finder-email]').href=email+'?subject='+encodeURIComponent(tr('Trip enquiry'))+'&body='+encodeURIComponent(message.replaceAll('\n','\r\n'));
    dialog.querySelector('[data-finder-whatsapp]').href='https://wa.me/'+window.CMS.site.whatsapp.replace(/\D/g,'')+'?text='+encodeURIComponent(message);
  }
  function selectTrip(id){
    const submit=onChoose;
    const details=answers();
    opener=null;
    dialog.close();
    submit(id,details);
  }
  function render(focus=true){
    clearTimeout(photoTimer);
    const result=step===steps.length;
    dialog.querySelector('.finder-counter').textContent=result?tr('Your recommendations'):tr('Question {number} of 3',{number:step+1});
    dialog.querySelectorAll('.finder-meter span').forEach((part,index)=>part.classList.toggle('is-filled',index<=step));
    const question=steps[step];
    const title=node('h2','',tr(result?'A few trips for you':question.title));
    title.id='finder-title';
    title.tabIndex=-1;
    const matches=result?recommendations():[];
    const hint=result?(matches.some(match=>match.matched.length)?'Choose a trip as a starting point and tell us what you’d change.':'These trips fit your time. We can tailor a route around your interests.'):question.hint;
    view.replaceChildren(title,node('p','finder-intro',tr(hint)));
    const controls=node('div','finder-actions');
    const back=button(tr('Back'),'text-link',()=>{step--;render()});
    if(step)controls.append(back);
    if(result){
      const list=node('div','finder-results');
      for(const {trip,matched} of matches){
        const card=node('article','finder-match');
        const img=node('img');
        img.src=trip.photos?.[0]?.variants?.find(variant=>variant.width>=320)?.path||trip.photos[0].path;
        img.alt='';
        const info=node('div','finder-match-copy');
        const labels=matched.map(key=>tr(themes.find(theme=>theme[0]===key)[1]));
        info.append(node('h3','',trip.title),node('p','',trip.duration+' · '+trip.start),
          node('p','finder-match-reason',labels.length?labels.join(' · '):tr('Fits your available time')));
        const details=node('div','finder-match-details');
        details.id='finder-details-'+trip.id;
        details.hidden=true;
        if(trip.end&&trip.end!==trip.start)details.append(node('p','finder-match-route',trip.start+' → '+trip.end));
        details.append(node('p','',trip.summary));
        if(trip.highlights?.length){
          const highlights=node('ul','finder-match-highlights');
          for(const highlight of trip.highlights)highlights.append(node('li','',highlight));
          details.append(highlights);
        }
        const itinerary=node('a','finder-full-trip',tr('View full trip'));
        itinerary.href='/'+encodeURIComponent(window.CMS.language.code)+'/journeys/'+encodeURIComponent(trip.id)+'/';
        itinerary.target='_blank';
        itinerary.rel='noopener noreferrer';
        itinerary.setAttribute('aria-label',tr('View full trip (opens in a new tab)'));
        const externalMark=node('span','', '↗');
        externalMark.setAttribute('aria-hidden','true');
        itinerary.append(externalMark);
        details.append(itinerary);
        const actions=node('div','finder-match-actions');
        const toggle=button(tr('See details'),'text-link',()=>{
          details.hidden=!details.hidden;
          toggle.setAttribute('aria-expanded',String(!details.hidden));
          toggle.textContent=tr(details.hidden?'See details':'Hide details');
        });
        toggle.setAttribute('aria-expanded','false');
        toggle.setAttribute('aria-controls',details.id);
        actions.append(toggle,button(tr('Choose this trip'),'text-link',()=>selectTrip(trip.id)));
        info.append(actions);
        card.append(img,info,details);
        list.append(card);
      }
      view.append(list);
      controls.append(button(tr('Build something custom'),'button button-outline',()=>selectTrip(null)));
    }else{
      const options=node('div','finder-options'+(step===1?' finder-photo-options':''));
      options.setAttribute('role','group');
      options.setAttribute('aria-labelledby',title.id);
      const next=button(tr(step===2?'See my matches':'Continue'),'button button-rust',()=>{step++;render()});
      next.disabled=!choices[step].length;
      for(const [key,label,photo] of question.options){
        const choice=button(tr(label),'finder-choice',()=>{
          const selection=choices[step];
          if(step===1){
            if(selection.includes(key))choices[step]=selection.filter(value=>value!==key);
            else if(selection.length<2)selection.push(key);
            else return;
          }else choices[step]=[key];
          for(const item of options.children){
            item.setAttribute('aria-pressed',String(choices[step].includes(item.dataset.choice)));
            item.setAttribute('aria-disabled',String(step===1&&choices[step].length===2&&!choices[step].includes(item.dataset.choice)));
          }
          next.disabled=!choices[step].length;
          showPhoto(chosenPhoto());
          updateContact();
        });
        choice.dataset.choice=key;
        choice.setAttribute('aria-pressed',String(choices[step].includes(key)));
        choice.setAttribute('aria-disabled',String(step===1&&choices[step].length===2&&!choices[step].includes(key)));
        if(step===1){
          const img=node('img');
          const picture=photoFor(photo);
          if(picture){
            img.src=picture.variants?.find(variant=>variant.width>=320)?.path||picture.path;
            img.alt='';
            choice.prepend(img);
          }
        }
        choice.addEventListener('pointerenter',event=>{
          if(event.pointerType==='mouse')photoTimer=setTimeout(()=>showPhoto(photo),120);
        });
        choice.addEventListener('pointerleave',()=>{clearTimeout(photoTimer);showPhoto(chosenPhoto())});
        options.append(choice);
      }
      view.append(options);
      controls.append(next);
    }
    view.append(controls);
    showPhoto(chosenPhoto());
    updateContact();
    if(focus)title.focus({preventScroll:true});
  }
  dialog.addEventListener('close',()=>{
    clearTimeout(photoTimer);
    opener?.focus();
    opener=null;
  });
  return {
    open(callback){
      choices=[[],[],[]];
      step=0;
      onChoose=callback;
      opener=document.activeElement;
      dialog.showModal();
      render();
    },
  };
})();
