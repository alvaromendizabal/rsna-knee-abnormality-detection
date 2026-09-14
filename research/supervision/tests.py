"""Synthetic offline tests; no AWS/Kaggle access or real report reads."""
from __future__ import annotations
import copy,json,tempfile,unittest
from pathlib import Path
import numpy as np
from common import LABELS,STATES,ARMS,Stop,atomic,save_json,sha,digest,checkpoint,notebook_source
from labels import normalized_report,extract,masked_candidate,strict_macro_auc
from pipeline import split_rows,choose_pilot,analyze_sample

POSITIVES={
 'ACL':'Complete tear of the ACL.', 'MCL':'MCL sprain.',
 'Medial Meniscus':'Tear of the medial meniscus.', 'Lateral Meniscus':'Tear of the lateral meniscus.',
 'Medial OA':'Osteoarthritis of the medial compartment.', 'Lateral OA':'Osteoarthritis of the lateral compartment.',
 'PF OA':'Patellofemoral osteoarthritis.', 'Effusion':'Joint effusion.', 'Synovitis':'Synovitis.',
 "Baker's":"Baker's cyst.", 'Contusion':'Bone contusion.', 'Fracture':'Fracture of the tibia.',
}

def toy_rows(n=40):
    rows=[{'id':str(i),'report':'Example number '+str(i)+'. ACL tear.','has_gold':False} for i in range(n)]
    rows[0]['has_gold']=True
    return rows

class AssertionTests(unittest.TestCase):
    def test_unmentioned_is_not_negative(self):self.assertEqual(set(extract('No relevant dictionary vocabulary.').values()),{'unmentioned'})
    def test_all_nonbinary_masked(self):
        for state in STATES[2:]:self.assertEqual(masked_candidate(state),(None,0))
    def test_binary_mask(self):
        self.assertEqual(masked_candidate('positive'),(1.,1));self.assertEqual(masked_candidate('negative'),(0.,1))
    def test_invalid_state_rejected(self):
        with self.assertRaises(Stop):masked_candidate('absentish')
    def test_normal_acl(self):self.assertEqual(extract('ACL intact.')['ACL'],'negative')
    def test_possible_tear(self):self.assertEqual(extract('Possible ACL tear.')['ACL'],'uncertain')
    def test_cannot_exclude(self):self.assertEqual(extract('Cannot exclude ACL tear.')['ACL'],'uncertain')
    def test_no_definite_not_negative(self):self.assertEqual(extract('No definite ACL tear.')['ACL'],'uncertain')
    def test_history_not_current(self):self.assertEqual(extract('History: ACL tear.')['ACL'],'context_only')
    def test_findings_resume(self):self.assertEqual(extract('History: ACL tear.\nFindings: ACL intact.')['ACL'],'negative')
    def test_postoperative_abstention(self):self.assertEqual(extract('Prior ACL repair with tear.')['ACL'],'context_only')
    def test_conflict(self):self.assertEqual(extract('ACL tear. No ACL tear.')['ACL'],'conflict')
    def test_ambiguous_two_structures(self):
        v=extract('ACL tear and MCL sprain.');self.assertEqual(v['ACL'],'context_only');self.assertEqual(v['MCL'],'context_only')
    def test_contrastive_clause(self):
        v=extract('ACL intact but MCL sprain.');self.assertEqual(v['ACL'],'negative');self.assertEqual(v['MCL'],'positive')
    def test_meniscal_degeneration_not_tear(self):self.assertEqual(extract('Medial meniscus degeneration.')['Medial Meniscus'],'context_only')
    def test_edema_not_contusion(self):self.assertEqual(extract('Bone marrow edema.')['Contusion'],'unmentioned')
    def test_fluid_not_synovitis(self):self.assertEqual(extract('Joint effusion.')['Synovitis'],'unmentioned')
    def test_generic_oa_not_compartment(self):
        v=extract('Osteoarthritis.');self.assertEqual(v['Medial OA'],'unmentioned');self.assertEqual(v['PF OA'],'unmentioned')
    def test_cartilage_loss_not_oa(self):self.assertEqual(extract('Medial compartment cartilage loss.')['Medial OA'],'context_only')
    def test_mention_only_is_positive_control(self):self.assertEqual(extract('No ACL tear.','mention_only')['ACL'],'positive')
    def test_negation_ablation(self):self.assertEqual(extract('No ACL tear.','joint_no_negation')['ACL'],'positive')
    def test_uncertainty_ablation(self):self.assertEqual(extract('Possible ACL tear.','joint_no_uncertainty')['ACL'],'positive')
    def test_context_ablation(self):self.assertEqual(extract('History: ACL tear.','joint_no_context_gate')['ACL'],'positive')
    def test_invalid_arm(self):
        with self.assertRaises(Stop):extract('ACL tear.','unregistered')
    def test_unicode_apostrophe(self):self.assertEqual(extract('Baker’s cyst.')["Baker's"],'positive')
    def test_exact_twelve_columns(self):self.assertEqual(list(extract('ACL tear.')),LABELS)

# Twenty-four separate target regressions, not one large all-pass assertion.
for i,(target,sentence) in enumerate(POSITIVES.items()):
    def positive(self,t=target,s=sentence):self.assertEqual(extract(s)[t],'positive')
    def negative(self,t=target,s=sentence):self.assertEqual(extract('No '+s)[t],'negative')
    setattr(AssertionTests,'test_target_positive_'+str(i),positive)
    setattr(AssertionTests,'test_target_negative_'+str(i),negative)

class SplitTests(unittest.TestCase):
    def test_normalization(self):self.assertEqual(normalized_report(' ACL   TEAR. '),'acl tear.')
    def test_gold_sealed(self):self.assertEqual(split_rows(toy_rows(),set())[0]['split'],'sealed_expert')
    def test_gold_report_overlap(self):
        r=toy_rows();r[1]['report']=r[0]['report'].upper();self.assertEqual(split_rows(r,set())[1]['split'],'expert_report_overlap')
    def test_pilot_forced_to_training(self):self.assertEqual(split_rows(toy_rows(),{'2'})[2]['split'],'training_unlabeled')
    def test_gold_reservation_overrides_pilot(self):
        r=toy_rows();r[1]['report']=r[0]['report'];self.assertEqual(split_rows(r,{'1'})[1]['split'],'expert_report_overlap')
    def test_repeated_reports_not_split(self):
        r=toy_rows();r[2]['report']=r[3]['report'];a=split_rows(r,set());self.assertEqual(a[2]['fold'],a[3]['fold'])
    def test_order_independent(self):
        r=toy_rows();a={x['id']:x for x in split_rows(r,set())};b={x['id']:x for x in split_rows(r[::-1],set())};self.assertEqual(a,b)
    def test_sample_only_training(self):
        r=toy_rows();a=split_rows(r,set());sample=choose_pilot(r,a,10);valid={x['id'] for x in a if x['split']=='training_unlabeled'}
        self.assertTrue({x['id'] for x in sample}<=valid);self.assertEqual(len(sample),10)
    def test_one_per_report_group(self):
        r=toy_rows();r[2]['report']=r[3]['report'];a=split_rows(r,{'2'});s=choose_pilot(r,a,100)
        self.assertEqual(len({normalized_report(x['report']) for x in s}),len(s))
    def test_no_candidates_when_gold(self):
        r=toy_rows(4)
        for x in r:x['has_gold']=True
        with self.assertRaises(Stop):choose_pilot(r,split_rows(r,set()))

class AggregateTests(unittest.TestCase):
    def test_same_reports_all_arms(self):
        _,a=analyze_sample(toy_rows(4))
        for arm in ARMS:
            for l in LABELS:self.assertEqual(sum(a['counts'][arm][l].values()),4)
    def test_no_accuracy_fabricated(self):
        _,a=analyze_sample(toy_rows(4));self.assertIsNone(a['official_auc']);self.assertFalse(a['training_targets_approved'])
    def test_raw_text_not_aggregate(self):
        r=toy_rows(4);_,a=analyze_sample(r);self.assertNotIn(r[0]['report'],json.dumps(a));self.assertNotIn('records',a)
    def test_scope_explicit(self):
        _,a=analyze_sample(toy_rows(4));self.assertIn('English',a['extraction_language_scope'])

class MetricTests(unittest.TestCase):
    def pairs(self):return np.tile([[0],[1]],(1,12))
    def test_perfect(self):self.assertEqual(strict_macro_auc(self.pairs(),self.pairs())['macro_auc'],1.)
    def test_reversed(self):self.assertEqual(strict_macro_auc(self.pairs(),1-self.pairs())['macro_auc'],0.)
    def test_ties(self):self.assertEqual(strict_macro_auc(self.pairs(),np.full((2,12),.5))['macro_auc'],.5)
    def test_nan_rejected(self):
        p=self.pairs().astype(float);p[0,0]=np.nan
        with self.assertRaises(Stop):strict_macro_auc(self.pairs(),p)
    def test_single_class_rejected(self):
        y=self.pairs();y[:,0]=1
        with self.assertRaises(Stop):strict_macro_auc(y,self.pairs())
    def test_eleven_columns_rejected(self):
        with self.assertRaises(Stop):strict_macro_auc(self.pairs()[:,:11],self.pairs()[:,:11])
    def test_probability_range(self):
        with self.assertRaises(Stop):strict_macro_auc(self.pairs(),self.pairs()*2)

class EvidenceTests(unittest.TestCase):
    def test_checkpoint_reuse(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);atomic(p/'x',b'a');save_json(p/'CHECKPOINT.json',{'key':'a','status':'complete','files':{'x':sha(p/'x')}})
            self.assertTrue(checkpoint(p,'a'))
    def test_checkpoint_tampering(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);atomic(p/'x',b'a');save_json(p/'CHECKPOINT.json',{'key':'a','status':'complete','files':{'x':sha(p/'x')}});atomic(p/'x',b'b')
            with self.assertRaises(Stop):checkpoint(p,'a')
    def test_checkpoint_path_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);save_json(p/'CHECKPOINT.json',{'key':'a','status':'complete','files':{'../bad':'hash'}})
            with self.assertRaises(Stop):checkpoint(p,'a')
    def test_missing_is_not_success(self):
        with tempfile.TemporaryDirectory() as d:self.assertFalse(checkpoint(Path(d),'a'))
    def test_outputs_not_notebook_source(self):
        a={'cells':[{'cell_type':'code','source':['print(1)'],'outputs':[]}]};b=copy.deepcopy(a);b['cells'][0]['outputs']=[{'x':2}]
        self.assertEqual(notebook_source(a),notebook_source(b))
    def test_source_edit_changes_hash(self):
        a={'cells':[{'cell_type':'code','source':['print(1)']}]};b={'cells':[{'cell_type':'code','source':['print(2)']}]}
        self.assertNotEqual(notebook_source(a),notebook_source(b))

class RenderingTests(unittest.TestCase):
    def test_png_and_plotly_same_numeric_spec(self):
        from plots import build
        s={'kind':'bar','title':'Synthetic renderer smoke test','caption':'Synthetic, not research evidence.',
           'number':1,'labels':['a','b'],'series':{'count':[1,2]},'ylabel':'Count'}
        figure,png=build(s);self.assertTrue(png.startswith(b'\x89PNG'))
        self.assertEqual(figure.layout.meta['numeric_spec_sha256'],digest(s));self.assertEqual(list(figure.data[0].y),[1,2])
    def test_missing_jaccard_not_zero(self):
        from plots import specification
        _,a=analyze_sample([{'id':'x','report':'no dictionary hits'}])
        s=specification(a,12);self.assertTrue(all(v is None for row in s['z'] for v in row))
    def test_all_twelve_specs_construct(self):
        from plots import specification
        _,a=analyze_sample(toy_rows(4));a['split_counts']={'sealed':1};a['fold_groups']={'0':1}
        for i in range(1,13):self.assertEqual(specification(a,i)['number'],i)
