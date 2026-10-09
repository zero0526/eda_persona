import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

from loaders.action_loader import ActionLoader
loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

reacts = df_actions[df_actions['intent'] == 'react'].copy()

print("=== 1. PHÂN BỐ CÁC LOẠI CẢM XÚC (REACTION TYPES) TOÀN HỆ THỐNG & THEO PERSONA ===")
if 'reaction' in reacts.columns:
    print(pd.crosstab(reacts['persona_id'], reacts['reaction'], margins=True))

# Xem chi tiết lag-1, lag-2, lag-3 cho từng persona
df_sorted = df_actions.sort_values(by=['persona_id', 'session_id', 'step_index']).copy()
df_sorted['prev_1'] = df_sorted.groupby(['persona_id', 'session_id'])['intent'].shift(1) + '@' + df_sorted.groupby(['persona_id', 'session_id'])['surface'].shift(1)
df_sorted['prev_2'] = df_sorted.groupby(['persona_id', 'session_id'])['intent'].shift(2) + '@' + df_sorted.groupby(['persona_id', 'session_id'])['surface'].shift(2)
df_sorted['prev_3'] = df_sorted.groupby(['persona_id', 'session_id'])['intent'].shift(3) + '@' + df_sorted.groupby(['persona_id', 'session_id'])['surface'].shift(3)
df_sorted['curr'] = df_sorted['intent'] + '@' + df_sorted['surface']

react_chains = df_sorted[df_sorted['intent'] == 'react'].copy()
react_chains['chain_3'] = react_chains['prev_2'] + " ➔ " + react_chains['prev_1'] + " ➔ " + react_chains['curr']

print("\n=== 2. TỔNG HỢP CÁC PHONG CÁCH / CHUỖI TIỀN ĐỀ DẪN ĐẾN LIKE (PATTERNS) ===")
# Phân loại phong cách:
# A. "Lướt thấy vừa mắt là thả tim": scroll -> observe -> react (hoặc observe -> react)
# B. "Đọc kỹ rồi mới like": scroll -> read -> react (hoặc expand -> read -> react)
# C. "Xem clip cuốn hút rồi like": next -> watch -> react (hoặc watch -> react)
# D. "Vào nhóm chuyên môn / cộng đồng sinh hoạt rồi like": group -> read/act_on_post -> react
# E. "Vào xem bình luận rồi like": detail / scroll_comments -> react

def classify_like_style(row):
    prev1 = str(row['prev_1'])
    prev2 = str(row['prev_2'])
    surface = str(row['surface'])
    
    if 'reels' in surface or 'watch' in prev1:
        return 'Xem Video cuốn hút (Reels Binge Like)'
    elif 'group' in surface or 'group' in prev1:
        return 'Sinh hoạt hội nhóm chuyên môn (Community Like)'
    elif 'comments' in prev1 or 'detail' in surface:
        return 'Đọc sâu chi tiết & bình luận (Deep Post/Comment Like)'
    elif 'expand' in prev1 or 'expand' in prev2:
        return 'Mở rộng đọc bài dài rồi like (Technical/Long-form Like)'
    elif 'read' in prev1:
        return 'Đọc nội dung chọn lọc trên Feed (Curated Feed Like)'
    elif 'observe' in prev1:
        return 'Nhìn lướt thấy hợp gu là thả tim (Impression/Visual Like)'
    else:
        return 'Khác / Tương tác lướt nhanh'

react_chains['style_category'] = react_chains.apply(classify_like_style, axis=1)

print("\nPhân bố Phong Cách Like theo Persona:")
ct_style = pd.crosstab(react_chains['persona_id'], react_chains['style_category'])
print(ct_style)

print("\n=== 3. INSIGHT CHI TIẾT TỪ REASONS (CoT) CỦA TỪNG PERSONA ===")
for pid, group in react_chains.groupby('persona_id'):
    print(f"\n==================== {pid} ====================")
    print(f"Tổng lượt like: {len(group)} | Chiếm: {len(group)/len(react_chains)*100:.1f}% toàn hệ thống")
    print("Các phong cách chính:")
    for style, cnt in group['style_category'].value_counts().items():
        print(f"  * {style}: {cnt} lần ({cnt/len(group)*100:.1f}%)")
    print("\nTrích xuất các lý do suy nghĩ (reason) tiêu biểu:")
    for i, (_, r) in enumerate(group.iterrows()):
        if i < 4:
            rx = r.get('reaction', 'LIKE')
            print(f"  [{r['surface']} | {rx}] prev: {r['prev_2']} ➔ {r['prev_1']} ➔ {r['curr']}")
            print(f"    CoT: {str(r['reason'])[:160]}...")
