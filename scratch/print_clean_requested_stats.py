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

def map_item(row):
    intent = str(row['intent']).lower()
    if intent == 'react':
        rx = str(row.get('reaction', 'LIKE')).upper()
        if any(neg in rx for neg in ['SAD', 'ANGRY']):
            return 'react_neg'
        else:
            return 'react_pos'
    elif intent == 'comment':
        return 'comment'
    elif intent == 'share':
        return 'share'
    elif intent == 'read':
        return 'read'
    elif intent in ['observe', 'object']:
        return 'observe'
    elif intent == 'next':
        return 'next'
    elif intent == 'watch':
        return 'watch'
    elif intent == 'scroll':
        return 'scroll'
    elif intent == 'expand':
        return 'expand'
    else:
        return 'other'

df['req_cat'] = df.apply(map_item, axis=1)

cols_order = ['react_pos', 'react_neg', 'comment', 'share', 'read', 'observe', 'next', 'watch', 'scroll', 'expand', 'other']

ct = pd.crosstab(df['persona_id'], df['req_cat']).reindex(columns=cols_order, fill_value=0)
ct['total_actions'] = ct.sum(axis=1)

print("=== BẢNG 1: SỐ LƯỢNG HÀNH VI TUYỆT ĐỐI ===")
print(ct.to_string())

print("\n=== BẢNG 2: TỶ LỆ PHẦN TRĂM (%) TRÊN TỔNG HÀNH ĐỘNG CỦA MỖI PERSONA ===")
pct = (ct[cols_order].div(ct['total_actions'], axis=0) * 100).round(2)
print(pct.to_string())

print("\n=== BẢNG 3: SỐ LƯỢNG CHI TIẾT TỪNG LOẠI REACTION ===")
reacts = df[df['intent'] == 'react'].copy()
reacts['rx'] = reacts['reaction'].fillna('like').str.lower()
print(pd.crosstab(reacts['persona_id'], reacts['rx'], margins=True).to_string())
