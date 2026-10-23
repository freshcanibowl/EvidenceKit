---
title: I Was Too Lazy to Check Every Citation, So I Built a Local Evidence Reviewer
published: false
tags: devchallenge, hf26challenge, opensource, ai
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

> Draft review gate: verify actual development-start evidence, public links and eligibility; visual browser QA remains incomplete. This post has not been published. Results below describe an experimental prototype, not production validation.

## What I Built

A report says an attachment arrived. The record says it did not. Before trusting the report, I have to compare the claim with its source myself.

Open EvidenceKit Lite prepares that comparison. Give it one English claim and up to five synthetic evidence records. It checks references, applies explicitly supplied time and source constraints, and uses a pinned open-weight natural language inference model to suggest how each piece of evidence relates to the claim.

The lazy part is preparing a consistent first-pass report: source IDs, model scores, rule checks and review reasons in one place. I still have to inspect the evidence. I have not measured a percentage of human time saved.

## Demo

[Watch the Lite 0.3 results walkthrough](https://github.com/freshcanibowl/EvidenceKit/blob/main/demo-guarded-walkthrough.mp4). It visualizes captured real inference and guard results; it is not a browser screen recording. The older Build 3 video remains available as a historical baseline.

The repository also includes a local Gradio app. One example compares “Attachment B was received” with “Attachment B was not received.” The NLI model reports contradiction and exposes its raw scores.

Another example contains a draft quoting “The invoice was paid” without a payment record. Version 0.3 routes that to human review before inference, rather than treating the quote as proof.

Every example is synthetic. Reports can be downloaded as JSON. Six HTTP/API interactions and report downloads have been exercised; visual layout, keyboard and console QA remain incomplete.

## Code

https://github.com/freshcanibowl/EvidenceKit

The application is MIT licensed. Model weights are downloaded separately, not redistributed in the repository. Original smoke tests, stress failures and post-repair results are retained. Repository creation and initial commit dates fall inside the contest window; timestamps do not independently prove the actual start of development.

## How I Built It

The semantic core is [MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli](https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli), pinned to revision `6f5cf0a2b59cabb106aca4c287eed12e357e90eb`. Its upstream model card declares MIT licensing. Transformers and PyTorch run it on CPU; Gradio provides the local interface.

Evidence is the premise and the claim is the hypothesis. The model returns entailment, contradiction and neutral scores. I fixed the threshold at 0.80 before the original evaluation and kept it unchanged through this repair. These are uncalibrated model scores, not probabilities that a fact is true.

Missing references stop inference. Conflicting evidence requires review. Eligible uncited records can veto cited support, but their support cannot establish a claim. Source and time constraints depend on declared metadata; the app does not authenticate sources or reliably extract dates from prose.

### The test that made the project more honest

The initial smoke suite looked encouraging: 40/45 semantic classifications matched the authored labels, with Macro-F1 0.886 and support precision 1.00. Fifteen rule cases were blocked as expected and excluded from semantic metrics.

The wider candidate set was less flattering: 37/50 semantic matches, Macro-F1 0.758 and support precision 0.857. A separate 12-probe set included a false support judgment for a quoted payment claim. The model also confused missing observation with contradiction, and failed an arithmetic comparison.

I retained the failures instead of changing labels or selecting only successful examples.

### Making it do less, deliberately

The repair adds an explicit abstention layer. Claims containing digits, evidence with selected quotation marks, certain uncertainty or observation-gap phrases, and detected leading-subject mismatches are sent to human review. These incomplete English heuristics can reject easy inputs too. They do not calculate, authenticate a quote, or recognize every entity.

If a guard fires, the report says so and includes no invented model scores. If inference fails, the app errors; it does not substitute simulated AI output. The NLI model remains responsible for semantic suggestions on eligible direct-text pairs.

| Measured set | Semantic matches after repair | Macro-F1 | Support precision |
|---|---:|---:|---:|
| Existing Gate 13 regression candidates | 41/50 | 0.819 | 1.000 |
| Existing adversarial regression probes | 11/12 | 0.937 | 1.000 |
| New developer-authored probes | 20/24 | 0.838 | 1.000 |

The 24 new probes were frozen after the implementation but before their first run. They are not independent validation. Their four mismatches are abstentions on numeric or quoted statements, showing the cost in coverage. Existing suites are regression tests after this repair, not held-out evidence. Nine reference checks and one intentional model-error injection are reported separately. Fifty unit/regression tests pass.

[The complete review](https://github.com/freshcanibowl/EvidenceKit/blob/main/docs/GUARDED_REVIEW.md) explains the schema adapter, incomplete guards and remaining gaps. The original candidate labels still need independent adjudication, particularly on temporal cases.

The model still wrongly calls “The cat stood near the bowl” a contradiction of “The cat ate its meal.” That failure remains in the demo. Human review is not a decorative checkbox.

## Why Does Open Innovation Matter?

For this task, I want control over where the evidence goes and how a model suggestion becomes a report.

After first downloading dependencies and weights, the adapter loads local files only. I exercised the example runs in a Python process with socket connection calls blocked. It recorded no connection attempts. That is a process-level offline check, not a full operating-system air-gap audit.

Open weights let me fix a revision, record checksums, inspect label mappings, and retain the same model while changing the surrounding review policy. No hosted inference API is needed after setup. Hardware, storage and electricity still cost money.

A closed API could perform NLI too. The demonstrated benefit here is control and inspectability: local weights, visible abstention rules, reproducible reports and published mistakes. It does not mean open models are automatically more accurate.

I used AI assistance to extend an independent Python scaffold, write checks, and inspect failures. No private CAIOS, PAIR or CARLi code or real customer records were imported. The Gate 13 fixture snapshot credits its preflight origins; those fixtures are not claimed as new application code.

## What I Would Improve Next

I would independently adjudicate labels, validate on independently authored inputs, and improve numeric, entity and temporal handling without hiding abstentions. I would also complete visual/keyboard QA and a timed manual-versus-assisted review experiment.

For now, this is a small local tool that automates comparison and report preparation while keeping the evidence, model scores and limitations available for a person to review.
