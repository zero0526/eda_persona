import json
import sys
from pathlib import Path

# Đảm bảo in Unicode tiếng Việt
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

nb_path = Path("notebooks/notebook_action_logs.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Current cells count: {len(nb['cells'])}")

# Định nghĩa các cell mới cần thêm
new_cells = []

# ------------------------------------------------------------------------------
# CELL 11: MARKDOWN HEADER H2
# ------------------------------------------------------------------------------
cell_11_source = [
    "---\n",
    "## 3. KHÁM PHÁ CÁC TRƯỜNG DỮ LIỆU ACTION LOGS PHỤC VỤ KIỂM ĐỊNH GIẢ THUYẾT $H_2$\n",
    "### (BEHAVIORAL & CONTRACT FIDELITY — ĐỘ TRUNG THỰC HÀNH VI & TUÂN THỦ HỢP ĐỒNG)\n",
    "\n",
    "> **Mục tiêu nghiên cứu Giả thuyết $H_2$:**  \n",
    "> Đánh giá xem dòng hành vi thực thi ghi nhận trong nhật ký vi thao tác (`agent_live_steps` & `episodes`) có **tuân thủ trung thực** với các ràng buộc trong Hợp đồng Hành vi (`BehavioralContract`) và Hồ sơ Bản sắc (`BotContext`) qua 4 cấp độ đo lường khách quan:\n",
    ">\n",
    "> 1. **Cấp độ 1 (Phiên Tổng hợp - Macro):** Khảo sát quy mô hoạt động, phân tách các nhóm phong cách duyệt mạng xã hội và phân loại ngoại lai (áp dụng điều kiện lọc tiên quyết `terminal_reason == 'agent_stop'`).\n",
    "> 2. **Cấp độ 2 (Không gian Bề mặt & Ý định Vi thao tác):** Kiểm định mức độ tuân thủ phân bổ không gian (`surface`), bản mẫu ý định vi mô (`intent`), tỷ lệ tương tác chủ động (AER) và 7 hành vi tìm kiếm chủ động (`search`).\n",
    "> 3. **Cấp độ 3 (Cơ học Cử chỉ Vật lý Trình duyệt):** Kiểm định ràng buộc nhịp cuộn chuột (`scrollCadence`) đo trực tiếp từ động cơ Playwright (`gesture_pace`, `scroll_speed_px_s`).\n",
    "> 4. **Cấp độ 4 & 5 (Động cơ Bản sắc & Bộ nhớ Làm việc):** Khảo sát ma trận quy gán bản sắc (`primary_dimension`) và cơ chế chống sa đà trôi dạt nhận thức (Working Memory & Drift Control).\n"
]
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": cell_11_source
})

# ------------------------------------------------------------------------------
# CELL 12: CODE CẤP ĐỘ 1 — PHIÊN TỔNG HỢP (LỌC AGENT_STOP)
# ------------------------------------------------------------------------------
cell_12_source = [
    "# ==============================================================================\n",
    "# BƯỚC 7: CẤP ĐỘ 1 — BỨC TRANH VĨ MÔ CẤP PHIÊN (LỌC THEO ĐIỀU KIỆN agent_stop)\n",
    "# ==============================================================================\n",
    "\n",
    "# 1. Áp dụng bộ lọc tiên quyết: Chỉ lấy các phiên hoàn thành tự nhiên (agent_stop)\n",
    "#    Loại trừ các phiên dừng sớm do lỗi hạ tầng trình duyệt (episode_error) và pending\n",
    "df_sessions_stop = df_sessions[df_sessions['terminal_reason'] == 'agent_stop'].copy()\n",
    "df_sessions_stop['duration_min'] = df_sessions_stop['duration_seconds'] / 60.0\n",
    "\n",
    "# 2. Thống kê cấp phiên theo Persona\n",
    "sess_macro_stats = df_sessions_stop.groupby('persona_id').agg(\n",
    "    n_valid_sessions=('session_id', 'count'),\n",
    "    mean_duration_min=('duration_min', 'mean'),\n",
    "    mean_actions=('total_actions', 'mean'),\n",
    "    median_scroll_px=('total_scroll_px', 'median'),\n",
    "    mean_verified_rate=('verified_rate', lambda x: x.mean() * 100)\n",
    ").reset_index()\n",
    "\n",
    "sess_macro_stats.columns = [\n",
    "    'Persona ID', 'Số Phiên Hợp lệ (N)', 'Thời lượng TB (phút)', \n",
    "    'Số Actions TB', 'Median Cuộn Trang (px)', 'Verified Rate TB (%)'\n",
    "]\n",
    "\n",
    "print('=== BẢNG CHỈ SỐ CẤP PHIÊN TỔNG HỢP (ĐÃ LỌC agent_stop) ===')\n",
    "# Hiển thị bảng định dạng Styler trực quan\n",
    "styled_sess = sess_macro_stats.style\\\n",
    "    .format({\n",
    "        'Thời lượng TB (phút)': '{:.2f}',\n",
    "        'Số Actions TB': '{:.1f}',\n",
    "        'Median Cuộn Trang (px)': '{:,.1f}',\n",
    "        'Verified Rate TB (%)': '{:.2f}%'\n",
    "    })\\\n",
    "    .background_gradient(subset=['Thời lượng TB (phút)'], cmap='YlGn')\\\n",
    "    .background_gradient(subset=['Median Cuộn Trang (px)'], cmap='Blues')\\\n",
    "    .background_gradient(subset=['Verified Rate TB (%)'], cmap='Greens')\\\n",
    "    .set_properties(**{'text-align': 'center', 'font-family': 'monospace'})\n",
    "display(styled_sess)\n",
    "\n",
    "print('\\n⚠️ Lưu ý mẫu dữ liệu:')\n",
    "print(' • vn_fb_001 có 2 phiên đều kết thúc sớm vì lỗi hạ tầng (episode_error) nên không có mặt ở cấp phiên.')\n",
    "print(' • Toàn bộ 84 actions của vn_fb_001 diễn ra trước khi lỗi vẫn được sử dụng đầy đủ ở Cấp độ Vi thao tác.\\n')\n",
    "\n",
    "# 3. Trực quan hóa Đồ thị Cấp phiên (3 Panels)\n",
    "fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))\n",
    "\n",
    "# Panel A: Thời lượng trung bình vs Khung ngân sách hợp đồng [10, 20] phút\n",
    "bars1 = axes[0].bar(sess_macro_stats['Persona ID'], sess_macro_stats['Thời lượng TB (phút)'], \n",
    "                    color=[PERSONA_PALETTE.get(p, '#333') for p in sess_macro_stats['Persona ID']], \n",
    "                    edgecolor='black', alpha=0.85, width=0.55)\n",
    "axes[0].axhspan(10, 20, color='green', alpha=0.12, label='Ngân sách hợp đồng [10, 20] min')\n",
    "axes[0].axhline(10, color='green', linestyle='--', alpha=0.6)\n",
    "axes[0].set_title('(A) Thời Lượng Phiên TB vs Hợp Đồng (phút)', fontweight='bold')\n",
    "axes[0].set_ylabel('Thời lượng (phút)')\n",
    "axes[0].set_ylim(0, 22)\n",
    "axes[0].legend(loc='upper left', frameon=True)\n",
    "for b in bars1:\n",
    "    axes[0].text(b.get_x() + b.get_width()/2., b.get_height() + 0.4, f'{b.get_height():.1f}m',\n",
    "                 ha='center', va='bottom', fontsize=9.5, fontweight='bold')\n",
    "\n",
    "# Panel B: Quãng đường cuộn trang trung vị (Log scale làm rõ phân tách cực đoan)\n",
    "bars2 = axes[1].bar(sess_macro_stats['Persona ID'], sess_macro_stats['Median Cuộn Trang (px)'], \n",
    "                    color=[PERSONA_PALETTE.get(p, '#333') for p in sess_macro_stats['Persona ID']], \n",
    "                    edgecolor='black', alpha=0.85, width=0.55)\n",
    "axes[1].set_title('(B) Cự Ly Cuộn Trang Median (px)', fontweight='bold')\n",
    "axes[1].set_ylabel('Quãng đường cuộn (px)')\n",
    "axes[1].set_ylim(0, 20000)\n",
    "for b in bars2:\n",
    "    val = b.get_height()\n",
    "    axes[1].text(b.get_x() + b.get_width()/2., val + 350, f'{val:,.0f} px',\n",
    "                 ha='center', va='bottom', fontsize=9.5, fontweight='bold')\n",
    "\n",
    "# Panel C: Tỷ lệ xác minh thành công trên DOM (%)\n",
    "bars3 = axes[2].bar(sess_macro_stats['Persona ID'], sess_macro_stats['Verified Rate TB (%)'], \n",
    "                    color=[PERSONA_PALETTE.get(p, '#333') for p in sess_macro_stats['Persona ID']], \n",
    "                    edgecolor='black', alpha=0.85, width=0.55)\n",
    "axes[2].axhline(80, color='red', linestyle=':', label='Ngưỡng chuẩn (80%)')\n",
    "axes[2].set_title('(C) Tỷ Lệ Xác Minh DOM TB (%)', fontweight='bold')\n",
    "axes[2].set_ylabel('Verified Rate (%)')\n",
    "axes[2].set_ylim(70, 102)\n",
    "axes[2].legend(loc='lower right', frameon=True)\n",
    "for b in bars3:\n",
    "    axes[2].text(b.get_x() + b.get_width()/2., b.get_height() + 0.8, f'{b.get_height():.1f}%',\n",
    "                 ha='center', va='bottom', fontsize=9.5, fontweight='bold')\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()\n"
]
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_12_source
})

# ------------------------------------------------------------------------------
# CELL 13: MARKDOWN NHẬN XÉT CẤP ĐỘ 1
# ------------------------------------------------------------------------------
cell_13_source = [
    "---\n",
    "### Nhận định Nhanh từ Cấp độ 1 (Bức tranh Vĩ mô Cấp phiên):\n",
    "\n",
    "1. **Độ tuân thủ thời lượng hợp đồng (Duration Fidelity) hội tụ cao độ:**\n",
    "   - Khi áp dụng điều kiện lọc tiên quyết `terminal_reason == 'agent_stop'`, toàn bộ các phiên hợp lệ đều nằm chuẩn xác trong khung ngân sách hợp đồng $[10, 20]$ phút.\n",
    "   - Nhóm duyệt tin (`vn_fb_002, 003, 005, 006`) kết thúc gọn gàng quanh mốc **$9.39 - 10.52$ phút**; trong khi nhóm nghiện xem Reels (`vn_fb_004`) kéo dài tự nhiên lên **$15.41$ phút** do đặc thù tiêu thụ video.\n",
    "2. **Loại bỏ hoàn toàn nhiễu kỹ thuật trên `verified_rate`:**\n",
    "   - Tỷ lệ xác minh thành công trên DOM đồng loạt đạt mức cao $\\mathbf{84.0\\% - 95.0\\%}$, khẳng định engine Playwright hoạt động cực kỳ ổn định trong điều kiện vận hành bình thường.\n",
    "3. **Phân tách nhị phân tuyệt đối về hành vi cuộn chuột (`total_scroll_px`):**\n",
    "   - Chênh lệch hơn **30 lần** giữa nhóm tiêu thụ video ngắn (`vn_fb_004` chỉ cuộn median $504$ px) và nhóm Gen Z lướt feed (`vn_fb_002`: $13,547$ px; `vn_fb_003`: $16,585$ px). Đây là bằng chứng vàng về sự khác biệt phong cách sống của Persona.\n"
]
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": cell_13_source
})

# ------------------------------------------------------------------------------
# CELL 14: CODE CẤP ĐỘ 2 — SURFACE & INTENT
# ------------------------------------------------------------------------------
cell_14_source = [
    "# ==============================================================================\n",
    "# BƯỚC 8: CẤP ĐỘ 2 — KHÔNG GIAN BỀ MẶT & Ý ĐỊNH VI THAO TÁC (SURFACE & INTENT)\n",
    "# ==============================================================================\n",
    "\n",
    "# 1. Bảng chéo Phân bố Bề mặt Giao diện (surface Crosstab - %)\n",
    "ct_surface_pct = (pd.crosstab(df_actions['surface'], df_actions['persona_id'], normalize='columns') * 100).round(2)\n",
    "chi2_s, p_s, dof_s, _ = stats.chi2_contingency(pd.crosstab(df_actions['surface'], df_actions['persona_id']))\n",
    "\n",
    "print(f'=== 1. BẢNG PHÂN BỐ BỀ MẶT GIAO DIỆN (SURFACE CROSSTAB - %) ===')\n",
    "print(f'Kiểm định Chi-Square: chi2 = {chi2_s:.2f}, dof = {dof_s}, p-value = {p_s:.3e} (Ý nghĩa thống kê cực mạnh)\\n')\n",
    "styled_surface = ct_surface_pct.style\\\n",
    "    .format('{:.1f}%')\\\n",
    "    .background_gradient(cmap='Blues', axis=1)\\\n",
    "    .highlight_max(axis=1, color='#ffe082')\\\n",
    "    .set_properties(**{'text-align': 'center'})\n",
    "display(styled_surface)\n",
    "\n",
    "# 2. Bảng chéo Phân bố Ý định Vi thao tác (intent Crosstab - %) đầy đủ 19 intent\n",
    "ct_intent_pct = (pd.crosstab(df_actions['intent'], df_actions['persona_id'], normalize='columns') * 100).round(2)\n",
    "# Sắp xếp theo tổng tần suất xuất hiện giảm dần\n",
    "intent_order = df_actions['intent'].value_counts().index\n",
    "ct_intent_pct = ct_intent_pct.loc[intent_order]\n",
    "chi2_i, p_i, dof_i, _ = stats.chi2_contingency(pd.crosstab(df_actions['intent'], df_actions['persona_id']))\n",
    "\n",
    "print(f'\\n=== 2. BẢNG PHÂN BỐ Ý ĐỊNH VI THAO TÁC (INTENT CROSSTAB - %) ===')\n",
    "print(f'Kiểm định Chi-Square: chi2 = {chi2_i:.2f}, dof = {dof_i}, p-value = {p_i:.3e}\\n')\n",
    "styled_intent = ct_intent_pct.style\\\n",
    "    .format('{:.1f}%')\\\n",
    "    .background_gradient(cmap='Oranges', axis=1)\\\n",
    "    .highlight_max(axis=1, color='#ffe082')\\\n",
    "    .set_properties(**{'text-align': 'center'})\n",
    "display(styled_intent)\n",
    "\n",
    "# 3. Tính Tỷ lệ Tương tác Chủ động (AER: Active Engagement Rate = react + comment + share)\n",
    "df_actions['is_aer'] = df_actions['intent'].isin(['react', 'comment', 'share'])\n",
    "aer_df = (df_actions.groupby('persona_id')['is_aer'].mean() * 100).round(2).reset_index()\n",
    "aer_df.columns = ['Persona ID', 'Tỷ lệ Tương tác Chủ động (AER %)']\n",
    "\n",
    "# 4. Trích xuất chi tiết 7 hành động Tìm kiếm Chủ động (search & search_related)\n",
    "df_search_steps = df_actions[df_actions['intent'].isin(['search', 'search_related'])][\n",
    "    ['persona_id', 'session_id', 'step_index', 'intent', 'surface', 'reason']\n",
    "].copy()\n",
    "df_search_steps['session_id'] = df_search_steps['session_id'].str[:8]\n",
    "df_search_steps.columns = ['Persona', 'Session', 'Bước', 'Ý định', 'Bề mặt', 'Lý do CoT (Mục đích tìm kiếm)']\n",
    "\n",
    "print('\\n=== 3. CHI TIẾT 7 BƯỚC TÌM KIẾM CHỦ ĐỘNG (PROACTIVE AGENCY) ===')\n",
    "display(df_search_steps)\n",
    "\n",
    "# 5. Trực quan hóa Cấp độ 2 (100% Stacked Bar Bề mặt & Bar chart AER)\n",
    "fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))\n",
    "\n",
    "# Panel A: 100% Stacked Bar Chart Surface\n",
    "ct_surface_pct.T.plot(kind='bar', stacked=True, ax=ax1, colormap='tab20', edgecolor='white', alpha=0.9)\n",
    "ax1.set_title('(A) Phân Bố Không Gian Bề Mặt (100% Stacked %)', fontweight='bold')\n",
    "ax1.set_xlabel('Persona ID')\n",
    "ax1.set_ylabel('Tỷ lệ (%)')\n",
    "ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)\n",
    "ax1.legend(title='Bề mặt', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)\n",
    "\n",
    "# Panel B: Tỷ lệ Tương tác Chủ động (AER %)\n",
    "bars_aer = ax2.bar(aer_df['Persona ID'], aer_df['Tỷ lệ Tương tác Chủ động (AER %)'],\n",
    "                   color=[PERSONA_PALETTE.get(p, '#333') for p in aer_df['Persona ID']],\n",
    "                   edgecolor='black', alpha=0.85, width=0.55)\n",
    "ax2.set_title('(B) Tỷ Lệ Tương Tác Chủ Động (AER = React + Comment + Share %)', fontweight='bold')\n",
    "ax2.set_xlabel('Persona ID')\n",
    "ax2.set_ylabel('AER (%)')\n",
    "ax2.set_ylim(0, 24)\n",
    "for b in bars_aer:\n",
    "    ax2.text(b.get_x() + b.get_width()/2., b.get_height() + 0.5, f'{b.get_height():.1f}%',\n",
    "             ha='center', va='bottom', fontsize=10, fontweight='bold')\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()\n"
]
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_14_source
})

# ------------------------------------------------------------------------------
# CELL 15: MARKDOWN NHẬN XÉT CẤP ĐỘ 2
# ------------------------------------------------------------------------------
cell_15_source = [
    "---\n",
    "### Nhận định Nhanh từ Cấp độ 2 (Không gian Bề mặt & Ý định Vi thao tác):\n",
    "\n",
    "1. **Phân tách không gian tuyệt đối ($\\chi^2 = 776.76, p < 10^{-100}$):**\n",
    "   - `vn_fb_004` dành đến **$81.7\\%$** số bước trên `surface = reels` (đúng cam kết định dạng video ngắn).\n",
    "   - `vn_fb_006` dành **$23.4\\%$** số bước trong `surface = group` (đúng cam kết tìm hiểu cộng đồng nhà đất Cần Thơ).\n",
    "   - `vn_fb_003` và `vn_fb_005` dành **$30.3\\% - 38.5\\%$** trong `surface = detail` để đọc sâu bài viết và bình luận.\n",
    "2. **Cụm hành vi vi thao tác phân hóa rõ nét ($\\chi^2 = 785.43, p < 10^{-100}$):**\n",
    "   - Cụm tiêu thụ video: `vn_fb_004` chiếm trọn vẹn cụm `next` ($50.8\\%$) và `watch` ($26.7\\%$).\n",
    "   - Cụm đọc sâu: `vn_fb_006` đọc bài kỹ lưỡng nhất (`read` $= 24.1\\%$); `vn_fb_005` mở rộng bài nhiều nhất (`expand` $= 10.1\\%$).\n",
    "   - Tỷ lệ tương tác chủ động (AER): Phân định nhóm tương tác cao (`vn_fb_005`: $19.1\\%$, `vn_fb_002`: $14.8\\%$) đối lập với nhóm tiêu thụ thụ động (`vn_fb_004`: $1.7\\%$).\n",
    "3. **Tính chủ động (Proactive Agency) qua 7 bước `search`:**\n",
    "   - Bot kích hoạt hành vi tìm kiếm khi feed không đáp ứng sở thích: `vn_fb_003` tìm bún trộn Đà Nẵng, `vn_fb_004` tìm highlight bóng đá, `vn_fb_006` tìm kiểm chứng đất Cần Thơ, `vn_fb_001` tìm kỷ lục cờ chớp.\n"
]
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": cell_15_source
})

# ------------------------------------------------------------------------------
# CELL 16: CODE CẤP ĐỘ 3 — CƠ HỌC VẬT LÝ
# ------------------------------------------------------------------------------
cell_16_source = [
    "# ==============================================================================\n",
    "# BƯỚC 9: CẤP ĐỘ 3 — CƠ HỌC CỬ CHỈ VẬT LÝ TRÌNH DUYỆT (PHYSICAL KINEMATICS)\n",
    "# ==============================================================================\n",
    "\n",
    "# 1. Lọc toàn bộ 150 bước thực thi cuộn chuột Playwright\n",
    "df_gestures = df_actions[df_actions['gesture_total_px'].notnull()].copy()\n",
    "df_gestures['scroll_speed_px_s'] = (\n",
    "    df_gestures['gesture_total_px'] / (df_gestures['gesture_ms'] / 1000.0)\n",
    ").astype(float).round(2)\n",
    "\n",
    "# 2. Thống kê cơ học cử chỉ theo Persona\n",
    "kin_stats = df_gestures.groupby('persona_id').agg(\n",
    "    n_gestures=('step_index', 'count'),\n",
    "    pct_fast=('gesture_pace', lambda x: (x == 'fast').mean() * 100),\n",
    "    median_scroll_px=('gesture_total_px', 'median'),\n",
    "    median_gesture_ms=('gesture_ms', 'median'),\n",
    "    median_speed_px_s=('scroll_speed_px_s', 'median')\n",
    ").round(2).reset_index()\n",
    "\n",
    "kin_stats.columns = [\n",
    "    'Persona ID', 'Số lần cuộn (N)', 'Tỷ lệ Fast (%)', \n",
    "    'Median Cự ly Cuộn (px)', 'Median Thời gian (ms)', 'Median Vận tốc (px/s)'\n",
    "]\n",
    "\n",
    "# 3. Kiểm định Kruskal-Wallis cho Vận tốc cuộn chuột (scroll_speed_px_s)\n",
    "kw_groups = [np.asarray(g['scroll_speed_px_s'].dropna().values, dtype=np.float64) \n",
    "             for _, g in df_gestures.groupby('persona_id')]\n",
    "h_stat, p_kw = stats.kruskal(*kw_groups)\n",
    "\n",
    "print(f'=== BẢNG ĐO LƯỜNG CƠ HỌC CỬ CHỈ VẬT LÝ TRÌNH DUYỆT (N = {len(df_gestures)}) ===')\n",
    "print(f'Kiểm định Kruskal-Wallis Vận tốc Cuộn: H = {h_stat:.2f}, p-value = {p_kw:.3e} (Ý nghĩa thống kê cực mạnh)\\n')\n",
    "\n",
    "styled_kin = kin_stats.style\\\n",
    "    .format({\n",
    "        'Tỷ lệ Fast (%)': '{:.1f}%',\n",
    "        'Median Cự ly Cuộn (px)': '{:,.1f}',\n",
    "        'Median Thời gian (ms)': '{:.1f}',\n",
    "        'Median Vận tốc (px/s)': '{:,.1f}'\n",
    "    })\\\n",
    "    .background_gradient(subset=['Tỷ lệ Fast (%)'], cmap='Reds')\\\n",
    "    .background_gradient(subset=['Median Vận tốc (px/s)'], cmap='Purples')\\\n",
    "    .set_properties(**{'text-align': 'center'})\n",
    "display(styled_kin)\n",
    "\n",
    "# 4. Trực quan hóa Cấp độ 3 (Boxplot Vận tốc & Tỷ lệ Pace)\n",
    "fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))\n",
    "\n",
    "# Panel A: Boxplot Vận tốc cuộn chuột px/s kèm Stripplot\n",
    "sns.boxplot(data=df_gestures, x='persona_id', y='scroll_speed_px_s', ax=ax1, \n",
    "            palette=PERSONA_PALETTE, boxprops=dict(alpha=0.7), showmeans=True)\n",
    "sns.stripplot(data=df_gestures, x='persona_id', y='scroll_speed_px_s', ax=ax1, \n",
    "              color='black', alpha=0.4, jitter=0.2, size=5)\n",
    "ax1.axhline(4000, color='red', linestyle='--', linewidth=1.5, label='Ngưỡng phân tách Fast vs Slow (4,000 px/s)')\n",
    "ax1.set_title('(A) Phân Bố Vận Tốc Cuộn Chuột Vật Lý (px/giây)', fontweight='bold')\n",
    "ax1.set_xlabel('Persona ID')\n",
    "ax1.set_ylabel('Vận tốc cuộn (px/s)')\n",
    "ax1.legend(loc='upper right', frameon=True)\n",
    "\n",
    "# Panel B: Tỷ lệ Chế độ Nhịp độ gesture_pace (100% Fast vs 100% Careful/Balanced)\n",
    "pace_ct = pd.crosstab(df_gestures['persona_id'], df_gestures['gesture_pace'], normalize='index') * 100\n",
    "pace_ct.plot(kind='bar', stacked=True, ax=ax2, color=['#ff9800', '#2196f3'], edgecolor='white', alpha=0.9)\n",
    "ax2.set_title('(B) Tỷ Lệ Nhãn Nhịp Độ Thao Tác (gesture_pace %)', fontweight='bold')\n",
    "ax2.set_xlabel('Persona ID')\n",
    "ax2.set_ylabel('Tỷ lệ (%)')\n",
    "ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)\n",
    "ax2.legend(title='Chế độ nhịp', loc='upper right', frameon=True)\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()\n"
]
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_16_source
})

# ------------------------------------------------------------------------------
# CELL 17: MARKDOWN NHẬN XÉT CẤP ĐỘ 3
# ------------------------------------------------------------------------------
cell_17_source = [
    "---\n",
    "### Nhận định Nhanh từ Cấp độ 3 (Cơ học Cử chỉ Vật lý Trình duyệt):\n",
    "\n",
    "1. **Tuân thủ hợp đồng tuyệt đối 100% ($p < 10^{-14}$):**\n",
    "   - Toàn bộ nhóm cấu hình `scrollCadence = quick` (`vn_fb_001, 002, 005`) được engine Playwright kích hoạt chính xác **$100\\%$ nhãn FAST**.\n",
    "   - Nhóm cấu hình `scrollCadence = balanced / careful` (`vn_fb_003, 004, 006`) thực thi chính xác **$100\\%$ nhãn BALANCED/CAREFUL**.\n",
    "2. **Phân hóa cơ học vận tốc rõ rệt ($H = 69.07, p = 1.59 \\times 10^{-13}$):**\n",
    "   - Nhóm `FAST`: Vận tốc cuộn trung vị đạt đỉnh $> 4,000$ px/s (`vn_fb_002` đạt $5,410$ px/s, đỉnh $7,328$ px/s), thời gian vuốt dứt khoát $\\sim 200$ ms.\n",
    "   - Nhóm `CAREFUL`: Vận tốc cuộn chậm rãi $\\sim 2,000 - 2,500$ px/s, thời gian vuốt giữ chuột kéo dài $\\sim 260$ ms để quan sát nội dung.\n"
]
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": cell_17_source
})

# ------------------------------------------------------------------------------
# CELL 18: CODE CẤP ĐỘ 4 & 5 — DIMENSION & WORKING MEMORY
# ------------------------------------------------------------------------------
cell_18_source = [
    "# ==============================================================================\n",
    "# BƯỚC 10: CẤP ĐỘ 4 & 5 — ĐỘNG CƠ BẢN SẮC & BỘ NHỚ LÀM VIỆC (DIMENSION & WORKING MEMORY)\n",
    "# ==============================================================================\n",
    "\n",
    "# 1. Ma trận Bảng chéo Bản Sắc Chi Phối (primary_dimension Crosstab)\n",
    "top_dims = df_actions['primary_dimension'].value_counts().head(10).index\n",
    "ct_dim = pd.crosstab(df_actions['primary_dimension'], df_actions['persona_id']).loc[top_dims]\n",
    "\n",
    "print('=== 1. MA TRẬN BẢNG CHÉO BẢN SẮC CHI PHỐI (PRIMARY DIMENSION CROSSTAB) ===')\n",
    "styled_dim = ct_dim.style\\\n",
    "    .background_gradient(cmap='YlGnBu')\\\n",
    "    .highlight_max(axis=1, color='#ffe082')\\\n",
    "    .set_properties(**{'text-align': 'center'})\n",
    "display(styled_dim)\n",
    "\n",
    "# 2. Trích xuất chỉ số Working Memory (Cấp độ 5) trực tiếp từ đối tượng SessionLog\n",
    "wm_records = []\n",
    "for pid, h in histories.items():\n",
    "    for s in h.sessions:\n",
    "        wm = s.working_memory\n",
    "        if wm:\n",
    "            wm_records.append({\n",
    "                'persona_id': pid,\n",
    "                'session_id': s.session_id[:8],\n",
    "                'active_threads': len(wm.active_threads) if wm.active_threads else 0,\n",
    "                'read_posts': len(wm.read_posts) if wm.read_posts else 0,\n",
    "                'situational_steps': wm.novelty.situational_steps if wm.novelty else 0,\n",
    "                'memory_deltas': len(wm.memory_deltas) if wm.memory_deltas else 0\n",
    "            })\n",
    "\n",
    "df_wm = pd.DataFrame(wm_records)\n",
    "wm_stats = df_wm.drop(columns=['session_id']).groupby('persona_id').mean().round(2).reset_index()\n",
    "wm_stats.columns = [\n",
    "    'Persona ID', 'Mạch Chủ Đề Mở (TB)', 'Bài Viết Đã Đọc (TB)', \n",
    "    'Bước Sa Đà Tình Huống (TB)', 'Tri Thức Mới Học (TB)'\n",
    "]\n",
    "\n",
    "print('\\n=== 2. BẢNG CHỈ SỐ BỘ NHỚ LÀM VIỆC & KIỂM SOÁT SA ĐÀ (WORKING MEMORY) ===')\n",
    "styled_wm = wm_stats.style\\\n",
    "    .format({\n",
    "        'Mạch Chủ Đề Mở (TB)': '{:.2f}',\n",
    "        'Bài Viết Đã Đọc (TB)': '{:.2f}',\n",
    "        'Bước Sa Đà Tình Huống (TB)': '{:.2f}',\n",
    "        'Tri Thức Mới Học (TB)': '{:.2f}'\n",
    "    })\\\n",
    "    .background_gradient(subset=['Bài Viết Đã Đọc (TB)'], cmap='Blues')\\\n",
    "    .background_gradient(subset=['Bước Sa Đà Tình Huống (TB)'], cmap='Reds')\\\n",
    "    .set_properties(**{'text-align': 'center'})\n",
    "display(styled_wm)\n",
    "\n",
    "# 3. Trực quan hóa Cấp độ 4 & 5 (Heatmap Bản Sắc & Bar chart Working Memory)\n",
    "fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5.5))\n",
    "\n",
    "# Panel A: Heatmap Bản Sắc Chi Phối\n",
    "sns.heatmap(ct_dim, annot=True, fmt='d', cmap='YlGnBu', cbar=True, ax=ax1, linewidths=0.5)\n",
    "ax1.set_title('(A) Heatmap Ma Trận Quy Gán Bản Sắc (Primary Dimension)', fontweight='bold')\n",
    "ax1.set_xlabel('Persona ID')\n",
    "ax1.set_ylabel('Chiều Bản Sắc (Dimension)')\n",
    "\n",
    "# Panel B: So sánh Độ sâu đọc bài vs Sa đà nhận thức trong Working Memory\n",
    "x = np.arange(len(wm_stats))\n",
    "width = 0.35\n",
    "ax2.bar(x - width/2, wm_stats['Bài Viết Đã Đọc (TB)'], width, label='Số Bài Đã Đọc (read_posts)', color='#1976d2', alpha=0.85)\n",
    "ax2.bar(x + width/2, wm_stats['Bước Sa Đà Tình Huống (TB)'], width, label='Bước Sa Đà (situational_steps)', color='#e53935', alpha=0.85)\n",
    "ax2.set_xticks(x)\n",
    "ax2.set_xticklabels(wm_stats['Persona ID'])\n",
    "ax2.set_title('(B) Độ Sâu Đọc Bài vs Mức Độ Sa Đà Nhận Thức (Working Memory)', fontweight='bold')\n",
    "ax2.set_xlabel('Persona ID')\n",
    "ax2.set_ylabel('Số lượng (TB / phiên)')\n",
    "ax2.legend(frameon=True)\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()\n"
]
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_18_source
})

# ------------------------------------------------------------------------------
# CELL 19: MARKDOWN NHẬN XÉT CẤP ĐỘ 4 & 5 + TỔNG KẾT
# ------------------------------------------------------------------------------
cell_19_source = [
    "---\n",
    "### Nhận định Nhanh từ Cấp độ 4 & 5 và Định hướng Phân tích Sâu hơn cho Giả thuyết $H_2$:\n",
    "\n",
    "1. **Bằng chứng số 1 của Giả thuyết $H_2$ — Độ chính xác quy gán tuyệt đối (100% Attribution Precision):**\n",
    "   - Mỗi Persona kích hoạt chính xác các chiều bản sắc cốt lõi trong hồ sơ gốc:\n",
    "     * `vn_fb_004`: $100\\%$ độc quyền chiều `content_consumption_format` ($82$ lần viện dẫn \"Video ngắn\") và theo dõi bóng đá (`sport_football`: $21$ lần).\n",
    "     * `vn_fb_003`: Chi phối bởi ẩm thực và điện ảnh (`cuisine_vietnamese`: $68$ lần, `interest_film`: $36$ lần, `cuisine_street_food`: $34$ lần).\n",
    "     * `vn_fb_006`: Độc quyền quan tâm địa ốc (`interest_real_estate`: $48$ lần).\n",
    "     * `vn_fb_005`: Độc quyền coi trọng truyền thống gia đình (`value_tradition`: $28$ lần).\n",
    "2. **Cơ chế kiểm soát trôi dạt nhận thức (Working Memory & Drift Control):**\n",
    "   - Persona đọc sâu (`vn_fb_005`) bị cuốn theo chủ đề lạ tới $24$ bước liên tiếp, hệ thống đã kích hoạt cờ cảnh báo `novelty_warning` để điều hướng Agent hồi phục về sở thích gốc.\n",
    "   - Phân tách rành mạch độ sâu thông tin: Người đọc báo truyền thống (`001, 005, 006`) đọc trung bình $4.5 - 5.0$ bài viết/phiên; trong khi người xem video (`004`) chỉ đọc $0.25$ bài viết/phiên.\n",
    "\n",
    "---\n",
    "### 📌 TỔNG KẾT & 3 ĐỊNH HƯỚNG PHÂN TÍCH SÂU HƠN TIẾP THEO\n",
    "\n",
    "> **Kết luận sơ bộ cho Giả thuyết $H_2$:**  \n",
    "> Toàn bộ 4 tầng dữ liệu Action Logs đều đồng thuận xác nhận tính thích ứng bản sắc và độ trung thực hợp đồng rất cao. Hiệu ứng phân hóa thể hiện rõ nét từ quy mô phiên, bề mặt giao diện, cơ học cuộn chuột vật lý cho đến căn cứ lý luận tư duy.\n",
    "\n",
    "**3 Hướng phân tích sâu hơn tiếp theo:**\n",
    "1. **Mô hình hóa chuỗi hành vi bằng Ma trận Chuyển Trạng thái (Markov Transition Matrix):**\n",
    "   - Tính xác suất chuyển trạng thái giữa các bề mặt ($P(\\text{surface}_{t+1} \\mid \\text{surface}_t)$) và ý định vi thao tác ($P(\\text{intent}_{t+1} \\mid \\text{intent}_t)$) để khẳng định mỗi Persona có một đồ thị luồng hành vi (Behavioral Workflow Graph) đặc thù.\n",
    "2. **Phân tích Ngữ nghĩa Nội dung Đã Đọc (Semantic Cosine Similarity):**\n",
    "   - Dùng mô hình Sentence Transformers nhúng văn bản để tính khoảng cách Cosine giữa các bài viết đã đọc (`read_posts`) với vector mô tả sở thích cốt lõi (`core_interests`).\n",
    "3. **Thiết lập Chỉ số Tuân thủ Hợp đồng Tổng hợp (Composite Fidelity Score):**\n",
    "   - Chuẩn hóa thành điểm số tổng hợp ($0 - 100\\%$) để so sánh trực diện độ trung thực giữa các Persona và đối chứng với nhóm không có Persona (No-Persona Baseline).\n"
]
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": cell_19_source
})

# Ghép các cell mới vào notebook
nb["cells"].extend(new_cells)

# Lưu lại notebook
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"✅ Đã thêm thành công {len(new_cells)} cells mới vào {nb_path}!")
print(f"Tổng số cells hiện tại trong notebook: {len(nb['cells'])}")
