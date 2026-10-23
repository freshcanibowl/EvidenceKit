"""Explicit model setup and offline-only, pinned natural language inference."""
import argparse
import hashlib
import json
from pathlib import Path
import time

MODEL_ID = 'MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli'
REVISION = '6f5cf0a2b59cabb106aca4c287eed12e357e90eb'
MODEL_DIR = Path(__file__).resolve().parents[2] / 'models' / REVISION

class LocalNLI:
    def __init__(self, model_dir=MODEL_DIR):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        torch.set_num_threads(2)
        self.torch = torch
        self.path = Path(model_dir)
        manifest = json.loads((self.path / 'evidencekit-model.json').read_text())
        if manifest['model_id'] != MODEL_ID or manifest['revision'] != REVISION:
            raise ValueError('Model manifest does not match pinned model')
        for name in ('config.json','model.safetensors','spm.model','tokenizer_config.json','special_tokens_map.json'):
            entry = manifest['files'].get(name)
            if entry is None:
                raise ValueError('Missing pinned model file: ' + name)
            h = hashlib.sha256()
            with (self.path / name).open('rb') as stream:
                for block in iter(lambda: stream.read(1024*1024), b''): h.update(block)
            if h.hexdigest() != entry['sha256']:
                raise ValueError('Model file checksum mismatch: ' + name)
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.path), local_files_only=True, use_fast=False, trust_remote_code=False)
        self.model = AutoModelForSequenceClassification.from_pretrained(str(self.path), local_files_only=True, trust_remote_code=False, use_safetensors=True)
        self.model.eval()
        self.labels = {int(k): v.lower() for k,v in self.model.config.id2label.items()}
        if set(self.labels.values()) != {'entailment','neutral','contradiction'}:
            raise ValueError('Unexpected NLI label mapping')

    def predict(self, premise, hypothesis):
        started = time.perf_counter()
        inputs = self.tokenizer(premise, hypothesis, return_tensors='pt', truncation=False)
        if inputs['input_ids'].shape[1] > 512:
            raise ValueError('Pair exceeds 512 tokens; shorten evidence or claim. Nothing was truncated.')
        with self.torch.inference_mode():
            probs = self.model(**inputs).logits.softmax(-1)[0].tolist()
        return {'scores': {self.labels[i]: float(p) for i,p in enumerate(probs)},
                'elapsed_ms': round((time.perf_counter()-started)*1000, 2)}

    @property
    def provenance(self):
        return {'model_id': MODEL_ID, 'revision': REVISION, 'device': 'cpu',
                'local_files_only': True, 'trust_remote_code': False}

def download():
    from huggingface_hub import snapshot_download
    path = Path(snapshot_download(MODEL_ID, revision=REVISION, local_dir=MODEL_DIR,
        allow_patterns=['config.json','model.safetensors','tokenizer*','special_tokens_map.json','spm.model','README.md','LICENSE*']))
    files = {}
    for p in path.iterdir():
        if p.is_file() and p.name != 'evidencekit-model.json':
            h = hashlib.sha256()
            with p.open('rb') as stream:
                for block in iter(lambda: stream.read(1024*1024), b''): h.update(block)
            files[p.name] = {'sha256':h.hexdigest(), 'bytes':p.stat().st_size}
    manifest = {'model_id':MODEL_ID,'revision':REVISION,'license_declared_upstream':'MIT','files':files}
    (path/'evidencekit-model.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--download',action='store_true',required=True,help='Explicit network download of pinned weights')
    parser.parse_args()
    download()
