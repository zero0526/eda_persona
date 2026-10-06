import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

nb = json.load(open('notebooks/eda_action_v2.ipynb', encoding='utf-8'))
for i in range(14, min(19, len(nb['cells']))):
    c = nb['cells'][i]
    src = ''.join(c.get('source', []))
    print(f"=== Cell {i} ({c['cell_type']}) ===")
    print(src[:400])
    print("-" * 50)
