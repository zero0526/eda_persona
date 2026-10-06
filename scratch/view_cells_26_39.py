import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

nb = json.load(open('notebooks/eda_action_logs.ipynb', encoding='utf-8'))
for idx in [26, 27, 38, 39]:
    c = nb['cells'][idx]
    print(f"=== Cell {idx} ({c['cell_type']}) ===")
    print(''.join(c.get('source', [])))
    print("=" * 70)
