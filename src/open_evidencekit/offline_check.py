"""Independent offline inference check: Python socket connects are blocked."""
import json
from pathlib import Path
import socket
from open_evidencekit.nli import LocalNLI
from open_evidencekit.lite import review_lite
from open_evidencekit.demo import EXAMPLES,example_bundle

def main():
    attempts=[]
    def denied(self,address):
        attempts.append(str(address))
        raise RuntimeError('Network disabled for offline verification')
    socket.socket.connect=denied
    socket.socket.connect_ex=denied
    model=LocalNLI()
    outputs=[]
    for title,claim,evidence in EXAMPLES:
        outputs.append({'title':title,'claim':claim,'evidence':evidence,'report':review_lite(example_bundle(claim,evidence),model)})
    result={'network_policy':'Python socket connect/connect_ex blocked in this process; not an OS-level air-gap test',
            'network_connect_attempts':attempts,'model':model.provenance,'outputs':outputs}
    root=Path(__file__).resolve().parents[2]
    (root/'reports/offline-check.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
