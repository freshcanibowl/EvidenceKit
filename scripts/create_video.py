"""Visualize saved real inference reports. This is not a browser recording."""
import json
from pathlib import Path
import subprocess
import tempfile
import textwrap
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1]
r=json.loads((root/'reports/offline-check.json').read_text())
e=json.loads((root/'reports/evaluation.json').read_text())
scenes=[('Open EvidenceKit Lite',[
 'Let a local open model prepare your evidence review.',
 'One claim + up to five synthetic evidence records.',
 'Pinned DeBERTa NLI | CPU | local weights',
 '',
 'This video visualizes captured real inference outputs.',
 'It is not a browser screen recording.',
 'Human review is required for every result.'],8)]
for row in r['outputs']:
 p=row['report']; scores=p['per_evidence'][0]['scores']
 lines=['CLAIM: '+row['claim'],'EVIDENCE E-1: '+row['evidence'],'',
        'ACTUAL MODEL RESULT: '+p['verdict'],
        'Entailment: %.4f   Neutral: %.4f   Contradiction: %.4f' % (scores['entailment'],scores['neutral'],scores['contradiction']),
        'Reason: '+', '.join(p['reason_codes']),
        'Human review required: true']
 if 'Known failure' in row['title']:
  lines+=['','EXPECTED: insufficient evidence. This model result is WRONG.',
           'Standing near a bowl proves neither eating nor not eating.']
 scenes.append((row['title'],lines,12 if 'Known failure' in row['title'] else 9))
scenes+=[('Measured, with limitations',[
 f"Semantic classifications: {e['semantic_passed']}/{e['semantic_cases']}",
 f"Semantic Macro-F1: {e['macro_f1']:.3f}",
 'Support precision: 1.00 (15 predicted supports)',
 'Rule checks: 15/15 | Unit and regression tests: 42 passed',
 'Five insufficient-evidence cases were called contradiction.',
 '',
 'Small developer-authored synthetic set. Not held-out validation.',
 'No human time-savings experiment has been performed.'],10),
 ('Why open innovation matters',[
 'The open-weight model performs the semantic relation task.',
 'Cached model ran with Python socket connection calls blocked.',
 'Network connection attempts in that process: '+str(len(r['network_connect_attempts'])),
 'Fixed revision, file checksums and inspectable decision rules.',
 '',
 'No hosted inference API is needed after setup.',
 'Not a full OS air-gap audit. Not a real-world truth detector.',
 'Less repetitive preparation; a person still reviews the evidence.'],10)]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp); entries=[]
 for i,(title,lines,duration) in enumerate(scenes):
  img=Image.new('RGB',(1280,720),'#101c2a'); d=ImageDraw.Draw(img)
  d.rounded_rectangle((35,25,1245,695),radius=24,fill='#172b3d')
  d.text((65,48),'OPEN EVIDENCEKIT LITE / HF26 WEEK 3',font=ImageFont.truetype(font,18),fill='#80e2c2')
  d.text((65,95),title,font=ImageFont.truetype(font,34),fill='white')
  y=165
  for line in lines:
   for part in textwrap.wrap(line,88) or ['']:
    color='#ffb4a2' if ('WRONG' in part or 'EXPECTED:' in part) else '#d8e6ef'
    d.text((65,y),part,font=ImageFont.truetype(font,23),fill=color); y+=35
  d.text((65,650),f'Captured inference results | Synthetic examples only | {i+1}/{len(scenes)}',font=ImageFont.truetype(font,17),fill='#a9bac7')
  path=tmp/f'{i:02}.png'; img.save(path)
  entries+= ["file '"+str(path)+"'",'duration '+str(duration)]
 entries.append("file '"+str(path)+"'")
 concat=tmp/'frames.txt'; concat.write_text('\n'.join(entries)+'\n')
 subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-vf','fps=15,format=yuv420p','-c:v','libx264','-preset','fast','-crf','23','-movflags','+faststart',str(root/'demo-results-walkthrough.mp4')],check=True)
print('Created',root/'demo-results-walkthrough.mp4')
