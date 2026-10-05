import json

with open("scratch/episode_deep_summary.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print("=== EPISODE ROW ===")
print(json.dumps(d["ep_row"], indent=2, ensure_ascii=False))

print("\n=== BOT ROW ===")
print(json.dumps(d["bot_row"], indent=2, ensure_ascii=False))

print("\n=== RUN ROW ===")
print(json.dumps(d["run_row_preview"], indent=2, ensure_ascii=False))

print("\n=== WORKING MEMORY KEYS & STRUCTURE ===")
if d["working_memory_preview"]:
    print("Keys:", list(d["working_memory_preview"].keys()))
    print("Sample:", json.dumps({k: d["working_memory_preview"][k] for k in list(d["working_memory_preview"].keys())[:5]}, indent=2, ensure_ascii=False))

print("\n=== STEP PAYLOAD KEYS & STRUCTURE ===")
if d["sample_step_payload"]:
    print("Keys:", list(d["sample_step_payload"].keys()))
    for k in d["sample_step_payload"].keys():
        val = d["sample_step_payload"][k]
        if isinstance(val, dict):
            print(f"  [{k}] (dict keys):", list(val.keys()))
        elif isinstance(val, list):
            print(f"  [{k}] (list len {len(val)})")
        else:
            print(f"  [{k}]:", val)

print("\n=== SAMPLE EVIDENCE ===")
print(json.dumps(d["sample_evidence"], indent=2, ensure_ascii=False))

print("\n=== SAMPLE EVENT ===")
print(json.dumps(d["sample_event"], indent=2, ensure_ascii=False))

print("\n=== SAMPLE CONSOLIDATION ===")
print(json.dumps(d["sample_consolidation"], indent=2, ensure_ascii=False))

print("\n=== SAMPLE DELTA ===")
print(json.dumps(d["sample_delta"], indent=2, ensure_ascii=False))
