import sys, os
sys.path.append(os.path.abspath('.'))
import json, sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.stdout.reconfigure(encoding='utf-8')
from loaders.episode_loader import get_sqlite_path, list_episodes, load_episode

# 1. Nạp dữ liệu từ Database SQLite
DB_PATH = get_sqlite_path()
conn = sqlite3.connect(DB_PATH)
df_bots = conn.execute('SELECT b.persona_id, pv.content_json FROM bots b JOIN persona_versions pv ON pv.bot_id = b.id').fetchall()
conn.close()
personas_dict = {p_id: json.loads(p_json) if p_json else {} for p_id, p_json in df_bots}

# 2. Nạp toàn bộ Live Steps và tính Ma trận Phân bố Bề mặt (Surface Crosstab)
episodes_summary = list_episodes(DB_PATH)
all_steps = [load_episode(ep['id'], DB_PATH).to_steps_dataframe() for ep in episodes_summary]
df_steps = pd.concat(all_steps, ignore_index=True)

# Lọc các surface chính
surfaces = ['feed', 'reels', 'group', 'detail', 'search']
ct_raw = pd.crosstab(df_steps['persona_id'], df_steps['surface'].fillna('unknown'), normalize='index') * 100
for s in surfaces + ['unknown']:
    if s not in ct_raw.columns:
        ct_raw[s] = 0.0

# 3. Trích xuất 3 thuộc tính gốc Persona có Support N >= 2
records = []
for p_id in sorted(ct_raw.index):
    attrs = personas_dict.get(p_id, {}).get('attributes', {})
    
    # a. Loại hình nội dung yêu thích (Video ngắn, Video dài, Đa dạng/Khác)
    fmt_raw = attrs.get('Loại hình nội dung yêu thích nhất', '')
    if 'Video ngắn' in fmt_raw:
        fmt_grp = 'Video ngắn (N=2)'
    elif 'Video dài' in fmt_raw:
        fmt_grp = 'Video dài (N=2)'
    else:
        fmt_grp = 'Đa dạng/Khác (N=2)'
        
    # b. Mức độ sinh hoạt hội nhóm (Chỉ nằm vùng, Theo dõi đọc bài, Hỏi tư vấn)
    grp_raw = attrs.get('Mức độ sinh hoạt trong các hội nhóm và cộng đồng mạng xã hội.', '')
    if 'đặt câu hỏi' in grp_raw:
        grp_act = 'Hỏi nhờ tư vấn (N=2)'
    elif 'theo dõi và đọc bài' in grp_raw:
        grp_act = 'Theo dõi đọc bài (N=2)'
    else:
        grp_act = 'Chỉ nằm vùng (N=2)'
        
    # c. Xu hướng tư duy (Nhìn tổng quan vs Cân bằng/Chi tiết)
    focus_raw = attrs.get('Xu hướng nhìn nhận bức tranh toàn cảnh hay đi sâu vào chi tiết nhỏ.', '')
    if 'nhìn tổng quan' in focus_raw.lower():
        focus_grp = 'Nhìn tổng quan (N=3)'
    else:
        focus_grp = 'Cân bằng/Chi tiết (N=3)'
        
    row_data = {
        'persona_id': p_id,
        'Nội dung': fmt_grp,
        'Hội nhóm': grp_act,
        'Tư duy': focus_grp,
    }
    for s in surfaces + ['unknown']:
        row_data[s] = ct_raw.loc[p_id, s]
    records.append(row_data)

df_p = pd.DataFrame(records).set_index('persona_id')

# 4. Tính toán Ma trận Tổng hợp theo Nhóm Thuộc tính (Mean Surface % có Support N)
group_summary_rows = []

# Nhóm 1: Nội dung
for grp_val in ['Video ngắn (N=2)', 'Video dài (N=2)', 'Đa dạng/Khác (N=2)']:
    sub = df_p[df_p['Nội dung'] == grp_val]
    row = {'Attribute Group': 'Nội dung ưa thích', 'Value Group': grp_val, 'Support': len(sub)}
    for s in surfaces:
        row[s] = sub[s].mean()
    group_summary_rows.append(row)

# Nhóm 2: Sinh hoạt Hội nhóm
for grp_val in ['Chỉ nằm vùng (N=2)', 'Theo dõi đọc bài (N=2)', 'Hỏi nhờ tư vấn (N=2)']:
    sub = df_p[df_p['Hội nhóm'] == grp_val]
    row = {'Attribute Group': 'Sinh hoạt Hội nhóm', 'Value Group': grp_val, 'Support': len(sub)}
    for s in surfaces:
        row[s] = sub[s].mean()
    group_summary_rows.append(row)

# Nhóm 3: Tư duy
for grp_val in ['Nhìn tổng quan (N=3)', 'Cân bằng/Chi tiết (N=3)']:
    sub = df_p[df_p['Tư duy'] == grp_val]
    row = {'Attribute Group': 'Xu hướng Tư duy', 'Value Group': grp_val, 'Support': len(sub)}
    for s in surfaces:
        row[s] = sub[s].mean()
    group_summary_rows.append(row)

df_group_heatmap = pd.DataFrame(group_summary_rows).set_index('Value Group')

print("=== MA TRẬN ĐỐI SÁNH NHÓM THUỘC TÍNH GỐC (SUPPORT N >= 2) ===")
print(df_group_heatmap[['Attribute Group', 'Support'] + surfaces].round(1).to_string())
