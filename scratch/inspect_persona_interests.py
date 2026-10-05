import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

p_path = Path("data/original_facebook_persona.json")
with open(p_path, "r", encoding="utf-8") as f:
    p_data = json.load(f)

for p in p_data:
    pid = p.get("persona_id")
    persona_obj = p.get("persona", {})
    contract = p.get("behavioral_contract", {})
    fb_prof = p.get("facebook_behavior_profile", {})
    
    print("=" * 70)
    print(f"PERSONA ID: {pid}")
    print("  persona keys:", list(persona_obj.keys()))
    print("  interests in persona:", persona_obj.get("interests"))
    print("  hobbies:", persona_obj.get("hobbies"))
    print("  topics:", persona_obj.get("topics"))
    print("  contract keys:", list(contract.keys()) if isinstance(contract, dict) else "Not dict")
    if isinstance(contract, dict):
        print("  contract preferred_topics:", contract.get("preferred_topics"))
        print("  contract topic_preferences:", contract.get("topic_preferences"))
        print("  contract interests:", contract.get("interests"))
        print("  contract candidate_topics:", contract.get("candidate_topics"))
        print("  contract rules / dimensions:", list(contract.get("rules", {}).keys()) if isinstance(contract.get("rules"), dict) else "N/A")
