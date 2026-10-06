import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

nb = json.load(open('notebooks/eda_action_logs.ipynb', encoding='utf-8'))
print(f"Total cells: {len(nb['cells'])}")
for idx, c in enumerate(nb['cells']):
    src = ''.join(c.get('source', []))
    header = src.split('\n')[0] if src else '(empty)'
    print(f"Cell {idx:02d} ({c['cell_type']}): {header[:120]}")
    if any(k in src.lower() for k in ['h2', 'giả thuyết', 'consistency', 'nhất quán', 'persona', 'contract', 'entropy', 'evidence', 'decision', 'grounding', 'reason', 'cosine', 'tfidf', 'similarity']):
        print(f"   -> Match snippet: {src[:200].strip()}...\n")
