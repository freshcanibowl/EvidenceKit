"""Offline-only environment and artifact preflight. Never downloads weights."""
from __future__ import annotations
import importlib.metadata as metadata
import importlib.util
import json
import os
from pathlib import Path

DEFAULT_MODEL = 'Qwen/Qwen2.5-0.5B-Instruct'

def inspect(model: str = DEFAULT_MODEL) -> dict:
    packages = {}
    for name in ('transformers', 'torch', 'pytest', 'setuptools'):
        try:
            packages[name] = {'installed': True, 'version': metadata.version(name)}
        except metadata.PackageNotFoundError:
            packages[name] = {'installed': False, 'version': None}
    cache = Path(os.environ.get('HF_HUB_CACHE', str(Path.home()/'.cache/huggingface/hub')))
    model_folder = cache / ('models--' + model.replace('/', '--'))
    snapshots = model_folder/'snapshots'
    revisions = sorted(x.name for x in snapshots.iterdir() if x.is_dir()) if snapshots.is_dir() else []
    return {
        'schema': 'open-evidencekit-preflight/0.2',
        'model': model,
        'model_license': 'UNVERIFIED: verify upstream model card and pinned revision',
        'packages': packages,
        'cached_snapshot_revisions': revisions,
        'ready_for_inference': packages['transformers']['installed'] and packages['torch']['installed'] and bool(revisions),
        'inference_executed': False,
        'network_access_performed': False,
        'note': 'Cache presence does not prove that inference succeeds or model license is cleared.'
    }

def main():
    print(json.dumps(inspect(), indent=2))

if __name__ == '__main__':
    main()
