import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path('notebooks/eda_action_logs.ipynb')
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i in range(21, len(nb['cells'])):
    c = nb['cells'][i]
    print(f"=== CELL {i} ({c['cell_type']}) ===")
    src = ''.join(c['source'])
    print(src[:400] + ('...' if len(src) > 400 else ''))
