import sys
import json
import shutil
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

# 1. Cập nhật bảng step5_prominent_trigram_patterns.csv: Bỏ cột JSD
csv_path = Path("output/tables/step5_prominent_trigram_patterns.csv")
if csv_path.exists():
    df_pat = pd.read_csv(csv_path)
    if "Đóng góp JSD (bit)" in df_pat.columns:
        df_pat = df_pat.drop(columns=["Đóng góp JSD (bit)"])
    if "Lift_P_vs_NP" in df_pat.columns:
        df_pat = df_pat.drop(columns=["Lift_P_vs_NP"])
    df_pat.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"1. Cập nhật bảng {csv_path.name} thành công. Cột còn lại: {list(df_pat.columns)}")

# 2. Backup notebook
nb_path = Path("notebooks/eda_action_logs.ipynb")
backup_path = Path("notebooks/eda_action_logs.ipynb.bak7")
shutil.copy2(nb_path, backup_path)
print(f"2. Đã tạo bản sao lưu tại {backup_path.name}")

# 3. Đọc notebook
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Cell 36 [Markdown]: Thay thế nội dung giải thích đơn giản bằng Log-Odds Ratio
new_markdown_cell_36 = [
    "## 5.2. Động lực học Chuỗi Chuyển tiếp Hành vi & Phân kỳ Log-Odds Ratio (Behavioral Sequence Dynamics & Log-Odds Ratio Analysis)\n",
    "\n",
    "Để vượt qua giới hạn của việc phân tích tần suất hành vi độc lập, chúng tôi trích xuất toàn bộ các chuỗi chuyển tiếp hành động bậc cao ($n$-grams) trong từng phiên:\n",
    "- **Chuỗi Chuyển tiếp Nhị phân (Bigrams: $A_t \\rightarrow A_{t+1}$):** Đo lường quán tính chuyển giao hành động kế tiếp.\n",
    "- **Chuỗi Chu trình Tam phân (Trigrams: $A_t \\rightarrow A_{t+1} \\rightarrow A_{t+2}$):** Bộc lộ các chu trình nhận thức hoàn chỉnh (khám phá, thẩm thấu, tương tác, hoặc bế tắc giao diện).\n",
    "\n",
    "### 1. Phương pháp Thống kê: Đo lường Phân kỳ Bằng Hệ số Log-Odds Ratio (LOR)\n",
    "Tương đồng với kỹ thuật phân tích phân hóa từ vựng tư duy (CoT) ở Mục 4.4, chúng tôi áp dụng **Log-Odds Ratio (Hệ số Log-tỷ số khả dĩ)** để định lượng mức độ phân hóa của từng chuỗi hành vi giữa hai nhóm thực nghiệm:\n",
    "$$\\text{LOR}(s) = \\ln\\left(\\frac{P(s \\mid \\text{Persona}) + \\epsilon}{P(s \\mid \\text{No-Persona}) + \\epsilon}\\right)$$\n",
    "\n",
    "*Trong đó:* $P(s \\mid \\text{Persona})$ và $P(s \\mid \\text{No-Persona})$ là xác suất xuất hiện tương đối của chuỗi $s$ trong từng nhóm; $\\epsilon = 10^{-5}$ là hệ số làm mịn Laplace để xử lý các chuỗi có tần suất bằng 0.\n",
    "\n",
    "**Quy tắc diễn giải trực quan:**\n",
    "- **$\\text{LOR}(s) > 0$ (Hệ số dương):** Chuỗi hành vi đặc trưng **áp đảo ở nhóm Có Persona**. Độ lớn của $\\text{LOR}$ phản ánh cấp số nhân ưu thế (ví dụ: $\\text{LOR} = +2.44 \\implies$ xuất hiện gấp $e^{2.44} \\approx 11.5$ lần so với No-Persona).\n",
    "- **$\\text{LOR}(s) < 0$ (Hệ số âm):** Chuỗi hành vi đặc trưng **áp đảo ở nhóm Không Có Persona** (No-Persona). Giá trị càng âm sâu thể hiện hành vi bất thường hoặc bế tắc của nhóm đối chứng.\n",
    "\n",
    "### 2. Hai Mô hình Động lực học Nhận thức Đối lập\n",
    "1. **Nhóm Có Persona: Chu trình Dòng chảy Tự chủ (Goal-Directed Flow Loops - $\\text{LOR} > 0$):**\n",
    "   * **Tương tác Xã hội theo Cụm:** $\\text{React} \\rightarrow \\text{Observe} \\rightarrow \\text{React}$ ($6.23\\%$ vs $0.00\\%$, $\\mathbf{\\text{LOR} = +2.44}$) — Tương tác bùng nổ liên tiếp khi gặp chuỗi bài viết đúng sở thích.\n",
    "   * **Dòng chảy Lướt Tự nhiên (Flow Loop):** $\\text{Scroll} \\rightarrow \\text{Scroll} \\rightarrow \\text{Scroll}$ ($3.86\\%$ vs $0.00\\%$, $\\mathbf{\\text{LOR} = +1.95}$) — Hành vi lướt mượt mà, chủ động duyệt nội dung như người thật.\n",
    "   * **Tìm kiếm Chủ động Đa tầng:** $\\text{Scroll} \\rightarrow \\text{Search} \\rightarrow \\text{Search}$ ($2.08\\%$ vs $0.00\\%$, $\\mathbf{\\text{LOR} = +1.34}$) và $\\text{Search} \\rightarrow \\text{Search} \\rightarrow \\text{Read}$ ($1.48\\%$ vs $0.00\\%$, $\\mathbf{\\text{LOR} = +1.03}$) — Khi nguồn cấp dữ liệu bão hòa, Agent tự đổi từ khóa để tìm kiếm đúng chủ đề trong profile.\n",
    "   * **Chu trình Tiêu thụ Hoàn chỉnh:** $\\text{Scroll Feed} \\rightarrow \\text{Deep Read} \\rightarrow \\text{React/Social}$ ($1.48\\%$ vs $0.00\\%$, $\\mathbf{\\text{LOR} = +1.03}$) — Chu trình kinh điển: Lướt bắt gặp bài $\\rightarrow$ Đọc kỹ nội dung $\\rightarrow$ Bày tỏ cảm xúc.\n",
    "\n",
    "2. **Nhóm Không Persona: Hội chứng \"The Modal Trap\" & Vòng lặp Bế tắc ($\\text{LOR} < 0$):**\n",
    "   * **Vòng lặp Kẹt Modal Áp đảo:** $\\text{Observe} \\rightarrow \\text{Deep Read} \\rightarrow \\text{Observe}$ chiếm tới **$14.29\\%$** tổng số trigram của No-Persona (so với chỉ $0.30\\%$ ở Persona, $\\mathbf{\\text{LOR} = -3.66}$). Tần suất xuất hiện ở No-Persona cao gấp gần **$50$ lần** so với Persona.\n",
    "   * **Trở ngại Thoát giao diện Chi tiết:** $\\text{Deep Read} \\rightarrow \\text{Observe} \\rightarrow \\text{Navigate}$ ($4.76\\%$, $\\mathbf{\\text{LOR} = -3.63}$) và $\\text{Deep Read} \\rightarrow \\text{Observe} \\rightarrow \\text{Other}$ ($2.38\\%$, $\\mathbf{\\text{LOR} = -3.02}$) — Sau khi mở xem bài viết, Agent không biết cách đóng modal, loay hoay quan sát và gọi lệnh điều hướng vô hiệu.\n",
    "   * **Đứng nhìn Thụ động & Thao tác Thừa:** $\\text{Observe} \\rightarrow \\text{Other} \\rightarrow \\text{Observe}$ ($4.76\\%$, $\\mathbf{\\text{LOR} = -3.63}$) — Hoàn toàn mất định hướng hành vi vì không có profile dẫn dắt."
]

nb["cells"][36]["source"] = new_markdown_cell_36

# Cell 37 [Code]: Cập nhật code hiển thị bảng và đồ thị Log-Odds Ratio
new_code_cell_37 = [
    "# 5.2. Đối soát Chuỗi Hành vi N-gram & Phân kỳ Log-Odds Ratio (LOR)\n",
    "from IPython.display import Image, display\n",
    "\n",
    "# 1. Đọc và hiển thị Bảng 10 Pattern Trigram Tinh gọn (Phân loại theo Log-Odds Ratio)\n",
    "df_patterns = pd.read_csv(project_root / \"output\" / \"tables\" / \"step5_prominent_trigram_patterns.csv\")\n",
    "\n",
    "print(\"=== BẢNG 10 CHUỖI HÀNH VI (TRIGRAMS) ĐẶC TRƯNG NỔI BẬT NHẤT GIỮA HAI NHÓM ===\")\n",
    "print(\"Phương pháp Thống kê: Log-Odds Ratio (LOR) | Dương: Nghiêng về Persona, Âm: Nghiêng về No-Persona\\n\")\n",
    "display(\n",
    "    df_patterns.style\n",
    "    .set_properties(subset=['Ý nghĩa Chu trình'], **{'font-weight': 'bold'})\n",
    "    .format({\n",
    "        'Tỷ trọng Persona (%)': '{:.2f}%',\n",
    "        'Tỷ trọng No-Persona (%)': '{:.2f}%',\n",
    "        'Log_Odds_Ratio': '{:+0.2f}'\n",
    "    })\n",
    "    .background_gradient(subset=['Log_Odds_Ratio'], cmap='coolwarm', vmin=-4.0, vmax=3.0)\n",
    "    .set_properties(**{'text-align': 'center'})\n",
    "    .set_properties(subset=['Ý nghĩa Chu trình'], **{'text-align': 'left'})\n",
    "    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])\n",
    ")\n",
    "\n",
    "# 2. Hiển thị đồ họa đối soát phân kỳ hành vi 2 panel (Log-Odds Ratio & Probability %)\n",
    "fig_patterns_path = project_root / \"output\" / \"figures\" / \"step5_prominent_behavioral_patterns.png\"\n",
    "display(Image(filename=str(fig_patterns_path)))\n"
]

nb["cells"][37]["source"] = new_code_cell_37

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("3. Đã ghi đè thành công nội dung Cell 36 và Cell 37 trong notebooks/eda_action_logs.ipynb!")
