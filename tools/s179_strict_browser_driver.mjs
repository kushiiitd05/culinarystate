import fs from 'node:fs';
const [port,base,outFile,screenshot]=process.argv.slice(2);
const pages=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const ws=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
let sequence=0;const pending=new Map();
ws.onmessage=message=>{const data=JSON.parse(message.data);if(data.id){const [resolve,reject]=pending.get(data.id);pending.delete(data.id);data.error?reject(new Error(JSON.stringify(data.error))):resolve(data.result);}};
function send(method,params={}){const id=++sequence;return new Promise((resolve,reject)=>{pending.set(id,[resolve,reject]);ws.send(JSON.stringify({id,method,params}));});}
async function evaluate(expression){const out=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(out.exceptionDetails)throw new Error(JSON.stringify(out.exceptionDetails));return out.result.value;}
await send('Page.enable');await send('Runtime.enable');await send('Network.enable');
const external=[];const original=ws.onmessage;ws.onmessage=message=>{const p=JSON.parse(message.data);if(p.method==='Network.requestWillBeSent'&&!p.params.request.url.startsWith(base)&&!p.params.request.url.startsWith('data:'))external.push(p.params.request.url);original(message);};
await send('Emulation.setDeviceMetricsOverride',{width:1280,height:1200,deviceScaleFactor:1,mobile:false});
await send('Page.navigate',{url:base});
for(let i=0;i<100;i++){if(await evaluate("!!document.querySelector('#question')"))break;await new Promise(r=>setTimeout(r,30));}
const cases=[
 {id:'transform_heat',question:'How much vitamin C remains after boiling carrot?',recipe:'Boil carrot in water at 90 C for 5 minutes.'},
 {id:'substitution',question:'Can I substitute butter with olive oil?',recipe:''},
 {id:'safety',question:'Is this chicken safe to eat?',recipe:''},
 {id:'unsupported',question:'Here is a photo of my bread, is it proofed?',recipe:''},
];
const results=[];
for(const item of cases){
 const started=performance.now();
 await evaluate(`document.querySelector('#question').value=${JSON.stringify(item.question)};document.querySelector('#recipe').value=${JSON.stringify(item.recipe)};document.querySelector('#question-form').requestSubmit();`);
 for(let i=0;i<200;i++){if(await evaluate("!document.querySelector('#submit').disabled && !!document.querySelector('#result .card')"))break;await new Promise(r=>setTimeout(r,25));}
 const actual=await evaluate(`({badge:document.querySelector('#result .badge')?.textContent,quantityCount:document.querySelectorAll('#result .quantity').length,allQuantityBasis:[...document.querySelectorAll('#result .quantity')].every(n=>n.querySelector('.basis')?.textContent.includes('not validated')),unknownOrNonfiniteDisplayed:/NaN|Infinity/.test(document.querySelector('#result').textContent),sourceRowMislabel:/Measured data/.test(document.querySelector('#result').textContent),errors:document.querySelectorAll('#result .error').length})`);
 results.push({id:item.id,elapsed_ms:Math.round((performance.now()-started)*1000)/1000,...actual});
 if(actual.errors||actual.unknownOrNonfiniteDisplayed||actual.sourceRowMislabel||!actual.allQuantityBasis)throw new Error('UI failed '+item.id);
 if(item.id==='transform_heat'){const image=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});fs.writeFileSync(screenshot,Buffer.from(image.data,'base64'));}
}
// Planted output verifies that null endpoints are not coerced by the actual renderer.
const fixture={mode:'ABSTAIN',answer:'Synthetic missing-value regression',citable:false,detail:{recipe_display:{steps:[{action:'Synthetic null endpoint',badge:'Condition applicability unknown',explanation:'Synthetic control, not an observed recipe.',physics:{numbers:[],unavailable_paths:['scenario.range_core_end_c.1','scenario.typical_core_end_c']}}]}}};
await evaluate(`render(${JSON.stringify(fixture)});`);
const missing=await evaluate(`({quantityCount:document.querySelectorAll('#result .quantity').length,unknownNotice:document.querySelector('#result').textContent.includes('unknown provenance'),fabricatedZero:/0 degC|0 °C/.test(document.querySelector('#result').textContent)})`);
if(missing.quantityCount||!missing.unknownNotice||missing.fabricatedZero)throw new Error('Missing-value browser regression');
fs.writeFileSync(outFile,JSON.stringify({cases:results,planted_missing_value:missing,external_requests:external,status:'PASS'},null,2)+'\n');
ws.close();
