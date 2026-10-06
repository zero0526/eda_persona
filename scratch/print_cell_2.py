import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("notebooks/eda_action_v2.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print("=== CELL 2 SOURCE ===")
print("".join(nb["cells"][2]["source"]))
