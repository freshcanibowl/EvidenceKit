"""Single-claim evidence relations, never independent fact verification."""
from datetime import datetime
import hashlib
import json
import math
import time

THRESHOLD = 0.80  # Frozen before evaluation; softmax scores are not calibrated.
VERDICTS = ('SUPPORTED','CONTRADICTED','INSUFFICIENT_EVIDENCE')

def stamp(value):
    if not isinstance(value,str): raise ValueError('Timestamp must be an ISO-8601 string')
    result = datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None: raise ValueError('Timezone is required')
    return result

def validate(bundle):
    if not isinstance(bundle,dict) or bundle.get('synthetic') is not True:
        raise ValueError('This demo accepts synthetic=true bundles only')
    claim, evidence = bundle.get('claim'), bundle.get('evidence')
    if not isinstance(claim,dict) or not isinstance(evidence,list) or not 1<=len(evidence)<=5:
        raise ValueError('One claim and 1–5 evidence records are required')
    for field in ('id','text'):
        if not isinstance(claim.get(field),str) or not claim[field].strip(): raise ValueError('Claim id and text are required')
    if len(claim['text'])>2000: raise ValueError('Claim exceeds 2000 characters')
    refs=claim.get('source_ids')
    if not isinstance(refs,list) or not refs or any(not isinstance(r,str) or not r.strip() for r in refs) or len(set(refs))!=len(refs):
        raise ValueError('source_ids must be a nonempty list of unique IDs')
    ids=[]
    for e in evidence:
        if not isinstance(e,dict): raise ValueError('Evidence must be an object')
        for field in ('id','text','source_type'):
            if not isinstance(e.get(field),str) or not e[field].strip(): raise ValueError('Evidence id, text and source_type are required')
        if len(e['text'])>4000: raise ValueError('Evidence exceeds 4000 characters')
        stamp(e.get('observed_at'))
        ids.append(e['id'])
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate evidence IDs')
    allowed=claim.get('allowed_source_types')
    if allowed is not None and (not isinstance(allowed,list) or not allowed or any(not isinstance(s,str) or not s for s in allowed)):
        raise ValueError('allowed_source_types must be a nonempty string list')
    bounds=claim.get('time_range')
    if bounds is not None:
        if not isinstance(bounds,dict): raise ValueError('time_range must contain start and end')
        if stamp(bounds.get('start'))>stamp(bounds.get('end')): raise ValueError('Reversed time range')
    # Temporal aggregation is beyond single-pair NLI; explicit declaration is mandatory.
    if not isinstance(claim.get('requires_temporal_aggregation',False),bool):
        raise ValueError('requires_temporal_aggregation must be boolean')
    return claim, {e['id']:e for e in evidence}

def review_lite(bundle, predictor):
    started=time.perf_counter()
    claim,lookup=validate(bundle)
    refs=claim['source_ids']
    missing=sorted(set(refs)-lookup.keys())
    present=[lookup[r] for r in refs if r in lookup]
    bounds=claim.get('time_range')
    wrong_time=[e['id'] for e in present if bounds and not stamp(bounds['start'])<=stamp(e['observed_at'])<=stamp(bounds['end'])]
    allowed=claim.get('allowed_source_types')
    wrong_source=[e['id'] for e in present if allowed and e['source_type'] not in allowed]
    checks={'all_source_ids_exist':not missing,'time_consistency':not wrong_time,'source_types_compatible':not wrong_source}
    reasons=[]
    rows=[]
    if not all(checks.values()):
        status='INVALID_REFERENCE'
        verdict='INSUFFICIENT_EVIDENCE'
        reasons=['INVALID_REFERENCE']
    else:
        status='REVIEWED'
        for e in present:
            raw=predictor.predict(e['text'],claim['text'])
            scores=raw['scores']
            if set(scores)!={'entailment','neutral','contradiction'} or any(not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in scores.values()) or abs(sum(scores.values())-1)>0.001:
                raise ValueError('Invalid model score distribution')
            label=max(scores,key=scores.get)
            relation=({'entailment':'SUPPORTED','contradiction':'CONTRADICTED'}.get(label,'INSUFFICIENT_EVIDENCE')
                      if scores[label]>=THRESHOLD else 'INSUFFICIENT_EVIDENCE')
            rows.append({'evidence_id':e['id'],'verdict':relation,**raw})
        relations={r['verdict'] for r in rows}
        if {'SUPPORTED','CONTRADICTED'}<=relations:
            verdict='INSUFFICIENT_EVIDENCE'; reasons=['CONFLICTING_EVIDENCE']
        elif claim.get('requires_temporal_aggregation',False):
            verdict='INSUFFICIENT_EVIDENCE'; reasons=['TEMPORAL_AGGREGATION_REQUIRES_REVIEW']
        elif 'CONTRADICTED' in relations:
            verdict='CONTRADICTED'; reasons=['MODEL_CONTRADICTION']
        elif 'SUPPORTED' in relations:
            verdict='SUPPORTED'; reasons=['MODEL_ENTAILMENT']
        else:
            verdict='INSUFFICIENT_EVIDENCE'; reasons=['NEUTRAL_OR_LOW_CONFIDENCE']
    return {'schema':'open-evidencekit-lite/0.2','status':status,'claim_id':claim['id'],
            'verdict':verdict,'reason_codes':reasons,'human_review_required':True,
            'rule_checks':checks,'missing_ids':missing,'out_of_range_ids':wrong_time,
            'incompatible_source_ids':wrong_source,'per_evidence':rows,
            'model':predictor.provenance if rows else None,'threshold':THRESHOLD,
            'input_sha256':hashlib.sha256(json.dumps(bundle,sort_keys=True).encode()).hexdigest(),
            'elapsed_ms':round((time.perf_counter()-started)*1000,2),
            'limitations':'Relations to supplied text only; not truth, source authenticity or medical advice. Scores are uncalibrated. Temporal/source rules use caller-declared metadata, not automatic extraction.'}
