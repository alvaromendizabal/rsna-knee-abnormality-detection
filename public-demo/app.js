import {CONFIG, TARGETS, createExperiment, step, metrics, roc, snapshot, restore, result} from './engine.js';

const $ = id => document.getElementById(id);
const STORAGE_KEY = `rsna-public-demo:${CONFIG.version}`;
const svgNS = 'http://www.w3.org/2000/svg';
let experiment = createExperiment();
let stableCheckpoint = snapshot(experiment);
let running = false;
let frame = null;
let blockedCheckpoint = false;
let selectedFold = 0;
let notes = [];
let evaluation = metrics(experiment);

function note(message) {
  notes = [message, ...notes].slice(0, 6);
  $('log').replaceChildren(...notes.map(message => {
    const p = document.createElement('p');
    const dot = document.createElement('span');
    dot.className = 'log-dot';
    p.append(dot, document.createTextNode(message));
    return p;
  }));
}

function saveCheckpoint() {
  stableCheckpoint = snapshot(experiment);
  try {
    localStorage.setItem(STORAGE_KEY, stableCheckpoint);
    $('storage-note').textContent = 'Saved on this device every 10 epochs, on pause and after each fold. Reload to recover.';
  } catch {
    $('storage-note').textContent = 'Browser storage is unavailable. Training works, but this session cannot survive a reload.';
  }
}

function element(tag, attributes, text) {
  const node = document.createElementNS(svgNS, tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, String(value));
  if (text !== undefined) {
    node.textContent = text;
    if (tag === 'text') {
      node.setAttribute('font-size', 'inherit');
      node.setAttribute('fill', '#53636d');
    }
  }
  return node;
}

function scaleChartLabels(svg, viewWidth) {
  const width = svg.getBoundingClientRect?.().width;
  // SVG coordinates shrink on narrow displays. Preserve 12px rendered labels.
  const fontSize = width > 0 ? Math.max(12, 12 * viewWidth / width) : 12;
  svg.style.fontSize = `${fontSize}px`;
  return fontSize;
}

function renderPlots() {
  const target = Number($('target').value);
  const evaluated = experiment.data.rows.flatMap((row, i) => experiment.probabilities[i] ? [i] : []);
  const labels = evaluated.map(i => experiment.data.rows[i].y[target]);
  const probabilities = evaluated.map(i => experiment.probabilities[i][target]);
  const chart = $('roc');
  const chartFont = scaleChartLabels(chart, 600);
  chart.replaceChildren();
  const leftMargin = Math.max(47, chartFont * 3.7);
  const topMargin = Math.max(18, chartFont);
  const box = {left:leftMargin, top:topMargin, width:600-leftMargin-Math.max(20,chartFont*1.4), height:335-topMargin-chartFont*3.6};
  for (let tick = 0; tick <= 5; tick++) {
    const value = tick / 5;
    const x = box.left + value * box.width;
    const y = box.top + (1 - value) * box.height;
    chart.append(element('line', {x1:box.left, y1:y, x2:box.left + box.width, y2:y, stroke:'#e8ece6'}));
    chart.append(element('text', {x:box.left - 9, y:y + 3, 'text-anchor':'end'}, value.toFixed(1)));
    chart.append(element('text', {x, y:box.top + box.height + chartFont * 1.5, 'text-anchor':'middle'}, value.toFixed(1)));
  }
  chart.append(element('line', {x1:box.left, y1:box.top + box.height, x2:box.left + box.width, y2:box.top, stroke:'#b7c3bd', 'stroke-dasharray':'5 5'}));
  chart.append(element('text', {x:box.left + box.width / 2, y:334-chartFont*.4, 'text-anchor':'middle'}, 'False positive rate'));
  chart.append(element('text', {x:12, y:box.top + box.height / 2, transform:`rotate(-90 12 ${box.top + box.height / 2})`, 'text-anchor':'middle'}, 'True positive rate'));
  if (evaluated.length) {
    const points = roc(labels, probabilities);
    const path = points.map(([x,y],i) => `${i ? 'L' : 'M'}${(box.left+x*box.width).toFixed(2)},${(box.top+(1-y)*box.height).toFixed(2)}`).join(' ');
    chart.append(element('path', {d:`${path} L${box.left+box.width},${box.top+box.height} Z`, fill:'#e5f2ed', opacity:'.65'}));
    chart.append(element('path', {d:path, fill:'none', stroke:'#087d72', 'stroke-width':'2.5', 'stroke-linejoin':'round'}));
  }
  $('chart-empty').hidden = evaluated.length > 0;
  $('target-name').textContent = `${TARGETS[target]} AUC`;
  $('target-auc').textContent = evaluation.perTarget.length ? evaluation.perTarget[target].toFixed(4) : '—';
  chart.setAttribute('aria-label', evaluated.length ? `${TARGETS[target]} held-out ROC curve; AUC ${evaluation.perTarget[target].toFixed(4)} on ${evaluated.length} synthetic rows` : 'Empty ROC plot; run an experiment to produce held-out predictions');

  const histogram = $('distribution');
  const histogramFont = scaleChartLabels(histogram, 430);
  histogram.replaceChildren();
  const counts = [Array(20).fill(0), Array(20).fill(0)];
  probabilities.forEach((p,i) => counts[labels[i]][Math.min(19, Math.floor(p * 20))]++);
  const maximum = Math.max(1, ...counts.flat());
  const left = Math.max(25,histogramFont*2.2), top = Math.max(8,histogramFont);
  const width = 430-left-Math.max(15,histogramFont*1.2), height = 135-top-histogramFont*2;
  for (let i = 0; i <= 2; i++) {
    const y = top + height - height * i / 2;
    histogram.append(element('line', {x1:left, y1:y, x2:left + width, y2:y, stroke:'#edf0e9'}));
    if (evaluated.length) histogram.append(element('text', {x:left-5, y:y+3, 'text-anchor':'end'}, String(Math.round(maximum*i/2))));
    histogram.append(element('text', {x:left + width*i/2, y:128, 'text-anchor':'middle'}, (i/2).toFixed(1)));
  }
  for (let label = 0; label < 2; label++) {
    counts[label].forEach((count, i) => {
      if (!count) return;
      const barHeight = count / maximum * height;
      histogram.append(element('rect', {x:left+i*width/20+label*8.5+1, y:top+height-barHeight, width:8, height:barHeight, fill:label ? '#087d72' : '#7894ab', rx:1}));
    });
  }
  histogram.setAttribute('aria-label', evaluated.length ? `Probability counts by synthetic label for ${TARGETS[target]}, ${evaluated.length} held-out rows` : 'Empty probability distribution');
}

function renderFolds() {
  for (let fold = 0; fold < CONFIG.folds; fold++) {
    const button = $(`fold-${fold}`);
    button.className = ['fold-button', selectedFold === fold ? 'selected' : '', fold < experiment.fold ? 'done' : '', fold === experiment.fold && experiment.epoch > 0 ? 'active' : ''].filter(Boolean).join(' ');
    button.setAttribute('aria-pressed', String(selectedFold === fold));
    button.setAttribute('aria-label', `Fold ${fold+1}, ${fold < experiment.fold ? 'evaluated' : fold === experiment.fold && experiment.epoch ? 'training' : 'pending'}`);
  }
  const detail = $('fold-detail');
  const summary = experiment.summaries[selectedFold];
  const state = summary ? `Evaluated · macro AUC ${summary.macroAuc.toFixed(4)}` : selectedFold === experiment.fold && experiment.epoch ? `Training · epoch ${experiment.epoch} / ${CONFIG.epochs}` : 'Pending · no predictions yet';
  detail.innerHTML = `<strong>Fold ${selectedFold+1} · scanners ${selectedFold+1} &amp; ${selectedFold+6}</strong><div class="split-rule"><span></span></div><p>384 training rows &nbsp;/&nbsp; 96 held-out rows</p><p>${state}</p><p>No subject or scanner crosses this boundary.</p>`;
}

function renderProgress() {
  const epochs = experiment.fold * CONFIG.epochs + experiment.epoch;
  const complete = experiment.fold === CONFIG.folds;
  $('status').textContent = blockedCheckpoint ? 'CHECKPOINT ERROR' : running ? 'TRAINING' : complete ? 'COMPLETE' : epochs ? 'PAUSED' : 'READY';
  $('status').className = `status ${blockedCheckpoint ? 'error' : running ? 'running' : complete ? 'complete' : ''}`;
  $('run').disabled = running || complete || blockedCheckpoint;
  $('run').textContent = complete ? 'Experiment complete ✓' : epochs ? 'Resume experiment →' : 'Run experiment →';
  $('pause').disabled = !running;
  $('seed').disabled = running || epochs > 0 || blockedCheckpoint;
  $('export').disabled = !evaluation.rows;
  $('percent').textContent = `${Math.floor(epochs / (CONFIG.folds * CONFIG.epochs) * 100)}%`;
  $('progress-fill').style.width = `${epochs / (CONFIG.folds * CONFIG.epochs) * 100}%`;
  document.querySelector('.progress-track').setAttribute('aria-valuenow', String(epochs));
  $('progress-text').textContent = complete ? 'All five folds evaluated · 300 actual training epochs completed' : epochs || running ? `Fold ${experiment.fold+1} / 5 · epoch ${experiment.epoch} / 60 · ${epochs} total epochs${running ? '' : ' · paused'}` : 'Ready to train · normalization is fit separately within each fold';
  $('loss').textContent = experiment.loss === null ? 'Training loss: —' : `Training loss: ${experiment.loss.toFixed(4)} · synthetic BCE`;
  renderFolds();
}

function renderEvaluation() {
  evaluation = metrics(experiment);
  $('macro').textContent = evaluation.macroAuc === null ? '—' : evaluation.macroAuc.toFixed(4);
  $('metric-scope').textContent = !evaluation.rows ? 'Available after the first completed fold' : experiment.fold === CONFIG.folds ? 'All 480 held-out rows · synthetic data only' : `${evaluation.rows} held-out rows · partial evaluation`;
  $('rows').innerHTML = `${evaluation.rows} <span>/ 480</span>`;
  $('completed').innerHTML = `${experiment.fold} <span>/ 5</span>`;
  renderPlots();
}

function tick() {
  frame = null;
  if (!running) return;
  try {
    const update = step(experiment);
    if (experiment.epoch % 10 === 0 || update.committed) saveCheckpoint();
    if (update.committed) {
      const summary = experiment.summaries.at(-1);
      note(`Fold ${summary.fold+1} committed: 96 held-out rows, AUC ${summary.macroAuc.toFixed(4)}.`);
      renderEvaluation();
    }
    if (update.done) {
      running = false;
      note('Complete. All 480 predictions were made outside their training fold.');
    }
    renderProgress();
    if (running) frame = requestAnimationFrame(tick);
  } catch (error) {
    running = false;
    // step() may have mutated its state before failing; never persist that state.
    experiment = restore(stableCheckpoint);
    renderEvaluation();
    $('notice').textContent = `Execution stopped: ${error.message}. Recovered the previous checkpoint; resume or reset when ready.`;
    note(`Recovered the last successful checkpoint at ${experiment.lossHistory.length} epochs.`);
    renderProgress();
  }
}

$('run').addEventListener('click', () => {
  try {
    if (!experiment.lossHistory.length) {
      experiment = createExperiment(Number($('seed').value));
      stableCheckpoint = snapshot(experiment);
    }
    $('notice').textContent = '';
    running = true;
    note(experiment.lossHistory.length ? `Resumed at fold ${experiment.fold+1}, epoch ${experiment.epoch}.` : `Started seed ${experiment.seed}. All data is generated on this device.`);
    renderProgress();
    frame = requestAnimationFrame(tick);
  } catch (error) {
    $('notice').textContent = error.message;
  }
});
$('pause').addEventListener('click', () => {
  running = false;
  if (frame !== null) cancelAnimationFrame(frame);
  frame = null;
  saveCheckpoint();
  note(`Paused after ${experiment.lossHistory.length} completed epochs. Ready to resume.`);
  renderProgress();
});
$('reset').addEventListener('click', () => {
  running = false;
  if (frame !== null) cancelAnimationFrame(frame);
  frame = null;
  const seed = Number($('seed').value);
  try { experiment = createExperiment(seed); }
  catch { experiment = createExperiment(); }
  $('seed').value = String(experiment.seed);
  stableCheckpoint = snapshot(experiment);
  blockedCheckpoint = false;
  selectedFold = 0;
  try { localStorage.removeItem(STORAGE_KEY); } catch { /* Storage may be disabled. */ }
  $('notice').textContent = '';
  $('storage-note').textContent = 'Checkpoints stay in this browser. No data is sent anywhere.';
  notes = [];
  note('Reset complete. Change the seed or start a fresh experiment.');
  renderEvaluation();
  renderProgress();
});
$('export').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify(result(experiment), null, 2)], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `synthetic-experiment-seed-${experiment.seed}.json`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  note(`Exported ${evaluation.rows} held-out rows as synthetic JSON.`);
});
$('target').replaceChildren(...TARGETS.map((name, i) => {
  const option = document.createElement('option');
  option.value = String(i);
  option.textContent = name;
  return option;
}));
$('target').addEventListener('change', renderPlots);
for (let fold = 0; fold < CONFIG.folds; fold++) {
  const button = document.createElement('button');
  button.id = `fold-${fold}`;
  button.textContent = String(fold+1).padStart(2,'0');
  button.addEventListener('click', () => { selectedFold = fold; renderFolds(); });
  $('folds').append(button);
}
let stored = null;
try { stored = localStorage.getItem(STORAGE_KEY); }
catch { $('storage-note').textContent = 'Browser storage is unavailable. Training works, but this session cannot survive a reload.'; }
if (stored) {
  try {
    experiment = restore(stored);
    stableCheckpoint = stored;
    $('seed').value = String(experiment.seed);
    selectedFold = Math.min(experiment.fold, CONFIG.folds-1);
    note(`Recovered a verified local checkpoint: ${experiment.lossHistory.length} epochs, ${experiment.fold} evaluated folds.`);
    $('storage-note').textContent = 'Local checkpoint recovered. Resume uses the saved weights and training progress.';
  } catch {
    blockedCheckpoint = true;
    $('notice').textContent = 'The stored checkpoint could not be read or verified. Reset the experiment to start fresh.';
  }
}
window.addEventListener('resize', renderPlots);
window.addEventListener('beforeunload', () => { if (!blockedCheckpoint && experiment.lossHistory.length) saveCheckpoint(); });
renderEvaluation();
renderProgress();
