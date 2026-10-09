import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

c24 = nb['cells'][24]
print("=== CELL 24 SOURCE ===")
print(''.join(c24['source']))

if len(nb['cells']) > 25:
    c25 = nb['cells'][25]
    print("\n=== CELL 25 SOURCE ===")
    print(''.join(c25['source'])[:2000])
