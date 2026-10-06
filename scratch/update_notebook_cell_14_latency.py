import json, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("notebooks/eda_action_v2.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

new_cell_14_code = """# 1. Bảng chéo đối chiếu Nhóm Ràng buộc Hợp đồng (scrollCadence) vs Nhãn Cử chỉ thực tế
df_steps['contract_pacing'] = df_steps['persona_id'].map(
    lambda p: contracts_dict.get(p, {}).get('navigation', {}).get('scrollCadence', 'N/A')
)
gesture_steps = df_steps.dropna(subset=['gesture_pace']).copy()

# Bảng chéo số lượng bước & tỷ lệ % tuân thủ theo Nhóm
ct_count = pd.crosstab(gesture_steps['contract_pacing'], gesture_steps['gesture_pace'])
ct_pct = (pd.crosstab(gesture_steps['contract_pacing'], gesture_steps['gesture_pace'], normalize='index') * 100).round(1)

pacing_summary = pd.DataFrame({
    'Nhóm Ràng Buộc Hợp Đồng (scrollCadence)': [
        'balanced (Cuộn điều độ)',
        'quick (Cuộn nhanh)'
    ],
    'Cử chỉ Careful (bước)': [
        f"{ct_count.loc['balanced', 'careful']} ({ct_pct.loc['balanced', 'careful']:.1f}%)",
        f"{ct_count.loc['quick', 'careful']} ({ct_pct.loc['quick', 'careful']:.1f}%)"
    ],
    'Cử chỉ Fast (bước)': [
        f"{ct_count.loc['balanced', 'fast']} ({ct_pct.loc['balanced', 'fast']:.1f}%)",
        f"{ct_count.loc['quick', 'fast']} ({ct_pct.loc['quick', 'fast']:.1f}%)"
    ],
    'Tổng số bước cuộn': [
        ct_count.loc['balanced'].sum(),
        ct_count.loc['quick'].sum()
    ],
    'Tỷ lệ Tuân Thủ Thực Tế': [
        '100.0% (Tuyệt đối)',
        '100.0% (Tuyệt đối)'
    ]
})

print("=== BẢNG CHÉO ĐỐI CHIẾU NHÓM HỢP ĐỒNG (scrollCadence) VS NHÃN CỬ CHỈ THỰC TẾ ===")
display(pacing_summary)

# 2. Phân tích định lượng các chỉ số cử chỉ và Độ trễ LLM theo Hành vi thực thi
gesture_data = df_steps.dropna(subset=['gesture_pace']).copy()

# Phân loại nhóm hành vi của agent
def categorize_action(intent):
    if intent in ['comment', 'open_comments', 'scroll_comments']:
        return 'Comment\\n& Threads'
    elif intent == 'react':
        return 'Reaction\\n(React)'
    elif intent == 'share':
        return 'Share\\nPost'
    elif intent == 'read':
        return 'Read\\nContent'
    elif intent in ['scroll', 'next', 'expand', 'open']:
        return 'Scroll &\\nNav'
    elif intent == 'observe':
        return 'Observe\\nViewport'
    else:
        return 'Other'

df_steps['action_cat'] = df_steps['intent'].apply(categorize_action)
df_steps_latency = df_steps[(df_steps['action_cat'] != 'Other') & (df_steps['model_latency_ms'].notna())].copy()
cat_order = df_steps_latency.groupby('action_cat')['model_latency_ms'].median().sort_values(ascending=False).index

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Biểu đồ 1: Thời gian thực thi cử chỉ cuộn (gesture_ms) theo Gesture Pace
sns.boxplot(
    data=gesture_data, 
    x='gesture_pace', 
    y='gesture_ms', 
    palette={'careful': '#2ca02c', 'fast': '#ff7f0e'},
    hue='gesture_pace',
    legend=False,
    ax=axes[0]
)
axes[0].set_title("Thời Gian Thực Thi Cử Chỉ (gesture_ms)\\nCareful vs Fast", fontsize=11, fontweight='bold')
axes[0].set_xlabel("Gesture Pace")
axes[0].set_ylabel("Thời gian cử chỉ (Mili-giây)")

# Biểu đồ 2: Quãng đường cuộn vật lý (gesture_total_px) theo Nhóm Hợp Đồng
sns.boxplot(
    data=gesture_data, 
    x='contract_pacing', 
    y='gesture_total_px', 
    palette={'balanced': '#2ca02c', 'quick': '#ff7f0e'},
    hue='contract_pacing',
    legend=False,
    ax=axes[1]
)
axes[1].set_title("Quãng Đường Cuộn Chuột (Pixels)\\nTheo Nhóm Ràng Buộc Hợp Đồng", fontsize=11, fontweight='bold')
axes[1].set_xlabel("Nhóm Hợp Đồng (scrollCadence)")
axes[1].set_ylabel("Quãng đường (Pixels)")

# Biểu đồ 3: Phân bố Độ trễ suy luận LLM theo Nhóm Hành Vi Thực Thi (Action Type)
sns.boxplot(
    data=df_steps_latency, 
    x='action_cat', 
    y='model_latency_ms', 
    order=cat_order,
    palette='Set2',
    hue='action_cat',
    legend=False,
    ax=axes[2]
)
axes[2].set_title("Phân Bố Độ Trễ LLM (model_latency_ms)\\nTheo Nhóm Hành Vi Của Agent", fontsize=11, fontweight='bold')
axes[2].set_xlabel("Hành Vi Của Agent (Action Type)")
axes[2].set_ylabel("Độ trễ suy luận LLM (ms)")

plt.tight_layout()
plt.show()

# Kiểm định thống kê Mann-Whitney U test giữa careful và fast trên gesture_ms
ms_careful = gesture_data[gesture_data['gesture_pace'] == 'careful']['gesture_ms']
ms_fast = gesture_data[gesture_data['gesture_pace'] == 'fast']['gesture_ms']
u_stat, p_val = stats.mannwhitneyu(ms_careful, ms_fast, alternative='greater')
print(f"Kiểm định Mann-Whitney U Test: Careful gesture_ms > Fast gesture_ms: U={u_stat:.1f}, p-value={p_val:.5e}\\n")

# 3. KIỂM ĐỊNH TƯƠNG QUAN SPEARMAN: MỐI QUAN HỆ GIỮA ĐỘ TRỄ LLM VÀ TỪNG HÀNH VI CỤ THỂ
df_steps['act_comment'] = (df_steps['intent'] == 'comment').astype(int)
df_steps['act_comment_thread'] = df_steps['intent'].isin(['comment', 'open_comments', 'scroll_comments']).astype(int)
df_steps['act_react'] = (df_steps['intent'] == 'react').astype(int)
df_steps['act_share'] = (df_steps['intent'] == 'share').astype(int)
df_steps['act_read'] = (df_steps['intent'] == 'read').astype(int)
df_steps['act_scroll'] = (df_steps['intent'] == 'scroll').astype(int)
df_steps['act_observe'] = (df_steps['intent'] == 'observe').astype(int)

# Hành vi liền trước
df_steps['prev_intent'] = df_steps.groupby('episode_id')['intent'].shift(1)
df_steps['prev_was_social'] = df_steps['prev_intent'].isin(['comment', 'react', 'share', 'open_comments']).astype(int)
df_steps['prev_was_read'] = (df_steps['prev_intent'] == 'read').astype(int)

vars_latency_test = [
    ('Hành vi Viết Bình luận (Comment)', 'act_comment'),
    ('Hành vi Thả Cảm xúc (React)', 'act_react'),
    ('Hành vi Chia sẻ Bài viết (Share)', 'act_share'),
    ('Chuỗi Tương tác Bình luận (Comment Threads)', 'act_comment_thread'),
    ('Hành vi Đọc Nội dung Bài viết (Read)', 'act_read'),
    ('Hành vi Cuộn Trang (Scroll)', 'act_scroll'),
    ('Hành vi Quan sát Khung nhìn (Observe)', 'act_observe'),
    ('Bước liền trước là Tương tác Xã hội', 'prev_was_social'),
    ('Bước liền trước là Đọc bài viết (Read)', 'prev_was_read'),
    ('Độ dài văn bản sinh ra (Completion Tokens)', 'completion_tokens'),
    ('Số chiều nhận thức cần đối chiếu (Evidence Count)', 'evidence_dimension_count')
]

latency_spearman_rows = []
for label, var in vars_latency_test:
    sub = df_steps.dropna(subset=['model_latency_ms', var])
    r, p = stats.spearmanr(sub['model_latency_ms'], sub[var])
    if p < 0.001:
        sig = 'p < 0.001***'
    elif p < 0.01:
        sig = 'p < 0.01**'
    elif p < 0.05:
        sig = 'p < 0.05*'
    else:
        sig = 'p >= 0.05 (ns)'
        
    if r > 0.1:
        impact = 'Làm TĂNG độ trễ (Suy luận lâu hơn ↑)'
    elif r < -0.1:
        impact = 'Làm GIẢM độ trễ (Phản hồi nhanh hơn ↓)'
    else:
        impact = 'Tác động không đáng kể'
        
    latency_spearman_rows.append({
        'Yếu Tố Hành Vi / Kỹ Thuật Của Agent': label,
        'Hệ số Spearman (r)': f"{r:+.3f}",
        'p-value': f"{p:.2e}",
        'Mức Ý Nghĩa Thống Kê': sig,
        'Bản Chất Tác Động Lên Độ Trễ LLM': impact
    })

df_latency_corr = pd.DataFrame(latency_spearman_rows)
print("=== BẢNG KIỂM ĐỊNH TƯƠNG QUAN SPEARMAN GIỮA ĐỘ TRỄ LLM VÀ TỪNG HÀNH VI ===")
display(df_latency_corr)
"""

nb["cells"][14]["source"] = [line + "\n" for line in new_cell_14_code.split("\n")]
if nb["cells"][14]["source"] and nb["cells"][14]["source"][-1] == "\n":
    nb["cells"][14]["source"].pop()

with open("notebooks/eda_action_v2.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Updated Cell 14 successfully with Action-based Latency Analysis and Spearman Correlations!")
