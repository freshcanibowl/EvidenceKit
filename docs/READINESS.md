# Build 3 readiness

## Completed here
- Actual pinned DeBERTa NLI on CPU, with raw scores and report provenance.
- Gradio local app, HTTP 200, four actual API interactions and report downloads.
- 42 unit tests passed; frozen synthetic evaluation 55/60 expected outcomes, 60/60 completed.
- Python socket-blocked offline check; no attempted connections in that process.
- All five semantic failures retained and a known failure exposed in Demo examples.
- Original source MIT license and declared model license/revision, installed dependency metadata.
- English DEV draft and results walkthrough video, with limitations.

## Remaining gates
1. Public repository confirmed: https://github.com/freshcanibowl/EvidenceKit. Created 2026-10-23 18:41:24 UTC (Oct 24 02:41:24 MYT), within the challenge window. Initial inspection found it empty; Build 3 is being published without backdating. See reports/repository-initial-inspection.json and the live GitHub commit history. Repository metadata does not establish the actual start of development.
2. Executed `python scripts/repository_proof.py freshcanibowl/EvidenceKit`. reports/repository-proof.json records repository creation and both initial commits within the window. It is a snapshot at implementation commit 65789dfb354c3be06f5e2f8ffa927e4426e4e1a0; this documentation commit follows it. GitHub Actions run 40006218763 passed; 49 uploaded file blob hashes matched local files. Timestamps alone do not prove development start or authorship.
3. Visual browser QA not performed: Browser runtime initialization timed out. API checks do not prove layout, keyboard interaction, or console health.
4. Model metrics pass the two numerical targets on this small synthetic suite, but the frozen spec's adversarial coverage is incomplete. Do not claim full SG acceptance, production readiness or independent validation.
5. No human time-savings evidence. Do not publish a savings percentage or include an empirical Lazy Payoff claim.
6. The supplied MP4 is published alongside the source at demo-results-walkthrough.mp4. It is an annotated results walkthrough, not a screen recording. Verify logged-out playback/download access and record browser interaction locally if desired.
7. Replace article blockers, verify public links/logged-out access and publish DEV post with required tags before the official deadline.

Window: 2026-10-19 16:00 UTC through 2026-10-26 06:59 UTC (Malaysia: Oct 20 00:00 through Oct 26 14:59). Source: https://dev.to/page/hacktoberfest-week3-2026-10-19-contest-rules

No automatic claim of eligibility, cloud deployment or final DEV submission. GitHub source publication is separate from contest submission.

## Public verification

Implementation commit: https://github.com/freshcanibowl/EvidenceKit/commit/65789dfb354c3be06f5e2f8ffa927e4426e4e1a0

CI: https://github.com/freshcanibowl/EvidenceKit/actions/runs/40006218763 (unit tests only; local model inference is evidenced separately).

## Wider stress update

HOLD: Gate 13 semantic Macro-F1 0.758 / support precision 0.857. Additional 12-probe set 10/12, Macro-F1 0.792 / support precision 0.500. Both fail the original pair of numerical gates. Original smoke results remain unchanged. See STRESS_REVIEW.md. Browser initialization again timed out. The original public video predates this update. No submission is certified or published.

## Lite 0.3 superseding repair status

See GUARDED_REVIEW.md. Gate 13 regression Macro-F1 0.819 / support precision 1.000; new 24 authored probes 20/24, Macro-F1 0.838 / support precision 1.000. Both numerical targets pass on these measured sets. Guards trade coverage for precision and remain incomplete. Full acceptance, independent adjudication, visual QA and actual development-start evidence remain unresolved. No DEV post has been published. Latest video: demo-guarded-walkthrough.mp4 (captioned captured results, not browser recording). Historical HOLD results above remain as an audit trail.
