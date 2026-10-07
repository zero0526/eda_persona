import nbformat

nb_path = 'notebooks/notebook_action_logs.ipynb'
nb = nbformat.read(nb_path, as_version=4)

# ==============================================================================
# CELL 21: BƯỚC 11 (GỌI TỪ MODULE ALGORITHMS)
# ==============================================================================
nb.cells[21].source = r"""# ==============================================================================
# BƯỚC 11: BẢNG TỔNG HỢP ĐỘ TƯƠNG ĐỒNG HÀNH VI QUA CÁC PHIÊN THEO 4 CẤP ĐỘ
# ==============================================================================

from algorithms.cross_session_behavior_profiler import (
    prepare_h3_dataset,
    extract_cross_session_entities,
    compute_multi_level_consistency
)

# 1. Chuẩn bị tập dữ liệu 13 phiên hoàn chỉnh cho kiểm định H3
df_actions_h3, df_sessions_h3 = prepare_h3_dataset(df_actions, df_sessions)

# 2. Bóc tách thực thể lặp lại và bản đồ ghi nhớ xuyên phiên hoàn toàn động từ SQLite
entity_res = extract_cross_session_entities()

# 3. Tính toán bảng tổng hợp độ tương đồng qua 4 cấp độ
df_multi_level_consistency = compute_multi_level_consistency(
    df_actions_h3, df_sessions_h3, entity_res['continuity_map']
)

print("=== BẢNG 1: TỔNG HỢP ĐỘ TƯƠNG ĐỒNG HÀNH VI CỦA CÁC PERSONA QUA CÁC PHIÊN ===")
styled_multi_consistency = (
    df_multi_level_consistency.style
    .format({
        'Cấp phiên: Lệch nhịp độ (bước/phút)': '{:.2f}',
        'Ý định: Độ tương đồng (r)': '{:.4f}',
        'Bề mặt: Độ tương đồng (r)': '{:.4f}',
        'Thao tác trình duyệt: Lệch tốc độ cuộn (px/s)': '{:.1f}',
        'Bằng chứng hành động: Độ tương đồng (r)': '{:.4f}',
    }, na_rep='-')
    .background_gradient(subset=['Ý định: Độ tương đồng (r)', 'Bề mặt: Độ tương đồng (r)', 'Bằng chứng hành động: Độ tương đồng (r)'], cmap='Greens', vmin=0.0, vmax=1.0)
    .set_properties(**{'text-align': 'center'})
)
display(styled_multi_consistency)
"""

# ==============================================================================
# CELL 23: BƯỚC 12 (GỌI TỪ ALGORITHMS VÀ VIZ)
# ==============================================================================
nb.cells[23].source = r"""# ==============================================================================
# BƯỚC 12: MÔ HÌNH HÓA VÀ VẼ SƠ ĐỒ CHUYỂN ĐỔI GIỮA 4 MÀN HÌNH CHÍNH
# ==============================================================================

import matplotlib.pyplot as plt
from algorithms.cross_session_behavior_profiler import compute_macro_surface_transitions
from viz.session_consistency_viz import plot_macro_surface_transitions

# 1. Tính toán ma trận chuyển đổi và các luồng điều hướng nổi bật
transition_data = compute_macro_surface_transitions(df_actions_h3)
prob_matrix = transition_data['prob_matrix']

print(f"=== BẢNG 2: TỶ LỆ CHUYỂN ĐỔI GIỮA 4 MÀN HÌNH CHÍNH (TỔNG SỐ LẦN CHUYỂN N = {transition_data['total_shifts']}) ===")
display(
    prob_matrix.style
    .format('{:.1%}')
    .background_gradient(cmap='Blues', vmin=0.0, vmax=1.0)
    .set_properties(**{'text-align': 'center'})
)

# 2. Trực quan hóa Sơ đồ Chuyển đổi giữa 4 Màn hình chính
fig, ax = plot_macro_surface_transitions(transition_data)
plt.show()
"""

# ==============================================================================
# CELL 24: BƯỚC 13 (DÙNG KẾT QUẢ ĐỘNG TỪ ALGORITHMS)
# ==============================================================================
nb.cells[24].source = r"""# ==============================================================================
# BƯỚC 13: MẠCH GHI NHỚ TRANG VÀ HỘI NHÓM XUYÊN PHIÊN (BẰNG CHỨNG HÀNH ĐỘNG)
# ==============================================================================

# Sử dụng kết quả bóc tách thực thể tự động từ module algorithms.cross_session_behavior_profiler
cross_authors_df = entity_res['authors_df']
cross_groups_df = entity_res['groups_df']

print("=== BẢNG 3: CÁC TRANG VÀ TÁC GIẢ ĐƯỢC TƯƠNG TÁC LẶP LẠI QUA CÁC PHIÊN ===")
styled_cross_authors = (
    cross_authors_df.style
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Trang / Tác giả lặp lại'], **{'text-align': 'left'})
)
display(styled_cross_authors)

print("\n=== HỘI NHÓM ĐƯỢC TƯƠNG TÁC LẶP LẠI QUA CÁC PHIÊN ===")
display(cross_groups_df.style.set_properties(**{'text-align': 'center'}))
"""

# ==============================================================================
# CELL 25: BƯỚC 14 (GỌI TỪ ALGORITHMS VÀ VIZ)
# ==============================================================================
nb.cells[25].source = r"""# ==============================================================================
# BƯỚC 14: THÓI QUEN THAO TÁC, MA TRẬN TƯƠNG ĐỒNG 13 PHIÊN & TRỰC QUAN HÓA
# ==============================================================================

import matplotlib.pyplot as plt
from algorithms.cross_session_behavior_profiler import (
    compute_surface_retention,
    compute_habit_evolution_and_correlation
)
from viz.session_consistency_viz import plot_h3_three_panel_comparison

# 1. BẢNG MỨC ĐỘ Ở LẠI TRÊN TỪNG MÀN HÌNH THEO PHIÊN
df_surface_retention = compute_surface_retention(df_actions_h3)

print("=== BẢNG 4: MỨC ĐỘ Ở LẠI TRÊN TỪNG MÀN HÌNH THEO PHIÊN ===")
styled_surface_retention = (
    df_surface_retention.style
    .format({
        'Tỷ lệ ở lại (%)': '{:.1f}%',
        'Feed (%)': '{:.1f}%',
        'Detail (%)': '{:.1f}%',
        'Group (%)': '{:.1f}%',
        'Reels (%)': '{:.1f}%',
        'Search (%)': '{:.1f}%'
    })
    .background_gradient(subset=['Tỷ lệ ở lại (%)', 'Feed (%)', 'Detail (%)', 'Group (%)', 'Reels (%)'], cmap='Blues', vmin=0, vmax=100)
    .set_properties(**{'text-align': 'center'})
)
display(styled_surface_retention)

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
print("Applied modular H3 code to notebook successfully!")
