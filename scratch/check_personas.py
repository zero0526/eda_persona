import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/selected_6_facebook_personas_description.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        pid = data.get('persona_id') or data.get('id')
        print("="*50)
        print("PERSONA ID:", pid)
        for k, v in data.items():
            if isinstance(v, (str, int, float, list)):
                val_str = str(v)
                if len(val_str) > 100:
                    val_str = val_str[:100] + '...'
                print(f"  {k}: {val_str}")
