"""Bounded lifetime for synthetic, single-user demo download files.

Only files produced in our dedicated private directory are eligible for cleanup.
Cleanup is best-effort at startup and before each new report; no background agent.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import time

PREFIX = "evidencekit-report-"
TTL_SECONDS = 3600
MAX_REPORT_BYTES = 2_000_000


def report_dir() -> Path:
    base = Path(tempfile.gettempdir()) / f"evidencekit-reports-{os.getuid()}" if hasattr(os, "getuid") else Path(tempfile.gettempdir()) / "evidencekit-reports-local"
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    if base.is_symlink() or not base.is_dir():
        raise RuntimeError("Unsafe report directory")
    if os.name == "posix":
        st = base.stat()
        if st.st_uid != os.getuid():
            raise RuntimeError("Report directory ownership mismatch")
        base.chmod(0o700)
    return base


def cleanup_expired(*, now: float | None = None) -> int:
    root = report_dir()
    now = time.time() if now is None else now
    removed = 0
    for entry in root.iterdir():
        if not entry.name.startswith(PREFIX) or entry.suffix != ".json" or entry.is_symlink() or not entry.is_file():
            continue
        if now - entry.stat().st_mtime >= TTL_SECONDS:
            entry.unlink(missing_ok=True)
            removed += 1
    return removed


def save_report(report: dict) -> str:
    root = report_dir()
    cleanup_expired()
    encoded = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
    if len(encoded) > MAX_REPORT_BYTES:
        raise ValueError("Report exceeds size limit")
    fd, path = tempfile.mkstemp(prefix=PREFIX, suffix=".json", dir=root)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(encoded)
        if os.name == "posix":
            os.chmod(path, 0o600)
    except BaseException:
        Path(path).unlink(missing_ok=True)
        raise
    return path
