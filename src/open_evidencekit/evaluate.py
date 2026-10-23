"""Report every synthetic benchmark result, including abstentions and errors."""
import hashlib
import json
from pathlib import Path
import platform
import statistics
import time
from datetime import datetime,timezone
from open_evidencekit.lite import review_lite,VERDICTS
from open_evidencekit.nli import LocalNLI,MODEL_DIR

def main():
    root=Path(__file__).resolve().parents[2]
    raw=(root/'evaluation/cases.json').read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    assert sha==(root/'evaluation/FROZEN.sha256').read_text().split()[0]
    started=time.perf_counter(); model=LocalNLI(); load_ms=(time.perf_counter()-started)*1000
    rows=[]
    for case in json.loads(raw)['cases']:
        try:
            result=review_lite(case['bundle'],model)
            ok=result['verdict']==case['expected'] and result['status']==case.get('expected_status','REVIEWED')
            rows.append({'id':case['id'],'category':case['category'],'expected':case['expected'],'pass':ok,'result':result})
        except Exception as e:
            rows.append({'id':case['id'],'category':case['category'],'expected':case['expected'],'pass':False,'error':str(e)})
    semantic=[r for r in rows if r['category'] in ['support','contradiction','insufficient']]
    matrix={e:{p:0 for p in (*VERDICTS,'ERROR')} for e in VERDICTS}
    for r in semantic: matrix[r['expected']][r.get('result',{}).get('verdict','ERROR')]+=1
    f1=[]
    for label in VERDICTS:
        tp=matrix[label][label]; fp=sum(matrix[k][label] for k in VERDICTS if k!=label); fn=sum(v for k,v in matrix[label].items() if k!=label)
        f1.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
    predicted_support=sum(matrix[k]['SUPPORTED'] for k in VERDICTS)
    precision=matrix['SUPPORTED']['SUPPORTED']/predicted_support if predicted_support else None
    times=[r['result']['elapsed_ms'] for r in semantic if 'result' in r]
    import importlib.metadata as meta
    report={'generated_at':datetime.now(timezone.utc).isoformat(),'dataset_sha256':sha,'model':model.provenance,
      'environment':{'python':platform.python_version(),'platform':platform.platform(),'cpu':platform.processor(),
      'dependencies':{k:meta.version(k) for k in ['torch','transformers','gradio','sentencepiece']}},
      'cases':len(rows),'passed':sum(r['pass'] for r in rows),'semantic_cases':len(semantic),
      'semantic_passed':sum(r['pass'] for r in semantic),'semantic_confusion_matrix':matrix,'macro_f1':sum(f1)/3,
      'supported_precision':precision,'model_load_ms':round(load_ms,2),'median_semantic_ms':statistics.median(times) if times else None,
      'total_seconds':round(time.perf_counter()-started,2),
      'gates':{'macro_f1_gt_0_80':sum(f1)/3>0.80,'supported_precision_gt_0_90':precision is not None and precision>0.90},
      'limitations':['Synthetic developer-authored smoke benchmark only, not generalization evidence.','Rule cases excluded from semantic metrics.','No human time-savings experiment has been performed.','Model relation scores do not prove real-world truth.'], 'results':rows}
    (root/'reports/evaluation.json').write_text(json.dumps(report,indent=2))
    (root/'reports/model-manifest.json').write_text((MODEL_DIR/'evidencekit-model.json').read_text())
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
if __name__=='__main__': main()
