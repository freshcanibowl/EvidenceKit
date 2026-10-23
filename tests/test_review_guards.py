import pytest
from open_evidencekit.lite import review_lite
from test_lite import Fake,bundle

@pytest.mark.parametrize('claim,text,reason',[
 ('The invoice was paid.','The note says "The invoice was paid" but has no receipt.','QUOTED_TEXT_REQUIRES_REVIEW'),
 ('Weight increased by 2.2 kg.','Weights were 68.2 and 69.4 kg.','NUMERIC_CLAIM_REQUIRES_REVIEW'),
 ('Luna ate breakfast.','Milo ate breakfast. Nothing is recorded about Luna.','SUBJECT_ALIGNMENT_REQUIRES_REVIEW'),
 ('The cat ate dinner.','No one observed the cat during dinner.','OBSERVATION_GAP_REQUIRES_REVIEW'),
 ('The parcel arrived.','The parcel might have arrived; it is unconfirmed.','UNCERTAINTY_REQUIRES_REVIEW'),
])
def test_risky_pairs_abstain_before_inference(claim,text,reason):
 b=bundle();b['claim']['text']=claim;b['evidence'][0]['text']=text;f=Fake()
 r=review_lite(b,f)
 assert r['verdict']=='INSUFFICIENT_EVIDENCE' and reason in r['reason_codes']
 assert f.calls==0 and r['model'] is None and r['per_evidence']==[]

def test_uncited_counterevidence_vetoes_support():
 b=bundle();b['evidence'].append({'id':'E2','text':'A did not arrive.','source_type':'log','observed_at':'2026-10-21T11:00:00Z'})
 r=review_lite(b,Fake(['entailment','contradiction']))
 assert r['verdict']=='INSUFFICIENT_EVIDENCE' and 'CONFLICTING_EVIDENCE' in r['reason_codes']
 assert r['per_evidence'][1]['cited'] is False

def test_uncited_support_does_not_establish_claim():
 b=bundle();b['evidence'].append({'id':'E2','text':'A arrived.','source_type':'log','observed_at':'2026-10-21T11:00:00Z'})
 r=review_lite(b,Fake(['neutral','entailment']))
 assert r['verdict']=='INSUFFICIENT_EVIDENCE'

def test_context_outside_declared_time_is_excluded():
 b=bundle();b['claim']['time_range']={'start':'2026-10-21T00:00:00Z','end':'2026-10-21T23:59:59Z'}
 b['evidence'].append({'id':'E2','text':'A did not arrive.','source_type':'log','observed_at':'2026-10-20T11:00:00Z'})
 f=Fake();r=review_lite(b,f)
 assert r['verdict']=='SUPPORTED' and f.calls==1 and r['excluded_context_ids']==['E2']
