import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for idx, cell in enumerate(nb['cells']):
    src = ''.join(cell['source'])
    headers = [l for l in src.split('\n') if l.strip().startswith('#')]
    if headers:
        print(f"Cell {idx} ({cell['cell_type']}): {headers}")
