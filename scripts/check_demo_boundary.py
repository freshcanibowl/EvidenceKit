"""Conservative source-level check, not runtime security proof."""
from pathlib import Path
import ast
import sys

source = Path('src/open_evidencekit/demo.py').read_text(encoding='utf-8')
tree = ast.parse(source)
launches = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'launch']
if len(launches) != 1:
    sys.exit('FAIL: expected one explicit launch() call')
kwargs = {k.arg: k.value for k in launches[0].keywords}
if not (isinstance(kwargs.get('server_name'), ast.Constant) and kwargs['server_name'].value == '127.0.0.1'):
    sys.exit('FAIL: demo launch must explicitly bind to 127.0.0.1')
if not (isinstance(kwargs.get('share'), ast.Constant) and kwargs['share'].value is False):
    sys.exit('FAIL: demo launch must explicitly set share=False')
print('PASS: demo launch static loopback/share boundary')
