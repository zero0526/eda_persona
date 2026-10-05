import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("data/original_facebook_persona.json", "r", encoding="utf-8") as f:
    p_data = json.load(f)

for p in p_data:
    pid = p.get("persona_id")
    attrs = p.get("persona", {}).get("attributes", {})
    taste = p.get("behavioral_contract", {})
    taste_obj = taste.get("taste") if isinstance(taste, dict) else None
    
    print("=" * 70)
    print(f"PERSONA {pid}:")
    print("Attributes keys:", list(attrs.keys()))
    for k in attrs:
        if any(w in k.lower() for w in ['interest', 'topic', 'hobby', 'taste', 'prefer', 'like', 'lifestyle', 'domain']):
            print(f"  {k}: {attrs[k]}")
    if taste_obj:
        print("Taste in contract:", taste_obj)
