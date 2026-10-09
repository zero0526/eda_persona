import sys
from pathlib import Path
from collections import Counter
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

from loaders.action_loader import ActionLoader

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

print("df_actions shape:", df_actions.shape)
print("Các cột liên quan:", [c for c in df_actions.columns if any(k in c for k in ['react', 'intent', 'action', 'type', 'surface', 'reason'])])

# Kiểm tra các giá trị của intent và reaction
print("\nGiá trị của intent:")
print(df_actions['intent'].value_counts())

# Xem các dòng có hành vi tương tác like/react
react_rows = df_actions[df_actions['intent'] == 'react']
print(f"\nTổng số lượt react: {len(react_rows)}")
print(react_rows['persona_id'].value_counts())

if 'reaction' in df_actions.columns:
    print("\nChi tiết reaction column:")
    print(react_rows['reaction'].value_counts(dropna=False))

# Phân tích chuỗi trước react: lag-1, lag-2
df_sorted = df_actions.sort_values(by=['persona_id', 'session_id', 'step_index']).copy()
df_sorted['prev_1_intent'] = df_sorted.groupby(['persona_id', 'session_id'])['intent'].shift(1)
df_sorted['prev_1_surface'] = df_sorted.groupby(['persona_id', 'session_id'])['surface'].shift(1)
df_sorted['prev_2_intent'] = df_sorted.groupby(['persona_id', 'session_id'])['intent'].shift(2)
df_sorted['prev_2_surface'] = df_sorted.groupby(['persona_id', 'session_id'])['surface'].shift(2)

df_sorted['current_node'] = df_sorted['intent'] + '@' + df_sorted['surface'].fillna('unknown')
df_sorted['prev_1_node'] = df_sorted['prev_1_intent'].fillna('START') + '@' + df_sorted['prev_1_surface'].fillna('unknown')
df_sorted['prev_2_node'] = df_sorted['prev_2_intent'].fillna('START') + '@' + df_sorted['prev_2_surface'].fillna('unknown')

reacts = df_sorted[df_sorted['intent'] == 'react'].copy()

print("\n=== TOP CHUỖI 2-BƯỚC DẪN ĐẾN REACT (prev_1 -> react) ===")
reacts['chain_2'] = reacts['prev_1_node'] + " ➔ " + reacts['current_node']
print(reacts['chain_2'].value_counts())

print("\n=== TOP CHUỖI 3-BƯỚC DẪN ĐẾN REACT (prev_2 -> prev_1 -> react) ===")
reacts['chain_3'] = reacts['prev_2_node'] + " ➔ " + reacts['prev_1_node'] + " ➔ " + reacts['current_node']
print(reacts['chain_3'].value_counts())

print("\n=== THEO TỪNG PERSONA ===")
for pid, group in reacts.groupby('persona_id'):
    print(f"\n--- {pid} (Tổng số lượt react: {len(group)}) ---")
    print("Chuỗi 2 bước phổ biến nhất:")
    print(group['chain_2'].value_counts().head(5))
    print("Mẫu lý do CoT (reason) khi react:")
    for idx, r in group[['step_index', 'surface', 'reason']].head(3).iterrows():
        print(f"  - Bước {r['step_index']} ({r['surface']}): {str(r['reason'])[:120]}...")
