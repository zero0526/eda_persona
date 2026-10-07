import os, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from loaders.action_loader import ActionLoader
import pandas as pd

loader = ActionLoader(os.getenv('SQLITE_PATH'))
histories = loader.load_all_personas(source='sqlite')

actions = []
for pid, h in histories.items():
    for s in h.sessions:
        for a in s.actions:
            actions.append({
                'persona_id': pid,
                'session_id': s.session_id,
                'step_index': a.step_index,
                'intent': a.intent,
                'surface': a.surface,
                'tool': a.tool,
                'resolved_tool': a.resolved_tool,
                'reason': a.reason,
                'target_text': a.target_text
            })

df = pd.DataFrame(actions)
print(f"Total actions loaded: {len(df)}")
print("\nIntent Value Counts:")
print(df['intent'].value_counts())

print("\nIntent x Persona (Count):")
ct = pd.crosstab(df['intent'], df['persona_id'], margins=True)
print(ct)

print("\nIntent x Persona (% column):")
ct_pct = pd.crosstab(df['intent'], df['persona_id'], normalize='columns') * 100
print(ct_pct.round(2).to_string())

search_actions = df[df['intent'].astype(str).str.contains('search', case=False, na=False)]
print(f"\nSearch Intent Actions Detail ({len(search_actions)} steps):")
for idx, r in search_actions.iterrows():
    print(f"Persona: {r['persona_id']} | Sess: {r['session_id'][:8]} | Step: {r['step_index']:2d} | Intent: {r['intent']} | Surface: {r['surface']} | Tool: {r['tool']} | Reason: {r['reason']}")

surface_search = df[df['surface'] == 'search']
print(f"\nSurface == 'search' Actions Breakdown ({len(surface_search)} steps total):")
print(pd.crosstab(surface_search['intent'], surface_search['persona_id'], margins=True))

print("\nAll steps with surface == 'search':")
for idx, r in surface_search.iterrows():
    print(f"Persona: {r['persona_id']} | Sess: {r['session_id'][:8]} | Step: {r['step_index']:2d} | Intent: {r['intent']} | Tool: {r['tool']} | Text: {str(r['target_text'])[:40]} | Reason: {r['reason']}")
