import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("notebooks/eda_action_logs.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for i, cell in enumerate(nb["cells"]):
    cell_type = cell.get("cell_type")
    lines = [l.strip() for l in cell.get("source", []) if l.strip().startswith("#")]
    if lines:
        print(f"Cell {i:02d} [{cell_type}]: {lines[0]}")
    elif cell_type == "markdown":
        first_line = cell.get("source", [""])[0].strip()[:60]
        print(f"Cell {i:02d} [markdown]: {first_line}")
