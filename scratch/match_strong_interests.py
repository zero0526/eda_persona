import json
import sys
from pathlib import Path
import pandas as pd

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
print("MATCHING STRONG INTERESTS WITH EVIDENCE PER PERSONA EPISODE")
print("=" * 80)

for _, ep in df_ep[df_ep["dataset_type"] == "persona"].iterrows():
    ep_id = ep["episode_id"]
    pid = ep["persona_id"]
    total_steps = ep["total_steps"]
    
    p_info = persona_dict.get(pid, {})
    fb_prof = p_info.get("facebook_behavior_profile", {})
    interests_obj = fb_prof.get("interests", {})
    strong_list = interests_obj.get("strong", [])
    avoid_list = interests_obj.get("avoid", [])
    
    ep_dims = df_dims[df_dims["episode_id"] == ep_id]
    steps_with_ev = ep_dims["step_index"].nunique()
    
    # Check matching for each strong interest
    matched_strong = {}
    for item in strong_list:
        # e.g., 'Interest: Collecting' -> prefix 'Interest', topic 'Collecting'
        parts = item.split(": ")
        topic_name = parts[-1].strip().lower()
        full_lower = item.lower()
        
        # Search in ep_dims
        matches = []
        for _, row in ep_dims.iterrows():
            dim_str = str(row["dimension"]).lower()
            val_str = str(row["value"]).lower()
            ref_str = str(row["reference_id"]).lower()
            
            # Check if topic_name is in dimension, value, or reference_id
            # Also handle Vietnamese translations
            vn_terms = {
                "meditation": ["thiền", "meditation"],
                "chess": ["cờ vua", "chess"],
                "philosophy": ["triết học", "philosophy"],
                "collecting": ["sưu tầm", "collecting"],
                "gardening": ["làm vườn", "cây cảnh", "bonsai", "gardening"],
                "knitting": ["đan len", "đan móc", "knitting", "móc khăn"],
                "fitness": ["fitness", "gym", "thể hình"],
                "spirituality": ["tâm linh", "đền", "spirituality"],
                "politics": ["chính trị", "politics"],
                "magic tricks": ["ảo thuật", "magic"],
                "sports": ["thể thao", "sports"],
                "cycling": ["đạp xe", "cycling"],
                "calligraphy": ["thư pháp", "calligraphy"],
                "history": ["lịch sử", "history"],
                "biography": ["tiểu sử", "hồi ký", "biography"],
                "social media": ["mạng xã hội", "social media"],
                "religion": ["tôn giáo", "religion"],
                "environment": ["môi trường", "environment"],
                "yoga": ["yoga"],
                "cooking": ["nấu ăn", "cooking"]
            }
            
            terms_to_check = [topic_name]
            if topic_name in vn_terms:
                terms_to_check.extend(vn_terms[topic_name])
                
            hit = any(t in dim_str or t in val_str or t in ref_str for t in terms_to_check)
            if hit:
                matches.append((row["step_index"], row["dimension"], row["role"], row["value"]))
                
        if matches:
            matched_strong[item] = matches

    # Check for any citations of AVOIDED topics (Negative constraint violations)
    avoid_hits = {}
    for item in avoid_list:
        topic_name = item.split(": ")[-1].strip().lower()
        for _, row in ep_dims.iterrows():
            dim_str = str(row["dimension"]).lower()
            val_str = str(row["value"]).lower()
            ref_str = str(row["reference_id"]).lower()
            if topic_name in dim_str or topic_name in val_str or topic_name in ref_str:
                # Check role: was it avoided/constrained or mistakenly engaged?
                role = str(row["role"]).lower()
                avoid_hits.setdefault(item, []).append((row["step_index"], role, row["value"]))

    coverage_rate = len(matched_strong) / len(strong_list) * 100 if strong_list else 0.0
    
    print("-" * 75)
    print(f"Episode: {ep_id[:8]} | Persona: {pid} | Total Steps: {total_steps} | Steps with Evidence: {steps_with_ev}")
    print(f"  • Danh sách 12 sở thích mạnh (strong) trong hồ sơ:")
    for i, s in enumerate(strong_list, 1):
        status = "[X] COVERED" if s in matched_strong else "[ ] not explored"
        steps_c = f"(bước: {[m[0] for m in matched_strong[s]]})" if s in matched_strong else ""
        print(f"    {i:2d}. {status:16s} {s:30s} {steps_c}")
        
    print(f"  • TỔNG SỞ THÍCH MẠNH ĐƯỢC BAO TRÙM TRONG PHIÊN: {len(matched_strong)} / {len(strong_list)} ({coverage_rate:.1f}%)")
    print(f"  • Vi phạm chủ đề né tránh (Avoid Violations): {len(avoid_hits)} (Chi tiết: {list(avoid_hits.keys()) if avoid_hits else '0 vi phạm - Tuân thủ 100%'})")
