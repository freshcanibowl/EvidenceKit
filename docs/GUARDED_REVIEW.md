# Lite 0.3 — conservative review candidate

## Why change the policy

The NLI model made false support judgments for quoted propositions and arithmetic, and false contradictions for missing observations or different subjects. Separately, the engine ignored uncited counterevidence. Regression tests reproduced the engine gaps before the change (7 failed, 1 passed).

Version 0.3 adds a conservative English cue layer before inference. Claims containing digits, evidence with double/curly quotes or backticks, selected uncertainty/observation-gap cues, and a mismatch between recognized leading named subjects route to `INSUFFICIENT_EVIDENCE`. The report includes explicit guard reasons and no model scores if inference was skipped. This is abstention, not a successful semantic judgment.

Eligible uncited records are now also checked. Their contradiction can veto cited support; their support can never establish a claim. Uncited records outside explicitly declared time/source constraints are excluded and listed. Missing cited references still stop inference.

## Measured tradeoff

Model revision and 0.80 threshold are unchanged. Original datasets and labels are unchanged. Existing stress suites are regression tests after this repair, not held-out validation.

| Suite | Before | Lite 0.3 | Macro-F1 after | Support precision after |
|---|---:|---:|---:|---:|
| Gate 13 semantic candidates | 37/50 | 41/50 | 0.819 | 1.000 |
| Original adversarial probes | 10/12 | 11/12 | 0.937 | 1.000 |
| New authored validation probes | — | 20/24 | 0.838 | 1.000 |

The new 24-case set was authored and frozen after implementation but before inference. It is not independently authored/adjudicated validation. V07/V08/V15/V16 are valid or contradictory numeric/quoted inputs for which the system abstains. This explicitly tests lost coverage rather than removing inconvenient cases. All guard-only cases remain in classification metrics; they are not counted as model inference. See each report's inference_pair_calls and pre_inference_guard_abstentions.

Nine reference errors and one intentional model-error injection still pass separately. Fifty unit/regression tests pass. Six Gradio API interactions/downloads pass. Reports and the 0.3 captioned results walkthrough preserve a remaining cat-near-bowl error.

## Limits, not a universal fix

- The guard layer uses incomplete English regular expressions. It is not entity recognition, a temporal reasoner, an arithmetic engine, or source authentication.
- Digits trigger review even when a numeric statement is directly stated. Number words can be missed.
- Quotation cues can reject genuine quoted observations; unsupported quotation forms may be missed.
- Leading-subject matching recognizes only a restricted grammatical shape and verb list. Other subjects, pronouns and sentence structures are not reliably aligned.
- Observation/uncertainty cues are incomplete and can over-abstain. Unmatched evidence gaps can still become false contradictions.
- Uncited context is limited to the supplied bundle. No external sources are retrieved or verified.
- Improved precision on small developer-authored sets is not a guarantee of correctness or generalization. Some remaining failed cases need label adjudication, particularly temporal cases.

## Acceptance status

The two numerical targets are met on these measured authored suites. Full frozen-contract acceptance is NOT established: independent labels, wider coverage, visual browser QA and actual development-start evidence remain unresolved. The application remains an experimental candidate. No DEV submission has been published. The new video is a captioned visualization of actual reports, not a browser recording.

Files: src/open_evidencekit/guards.py, tests/test_review_guards.py, reports/gate13-postfix.json, reports/adversarial-postfix.json, reports/postfix-validation.json. Historical baseline results remain unchanged in Git history and the original report files.
