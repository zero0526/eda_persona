import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("notebooks/eda_action_v2.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    if any(k in src for k in ["df_windows", "bias_reels", "is_late_night", "surface_bias", "duration_min"]):
        print(f"=== Cell {idx} ({cell.get('cell_type')}) ===")
        for line in cell.get("source", []):
            if any(k in line for k in ["df_windows", "bias_reels", "is_late_night", "surface_bias", "duration_min", "SELECT", "FROM"]):
                print("  ", line.rstrip())
