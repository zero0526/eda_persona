import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("notebooks/eda_action_v2.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

new_cell_10_code = """import numpy as np
import scipy.stats as stats
from sklearn.linear_model import LinearRegression

# 1. Trích xuất đặc trưng định lượng & nhị phân từ hồ sơ Persona (Khái quát hóa thuộc tính)
persona_features = []

for p_id in sorted(df_windows['persona_id'].unique()):
    p_info = personas_dict.get(p_id, {})
    attrs = p_info.get('attributes', {})
    
    # Tuổi trung bình
    age_str = attrs.get('Nhóm tuổi', '')
    age_map = {'18-24 tuổi': 21.0, '25-34 tuổi': 29.5, '35-44 tuổi': 39.5, '45-54 tuổi': 49.5, '55-64 tuổi': 59.5}
    age_val = age_map.get(age_str, 30.0)
    
    # Con cái
    child_str = attrs.get('Số con', '')
    has_child = 0 if 'Chưa có con' in child_str else 1
    
    # Thời lượng xem video
    stream_str = str(attrs.get('Tổng thời gian xem phim, video và livestream hàng tuần.', ''))
    stream_val = 5.0 if '3-7' in stream_str else (11.5 if '8-15' in stream_str else 23.0)
    
    # Giới tính & Nghề nghiệp
    is_female = 1 if attrs.get('Bản dạng giới') == 'Nữ' else 0
    work_arr = attrs.get('Hình thức làm việc hiện tại', 'Khác')
    is_fnb = 1 if p_id == 'vn_fb_004' else 0
    is_gen_x = 1 if age_val >= 55 else 0
    
    persona_features.append({
        'persona_id': p_id,
        'age_num': age_val,
        'has_children': has_child,
        'streaming_hours_num': stream_val,
        'gender_female': is_female,
        'work_freelance_fnb': is_fnb,
        'age_gen_x': is_gen_x,
        'work_arrangement': work_arr
    })

df_feat = pd.DataFrame(persona_features)
# Merge df_windows với df_feat
df_corr_data = df_windows.merge(df_feat, on=['persona_id'], how='left')
df_corr_data['is_late_night'] = (df_corr_data['start_hour_local'] >= 21).astype(int)
df_corr_data['is_early_morning'] = (df_corr_data['start_hour_local'] <= 8).astype(int)

# 2. Tính ma trận tương quan Spearman Rank Correlation đầy đủ giữa 6 biến X và 5 biến Y (Cả r và p-value)
vars_x = ['age_num', 'streaming_hours_num', 'has_children', 'gender_female', 'work_freelance_fnb', 'age_gen_x']
vars_y = ['bias_reels', 'bias_feed', 'is_late_night', 'is_early_morning', 'duration_min']

labels_x_dict = {
    'age_num': 'Độ tuổi (Age)',
    'streaming_hours_num': 'Xem video (Streaming)',
    'has_children': 'Có con nhỏ (Children)',
    'gender_female': 'Nữ giới (Female)',
    'work_freelance_fnb': 'Nghề tự do/F&B',
    'age_gen_x': 'Cao tuổi (Gen X 55+)'
}
labels_y_dict = {
    'bias_reels': 'Bias Reels (Tỷ trọng Reels)',
    'bias_feed': 'Bias Feed (Tỷ trọng Feed)',
    'is_late_night': 'Đêm muộn (>=21h)',
    'is_early_morning': 'Sáng sớm (<=8h)',
    'duration_min': 'Thời lượng phiên (phút)'
}

labels_x = [labels_x_dict[x] for x in vars_x]
labels_y = [labels_y_dict[y] for y in vars_y]

corr_table = pd.DataFrame(index=vars_x, columns=vars_y)
pval_table = pd.DataFrame(index=vars_x, columns=vars_y)

for x in vars_x:
    for y in vars_y:
        r_val, p_val = stats.spearmanr(df_corr_data[x], df_corr_data[y])
        corr_table.loc[x, y] = r_val
        pval_table.loc[x, y] = p_val

corr_table = corr_table.astype(float)
pval_table = pval_table.astype(float)

# 3. Trực quan hóa Heatmap Tương quan Spearman (r) & Mức ý nghĩa thống kê (p) tích hợp trong từng ô
annot_matrix = pd.DataFrame(index=vars_x, columns=vars_y)
for x in vars_x:
    for y in vars_y:
        r = corr_table.loc[x, y]
        p = pval_table.loc[x, y]
        if p < 0.001:
            p_str = "p<0.001***"
        elif p < 0.01:
            p_str = f"p={p:.3f}**"
        elif p < 0.05:
            p_str = f"p={p:.3f}*"
        else:
            p_str = f"p={p:.2f} (ns)"
        annot_matrix.loc[x, y] = f"{r:+.2f}\\n({p_str})"

fig, ax_corr = plt.subplots(figsize=(11, 6.5))
sns.heatmap(
    corr_table, 
    xticklabels=labels_y, 
    yticklabels=labels_x, 
    annot=annot_matrix.values, 
    fmt='', 
    cmap='coolwarm', 
    vmin=-0.65, 
    vmax=0.65, 
    cbar_kws={'label': "Hệ số tương quan Spearman (r)"},
    linewidths=1.2,
    linecolor='white',
    annot_kws={'fontsize': 10, 'weight': 'bold'},
    ax=ax_corr
)
ax_corr.set_title("MA TRẬN HỆ SỐ TƯƠNG QUAN SPEARMAN (r) & Ý NGHĨA THỐNG KÊ (p) - KIỂM ĐỊNH GIẢ THUYẾT H1\\n(*: p < 0.05, **: p < 0.01, ***: p < 0.001; ns: không có ý nghĩa thống kê; N = 392 phiên)", fontsize=12, fontweight='bold', pad=15)
ax_corr.tick_params(axis='x', rotation=15)
plt.tight_layout()
plt.show()

# 4. BẢNG TÁC ĐỘNG CỰC ĐẠI (|r| MAX) & KẾT LUẬN KIỂM ĐỊNH GIẢ THUYẾT H1
max_impact_rows = []
for y in vars_y:
    abs_r_series = corr_table[y].abs()
    max_x = abs_r_series.idxmax()
    max_r = corr_table.loc[max_x, y]
    p_val = pval_table.loc[max_x, y]
    
    if p_val < 0.001:
        sig_text = "Cực cao (p < 0.001)***"
    elif p_val < 0.01:
        sig_text = "Rất cao (p < 0.01)**"
    elif p_val < 0.05:
        sig_text = "Có ý nghĩa (p < 0.05)*"
    else:
        sig_text = "Không ý nghĩa (p >= 0.05 ns)"
        
    conclusion = "Bác bỏ H0, Chấp nhận H1 (Tác động rõ rệt)" if p_val < 0.05 else "Chưa đủ bằng chứng bác bỏ H0"
    direction = "Đồng biến (Tăng ↑)" if max_r > 0 else "Nghịch biến (Giảm ↓)"
    
    max_impact_rows.append({
        'Biến Kết Quả (Y)': labels_y_dict[y],
        'Yếu Tố Ảnh Hưởng Lớn Nhất (Max X)': labels_x_dict[max_x],
        'Hệ số r Max': f"{max_r:+.3f}",
        '|r| Max': f"{abs(max_r):.3f}",
        'Hướng Tác Động': direction,
        'p-value': f"{p_val:.2e}",
        'Mức Ý Nghĩa Thống Kê': sig_text,
        'Kết Luận Kiểm Định H1': conclusion
    })

df_max_impact = pd.DataFrame(max_impact_rows)
print("=== BẢNG TÁC ĐỘNG CỰC ĐẠI (|r| MAX) VÀ KẾT LUẬN KIỂM ĐỊNH GIẢ THUYẾT H1 ===")
display(df_max_impact)

# 5. BẢNG MA TRẬN P-VALUE CHI TIẾT TOÀN DIỆN (FULL P-VALUE MATRIX)
pval_display = pval_table.copy()
pval_display.index = labels_x
pval_display.columns = labels_y
for col in pval_display.columns:
    pval_display[col] = pval_display[col].apply(lambda p: f"{p:.2e}")
print("\\n=== MA TRẬN P-VALUE TOÀN DIỆN (FULL P-VALUE MATRIX) ===")
display(pval_display)
"""

nb["cells"][10]["source"] = [line + "\n" for line in new_cell_10_code.split("\n")]
if nb["cells"][10]["source"] and nb["cells"][10]["source"][-1] == "\n":
    nb["cells"][10]["source"].pop()

with open("notebooks/eda_action_v2.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Updated Cell 10 with max impact table, integrated r & p heatmap, and full p-value matrix successfully!")
