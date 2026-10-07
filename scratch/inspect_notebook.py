import json, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for idx, c in enumerate(nb['cells']):
    c_type = c['cell_type']
    source = ''.join(c['source'])[:100].replace('\n', ' ')
    print(f"Cell {idx:2d} [{c_type:8s}]: {source}")
