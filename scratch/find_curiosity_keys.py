import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

path = Path('data/selected_6_facebook_personas_description.jsonl')
with open(path, 'r', encoding='utf-8') as f:
    for line in f:
        p = json.loads(line)
        pid = p['persona_id']
        print(f"=== {pid} ===")
        for k, v in p['attributes'].items():
            if any(w in k.lower() for w in ['tò mò', 'khám phá', 'mới', 'tìm hiểu', 'cởi mở', 'tâm trạng', 'hóng', 'big five', 'chú ý']):
                print(f"  {k}: {v}")
