from pathlib import Path
from open_evidencekit.preflight import inspect
from open_evidencekit.security import scan


def test_preflight_does_not_claim_inference():
    result = inspect()
    assert result['inference_executed'] is False
    assert result['network_access_performed'] is False
    assert result['model_license'].startswith('UNVERIFIED')


def test_security_scan_detects_secret_and_import(tmp_path):
    (tmp_path/'x.py').write_text('import caios\n')
    (tmp_path/'key.txt').write_text('-----BEGIN ' + 'PRIVATE KEY-----')
    findings = scan(tmp_path)
    assert {x['reason'] for x in findings} == {'private_key', 'private_project_import'}


def test_security_scan_ignores_generated_caches(tmp_path):
    cache = tmp_path/'__pycache__'
    cache.mkdir()
    (cache/'bad.py').write_text('import pair')
    assert scan(tmp_path) == []
