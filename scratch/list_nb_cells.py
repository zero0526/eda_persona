import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path('notebooks/eda_action_logs.ipynb')
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, cell in enumerate(nb['cells']):
    cell_type = cell['cell_type']
    source = ''.join(cell['source'])
    first_line = source.split('\n')[0] if source else ''
    if cell_type == 'markdown':
        print(f"Cell {i:2d} [MD]  : {first_line[:85]}")
    else:
        print(f"Cell {i:2d} [CODE]: {first_line[:85]}")
