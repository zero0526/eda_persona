import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from loaders.loaders.persona_action import PersonaActionLoader
loader = PersonaActionLoader()
df_dims = loader.load_dimension_evidences()
df_ep = loader.load_action_logs()

# Load original personas
with open("data/original_facebook_persona.json", "r", encoding="utf-8") as f:
    raw_personas = json.load(f)

persona_dict = {p["persona_id"]: p for p in raw_personas}

print("=" * 80)
print("ANALYZING CONFIGURED INTERESTS VS EXPLORED EVIDENCE PER EPISODE")
print("=" * 80)

results = []

for _, ep in df_ep.iterrows():
    ep_id = ep["episode_id"]
    pid = ep["persona_id"]
    dtype = ep["dataset_type"]
    total_steps = ep["total_steps"]
    
    # 1. Configured interests from Persona profile
    p_info = persona_dict.get(pid, {})
    attrs = p_info.get("persona", {}).get("attributes", {})
    contract = p_info.get("behavioral_contract", {})
    taste = contract.get("taste", {}) if isinstance(contract, dict) else {}
    ranked_topics = taste.get("rankedTopics", [])
    
    # Positive attributes (Passionate or Interested, or Active hobby)
    pos_attrs = []
    for k, v in attrs.items():
        if k.startswith("interest_") and v in ["Passionate", "Interested"]:
            topic_clean = k.replace("interest_", "").replace("_", " ").title()
            pos_attrs.append(f"{topic_clean} ({v})")
        elif k.startswith("hobby_") and v in ["Active", "Curious"]:
            hobby_clean = k.replace("hobby_", "").replace("_", " ").title()
            pos_attrs.append(f"Hobby: {hobby_clean} ({v})")
            
    # 2. Evidence cited in this episode's steps
    ep_dims = df_dims[df_dims["episode_id"] == ep_id]
    steps_with_ev = ep_dims["step_index"].nunique()
    
    # Extract unique interest dimensions cited
    # Look for dimension == 'interest' or dimensions starting with 'Interest' or reference_id starting with 'interest-'
    interest_evs = ep_dims[
        ep_dims["dimension"].str.lower().str.contains("interest|sport|topic|hobby", na=False) |
        ep_dims["reference_id"].str.lower().str.contains("interest", na=False) |
        ep_dims["value"].str.lower().str.contains("sở thích|quan tâm|yêu thích", na=False)
    ]
    
    unique_dim_names = ep_dims["dimension"].unique().tolist()
    unique_ref_ids = ep_dims["reference_id"].dropna().unique().tolist()
    interest_refs = [r for r in unique_ref_ids if "interest" in str(r).lower()]
    
    # Also extract values
    cited_values = ep_dims[ep_dims["dimension"].str.lower().str.contains("interest", na=False)]["value"].unique().tolist()
    if not cited_values:
        # Check reference_id
        cited_values = interest_refs
        
    print(f"\nEpisode {ep_id[:8]} | Dataset: {dtype.upper()} | Persona: {pid} | Steps: {total_steps}")
    print(f"  Configured Ranked Topics in Contract (N={len(ranked_topics)}): {ranked_topics[:6]}")
    print(f"  Configured Positive Interests in Attributes (N={len(pos_attrs)}): {pos_attrs[:6]}")
    print(f"  Total Steps with Evidence: {steps_with_ev} / {total_steps} ({steps_with_ev/total_steps*100:.1f}%)")
    print(f"  Total Evidence rows: {len(ep_dims)}")
    print(f"  Distinct Dimensions cited: {len(unique_dim_names)} -> {unique_dim_names[:5]}")
    print(f"  Interest references / dimensions cited: {interest_refs if interest_refs else unique_dim_names[:5]}")
    print(f"  Specific Interest values cited: {cited_values[:5]}")
