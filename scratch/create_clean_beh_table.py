import pandas as pd
from pathlib import Path

project_root = Path('.')
ct_p = pd.read_csv(project_root / "output" / "tables" / "step5_behavior_crosstab_persona.csv", index_col=0)
ct_np = pd.read_csv(project_root / "output" / "tables" / "step5_behavior_crosstab_nopersona.csv", index_col=0)

records = []
for phase in ct_p.index:
    for beh in ct_p.columns:
        p_val = ct_p.loc[phase, beh]
        np_val = ct_np.loc[phase, beh]
        records.append({
            "Phase": phase,
            "Macro_Behavior": beh,
            "Persona (%)": round(p_val, 1),
            "No-Persona (%)": round(np_val, 1),
            "Diff (P - NP)": round(p_val - np_val, 1)
        })

df_clean = pd.DataFrame(records)
df_clean.to_csv(project_root / "output" / "tables" / "step5_behavior_distribution_comparison_clean.csv", index=False, encoding="utf-8-sig")
print("Saved clean table!")
