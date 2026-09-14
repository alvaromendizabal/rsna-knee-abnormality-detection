"""Aggregate-only Plotly figures. No report text, patient identifiers, or MRI pixels."""
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from rsna_knee.schema import PLANES


def finish(fig,title,y=None):
    fig.update_layout(title=title,height=470,margin=dict(l=70,r=25,t=80,b=100),
                      template='plotly_white',font=dict(size=13))
    if y: fig.update_yaxes(title=y)
    return fig


def round1_figure(directory,number):
    p=pd.read_csv(directory/'feature_profile.csv'); new=p[p.feature.str.startswith('r1__')].copy()
    summary=json.loads((directory/'construction_summary.json').read_text())
    if number==1:
        frame=pd.DataFrame({'panel':['Preserved baseline','New Round 1'],
            'columns':[summary['baseline_columns'],summary['new_columns']]})
        return finish(px.bar(frame,x='panel',y='columns'),'Representation size — counts are not evidence of predictive value','Feature columns')
    if number==2:
        f=new.groupby('family').size().reset_index(name='columns')
        return finish(px.bar(f,x='family',y='columns'),'Eight prepared domain families','Feature columns')
    if number==3:
        return finish(px.histogram(new,x='distinct_values',nbins=20),'Observed variation in the unlabeled development pool','Feature columns')
    if number==4:
        f=new.groupby('family').zero_fraction.mean().reset_index()
        return finish(px.bar(f,x='family',y='zero_fraction'),'Mean zero fraction by family — absence is not disease negativity','Fraction')
    if number==5:
        f=new.assign(constant=new.distinct_values.le(1)).groupby('family').constant.sum().reset_index()
        return finish(px.bar(f,x='family',y='constant'),'Constant candidates — recorded, not automatically removed','Feature columns')
    if number==6:
        f=new.assign(span=new.maximum-new.minimum).groupby('family').span.median().reset_index()
        return finish(px.bar(f,x='family',y='span'),'Median observed feature range by family — heterogeneous descriptor units','Median descriptor range')
    if number==7:
        plan=pd.read_csv(directory/'sample_plan.private.csv')
        f=plan.Anatomical_Plane.value_counts().reindex(PLANES,fill_value=0).rename_axis('plane').reset_index(name='selected_series')
        return finish(px.bar(f,x='plane',y='selected_series'),'Planned image pilot — one preferred series per available plane','Series')
    if number==8:
        f=new[new.family.eq('within_plane_contrast')].copy()
        f['plane']=f.feature.str.extract(r'r1__(\w+)_conditional')[0]
        f['contrast']=f.feature.str.extract(r'conditional_(.*)')[0]
        matrix=f.pivot(index='plane',columns='contrast',values='mean')
        return finish(px.imshow(matrix,aspect='auto',labels=dict(color='Mean fraction')),'Mean within-plane contrast proportions — unlabeled development only')
    if number==9:
        f=new[new.feature.str.endswith('contrast_entropy')]
        return finish(px.bar(f,x='feature',y='mean',error_y=f['maximum']-f['mean'],error_y_minus=f['mean']-f['minimum']),
                      'Within-plane contrast entropy — bars show mean; whiskers show range, not confidence intervals','Entropy, natural-log units')
    if number==10:
        f=new[new.feature.str.endswith('contrast_jaccard')]
        return finish(px.bar(f,x='feature',y='mean'),'Cross-plane overlap of available contrasts','Mean Jaccard overlap')
    if number==11:
        s=json.loads((directory/'reservation.json').read_text())
        keys=['expert_labeled_studies_reserved','unlabeled_exact_report_duplicates_reserved','unlabeled_development_studies']
        return finish(px.bar(x=keys,y=[s[k] for k in keys]),'Evaluation protection inventory — no disease values inspected','Studies')
    if number==12:
        f=new[new.feature.str.endswith('nonredundant_fraction')]
        return finish(px.bar(f,x='feature',y='mean'),'Nonredundant contrast coverage — more series need not add another view','Mean nonredundant fraction')
    raise ValueError('Figure number must be 1-12.')


def round2_figure(directory,number):
    p=pd.read_csv(directory/'feature_profile.csv'); s=json.loads((directory/'summary.json').read_text())
    if number==1:
        return finish(px.bar(x=['Planned','Complete on disk','Processed in this pilot'],
            y=[s['planned_series'],s['available_complete_series'],s['series_processed']]),'Pilot coverage — this is not a disease validation cohort','Series')
    if number==2:
        f=p.groupby('family').size().reset_index(name='columns')
        return finish(px.bar(f,x='family',y='columns'),'Eight image-representation families','Per-series feature columns')
    if number in (3,4,5,6,7,9,10):
        family={3:'intensity_distribution',4:'intensity_distribution',5:'signal_tails',6:'spatial_gradients',
                7:'cooccurrence_texture',9:'slice_context',10:'multiscale_context'}[number]
        f=p[p.family.eq(family)].copy()
        f['crop']=f.feature.str.split('__').str[0]; f['descriptor']=f.feature.str.split('__').str[1]
        if number==4:
            matrix=f.pivot(index='descriptor',columns='crop',values='mean')
            d=matrix['center75']-matrix['full']
            return finish(px.bar(x=d.index,y=d.values),'Center-window minus full-view descriptors — representation differences, not AUC gains','Descriptor difference; mixed units')
        if number==6: f=f[f.descriptor.str.endswith('gradient_mean')]
        if number==7: f=f[f.descriptor.str.endswith('contrast')]
        if number==9: f=f[f.descriptor.str.contains('difference_mean')]
        if number==10: f=f[f.descriptor.str.endswith('entropy16')]
        title={3:'Signal distribution after fixed within-series normalization',5:'Relative bright/dark signal — not tissue-specific pathology',
          6:'In-plane gradients under two fixed fields of view',7:'16-bin texture contrast at 1/2-pixel offsets — not IBSI-certified',
          9:'Through-slice context under two fixed fields of view',10:'Fixed 2x/4x average-pooling context'}[number]
        return finish(px.bar(f,x='descriptor',y='mean',color='crop',barmode='group'),title,'Mean descriptor value across processed pilot series')
    if number==8:
        f=p[p.feature.str.match(r'full__patch\d\d_mean')].copy()
        f['row']=f.feature.str.extract(r'patch(\d)')[0].astype(int)
        f['column']=f.feature.str.extract(r'patch\d(\d)')[0].astype(int)
        return finish(px.imshow(f.pivot(index='row',columns='column',values='mean'),aspect='equal',
            labels=dict(x='Image-relative column',y='Image-relative row',color='Mean normalized signal')),
            'Image-relative patch heterogeneity — not ligament, meniscus, or cartilage segmentation')
    if number==11:
        keys=['geometry__row_spacing_mm','geometry__column_spacing_mm','geometry__median_slice_step_mm']
        f=p[p.feature.isin(keys)]
        return finish(px.bar(f,x='feature',y='mean'),'Native physical spacing — no isotropic-resampling claim','Millimeters')
    if number==12:
        return finish(px.bar(x=['Newly computed','Checksum-reused'],y=[s['computed_series'],s['reused_verified_series']]),
            'Second invocation checkpoint evidence — expected: zero new series','Series')
    raise ValueError('Figure number must be 1-12.')
