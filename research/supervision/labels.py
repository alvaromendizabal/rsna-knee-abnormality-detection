"""Exploratory ENGLISH lexical supervision candidates, NOT clinical labels.

No pretrained labeler is implemented here. Clause windows are deliberately
conservative but still imperfect; this is NOT NegBio, a parser, or a multilingual
clinical system. Outputs cannot be used for training until independently reviewed.
"""
from __future__ import annotations
import re, unicodedata
from common import LABELS, STATES, ARMS, Stop

# Target dictionaries are intentionally precise: edema != contusion, fluid !=
# synovitis, meniscal degeneration != tear, and generic OA != compartment OA.
ANATOMY = {
 'ACL':r'\b(?:acl|anterior cruciate ligament)\b',
 'MCL':r'\b(?:mcl|medial collateral ligament)\b',
 'Medial Meniscus':r'\bmedial menisc(?:us|al)\b',
 'Lateral Meniscus':r'\blateral menisc(?:us|al)\b',
 'Medial OA':r'\b(?:medial (?:tibiofemoral|femorotibial)(?: compartment)?|medial compartment)\b',
 'Lateral OA':r'\b(?:lateral (?:tibiofemoral|femorotibial)(?: compartment)?|lateral compartment)\b',
 'PF OA':r'\b(?:patellofemoral(?: compartment)?|patello-femoral(?: compartment)?)\b',
 'Effusion':r'\b(?:joint effusion|knee effusion|effusion)\b',
 'Synovitis':r'\bsynovitis\b',
 "Baker's":r"\b(?:baker(?:'s|s)? cyst|popliteal cyst)\b",
 'Contusion':r'\b(?:bone (?:contusion|bruise)|osseous contusion|marrow contusion)\b',
 'Fracture':r'\bfracture\b',
}
PATHOLOGY = {
 'ACL':r'\b(?:tear|torn|ruptur\w*|injur\w*|sprain\w*|disrupt\w*)\b',
 'MCL':r'\b(?:tear|torn|ruptur\w*|injur\w*|sprain\w*|disrupt\w*)\b',
 'Medial Meniscus':r'\b(?:tear|torn|ruptur\w*)\b',
 'Lateral Meniscus':r'\b(?:tear|torn|ruptur\w*)\b',
 'Medial OA':r'\b(?:osteoarthrit\w*|osteoarthros\w*|arthrosis)\b',
 'Lateral OA':r'\b(?:osteoarthrit\w*|osteoarthros\w*|arthrosis)\b',
 'PF OA':r'\b(?:osteoarthrit\w*|osteoarthros\w*|arthrosis)\b',
}
NEGATION=re.compile(r'\b(?:no|not|without|absent|absence of|negative for|free of|neither|nor)\b')
NORMAL=re.compile(r'\b(?:intact|normal|unremarkable|preserved|uninjured)\b')
UNCERTAIN=re.compile(r'\b(?:possible|possibly|probable|probably|may|might|suspect\w*|suggest\w*|equivocal|questionable|cannot exclude|can not exclude|cannot be excluded|cannot rule out|not excluded|not ruled out|no definite|no significant|no appreciable|not clearly)\b')
HISTORY=re.compile(r'\b(?:history of|prior|previous|status post|s/p|postoperative|post-operative|reconstruct\w*|repair\w*|healed|old fracture)\b')
HEADING=re.compile(r'^\s*(history|clinical history|indication|clinical information|technique|comparison|findings|impression|conclusion)\s*:\s*(.*)$')
SEVERITY=re.compile(r'\b(?:trace|minimal|mild|moderate|severe|small|large|partial|complete|grade\s*[1-4iv]+)\b')


def normalized_report(text):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(text))).strip().casefold()

def clauses(report):
    text=unicodedata.normalize('NFKC',str(report)).replace('\u2019',"'").casefold()
    section='unknown'
    for line in text.splitlines():
        match=HEADING.match(line)
        if match:section,line=match.groups()
        for sentence in re.split(r'(?<=[.!?])\s+|;',line):
            for clause in re.split(r'\b(?:but|however|although)\b',sentence):
                if clause.strip():yield section,clause.strip()

def mentions_for_target(clause,target):
    return list(re.finditer(ANATOMY[target],clause))

def clause_state(clause,target,section,arm):
    mentions=mentions_for_target(clause,target)
    if not mentions:return None
    if arm=='mention_only':return 'positive'
    # Multi-target clauses can attach a finding or its negation to the wrong
    # anatomy. Abstain instead of guessing grammatical scope.
    other=[t for t in LABELS if t!=target and mentions_for_target(clause,t)]
    if other:return 'context_only'
    m=mentions[0]
    before=clause[:m.start()].split()[-8:]
    after=clause[m.end():].split()[:10]
    window=' '.join(before+[m.group()]+after)
    if arm!='joint_no_context_gate':
        if section in ('history','clinical history','indication','clinical information','technique','comparison') or HISTORY.search(window):
            return 'context_only'
    if arm!='joint_no_uncertainty' and UNCERTAIN.search(window):return 'uncertain'
    has_pathology = target not in PATHOLOGY or bool(re.search(PATHOLOGY[target],window))
    normal_structure = target in ('ACL','MCL','Medial Meniscus','Lateral Meniscus') and bool(NORMAL.search(window))
    if not has_pathology and not normal_structure:return 'context_only'
    if arm!='joint_no_negation' and (NEGATION.search(window) or NORMAL.search(window)):
        return 'negative'
    if not has_pathology:return 'context_only'
    return 'positive'

def merge_states(states):
    s=set(x for x in states if x is not None)
    if 'positive' in s and 'negative' in s:return 'conflict'
    if 'uncertain' in s:return 'uncertain'
    if 'positive' in s:return 'positive'
    if 'negative' in s:return 'negative'
    if s:return 'context_only'
    return 'unmentioned'

def extract(report,arm='joint_context'):
    if arm not in ARMS:raise Stop('UNKNOWN_SUPERVISION_ARM')
    parsed=list(clauses(report))
    return {target:merge_states(clause_state(c,target,section,arm) for section,c in parsed) for target in LABELS}

def masked_candidate(state):
    if state not in STATES:raise Stop('UNKNOWN_ASSERTION_STATE')
    # Returning (None, 0) for all nonbinary cases prevents silent negatives.
    return (1.0,1) if state=='positive' else (0.0,1) if state=='negative' else (None,0)

def strict_macro_auc(y_true,y_score):
    """Future-use metric, not invoked on gold labels by this milestone.

    All 12 columns must be defined, finite, binary, and have both classes.
    No silently reduced-label macro score. Average-rank ties are exact.
    """
    import numpy as np
    y=np.asarray(y_true,dtype=float);p=np.asarray(y_score,dtype=float)
    if y.ndim!=2 or y.shape!=p.shape or y.shape[1]!=12 or y.shape[0]<2:raise Stop('AUC_SHAPE')
    if not np.isfinite(y).all() or not np.isfinite(p).all():raise Stop('AUC_NONFINITE')
    if not np.isin(y,[0,1]).all() or ((p<0)|(p>1)).any():raise Stop('AUC_VALUES')
    out=[]
    for i in range(12):
        labels=y[:,i];s=p[:,i];pos=int(labels.sum());neg=len(labels)-pos
        if not pos or not neg:raise Stop('AUC_SINGLE_CLASS_LABEL')
        order=np.argsort(s,kind='stable');ranks=np.empty(len(s),float);j=0
        while j<len(s):
            k=j+1
            while k<len(s) and s[order[k]]==s[order[j]]:k+=1
            ranks[order[j:k]]=(j+1+k)/2;j=k
        out.append(float((ranks[labels==1].sum()-pos*(pos+1)/2)/(pos*neg)))
    return {'macro_auc':float(np.mean(out)),'per_label_auc':dict(zip(LABELS,out))}
