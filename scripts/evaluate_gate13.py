"""Execute original Gate13 candidates through an explicit Lite-schema adapter."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time
from open_evidencekit.lite import review_lite,VERDICTS
from open_evidencekit.nli import LocalNLI,MODEL_DIR

class Unavailable:
    @property
    def provenance(self): return {'fault_injection':True}
    def predict(self,*args): raise RuntimeError('Injected model unavailable')

def main():
    p=argparse.ArgumentParser();p.add_argument('--model-dir',type=Path,default=MODEL_DIR);p.add_argument('--dataset',type=Path);p.add_argument('--output',default='gate13-real-inference.json');a=p.parse_args()
    root=Path(__file__).resolve().parents[1]; src=a.dataset or root/'evaluation/gate13-candidates.json'
    sha=hashlib.sha256(src.read_bytes()).hexdigest()
    assert sha==src.with_suffix('.sha256').read_text().split()[0]
    model=LocalNLI(a.model_dir);rows=[];started=time.perf_counter()
    matrix={k:{v:0 for v in (*VERDICTS,'ERROR')} for k in VERDICTS}
    for case in json.loads(src.read_text())['cases']:
        inp=case['input'];claim=dict(inp['claim']);claim['source_ids']=inp['cited_evidence_ids']
        bundle={'synthetic':case['synthetic'],'claim':claim,'evidence':inp['evidence']}
        expected=case['expected']['verdict'];expected='INSUFFICIENT_EVIDENCE' if expected=='INSUFFICIENT' else expected
        row={'case_id':case['case_id'],'expected_original':case['expected'],'adapted_bundle':bundle}
        try:
            result=review_lite(bundle,Unavailable() if case.get('test_mode')=='fault_injection' else model)
            row['result']=result
            if result['status']=='INVALID_REFERENCE': row['evaluation_group']='reference_guard';row['pass']=bool(set(claim['source_ids'])-{e['id'] for e in inp['evidence']})
            else:
                row['evaluation_group']='semantic';row['pass']=result['verdict']==expected
                if expected in matrix: matrix[expected][result['verdict']]+=1
        except Exception as exc:
            row.update({'error':str(exc),'evaluation_group':'fault_injection' if case.get('test_mode')=='fault_injection' else 'unexpected_error','pass':case.get('test_mode')=='fault_injection' and str(exc)=='Injected model unavailable'})
            if row['evaluation_group']=='unexpected_error' and expected in matrix: matrix[expected]['ERROR']+=1
        rows.append(row)
    f1=[];metrics={}
    for label in VERDICTS:
        tp=matrix[label][label];fp=sum(matrix[k][label] for k in VERDICTS if k!=label);fn=sum(v for k,v in matrix[label].items() if k!=label)
        precision=tp/(tp+fp) if tp+fp else None
        score=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0
        f1.append(score);metrics[label]={'precision':precision,'f1':score,'expected_count':sum(matrix[label].values())}
    report={'generated_at':datetime.now(timezone.utc).isoformat(),'dataset_sha256':sha,'model':model.provenance,'threshold':0.8,'cases':len(rows),'passed_under_declared_adapter':sum(r['pass'] for r in rows),'groups':{g:{'total':sum(r['evaluation_group']==g for r in rows),'passed':sum(r['evaluation_group']==g and r['pass'] for r in rows)} for g in sorted({r['evaluation_group'] for r in rows})},'semantic_macro_f1':sum(f1)/3,'semantic_supported_precision':metrics['SUPPORTED']['precision'],'semantic_matrix':matrix,'semantic_metrics':metrics,'failed_case_ids':[r['case_id'] for r in rows if not r['pass']],'elapsed_seconds':round(time.perf_counter()-started,2),'full_original_contract_accepted':False,'performance_thresholds_met':sum(f1)/3>0.80 and metrics['SUPPORTED']['precision'] is not None and metrics['SUPPORTED']['precision']>0.90,
    'adapter_disclosures':['Input cited_evidence_ids maps to claim.source_ids; evidence text and candidate labels unchanged.','INSUFFICIENT maps to INSUFFICIENT_EVIDENCE. Missing references assessed as blocked before inference, not exact original status/verdict equality.','T20 intentionally injects an exception; it is not real model inference and is excluded from semantic scores.','No added temporal metadata or numeric calculator. Current cue-based guards may abstain before inference on numeric claims, quoted text, gaps, uncertainty or detected subject mismatch. Source_id/finalized/source_quote fields are not authenticated.','Current Lite checks eligible uncited context for contradiction; uncited support cannot establish a claim. Out-of-scope context is logged as excluded.','All reports require human review; original expected review_required=false is not accepted as a product change.','Candidate labels are authored and unadjudicated; metrics do not prove generalization. Original benchmark remains unchanged.','Upstream evaluate_predictions.py was not used: it combines fault injection with invalid-input accounting and omits semantic mismatches from failed_case_ids.'], 'results':rows}
    (root/'reports'/a.output).write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
if __name__=='__main__':main()
