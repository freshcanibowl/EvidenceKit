"""Captioned visualization of actual Lite 0.3 results; not a browser recording."""
import json
from pathlib import Path
import subprocess,tempfile,textwrap
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1]
o=json.loads((root/'reports/guarded-offline-check.json').read_text())
g=json.loads((root/'reports/gate13-postfix.json').read_text())
v=json.loads((root/'reports/postfix-validation.json').read_text())
scenes=[('Open EvidenceKit Lite 0.3',[
 'A local open model prepares evidence-review suggestions.',
 'Conservative guards send risky inputs to human review.',
 'Pinned DeBERTa NLI + explicit abstention. CPU only.',
 '',
 'These are captured real results, visualized with captions.',
 'This is not a browser screen recording.',
 'Synthetic examples. Human review always required.'],8)]
for row in o['outputs']:
 r=row['report'];lines=['CLAIM: '+row['claim'],'EVIDENCE: '+row['evidence'],'','RESULT: '+r['verdict'],'Reason: '+', '.join(r['reason_codes'])]
 if r['per_evidence']:
  s=r['per_evidence'][0]['scores'];lines+=['NLI scores: entailment %.4f / neutral %.4f / contradiction %.4f'%(s['entailment'],s['neutral'],s['contradiction'])]
 else: lines+=['Model not called: explicit pre-inference abstention.']
 if 'Known failure' in row['title']: lines+=['','KNOWN ERROR: expected insufficient evidence.','The model still over-interprets a cat near a bowl.']
 scenes.append((row['title'],lines,9))
scenes += [('Measured improvement, with a tradeoff',[
 f"Gate 13 regression: 37/50 -> 41/50 semantic matches.",
 f"Macro-F1: 0.758 -> {g['semantic_macro_f1']:.3f}; support precision: 0.857 -> 1.000.",
 f"New authored validation probes: {v['passed_under_declared_adapter']}/24; Macro-F1 {v['semantic_macro_f1']:.3f}.",
 'The four new-probe errors are numeric/quoted-input abstentions.',
 'Threshold and candidate labels were not changed.',
 '',
 'Small authored datasets, not independent validation.',
 'No measured percentage of human time saved.'],12),
 ('Open weights, visible boundaries',[
 'Pinned local weights perform semantic classification.',
 'Numeric/quoted inputs may skip the model and require review.',
 'Python socket connections blocked during these example runs.',
 'No connection attempts: '+str(len(o['network_connect_attempts'])),
 '',
 'Guards are incomplete English heuristics, not proof of truth.',
 'The model can still confuse an evidence gap with contradiction.',
 'Inspect the raw evidence, scores and reports.'],10)]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp);frames=[]
 for i,(title,lines,seconds) in enumerate(scenes):
  im=Image.new('RGB',(1280,720),'#101c2a');d=ImageDraw.Draw(im);d.rounded_rectangle((35,25,1245,695),radius=24,fill='#172b3d')
  d.text((65,48),'OPEN EVIDENCEKIT LITE 0.3 / HF26 WEEK 3',font=ImageFont.truetype(font,18),fill='#80e2c2')
  d.text((65,95),title,font=ImageFont.truetype(font,31),fill='white');y=165
  for line in lines:
   for part in textwrap.wrap(line,86) or ['']:
    d.text((65,y),part,font=ImageFont.truetype(font,22),fill='#ffb4a2' if 'ERROR' in part else '#d8e6ef');y+=34
  d.text((65,650),f'Captured results | Human review required | {i+1}/{len(scenes)}',font=ImageFont.truetype(font,17),fill='#a9bac7')
  path=tmp/f'{i:02}.png';im.save(path);frames += [f"file '{path}'",f'duration {seconds}']
 frames.append(f"file '{path}'");lst=tmp/'frames.txt';lst.write_text('\n'.join(frames)+'\n')
 subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(lst),'-vf','fps=15,format=yuv420p','-c:v','libx264','-crf','23','-movflags','+faststart',str(root/'demo-guarded-walkthrough.mp4')],check=True)
print('Created demo-guarded-walkthrough.mp4')
