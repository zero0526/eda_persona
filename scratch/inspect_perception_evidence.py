import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("scratch/episode_deep_summary.json", "r", encoding="utf-8") as f:
    d = json.load(f)

step = d["sample_step_payload"]
p = step.get("perception")
print("Perception type:", type(p))
if isinstance(p, dict):
    print("Perception keys:", list(p.keys()))
    for k, v in p.items():
        if isinstance(v, (dict, list)):
            print(f"  {k}: {type(v)} len={len(v)}")
        else:
            print(f"  {k}: {v}")
elif isinstance(p, str):
    print("Perception string sample:", p[:300])

print("\nEvidence in step outcome:")
print("outcome.evidence:", json.dumps(step.get("outcome", {}).get("evidence"), indent=2, ensure_ascii=False))

print("\nSample decision_evidence row:")
print(json.dumps(d.get("sample_evidence"), indent=2, ensure_ascii=False))
