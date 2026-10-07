import nbformat

nb_path = 'notebooks/notebook_action_logs.ipynb'
nb = nbformat.read(nb_path, as_version=4)

# ==============================================================================
# CELL 21: CẬP NHẬT STYLER BẢNG 1 VỚI CỘT %
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
        'Cấp phiên: Lệch nhịp độ (%)': '{:.1f}%',
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
# CELL 22: NHẬN ĐỊNH BẢNG 1 - NÓI RÕ CÓ AGENT NHẤT QUÁN, CÓ AGENT KHÔNG VÀ NGUYÊN DO
# ==============================================================================
nb.cells[22].source = r"""---
### Nhận định từ Bảng Tổng hợp Độ tương đồng qua 4 Cấp độ:

1. **Cấp phiên (Nhịp độ thao tác chung):**
   - **Có agent duy trì nhịp độ rất nhất quán qua các phiên (mức lệch chỉ từ $7.0\% - 17.8\%$):**
     * Điển hình là `vn_fb_003` (chuyên đọc tin tức): nhịp độ thao tác giữa 2 phiên gần như tương đương ($6.46$ so với $6.91$ hành động/phút, mức lệch chỉ **$7.0\%$**). Thói quen lướt bảng tin và mở xem chi tiết bài đọc diễn ra rất đều đặn.
     * Tương tự, `vn_fb_004` (chuyên xem video Reels): nhịp độ duy trì ở mức chậm và ổn định ($3.48$ và $4.10$ hành động/phút, lệch **$17.8\%$**). Nguyên nhân là do agent này dành phần lớn thời gian để chờ xem hết từng video Reels trước khi chuyển tiếp, nên tốc độ bấm bị chi phối bởi độ dài video.
   - **Có agent lại có nhịp độ biến động khá nhiều giữa các phiên (mức lệch từ $41.0\%$ đến hơn $150\%$):**
     * Rõ nét nhất là `vn_fb_006`: ở Phiên 2 chỉ đạt $2.15$ hành động/phút, nhưng sang Phiên 3 lại tăng lên $5.47$ hành động/phút (mức chênh lệch lên tới **$153.8\%$**; giữa Phiên 1 và Phiên 2 cũng lệch **$41.0\%$**).
     * `vn_fb_002` cũng có sự thay đổi nhịp độ đáng kể (**$44.9\%$**, từ $5.48$ bước/phút ở Phiên 1 lên $7.95$ bước/phút ở Phiên 2).
   - **Nguyên do dẫn đến sự phân hóa này:**
     * Sự nhất quán hay biến động về nhịp độ chủ yếu phụ thuộc vào **mục tiêu và tính chất nội dung tiếp cận trong từng phiên**.
     * Khi agent thực hiện các tác vụ đòi hỏi tìm hiểu sâu (như `vn_fb_006` vào hội nhóm BĐS Cần Thơ đọc kỹ từng bài đăng mua bán đất, so sánh giá), thời gian dừng lại đọc và quan sát lâu khiến số hành động trên mỗi phút giảm xuống rõ rệt. Ngược lại, khi chuyển sang lướt bảng tin chung (`feed`) đọc nhiều tin tức ngắn liên tục (`vn_fb_002` hoặc `vn_fb_006` ở Phiên 3), số lượt bấm và cuộn tăng cao khiến nhịp độ đẩy lên nhanh hơn.

2. **Không gian Bề mặt & Ý định thao tác:**
   - **Màn hình sử dụng (Bề mặt):** Mức độ tương đồng của cùng một Persona qua các phiên đạt trung bình khoảng $0.5435$, cao hơn đáng kể so với khi so chéo giữa các Persona khác nhau (mức trung bình so chéo là $0.2558$, gấp hơn 2 lần). Các agent như `vn_fb_002` ($r = 0.9900$) và `vn_fb_004` ($r = 0.9786$) thường chỉ tập trung vào một vài màn hình quen thuộc.
   - **Ý định thao tác:** Độ tương đồng về các kiểu hành động của cùng một Persona đạt trung bình khoảng $0.7027$ (cao hơn rõ rệt so với mức $0.4392$ của việc so chéo). Trong đó, `vn_fb_003` lặp lại gần như trọn vẹn bộ thói quen thao tác giữa hai phiên ($r = 0.9146$).

3. **Thao tác trình duyệt (Tốc độ cuộn trang):**
   - Phân hóa rõ rệt về thói quen cuộn chuột: nhóm cuộn nhanh (`vn_fb_002`, `vn_fb_005` thường cuộn lướt nhanh trên $4,000 - 5,300\text{ px/s}$) khác biệt so với nhóm cuộn chậm để đọc kỹ từng đoạn (`vn_fb_003`, `vn_fb_004` dưới $2,800\text{ px/s}$). Thói quen cuộn này duy trì tương đối ổn định qua các phiên ($r \approx 0.415$).

4. **Bằng chứng hành động & Ghi nhớ thực thể:**
   - Độ tương đồng về bằng chứng hành động nội tại đạt trung bình khoảng $0.4580$, cao hơn nhiều so với khi so giữa các agent khác nhau (chỉ khoảng $0.0795$). Các agent `vn_fb_001` ($r = 0.9968$), `vn_fb_004` ($r = 0.9397$), `vn_fb_006` ($r = 0.9933$) thể hiện các mối quan tâm rất nhất quán.
   - Đồng thời, ghi nhận một số trang fanpage và hội nhóm quen thuộc được agent chủ động tìm lại ở các phiên sau, cho thấy agent có xu hướng lưu giữ thông tin quan tâm qua các phiên."""

# ==============================================================================
# CELL 26: CẬP NHẬT BẢNG TỔNG HỢP VỚI CỘT NHỊP ĐỘ %
# ==============================================================================
nb.cells[26].source = r"""---
### Nhận định Tổng hợp: Hành vi của Agent qua các phiên có giữ được thói quen riêng không?

1. **Agent thể hiện thói quen thao tác nhất quán qua các phiên:**
   - Khi cùng một Persona chạy lại ở các phiên khác nhau, cách thức thao tác có mức độ tương đồng khá cao ($r$ trung bình đạt $0.7016$), vượt trội rõ rệt so với mức độ tương đồng khi so chéo giữa các Persona khác nhau ($r$ trung bình là $0.4343$).
   - Nổi bật nhất là trường hợp của `vn_fb_004` (chuyên xem video ngắn): ở cả 2 phiên, agent này duy trì độ tương đồng tự thân rất cao ($r = 0.7015$), nhưng lại gần như không có điểm chung nào với 5 Persona còn lại ($r \le 0$). Điều này cho thấy mỗi agent đã hình thành phong cách thao tác riêng biệt, không bị trộn lẫn.

2. **Hai thói quen sử dụng màn hình nổi bật:**
   - *Thói quen xem liên tục khó dứt trên Reels:* Agent `vn_fb_004` một khi đã chuyển sang Reels thì gần như chỉ tiếp tục cuộn xem video tiếp theo ($98.6\% - 100\%$ các bước là tự lặp lại trên Reels), rất sát với thói quen lướt video ngắn thực tế.
   - *Thói quen đọc sâu từng bài rồi quay lại dòng tin:* Các agent như `vn_fb_003` và `vn_fb_005` thường xuyên luân chuyển nhịp nhàng: lướt dòng tin (`feed`) $\to$ mở xem bài viết (`detail`) $\to$ đọc kỹ, xem bình luận $\to$ quay lại dòng tin để lướt tiếp (tỷ lệ ở lại mỗi màn hình từ $80\% - 94\%$).
   - *Thói quen tập trung vào hội nhóm:* Agent `vn_fb_006` dành phần lớn thời gian để hoạt động trong nhóm bất động sản Cần Thơ (ở lại trong nhóm $> 75\% - 96\%$).

3. **Vừa giữ thói quen cũ, vừa làm quen thêm thao tác mới:**
   - Các agent giữ được phần lớn các thao tác quen thuộc cốt lõi qua các phiên (như cuộn, đọc, xem). Ví dụ `vn_fb_003` bảo tồn trọn vẹn $12/12$ loại thao tác từ phiên 1 sang phiên 2 ($r = 0.9146$).
   - Đồng thời, ở các phiên sau, agent có xu hướng mở rộng thêm một số thao tác mới tùy theo nội dung bắt gặp (như `vn_fb_004` bắt đầu tìm kiếm từ khóa, `vn_fb_005` thử chia sẻ và bày tỏ cảm xúc). Điều này cho thấy agent có khả năng thích nghi linh hoạt chứ không hoạt động máy móc, xơ cứng.

---

### Bảng Tổng hợp So sánh Hành vi của Agent qua các Phiên

| Khía cạnh quan sát | Chỉ số theo dõi | Mức độ tương đồng cùng Persona | So với khi khác Persona | Nhận xét thực tế |
| :--- | :--- | :---: | :---: | :--- |
| **Cấp phiên (Nhịp độ)** | Lệch nhịp độ thao tác (%) | Nhất quán ở thói quen cố định ($7\% - 18\%$); biến động khi đổi mục tiêu ($41\% - 154\%$) | Biến động tùy nội dung | Nhóm xem video / đọc tin giữ nhịp đều; nhóm tra cứu hội nhóm chậm rãi hơn nhiều so với lướt tin |
| **Màn hình sử dụng** | Tỷ lệ dùng 5 màn hình | **0.5435** | 0.2558 (cao hơn gấp 2 lần) | Rõ nét nhất ở agent xem Reels và lướt tin |
| **Ý định thao tác** | Tỷ lệ 20 loại hành động | **0.7016** | 0.4343 (cao hơn rõ rệt) | Giữ được thói quen thao tác tương tự qua các phiên |
| **Thao tác trình duyệt** | Tốc độ cuộn chuột (px/s) | Có xu hướng tương đồng | Phân hóa 2 nhóm rõ rệt | Nhóm cuộn lướt nhanh vs Nhóm cuộn chậm đọc kỹ |
| **Bằng chứng hành động** | Xu hướng nội dung quan tâm | **0.4580** | 0.0795 (cao hơn gần 6 lần) | Các chủ đề quan tâm thể hiện rất nhất quán |
| **Ghi nhớ lặp lại** | Trang, Hội nhóm quen thuộc | 4 trang + 1 hội nhóm lặp lại | Không bị nhầm lẫn | Agent nhớ và quay lại đúng trang/nhóm trước đó |

> **TÓM LẠI:**  
> Dữ liệu qua 13 phiên cho thấy hành vi của các Persona Agent không phải là những cú bấm ngẫu nhiên vô nghĩa. Mỗi agent giữ được thói quen sử dụng Facebook tương đối ổn định từ nhịp độ, cách cuộn trang, màn hình ưa thích cho đến nội dung bài viết và hội nhóm tương tác qua các phiên."""

nbformat.write(nb, nb_path)
print("Updated Cell 21, 22, 26 with percentage pace difference and explanations successfully!")
