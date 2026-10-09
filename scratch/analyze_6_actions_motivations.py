import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader

loader = ActionLoader()
df = loader.to_unified_actions_dataframe()
focused = ['read', 'comment', 'react', 'expand', 'search', 'share']
sub = df[df['intent'].isin(focused)].copy()

for act in focused:
    print(f"\n=============================================================")
    print(f"=== HÀNH ĐỘNG: {act.upper()} (Tổng {len(sub[sub['intent'] == act])} lượt) ===")
    print(f"=============================================================")
    sub_act = sub[sub['intent'] == act]
    for pid in ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']:
        p_sub = sub_act[sub_act['persona_id'] == pid]
        if p_sub.empty:
            print(f"* {pid} (0 lượt): Không thực hiện hành vi này.")
            continue
        top_dims = p_sub['primary_dimension'].value_counts().head(3)
        dims_str = ', '.join([f"{d} ({cnt})" for d, cnt in top_dims.items()])
        sample_r = str(p_sub.iloc[0]['reason']).replace('\n', ' ')[:100]
        print(f"* {pid} ({len(p_sub)} lượt): {dims_str}")
        print(f"    Log: \"{sample_r}...\"")
