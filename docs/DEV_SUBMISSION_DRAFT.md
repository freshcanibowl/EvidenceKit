---
title: I Was Too Lazy to Check Every Citation, So I Built a Local Evidence Reviewer
published: false
tags: devchallenge, hf26challenge, opensource, ai
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

> Draft gate: review the public code/video links below, confirm development-window eligibility, perform visual QA, and confirm this account has not already entered this challenge before publishing. This draft has not been submitted.

## What I Built

A report says an attachment arrived. The underlying record says it did not. Before I can trust the report, I have to compare the claim with the record myself.

Open EvidenceKit Lite prepares that comparison. Give it one English claim and up to five evidence records. It checks whether the references exist, applies any explicitly supplied source and time constraints, and runs an open-weight natural language inference model on each claim–evidence pair. The output is a review report with source IDs, relation scores, reasons, and the exact model revision.

The lazy part is the first pass: one action prepares a consistent set of comparisons instead of making me repeat the same reading and formatting steps. It does not remove the final human review, and I have not measured how much human time it saves.

## Demo

[Watch the captured-results walkthrough](https://github.com/freshcanibowl/EvidenceKit/blob/main/demo-results-walkthrough.mp4) — captioned walkthrough of actual saved inference results, including a failure. This is a results visualization, not a browser screen recording.

You can also run the local Gradio app from the repository. The examples cover support, contradiction, insufficient evidence, and a known misclassification. Every example is synthetic.

For the clearest example:

- Claim: “Attachment B was received.”
- Evidence E-1: “Attachment B was not received.”
- Result: `CONTRADICTED`.

For a less obvious one:

- Claim: “The parcel was delivered.”
- Evidence E-1: “A parcel label was printed.”
- Result: `INSUFFICIENT_EVIDENCE`.

You can inspect the raw scores and download the report as JSON.

## Code

https://github.com/freshcanibowl/EvidenceKit

The application is MIT licensed. Model weights are downloaded separately from the upstream publisher and are not bundled with the application archive. The repository includes setup instructions, the frozen synthetic evaluation set, raw results, dependency metadata, model checksums, and a read-only GitHub chronology collector.

## How I Built It

The core AI is [`MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`](https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli), pinned to revision `6f5cf0a2b59cabb106aca4c287eed12e357e90eb`. Its upstream model card declares MIT licensing.

This is a natural language inference model, not a chat model. Evidence is the premise and the claim is the hypothesis. Transformers and PyTorch run it locally on CPU; Gradio provides the interface. The model performs the semantic task: a rule checker alone cannot decide that printing a shipping label does not establish delivery.

I fixed the score threshold at 0.80 before the evaluation. Lower-confidence relations become insufficient evidence. Missing references, incompatible declared source types, or out-of-range timestamps prevent inference. Conflicting support and contradiction produce an insufficient result with a conflict reason. Every result still requires human review.

The application does not silently truncate long inputs, download models during a review, or replace a failed model call with simulated AI output. It does not authenticate sources or automatically extract time constraints from prose. Cross-day claims must be explicitly marked for temporal aggregation and are routed to human review.

I used AI assistance to extend an independent Python scaffold, write checks, and inspect results. The build does not import private application code or production data.

### What the test actually showed

Before running inference, I froze 60 synthetic cases and saved their SHA-256 hash. Fifteen exercise reference, time and source rules. The remaining 45 test semantic relations: 15 support, 15 contradiction, and 15 insufficient-evidence examples.

| Measurement | Result |
|---|---:|
| Cases completed without errors | 60/60 |
| Expected outcomes matched | 55/60 |
| Semantic classifications matched | 40/45 |
| Rule cases blocked as expected | 15/15 |
| Semantic Macro-F1 | 0.886 |
| Precision of predicted support | 1.00, from 15 predicted supports |
| Unit and regression tests | 42 passed |
| Median semantic review call | 160.84 ms in the initial Linux CPU evaluation |

These are small, developer-authored smoke tests, not an independent held-out benchmark. The 15 rule cases are excluded from semantic metrics. I did not tune the threshold after seeing this evaluation.

### The failure I am keeping in the demo

“The cat stood near the bowl” does not establish that the cat ate, but it also does not establish that the cat did not eat.

The model called that pair a contradiction. It made the same kind of mistake on four other insufficient-evidence examples. A high model score did not make those judgments correct.

I kept every failed result and added the cat example to the interface. This is why the output says human review is required, and why I describe the tool as an evidence reviewer rather than a truth detector. The current synthetic suite also does not complete all the adversarial coverage envisioned in the original specification.

## Why Does Open Innovation Matter?

For this task I want control over where the evidence goes and how the model's result is handled.

After downloading the dependencies and weights, the model loads from local files. I exercised inference in a separate Python process where socket connection calls were blocked. The cached model produced the example reports with no recorded connection attempts. This is a process-level offline check, not a full operating-system air-gap audit.

Open weights let me fix the model revision, record checksums, inspect the label mapping, and change the surrounding decision rules without a hosted inference API. There is no per-request hosted inference fee on this path, although hardware, storage and electricity still have costs.

A closed API could perform this task too. What this approach gives me is a local, inspectable setup whose weights and review behavior I control. Its limitations are visible as well: I can publish the exact failures instead of presenting a confident answer as proof.

## What I Would Improve Next

I would add independently authored adversarial cases, test numeric and temporal claims more rigorously, and run a timed comparison of manual review versus assisted review. I would also complete visual and keyboard QA on the local interface; current verification covers HTTP/API interactions and report downloads.

For now, the payoff is modest and concrete: the repetitive comparison and report preparation are automated, while the evidence IDs, model scores and mistakes remain available for a person to inspect.
