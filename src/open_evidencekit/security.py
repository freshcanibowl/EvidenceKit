"""Conservative, offline checks for accidental secrets and private project imports."""
from __future__ import annotations
import re
from pathlib import Path

SENSITIVE = {
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'aws_access_key': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'github_token': re.compile(r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b'),
}
FORBIDDEN_IMPORT = re.compile(r'^\s*(?:from|import)\s+(?:caios|pair|carli)(?:\.|\s|$)', re.I | re.M)
EXTS = {'.py', '.md', '.txt', '.json', '.toml', '.yml', '.yaml'}

def scan(root: Path) -> list[dict]:
    findings = []
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in EXTS or any(s in p.parts for s in ('.git', '.venv', '__pycache__', '.pytest_cache')):
            continue
        if p.stat().st_size > 2_000_000:
            findings.append({'file': str(p.relative_to(root)), 'reason': 'oversized_file_not_scanned'})
            continue
        body = p.read_text(encoding='utf-8', errors='replace')
        for name, pattern in SENSITIVE.items():
            if pattern.search(body):
                findings.append({'file': str(p.relative_to(root)), 'reason': name})
        if p.suffix == '.py' and FORBIDDEN_IMPORT.search(body):
            findings.append({'file': str(p.relative_to(root)), 'reason': 'private_project_import'})
    return findings
