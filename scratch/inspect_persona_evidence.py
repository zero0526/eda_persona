import sys
from pathlib import Path
import json
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from loaders.loaders.persona_action import PersonaActionLoader
loader = PersonaActionLoader()
df_dims = loader.load_dimension_evidences()

print("=" * 80)
print("1. OVERVIEW OF LOADED DIMENSION EVIDENCES")
print("=" * 80)
print(f"Total dimension evidence rows: {len(df_dims)}")
print(f"Unique dimensions: {df_dims['dimension'].unique().tolist()}")
print(f"Unique roles: {df_dims['role'].value_counts().to_dict()}")
print(f"Rows by dataset_type: {df_dims['dataset_type'].value_counts().to_dict()}")

print("\nSample rows of df_dims:")
print(df_dims[['episode_id', 'persona_id', 'step_index', 'dimension', 'role', 'weight', 'value', 'reference_id']].head(15).to_string())

print("\n" + "=" * 80)
print("2. DIMENSIONS CITED IN PERSONA EPISODES")
print("=" * 80)
for ep_id, ep_df in df_dims[df_dims['dataset_type'] == 'persona'].groupby('episode_id'):
    pid = ep_df['persona_id'].iloc[0]
    unique_dims = ep_df['dimension'].unique().tolist()
    unique_vals = ep_df['value'].unique().tolist()
    unique_refs = ep_df['reference_id'].unique().tolist()
    steps_with_ev = ep_df['step_index'].nunique()
    print(f"\nEpisode {ep_id[:8]} (Persona {pid}):")
    print(f"  Steps with evidence: {steps_with_ev}")
    print(f"  Dimensions cited: {unique_dims}")
    print(f"  Unique reference IDs: {unique_refs}")
    print(f"  Unique values / topics cited:\n    {unique_vals[:10]}")

print("\n" + "=" * 80)
print("3. ORIGINAL PERSONA PROFILES IN data/original_facebook_persona.json")
print("=" * 80)
p_path = Path("data/original_facebook_persona.json")
if p_path.exists():
    with open(p_path, "r", encoding="utf-8") as f:
        p_data = json.load(f)
    print(f"Type of p_data: {type(p_data)}, length: {len(p_data) if isinstance(p_data, (list, dict)) else 'N/A'}")
    if isinstance(p_data, list):
        print("First persona keys:", list(p_data[0].keys()) if p_data else "Empty")
        sample_p = [p for p in p_data if p.get("persona_id") == "vn_000081"]
        if sample_p:
            print("vn_000081 profile sample keys & interests:")
            p0 = sample_p[0]
            for k in ["persona_id", "demographics", "interests", "preferences", "behaviors", "cognitive_matrix", "topics"]:
                if k in p0:
                    print(f"  {k}: {p0[k]}")
