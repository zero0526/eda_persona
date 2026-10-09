import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader
loader = ActionLoader()
df = loader.to_unified_actions_dataframe()

print("Columns in df:", df.columns.tolist())
print("\nUnique intents:", df['intent'].value_counts())

if 'reaction' in df.columns:
    print("\nUnique reactions for react intent:")
    print(df[df['intent'] == 'react']['reaction'].value_counts(dropna=False))

# Định nghĩa phân loại:
# react_positive: Like, Love, Care, Haha, Wow
# react_negative: Sad, Angry
# comment
# share
# read (bao gồm read, expand) hoặc tách riêng
# observe
# next
# watch

def categorize_behavior(row):
    intent = str(row['intent']).lower()
    if intent == 'react':
        rx = str(row.get('reaction', 'LIKE')).upper()
        if any(neg in rx for neg in ['SAD', 'ANGRY']):
            return 'React (Tiêu cực: Sad/Angry)'
        else:
            return 'React (Tích cực: Like/Love/Care/Haha/Wow)'
    elif intent == 'comment':
        return 'Comment'
    elif intent == 'share':
        return 'Share'
    elif intent == 'read':
        return 'Read (Đọc sâu)'
    elif intent == 'expand':
        return 'Expand (Xem thêm)'
    elif intent in ['observe', 'object']:
        return 'Observe (Quan sát nhanh)'
    elif intent == 'next':
        return 'Next (Chuyển Reels)'
    elif intent == 'watch':
        return 'Watch (Xem video)'
    elif intent == 'scroll':
        return 'Scroll (Cuộn trang)'
    elif intent == 'search':
        return 'Search (Tìm kiếm)'
    else:
        return f'Khác ({intent})'

df['behavior_cat'] = df.apply(categorize_behavior, axis=1)

print("\n=== BẢNG 1: SỐ LƯỢNG HÀNH VI THEO CÁC TRƯỜNG YÊU CẦU ===")
ct_counts = pd.crosstab(df['persona_id'], df['behavior_cat'], margins=True)
print(ct_counts)

print("\n=== BẢNG 2: TỶ LỆ PHẦN TRĂM (%) THEO TỪNG PERSONA ===")
ct_pct = pd.crosstab(df['persona_id'], df['behavior_cat'], normalize='index') * 100
print(ct_pct.round(2))

# Thống kê chi tiết riêng về Reactions:
reacts = df[df['intent'] == 'react'].copy()
reacts['rx_clean'] = reacts['reaction'].fillna('LIKE').str.upper()
def rx_valence(rx):
    if any(neg in rx for neg in ['SAD', 'ANGRY']):
        return 'Tiêu cực (Sad/Angry)'
    elif any(pos in rx for pos in ['LOVE', 'CARE']):
        return 'Ấm áp/Gắn kết (Love/Care)'
    elif any(fun in rx for fun in ['HAHA', 'WOW']):
        return 'Thích thú/Ngạc nhiên (Haha/Wow)'
    else:
        return 'Tán thành chuẩn mực (Like)'

reacts['valence'] = reacts['rx_clean'].apply(rx_valence)
print("\n=== BẢNG 3: CHI TIẾT SẮC THÁI CẢM XÚC (REACTIONS) ===")
print(pd.crosstab(reacts['persona_id'], reacts['valence'], margins=True))
print("\nTỷ lệ % Sắc thái cảm xúc theo Persona:")
print((pd.crosstab(reacts['persona_id'], reacts['valence'], normalize='index') * 100).round(1))
