import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from loaders.loaders.persona_action import PersonaActionLoader
loader = PersonaActionLoader()
df_steps = loader.load_step_records()
sub = df_steps[df_steps['episode_id'] == '755b1653-927c-48f3-baf4-259c8d9091d8'].sort_values('step_index')

print("All steps of Episode 755b1653:")
for i in range(len(sub)):
    r = sub.iloc[i]
    print(f"Step {r['step_index']:02d}: sit={r['wm_situational_steps']}, warn={r['wm_has_novelty_warning']}, intent={r['intent']}, tool={r['resolved_tool']}")
