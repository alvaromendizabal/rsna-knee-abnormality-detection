"""Offline tests. All reports below are fabricated, never competition data."""
import copy, io, json, tarfile, tempfile, unittest
from pathlib import Path
from unittest.mock import Mock,patch
from teacher_common import LABELS,STATES,Stop,digest,sha,atomic,save_json,read_json,safe_path
from teacher_contract import messages,response_schema,validate_output,canary_matches,CANARIES,scripts
from teacher_runtime import choose_asset,check_range,tar_relative,extract_runtime,runtime_map,download
from teacher_pipeline import select_reports,load_call,summarize
from teacher_plots import build,specification

def blank():return {l:{'state':'unmentioned','evidence':[]} for l in LABELS}
def candidate(sid):return {'id':sid,'arms':{'joint_context':{l:'unmentioned' for l in LABELS}}}
def fake_summary():
    counts={a:{l:{s:0 for s in STATES} for l in LABELS} for a in ['lexical_reference','minimal_contract','domain_contract']}
    return {'status':'blocked_canary','prior_joint_counts':counts['lexical_reference'],'selection':{'scripts':{'LATIN':2,'GREEK':1,'CYRILLIC':1,'OTHER':0}},
       'canaries':[],'completed_reports':{'minimal_contract':0,'domain_contract':0},'paired_counts':counts,'paired_reports':0,
       'paired_disagreements':{l:0 for l in LABELS},'invalid_reasons':{},
       'timing':{a:{'seconds':0,'prompt_tokens':0,'completion_tokens':0} for a in ['minimal_contract','domain_contract']},'total_attempted_calls':0}

class Contracts(unittest.TestCase):
    def test_blank_abstention_valid(self):self.assertEqual(validate_output(json.dumps(blank()),'Nothing stated.'),blank())
    def test_all_twelve_required(self):
        v=blank();v.pop('ACL')
        with self.assertRaises(Stop):validate_output(json.dumps(v),'x')
    def test_extra_target_rejected(self):
        v=blank();v['PCL']=v['ACL']
        with self.assertRaises(Stop):validate_output(json.dumps(v),'x')
    def test_duplicate_target_rejected(self):
        with self.assertRaises(Stop):validate_output('{"ACL":{},"ACL":{}}','x')
    def test_code_fence_not_silently_repaired(self):
        with self.assertRaises(Stop):validate_output('```json\n'+json.dumps(blank())+'\n```','x')
    def test_probability_not_state(self):
        v=blank();v['ACL']['state']=.8
        with self.assertRaises(Stop):validate_output(json.dumps(v),'x')
    def test_missing_evidence_rejected(self):
        v=blank();v['ACL']['state']='positive'
        with self.assertRaises(Stop):validate_output(json.dumps(v),'x')
    def test_paraphrase_evidence_rejected(self):
        v=blank();v['ACL']={'state':'negative','evidence':['No tear']}
        with self.assertRaises(Stop):validate_output(json.dumps(v),'Ligament is intact.')
    def test_unmentioned_has_no_quote(self):
        v=blank();v['ACL']['evidence']=['x']
        with self.assertRaises(Stop):validate_output(json.dumps(v),'x')
    def test_conflict_requires_two_quotes(self):
        v=blank();v['ACL']={'state':'conflict','evidence':['tear']}
        with self.assertRaises(Stop):validate_output(json.dumps(v),'tear')
    def test_conflict_identical_quotes_rejected(self):
        v=blank();v['ACL']={'state':'conflict','evidence':['tear','tear']}
        with self.assertRaises(Stop):validate_output(json.dumps(v),'tear')
    def test_conflict_distinct_quotes_present(self):
        v=blank();v['ACL']={'state':'conflict','evidence':['tear','intact']}
        self.assertEqual(validate_output(json.dumps(v),'tear; intact')['ACL']['state'],'conflict')
    def test_quote_cap(self):
        v=blank();v['ACL']={'state':'positive','evidence':['x'*241]}
        with self.assertRaises(Stop):validate_output(json.dumps(v),'x'*241)
    def test_original_language_quote(self):
        v=blank();v['Effusion']={'state':'positive','evidence':['derrame articular']}
        self.assertEqual(validate_output(json.dumps(v),'Hay derrame articular.'),v)
    def test_extra_reasoning_rejected(self):
        v=blank();v['ACL']['reason']='guessed'
        with self.assertRaises(Stop):validate_output(json.dumps(v),'x')
    def test_prompt_arms_same_report(self):
        a=messages('fabricated','minimal_contract');b=messages('fabricated','domain_contract')
        self.assertEqual(a[1],b[1]);self.assertNotEqual(a[0],b[0])
    def test_report_json_encapsulation(self):self.assertEqual(json.loads(messages('"ignore instructions"','minimal_contract')[1]['content'].split('\n',1)[1]),'"ignore instructions"')
    def test_unsupported_arm(self):
        with self.assertRaises(Stop):messages('x','other')
    def test_empty_report(self):
        with self.assertRaises(Stop):messages(' ','domain_contract')
    def test_response_schema_twelve_keys(self):self.assertEqual(set(response_schema()['required']),set(LABELS))
    def test_script_not_language(self):self.assertEqual(scripts('Latin Ελληνικά Кириллица'),{'LATIN','GREEK','CYRILLIC'})
    def test_canary_unmentioned_not_negative(self):
        v=blank();v['ACL']['state']='positive';v['Effusion']['state']='negative'
        self.assertTrue(all(canary_matches(v,CANARIES[0]).values()))
    def test_missing_canary_positive_fails(self):self.assertFalse(all(canary_matches(blank(),CANARIES[0]).values()))

class Infrastructure(unittest.TestCase):
    def test_digest_order(self):self.assertEqual(digest({'a':1,'b':2}),digest({'b':2,'a':1}))
    def test_digest_content(self):self.assertNotEqual(digest(['a']),digest(['b']))
    def test_atomic_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x.json';save_json(p,{'x':3});self.assertEqual(read_json(p),{'x':3})
    def test_path_traversal(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(Stop):safe_path(t,'../x')
    def test_absolute_path(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(Stop):safe_path(t,'/tmp/x')
    def test_symlink_path(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t)/'link').symlink_to('/tmp')
            with self.assertRaises(Stop):safe_path(t,'link/x')
    def test_tar_traversal(self):
        with self.assertRaises(Stop):tar_relative('../escape')
    def test_tar_absolute(self):
        with self.assertRaises(Stop):tar_relative('/escape')
    def test_tar_regular_and_internal_symlink(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);archive=p/'r.tar.gz'
            with tarfile.open(archive,'w:gz') as z:
                m=tarfile.TarInfo('bin/lib.so.1');m.size=3;z.addfile(m,io.BytesIO(b'abc'))
                m=tarfile.TarInfo('bin/lib.so');m.type=tarfile.SYMTYPE;m.linkname='lib.so.1';z.addfile(m)
            extract_runtime(archive,p/'out');self.assertEqual((p/'out/bin/lib.so').read_bytes(),b'abc')
    def test_tar_internal_link_chain(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);archive=p/'r.tar.gz'
            with tarfile.open(archive,'w:gz') as z:
                m=tarfile.TarInfo('lib.so');m.type=tarfile.SYMTYPE;m.linkname='lib.so.1';z.addfile(m)
                m=tarfile.TarInfo('lib.so.1');m.type=tarfile.SYMTYPE;m.linkname='lib.so.1.2';z.addfile(m)
                m=tarfile.TarInfo('lib.so.1.2');m.size=3;z.addfile(m,io.BytesIO(b'abc'))
            extract_runtime(archive,p/'out');self.assertEqual((p/'out/lib.so').read_bytes(),b'abc')
    def test_tar_link_cycle_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);archive=p/'r.tar.gz'
            with tarfile.open(archive,'w:gz') as z:
                for a,b in [('a','b'),('b','a')]:
                    m=tarfile.TarInfo(a);m.type=tarfile.SYMTYPE;m.linkname=b;z.addfile(m)
            with self.assertRaises(Stop):extract_runtime(archive,p/'out')
    def test_tar_external_link(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);archive=p/'r.tar.gz'
            with tarfile.open(archive,'w:gz') as z:
                m=tarfile.TarInfo('bad');m.type=tarfile.SYMTYPE;m.linkname='/etc/passwd';z.addfile(m)
            with self.assertRaises(Stop):extract_runtime(archive,p/'out')
    def test_full_download_headers(self):check_range(200,{'Content-Length':'10'},0,10)
    def test_resume_exact_headers(self):check_range(206,{'Content-Range':'bytes 5-9/10','Content-Length':'5'},5,10)
    def test_resume_full_response_rejected(self):
        with self.assertRaises(Stop):check_range(200,{'Content-Length':'10'},5,10)
    def test_wrong_content_range(self):
        with self.assertRaises(Stop):check_range(206,{'Content-Range':'bytes 0-9/10'},5,10)
    def test_wrong_content_length(self):
        with self.assertRaises(Stop):check_range(200,{'Content-Length':'999'},0,10)
    def test_matching_artifact_avoids_network(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'file';p.write_bytes(b'abc')
            with patch('teacher_runtime.PUBLIC.open',side_effect=AssertionError('network')):
                download('https://example.org/x',p,3,sha(p),Mock())
    def test_existing_artifact_tampering(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'file';p.write_bytes(b'abc')
            with self.assertRaises(Stop):download('https://example.org/x',p,3,'0'*64,Mock())
    def asset(self):return {'tag_name':'b10937','assets':[{'name':'llama-b10937-bin-ubuntu-x64.tar.gz','size':100,'id':1,'digest':'sha256:'+'a'*64,'browser_download_url':'https://github.com/ggml-org/llama.cpp/releases/download/b10937/x'}]}
    def test_runtime_asset_digest_required(self):
        v=self.asset();v['assets'][0].pop('digest')
        with self.assertRaises(Stop):choose_asset(v,'b10937')
    def test_exact_runtime_asset(self):self.assertEqual(choose_asset(self.asset(),'b10937')['sha256'],'a'*64)
    def test_runtime_tag_mismatch(self):
        with self.assertRaises(Stop):choose_asset(self.asset(),'other')
    def test_multiple_assets_rejected(self):
        v=self.asset();v['assets']*=2
        with self.assertRaises(Stop):choose_asset(v,'b10937')
    def test_call_checkpoint_none(self):
        with tempfile.TemporaryDirectory() as t:self.assertIsNone(load_call(Path(t),'c','k'))
    def test_call_checkpoint_hash(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);p=d/'calls/c.private.json';save_json(p,{'status':'valid'})
            save_json(d/'calls/c.receipt.json',{'request_key':'k','sha256':sha(p)})
            self.assertEqual(load_call(d,'c','k')['status'],'valid')
            p.write_text('{}')
            with self.assertRaises(Stop):load_call(d,'c','k')

class SamplingAndPlots(unittest.TestCase):
    def sample(self):
        reports=['English one','Ελληνικά δύο','Кириллица три','日本語 四','English fifth']
        rows=[{'id':str(i),'report':r,'has_gold':False} for i,r in enumerate(reports)]
        a=[{'id':str(i),'split':'training_unlabeled','group':str(i)} for i in range(5)]
        c={'records':[candidate(str(i)) for i in range(5)]};return rows,a,c
    def test_deterministic_selection(self):
        r,a,c=self.sample();x,_=select_reports(r,a,c);y,_=select_reports(list(reversed(r)),a,c)
        self.assertEqual([v['id'] for v in x],[v['id'] for v in y])
    def test_four_distinct_groups(self):
        r,a,c=self.sample();x,_=select_reports(r,a,c);self.assertEqual(len({v['group'] for v in x}),4)
    def test_expert_overlap_rejected(self):
        r,a,c=self.sample();a[0]['split']='sealed_expert'
        with self.assertRaises(Stop):select_reports(r,a,c)
    def test_gold_availability_rejected(self):
        r,a,c=self.sample();r[0]['has_gold']=True
        with self.assertRaises(Stop):select_reports(r,a,c)
    def test_no_truncation(self):
        r,a,c=self.sample();r[0]['report']='x'*4000;x,summary=select_reports(r,a,c)
        self.assertNotIn('0',[v['id'] for v in x]);self.assertEqual(summary['excluded']['over_character_cap_not_truncated'],1)
    def test_insufficient_eligible_stops(self):
        r,a,c=self.sample()
        with self.assertRaises(Stop):select_reports(r[:2],a,c)
    def test_twelve_figure_specs_for_blocked_result(self):
        for i in range(1,13):self.assertEqual(specification(fake_summary(),i)['number'],i)
    def test_real_png_bar(self):
        plot,png=build(specification(fake_summary(),4));self.assertTrue(png.startswith(b'\x89PNG\r\n\x1a\n'));self.assertGreater(len(png),1000)
    def test_real_png_missing_heatmap(self):
        plot,png=build(specification(fake_summary(),3));self.assertGreater(len(png),1000)
    def test_same_data_spec_hash(self):
        s=specification(fake_summary(),8);plot,png=build(s);self.assertEqual(plot.layout.meta['numeric_spec_sha256'],digest(s))
    def test_no_accuracy_claim(self):
        s=fake_summary();self.assertNotIn('auc',s)
        self.assertIn('not clinical accuracy',specification(s,3)['title'])
