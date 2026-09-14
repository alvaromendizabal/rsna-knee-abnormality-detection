"""Every figure: native Plotly + separate PNG from the SAME aggregate series.

PNG companions use Matplotlib's Agg backend, not a screenshot or Kaleido export.
No browser, browser install, CDN, or Javascript renderer is needed for the PNG.
"""
from __future__ import annotations
import io, json, math
from pathlib import Path
from common import ROOT,WORK,LABELS,STATES,ARMS,Stop,sha,digest,atomic,save_json,read_json,utc

TITLES=[
 'Study allocation - expert outcomes remain sealed',
 'Distinct report groups in the frozen five-fold assignment',
 'Unicode script presence in sampled training reports - not language identity',
 'Joint-context supervision candidates - six distinct states',
 'Mention-only versus joint context - positive-candidate counts',
 'Negation ablation - changes relative to the joint pipeline',
 'Uncertainty ablation - changes relative to the joint pipeline',
 'Section and history ablation - changes relative to the joint pipeline',
 'Explicit negative candidates by finding',
 'Conflicting assertion candidates by finding',
 'Abstention by finding - uncertainty is not a negative label',
 'Shared binary-evidence coverage - not disease co-occurrence',
]
CAPTIONS=[
 'These are availability-based splits, not disease prevalence or verified patient groups.',
 'Fold zero is reserved for later development checks; the candidate pilot uses folds 1-4 only.',
 'One report can contain multiple scripts; Latin script does not establish English-language support.',
 'Candidate state counts are not clinical labels. English lexical scope has not been adjudicated.',
 'Both methods see the same sampled reports. A reduction in positives does not establish accuracy.',
 'Removing a block from the full pipeline tests its conditional effect on assignments, not AUC.',
 'Uncertain findings remain masked under the joint pipeline; no numeric probability is assigned.',
 'The joint context gate separates clinical history, indications and postoperative context from current findings.',
 'Absence requires explicit negative evidence. Unmentioned findings are never silently converted to zero.',
 'Conflicting positive and negative evidence is retained as conflict, not resolved by a guessed priority.',
 'All nonbinary states are abstentions. No candidate target is approved for image-model training.',
 'This matrix describes where reports contain binary assertions for both findings, not their diagnoses.',
]

def specification(summary,index):
    if not 1<=index<=12:raise Stop('FIGURE_INDEX')
    c=summary['counts'];joint=c['joint_context']
    def vec(arm,state):return [c[arm][l][state] for l in LABELS]
    spec={'title':TITLES[index-1],'caption':CAPTIONS[index-1],'number':index}
    if index==1:spec.update(kind='bar',labels=list(summary['split_counts']),series={'Studies':list(summary['split_counts'].values())},ylabel='Study count')
    elif index==2:spec.update(kind='bar',labels=['Fold '+k for k in summary['fold_groups']],series={'Report groups':list(summary['fold_groups'].values())},ylabel='Distinct normalized-report groups')
    elif index==3:spec.update(kind='bar',labels=list(summary['scripts']),series={'Reports':list(summary['scripts'].values())},ylabel='Reports containing this script')
    elif index==4:spec.update(kind='heatmap',x=STATES,y=LABELS,z=[[joint[l][s] for s in STATES] for l in LABELS],ylabel='Finding',xlabel='Candidate assertion state',unit='Count')
    elif index==5:spec.update(kind='bar',labels=LABELS,series={'Mention only':vec('mention_only','positive'),'Joint context':vec('joint_context','positive')},ylabel='Positive-candidate count')
    elif index in (6,7,8):
        arm={6:'joint_no_negation',7:'joint_no_uncertainty',8:'joint_no_context_gate'}[index]
        spec.update(kind='bar',labels=LABELS,series={'Changed state':list(summary['disagreement_with_joint'][arm][l] for l in LABELS),
             'Positive-count change':[c[arm][l]['positive']-joint[l]['positive'] for l in LABELS]},ylabel='Candidate cells or count change')
    elif index==9:spec.update(kind='bar',labels=LABELS,series={'Explicit negatives':vec('joint_context','negative')},ylabel='Negative-candidate count')
    elif index==10:spec.update(kind='bar',labels=LABELS,series={'Conflicts':vec('joint_context','conflict')},ylabel='Conflicting-candidate count')
    elif index==11:spec.update(kind='bar',labels=LABELS,series={s:vec('joint_context',s) for s in ['uncertain','conflict','context_only','unmentioned']},ylabel='Abstention count')
    else:
        z=[[summary['binary_evidence_jaccard'][i][j] if summary['binary_evidence_union'][i][j] else None for j in range(12)] for i in range(12)]
        spec.update(kind='heatmap',x=LABELS,y=LABELS,z=z,ylabel='Finding',xlabel='Finding',unit='Jaccard coverage; blank = undefined')
    return spec

def build(spec):
    import numpy as np
    import plotly.graph_objects as go
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    # Each companion is one plot, never an array of cramped subplots.
    figure=Figure(figsize=(12,7));FigureCanvasAgg(figure);axis=figure.add_subplot(111)
    plot=go.Figure()
    if spec['kind']=='bar':
        labels=spec['labels'];keys=list(spec['series']);pos=np.arange(len(labels));width=.8/max(len(keys),1)
        for j,name in enumerate(keys):
            values=spec['series'][name]
            plot.add_trace(go.Bar(name=name,x=labels,y=values))
            axis.bar(pos-.4+width*(j+.5),values,width=width,label=name)
        axis.set_xticks(pos);axis.set_xticklabels(labels,rotation=40,ha='right');axis.set_ylabel(spec['ylabel'])
        axis.legend(loc='best',fontsize=9);axis.axhline(0,linewidth=.7)
        plot.update_layout(barmode='group',yaxis_title=spec['ylabel'])
    else:
        z=np.asarray([[np.nan if v is None else v for v in row] for row in spec['z']],dtype=float)
        img=axis.imshow(z,aspect='auto');figure.colorbar(img,ax=axis,label=spec['unit'])
        axis.set_xticks(range(len(spec['x'])));axis.set_xticklabels(spec['x'],rotation=40,ha='right')
        axis.set_yticks(range(len(spec['y'])));axis.set_yticklabels(spec['y'])
        axis.set_ylabel(spec['ylabel']);axis.set_xlabel(spec['xlabel'])
        plot.add_trace(go.Heatmap(x=spec['x'],y=spec['y'],z=spec['z'],colorbar={'title':spec['unit']}))
        plot.update_layout(xaxis_title=spec['xlabel'],yaxis_title=spec['ylabel'])
    axis.set_title(spec['title'],fontsize=13,pad=15);figure.tight_layout()
    plot.update_layout(title=spec['title'],height=580,margin={'b':140,'l':100},
                       meta={'numeric_spec_sha256':digest(spec),'role':'aggregate_supervision_diagnostic'})
    buffer=io.BytesIO();figure.savefig(buffer,format='png',dpi=140,bbox_inches='tight');png=buffer.getvalue()
    if not png.startswith(b'\x89PNG\r\n\x1a\n') or len(png)<1000:raise Stop('PNG_RENDER_FAILED')
    return plot,png

def display_saved(index):
    from pipeline import current_run
    from IPython.display import display,Image,Markdown
    from plotly.offline import get_plotlyjs
    directory,summary=current_run();out=directory/'figures';out.mkdir(exist_ok=True)
    spec=specification(summary,index);stem=f'{index:02d}';plot,png=build(spec)
    js=out/'plotly.min.js'
    if not js.exists():atomic(js,get_plotlyjs().encode())
    import plotly.io as pio
    atomic(out/(stem+'.png'),png)
    atomic(out/(stem+'.plotly.json'),pio.to_json(plot).encode())
    save_json(out/(stem+'.spec.json'),spec)
    atomic(out/(stem+'.html'),pio.to_html(plot,include_plotlyjs='plotly.min.js',full_html=True).encode())
    mpath=out/'FIGURES.json';m=read_json(mpath) if mpath.exists() else {'renderer':'Plotly interactive; Matplotlib PNG companion from identical numeric specification','figures':{}}
    m['figures'][stem]={'numeric_spec_sha256':digest(spec),'files':{stem+ext:sha(out/(stem+ext)) for ext in ('.png','.plotly.json','.spec.json','.html')}}
    m['plotly_js_sha256']=sha(js);save_json(mpath,m)
    display(Markdown('**'+spec['title']+'**\n\n'+spec['caption']))
    # Separate outputs are essential: an unsupported Plotly MIME choice cannot
    # conceal the independently emitted ordinary image/png output.
    display(Image(data=png,format='png'))
    plot.show(renderer='plotly_mimetype')

def finalize_figures():
    from pipeline import current_run
    directory,_=current_run();out=directory/'figures';m=read_json(out/'FIGURES.json')
    if set(m['figures'])!={f'{i:02d}' for i in range(1,13)}:raise Stop('TWELVE_FIGURES_NOT_SAVED')
    for value in m['figures'].values():
        for n,h in value['files'].items():
            if sha(out/n)!=h:raise Stop('FIGURE_FILE_CHANGED')
    if sha(out/'plotly.min.js')!=m['plotly_js_sha256']:raise Stop('PLOTLY_JS_CHANGED')
    links=''.join(f'<li><a href="{i:02d}.html">{i:02d} - {TITLES[i-1]}</a></li>' for i in range(1,13))
    atomic(out/'index.html',('<!doctype html><meta charset="utf-8"><title>Supervision diagnostics</title><h1>Supervision candidate comparisons</h1><p>Counts are not clinical accuracy or image-model AUC.</p><ul>'+links+'</ul>').encode())
    save_json(WORK/'notebook_ready.json',{'status':'complete_outputs_generated_save_notebook','utc':utc(),
        'key':read_json(WORK/'latest.json')['key'],'png_files':12,'plotly_files':12,'model_fits':0,'official_auc':None})
    return out
