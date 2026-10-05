import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
nb = json.load(open('notebooks/eda_action_logs.ipynb', encoding='utf-8'))
for i in range(30, len(nb['cells'])):
    c = nb['cells'][i]
    src = ''.join(c.get('source', []))[:120].replace('\n', ' ')
    print(f"Cell {i} ({c.get('cell_type')}): {src}")
