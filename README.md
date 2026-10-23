# Open EvidenceKit Lite — HF26 Week 3

Let a local open model prepare your evidence review. One English claim + 1–5 synthetic evidence records → reference/time/source checks → pinned DeBERTa NLI → a review report you can inspect.

**Status: real NLI and Gradio API exercised; not yet a completed submission.** Public repository creation is verified (2026-10-23 18:41:24 UTC). Commit chronology is recorded after initial publication. Visual browser QA, adversarial evaluation coverage and DEV publication remain incomplete. No production system was changed.

## Run (Python 3.11/3.12 recommended)

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --extra-index-url https://download.pytorch.org/whl/cpu -e '.[ai,demo,test]'
python -m open_evidencekit.nli --download
python -m open_evidencekit.demo
```

Open http://127.0.0.1:7860 on the same computer. First setup needs internet to download dependencies and weights. Subsequent review uses local files only. Never use `share=True` for private records; this demo accepts synthetic data only. The recorded environment is Linux CPU; Windows installation has not been exercised.

## Verify

```bash
python -m pytest -q
python -m open_evidencekit.evaluate
python -m open_evidencekit.offline_check
python scripts/repository_proof.py YOUR_OWNER/YOUR_REPO
```

On Linux/macOS you may additionally set `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 GRADIO_ANALYTICS_ENABLED=False`. On PowerShell use `$env:HF_HUB_OFFLINE='1'` and the equivalent for the other variables. `offline_check` blocks Python socket connects during model loading and inference. This is not a full OS air-gap audit.

## Actual results

- 42 unit/regression tests passed at build time (25 legacy + 17 Lite).
- Frozen 60-case synthetic suite: 55 expected outcomes, 60 completed without errors.
- 45 semantic cases: 40 correct; Macro-F1 0.885714; support precision 1.0 (15 predicted supports).
- 15 invalid-reference/time/source cases: all blocked before model calls. These are excluded from semantic metrics.
- Median semantic call: 160.84 ms on this Linux CPU environment; cold model load about 3.03 seconds in the initial evaluation, before startup checksum verification was added. Do not generalize to other devices.
- Five neutral/insufficient cases were wrongly classified as contradiction. The UI includes a known failure example. This is not an independently held-out benchmark or evidence of production accuracy.
- Four Gradio HTTP/API examples returned reports and downloadable JSON. Visual browser QA was blocked by a browser initialization timeout.
- No human time-savings experiment has been performed.

Full raw results, model revision and checksums: `reports/`. The benchmark and threshold were frozen before the first evaluation. Scores are uncalibrated softmax outputs, not probabilities that a fact is true.

## Contract and limits

See `evaluation/cases.json` for inputs. Each bundle declares `synthetic: true`, a `claim` with `id`, `text`, and `source_ids`, and evidence with `id`, `text`, `source_type`, `observed_at` (timezone required). Optional claim `time_range` and `allowed_source_types` are caller-declared; the app does not infer them from prose. Set `requires_temporal_aggregation: true` for cross-day claims: the app abstains. It cannot detect all undisclosed temporal or numeric reasoning.

Output verdicts: `SUPPORTED`, `CONTRADICTED`, `INSUFFICIENT_EVIDENCE`. Invalid metadata has separate `status: INVALID_REFERENCE`, no model call, and an insufficient verdict. Mixed support/contradiction abstains with `CONFLICTING_EVIDENCE`. Every result requires human review. Pair length above 512 tokens errors instead of silently truncating. No automatic model fallback or model download occurs during review.

A caller's source metadata is not authenticated. A model relation is not real-world verification. No clinical, legal or regulatory determination is made. JSON only; no RAG, OCR, uploaded documents, tools, external URL fetching or code execution. UI reports remain as temporary local JSON files until removed. Default loopback binding is for single-user local use only.

The old `evidencekit` CLI and Qwen checklist adapter remain as explicitly legacy code; the new Lite demo does not use user-supplied `stance` or the Qwen adapter.

## Open innovation and attribution

Application code: MIT. Model: [MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli](https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli), revision `6f5cf0a2b59cabb106aca4c287eed12e357e90eb`, upstream model-card license tag MIT. Downloaded model files and weights are not redistributed in the source archive. The manifest records file hashes; startup checks the files used for inference. These checksums are integrity records, not signed provenance.

Transformers (Apache-2.0), PyTorch (BSD-style), Gradio (Apache-2.0), SentencePiece (Apache-2.0); see upstream package notices and `reports/dependency-metadata.json`. That file records installed metadata, not a full legal audit or SPDX SBOM. `requirements-observed.txt` captures the tested Linux environment, including CPU-specific package versions; it is not a cross-platform lockfile.

The open model performs the core semantic relation task. It can run after initial setup without a hosted inference API, and the adapter, thresholds and abstention rules can be inspected. A closed API could perform NLI too; the benefits demonstrated here are control of weights, local processing and inspectability, not exclusive capability or superior accuracy.

## Public links

- Code: https://github.com/freshcanibowl/EvidenceKit
- Results demo video (captioned, not a browser recording): https://github.com/freshcanibowl/EvidenceKit/blob/main/demo-results-walkthrough.mp4
- Direct MP4: https://raw.githubusercontent.com/freshcanibowl/EvidenceKit/main/demo-results-walkthrough.mp4

## Submission materials

- `docs/DEV_SUBMISSION_DRAFT.md` — English article with public-link blockers visibly marked.
- `docs/VIDEO_SCRIPT.md` — walkthrough and browser recording plan.
- `demo-results-walkthrough.mp4` — captioned visualization of captured real model outputs; **not a browser screen recording**.
- `docs/READINESS.md` — current completed and blocked gates.
- `PROVENANCE.md` — independent implementation boundary.

Development history must be genuine. Do not backdate commits or present this ZIP timestamp as GitHub repository proof. Post-deadline changes must be identified in this README before any later update, as required by the challenge.
