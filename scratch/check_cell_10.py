import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("notebooks/eda_action_v2.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Let's inspect cell 10 code lines
cell_10_src = nb["cells"][10]["source"]
print("Current cell 10 line count:", len(cell_10_src))
