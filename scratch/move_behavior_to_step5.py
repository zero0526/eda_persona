import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("notebooks/eda_action_logs.ipynb")
backup_path = Path("notebooks/eda_action_logs.ipynb.bak2")

# Backup
shutil.copy2(nb_path, backup_path)
print(f"Backed up {nb_path} to {backup_path}")

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Initial total cells: {len(nb['cells'])}")

# 1. Tìm và xóa cell 4.3.2 nếu nó đang nằm trong phần 4
cells_filtered = []
for idx, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    if "### 4.3.2. Động lực học Phân bố Hành vi theo Tiến trình Thời gian" in src:
        print(f"Removing misplaced cell 4.3.2 markdown at index {idx}")
        continue
    if "# 4.3.2. Đối soát Phân bố Hành vi theo Tiến trình Thời gian" in src:
        print(f"Removing misplaced cell 4.3.2 code at index {idx}")
        continue
    cells_filtered.append(cell)

nb["cells"] = cells_filtered
print(f"Cells after removing 4.3.2: {len(nb['cells'])}")

# 2. Tạo Markdown Cell cho Mục 5
md_step5 = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# 5: PHÂN TÍCH HAI BIẾN VÀ ĐA BIẾN (BIVARIATE & MULTIVARIATE ANALYSIS)\n",
        "\n",
        "Sau khi hoàn tất việc khảo sát độc lập các biến ở Bước 4, Bước 5 mở rộng phân tích các mối quan hệ tương tác, sự biến đổi theo tiến trình thời gian và đối sánh đa chiều giữa hai nhóm thực nghiệm:\n",
        "- **Nhóm Can thiệp (Persona):** Agent được nạp hồ sơ người dùng đa chiều (`demographics`, `psychographics`, `facebook_behavior_profile`).\n",
        "- **Nhóm Đối chứng (No-Persona):** Agent trung tính hoạt động tự do không có hồ sơ định hướng.\n",
        "\n",
        "## 5.1. Động lực học Phân bố Hành vi theo Tiến trình Thời gian (Temporal Dynamics: Persona vs No-Persona)\n",
        "\n",
        "Để hiểu rõ cách thức phân bổ nỗ lực nhận thức và hành động diễn biến như thế nào theo thời gian, chúng tôi chuẩn hóa toàn bộ chuỗi thao tác của các phiên thành **4 giai đoạn tiến trình ($Q_1 \\rightarrow Q_4$ từ 0% đến 100% thời lượng phiên)** và phân nhóm các hành động thành các nhóm hành vi cốt lõi (Macro-Behaviors):\n",
        "\n",
        "### 1. Nhóm có Persona: Chu trình Nhận thức Định hướng & Tự chủ (Goal-Directed Cognitive Flow)\n",
        "- **Tìm kiếm (`Search Query`) và Điều hướng (`Navigate`) chiếm tỷ trọng rất lớn ở các pha đầu:**\n",
        "  - Ngay tại $Q_1$, hành vi tìm kiếm chủ đề bùng nổ lên tới **$27.9\\%$** và điều hướng đạt **$10.5\\%$** (tổng cộng chiếm gần **$40\\%$** thời lượng ban đầu). Đây là giai đoạn Persona chủ động \"săn tìm và nạp nguồn nội dung quan tâm\" vào Working Memory.\n",
        "  - Khi đã nạp đủ luồng bài viết ưng ý, nhu cầu tìm kiếm giảm dần sang $Q_2$ ($14.9\\%$), $Q_3$ ($12.6\\%$) và **chấm dứt hoàn toàn ở $Q_4$ ($0.0\\%$)**.\n",
        "- **Đọc sâu (`Deep Read`) và Tương tác xã hội (`React / Social`) chuyển dịch nhịp nhàng:**\n",
        "  - Hành vi đọc sâu đạt đỉnh ở $Q_2$ (**$13.8\\%$**) ngay sau khi tìm kiếm thành công ở $Q_1$.\n",
        "  - Tương tác xã hội (thả react, like, share) tăng lũy tiến từ $Q_1$ ($9.3\\%$) vọt lên $Q_3$ (**$14.9\\%$**) và $Q_4$ (**$14.6\\%$) — phản ánh quy luật nhận thức tự nhiên: tương tác cảm xúc bộc lộ mạnh nhất sau khi nội dung đã được đọc và thẩm thấu.\n",
        "- **Tự chủ Thoát phiên (`End Session`):**\n",
        "  - Tỷ trọng gọi lệnh kết thúc vọt lên **$22.5\\%$ ở $Q_4$**, chứng minh Agent nhận thức rõ thời lượng phiên và chủ động dừng lại khi đã đạt mục tiêu.\n",
        "\n",
        "### 2. Nhóm Không Persona: Quan sát Thụ động & Buông xuôi Bế tắc (Passive Observation & Idling)\n",
        "- **Quan sát màn hình (`Observe Viewport`) chiếm tỷ trọng rất cao trong suốt cả 4 pha:**\n",
        "  - Duy trì áp đảo từ **$33.3\\%$ ($Q_1$) $\\rightarrow 40.9\\%$ ($Q_2$) $\\rightarrow 45.5\\%$ ($Q_3$) $\\rightarrow 39.1\\%$ ($Q_4$)**. Gần một nửa thời lượng No-Persona chỉ \"đứng nhìn\" màn hình một cách thụ động vì hoàn toàn không có profile mục tiêu để dẫn dắt hành động.\n",
        "  - Hành vi tìm kiếm rất yếu ở đầu phiên ($14.3\\%$) và tắt hẳn ở nửa sau ($0.0\\%$).\n",
        "- **Pha 4 xuất hiện tới $\\approx 9\\%$ ($8.7\\%$) hành vi Nghỉ ngơi (`Rest`):**\n",
        "  - Khác biệt hoàn toàn với nhịp nghỉ tái tạo năng lượng định kỳ của Persona, hành vi `rest` của No-Persona ở cuối phiên đơn giản là **\"nghỉ không làm gì để đợi rời phiên — nghĩa là chán chường, buông xuôi, chả muốn làm gì nữa chỉ đợi hết giờ\"** sau khi bị kẹt giao diện và lỗi thao tác liên tiếp.\n",
        "  - Tương tác xã hội gần như triệt tiêu ($4.8\\%$ ở $Q_1$, $0.0\\%$ ở $Q_3$). Lệnh kết thúc ở $Q_4$ ($13.0\\%$) thực chất là sự ngắt cưỡng chế của hệ thống sau chuỗi lỗi đóng modal (`close_detail` lỗi 6 lần liên tiếp).\n"
    ]
}

# 3. Tạo Code Cell cho Mục 5.1
code_step5 = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 5.1. Đối soát Phân bố Hành vi theo Tiến trình Thời gian (Persona vs No-Persona)\n",
        "from IPython.display import Image, display\n",
        "\n",
        "# 1. Đọc bảng phân bố hành vi qua 4 giai đoạn\n",
        "ct_p = pd.read_csv(project_root / \"output\" / \"tables\" / \"step5_behavior_crosstab_persona.csv\", index_col=0)\n",
        "ct_np = pd.read_csv(project_root / \"output\" / \"tables\" / \"step5_behavior_crosstab_nopersona.csv\", index_col=0)\n",
        "\n",
        "print(\"=== 1. TỶ TRỌNG PHÂN BỐ HÀNH VI (%) THEO 4 GIAI ĐOẠN - NHÓM CÓ PERSONA ===\")\n",
        "display(ct_p.style.format(\"{:.1f}%\").background_gradient(cmap=\"Blues\", axis=1))\n",
        "\n",
        "print(\"\\n=== 2. TỶ TRỌNG PHÂN BỐ HÀNH VI (%) THEO 4 GIAI ĐOẠN - NHÓM KHÔNG CÓ PERSONA ===\")\n",
        "display(ct_np.style.format(\"{:.1f}%\").background_gradient(cmap=\"Reds\", axis=1))\n",
        "\n",
        "# 3. Hiển thị biểu đồ trực quan hóa đối sánh động lực học hành vi theo thời gian\n",
        "fig_beh_path = project_root / \"output\" / \"figures\" / \"step5_temporal_behavior_distribution.png\"\n",
        "display(Image(filename=str(fig_beh_path)))\n"
    ]
}

# Thêm vào cuối notebook
nb["cells"].append(md_step5)
nb["cells"].append(code_step5)

print(f"Final total cells: {len(nb['cells'])}")

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Successfully moved Behavior Distribution to Section 5 at the end of the notebook!")
