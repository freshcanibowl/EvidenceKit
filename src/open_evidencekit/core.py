"""Deterministic evidence checks; no network, no hidden model calls."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

ALLOWED_VERDICTS = {"supported", "unsupported", "conflict", "needs_review"}


def canonical_hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def review(bundle: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise ValueError("Bundle must be a JSON object")
    claims, evidence = bundle.get("claims"), bundle.get("evidence")
    if not isinstance(claims, list) or not isinstance(evidence, list):
        raise ValueError("Bundle requires claims and evidence arrays")
    if len(claims) > 100 or len(evidence) > 500:
        raise ValueError("Bundle exceeds safety limits")
    ids = [e.get("id") for e in evidence if isinstance(e, dict)]
    if len(ids) != len(evidence) or any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError("Evidence IDs must be unique nonempty strings")
    lookup = {e["id"]: e for e in evidence}
    results = []
    seen_claims = set()
    for c in claims:
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not isinstance(c.get("text"), str):
            raise ValueError("Each claim requires id and text")
        if c["id"] in seen_claims:
            raise ValueError("Duplicate claim ID")
        seen_claims.add(c["id"])
        refs = c.get("evidence_ids", [])
        if not isinstance(refs, list) or any(not isinstance(x, str) for x in refs):
            raise ValueError("evidence_ids must be a list of strings")
        missing = sorted(set(refs) - lookup.keys())
        present = [lookup[x] for x in dict.fromkeys(refs) if x in lookup]
        codes = []
        if missing:
            codes.append("MISSING_EVIDENCE")
        if not refs:
            codes.append("NO_EVIDENCE_REFERENCED")
        if any(not e.get("source") or not e.get("text") for e in present):
            codes.append("INCOMPLETE_SOURCE")
        versions = {str(e.get("version")) for e in present if e.get("version") is not None}
        if len(versions) > 1:
            codes.append("MIXED_VERSIONS")
        stances = {e.get("stance", "unknown") for e in present}
        if not stances.issubset({"supports", "refutes", "unknown"}):
            raise ValueError("Invalid evidence stance")
        if {"supports", "refutes"}.issubset(stances):
            codes.append("CONFLICTING_EVIDENCE")
        if "CONFLICTING_EVIDENCE" in codes:
            verdict = "conflict"
        elif missing or not refs or "INCOMPLETE_SOURCE" in codes or "MIXED_VERSIONS" in codes:
            verdict = "needs_review"
        elif "refutes" in stances and "supports" not in stances:
            verdict = "unsupported"
        elif stances == {"supports"}:
            # A supplied stance is an annotation, not independently verified entailment.
            verdict = "needs_review"
            codes.append("SUPPORT_NOT_INDEPENDENTLY_VERIFIED")
        else:
            verdict = "needs_review"
            codes.append("UNKNOWN_SUPPORT")
        results.append({"claim_id": c["id"], "claim": c["text"], "verdict": verdict,
                        "reason_codes": sorted(set(codes)), "evidence_ids": [e["id"] for e in present],
                        "missing_evidence_ids": missing})
    return {"schema": "open-evidencekit-report/0.1", "input_sha256": canonical_hash(bundle),
            "review_mode": "deterministic", "limitations": "Stances are input annotations, not verified truth. Human review required.",
            "results": results, "counts": {k: sum(x["verdict"] == k for x in results) for k in sorted(ALLOWED_VERDICTS)}}


def load_bundle(path: str, max_bytes: int = 2_000_000) -> dict[str, Any]:
    p = Path(path)
    if p.stat().st_size > max_bytes:
        raise ValueError("Input too large")
    return json.loads(p.read_text(encoding="utf-8"))
