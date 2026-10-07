import json

with open('notebooks/notebook_action_logs.ipynb') as f:
    nb = json.load(f)

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
   - Không chỉ tương đồng về mặt phân phối hành vi tổng thể, agent còn lặp lại các chuỗi thao tác liên hoàn đặc trưng:
     * `vn_fb_003` duy trì chuỗi cuộn bài liên tục (`scroll → scroll → scroll`) và chuỗi bình luận xong quan sát (`comment → observe`); $100\\%$ các chuỗi Bigram Top 5 ở phiên 1 đều tái hiện ở phiên 2.
     * `vn_fb_004` duy trì chuỗi lướt video ngắn liên tiếp (`next → next → next`); sang phiên 2 bổ sung thêm nhịp xem video (`next → watch → next`) rất tự nhiên.
     * `vn_fb_006` có mức độ trùng lặp chuỗi thao tác rất cao giữa phiên 2 và phiên 3 (trùng $60\\%$ chuỗi Bigram Top 5, và $100\\%$ chuỗi quen thuộc phiên 2 đều tái hiện ở phiên 3).
   - Sự tái hiện các chuỗi 2 và 3 hành động này minh chứng cho tính tự nhiên và tính ổn định trong thói quen lướt mạng xã hội của các tác tử.

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

print('Updated Cell 26 clean!')
