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
  const context = {e:{preventDefault(){},currentTarget:form},FormData:function(){return Object.entries(fields)},
    planTrip:{id:'sahara-marrakech-3-days',title:'Three Days to the Sahara',duration:'3 days'},
    tr:x=>x,CMS:{site:{whatsapp:'212667687763'}},
    $:s=>s==='#duration-field'?{hidden:false}:status,
    window:{open:(url)=>{opened=url}},document:{createTextNode:x=>x,createElement:()=>({})}};
  vm.runInNewContext('(function(){' + handler + '\n})()',context);
  const url = new URL(opened);
  assert.equal(url.origin,'https://wa.me');assert.equal(url.pathname,'/212667687763');
  assert.ok(url.searchParams.get('text').includes('sahara-marrakech-3-days'));
  assert.equal(url.searchParams.get('text').includes('Email:'),Boolean(email));
  assert.equal(status.link.href,opened);assert.ok(feedback.includes('Send it in WhatsApp'));
}
console.log('PASS: actual WhatsApp submit handler handles optional email, trip context, number and popup fallback; no messages sent.');
