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

print("=== 1. TỔNG SỐ HÀNH ĐỘNG CỦA TỪNG PERSONA ===")
print(df['persona_id'].value_counts().sort_index())

print("\n=== 2. PHÂN PHỐI TẤT CẢ INTENTS (HÀNH VI) THEO TỪNG PERSONA (SỐ LƯỢNG & TỶ LỆ %) ===")
ct_intent = pd.crosstab(df['persona_id'], df['intent'], margins=True)
print(ct_intent)

print("\n--- Tỷ lệ % Intent theo từng Persona (hàng = 100%) ---")
ct_intent_pct = pd.crosstab(df['persona_id'], df['intent'], normalize='index') * 100
print(ct_intent_pct.round(1))

print("\n=== 3. THỐNG KÊ CHI TIẾT TƯƠNG TÁC (REACT, COMMENT, SHARE) ===")
# Các tương tác trực tiếp
interactions = df[df['intent'].isin(['react', 'comment', 'share'])].copy()
print("Số lượt tương tác tuyệt đối:")
print(pd.crosstab(interactions['persona_id'], interactions['intent'], margins=True))

# Phân bố sắc thái (Reaction types + Comment + Share) như Panel B
print("\n=== 4. CƠ CẤU SẮC THÁI CẢM XÚC + COMMENT + SHARE (PANEL B) ===")
# Chuẩn bị cột type
def get_interaction_type(row):
    if row['intent'] == 'comment':
        return 'Comment'
    elif row['intent'] == 'share':
        return 'Share'
    elif row['intent'] == 'react':
        rx = str(row.get('reaction', 'LIKE')).upper()
        if 'LOVE' in rx: return 'Love'
        if 'CARE' in rx: return 'Care'
        if 'HAHA' in rx: return 'Haha'
        if 'WOW' in rx: return 'Wow'
        if 'SAD' in rx: return 'Sad'
        if 'ANGRY' in rx: return 'Angry'
        return 'Like'
    return 'Other'

interactions['sub_type'] = interactions.apply(get_interaction_type, axis=1)
ct_subtype = pd.crosstab(interactions['persona_id'], interactions['sub_type'], margins=True)
print(ct_subtype)

print("\n--- Tỷ lệ % Cơ cấu tương tác (chuẩn hóa = 100% như Panel B) ---")
ct_subtype_pct = pd.crosstab(interactions['persona_id'], interactions['sub_type'], normalize='index') * 100
print(ct_subtype_pct.round(1))

print("\n=== 5. MA TRẬN KHOẢNG CÁCH EUCLIDEAN / COSINE GIỮA 6 PERSONA TRÊN VECTOR HÀNH VI TƯƠNG TÁC ===")
from scipy.spatial.distance import pdist, squareform
dist_mat = squareform(pdist(ct_subtype_pct.values, metric='cosine'))
dist_df = pd.DataFrame(dist_mat, index=ct_subtype_pct.index, columns=ct_subtype_pct.index)
print("Cosine Distance Matrix (0 = giống nhau hoàn toàn, 1 = trực giao khác biệt):")
print(dist_df.round(3))
