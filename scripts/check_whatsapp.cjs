// Exercise the actual submit handler without opening WhatsApp or sending a message.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('app.js', 'utf8');
const handler = source.split("$('#plan-form').addEventListener('submit',e=>{")[1].split("\n});")[0];
for (const email of ['', 'test@example.invalid']) {
  let opened, feedback;
  const status = {replaceChildren(value){feedback=value}, append(value){this.link=value}};
  const fields = {name:'Release test',email,date:'',travelers:'2',style:'Private',comfort:'Help me decide',message:''};
  const form = {reportValidity:()=>true,elements:{duration_flexibility:{selectedOptions:[{textContent:'Keep the suggested duration'}]}}};
  const context = {location:{},e:{preventDefault(){},currentTarget:form},FormData:function(){return Object.entries(fields)},
    planTrip:{id:'sahara-marrakech-3-days',title:'Three Days to the Sahara',duration:'3 days'},
    tr:x=>x,CMS:{site:{whatsapp:'212667687763'}},
    $:s=>s==='#duration-field'?{hidden:false}:s==='#footer-email'?{href:'mailto:manystarstravel@gmail.com'}:status,
    window:{open:(url)=>{opened=url}},document:{createTextNode:x=>x,createElement:()=>({})}};
  vm.runInNewContext('(function(){' + handler + '\n})()',context);
  const url = new URL(opened);
  assert.equal(url.origin,'https://wa.me');assert.equal(url.pathname,'/212667687763');
  assert.ok(url.searchParams.get('text').includes('sahara-marrakech-3-days'));
  assert.equal(url.searchParams.get('text').includes('Email:'),Boolean(email));
  assert.equal(status.link.href,opened);assert.ok(feedback.includes('press Send'));
  context.e.submitter = {value:'email'};
  opened = undefined;
  vm.runInNewContext('(function(){' + handler + '\n})()',context);
  const draft = new URL(context.location.href);
  assert.equal(draft.protocol,'mailto:');
  assert.equal(draft.pathname,'manystarstravel@gmail.com');
  assert.match(draft.searchParams.get('subject'),/Three Days to the Sahara/);
  assert.match(draft.searchParams.get('body'),/sahara-marrakech-3-days/);
  assert.equal(draft.searchParams.get('body').includes('Email:'),Boolean(email));
  assert.equal(status.link.href,draft.href);
  assert.equal(opened,undefined);
}
console.log('PASS: WhatsApp and email draft handoffs preserve trip context and optional email. No messages sent.');
