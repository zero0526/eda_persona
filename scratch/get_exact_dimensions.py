import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))

sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader
import pandas as pd

loader = ActionLoader()
df = loader.to_unified_actions_dataframe()

intents = ['search', 'comment', 'read', 'expand', 'react', 'share']
for intent in intents:
    print(f"*** INTENT: {intent.upper()} ***")
    sub_intent = df[df['intent'] == intent]
    for p in ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']:
        p_sub = sub_intent[sub_intent['persona_id'] == p]
        n = len(p_sub)
        if n == 0:
            print(f"  {p}: [KHONG_PHAT_SINH - 0 luot]")
        else:
            vc = p_sub['primary_dimension'].value_counts()
            items = [f"{dim}: {cnt}/{n} ({cnt/n*100:.1f}%)" for dim, cnt in vc.items()]
            print(f"  {p} (N={n}): " + "; ".join(items))
