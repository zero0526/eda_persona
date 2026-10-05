import json
import sys
from pathlib import Path
import pandas as pd
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from loaders.loaders.persona_action import PersonaActionLoader
loader = PersonaActionLoader()
df_dims = loader.load_dimension_evidences()
df_ep = loader.load_action_logs()

with open("data/original_facebook_persona.json", "r", encoding="utf-8") as f:
    raw_personas = json.load(f)
persona_dict = {p["persona_id"]: p for p in raw_personas}

print("=" * 80)
print("DETAILED MAPPING: CONFIGURED INTERESTS VS EXPLORED TOPICS WITH EVIDENCE")
print("=" * 80)

summary_rows = []

for _, ep in df_ep[df_ep["dataset_type"] == "persona"].iterrows():
    ep_id = ep["episode_id"]
    pid = ep["persona_id"]
    total_steps = ep["total_steps"]
    
    p_info = persona_dict.get(pid, {})
    attrs = p_info.get("persona", {}).get("attributes", {})
    contract = p_info.get("behavioral_contract", {})
    taste = contract.get("taste", {}) if isinstance(contract, dict) else {}
    ranked_topics = taste.get("rankedTopics", [])
    
    # Positive interests from attributes
    passionate_interests = [k.replace("interest_", "").replace("hobby_", "").replace("_", " ").title() 
                            for k, v in attrs.items() if v in ["Passionate", "Active"]]
    interested_interests = [k.replace("interest_", "").replace("hobby_", "").replace("_", " ").title() 
                            for k, v in attrs.items() if v in ["Interested", "Curious"]]
    
    # Ranked topics clean
    clean_ranked = [t.split(":")[-1].strip().replace("_", " ").title() for t in ranked_topics]
    
    # Evidence for this episode
    ep_dims = df_dims[df_dims["episode_id"] == ep_id]
    
    # Find all interest-related citations
    cited_topics = set()
    for _, row in ep_dims.iterrows():
        dim = str(row["dimension"])
        val = str(row["value"])
        ref = str(row["reference_id"])
        
        # Check ref_id
        if "interest-" in ref.lower():
            t = ref.split("interest-")[-1].replace("_", " ").title()
            cited_topics.add(t)
            
        # Check dimension name (e.g. 'Interest: Spirituality')
        if "interest:" in dim.lower() or "sport:" in dim.lower():
            t = dim.split(":")[-1].strip().replace("_", " ").title()
            cited_topics.add(t)
            
        # Check text value
        for kw in ["meditation", "chess", "philosophy", "spirituality", "politics", "knitting", 
                   "fitness", "gym", "calligraphy", "history", "biography", "cycling", 
                   "bonsai", "làm vườn", "sưu tầm", "đan móc", "thư pháp", "lịch sử", "tiểu sử"]:
            if kw in val.lower():
                # Map to standard English name
                name_map = {
                    "meditation": "Meditation",
                    "chess": "Chess",
                    "philosophy": "Philosophy",
                    "spirituality": "Spirituality",
                    "politics": "Politics",
                    "knitting": "Knitting",
                    "đan móc": "Knitting",
                    "fitness": "Fitness",
                    "gym": "Fitness",
                    "calligraphy": "Calligraphy",
                    "thư pháp": "Calligraphy",
                    "history": "History",
                    "lịch sử": "History",
                    "biography": "Biography",
                    "tiểu sử": "Biography",
                    "cycling": "Cycling",
                    "bonsai": "Gardening / Bonsai",
                    "làm vườn": "Gardening / Bonsai",
                    "sưu tầm": "Collecting"
                }
                cited_topics.add(name_map[kw])
                
    # Also check what working memory threads / searched queries were executed
    searched_queries = str(ep.get("final_searched_queries", ""))
    
    # Determine base configured pool
    # A persona has a primary pool of focused topics (Ranked topics if contract exists, else Passionate/Active + top Interested)
    if clean_ranked:
        core_pool = list(dict.fromkeys(clean_ranked))
    else:
        core_pool = list(dict.fromkeys(passionate_interests + interested_interests[:6]))
        
    # Check which core topics were covered
    covered_in_core = [t for t in core_pool if any(t.lower() in ct.lower() or ct.lower() in t.lower() for ct in cited_topics)]
    
    coverage_rate = len(covered_in_core) / len(core_pool) * 100 if core_pool else 0.0
    
    print("-" * 75)
    print(f"Episode: {ep_id[:8]} | Persona: {pid} | Total Steps: {total_steps}")
    print(f"  • Danh sách sở thích cốt lõi được cấu hình (K={len(core_pool)}): {core_pool[:8]}")
    print(f"  • Các chủ đề đã được viện dẫn bằng evidence trong phiên ({len(cited_topics)}): {sorted(list(cited_topics))}")
    print(f"  • Các chủ đề cốt lõi ĐÃ BAO TRÙM ({len(covered_in_core)} / {len(core_pool)}): {covered_in_core}")
    print(f"  • Tỷ lệ bao trùm trong 1 phiên (Coverage Rate): {coverage_rate:.1f}%")
    print(f"  • Các chủ đề cốt lõi CHƯA kịp khám phá trong phiên (~10 phút): {[t for t in core_pool if t not in covered_in_core][:6]}")
    
    summary_rows.append({
        "episode_id": ep_id[:8],
        "persona_id": pid,
        "total_steps": total_steps,
        "steps_with_evidence": ep_dims["step_index"].nunique(),
        "evidence_step_share_pct": round(ep_dims["step_index"].nunique() / total_steps * 100, 1),
        "total_configured_core_topics": len(core_pool),
        "unique_topics_cited": len(cited_topics),
        "core_topics_covered_count": len(covered_in_core),
        "core_topics_covered_list": ", ".join(covered_in_core),
        "uncovered_core_topics_count": len(core_pool) - len(covered_in_core),
        "topic_coverage_rate_pct": round(coverage_rate, 1)
    })

df_res = pd.DataFrame(summary_rows)
print("\n" + "=" * 80)
print("BẢNG TỔNG HỢP MỨC ĐỘ BAO TRÙM CHỦ ĐỀ SỞ THÍCH TRONG 1 PHIÊN (STEP 4)")
print("=" * 80)
print(df_res.to_string(index=False))
