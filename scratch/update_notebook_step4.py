import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path('notebooks/eda_action_logs.ipynb')
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Keep cells 0 to 20 intact
cells_0_to_20 = nb['cells'][:21]

# Build new cells for Step 4 (cells 21 to 30)
new_cells = []

# Cell 21 [MD]: Introduction to Step 4
cell_21_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# BƯỚC 4: PHÂN TÍCH ĐƠN BIẾN (UNIVARIATE ANALYSIS)\n",
        "\n",
        "Mục tiêu của Bước 4 là tính toán phân phối độc lập các tham số thống kê mô tả cho cả 2 trường hợp **Persona** ($N=349$) và **No-Persona** ($N=88$), đồng thời chọn lọc ra các trường tiêu biểu nhất có **TÍNH SUY LUẬN HÀNH VI SÂU SẮC (Deep Behavioral & Cognitive Inferences)** thay vì các hệ quả kỹ thuật hiển nhiên.\n",
        "\n",
        "> **CHUYỂN DỊCH TỪ ĐẶC TRƯNG CƠ HỌC HIỂN NHIÊN SANG CHỈ SỐ NHẬN THỨC BẢN CHẤT:**\n",
        "> Thay vì chọn các biến hiển nhiên như `model_latency_ms` hay `reason_length` (vốn dĩ dài hơn do LLM phải giải trình theo persona), chúng tôi khảo sát **4 chỉ số phản ánh bản chất nhận thức và tổ chức hành vi**:\n",
        "> 1. **`wm_num_active_threads`**: Dung lượng đa nhiệm nhận thức (Cognitive Multi-threading Capacity).\n",
        "> 2. **`recent_last_gesture_px`**: Cơ học cuộn chuột vật lý (Biomechanical Gesture Dynamics).\n",
        "> 3. **`wm_cumulative_reads`**: Chiều sâu đọc và thẩm thấu nội dung thực chất (Deep Content Engagement).\n",
        "> 4. **`wm_cumulative_opened`**: Mức độ bứt phá khỏi Feed để thâm nhập Page/Group (Domain Exploration Depth)."
    ]
}

# Cell 22 [CODE]: 4.1 Numeric profiling
cell_22_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 4.1. Thực thi phân tích định lượng có tính suy luận hành vi sâu sắc & Vẽ biểu đồ so sánh\n",
        "from algorithms.univariate_numeric_profiler import profile_numeric_variables, compute_separate_distribution_tables\n",
        "from viz.univariate_viz import plot_top_numeric_comparison\n",
        "\n",
        "# 1. Xuất 2 bảng phân phối chi tiết 14 tham số độc lập cho từng nhóm\n",
        "sep_tables = compute_separate_distribution_tables(df_steps)\n",
        "sep_tables[\"persona_distribution\"].to_csv(project_root / \"output\" / \"tables\" / \"step4_numeric_profile_persona.csv\", encoding=\"utf-8-sig\", index=False)\n",
        "sep_tables[\"nopersona_distribution\"].to_csv(project_root / \"output\" / \"tables\" / \"step4_numeric_profile_no_persona.csv\", encoding=\"utf-8-sig\", index=False)\n",
        "\n",
        "# 2. Tạo bảng so sánh tập trung 4 biến định lượng nhận thức cốt lõi\n",
        "numeric_cols = [\"wm_num_active_threads\", \"recent_last_gesture_px\", \"wm_cumulative_reads\", \"wm_cumulative_opened\"]\n",
        "df_num_profile = profile_numeric_variables(df_steps, target_cols=numeric_cols)\n",
        "df_num_profile.to_csv(project_root / \"output\" / \"tables\" / \"step4_numeric_profile.csv\", index=False, encoding=\"utf-8-sig\")\n",
        "\n",
        "# 3. Vẽ biểu đồ so sánh phân phối trực quan\n",
        "plot_top_numeric_comparison(df_steps, output_path=project_root / \"output\" / \"figures\" / \"step4_top_numeric_comparison.png\")\n",
        "\n",
        "print(\"=== BẢNG HỒ SƠ SO SÁNH 4 BIẾN ĐỊNH LƯỢNG NHẬN THỨC CỐT LÕI (CHƯƠNG 4.1) ===\")\n",
        "display(df_num_profile.style.set_properties(**{'text-align': 'right'}).format({\n",
        "    'Persona_Mean': '{:.2f}', 'Persona_Median': '{:.2f}', 'Persona_Std': '{:.2f}',\n",
        "    'NoPersona_Mean': '{:.2f}', 'NoPersona_Median': '{:.2f}', 'NoPersona_Std': '{:.2f}',\n",
        "    'p_value': '{:.4f}'\n",
        "}))\n",
        "\n",
        "# Hiển thị ảnh so sánh trực quan\n",
        "from IPython.display import Image, display\n",
        "display(Image(filename=str(project_root / \"output\" / \"figures\" / \"step4_top_numeric_comparison.png\")))"
    ]
}

# Cell 23 [MD]: 4.2 Guardrail Warning & Surface Exploration
cell_23_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 4.2. Cơ chế Tiết chế (Brake/Guardrail), Bứt phá Không gian (Surface) & Tính Khả dụng (Verified)\n",
        "\n",
        "Khảo sát các biến phân loại và cờ bảo vệ để đánh giá mức độ kháng trôi dạt hành vi và tính kỷ luật của Agent:\n",
        "- **`wm_has_novelty_warning` (Cờ cảnh báo tiết chế tại từng bước):** Khi `situational_steps >= 3`, hệ thống kích hoạt thông điệp *\"CẢNH BÁO TIẾT CHẾ: Bạn đã dành nhiều thời gian cho chủ đề tình huống này. Hãy chủ động quay lại các mạch chính...\"*.\n",
        "  - **No-Persona:** Bị còi cảnh báo hú vang **$30.68\\%$ số bước** ($27/88$ bước)! Riêng tập `755b1653`, Agent bị cảnh báo kéo dài suốt $27/41$ bước ($65.85\\%$) do không có sở thích cốt lõi để quay về.\n",
        "  - **Persona:** Tuyệt đối **$0.0\\%$ số bước** ($0/349$ bước) bị cảnh báo. Agent sở hữu la bàn nội tâm tự điều chỉnh (`core threads`), tự giác quay lại mạch chính sau 1-2 bước.\n",
        "- **`surface` (Không gian giao diện):** Persona phân bổ đa chiều: Feed ($34.1\\%$), Search ($16.6\\%$), và **bứt phá vào `group` ($14.6\\%$) + `page` ($10.3\\%$)**. Ngược lại, No-Persona **$0.0\\%$ ở Group/Page**, bị bẫy $21.6\\%$ thời gian ở màn hình `detail`.\n",
        "- **`verified` (Tính hợp lệ của thao tác):** Persona đạt tỷ lệ thao tác chuẩn xác **$77.65\\%$ True**, trong khi No-Persona chỉ đạt **$61.36\\%$ True** (tỷ lệ lỗi/click mò mẫm cao gấp 1.7 lần)."
    ]
}

# Cell 24 [CODE]: 4.2 Guardrail code execution & display
cell_24_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 4.2. Thống kê Cơ chế Cảnh báo Tiết chế Guardrail, Phân phối Surface & Verified\n",
        "df_guardrail_sum = pd.read_csv(project_root / \"output\" / \"tables\" / \"step4_guardrail_warning_summary.csv\")\n",
        "df_cat_profile = pd.read_csv(project_root / \"output\" / \"tables\" / \"step4_categorical_profile.csv\")\n",
        "\n",
        "print(\"=== BẢNG TỔNG HỢP CƠ CHẾ CẢNH BÁO TIẾT CHẾ (GUARDRAIL WARNING PROFILE) ===\")\n",
        "display(df_guardrail_sum.style.set_properties(**{'text-align': 'left'}))\n",
        "\n",
        "print(\"\\n=== BẢNG PHÂN BỐ KHÔNG GIAN GIAO DIỆN (SURFACE) VÀ TÍNH HỢP LỆ (VERIFIED) ===\")\n",
        "display(df_cat_profile[df_cat_profile['Biến số'].isin(['surface', 'verified'])].style.set_properties(**{'text-align': 'left'}))\n",
        "\n",
        "# Vẽ lại biểu đồ so sánh biến phân loại\n",
        "from viz.univariate_viz import plot_top_categorical_comparison\n",
        "plot_top_categorical_comparison(df_steps, output_path=project_root / \"output\" / \"figures\" / \"step4_categorical_comparison.png\")\n",
        "display(Image(filename=str(project_root / \"output\" / \"figures\" / \"step4_categorical_comparison.png\")))"
    ]
}

# Cell 25 [MD]: 4.3 Session Termination Profile & Temporal Latency
cell_25_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 4.3. Hồ sơ Thoát Phiên (Termination Causes) & Sản Lượng Tri Nhận Lúc Thoát (Exit Yield)\n",
        "\n",
        "Khảo sát bước cuối cùng của mỗi phiên (`last_step`) và các chỉ số tích lũy tại thời điểm dừng hoạt động:\n",
        "- **`termination_cause` (Nguyên nhân dừng phiên):**\n",
        "  - **Persona:** Có tới **$50.0\\%$ số phiên tự dừng chủ động khi thỏa mãn mục tiêu** (Agent hoàn thành nhiệm vụ, mức năng lượng giảm dần: *\"Đã đọc 8 bài viết, tìm kiếm 4 chủ đề, hứng thú giảm dần, thời gian kết thúc phù hợp\"*). $16.7\\%$ Timeout 600s, $16.7\\%$ UI Deadlock, $16.7\\%$ Forced Cutoff.\n",
        "  - **No-Persona:** $100\\%$ kết thúc trong bế tắc: $50\\%$ do Bế tắc giao diện (UI Deadlock: kẹt modal 6 lần close lỗi) và $50\\%$ do Hết giờ thuần túy (Timeout 600s).\n",
        "- **Sản lượng tri nhận tại thời điểm kết thúc phiên (Output Yield at Exit):**\n",
        "  - **`reads_at_exit`:** Persona đạt trung bình **$3.67$ bài đọc** (tối đa 6 bài) vs No-Persona chỉ **$0.50$ bài** (tối đa 1 bài).\n",
        "  - **`searches_at_exit`:** Persona tìm kiếm trung bình **$3.33$ chủ đề** vs No-Persona chỉ **$1.00$ chủ đề**.\n",
        "  - **`opened_at_exit`:** Persona mở rộng **$3.17$ nguồn Page/Group** vs No-Persona **$0.00$ nguồn**.\n",
        "- **`step_delta_sec` (Cự ly thời gian giữa 2 bước liên tiếp):** Persona duy trì nhịp độ ổn định, tự nhiên như con người (Trung vị = $8.91$s, $75\\% = 12.53$s). Ngược lại, No-Persona giật cục và bất thường (Trung vị = $4.07$s hoặc ngưng trệ $24 - 63$s do bế tắc)."
    ]
}

# Cell 26 [CODE]: 4.3 Termination display & 4-subplot visualization
cell_26_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 4.3. Xuất Bảng Hồ sơ Thoát Phiên & Trực quan hóa 4 Ô Phân phối Đơn biến Mở rộng\n",
        "df_term_profile = pd.read_csv(project_root / \"output\" / \"tables\" / \"step4_termination_profile.csv\")\n",
        "\n",
        "print(\"=== BẢNG HỒ SƠ THOÁT PHIÊN VÀ SẢN LƯỢNG TRI NHẬN TẠI THỜI ĐIỂM DỪNG (EXIT PROFILE) ===\")\n",
        "display(df_term_profile[[\"group\", \"file_name\", \"total_steps\", \"elapsed_seconds\", \"overtime_seconds\", \"end_tool\", \"termination_cause\", \"reads_at_exit\", \"searches_at_exit\", \"opened_at_exit\"]].style.set_properties(**{'text-align': 'left'}))\n",
        "\n",
        "# Hiển thị biểu đồ 4 ô (Termination, Exit Yield, Surface, Verified)\n",
        "display(Image(filename=str(project_root / \"output\" / \"figures\" / \"step4_univariate_termination_and_surfaces.png\")))"
    ]
}

# Cell 27 [MD]: 4.4 NLP underthesea
cell_27_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 4.4. Phân tích NLP Tiếng Việt (underthesea) & So Sánh Phân Phối Token Bằng Log-Odds Ratio\n",
        "\n",
        "Để đào sâu vào **suy nghĩ nhận thức (Chain-of-Thought - `reason`)** của Agent và tìm ra các từ ngữ đặc trưng phân hóa tư duy giữa 2 nhóm, chúng tôi xây dựng pipeline xử lý ngôn ngữ tự nhiên tiếng Việt:\n",
        "1. **Tách từ ghép tiếng Việt (Vietnamese Word Segmentation):** Sử dụng thư viện chuyên dụng `underthesea` (`word_tokenize`) để nhận diện chính xác các khái niệm đa âm tiết (`bài_viết`, `sở_thích`, `khám_phá`, `tương_tác`, `bình_luận`, `thông_tin`, `nội_dung`...).\n",
        "2. **Lọc Stopwords tên miền mạng xã hội:** Loại bỏ các từ dừng giao diện (`page`, `group`, `mở`, `home`, `sở_thích`, `khám_phá`, `có`, `like`, `react`, `bài`, `xem`...).\n",
        "3. **Tính toán Phân phối Xác suất Token:**\n",
        "   $$P_P(w) = \\frac{\\text{count}_P(w)}{\\sum_v \\text{count}_P(v)}, \\quad P_N(w) = \\frac{\\text{count}_N(w)}{\\sum_v \\text{count}_N(v)}$$\n",
        "4. **Tính toán Log-Odds Ratio $LR(w)$:**\n",
        "   $$LR(w) = \\log\\frac{P_P(w) + \\epsilon}{P_N(w) + \\epsilon}$$\n",
        "   - $LR(w) > 0$: Từ ngữ phản ánh bản sắc độc bản của Persona (`cờ_vua`, `thiền`, `cộng_đồng`, `phù_hợp`, `nhiếp_ảnh`, `yoga`, `đạp_xe`...).\n",
        "   - $LR(w) < 0$: Từ ngữ phản ánh suy luận thụ động, cơ học của No-Persona (`kết_quả`, `tìm_kiếm`, `quay_lại`, `lướt`, `chi_tiết`, `truy_vấn`...)."
    ]
}

# Cell 28 [CODE]: 4.4 NLP code execution
cell_28_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 4.4. Pipeline underthesea tokenization & Log-Ratio Distribution Comparison\n",
        "from algorithms.underthesea_log_ratio_profiler import compute_underthesea_log_ratio\n",
        "from viz.underthesea_viz import plot_underthesea_log_ratio_divergence\n",
        "\n",
        "# 1. Thực thi tách từ underthesea và tính toán Log-ratio\n",
        "log_ratio_res = compute_underthesea_log_ratio(\n",
        "    df_steps,\n",
        "    text_col=\"reason\",\n",
        "    group_col=\"dataset_type\",\n",
        "    min_count=2,\n",
        "    filter_stopwords=True\n",
        ")\n",
        "\n",
        "df_lr = log_ratio_res[\"log_ratio_table\"]\n",
        "df_lr.to_csv(project_root / \"output\" / \"tables\" / \"step4_underthesea_log_ratio.csv\", index=False, encoding=\"utf-8-sig\")\n",
        "\n",
        "# 2. Vẽ biểu đồ phân cực Log-Ratio\n",
        "plot_underthesea_log_ratio_divergence(\n",
        "    log_ratio_res,\n",
        "    top_k=15,\n",
        "    output_path=project_root / \"output\" / \"figures\" / \"step4_underthesea_log_ratio.png\"\n",
        ")\n",
        "\n",
        "print(\"=== TOP TOKEN PHÂN HÓA SUY NGHĨ NHẬN THỨC (LOG-ODDS RATIO VỚI UNDERTHESEA) ===\")\n",
        "display(df_lr.head(15).style.set_properties(**{'text-align': 'right'}).format({\n",
        "    'prob_persona': '{:.4f}', 'prob_nopersona': '{:.4f}', 'log_ratio': '{:+.2f}'\n",
        "}))\n",
        "\n",
        "# Hiển thị biểu đồ phân kỳ từ vựng NLP\n",
        "display(Image(filename=str(project_root / \"output\" / \"figures\" / \"step4_underthesea_log_ratio.png\")))"
    ]
}

# Cell 29 [MD]: 4.5 Hypotheses Signals Mapping
cell_29_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 4.5. Tổng hợp Tín hiệu Đơn biến Gợi mở cho 5 Giả thuyết Thực nghiệm ($H_1 \\rightarrow H_5$)\n",
        "\n",
        "Toàn bộ các phát hiện phân phối đơn biến (Định lượng nhận thức + Cơ chế Guardrail + Không gian Surface + Hồ sơ Thoát phiên + NLP) đã hội tụ và tạo tiền đề vững chắc cho việc kiểm định thống kê chính thức ở Bước 5:"
    ]
}

# Cell 30 [CODE]: 4.5 Synthesis display
cell_30_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 4.5. Đọc và hiển thị Bảng Ánh xạ Tín hiệu Sơ khởi Toàn diện cho 5 Giả thuyết\n",
        "df_hypo_signals = pd.read_csv(project_root / \"output\" / \"tables\" / \"step4_hypotheses_preliminary_signals.csv\")\n",
        "display(df_hypo_signals.style.set_properties(**{\n",
        "    'text-align': 'left',\n",
        "    'white-space': 'pre-wrap',\n",
        "    'font-size': '12px'\n",
        "}))\n",
        "\n",
        "print(\"\\n\" + \"=\"*80)\n",
        "print(\"[✓] KẾT THÚC BƯỚC 4: Đã hoàn thành hồ sơ đơn biến toàn diện cho cả 2 nhóm.\")\n",
        "print(\"    Sẵn sàng chuyển sang BƯỚC 5: PHÂN TÍCH HAI BIẾN (BIVARIATE ANALYSIS) & KIỂM ĐỊNH GIẢ THUYẾT!\")\n",
        "print(\"=\"*80)"
    ]
}

new_cells = [
    cell_21_md, cell_22_code,
    cell_23_md, cell_24_code,
    cell_25_md, cell_26_code,
    cell_27_md, cell_28_code,
    cell_29_md, cell_30_code
]

nb['cells'] = cells_0_to_20 + new_cells

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Updated notebook successfully! Total cells: {len(nb['cells'])}")
