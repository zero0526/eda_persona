import sys, os
sys.path.append(os.path.abspath('.'))
import json, sqlite3
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
from loaders.episode_loader import get_sqlite_path, list_episodes, load_episode

# 1. Nạp dữ liệu
DB_PATH = get_sqlite_path()
conn = sqlite3.connect(DB_PATH)
df_bots = conn.execute('SELECT b.persona_id, pv.content_json FROM bots b JOIN persona_versions pv ON pv.bot_id = b.id').fetchall()
conn.close()
personas_dict = {p_id: json.loads(p_json) if p_json else {} for p_id, p_json in df_bots}

episodes_summary = list_episodes(DB_PATH)
all_steps = [load_episode(ep['id'], DB_PATH).to_steps_dataframe() for ep in episodes_summary]
df_steps = pd.concat(all_steps, ignore_index=True)

# Lọc các bước có surface xác định
df_clean = df_steps.dropna(subset=['surface']).copy()
df_clean = df_clean[df_clean['surface'] != 'unknown']

# 2. Gắn 194 trường persona vào từng step
first_pid = list(personas_dict.keys())[0]
attr_keys = list(personas_dict[first_pid].get('attributes', {}).keys())

for k in attr_keys:
    df_clean[k] = df_clean['persona_id'].map(lambda pid: personas_dict.get(pid, {}).get('attributes', {}).get(k, 'N/A'))

# 3. Tính Cramér's V và Chi-square cho từng thuộc tính với surface
def cramers_v(contingency_table):
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    r, k = contingency_table.shape
    phi2 = chi2 / n
    phi2_corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    r_corr = r - ((r - 1) ** 2) / (n - 1)
    k_corr = k - ((k - 1) ** 2) / (n - 1)
    denom = min(k_corr - 1, r_corr - 1)
    if denom <= 0:
        return 0.0
    return np.sqrt(phi2_corr / denom)

results = []
for k in attr_keys:
    # Bảng chéo giữa thuộc tính k và surface
    ct = pd.crosstab(df_clean[k], df_clean['surface'])
    # Bỏ qua nếu thuộc tính không có sự biến thiên
    if ct.shape[0] <= 1:
        continue
    chi2, p_val, dof, _ = stats.chi2_contingency(ct)
    v = cramers_v(ct)
    # Đếm số giá trị phân loại khác nhau
    n_categories = df_clean[k].nunique()
    results.append({
        'attribute': k,
        'n_categories': n_categories,
        'cramers_v': v,
        'chi2': chi2,
        'p_value': p_val
    })

df_res = pd.DataFrame(results).sort_values(by='cramers_v', ascending=False)

print("=== TOP 20 TRƯỜNG PHÂN TÁCH SURFACE MẠNH NHẤT (THEO CRAMÉR'S V) ===")
print(df_res.head(25)[['attribute', 'n_categories', 'cramers_v', 'chi2', 'p_value']].to_string(index=False))
