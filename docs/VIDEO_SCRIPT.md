# Demo walkthrough

The supplied captioned MP4 visualizes the exact saved inference reports, not a browser screen capture. It is silent and deliberately includes a failure. Use it as an honest results demo, or record the Gradio app on your own computer.

Suggested browser recording (about 90 seconds):
1. Show the local address and the one-claim/five-evidence scope.
2. Run the received/not received attachment example; expand raw scores and pinned revision.
3. Run the shipping-label example: a printed label does not establish delivery.
4. Run the known cat-at-bowl failure. State: the model wrongly calls this contradiction; we retain it and require review.
5. Download the JSON report and show the source IDs.
6. Show `reports/evaluation.json`: 40/45 semantic, 15/15 rules, Macro-F1 0.886.
7. Show `reports/offline-check.json`: sockets blocked; cached local model ran.
8. Close: less repetitive checking, with inspectable local AI; human judgment remains necessary.

Do not claim a percentage of time saved, 100% accuracy or full disconnected-machine testing. No partner category is claimed until actual partner use is evidenced.
