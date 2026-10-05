import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

nb = json.load(open('notebooks/eda_action_logs.ipynb', encoding='utf-8'))
for i, c in enumerate(nb['cells']):
    src = ''.join(c.get('source', []))
    for line in src.split('\n'):
        if line.startswith('# ') or line.startswith('## '):
            print(f"Cell {i:02d} [{c.get('cell_type')}]: {line}")
