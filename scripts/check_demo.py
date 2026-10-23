"""Real Gradio HTTP/API smoke check, requires downloaded local model."""
import json
from pathlib import Path
import urllib.request
from gradio_client import Client
from open_evidencekit.demo import build_demo,EXAMPLES,example_bundle

def main():
    app=build_demo()
    app.launch(server_name='127.0.0.1',server_port=7861,share=False,prevent_thread_lock=True,quiet=True)
    try:
        status=urllib.request.urlopen('http://127.0.0.1:7861',timeout=20).status
        assert status==200
        client=Client('http://127.0.0.1:7861',verbose=False)
        rows=[]
        for title,claim,evidence in EXAMPLES:
            result=client.predict(json.dumps(example_bundle(claim,evidence)),api_name='/review')
            assert isinstance(result[1],dict) and result[1]['human_review_required'] is True
            exists=Path(result[2]).is_file()
            assert exists
            rows.append({'example':title,'summary':result[0],'report':result[1],'download_exists':exists})
            print(title,result[0])
        Path('reports/demo-api-check.json').write_text(json.dumps({'http_status':status,'transport':'Gradio client over loopback HTTP','browser_visual_qa':'Not performed: Browser initialization timed out. API validation is not visual validation.','examples':rows},indent=2))
    finally: app.close()
if __name__=='__main__': main()
