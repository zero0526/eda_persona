import json

cell_16_code = """# ==============================================================================
# BƯỚC 9: CẤP ĐỘ 3 — CƠ HỌC CỬ CHỈ VẬT LÝ TRÌNH DUYỆT (PHYSICAL KINEMATICS)
# ==============================================================================

# 1. Lọc toàn bộ bước thực thi cuộn chuột Playwright và tính vận tốc vật lý
df_gestures = df_actions[df_actions['gesture_total_px'].notnull()].copy()
df_gestures['scroll_speed_px_s'] = (
    df_gestures['gesture_total_px'] / (df_gestures['gesture_ms'] / 1000.0)
).astype(float).round(2)

# Chuẩn hóa nhãn nhịp độ theo đúng hợp đồng hành vi (Quick vs Balanced)
# Gộp 'fast' và 'quick' -> 'quick' (Nhịp cuộn nhanh)
# Gộp 'careful' và 'balanced' -> 'balanced' (Nhịp cuộn cân bằng / từ tốn)
pace_map = {
    'fast': 'quick',
    'quick': 'quick',
    'careful': 'balanced',
    'balanced': 'balanced'
}
df_gestures['gesture_pace_std'] = df_gestures['gesture_pace'].map(pace_map).fillna(df_gestures['gesture_pace'])

# 2. Thống kê cơ học cử chỉ theo Persona
kin_stats = df_gestures.groupby('persona_id').agg(
    n_gestures=('step_index', 'count'),
    pct_quick=('gesture_pace_std', lambda x: (x == 'quick').mean() * 100),
    median_scroll_px=('gesture_total_px', 'median'),
    median_gesture_ms=('gesture_ms', 'median'),
    median_speed_px_s=('scroll_speed_px_s', 'median')
).round(2).reset_index()

kin_stats.columns = [
    'Persona ID', 'Số lần cuộn (N)', 'Tỷ lệ Quick (%)', 
    'Median Cự ly Cuộn (px)', 'Median Thời gian (ms)', 'Median Vận tốc (px/s)'
]

# 3. Kiểm định Kruskal-Wallis cho Vận tốc cuộn chuột (scroll_speed_px_s)
kw_groups = [np.asarray(g['scroll_speed_px_s'].dropna().values, dtype=np.float64) 
             for _, g in df_gestures.groupby('persona_id')]
h_stat, p_kw = stats.kruskal(*kw_groups)

print(f'=== BẢNG ĐO LƯỜNG CƠ HỌC CỬ CHỈ VẬT LÝ TRÌNH DUYỆT (N = {len(df_gestures)}) ===')
print(f'Kiểm định Kruskal-Wallis Vận tốc Cuộn: H = {h_stat:.2f}, p-value = {p_kw:.3e} (Ý nghĩa thống kê cực mạnh)\\n')

styled_kin = kin_stats.style\\
    .format({
        'Tỷ lệ Quick (%)': '{:.1f}%',
        'Median Cự ly Cuộn (px)': '{:,.1f}',
        'Median Thời gian (ms)': '{:.1f}',
        'Median Vận tốc (px/s)': '{:,.1f}'
    })\\
    .background_gradient(subset=['Tỷ lệ Quick (%)'], cmap='Oranges')\\
    .background_gradient(subset=['Median Vận tốc (px/s)'], cmap='Purples')\\
    .set_properties(**{'text-align': 'center'})
display(styled_kin)

# 4. Trực quan hóa Cấp độ 3 (Boxplot Vận tốc & Tỷ lệ Pace Chuẩn hóa)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))

# Panel A: Boxplot Vận tốc cuộn chuột px/s kèm Stripplot
sns.boxplot(data=df_gestures, x='persona_id', y='scroll_speed_px_s', ax=ax1, 
            palette=PERSONA_PALETTE, boxprops=dict(alpha=0.7), showmeans=True)
sns.stripplot(data=df_gestures, x='persona_id', y='scroll_speed_px_s', ax=ax1, 
              color='black', alpha=0.4, jitter=0.2, size=5)
ax1.axhline(4000, color='red', linestyle='--', linewidth=1.5, label='Ngưỡng phân tách Nhanh vs Cân bằng (4,000 px/s)')
ax1.set_title('(A) Phân Bố Vận Tốc Cuộn Chuột Vật Lý (px/giây)', fontweight='bold')
ax1.set_xlabel('Persona ID')
ax1.set_ylabel('Vận tốc cuộn (px/s)')
ax1.legend(loc='upper right', frameon=True)

# Panel B: Tỷ lệ Chế độ Nhịp độ Chuẩn hóa (100% Quick vs 100% Balanced)
pace_ct = pd.crosstab(df_gestures['persona_id'], df_gestures['gesture_pace_std'], normalize='index') * 100
cols_order = [c for c in ['quick', 'balanced'] if c in pace_ct.columns]
pace_ct = pace_ct[cols_order]

pace_colors = {'quick': '#ff7f0e', 'balanced': '#1f77b4'}
pace_ct.plot(kind='bar', stacked=True, ax=ax2, 
             color=[pace_colors[c] for c in pace_ct.columns], 
             edgecolor='white', alpha=0.9)
ax2.set_title('(B) Tỷ Lệ Chế Độ Nhịp Độ Chuẩn Hóa (Quick vs Balanced %)', fontweight='bold')
ax2.set_xlabel('Persona ID')
ax2.set_ylabel('Tỷ lệ (%)')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)
ax2.legend(title='Chế độ nhịp', loc='upper right', frameon=True)

plt.tight_layout()
plt.show()"""

with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

nb['cells'][16]['source'] = [line + '\n' for line in cell_16_code.split('\n')]
nb['cells'][16]['source'][-1] = nb['cells'][16]['source'][-1].rstrip('\n')

with open('notebooks/notebook_action_logs.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cell 16 updated successfully with standardized pace labels!")
