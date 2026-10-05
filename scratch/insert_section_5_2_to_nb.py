import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("notebooks/eda_action_logs.ipynb")
backup_path = Path("notebooks/eda_action_logs.ipynb.bak6")

# Backup
shutil.copy2(nb_path, backup_path)
print(f"Backed up {nb_path} to {backup_path}")

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Markdown cell 5.2
md_5_2 = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 5.2. Động lực học Chuỗi Chuyển tiếp Hành vi & Phân kỳ Jensen-Shannon (Behavioral Sequence Dynamics & JSD)\n",
        "\n",
        "Để vượt qua giới hạn của việc phân tích tần suất hành vi độc lập, chúng tôi trích xuất toàn bộ các chuỗi chuyển tiếp hành động bậc cao ($n$-grams) trong từng phiên:\n",
        "- **Chuỗi Chuyển tiếp Nhị phân (Bigrams: $A_t \\rightarrow A_{t+1}$):** Đo lường quán tính chuyển giao hành động kế tiếp.\n",
        "- **Chuỗi Chu trình Tam phân (Trigrams: $A_t \\rightarrow A_{t+1} \\rightarrow A_{t+2}$):** Bộc lộ các chu trình nhận thức hoàn chỉnh (khám phá, thẩm thấu, tương tác, hoặc bế tắc giao diện).\n",
        "\n",
        "### 1. Phép đo Phân kỳ Jensen-Shannon (Jensen-Shannon Divergence - JSD)\n",
        "Khoảng cách phân phối chuỗi giữa nhóm **Có Persona ($P$)** và **Không Persona ($Q$)** được định lượng thông qua JSD trên cơ số 2:\n",
        "$$M = \\frac{1}{2}(P + Q)$$\n",
        "$$D_{\\text{JS}}(P \\parallel Q) = \\frac{1}{2} D_{\\text{KL}}(P \\parallel M) + \\frac{1}{2} D_{\\text{KL}}(Q \\parallel M) \\quad (D_{\\text{JS}} \\in [0, 1] \\text{ bit})$$\n",
        "\n",
        "* **Kiểm định Hoán vị Nhãn Thực nghiệm (Permutation Test - $N = 500$ lần):**\n",
        "  * **Bigrams:** $D_{\\text{JS}} = \\mathbf{0.4564}\\text{ bit}$ (Khoảng cách $\\sqrt{D_{\\text{JS}}} = \\mathbf{0.6756}$, $p = \\mathbf{0.0440} < 0.05$).\n",
        "  * **Trigrams:** $D_{\\text{JS}} = \\mathbf{0.7286}\\text{ bit}$ (Khoảng cách $\\sqrt{D_{\\text{JS}}} = \\mathbf{0.8536}$, $p = \\mathbf{0.0440} < 0.05$).\n",
        "  * **Ý nghĩa Thống kê:** Mức phân kỳ $0.729\\text{ bit}$ ở cấp độ Trigram khẳng định cấu trúc chuỗi 3 bước của hai nhóm thuộc về hai \"ngôn ngữ hành vi\" gần như phân tách hoàn toàn.\n",
        "\n",
        "### 2. Hai Mô hình Động lực học Nhận thức Đối lập\n",
        "1. **Nhóm Có Persona: Chu trình Dòng chảy Tự chủ (Goal-Directed Flow Loops):**\n",
        "   * **Chu trình Tiêu thụ Hoàn chỉnh:** $\\text{Scroll Feed} \\rightarrow \\text{Deep Read} \\rightarrow \\text{React/Social}$ ($1.48\\%$ vs $0.00\\%$, $\\text{Log-Odds} = +1.03$) — Khám phá bài viết, thẩm thấu nội dung rồi thả like/cảm xúc.\n",
        "   * **Chu trình Tìm kiếm Chủ động Đa tầng:** $\\text{Search Query} \\rightarrow \\text{Search Query} \\rightarrow \\text{Deep Read}$ ($1.48\\%$ vs $0.00\\%$, $\\text{Log-Odds} = +1.03$) và $\\text{Scroll} \\rightarrow \\text{Search} \\rightarrow \\text{Search}$ ($2.08\\%$ vs $0.00\\%$) — Chủ động gõ từ khóa mới khi Newsfeed bão hòa.\n",
        "   * **Chu trình Tương tác Xã hội theo Cụm:** $\\text{React} \\rightarrow \\text{Observe} \\rightarrow \\text{React}$ ($6.23\\%$ vs $0.00\\%$, $\\text{Log-Odds} = +2.44$).\n",
        "   * **Dòng chảy Lướt Tự nhiên:** $\\text{Scroll} \\rightarrow \\text{Scroll} \\rightarrow \\text{Scroll}$ ($3.86\\%$ vs $0.00\\%$, $\\text{Log-Odds} = +1.95$).\n",
        "\n",
        "2. **Nhóm Không Persona: Hội chứng \"The Modal Trap\" & Vòng lặp Bế tắc:**\n",
        "   * **Vòng lặp Kẹt Modal Áp đảo:** $\\text{Observe} \\rightarrow \\text{Deep Read} \\rightarrow \\text{Observe}$ chiếm tới **$14.29\\%$** tổng số trigram của No-Persona (so với chỉ $0.30\\%$ ở Persona, $\\text{Log-Odds} = \\mathbf{-3.66}$). Chuỗi này đóng góp tới **$0.0625\\text{ bit}$** vào tổng JSD (cao nhất toàn bộ không gian hành vi).\n",
        "   * **Trở ngại Thoát giao diện Chi tiết:** $\\text{Deep Read} \\rightarrow \\text{Observe} \\rightarrow \\text{Navigate}$ ($4.76\\%$, $\\text{Log-Odds} = -3.63$) và $\\text{Deep Read} \\rightarrow \\text{Observe} \\rightarrow \\text{Other}$ ($2.38\\%$, $\\text{Log-Odds} = -3.02$) — Đọc bài xong không biết cách đóng modal, loay hoay click lỗi trước khi buông xuôi."
    ]
}

# Code cell 5.2
code_5_2 = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 5.2. Đối soát Chuỗi Hành vi N-gram & Phân kỳ Jensen-Shannon (JSD)\n",
        "from IPython.display import Image, display\n",
        "\n",
        "# 1. Đọc và hiển thị Bảng 10 Pattern Trigram Tinh gọn Không Trùng lặp\n",
        "df_patterns = pd.read_csv(project_root / \"output\" / \"tables\" / \"step5_prominent_trigram_patterns.csv\")\n",
        "\n",
        "print(\"=== BẢNG 10 CHUỖI HÀNH VI (TRIGRAMS) ĐẶC TRƯNG NỔI BẬT NHẤT GIỮA HAI NHÓM ===\")\n",
        "print(\"Jensen-Shannon Divergence: JSD = 0.7286 bit | Khoảng cách JS = 0.8536 | Permutation p = 0.0440\\n\")\n",
        "display(\n",
        "    df_patterns.style\n",
        "    .set_properties(subset=['Ý nghĩa Chu trình'], **{'font-weight': 'bold'})\n",
        "    .format({\n",
        "        'Tỷ trọng Persona (%)': '{:.1f}%',\n",
        "        'Tỷ trọng No-Persona (%)': '{:.1f}%',\n",
        "        'Log_Odds_Ratio': '{:+0.2f}',\n",
        "        'Đóng góp JSD (bit)': '{:.4f}'\n",
        "    })\n",
        "    .set_properties(**{'text-align': 'center'})\n",
        "    .set_properties(subset=['Ý nghĩa Chu trình'], **{'text-align': 'left'})\n",
        "    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])\n",
        ")\n",
        "\n",
        "# 2. Hiển thị đồ họa đối soát phân kỳ hành vi 2 panel\n",
        "fig_patterns_path = project_root / \"output\" / \"figures\" / \"step5_prominent_behavioral_patterns.png\"\n",
        "display(Image(filename=str(fig_patterns_path)))\n"
    ]
}

# Append or replace if 5.2 already exists
existing_5_2_idx = None
for idx, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    if "## 5.2" in src:
        existing_5_2_idx = idx
        break

if existing_5_2_idx is not None:
    print(f"Replacing existing Section 5.2 starting at Cell {existing_5_2_idx}...")
    nb["cells"][existing_5_2_idx] = md_5_2
    if existing_5_2_idx + 1 < len(nb["cells"]) and nb["cells"][existing_5_2_idx + 1].get("cell_type") == "code":
        nb["cells"][existing_5_2_idx + 1] = code_5_2
    else:
        nb["cells"].insert(existing_5_2_idx + 1, code_5_2)
else:
    print("Appending Section 5.2 cells at the end of the notebook...")
    nb["cells"].append(md_5_2)
    nb["cells"].append(code_5_2)

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Notebook successfully updated! Total cells now: {len(nb['cells'])}")
