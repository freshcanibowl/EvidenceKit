# Additional stress evaluation — HOLD

This extends the initial Build 3 smoke evaluation. It does not replace or tune that benchmark. The application is an experimental review assistant; the original performance acceptance targets have not been met on this wider candidate set.

| Dataset | Semantic correct | Macro-F1 | Precision of predicted support |
|---|---:|---:|---:|
| Original 60-case smoke suite (45 semantic) | 40/45 | 0.886 | 1.000 (15 supports) |
| Gate 13 candidates (50 semantic) | 37/50 | 0.758 | 0.857 (14 supports) |
| Additional adversarial probes | 10/12 | 0.792 | 0.500 (2 supports) |

Nine Gate 13 missing-reference cases were blocked before inference. A separate intentional model-error injection propagated its exception. These ten cases are excluded from semantic metrics. Neither new dataset clears both frozen targets: Macro-F1 >0.80 and support precision >0.90.

These datasets contain authored synthetic labels, not independent adjudication. Counts are small. T53–T60 temporal labels are explicitly provisional: different timestamps can describe different events; the model often assumes contradiction. They need independent review, rather than automatic relabeling to improve scores.

## Observed problems

- T06: contradictory evidence was supplied but only one item was cited. Lite currently reviews only cited sources; the candidate expects all-source conflict detection. This is a scope/contract mismatch that can still mislead users if unstated.
- T08: incorrect arithmetic (2.2 kg claimed versus a 1.2 kg increase) was marked supported. NLI is not a reliable calculator.
- T04/T13/T16/T38 and several temporal cases: limited or absent observation was treated as contradiction.
- A04: a quoted sentence about payment, explicitly lacking payment records, was wrongly marked supported.
- A12: evidence about Pika with no information about Luna was treated as contradiction of a Luna claim.

The demo now highlights stress-validation failure and exposes quotation/entity failure examples. No threshold was changed, no labels were altered, and no new semantic rule was added to fit these cases.

## Adapter and measurement boundaries

Gate 13 uses a different schema. Its original input and expected labels are retained in evaluation/gate13-candidates.json. The runner maps cited_evidence_ids to claim.source_ids and INSUFFICIENT to INSUFFICIENT_EVIDENCE. Original reason codes, review flags, finalized/source_quote semantics and exact invalid-input statuses are not implemented or certified. Full contract acceptance remains false.

The original Gate 13 score utility was not used: it counts the model-error case alongside invalid inputs and does not add ordinary semantic mismatches to failed_case_ids. The new runner retains every mismatch and records errors explicitly. T20 is fault injection, never described as actual model inference.

## Provenance

The candidate snapshot came from EvidenceKit_Gate13_60_Case_Candidate_Pack_2026-10-24.zip. Its archive SHA-256 is recorded in the snapshot. That pack says T01–T20 are copied preflight fixtures and T21–T60 are new unadjudicated candidates. They are evaluation material, not newly claimed application code. The 12 additional probes and their labels were separately frozen before their first inference run. Dataset SHA-256 files accompany both sets.

Raw results: reports/gate13-real-inference.json and reports/adversarial-real-inference.json. Model/revision/threshold are unchanged from Build 3.

## Remaining work

Independent label adjudication; reliable handling or abstention for arithmetic, quoted propositions, entity identity and temporal coverage; validation on a new held-out set after any change. Do not tune on these published cases and then present the same cases as independent validation.

Browser initialization again timed out. HTTP/API checks do not establish visual layout, keyboard use or console health. Visual QA and evidence of actual development start remain unresolved. No DEV post was published by this work.
