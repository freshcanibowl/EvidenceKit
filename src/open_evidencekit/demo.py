"""Loopback-only demo. Review is offline; download is a separate explicit step."""
import json
import tempfile
from functools import lru_cache
from pathlib import Path
from open_evidencekit.lite import review_lite
from open_evidencekit.nli import LocalNLI

EXAMPLES=[
 ('Supported','The parcel was delivered.','The parcel was delivered this morning.'),
 ('Contradicted','Attachment B was received.','Attachment B was not received.'),
 ('Insufficient','The parcel was delivered.','A parcel label was printed.'),
 ('Known failure: expected insufficient','The cat ate its meal.','The cat stood near the bowl.'),
 ('Guarded: quotation','The invoice was paid.','The draft contains the sentence "The invoice was paid", but no payment record is available.'),
 ('Guarded: different leading subjects','Luna ate breakfast.','Pika ate breakfast. Nothing was recorded about Luna.'),
]

def example_bundle(claim,evidence):
    return {'synthetic':True,'claim':{'id':'C-1','text':claim,'source_ids':['E-1']},
            'evidence':[{'id':'E-1','text':evidence,'source_type':'synthetic_log','observed_at':'2026-10-21T10:00:00Z'}]}

@lru_cache(maxsize=1)
def model(): return LocalNLI()

def run_review(raw):
    if len(raw.encode())>32000: raise ValueError('Input exceeds 32KB')
    report=review_lite(json.loads(raw),model())
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',prefix='evidencekit-',delete=False,encoding='utf-8') as f:
        json.dump(report,f,indent=2); path=f.name
    summary=f"{report['verdict']} — {', '.join(report['reason_codes'])}. Human review required."
    return summary,report,path

def build_demo():
    import gradio as gr
    with gr.Blocks(title='Open EvidenceKit Lite',analytics_enabled=False) as demo:
        gr.Markdown('# Open EvidenceKit Lite\nLet a local open model prepare your evidence review.\n\nOne English claim, up to five synthetic evidence records. Relations to supplied text only; human review required. No records are sent to an inference API.')
        gr.Markdown('**Experimental: human review remains required.** Version 0.3 abstains on numeric claims, quoted text and selected risk cues, and checks eligible uncited context for counterevidence. These incomplete English heuristics can miss risks or abstain unnecessarily. The model can still confuse missing information with contradiction. Review original evidence yourself.')
        raw=gr.Textbox(label='Synthetic evidence bundle (JSON)',lines=15,value=json.dumps(example_bundle(*EXAMPLES[1][1:]),indent=2))
        gr.Examples([[json.dumps(example_bundle(*e[1:]),indent=2)] for e in EXAMPLES],inputs=raw,label='Try: supported / contradicted / insufficient / known model failures')
        button=gr.Button('Prepare my review',variant='primary')
        summary=gr.Textbox(label='Review result')
        report=gr.JSON(label='Evidence relations, scores and provenance')
        download=gr.File(label='Download report')
        button.click(run_review,raw,[summary,report,download],api_name='review',concurrency_limit=1)
        gr.Markdown('First run: explicitly download the pinned model with `python -m open_evidencekit.nli --download`. After setup, inference loads local files only. Scores are uncalibrated model outputs. Runtime errors stop the review; there is no simulated AI fallback. Temporal rules require caller-declared time ranges; cross-day claims require manual review. Reports are temporary local files; restart/clear the temp directory to remove them.')
    return demo

if __name__=='__main__':
    build_demo().queue(max_size=8).launch(server_name='127.0.0.1',server_port=7860,share=False,inbrowser=False)
