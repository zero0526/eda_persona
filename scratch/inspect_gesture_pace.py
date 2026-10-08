import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from loaders.action_loader import ActionLoader

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

df_gestures = df_actions[df_actions['gesture_total_px'].notnull()].copy()
print("Total gesture steps:", len(df_gestures))
print("Unique gesture_pace values:", df_gestures['gesture_pace'].unique())

print("\n=== Crosstab gesture_pace by Persona ===")
ct_pace = pd.crosstab(df_gestures['persona_id'], df_gestures['gesture_pace'], margins=True)
print(ct_pace)

print("\n=== Crosstab gesture_pace by Persona (%) ===")
ct_pace_pct = (pd.crosstab(df_gestures['persona_id'], df_gestures['gesture_pace'], normalize='index') * 100).round(1)
print(ct_pace_pct)

print("\n=== gesture_pace by Persona and Session ===")
for pid, group in df_gestures.groupby('persona_id'):
    print(f"\n*** Persona: {pid} ***")
    sess_pace = pd.crosstab(group['session_id'].str[:8], group['gesture_pace'])
    print(sess_pace)

profiles, contracts = loader.load_persona_profiles_and_contracts()
print("\n=== Contracts scrollCadence & scanRatio ===")
for pid in sorted(contracts.keys()):
    c = contracts[pid].get('navigation', {})
    print(f"{pid}: scrollCadence = {c.get('scrollCadence')}, scanRatio = {c.get('scanRatio')}")
