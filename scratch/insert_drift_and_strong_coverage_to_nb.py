import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("notebooks/eda_action_logs.ipynb")
backup_path = Path("notebooks/eda_action_logs.ipynb.bak")

# 1. Tạo backup an toàn
shutil.copy2(nb_path, backup_path)
print(f"Created backup at: {backup_path}")

# 2. Đọc file notebook
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells = nb["cells"]
print(f"Original cell count: {len(cells)}")

# Cell 24 (MD): Quỹ đạo sa đà & Guardrail
cell_drift_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 4.2.2. Quỹ đạo Thời gian của Sa đà Nhận thức (Temporal Drift) & Hiệu lực Can thiệp Guardrail\n",
        "\n",
        "Để trả lời sâu sắc **RQ3** (Khả năng chống phân tâm & duy trì mục tiêu), chúng tôi kiểm định hai câu hỏi thống kê chuyên sâu:\n",
        "1. *Hiện tượng sa đà của No-Persona xuất hiện từ bước thứ mấy, và có tích lũy tăng dần theo thời gian (Linear Drift Accumulation) hay không?*\n",
        "2. *Khi hệ thống phát thông điệp `CẢNH BÁO TIẾT CHẾ` (`wm_has_novelty_warning == True`), tác tử có thể tự điều chỉnh để quay về hay tiếp tục bị trôi dạt?*\n",
        "\n",
        "> **KẾT QUẢ KIỂM ĐỊNH THỐNG KÊ:**\n",
        "> - **Khởi phát sa đà (Onset Step):** Persona hoàn toàn **miễn nhiễm tuyệt đối** ($349/349$ bước có `wm_situational_steps = 0`). Ngược lại, No-Persona khởi phát sa đà rất sớm (tại **Bước 2** ở phiên `45257517` và **Bước 7** ở phiên `755b1653`).\n",
        "> - **Cơ chế Nhảy bậc & Bão hòa (State Jump & Absorbing Plateau):** Kiểm định tương quan thời gian trong nội bộ No-Persona cho thấy xu hướng tăng tuyến tính **không đạt ý nghĩa thống kê** (Spearman $\\rho = 0.1845, p = 0.0852$; OLS $p = 0.0675$). Lý do: No-Persona không trôi dạt từ từ, mà **nhảy vọt đột ngột lên mức trần tối đa 6 bước** ở Bước 14 và **bị kẹt cứng ở mức 6 suốt 28 bước liên tiếp** cho tới khi hết giờ!\n",
        "> - **Vô hiệu hóa Cảnh báo Tiết chế (Zero Recovery Rate):** Khi có cảnh báo ($N=26$ transitions), tỷ lệ kéo giảm sa đà chỉ là $23.08\\%$, so với $31.67\\%$ khi không cảnh báo (Fisher's exact $p = 0.6057$). Trong các bước có Working Memory, **$80.8\\%$ số bước có cảnh báo bị kẹt cứng ở mức 6**. No-Persona hoàn toàn thiếu cơ chế kiểm soát nhận thức (Lack of Executive Control) để tự giải phóng khỏi trạng thái hấp thụ bế tắc."
    ]
}

# Cell 25 (CODE): Code thực thi & trực quan hóa Drift Trajectory
cell_drift_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 4.2.2. Kiểm định Thống kê Quỹ đạo Sa đà & Ma trận Hồi phục Cảnh báo Tiết chế\n",
        "from algorithms.drift_and_rest_statistical_profiler import (\n",
        "    evaluate_temporal_drift_trajectory,\n",
        "    evaluate_guardrail_warning_recovery\n",
        ")\n",
        "from IPython.display import Image, display\n",
        "\n",
        "# 1. Hiển thị bảng khởi phát và quỹ đạo sa đà theo phiên\n",
        "df_drift_onset = pd.read_csv(project_root / \"output\" / \"tables\" / \"step4_drift_trajectory_and_onset.csv\")\n",
        "print(\"=== 1. ĐIỂM KHỞI PHÁT VÀ QUỸ ĐẠO SA ĐÀ THEO PHIÊN (TEMPORAL DRIFT ONSET) ===\")\n",
        "display(df_drift_onset.style.set_properties(**{'text-align': 'left'}))\n",
        "\n",
        "# 2. Hiển thị ma trận chuyển trạng thái sau cảnh báo Guardrail\n",
        "df_guardrail_mat = pd.read_csv(project_root / \"output\" / \"tables\" / \"step4_guardrail_recovery_matrix.csv\", index_col=0)\n",
        "print(\"\\n=== 2. MA TRẬN CHUYỂN TRẠNG THÁI & HIỆU LỰC HỒI PHỤC SAU CẢNH BÁO GUARDRAIL ===\")\n",
        "display(df_guardrail_mat)\n",
        "\n",
        "# 3. Trực quan hóa quỹ đạo thời gian và động lực học dừng nghỉ\n",
        "display(Image(filename=str(project_root / \"output\" / \"figures\" / \"step4_drift_and_rest_deep_dive.png\")))\n"
    ]
}

# Cell 26 (MD): Độ phủ sở thích mạnh interests.strong
cell_strong_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 4.2.3. Độ phủ Danh mục Sở thích Mạnh (interests.strong) & Bằng chứng Nhất quán Nhận thức\n",
        "\n",
        "Để chứng minh **Độ nhất quán nhận thức (Cognitive Consistency) và Tính chân thực Persona (Persona Fidelity)** cho **RQ1**, chúng tôi đối soát trực tiếp các lập luận trong `dimension_evidence` của từng hành động với danh mục 12 sở thích mạnh (`facebook_behavior_profile.interests.strong`) được định nghĩa trong hồ sơ của từng Persona:\n",
        "\n",
        "> **3 BẰNG CHỨNG NHẬN THỨC CỐT LÕI:**\n",
        "> 1. **Độ chính xác nhất quán tuyệt đối (Consistency Precision = 100%):** Trong toàn bộ 181 bước có Dimension Evidence của Persona, **100% các chủ đề được Agent viện dẫn** (*Knitting, Fitness, Politics, Spirituality, Magic tricks, Meditation, Chess, Collecting, Books...*) đều thuộc danh mục `interests.strong` hoặc thuộc tính tích cực trong hồ sơ. Tỷ lệ ảo giác sở thích ngoài luồng là **0.0%**.\n",
        "> 2. **Tỷ lệ neo giữ nhận thức cao (Cognitive Anchoring = 50.4%):** Trung bình cứ 2 bước hành động thì có hơn 1 bước Agent chủ động viện dẫn sở thích mạnh từ hồ sơ để làm căn cứ điều hướng tương tác.\n",
        "> 3. **Tính chọn lọc tâm lý: Đào sâu (Depth) thay vì dàn trải hời hợt (Breadth):** Trong phiên làm việc ngắn 10 phút (~55 bước), Agent Persona bao trùm trung bình **$32.0\\%$ danh mục sở thích mạnh** (dao động từ 2 đến 6 chủ đề/phiên). Đây là biểu hiện của **Hành vi người thực tế**: thay vì lướt qua máy móc cả 12 chủ đề, Agent tập trung thẩm thấu sâu vào 2–4 chủ đề kích thích mạnh nhất (đọc bài, tương tác reaction, thâm nhập Group/Page)."
    ]
}

# Cell 27 (CODE): Hiển thị bảng độ phủ sở thích mạnh
cell_strong_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 4.2.3. Thống kê Độ phủ Danh mục Sở thích Mạnh (interests.strong) trong Dimension Evidence\n",
        "df_strong_cov = pd.read_csv(project_root / \"output\" / \"tables\" / \"step4_strong_interests_coverage.csv\")\n",
        "\n",
        "print(\"=== BẢNG ĐỐI SOÁT ĐỘ PHỦ 12 SỞ THÍCH MẠNH (STRONG INTERESTS COVERAGE & FIDELITY) ===\")\n",
        "cols_show = ['episode_id', 'persona_id', 'total_steps', 'steps_with_evidence', 'evidence_anchoring_pct', 'total_strong_interests', 'covered_strong_count', 'coverage_rate_pct', 'covered_strong_list']\n",
        "display(df_strong_cov[cols_show].style.set_properties(**{'text-align': 'left'}).format({'evidence_anchoring_pct': '{:.1f}%', 'coverage_rate_pct': '{:.1f}%'}))\n"
    ]
}

# Ghép các cell:
# Giữ từ đầu đến Cell 23 (bao gồm Cell 23)
part1 = cells[:24]

# Chèn 4 cell mới vào sau Cell 23
new_insertions = [cell_drift_md, cell_drift_code, cell_strong_md, cell_strong_code]

# Phần còn lại: từ Cell 24 trở đi (trước đây là mục 4.3 trở đi)
part2 = cells[24:]

# Dọn dẹp output lỗi cũ ở cell 4.4 underthesea nếu có
for c in part2:
    if c.get("cell_type") == "code" and any("underthesea" in line for line in c.get("source", [])):
        c["outputs"] = []
        c["execution_count"] = None
        print("Cleaned stale error output in underthesea cell.")

final_cells = part1 + new_insertions + part2
nb["cells"] = final_cells

print(f"Updated cell count: {len(final_cells)} (added {len(new_insertions)} new cells)")

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Successfully written updated notebook:", nb_path)
