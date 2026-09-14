"""Same-data Plotly + Agg PNG outputs, regenerated and saved each notebook run."""
from __future__ import annotations
import io, json
from teacher_common import LABELS,STATES,ARMS,Stop,digest,atomic,save_json,read_json,sha

TITLES=[
 'Earlier lexical pilot: binary candidate coverage by finding',
 'Teacher pilot: selected training-report script presence',
 'Synthetic operational checks: exact expected states, not clinical accuracy',
 'Teacher completion: same four planned reports per prompt arm',
 'Binary candidate counts on common successful reports only',
 'Prompt-definition sensitivity: paired state disagreements',
 'Explicit negative candidates on the matched reports',
 'Domain-contract assertion states: missing is not negative',
 'Output-contract rejections: evidence validity is not entailment',
 'Tokens used in real-report inference by prompt arm',
 'Measured real-report generation time by prompt arm',
 'Experiment accounting: inference calls and protected evaluation studies',
]
CAPTIONS=[
 '330 of 3,072 cells were binary in the prior 256-report sample. Coverage does not measure correctness.',
 'Sampling favors distinct scripts where available. Script is not language identity; four reports are not representative.',
 'English and Spanish fabricated cases test a narrow execution contract. Unrun cases remain blank, not failed.',
 'Invalid output stops additional real-report inference; successful subsets must not be compared with different denominators.',
 'All series use exactly the intersection of successfully processed reports. These are label candidates, not ground truth.',
 'The same model, decoder and reports are used. A changed state does not establish an improvement.',
 'An explicit negative needs a verbatim quote. The validator does not prove that the quote entails the conclusion.',
 'Uncertainty, conflict, history-only and unmentioned remain nonbinary. Do not train an image model on these outputs yet.',
 'Strict schema and quote checks can catch malformed outputs, not all semantic or multilingual mistakes.',
 'Tokens are resource measurements, not measures of clinical quality. Failed calls may not return token usage.',
 'Measured generation times exclude server startup and token counting. Counterbalanced order does not eliminate warm-up effects.',
 'Checkpoint reuse must introduce zero new inference calls. All 58 expert studies and four report overlaps stay sealed.',
]

def specification(s,i):
    if i not in range(1,13):raise Stop('FIGURE_NUMBER')
    spec={'number':i,'title':TITLES[i-1],'caption':CAPTIONS[i-1],'outcome':s['status'],'paired_reports':s['paired_reports']}
    def vec(arm,state):return [s['paired_counts'][arm][l][state] for l in LABELS]
    if i==1:
        spec.update(kind='bar',labels=LABELS,series={'Binary candidates':[s['prior_joint_counts'][l]['positive']+s['prior_joint_counts'][l]['negative'] for l in LABELS]},ylabel='Candidate count / 256 reports')
    elif i==2:spec.update(kind='bar',labels=list(s['selection']['scripts']),series={'Selected reports':list(s['selection']['scripts'].values())},ylabel='Reports containing script')
    elif i==3:
        c={x['name']:x for x in s['canaries']}
        spec.update(kind='heatmap',x=LABELS,y=['English synthetic','Spanish synthetic'],z=[c.get(k,{}).get('matches',[None]*12) for k in ('C01','C02')],ylabel='Fabricated case',xlabel='Finding',unit='Expected state matched: 1 / 0; blank = unrun')
    elif i==4:spec.update(kind='bar',labels=ARMS,series={'Planned':[4,4],'Valid completed':[s['completed_reports'][a] for a in ARMS]},ylabel='Report count')
    elif i==5:spec.update(kind='bar',labels=LABELS,series={a:[s['paired_counts'][a][l]['positive']+s['paired_counts'][a][l]['negative'] for l in LABELS] for a in ['lexical_reference',*ARMS]},ylabel='Binary candidates on '+str(s['paired_reports'])+' common reports')
    elif i==6:spec.update(kind='bar',labels=LABELS,series={'Different state':[s['paired_disagreements'][l] for l in LABELS]},ylabel='Changed states on '+str(s['paired_reports'])+' common reports')
    elif i==7:spec.update(kind='bar',labels=LABELS,series={a:vec(a,'negative') for a in ['lexical_reference',*ARMS]},ylabel='Negative candidates on common reports')
    elif i==8:spec.update(kind='heatmap',x=STATES,y=LABELS,z=[[s['paired_counts']['domain_contract'][l][st] for st in STATES] for l in LABELS],xlabel='State',ylabel='Finding',unit='Count on common reports')
    elif i==9:
        reasons=s['invalid_reasons'] or {'No observed output rejection':0}
        spec.update(kind='bar',labels=list(reasons),series={'Rejected calls':list(reasons.values())},ylabel='Call count; not an accuracy score')
    elif i==10:spec.update(kind='bar',labels=ARMS,series={k:[s['timing'][a][k] for a in ARMS] for k in ('prompt_tokens','completion_tokens')},ylabel='Reported tokens; real reports only')
    elif i==11:spec.update(kind='bar',labels=ARMS,series={'Seconds':[s['timing'][a]['seconds'] for a in ARMS]},ylabel='Measured generation wall seconds')
    else:spec.update(kind='bar',labels=['Inference attempts','Training fits','Sealed expert studies','Sealed report overlaps'],series={'Count':[s['total_attempted_calls'],0,58,4]},ylabel='Count (different units; not performance)')
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
                       meta={'numeric_spec_sha256':digest(spec),'role':'aggregate_teacher_diagnostic'})
    buffer=io.BytesIO();figure.savefig(buffer,format='png',dpi=140,bbox_inches='tight');png=buffer.getvalue()
    if not png.startswith(b'\x89PNG\r\n\x1a\n') or len(png)<1000:raise Stop('PNG_RENDER_FAILED')
    return plot,png

def display_saved(index):
    from teacher_pipeline import current_run
    from IPython.display import display,Image,Markdown
    from plotly.offline import get_plotlyjs
    import plotly.io as pio
    directory,summary=current_run();out=directory/'figures';out.mkdir(exist_ok=True)
    spec=specification(summary,index);stem=f'{index:02d}';plot,png=build(spec)
    js=out/'plotly.min.js'
    if not js.exists():atomic(js,get_plotlyjs().encode())
    atomic(out/(stem+'.png'),png);atomic(out/(stem+'.plotly.json'),pio.to_json(plot).encode())
    save_json(out/(stem+'.spec.json'),spec)
    atomic(out/(stem+'.html'),pio.to_html(plot,include_plotlyjs='plotly.min.js',full_html=True).encode())
    mpath=out/'FIGURES.json';m=read_json(mpath) if mpath.exists() else {'renderer':'Plotly plus same-data Matplotlib Agg PNG','figures':{}}
    m['figures'][stem]={'numeric_spec_sha256':digest(spec),'files':{stem+ext:sha(out/(stem+ext)) for ext in ('.png','.plotly.json','.spec.json','.html')}}
    m['plotly_js_sha256']=sha(js);save_json(mpath,m)
    display(Markdown('**'+spec['title']+'**\n\n'+spec['caption']+'\n\nOutcome: `'+summary['status']+'`; common paired reports: '+str(summary['paired_reports'])))
    try:plot.show(renderer='plotly_mimetype')
    finally:display(Image(data=png))

def finalize_figures():
    from teacher_pipeline import current_run
    d,_=current_run();out=d/'figures';m=read_json(out/'FIGURES.json')
    if set(m['figures'])!={f'{i:02d}' for i in range(1,13)}:raise Stop('TWELVE_TEACHER_FIGURES_REQUIRED')
    for v in m['figures'].values():
        for n,h in v['files'].items():
            if sha(out/n)!=h:raise Stop('TEACHER_FIGURE_HASH_CHANGED')
    if sha(out/'plotly.min.js')!=m['plotly_js_sha256']:raise Stop('PLOTLY_BUNDLE_CHANGED')
    html='<html><meta charset="utf-8"><title>RSNA local teacher pilot</title><h1>Local teacher pilot — candidate supervision, not clinical accuracy</h1>'
    for i,title in enumerate(TITLES,1):html+=f'<p><a href="{i:02d}.html">{i:02d}. {title}</a> · <a href="{i:02d}.png">PNG</a></p>'
    atomic(out/'index.html',(html+'</html>').encode());return out
