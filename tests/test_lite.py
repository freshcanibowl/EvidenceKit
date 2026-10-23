import copy
import pytest
from open_evidencekit.lite import review_lite

class Fake:
    provenance={'test_double':True}
    def __init__(self,labels=('entailment',)): self.labels=iter(labels); self.calls=0
    def predict(self,p,h):
        self.calls+=1
        label=next(self.labels)
        return {'scores':{k:0.96 if k==label else 0.02 for k in ('entailment','neutral','contradiction')},'elapsed_ms':0}

def bundle():
    return {'synthetic':True,'claim':{'id':'C','text':'A arrived.','source_ids':['E']},'evidence':[{'id':'E','text':'A arrived.','source_type':'log','observed_at':'2026-10-21T10:00:00Z'}]}

@pytest.mark.parametrize('label,expected',[('entailment','SUPPORTED'),('contradiction','CONTRADICTED'),('neutral','INSUFFICIENT_EVIDENCE')])
def test_relations(label,expected): assert review_lite(bundle(),Fake([label]))['verdict']==expected

@pytest.mark.parametrize('change', ['missing','time','source'])
def test_rules_stop_model(change):
    b=bundle(); f=Fake()
    if change=='missing': b['claim']['source_ids']=['absent']
    if change=='time': b['claim']['time_range']={'start':'2026-10-22T00:00:00Z','end':'2026-10-23T00:00:00Z'}
    if change=='source': b['claim']['allowed_source_types']=['camera']
    r=review_lite(b,f)
    assert r['status']=='INVALID_REFERENCE' and f.calls==0 and r['model'] is None

def test_conflict_is_not_support():
    b=bundle(); e=copy.deepcopy(b['evidence'][0]); e['id']='E2'; b['evidence'].append(e); b['claim']['source_ids'].append('E2')
    r=review_lite(b,Fake(['entailment','contradiction']))
    assert r['verdict']=='INSUFFICIENT_EVIDENCE' and 'CONFLICTING_EVIDENCE' in r['reason_codes']

def test_temporal_aggregation_abstains():
    b=bundle(); b['claim']['requires_temporal_aggregation']=True
    assert review_lite(b,Fake())['verdict']=='INSUFFICIENT_EVIDENCE'

@pytest.mark.parametrize('change',['duplicate','six','empty','timezone','oversize','real','reversed','nan'])
def test_invalid_inputs(change):
    b=bundle(); f=Fake()
    if change=='duplicate': b['evidence']*=2
    if change=='six': b['evidence']*=6
    if change=='empty': b['claim']['source_ids']=[]
    if change=='timezone': b['evidence'][0]['observed_at']='2026-10-21'
    if change=='oversize': b['evidence'][0]['text']='x'*4001
    if change=='real': b['synthetic']=False
    if change=='reversed': b['claim']['time_range']={'start':'2026-10-23T00:00:00Z','end':'2026-10-22T00:00:00Z'}
    if change=='nan': f.predict=lambda p,h: {'scores':{'entailment':float('nan'),'neutral':0,'contradiction':0}}
    with pytest.raises(ValueError): review_lite(b,f)

def test_predictor_failure_propagates():
    class Broken(Fake):
        def predict(self,p,h): raise RuntimeError('no model')
    with pytest.raises(RuntimeError,match='no model'): review_lite(bundle(),Broken())
