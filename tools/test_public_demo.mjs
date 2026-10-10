/** Dependency-free checks of the public synthetic engine and actual UI handlers. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = fs.readFileSync(path.join(root, 'public-demo/engine.js'), 'utf8');
const engineURL = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
const E = await import(engineURL);
let count = 0;
async function test(name, fn) { await fn(); count++; console.log(`ok ${count} - ${name}`); }
const advance = (state, n) => { for (let i=0; i<n; i++) E.step(state); return state; };
const finish = state => { while(state.fold < E.CONFIG.folds) E.step(state); return state; };
const reEnvelope = (raw, change) => {const p=JSON.parse(JSON.parse(raw).body);change(p);const body=JSON.stringify(p);return JSON.stringify({body,checksum:E.hash(body)});};
const dataset = E.makeDataset();
let full;

await test('seeded synthetic inputs are reproducible and seed-sensitive', () => {
  assert.deepEqual(dataset,E.makeDataset(2026));
  assert.notEqual(dataset.signature,E.makeDataset(2027).signature);
  assert.equal(dataset.evidence,'SYNTHETIC_ONLY');
  assert.throws(()=>E.makeDataset(0)); assert.throws(()=>E.makeDataset(1.5));
});
await test('five folds isolate every scanner and nested subject group', () => {
  const held = [];
  for(let fold=0;fold<5;fold++) {
    const {train,test} = E.foldIndices(dataset,fold);
    assert.equal(train.length,384); assert.equal(test.length,96);
    for(const key of ['scanner','group']) {
      const training = new Set(train.map(i=>dataset.rows[i][key]));
      assert.ok(test.every(i=>!training.has(dataset.rows[i][key])));
    }
    held.push(...test);
  }
  assert.equal(new Set(held).size,480); assert.equal(held.length,480);
});
await test('normalization uses training rows only', () => {
  const {train,test} = E.foldIndices(dataset,0);
  const changed = structuredClone(dataset);
  test.forEach(i=>changed.rows[i].x.fill(1e9));
  assert.deepEqual(E.fitScaler(dataset,train),E.fitScaler(changed,train));
  const mean = train.reduce((s,i)=>s+dataset.rows[i].x[0]/train.length,0);
  assert.equal(E.fitScaler(dataset,train).mean[0],mean);
});
await test('held-out features and labels cannot change active-fold learning', () => {
  const a=E.createExperiment(),b=E.createExperiment();
  E.foldIndices(b.data,0).test.forEach(i=>{b.data.rows[i].x.fill(1e6);b.data.rows[i].y.fill(0);});
  advance(a,17); advance(b,17);
  assert.deepEqual(a.weights,b.weights); assert.deepEqual(a.scaler,b.scaler);
  assert.deepEqual(a.lossHistory,b.lossHistory);
});
await test('AUC implements average ties and known ranking examples', () => {
  assert.equal(E.auc([0,1,0,1],[.5,.5,.5,.5]),.5);
  assert.equal(E.auc([0,0,1,1],[.1,.2,.8,.9]),1);
  assert.equal(E.auc([0,0,1,1],[.8,.9,.1,.2]),0);
  assert.equal(E.auc([0,0,1,1],[.1,.4,.35,.8]),.75);
  assert.throws(()=>E.auc([1,1],[.2,.3]));
  assert.throws(()=>E.auc([0,1],[NaN,.3]));
});
await test('ROC groups tied thresholds and stays monotone', () => {
  assert.deepEqual(E.roc([0,1],[.5,.5]),[[0,0],[1,1]]);
  const points=E.roc([0,1,0,1],[.1,.8,.4,.6]);
  assert.deepEqual(points.at(-1),[1,1]);
  points.slice(1).forEach((p,i)=>assert.ok(p[0]>=points[i][0]&&p[1]>=points[i][1]));
});
await test('predictions appear only after a full fold and only for held-out rows', () => {
  const state=advance(E.createExperiment(),59);
  assert.equal(E.metrics(state).rows,0); assert.ok(state.probabilities.every(p=>p===null));
  const update=E.step(state); assert.equal(update.committed,true);
  assert.equal(E.metrics(state).rows,96);
  state.probabilities.forEach((p,i)=>assert.equal(p!==null,state.data.rows[i].fold===0));
});
await test('all five trained folds yield bounded probabilities and evaluated evidence', () => {
  full=finish(E.createExperiment());
  assert.equal(full.lossHistory.length,300);
  assert.equal(E.metrics(full).rows,480);
  assert.ok(full.probabilities.every(p=>p.length===12&&p.every(v=>Number.isFinite(v)&&v>0&&v<1)));
  for(let fold=0;fold<5;fold++) assert.ok(full.lossHistory[fold*60+59]<full.lossHistory[fold*60]);
  assert.ok(E.metrics(full).macroAuc>.5&&E.metrics(full).macroAuc<1);
  assert.equal(E.result(full).evidence,'SYNTHETIC_ONLY');
  assert.equal(E.result(full).status,'COMPLETE');
});
await test('mid-fold checkpoint resumes to exactly the uninterrupted result', () => {
  const partial=advance(E.createExperiment(),77);
  assert.equal(E.result(partial).status,'PARTIAL');
  const resumed=finish(E.restore(E.snapshot(partial)));
  assert.deepEqual(E.result(resumed),E.result(full));
  assert.deepEqual(resumed.lossHistory,full.lossHistory);
});
await test('fold-boundary and completed checkpoints are stable', () => {
  const boundary=advance(E.createExperiment(),60);
  assert.deepEqual(E.result(finish(E.restore(E.snapshot(boundary)))),E.result(full));
  const complete=E.restore(E.snapshot(full)),before=E.snapshot(complete);
  assert.deepEqual(E.step(complete),{done:true,committed:false});
  assert.equal(E.snapshot(complete),before);
});
await test('corruption, incompatible configuration and recipe changes reject resume', async () => {
  const raw=E.snapshot(advance(E.createExperiment(),7));
  assert.throws(()=>E.restore(raw.replace('checksum','wrong')));
  assert.throws(()=>E.restore(reEnvelope(raw,p=>p.config.epochs=61)));
  assert.throws(()=>E.restore(reEnvelope(raw,p=>p.implementation='different')));
  const changed = source.replace('const gradient=state.weights.map','const recipeChanged=true; const gradient=state.weights.map');
  const alternate=await import(`data:text/javascript;base64,${Buffer.from(changed).toString('base64')}`);
  assert.notEqual(alternate.ENGINE_SIGNATURE,E.ENGINE_SIGNATURE);
  assert.throws(()=>alternate.restore(raw));
});
await test('checkpoint schema rejects leaked membership and altered normalization', () => {
  const raw=E.snapshot(advance(E.createExperiment(),7));
  assert.throws(()=>E.restore(reEnvelope(raw,p=>p.probabilities[0]=Array(12).fill(.5))));
  assert.throws(()=>E.restore(reEnvelope(raw,p=>p.scaler.mean[0]+=1)));
  assert.throws(()=>E.restore(reEnvelope(raw,p=>p.weights[0][0]=null)));
  assert.throws(()=>E.restore(reEnvelope(raw,p=>p.lossHistory.pop())));
});
await test('checkpoint metrics must agree with committed predictions', () => {
  const raw=E.snapshot(full);
  assert.throws(()=>E.restore(reEnvelope(raw,p=>p.summaries[0].macroAuc=9.9)));
  assert.throws(()=>E.restore(reEnvelope(raw,p=>p.summaries[0].normalizationFitRows=480)));
  assert.throws(()=>E.restore(reEnvelope(raw,p=>p.summaries[0].perTarget[0]=.1)));
});

// A deliberately small DOM harness executes the actual app module, event handlers,
// rendering and animation-frame loop. It is not a browser layout/accessibility test.
const html=fs.readFileSync(path.join(root,'public-demo/index.html'),'utf8');
const appSource=fs.readFileSync(path.join(root,'public-demo/app.js'),'utf8');
let loadNumber=0;
async function browser({checkpoint=null,storageDenied=false,throwAfterMutation=false}={}) {
  const nodes=new Map(),frames=new Map(),storage=new Map();let nextFrame=0,download=null;
  if(checkpoint)storage.set(`rsna-public-demo:${E.CONFIG.version}`,checkpoint);
  class Element {
    constructor(tag='div'){this.tag=tag;this.children=[];this.handlers={};this.attributes={};this.style={};this.disabled=false;this.value='';this.textContent='';this.innerHTML='';this.hidden=false;}
    set id(id){this._id=id;nodes.set(id,this);}get id(){return this._id;}
    setAttribute(key,value){this.attributes[key]=value;}
    append(...children){this.children.push(...children);}
    replaceChildren(...children){this.children=children;if(this.tag==='select')this.value=children[0]?.value||'';}
    addEventListener(name,fn){this.handlers[name]=fn;}
    click(){if(!this.disabled)this.handlers.click?.();if(this.download)download=this;}
  }
  for(const match of html.matchAll(/<([a-z]+)[^>]*\bid="([^"]+)"[^>]*>/g)){const node=new Element(match[1]);node.id=match[2];}
  nodes.get('seed').value='2026';
  const progress=new Element();
  globalThis.document={getElementById:id=>nodes.get(id),querySelector:selector=>selector==='.progress-track'?progress:null,createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag),createTextNode:text=>text};
  globalThis.window={addEventListener(){}};
  globalThis.localStorage={getItem:key=>{if(storageDenied)throw new Error('blocked');return storage.get(key)||null;},setItem:(key,value)=>{if(storageDenied)throw new Error('blocked');storage.set(key,value);},removeItem:key=>storage.delete(key)};
  globalThis.requestAnimationFrame=fn=>{const id=++nextFrame;frames.set(id,fn);return id;};
  globalThis.cancelAnimationFrame=id=>frames.delete(id);
  let exported=null;
  const originalCreate=URL.createObjectURL,originalRevoke=URL.revokeObjectURL;
  URL.createObjectURL=blob=>{exported=blob;return 'blob:synthetic-test';};
  URL.revokeObjectURL=()=>{};
  let moduleSource=appSource.replace("'./engine.js'",JSON.stringify(engineURL));
  if(throwAfterMutation)moduleSource=moduleSource.replace('createExperiment, step,','createExperiment, step as realStep,').replace("const $ = id", "const step = state => { if(state.lossHistory.length===11){state.epoch=60;state.weights=null;throw new Error('injected mutation failure');} return realStep(state); };\nconst $ = id");
  await import(`data:text/javascript;base64,${Buffer.from(moduleSource).toString('base64')}#${++loadNumber}`);
  return {nodes,storage,progress,frames,get exported(){return exported;},get download(){return download;},restoreURL(){URL.createObjectURL=originalCreate;URL.revokeObjectURL=originalRevoke;},flush(n){for(let i=0;i<n&&frames.size;i++){const [id,fn]=frames.entries().next().value;frames.delete(id);fn();}}};
}
let saved;
await test('actual UI starts, advances real epochs, pauses and writes its checkpoint', async () => {
  const b=await browser();
  assert.equal(b.nodes.get('macro').textContent,'—');assert.equal(b.nodes.get('export').disabled,true);
  b.nodes.get('run').click();b.flush(17);b.nodes.get('pause').click();
  assert.equal(b.nodes.get('status').textContent,'PAUSED');assert.equal(b.frames.size,0);
  saved=b.storage.values().next().value;
  assert.equal(E.restore(saved).epoch,17);
  assert.equal(b.progress.attributes['aria-valuenow'],'17');b.restoreURL();
});
await test('actual UI recovers, completes, inspects targets and exports real JSON', async () => {
  const b=await browser({checkpoint:saved});
  assert.equal(b.nodes.get('status').textContent,'PAUSED');
  b.nodes.get('run').click();b.flush(400);
  assert.equal(b.nodes.get('status').textContent,'COMPLETE');assert.equal(b.progress.attributes['aria-valuenow'],'300');
  assert.equal(b.nodes.get('macro').textContent,E.metrics(full).macroAuc.toFixed(4));
  b.nodes.get('target').value='4';b.nodes.get('target').handlers.change();
  assert.equal(b.nodes.get('target-auc').textContent,E.metrics(full).perTarget[4].toFixed(4));
  b.nodes.get('fold-3').click();assert.equal(b.nodes.get('fold-3').attributes['aria-pressed'],'true');
  b.nodes.get('export').click();
  assert.deepEqual(JSON.parse(await b.exported.text()),E.result(full));
  assert.equal(b.download.download,'synthetic-experiment-seed-2026.json');b.restoreURL();
});
await test('actual UI rolls back a failed mutated step without overwriting its good checkpoint', async () => {
  const b=await browser({throwAfterMutation:true});b.nodes.get('run').click();b.flush(10);
  const good=b.storage.values().next().value;b.flush(5);
  assert.equal(b.storage.values().next().value,good);
  assert.equal(E.restore(good).epoch,10);
  assert.equal(b.frames.size,0);
  assert.equal(b.progress.attributes['aria-valuenow'],'10');
  assert.match(b.nodes.get('notice').textContent,/Recovered the previous checkpoint/);b.restoreURL();
});
await test('actual UI reset cancels running work and permits a different seed', async () => {
  const b=await browser();b.nodes.get('run').click();b.flush(5);b.nodes.get('reset').click();
  assert.equal(b.frames.size,0);assert.equal(b.nodes.get('seed').disabled,false);
  b.nodes.get('seed').value='2027';b.nodes.get('run').click();b.flush(10);b.nodes.get('pause').click();
  assert.equal(E.restore(b.storage.values().next().value).seed,2027);b.restoreURL();
});
await test('actual UI blocks invalid checkpoints until explicit reset', async () => {
  const b=await browser({checkpoint:'corrupted'});
  assert.equal(b.nodes.get('run').disabled,true);assert.equal(b.nodes.get('status').textContent,'CHECKPOINT ERROR');
  b.nodes.get('reset').click();assert.equal(b.nodes.get('run').disabled,false);assert.equal(b.storage.size,0);b.restoreURL();
});
await test('actual UI remains runnable when browser storage is denied', async () => {
  const b=await browser({storageDenied:true});assert.equal(b.nodes.get('run').disabled,false);
  b.nodes.get('run').click();b.flush(10);b.nodes.get('pause').click();
  assert.equal(b.nodes.get('status').textContent,'PAUSED');assert.match(b.nodes.get('storage-note').textContent,/unavailable/);b.restoreURL();
});
await test('public UI uses only local assets and labels its synthetic scope', () => {
  assert.ok(html.includes('SYNTHETIC_ONLY'));assert.ok(html.includes('not an MRI classifier'));
  for(const match of html.matchAll(/<(?:script|link)\b[^>]*(?:src|href)="([^"]+)"/g))assert.ok(['styles.css','app.js','https://alvaro-rsna-engineering-lab.tartmacaw2.chatgpt.site/'].includes(match[1]));
  assert.ok(!/\b(?:fetch|XMLHttpRequest|WebSocket)\s*\(/.test(source+appSource));
});
console.log(`\n${count} public demo checks passed. Synthetic macro AUC: ${E.metrics(full).macroAuc.toFixed(8)} (not medical performance).`);
