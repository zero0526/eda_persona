import nbformat

nb_path = 'notebooks/notebook_action_logs.ipynb'
nb = nbformat.read(nb_path, as_version=4)

# ==============================================================================
# CELL 25: CẬP NHẬT BẢNG 4 THÀNH SO SÁNH SAI KHÁC S1 -> S2
# ==============================================================================
nb.cells[25].source = r"""# ==============================================================================
# BƯỚC 14: THÓI QUEN THAO TÁC, MA TRẬN TƯƠNG ĐỒNG 13 PHIÊN & TRỰC QUAN HÓA
# ==============================================================================

import matplotlib.pyplot as plt
from algorithms.cross_session_behavior_profiler import (
    compute_surface_retention_comparison,
    compute_habit_evolution_and_correlation
)
from viz.session_consistency_viz import plot_h3_three_panel_comparison

# 1. BẢNG SO SÁNH MỨC ĐỘ Ở LẠI TRÊN CÁC MÀN HÌNH GIỮA CÁC PHIÊN (S1 -> S2)
df_surface_comparison = compute_surface_retention_comparison(df_actions_h3)

print("=== BẢNG 4: SO SÁNH MỨC ĐỘ Ở LẠI TRÊN CÁC MÀN HÌNH GIỮA CÁC PHIÊN (S1 -> S2) ===")
styled_surface_comp = (
    df_surface_comparison.style
    .format({
        'Tỷ lệ ở lại S1 (%)': '{:.1f}%',
        'Tỷ lệ ở lại S2 (%)': '{:.1f}%',
        'Sai khác mức ở lại (%)': '{:+.1f}%'
    })
    .background_gradient(subset=['Tỷ lệ ở lại S1 (%)', 'Tỷ lệ ở lại S2 (%)'], cmap='Blues', vmin=70, vmax=100)
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Thói quen màn hình', 'Nhận xét chuyển biến thực tế'], **{'text-align': 'left'})
)
display(styled_surface_comp)

# 2. BẢNG THEO DÕI THÓI QUEN CŨ VS THAO TÁC MỚI XUẤT HIỆN
evolution_data = compute_habit_evolution_and_correlation(df_actions_h3)
df_evolution = evolution_data['evolution_df']

print("\n=== BẢNG 5: MỨC ĐỘ GIỮ LẠI THÓI QUEN CŨ VÀ PHÁT SINH THAO TÁC MỚI ===")
styled_evolution = (
    df_evolution[['Persona', 'Cặp phiên', 'Số thao tác phiên 1', 'Số thao tác phiên 2', 
                  'Thao tác giữ lại', 'Thao tác mới xuất hiện', 'Tỷ lệ thao tác quen thuộc (%)', 
                  'Tỷ lệ thao tác mới (%)', 'Độ tương đồng (r)', 'Các thao tác mới cụ thể']].style
    .format({
        'Tỷ lệ thao tác quen thuộc (%)': '{:.1f}%',
        'Tỷ lệ thao tác mới (%)': '{:.1f}%',
        'Độ tương đồng (r)': '{:.4f}'
    })
    .background_gradient(subset=['Độ tương đồng (r)'], cmap='Greens', vmin=0.0, vmax=1.0)
    .background_gradient(subset=['Tỷ lệ thao tác quen thuộc (%)'], cmap='Blues', vmin=50, vmax=100)
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Các thao tác mới cụ thể'], **{'text-align': 'left'})
)
display(styled_evolution)

# 3. THỐNG KÊ ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN
print("\n=== ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN ===")
print(f"- Khi so sánh cùng Persona qua các phiên: r trung bình = {evolution_data['intra_mean']:.4f} +/- {evolution_data['intra_std']:.4f} (Trung vị: {evolution_data['intra_median']:.4f})")
print(f"- Khi so sánh khác Persona giữa các phiên: r trung bình = {evolution_data['inter_mean']:.4f} +/- {evolution_data['inter_std']:.4f} (Trung vị: {evolution_data['inter_median']:.4f})")
print("- Nhận xét: Độ tương đồng hành vi của cùng Persona cao hơn rõ rệt so với giữa các Persona khác nhau.")

# 4. TRỰC QUAN HÓA 3-PANEL BẰNG BIỂU ĐỒ GẦN GŨI
fig, axes = plot_h3_three_panel_comparison(
    df_session_corr=evolution_data['correlation_matrix'],
    df_evolution=df_evolution,
    intra_vals=evolution_data['intra_correlations'],
    inter_vals=evolution_data['inter_correlations']
)
plt.show()
"""

nbformat.write(nb, nb_path)
print("Updated Cell 25 with comparative Table 4 successfully!")
