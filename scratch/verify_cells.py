import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("notebooks/notebook_action_logs.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx in [6, 7, 8, 9, 10]:
    cell = nb["cells"][idx]
    print(f"\n==================== CELL {idx} ({cell['cell_type']}) ====================")
    source = "".join(cell.get("source", []))
    print(f"--- SOURCE ---\n{source[:250]}...")
    outputs = cell.get("outputs", [])
    print(f"--- OUTPUTS ({len(outputs)} items) ---")
    for o_idx, out in enumerate(outputs):
        otype = out.get("output_type")
        if otype == "stream":
            text = "".join(out.get("text", []))[:200]
            print(f"  [{o_idx}] stream: {text}...")
        elif otype == "display_data" or otype == "execute_result":
            data = out.get("data", {})
            keys = list(data.keys())
            print(f"  [{o_idx}] {otype}: keys={keys}")
            if "text/plain" in data:
                print(f"      text/plain: {''.join(data['text/plain'])[:100]}...")
            if "image/png" in data:
                print(f"      image/png: length {len(data['image/png'])} chars")
