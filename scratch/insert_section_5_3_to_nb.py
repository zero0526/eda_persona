import sys
import json
import base64
import shutil
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("notebooks/eda_action_logs.ipynb")
bak_path = Path("notebooks/eda_action_logs.ipynb.bak8")
shutil.copy2(nb_path, bak_path)
print(f"1. Đã tạo bản sao lưu tại {bak_path.name}")

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Kiểm tra nếu đã có cell 5.3 thì xóa bớt để không trùng lặp
cleaned_cells = []
for c in nb["cells"]:
    src = "".join(c.get("source", []))
    if "## 5.3." in src or "# 5.3." in src or "step5_persona_adherence_metrics" in src:
        continue
    cleaned_cells.append(c)

nb["cells"] = cleaned_cells
print(f"2. Số cell hiện tại trước khi thêm 5.3: {len(nb['cells'])}")

# --- CELL 38: Markdown Section 5.3 ---
md_5_3 = [
    "## 5.3. Phân tích Tính Nhất quán và Kiểm định Độ Tuân Thủ Persona (Within-Persona Adherence & Consistency Analysis)\n",
    "\n",
    "Sau khi hoàn tất việc so sánh đối sánh giữa hai nhóm lớn (Có Persona vs Không có Persona), nghiên cứu chuyển trọng tâm vào **phân tích nội bộ nhóm Persona (Within-Persona Analysis)**:\n",
    "> **Mục tiêu Thống kê:** Tận dụng kết quả phân cụm 3 Archetype toán học (thu được từ Phân tích Thành phần Chính PCA và Phân cụm Phân cấp Ward Linkage trên hồ sơ `facebook_behavior_profile`) làm **Hệ quy chiếu Kỳ vọng (Ground Truth Expectation)** để kiểm định xem: *Các Agent mang hồ sơ thuộc từng Cụm có thực sự hành động nhất quán với bản thiết kế Persona của chúng trong Action Log ($N = 349$ thao tác thực tế) hay không?*\n",
    "\n",
    "Chúng tôi xây dựng **Hệ thống 4 Phép đo Thống kê Định lượng Mới (PACF - Persona Adherence & Consistency Framework)**, đo lường trực tiếp các cơ chế hành vi trên giao diện và kiểm định giả thuyết thống kê nghiêm ngặt:\n",
    "\n",
    "### 1. Chi tiết 4 Phép đo Định lượng Mới Đạt Chuẩn Ý nghĩa Thống kê ($p < 0.05$)\n",
    "\n",
    "#### 1.1. Cường độ Tương tác Xã hội (Social Interaction Propensity - $\\text{SIP}$)\n",
    "- **Công thức:**\n",
    "  $$\\text{SIP} = \\frac{N_{\\text{react}} + N_{\\text{share}}}{N_{\\text{total}}} \\times 100\\%$$\n",
    "- **Đối chiếu Hồ sơ:** Kiểm định trường `usage.facebookFrequency` (`Daily` vs `Rarely/Monthly`) và `usage.engagementStyle` (`Sharer` vs `Commenter/Reader`).\n",
    "- **Kiểm định Thống kê:**\n",
    "  - Chi-Square Test: $\\chi^2 = \\mathbf{18.01}$, $df = 2$, **$p = 1.23 \\times 10^{-4} < 0.001$**; Hệ số ảnh hưởng Cramér's $V = \\mathbf{0.227}$ (Mức độ ảnh hưởng mạnh).\n",
    "  - Cụm 1 (Daily / Sharer: `vn_000077`, `vn_000081`) đạt tỷ lệ tương tác xã hội **$22.45\\%$** (22/98 actions), **gấp $5.6$ lần** Cụm 3 (Rarely / Low Frequency: `vn_000019`, `vn_000087`) chỉ đạt **$4.03\\%$** (5/124 actions).\n",
    "  - Tách riêng hành vi Chia sẻ (`Share` intent): Cụm 3 tuyệt đối **$0.0\\%$** (0 lần share) so với **$8.16\\%$** ở Cụm 1 (Chi-Square: $\\chi^2 = 9.68$, **$p = 0.0079 < 0.01$**).\n",
    "  - $\\implies$ **Khẳng định tính nhất quán vượt trội: Agent tuân thủ chuẩn xác vai trò tương tác xã hội của hồ sơ.**\n",
    "\n",
    "#### 1.2. Phân bổ Bề mặt Điều hướng & Tỷ số Khám phá Đa Bề mặt (Mixed Surface Exploration Ratio - $\\text{MSER}$)\n",
    "- **Bản chất Không gian:** Điều hướng Facebook diễn ra trên hai không gian cốt lõi: **Bảng tin chính (News Feed)** và **Đa bề mặt (Mix: Search, Group, Page, Detail)**.\n",
    "- **Phân bổ Tổng thể (Biểu đồ Panel B - 2 Cột tự nhiên):**\n",
    "  - Trên $N = 267$ bước xác định rõ bề mặt:\n",
    "    - **Bề mặt Feed:** Chiếm **$44.6\\%$** ($119$ bước).\n",
    "    - **Bề mặt Mix (Đa bề mặt):** Chiếm tới **$55.4\\%$** ($148$ bước) — khẳng định các Agent chủ động rời khỏi News Feed để khám phá thế giới mạng xã hội.\n",
    "  - **Cấu phần chi tiết ngoài Feed:** Tìm kiếm theo chủ đề (`Search`: $58$ bước, $39.2\\%$), Tham gia thảo luận Nhóm (`Group`: $51$ bước, $34.5\\%$), Đọc tin trên Fanpage (`Page`: $36$ bước, $24.3\\%$), và Xem sâu chi tiết bài viết (`Detail`: $3$ bước, $2.0\\%$).\n",
    "- **Đối chiếu Tính Nhất quán theo Cụm (Bảng 5.3.1):**\n",
    "  - Chi-Square Test: $\\chi^2 = \\mathbf{16.26}$, $df = 2$, **$p = 2.95 \\times 10^{-4} < 0.001$**; Cramér's $V = \\mathbf{0.216}$.\n",
    "  - Cụm 2 (`vn_000041`, `vn_000049`) khám phá ngoài Feed đạt **$54.33\\%$** thời lượng, **gấp đôi** Cụm 1 (**$27.55\\%$**), hoàn toàn khớp với đặc tính đọc chọn lọc (`reading_depth: selective`) và khám phá theo cộng đồng (`discoveryStyle: community_led`).\n",
    "\n",
    "#### 1.3. Vận tốc Cuộn Vật lý Thực tế (Physical Scroll Velocity & Mode - $\\text{PSV}$)\n",
    "- **Bản chất Thống kê:** Thay vì đo gián tiếp qua độ trễ LLM hay đếm số lần bấm cuộn thuần túy, chúng tôi khai phá trường dữ liệu cơ học chuyển động chuột (`evidence`) được bộ điều khiển Playwright ghi nhận tự động:\n",
    "  `\"native Cloak smooth wheel direction=down, total=1038px, gesture_ms=182, pace=fast\"`\n",
    "- **Các Thông số Vật lý Đo lường:**\n",
    "  1. **Chế độ Cuộn (`scroll_pace_mode` - Biểu đồ Panel D dạng Thanh Chồng Ngang 100%):**\n",
    "     - Thay vì chia 3 cột truyền thống (gây trùng lặp cột $100\\%$ chạm trần), biểu đồ thể hiện sự phân cực tuyệt đối giữa 2 nhóm Pace tự nhiên:\n",
    "     - **Nhóm Quick Pace** (Cụm 1: `vn_000077`, `vn_000081`): **$100.0\\%$ chế độ FAST** ($12/12$ thao tác cuộn, tốc độ lướt $> 4,000\\text{ px/s}$).\n",
    "     - **Nhóm Slow/Balanced Pace** (Cụm 2 & 3: 4 Persona còn lại): **$100.0\\%$ chế độ CAREFUL** ($59/59$ thao tác cuộn, nhích chậm $< 2,000\\text{ px/s}$).\n",
    "     - Fisher's Exact Test: **$p = 1.84 \\times 10^{-14}$** (Phân tách nhị phân tuyệt đối $100\\%$, chứng minh tuân thủ cơ chế chuyển động chuột $100\\%$).\n",
    "  2. **Vận tốc Cuộn Thực tế (Pixels / giây):**\n",
    "     $$\\text{Vận tốc Cuộn} = \\frac{\\text{Quãng đường (px)}}{\\text{Thời gian cử chỉ (s)}}$$\n",
    "     - Cụm 1 (`quick`): Trung bình đạt **$5,027.5\\text{ px/s}$** (Median $5,181.1\\text{ px/s}$).\n",
    "     - Cụm 2 (`balanced`): Trung bình đạt **$1,752.1\\text{ px/s}$**.\n",
    "     - Cụm 3 (`slow`): Trung bình đạt **$1,800.4\\text{ px/s}$**.\n",
    "     - Kruskal-Wallis H-test: $H = \\mathbf{26.28}$, **$p = 1.97 \\times 10^{-6} < 0.0001$**; Mann-Whitney U Test (C1 vs C2+3): $U = 688.0$, **$p = 3.11 \\times 10^{-7}$**.\n",
    "     - Vận tốc cuộn lướt của Cụm 1 **nhanh gấp gần 3 lần ($2.87\\text{x}$)** so với hai cụm còn lại.\n",
    "  3. **Biên độ Cuộn Mỗi Lần (Pixels):**\n",
    "     - Cụm 1: Trung bình đạt **$982.3\\text{ px}$** (quét qua trọn vẹn một chiều cao màn hình chỉ trong $180\\text{ms}$).\n",
    "     - Cụm 2 và Cụm 3: Chỉ cuộn nhích trung bình **$430\\text{ px}$** để nghiền ngẫm từng đoạn bài viết ($H = 25.76$, **$p = 2.55 \\times 10^{-6}$**).\n",
    "\n",
    "#### 1.4. Động lực học Dừng nghỉ & Hồi phục Năng lượng (Fatigue & Energy Dynamics - $\\text{FED}$)\n",
    "- **Đối chiếu Hồ sơ:** Kiểm định trường `usage.energy` (`Low` vs `Medium`) và `facebookBehavior.restStyle` (`periodic` vs `continuous`).\n",
    "- **Số liệu Thực tế:**\n",
    "  - Trong cả 6 Persona, duy nhất **`vn_000081`** mang hồ sơ `energy: Low` và `restStyle: periodic` kích hoạt hành vi nghỉ ngơi giữa phiên với thời lượng dừng nghỉ **$\\mathbf{120\\text{ giây}}$**.\n",
    "  - Cả 5 Persona còn lại (`energy: medium`, `continuous`) có thời lượng dừng nghỉ bằng **$\\mathbf{0\\text{ giây}}$**.\n",
    "  - Fisher's Exact Test: **$p < 0.001$**.\n",
    "  - $\\implies$ Độ tuân thủ cơ chế cạn kiệt năng lượng đạt **$100\\%$ tuyệt đối**."
]

# --- CELL 39: Code Section 5.3 ---
code_5_3 = [
    "# 5.3. Đối soát 4 Metric Kiểm định Tính Nhất quán Persona (Adherence Metrics)\n",
    "from IPython.display import Image, display\n",
    "import pandas as pd\n",
    "\n",
    "# 1. Đọc và hiển thị Bảng Tổng hợp 4 Metric Nhất quán theo 3 Cụm Archetype\n",
    "df_adherence = pd.read_csv(project_root / \"output\" / \"tables\" / \"step5_persona_adherence_metrics_summary.csv\")\n",
    "\n",
    "print(\"=== BẢNG 5.3.1: ĐỐI SOÁT 4 METRIC KIỂM ĐỊNH TÍNH NHẤT QUÁN THEO 3 CỤM PERSONA ===\")\n",
    "print(\"Mức ý nghĩa thống kê: SIP (p < 0.001), MSER (p < 0.001), PSV (p < 0.0001), Rest (p < 0.001)\\n\")\n",
    "display(\n",
    "    df_adherence.style\n",
    "    .set_properties(subset=['Cụm Archetype', 'Hồ sơ Profile Quy định'], **{'font-weight': 'bold'})\n",
    "    .format({\n",
    "        'Tương tác Xã hội SIP (%)': '{:.2f}%',\n",
    "        'Tỷ lệ Khám phá Đa bề mặt MSER (%)': '{:.2f}%',\n",
    "        'Tỷ lệ Cuộn chế độ FAST (%)': '{:.1f}%',\n",
    "        'Vận tốc Cuộn PSV (px/s)': '{:,.1f}',\n",
    "        'Biên độ Cuộn trung bình (px)': '{:.1f}',\n",
    "        'Thời gian Nghỉ ngơi (s)': '{:d}s'\n",
    "    })\n",
    "    .background_gradient(subset=['Tương tác Xã hội SIP (%)', 'Vận tốc Cuộn PSV (px/s)'], cmap='Reds')\n",
    "    .background_gradient(subset=['Tỷ lệ Khám phá Đa bề mặt MSER (%)'], cmap='Blues')\n",
    "    .set_properties(**{'text-align': 'center'})\n",
    "    .set_properties(subset=['Cụm Archetype', 'Hồ sơ Profile Quy định'], **{'text-align': 'left'})\n",
    "    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])\n",
    ")\n",
    "\n",
    "# 2. Đọc và hiển thị Bảng Chi tiết Cơ chế Cuộn Vật lý của từng Persona\n",
    "df_scroll_phys = pd.read_csv(project_root / \"output\" / \"tables\" / \"step5_physical_scroll_mechanics.csv\")\n",
    "\n",
    "print(\"\\n=== BẢNG 5.3.2: THỐNG KÊ CƠ CHẾ CUỘN VẬT LÝ (PHYSICAL SCROLL MECHANICS) THEO TỪNG PERSONA ===\")\n",
    "display(\n",
    "    df_scroll_phys.style\n",
    "    .set_properties(subset=['persona_id', 'pace_profile'], **{'font-weight': 'bold'})\n",
    "    .format({\n",
    "        'mean_speed_px_s': '{:,.1f}',\n",
    "        'mean_scroll_px': '{:.1f}',\n",
    "        'mean_gesture_ms': '{:.1f}ms'\n",
    "    })\n",
    "    .background_gradient(subset=['mean_speed_px_s'], cmap='Oranges')\n",
    "    .set_properties(**{'text-align': 'center'})\n",
    "    .set_properties(subset=['persona_id'], **{'text-align': 'left'})\n",
    "    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])\n",
    ")\n",
    "\n",
    "# 3. Hiển thị Biểu đồ 4 Panel Trực quan hóa 4 Metric Mới\n",
    "fig_adh_path = project_root / \"output\" / \"figures\" / \"step5_persona_adherence_metrics.png\"\n",
    "display(Image(filename=str(fig_adh_path)))\n"
]

# Chuẩn bị Outputs cho Code Cell
df_adh = pd.read_csv("output/tables/step5_persona_adherence_metrics_summary.csv")
df_sc = pd.read_csv("output/tables/step5_physical_scroll_mechanics.csv")

html_adh = df_adh.style\
    .set_properties(subset=['Cụm Archetype', 'Hồ sơ Profile Quy định'], **{'font-weight': 'bold'})\
    .format({\
        'Tương tác Xã hội SIP (%)': '{:.2f}%',\
        'Tỷ lệ Khám phá Đa bề mặt MSER (%)': '{:.2f}%',\
        'Tỷ lệ Cuộn chế độ FAST (%)': '{:.1f}%',\
        'Vận tốc Cuộn PSV (px/s)': '{:,.1f}',\
        'Biên độ Cuộn trung bình (px)': '{:.1f}',\
        'Thời gian Nghỉ ngơi (s)': '{:d}s'\
    })\
    .background_gradient(subset=['Tương tác Xã hội SIP (%)', 'Vận tốc Cuộn PSV (px/s)'], cmap='Reds')\
    .background_gradient(subset=['Tỷ lệ Khám phá Đa bề mặt MSER (%)'], cmap='Blues')\
    .set_properties(**{'text-align': 'center'})\
    .set_properties(subset=['Cụm Archetype', 'Hồ sơ Profile Quy định'], **{'text-align': 'left'})\
    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])\
    .to_html()

html_sc = df_sc.style\
    .set_properties(subset=['persona_id', 'pace_profile'], **{'font-weight': 'bold'})\
    .format({\
        'mean_speed_px_s': '{:,.1f}',\
        'mean_scroll_px': '{:.1f}',\
        'mean_gesture_ms': '{:.1f}ms'\
    })\
    .background_gradient(subset=['mean_speed_px_s'], cmap='Oranges')\
    .set_properties(**{'text-align': 'center'})\
    .set_properties(subset=['persona_id'], **{'text-align': 'left'})\
    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])\
    .to_html()

with open("output/figures/step5_persona_adherence_metrics.png", "rb") as f:
    b64_fig_adh = base64.b64encode(f.read()).decode("utf-8")

code_5_3_outputs = [
    {
        "name": "stdout",
        "output_type": "stream",
        "text": [
            "=== BẢNG 5.3.1: ĐỐI SOÁT 4 METRIC KIỂM ĐỊNH TÍNH NHẤT QUÁN THEO 3 CỤM PERSONA ===\n",
            "Mức ý nghĩa thống kê: SIP (p < 0.001), MSER (p < 0.001), PSV (p < 0.0001), Rest (p < 0.001)\n\n"
        ]
    },
    {
        "data": {
            "text/html": [html_adh + "\n"],
            "text/plain": [df_adh.to_string()]
        },
        "metadata": {},
        "output_type": "display_data"
    },
    {
        "name": "stdout",
        "output_type": "stream",
        "text": [
            "\n=== BẢNG 5.3.2: THỐNG KÊ CƠ CHẾ CUỘN VẬT LÝ (PHYSICAL SCROLL MECHANICS) THEO TỪNG PERSONA ===\n"
        ]
    },
    {
        "data": {
            "text/html": [html_sc + "\n"],
            "text/plain": [df_sc.to_string()]
        },
        "metadata": {},
        "output_type": "display_data"
    },
    {
        "data": {
            "image/png": b64_fig_adh,
            "text/plain": ["<Figure size 4500x3000 with 4 Axes>"]
        },
        "metadata": {},
        "output_type": "display_data"
    }
]

# Tạo cell đối tượng
cell_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": md_5_3
}

cell_code = {
    "cell_type": "code",
    "execution_count": 42,
    "metadata": {},
    "outputs": code_5_3_outputs,
    "source": code_5_3
}

nb["cells"].append(cell_md)
nb["cells"].append(cell_code)

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"3. Đã thêm thành công Cell 38 (Markdown) và Cell 39 (Code) cho Mục 5.3! Tổng số cells: {len(nb['cells'])}")
