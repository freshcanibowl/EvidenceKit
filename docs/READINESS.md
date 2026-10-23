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
2. Run `python scripts/repository_proof.py owner/repo` from the project root. Review actual GitHub created_at, default-branch commits and originality; timestamps alone do not prove authorship. Do not rewrite history.
3. Visual browser QA not performed: Browser runtime initialization timed out. API checks do not prove layout, keyboard interaction, or console health.
4. Model metrics pass the two numerical targets on this small synthetic suite, but the frozen spec's adversarial coverage is incomplete. Do not claim full SG acceptance, production readiness or independent validation.
5. No human time-savings evidence. Do not publish a savings percentage or include an empirical Lazy Payoff claim.
6. The supplied MP4 is published alongside the source at demo-results-walkthrough.mp4. It is an annotated results walkthrough, not a screen recording. Verify logged-out playback/download access and record browser interaction locally if desired.
7. Replace article blockers, verify public links/logged-out access and publish DEV post with required tags before the official deadline.

Window: 2026-10-19 16:00 UTC through 2026-10-26 06:59 UTC (Malaysia: Oct 20 00:00 through Oct 26 14:59). Source: https://dev.to/page/hacktoberfest-week3-2026-10-19-contest-rules

No automatic claim of eligibility, cloud deployment or final DEV submission. GitHub source publication is separate from contest submission.
