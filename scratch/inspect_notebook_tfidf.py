import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

keywords = ['ngram', 'n-gram', 'chain', 'tfidf', 'dấu ấn', 'chuỗi', 'markov', 'transition']
for idx, cell in enumerate(nb['cells']):
    src = ''.join(cell.get('source', []))
    if any(k in src.lower() for k in keywords):
        print(f"Cell {idx} ({cell['cell_type']}):")
        for l in src.split('\n')[:10]:
            print("  ", l)
        print("-" * 50)
