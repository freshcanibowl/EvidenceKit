"""Read-only public GitHub evidence. Does not create, push or rewrite history."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import urllib.request

START='2026-10-19T16:00:00+00:00'
END='2026-10-26T06:59:00+00:00'

def main():
    p=argparse.ArgumentParser(); p.add_argument('repository',help='owner/repo'); args=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',args.repository): p.error('Use owner/repo')
    def get(path):
        req=urllib.request.Request('https://api.github.com/repos/'+args.repository+path,headers={'Accept':'application/vnd.github+json','User-Agent':'OpenEvidenceKit-provenance'})
        with urllib.request.urlopen(req,timeout=30) as r: return json.load(r)
    repo=get(''); commits=[]
    for page in range(1,101):
        batch=get(f'/commits?per_page=100&page={page}')
        commits.extend(batch)
        if len(batch)<100: break
    else: raise RuntimeError('History truncated; no eligibility conclusion emitted')
    start,end=datetime.fromisoformat(START),datetime.fromisoformat(END)
    def within(s): return start<=datetime.fromisoformat(s.replace('Z','+00:00'))<=end
    rows=[{'sha':c['sha'],'url':c['html_url'],'author_date':c['commit']['author']['date'],'committer_date':c['commit']['committer']['date']} for c in commits]
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'repository':repo['full_name'],'url':repo['html_url'],
      'created_at':repo['created_at'],'default_branch':repo['default_branch'],'public':not repo['private'],
      'window_start':START,'window_end':END,'repository_created_in_window':within(repo['created_at']),
      'default_branch_commits':rows,'all_listed_commit_dates_in_window':bool(rows) and all(within(c['author_date']) and within(c['committer_date']) for c in rows),
      'limitations':'Read-only metadata for current default branch, not proof of original authorship or all branches. Commit timestamps are user-controlled; organizer decides eligibility. No dates were rewritten.'}
    Path('reports/repository-proof.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
