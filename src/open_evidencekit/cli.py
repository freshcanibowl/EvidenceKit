import argparse
import json
import sys
from .core import load_bundle, review
from .ai import explain_local

def main(argv=None):
    parser = argparse.ArgumentParser(description="Review synthetic evidence bundles")
    parser.add_argument("input", help="JSON evidence bundle")
    parser.add_argument("--output", help="Write JSON report to file")
    parser.add_argument("--local-ai", action="store_true", help="Run cached open-weight model; fail if unavailable")
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    args = parser.parse_args(argv)
    try:
        result = review(load_bundle(args.input))
        if args.local_ai:
            result["ai_assistance"] = explain_local(result, model=args.model)
        output = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            from pathlib import Path
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"EvidenceKit error: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
