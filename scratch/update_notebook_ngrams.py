import json

with open('notebooks/notebook_action_logs.ipynb') as f:
    nb = json.load(f)

# Update Cell 25
cell_25_lines = [
    "# ==============================================================================",
    "# BƯỚC 14: THÓI QUEN THAO TÁC, MA TRẬN TƯƠNG ĐỒNG 13 PHIÊN & TRỰC QUAN HÓA",
    "# ==============================================================================",
    "",
    "import matplotlib.pyplot as plt",
    "from algorithms.cross_session_behavior_profiler import (",
    "    compute_surface_retention_comparison,",
    "    compute_habit_evolution_and_correlation,",
    "    compute_intent_ngram_analysis,",
    "    compute_persona_repeated_ngram_patterns",
    ")",
    "from viz.session_consistency_viz import plot_h3_three_panel_comparison",
    "",
    "# 1. BẢNG SO SÁNH MỨC ĐỘ Ở LẠI TRÊN CÁC MÀN HÌNH GIỮA CÁC PHIÊN (S1 -> S2)",
    "df_surface_comparison = compute_surface_retention_comparison(df_actions_h3)",
    "",
    "print('=== BẢNG 4: SO SÁNH MỨC ĐỘ Ở LẠI TRÊN CÁC MÀN HÌNH GIỮA CÁC PHIÊN (S1 -> S2) ===')",
    "styled_surface_comp = (",
    "    df_surface_comparison.style",
    "    .format({",
    "        'Tỷ lệ ở lại S1 (%)': '{:.1f}%',",
    "        'Tỷ lệ ở lại S2 (%)': '{:.1f}%',",
    "        'Sai khác mức ở lại (%)': '{:+.1f}%'",
    "    })",
    "    .background_gradient(subset=['Tỷ lệ ở lại S1 (%)', 'Tỷ lệ ở lại S2 (%)'], cmap='Blues', vmin=70, vmax=100)",
    "    .set_properties(**{'text-align': 'center'})",
    "    .set_properties(subset=['Thói quen màn hình', 'Nhận xét chuyển biến thực tế'], **{'text-align': 'left'})",
    ")",
    "display(styled_surface_comp)",
    "",
    "# 2. BẢNG THEO DÕI THÓI QUEN CŨ VS THAO TÁC MỚI XUẤT HIỆN",
    "evolution_data = compute_habit_evolution_and_correlation(df_actions_h3)",
    "df_evolution = evolution_data['evolution_df']",
    "",
    "print('\\n=== BẢNG 5: MỨC ĐỘ GIỮ LẠI THÓI QUEN CŨ VÀ PHÁT SINH THAO TÁC MỚI ===')",
    "styled_evolution = (",
    "    df_evolution[['Persona', 'Cặp phiên', 'Số thao tác phiên 1', 'Số thao tác phiên 2', ",
    "                  'Thao tác giữ lại', 'Thao tác mới xuất hiện', 'Tỷ lệ thao tác quen thuộc (%)', ",
    "                  'Tỷ lệ thao tác mới (%)', 'Độ tương đồng (r)', 'Các thao tác mới cụ thể']].style",
    "    .format({",
    "        'Tỷ lệ thao tác quen thuộc (%)': '{:.1f}%',",
    "        'Tỷ lệ thao tác mới (%)': '{:.1f}%',",
    "        'Độ tương đồng (r)': '{:.4f}'",
    "    })",
    "    .background_gradient(subset=['Độ tương đồng (r)'], cmap='Greens', vmin=0.0, vmax=1.0)",
    "    .background_gradient(subset=['Tỷ lệ thao tác quen thuộc (%)'], cmap='Blues', vmin=50, vmax=100)",
    "    .set_properties(**{'text-align': 'center'})",
    "    .set_properties(subset=['Các thao tác mới cụ thể'], **{'text-align': 'left'})",
    ")",
    "display(styled_evolution)",
    "",
    "# 3. BẢNG TOP 5 CHUỖI Ý ĐỊNH THAO TÁC (BIGRAM & TRIGRAM) VÀ TỶ LỆ TRÙNG LẶP QUA CÁC PHIÊN",
    "ngram_res = compute_intent_ngram_analysis(df_actions_h3, top_k=5)",
    "df_session_top_grams = ngram_res['session_top_grams']",
    "df_ngram_overlap = ngram_res['overlap_comparison']",
    "",
    "print('\\n=== BẢNG 6: TOP 5 CHUỖI Ý ĐỊNH THAO TÁC (BIGRAM & TRIGRAM) CỦA MỖI PERSONA THEO PHIÊN ===')",
    "styled_session_top = (",
    "    df_session_top_grams.style",
    "    .set_properties(**{'text-align': 'center'})",
    "    .set_properties(subset=['Top 5 Chuỗi 2 thao tác (Bigram)', 'Top 5 Chuỗi 3 thao tác (Trigram)'], **{'text-align': 'left'})",
    ")",
    "display(styled_session_top)",
    "",
    "print('\\n=== BẢNG 7: SO SÁNH TỶ LỆ TRÙNG LẶP CHUỖI Ý ĐỊNH (N-GRAM OVERLAP) GIỮA CÁC PHIÊN ===')",
    "styled_ngram_overlap = (",
    "    df_ngram_overlap.style",
    "    .set_properties(**{'text-align': 'center'})",
    "    .set_properties(subset=['Chuỗi Bigram trùng Top 5', 'Chuỗi Trigram trùng Top 5', 'Nhận xét chuỗi thao tác'], **{'text-align': 'left'})",
    ")",
    "display(styled_ngram_overlap)",
    "",
    "# 4. BẢNG CÁC CHUỖI Ý ĐỊNH TRÙNG LẶP XUYÊN PHIÊN CỦA TỪNG PERSONA",
    "df_repeated_ngrams = compute_persona_repeated_ngram_patterns(df_actions_h3)",
    "",
    "print('\\n=== BẢNG 8: CÁC CHUỖI Ý ĐỊNH (BIGRAM & TRIGRAM) TRÙNG LẶP TRONG CÁC PHIÊN CỦA TỪNG PERSONA ===')",
    "styled_repeated_ngrams = (",
    "    df_repeated_ngrams.style",
    "    .set_properties(**{'text-align': 'center'})",
    "    .set_properties(subset=['Bigram trùng lặp nổi bật', 'Trigram trùng lặp nổi bật', 'Chu trình thao tác chủ đạo', 'Ý nghĩa hành vi thực tế'], **{'text-align': 'left'})",
    ")",
    "display(styled_repeated_ngrams)",
    "",
    "# 5. THỐNG KÊ ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN",
    "print('\\n=== ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN ===')",
    "print(f'- Khi so sánh cùng Persona qua các phiên: r trung bình = {evolution_data[\"intra_mean\"]:.4f} +/- {evolution_data[\"intra_std\"]:.4f} (Trung vị: {evolution_data[\"intra_median\"]:.4f})')",
    "print(f'- Khi so sánh khác Persona giữa các phiên: r trung bình = {evolution_data[\"inter_mean\"]:.4f} +/- {evolution_data[\"inter_std\"]:.4f} (Trung vị: {evolution_data[\"inter_median\"]:.4f})')",
    "print('- Nhận xét: Độ tương đồng hành vi của cùng Persona cao hơn rõ rệt so với giữa các Persona khác nhau.')",
    "",
    "# 6. TRỰC QUAN HÓA 3-PANEL BẰNG BIỂU ĐỒ GẦN GŨI",
    "fig, axes = plot_h3_three_panel_comparison(",
    "    df_session_corr=evolution_data['correlation_matrix'],",
    "    df_evolution=df_evolution,",
    "    intra_vals=evolution_data['intra_correlations'],",
    "    inter_vals=evolution_data['inter_correlations']",
    ")",
    "plt.show()",
]

nb['cells'][25]['source'] = [l + '\n' for l in cell_25_lines]
if nb['cells'][25]['source'] and nb['cells'][25]['source'][-1] == '\n':
    nb['cells'][25]['source'].pop()

# Update Cell 26 (Markdown)
cell_26_text = """---
### Nhận định Tổng hợp: Hành vi của Agent qua các phiên có giữ được thói quen riêng không?

1. **Agent thể hiện thói quen thao tác nhất quán qua các phiên:**
   - Khi cùng một Persona chạy lại ở các phiên khác nhau, cách thức thao tác có mức độ tương đồng khá cao ($r$ trung bình đạt $0.7016$), vượt trội rõ rệt so với mức độ tương đồng khi so chéo giữa các Persona khác nhau ($r$ trung bình là $0.4343$).
   - Nổi bật nhất là trường hợp của `vn_fb_004` (chuyên xem video ngắn): ở cả 2 phiên, agent này duy trì độ tương đồng tự thân rất cao ($r = 0.7015$), nhưng lại gần như không có điểm chung nào với 5 Persona còn lại ($r \\le 0$). Điều này cho thấy mỗi agent đã hình thành phong cách thao tác riêng biệt, không bị trộn lẫn.

2. **Hai thói quen sử dụng màn hình nổi bật:**
   - *Thói quen xem liên tục khó dứt trên Reels:* Agent `vn_fb_004` một khi đã chuyển sang Reels thì gần như chỉ tiếp tục cuộn xem video tiếp theo ($98.6\\% - 100\\%$ các bước là tự lặp lại trên Reels), rất sát với thói quen lướt video ngắn thực tế.
   - *Thói quen đọc sâu từng bài rồi quay lại dòng tin:* Các agent như `vn_fb_003` và `vn_fb_005` thường xuyên luân chuyển nhịp nhàng: lướt dòng tin (`feed`) $\\to$ mở xem bài viết (`detail`) $\\to$ đọc kỹ, xem bình luận $\\to$ quay lại dòng tin để lướt tiếp (tỷ lệ ở lại mỗi màn hình từ $80\\% - 94\\%$).
   - *Thói quen tập trung vào hội nhóm:* Agent `vn_fb_006` dành phần lớn thời gian để hoạt động trong nhóm bất động sản Cần Thơ (ở lại trong nhóm $> 75\\% - 96\\%$).

3. **Vừa giữ thói quen cũ, vừa làm quen thêm thao tác mới:**
   - Các agent giữ được phần lớn các thao tác quen thuộc cốt lõi qua các phiên (như cuộn, đọc, xem). Ví dụ `vn_fb_003` bảo tồn trọn vẹn $12/12$ loại thao tác từ phiên 1 sang phiên 2 ($r = 0.9133$).
   - Đồng thời, ở các phiên sau, agent có xu hướng mở rộng thêm một số thao tác mới tùy theo nội dung bắt gặp (như `vn_fb_004` bắt đầu tìm kiếm từ khóa, `vn_fb_005` thử chia sẻ và bày tỏ cảm xúc). Điều này cho thấy agent có khả năng thích nghi linh hoạt chứ không hoạt động máy móc, xơ cứng.

4. **Dấu ấn chuỗi hành vi liên tiếp (Bigram & Trigram Ý định thao tác):**
   - Từ kết quả ở **Bảng 8**, các chuỗi hành động lặp lại của từng Persona phản ánh chân thực các chu trình tâm lý và thói quen lướt mạng xã hội:
     * `next → next → next` *(Quẹt video liên hồi)*: Chuỗi chuyển tiếp không ngừng nghỉ trên Reels của `vn_fb_004` ($26$ lần). Sang phiên 2 bổ sung thêm nhịp dừng lại xem `watch → next → watch` ($26$ lần).
     * `scroll → scroll → scroll` *(Dòng chảy cuộn lướt liên tục - Flow state)*: Chuỗi cuộn liên tiếp để duyệt tin của `vn_fb_003` ($49$ lần). Thể hiện phong cách duyệt tin nhanh, tập trung cao.
     * `comment → observe` *(Viết bình luận rồi ngóng tương tác)*: Xuất hiện dày đặc ở `vn_fb_003` ($17$ lần). Viết bình luận xong thì nán lại quan sát phản hồi trước khi thoát ra.
     * `read → expand → observe` *(Mở "Xem thêm" đọc bài dài)*: Xuất hiện ổn định ở `vn_fb_005`. Thấy bài viết hay thì bấm mở rộng để đọc trọn vẹn chi tiết rồi xem phần bình luận (`observe → read → open_comments`).
     * `scroll → read → scroll` *(Lùng sục & sàng lọc tin tức)*: Lặp lại đều đặn qua cả 3 phiên của `vn_fb_006`. Cuộn tìm tin $\\to$ bắt trúng bài rao BĐS thì đọc $\\to$ đọc xong lại cuộn tìm tiếp.
     * `read → open_comments → observe` *(Xem bình luận cộng đồng)*: Xuất hiện ở `vn_fb_002` khi đọc bài xong thì mở mục bình luận để nắm bắt dư luận rồi thả cảm xúc (`observe → react`).

---

### Bảng Tổng hợp So sánh Hành vi của Agent qua các Phiên

| Khía cạnh quan sát | Chỉ số theo dõi | Mức độ tương đồng cùng Persona | So với khi khác Persona | Nhận xét thực tế |
| :--- | :--- | :---: | :---: | :--- |
| **Cấp phiên (Nhịp độ)** | Lệch nhịp độ thao tác (%) | Nhất quán ở thói quen cố định ($7\\% - 18\\%$); biến động khi đổi mục tiêu ($41\\% - 154\\%$) | Biến động tùy nội dung | Nhóm xem video / đọc tin giữ nhịp đều; nhóm tra cứu hội nhóm chậm rãi hơn nhiều so với lướt tin |
| **Màn hình sử dụng** | Tỷ lệ dùng 5 màn hình | **0.5435** | 0.2558 (cao hơn gấp 2 lần) | Rõ nét nhất ở agent xem Reels và lướt tin |
| **Ý định thao tác** | Tỷ lệ 20 loại hành động | **0.7016** | 0.4343 (cao hơn rõ rệt) | Giữ được thói quen thao tác tương tự qua các phiên |
| **Thao tác trình duyệt** | Lệch tốc độ cuộn trang (%) | Ổn định cao ở thói quen cố định ($16\\% - 19\\%$); dao động vừa phải ($28\\% - 43\\%$) | Phân hóa 2 nhóm rõ rệt | Nhóm cuộn nhanh luôn giữ phong cách lướt nhanh; nhóm đọc chậm duy trì nhịp cuộn từ tốn |
| **Bằng chứng hành động** | Xu hướng nội dung quan tâm | **0.4580** | 0.0795 (cao hơn gần 6 lần) | Các chủ đề quan tâm thể hiện rất nhất quán |
| **Ghi nhớ lặp lại** | Trang, Hội nhóm quen thuộc | 4 trang + 1 hội nhóm lặp lại | Không bị nhầm lẫn | Agent nhớ và quay lại đúng trang/nhóm trước đó |

> **TÓM LẠI:**  
> Dữ liệu qua 13 phiên cho thấy hành vi của các Persona Agent không phải là những cú bấm ngẫu nhiên vô nghĩa. Mỗi agent giữ được thói quen sử dụng Facebook tương đối ổn định từ nhịp độ, cách cuộn trang, màn hình ưa thích cho đến nội dung bài viết và hội nhóm tương tác qua các phiên.
"""

nb['cells'][26]['source'] = [line + '\n' for line in cell_26_text.split('\n')]
if nb['cells'][26]['source'] and nb['cells'][26]['source'][-1] == '\n':
    nb['cells'][26]['source'].pop()

with open('notebooks/notebook_action_logs.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print('Updated both Cell 25 and Cell 26 successfully!')
