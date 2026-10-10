/* Public synthetic engineering example. No MRI model, private weights or research predictions. */
export const CONFIG = Object.freeze({version:'synthetic-logistic-v1', rows:480, groups:120, scanners:10, folds:5, features:20, targets:12, epochs:60, learningRate:0.18, regularization:0.002});
export const TARGETS = Array.from({length:CONFIG.targets},(_,i)=>`Target ${String(i+1).padStart(2,'0')}`);
const check=(ok,message)=>{if(!ok)throw new Error(message);};
const sigmoid=x=>x>=0?1/(1+Math.exp(-x)):Math.exp(x)/(1+Math.exp(x));
function rng(seed){let a=seed>>>0;return()=>{a+=0x6D2B79F5;let t=Math.imul(a^(a>>>15),1|a);t^=t+Math.imul(t^(t>>>7),61|t);return((t^(t>>>14))>>>0)/4294967296;};}
export function hash(text){let h=2166136261;for(let i=0;i<text.length;i++)h=Math.imul(h^text.charCodeAt(i),16777619);return(h>>>0).toString(16).padStart(8,'0');}
export function makeDataset(seed=2026){
 check(Number.isInteger(seed)&&seed>=1&&seed<=999999999,'Choose an integer seed from 1 to 999999999.');
 const random=rng(seed),normal=()=>Math.sqrt(-2*Math.log(Math.max(random(),1e-12)))*Math.cos(2*Math.PI*random());
 const truth=Array.from({length:CONFIG.targets},()=>Array.from({length:CONFIG.features},()=>normal()/Math.sqrt(CONFIG.features)));
 const rows=[];
 for(let group=0;group<CONFIG.groups;group++){
  const scanner=group%CONFIG.scanners,shared=Array.from({length:CONFIG.features},normal);
  for(let member=0;member<4;member++){
   const x=shared.map((v,j)=>0.55*v+normal()+0.18*Math.sin(scanner+j));
   const y=truth.map((w,t)=>Number(random()<sigmoid(2.1*w.reduce((s,v,j)=>s+v*x[j],0)+(t%3-1)*0.25)));
   rows.push({id:`synthetic-${group}-${member}`,group,scanner,fold:scanner%CONFIG.folds,x,y});
  }
 }
 return {seed,rows,signature:hash(JSON.stringify(rows)),evidence:'SYNTHETIC_ONLY'};
}
export function foldIndices(data,fold){check(Number.isInteger(fold)&&fold>=0&&fold<5,'Invalid fold.');const train=[],test=[];data.rows.forEach((r,i)=>(r.fold===fold?test:train).push(i));return{train,test};}
export function fitScaler(data,indices){
 check(indices.length>0,'Training rows are required.');
 const mean=Array(CONFIG.features).fill(0),scale=Array(CONFIG.features).fill(0);
 for(const i of indices)for(let j=0;j<CONFIG.features;j++)mean[j]+=data.rows[i].x[j]/indices.length;
 for(const i of indices)for(let j=0;j<CONFIG.features;j++)scale[j]+=(data.rows[i].x[j]-mean[j])**2/indices.length;
 for(let j=0;j<CONFIG.features;j++)scale[j]=Math.max(Math.sqrt(scale[j]),1e-8);
 return{mean,scale};
}
export function auc(labels,scores){
 check(labels.length===scores.length&&labels.length>0,'AUC inputs must align.');
 const sorted=scores.map((p,i)=>{check(Number.isFinite(p)&&(labels[i]===0||labels[i]===1),'Invalid AUC input.');return{p,y:labels[i]};}).sort((a,b)=>a.p-b.p);
 const positives=labels.reduce((a,b)=>a+b,0),negatives=labels.length-positives;check(positives>0&&negatives>0,'AUC needs both classes.');
 let sum=0;
 for(let i=0;i<sorted.length;){let end=i+1;while(end<sorted.length&&sorted[end].p===sorted[i].p)end++;for(let k=i;k<end;k++)if(sorted[k].y)sum+=(i+1+end)/2;i=end;}
 return(sum-positives*(positives+1)/2)/(positives*negatives);
}
export function roc(labels,scores){
 const positives=labels.reduce((a,b)=>a+b,0),negatives=labels.length-positives;if(!positives||!negatives)return[[0,0],[1,1]];
 const sorted=scores.map((p,i)=>({p,y:labels[i]})).sort((a,b)=>b.p-a.p),points=[[0,0]];let tp=0,fp=0;
 for(let i=0;i<sorted.length;){let end=i;while(end<sorted.length&&sorted[end].p===sorted[i].p){if(sorted[end].y)tp++;else fp++;end++;}points.push([fp/negatives,tp/positives]);i=end;}
 return points;
}
export function createExperiment(seed=2026){const data=makeDataset(seed);return{data,seed,fold:0,epoch:0,weights:null,scaler:null,loss:null,lossHistory:[],summaries:[],probabilities:Array.from({length:CONFIG.rows},()=>null)};}
const vector=(row,scaler)=>[1,...row.x.map((v,j)=>(v-scaler.mean[j])/scaler.scale[j])];
export function predict(row,scaler,weights){const x=vector(row,scaler);return weights.map(w=>sigmoid(w.reduce((s,v,j)=>s+v*x[j],0)));}
export function step(state){
 if(state.fold===CONFIG.folds)return{done:true,committed:false};
 const {train,test}=foldIndices(state.data,state.fold);
 if(!state.weights){state.scaler=fitScaler(state.data,train);state.weights=Array.from({length:CONFIG.targets},()=>Array(CONFIG.features+1).fill(0));}
 const gradient=state.weights.map(w=>w.map(()=>0));let loss=0;
 for(const i of train){const row=state.data.rows[i],x=vector(row,state.scaler);
  for(let t=0;t<CONFIG.targets;t++){const p=sigmoid(state.weights[t].reduce((s,v,j)=>s+v*x[j],0)),error=p-row.y[t];loss-=row.y[t]*Math.log(Math.max(p,1e-12))+(1-row.y[t])*Math.log(Math.max(1-p,1e-12));for(let j=0;j<x.length;j++)gradient[t][j]+=error*x[j]/train.length;}
 }
 for(let t=0;t<CONFIG.targets;t++)for(let j=0;j<=CONFIG.features;j++)state.weights[t][j]-=CONFIG.learningRate*(gradient[t][j]+(j?CONFIG.regularization*state.weights[t][j]:0));
 state.epoch++;state.loss=loss/train.length/CONFIG.targets;state.lossHistory.push(state.loss);
 let committed=false;
 if(state.epoch===CONFIG.epochs){
  for(const i of test)state.probabilities[i]=predict(state.data.rows[i],state.scaler,state.weights);
  const perTarget=TARGETS.map((_,t)=>auc(test.map(i=>state.data.rows[i].y[t]),test.map(i=>state.probabilities[i][t])));
  state.summaries.push({fold:state.fold,trainRows:train.length,testRows:test.length,macroAuc:perTarget.reduce((a,b)=>a+b,0)/CONFIG.targets,perTarget,finalTrainingLoss:state.loss,normalizationFitRows:train.length});
  state.fold++;state.epoch=0;state.weights=null;state.scaler=null;committed=true;
 }
 return{done:state.fold===CONFIG.folds,committed};
}
export function metrics(state){
 const indices=state.probabilities.flatMap((p,i)=>p?[i]:[]);if(!indices.length)return{rows:0,macroAuc:null,perTarget:[]};
 const perTarget=TARGETS.map((_,t)=>auc(indices.map(i=>state.data.rows[i].y[t]),indices.map(i=>state.probabilities[i][t])));
 return{rows:indices.length,macroAuc:perTarget.reduce((a,b)=>a+b,0)/CONFIG.targets,perTarget};
}
function payload(state){return{version:CONFIG.version,implementation:ENGINE_SIGNATURE,config:CONFIG,seed:state.seed,datasetSignature:state.data.signature,fold:state.fold,epoch:state.epoch,weights:state.weights,scaler:state.scaler,loss:state.loss,lossHistory:state.lossHistory,summaries:state.summaries,probabilities:state.probabilities};}
export function snapshot(state){const body=JSON.stringify(payload(state));return JSON.stringify({body,checksum:hash(body)});}
export function restore(raw){
 check(typeof raw==='string'&&raw.length<1000000,'Checkpoint size is invalid.');const envelope=JSON.parse(raw);check(typeof envelope.body==='string'&&hash(envelope.body)===envelope.checksum,'Checkpoint checksum mismatch.');
 const p=JSON.parse(envelope.body);check(p.version===CONFIG.version&&p.implementation===ENGINE_SIGNATURE&&JSON.stringify(p.config)===JSON.stringify(CONFIG),'Checkpoint belongs to a different engine implementation or configuration.');
 const state=createExperiment(p.seed);check(p.datasetSignature===state.data.signature,'Synthetic input fingerprint mismatch.');
 check(Number.isInteger(p.fold)&&p.fold>=0&&p.fold<=5&&Number.isInteger(p.epoch)&&p.epoch>=0&&p.epoch<CONFIG.epochs&&(p.fold<5||p.epoch===0),'Invalid checkpoint progress.');
 const finiteArray=(a,n)=>Array.isArray(a)&&a.length===n&&a.every(Number.isFinite);
 check(Array.isArray(p.probabilities)&&p.probabilities.length===CONFIG.rows,'Invalid prediction checkpoint.');
 p.probabilities.forEach((a,i)=>check(state.data.rows[i].fold<p.fold?finiteArray(a,12)&&a.every(v=>v>=0&&v<=1):a===null,'Checkpoint prediction membership mismatch.'));
 check(Array.isArray(p.lossHistory)&&p.lossHistory.length===p.fold*CONFIG.epochs+p.epoch&&p.lossHistory.every(v=>Number.isFinite(v)&&v>=0),'Invalid training history.');
 check(Array.isArray(p.summaries)&&p.summaries.length===p.fold,'Invalid completed folds.');
 p.summaries.forEach((s,i)=>check(s.fold===i&&s.trainRows===384&&s.testRows===96&&s.normalizationFitRows===384&&finiteArray(s.perTarget,12)&&s.perTarget.every(v=>v>=0&&v<=1)&&s.macroAuc===s.perTarget.reduce((a,b)=>a+b,0)/CONFIG.targets&&s.finalTrainingLoss===p.lossHistory[(i+1)*CONFIG.epochs-1],'Invalid fold summary.'));
 if(p.epoch>0)check(Array.isArray(p.weights)&&p.weights.length===12&&p.weights.every(w=>finiteArray(w,21))&&p.scaler&&finiteArray(p.scaler.mean,20)&&finiteArray(p.scaler.scale,20)&&p.scaler.scale.every(v=>v>0),'Invalid active fold state.');
 else check(p.weights===null&&p.scaler===null,'Unexpected active fold state.');
 if(p.epoch>0)check(JSON.stringify(p.scaler)===JSON.stringify(fitScaler(state.data,foldIndices(state.data,p.fold).train)),'Checkpoint normalization differs from training-only fit.');
 p.summaries.forEach((summary,fold)=>{const test=foldIndices(state.data,fold).test;const scores=TARGETS.map((_,t)=>auc(test.map(i=>state.data.rows[i].y[t]),test.map(i=>p.probabilities[i][t])));check(JSON.stringify(scores)===JSON.stringify(summary.perTarget),'Checkpoint evaluation differs from saved predictions.');});
 check(p.loss===null&&p.lossHistory.length===0||Number.isFinite(p.loss)&&p.loss===p.lossHistory.at(-1),'Invalid loss checkpoint.');
 for(const key of ['fold','epoch','weights','scaler','loss','lossHistory','summaries','probabilities'])state[key]=p[key];
 return state;
}
export function result(state){return{evidence:'SYNTHETIC_ONLY',purpose:'Generic tabular ML engineering demonstration; not MRI inference or a scientific reproduction.',status:state.fold===5?'COMPLETE':'PARTIAL',implementation:ENGINE_SIGNATURE,configuration:CONFIG,seed:state.seed,datasetSignature:state.data.signature,completedFolds:state.fold,completedEpochs:state.fold*CONFIG.epochs+state.epoch,metrics:metrics(state),folds:state.summaries,predictions:state.data.rows.flatMap((row,i)=>state.probabilities[i]?[{syntheticId:row.id,fold:row.fold,labels:row.y,probabilities:state.probabilities[i]}]:[])};}

// A corruption/compatibility fingerprint, not a security signature. Changes to the
// numerical recipe invalidate previous weights even when CONFIG is unchanged.
export const ENGINE_SIGNATURE = hash(JSON.stringify(CONFIG) + [rng,sigmoid,makeDataset,foldIndices,fitScaler,createExperiment,vector,predict,step,auc,roc,metrics].map(fn=>fn.toString()).join('\n'));
