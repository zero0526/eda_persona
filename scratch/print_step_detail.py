import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("scratch/episode_deep_summary.json", "r", encoding="utf-8") as f:
    d = json.load(f)

step = d["sample_step_payload"]
print("=== STEP PAYLOAD DETAIL ===")
print("decision:")
print(json.dumps(step.get("decision"), indent=2, ensure_ascii=False))

print("\noutcome:")
print(json.dumps(step.get("outcome"), indent=2, ensure_ascii=False))

print("\nperception (type, keys/preview):")
p = step.get("perception")
if isinstance(p, dict):
    print("dict keys:", list(p.keys()))
    print(json.dumps({k: str(p[k])[:100] for k in p}, indent=2, ensure_ascii=False))
elif isinstance(p, str):
    print("string len:", len(p), "preview:", p[:200])
else:
    print(type(p), p)

print("\ndebug summary (keys & latency & usage):")
dbg = step.get("debug", {})
print("keys:", list(dbg.keys()))
print("modelLatencyMs:", dbg.get("modelLatencyMs"))
print("toolExecutionMs:", dbg.get("toolExecutionMs"))
print("llmUsage:", dbg.get("llmUsage"))

print("\n=== SAMPLE EVIDENCE ===")
print(json.dumps(d.get("sample_evidence"), indent=2, ensure_ascii=False))

print("\n=== SAMPLE EVENT ===")
print(json.dumps(d.get("sample_event"), indent=2, ensure_ascii=False))

print("\n=== SAMPLE CONSOLIDATION ===")
print(json.dumps(d.get("sample_consolidation"), indent=2, ensure_ascii=False))

print("\n=== SAMPLE DELTA ===")
print(json.dumps(d.get("sample_delta"), indent=2, ensure_ascii=False))
