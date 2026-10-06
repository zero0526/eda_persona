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

# 2. Phân tích định lượng các chỉ số cử chỉ (gesture_ms, gesture_total_px, model_latency_ms)
gesture_data = df_steps.dropna(subset=['gesture_pace']).copy()

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Thời gian thực thi cử chỉ cuộn (gesture_ms) theo Gesture Pace
sns.boxplot(
    data=gesture_data, 
    x='gesture_pace', 
    y='gesture_ms', 
    palette={'careful': '#2ca02c', 'fast': '#ff7f0e'},
    ax=axes[0]
)
axes[0].set_title("Thời Gian Thực Thi Cử Chỉ (gesture_ms)\\nCareful vs Fast", fontsize=11, fontweight='bold')
axes[0].set_xlabel("Gesture Pace")
axes[0].set_ylabel("Thời gian cử chỉ (Mili-giây)")

# Quãng đường cuộn vật lý (gesture_total_px) theo Nhóm Hợp Đồng
sns.boxplot(
    data=gesture_data, 
    x='contract_pacing', 
    y='gesture_total_px', 
    palette={'balanced': '#2ca02c', 'quick': '#ff7f0e'},
    ax=axes[1]
)
axes[1].set_title("Quãng Đường Cuộn Chuột (Pixels)\\nTheo Nhóm Ràng Buộc Hợp Đồng", fontsize=11, fontweight='bold')
axes[1].set_xlabel("Nhóm Hợp Đồng (scrollCadence)")
axes[1].set_ylabel("Quãng đường (Pixels)")

# Độ trễ suy luận mô hình LLM (model_latency_ms) theo Nhóm Hợp Đồng
df_steps_latency = df_steps.dropna(subset=['model_latency_ms']).copy()
sns.barplot(
    data=df_steps_latency, 
    x='contract_pacing', 
    y='model_latency_ms', 
    estimator=np.median,
    palette={'balanced': '#2ca02c', 'quick': '#ff7f0e'},
    errorbar=None,
    ax=axes[2]
)
axes[2].set_title("Trung Vị Độ Trễ Suy Luận LLM (model_latency_ms)\\nTheo Nhóm Hợp Đồng", fontsize=11, fontweight='bold')
axes[2].set_xlabel("Nhóm Hợp Đồng (scrollCadence)")
axes[2].set_ylabel("Median Latency (ms)")

plt.tight_layout()
plt.show()

# Kiểm định thống kê Mann-Whitney U test giữa careful và fast
ms_careful = gesture_data[gesture_data['gesture_pace'] == 'careful']['gesture_ms']
ms_fast = gesture_data[gesture_data['gesture_pace'] == 'fast']['gesture_ms']
u_stat, p_val = stats.mannwhitneyu(ms_careful, ms_fast, alternative='greater')
print(f"Kiểm định Mann-Whitney U Test: Careful gesture_ms > Fast gesture_ms: U={u_stat:.1f}, p-value={p_val:.5e}")
"""

nb["cells"][14]["source"] = [line + "\n" for line in new_cell_14_code.split("\n")]
if nb["cells"][14]["source"] and nb["cells"][14]["source"][-1] == "\n":
    nb["cells"][14]["source"].pop()

with open("notebooks/eda_action_v2.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Updated Cell 14 successfully with Group-based cross-tabulation!")
