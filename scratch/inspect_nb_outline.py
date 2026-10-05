import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path('notebooks/eda_action_logs.ipynb')
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, c in enumerate(nb['cells']):
    ctype = c['cell_type']
    src = ''.join(c.get('source', []))
    first_line = src.split('\n')[0] if src else ''
    headers = [line for line in src.split('\n') if line.startswith('#')]
    header_str = ' | '.join(headers[:2]) if headers else first_line[:60]
    print(f"Cell {i:2d} [{ctype[:4]}]: {header_str}")
