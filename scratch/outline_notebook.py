import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for idx, cell in enumerate(nb['cells']):
    c_type = cell['cell_type']
    source = ''.join(cell['source'])
    lines = [l.strip() for l in source.strip().split('\n') if l.strip()]
    if c_type == 'markdown':
        headers = [l for l in lines if l.startswith('#')]
        print(f"Cell {idx:2d} [MD]:   {headers}")
    else:
        # code cell
        code_comments = [l for l in lines if l.startswith('# BƯỚC') or ('===' in l and 'print' in l)]
        first_line = lines[0] if lines else ''
        print(f"Cell {idx:2d} [CODE]: {code_comments[:2]} | {first_line[:50]}")
