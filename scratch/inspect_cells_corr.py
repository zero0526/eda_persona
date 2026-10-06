import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("notebooks/eda_action_v2.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx in range(6, 12):
    if idx < len(nb["cells"]):
        cell = nb["cells"][idx]
        print(f"=== Cell {idx} ({cell.get('cell_type')}) ===")
        src = "".join(cell.get("source", []))
        print(src)
        print("-" * 50)
