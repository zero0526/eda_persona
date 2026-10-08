import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from loaders.action_loader import ActionLoader
from sklearn.feature_extraction.text import TfidfVectorizer

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

personas = sorted(df_actions['persona_id'].unique())
PERSONA_PALETTE = {
    'vn_fb_001': '#1f77b4',
    'vn_fb_002': '#ff7f0e',
    'vn_fb_003': '#2ca02c',
    'vn_fb_004': '#d62728',
    'vn_fb_005': '#9467bd',
    'vn_fb_006': '#8c564b'
}

session_acts = {}
session_total_acts = {}
persona_acts = {p: [] for p in personas}

for (p, s_order), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    bigrams = [f"{acts[i]}__then__{acts[i+1]}" for i in range(len(acts)-1)]
    tokens = acts + bigrams
    session_acts[(p, s_order)] = tokens
    session_total_acts[(p, s_order)] = len(grp_sorted)
    persona_acts[p].extend(tokens)

# TF-IDF with sublinear_tf=True
vec = TfidfVectorizer(token_pattern=r'(?u)\S+', lowercase=False, sublinear_tf=True)
corpus = [' '.join(persona_acts[p]) for p in personas]
X = vec.fit_transform(corpus).toarray()
features = np.array(vec.get_feature_names_out())

def format_pat(feat):
    if '__then__' in feat:
        parts = feat.split('__then__')
        p1 = parts[0].replace('@', ' [') + ']'
        p2 = parts[1].replace('@', ' [') + ']'
        return f"{p1} ➔ {p2}", "Chuỗi 2 bước"
    else:
        return feat.replace('@', ' [') + ']', "Hành vi đơn"

rows = []
for idx, p in enumerate(personas):
    top_indices = np.argsort(X[idx])[::-1]
    cnt = 0
    for i in top_indices:
        feat = features[i]
        score = X[idx][i]
        label, p_type = format_pat(feat)
        s_counts = [session_acts.get((p, s), []).count(feat) for s in [1, 2, 3, 4]]
        tot = sum(s_counts)
        active_sess = sum(1 for c in s_counts if c > 0)
        rows.append({
            'Persona ID': p,
            'Pattern Đặc Trưng (TF-IDF)': label,
            'Loại Pattern': p_type,
            'Điểm TF-IDF': round(score, 3),
            'Phiên 1': s_counts[0],
            'Phiên 2': s_counts[1],
            'Phiên 3': s_counts[2],
            'Phiên 4': s_counts[3],
            'Tổng số lần': tot,
            'TB / Phiên': round(tot / 4.0, 1),
            'Độ Bền Vững': f"{active_sess}/4 phiên"
        })
        cnt += 1
        if cnt >= 4:
            break

df_top = pd.DataFrame(rows)
print(df_top.head())

# Test plot
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 7))

# Panel A: Horizontal bar chart Top 1 Signature Pattern per Persona
top1_df = df_top.groupby('Persona ID').first().reset_index()
y_pos = np.arange(len(top1_df))
bars = ax1.barh(y_pos, top1_df['Điểm TF-IDF'], color=[PERSONA_PALETTE[p] for p in top1_df['Persona ID']], alpha=0.85, edgecolor='black')
ax1.set_yticks(y_pos)
ax1.set_yticklabels([f"{r['Persona ID']}: {r['Pattern Đặc Trưng (TF-IDF)']}" for _, r in top1_df.iterrows()], fontsize=9.5)
ax1.invert_yaxis()
ax1.set_xlabel('Điểm TF-IDF (Độ Đặc Trưng Hành Vi)', fontsize=10)
ax1.set_title('(A) Top 1 Dấu Ấn Hành Vi Đặc Trưng (TF-IDF)\\nTheo Từng Persona', fontsize=12, fontweight='bold')
ax1.grid(True, linestyle=':', alpha=0.6, axis='x')

# Add score labels on bars
for bar in bars:
    w = bar.get_width()
    ax1.text(w + 0.005, bar.get_y() + bar.get_height()/2, f"{w:.3f}", va='center', fontsize=9, fontweight='bold')

# Panel B: Heatmap tần suất xuất hiện qua các phiên của Top 1 Pattern mỗi persona
heat_data = top1_df[['Phiên 1', 'Phiên 2', 'Phiên 3', 'Phiên 4']].copy()
heat_data.index = [f"{r['Persona ID']}: {r['Pattern Đặc Trưng (TF-IDF)']}" for _, r in top1_df.iterrows()]
sns.heatmap(heat_data, annot=True, fmt='d', cmap='YlGnBu', cbar=True, ax=ax2, linewidths=0.5, cbar_kws={'label': 'Số lần xuất hiện (bước)'})
ax2.set_title('(B) Tần Suất Xuất Hiện Của Dấu Ấn Đặc Trưng\\nQua Toàn Bộ Các Phiên (Phiên 1 ➔ 4)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Thứ Tự Phiên Hoạt Động', fontsize=10)
ax2.set_ylabel('')

# Panel C: Tổng số lần xuất hiện và Độ bền vững
ax3.bar(top1_df['Persona ID'], top1_df['Tổng số lần'], color=[PERSONA_PALETTE[p] for p in top1_df['Persona ID']], alpha=0.85, edgecolor='black')
ax3.set_title('(C) Tổng Số Lần Thực Hiện Dấu Ấn Đặc Trưng\\nXuyên Suốt Tất Cả Các Phiên', fontsize=12, fontweight='bold')
ax3.set_xlabel('Persona ID', fontsize=10)
ax3.set_ylabel('Tổng Số Lần Xuất Hiện (bước)', fontsize=10)
ax3.grid(True, linestyle=':', alpha=0.6, axis='y')
for idx, r in top1_df.iterrows():
    ax3.text(idx, r['Tổng số lần'] + 3, f"{r['Tổng số lần']}\\n({r['Độ Bền Vững']})", ha='center', fontsize=8.5, fontweight='bold')

plt.tight_layout()
plt.savefig('scratch/test_tfidf_plot.png', dpi=150)
print('Plot saved successfully!')
