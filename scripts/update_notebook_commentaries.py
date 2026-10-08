import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

notebook_path = Path("notebooks/notebook_action_logs.ipynb")
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# CELL 10: Nhận xét về Khung giờ hoạt động
cell_10_content = """---
### Nhận định về Khung giờ Hoạt động của các Nhân vật:

1. **Về độ đầy đủ của dữ liệu theo dõi:**
   - Dữ liệu hiện tại đã ghi nhận **95 lượt hoạt động** trên cả 6 nhân vật, mỗi người có từ 12 đến 22 lượt theo dõi.
   - Hai nhân vật trước đây còn ít dữ liệu là `vn_fb_001` và `vn_fb_002` nay đã được bổ sung đầy đủ (lần lượt đạt 22 và 15 lượt), giúp bức tranh thói quen sinh hoạt trở nên rõ ràng và đáng tin cậy hơn.

2. **Đặc điểm thói quen sinh hoạt của từng nhân vật:**
   Nhìn chung, các nhân vật đều có lịch vào mạng rải đều ở các thời điểm trong ngày, nhưng khi quan sát kỹ từng người thì nhịp sinh hoạt phản ánh khá sát với nghề nghiệp và lứa tuổi thực tế:

   - **`vn_fb_001` (Nữ 25–34 tuổi, nhân viên văn phòng, 22 lượt):**  
     Hoạt động đều đặn suốt cả ngày (Sáng 36.4%, Trưa/Chiều 31.8%, Tối 31.8%), hơi nhỉnh hơn vào đầu giờ sáng khi chuẩn bị vào ca làm việc để nắm bắt tin tức đầu ngày.

   - **`vn_fb_002` (Nữ 35–44 tuổi, nội trợ / kinh doanh online, 15 lượt):**  
     Chia đều thời gian cho cả 3 buổi sáng, trưa, tối (mỗi buổi đúng 33.3%). Điều này phản ánh tính chất công việc tự do và việc nhà linh hoạt, có thể tranh thủ mở ứng dụng vào bất kỳ lúc nào rảnh tay.

   - **`vn_fb_003` (Nam 18–24 tuổi, bảo vệ trực tại Đà Nẵng, 12 lượt):**  
     Tập trung chủ yếu vào hai khoảng thời gian: sáng sớm (41.7%) và buổi tối (50.0%), gần như không dùng vào ban ngày (chỉ 8.3%). Thói quen này rất khớp với lịch trực ban ngày, người dùng chỉ vào mạng lúc bắt đầu hoặc kết thúc ca trực.

   - **`vn_fb_004` (Nữ 18–24 tuổi, sinh viên Hà Nội, 16 lượt):**  
     Vào mạng rải rác các buổi nhưng buổi tối chiếm tỷ lệ cao nhất (37.5%). Ban ngày bận học tập nên thời gian giải trí dài dồn vào buổi tối để xem video.

   - **`vn_fb_005` (Nam 35–44 tuổi, thợ kỹ thuật Đà Nẵng, 17 lượt):**  
     Tập trung nhiều hơn vào giờ nghỉ trưa (35.3%) và buổi tối sau giờ làm việc (35.3%), buổi sáng ít hơn (29.4%).

   - **`vn_fb_006` (Nam 55–64 tuổi, lao động tự do Cần Thơ, 13 lượt):**  
     Dồn phần lớn thời gian vào buổi trưa/chiều (46.2%) và buổi tối (46.2%), sáng sớm rất ít khi mở mạng xã hội (chỉ 7.7%).
"""

# CELL 11: Dẫn nhập Section 3
cell_11_content = """---
## 3. KHÁM PHÁ CÁC ĐẶC TRƯNG HÀNH VI CỦA CÁC NHÂN VẬT (ACTION LOGS)

> **Mục tiêu quan sát:**  
> Đánh giá xem cách mỗi nhân vật sử dụng Facebook trong thực tế có phản ánh đúng tính cách, thói quen và sở thích đã thiết lập hay không, qua 4 góc nhìn chính:
>
> 1. **Quy mô mỗi lần vào mạng:** Thời lượng ngồi lướt, tổng số thao tác thực hiện và quãng đường cuộn trang.
> 2. **Nơi hoạt động & hành động chính:** Thích xem ở màn hình nào (Bảng tin, Video Reels, Hội nhóm, Xem chi tiết bài viết) và thường làm gì (xem, đọc, bình luận, tương tác).
> 3. **Cách thao tác tay:** Lướt nhanh dứt khoát hay cuộn chậm rãi từ tốn.
> 4. **Mối quan tâm & ghi nhớ nội dung:** Quan tâm những chủ đề nào, đọc sâu bài viết ra sao và có giữ được sở thích quen thuộc hay không.
"""

# CELL 13: Cấp độ 1 Macro Sessions
cell_13_content = """---
### Nhận định về Bức tranh Hoạt động ở Cấp độ Phiên:

1. **Thời lượng mỗi lần vào mạng:**
   - *Nhóm vào nhanh, xem gọn:* Người đi làm kỹ thuật (`vn_fb_005`) và người lao động tự do (`vn_fb_006`) thường chỉ vào mạng khoảng 10 đến 11 phút mỗi lần rồi thoát ra làm việc khác. Người làm việc tại nhà (`vn_fb_002`) vào khoảng 12 phút.
   - *Nhóm ngồi lướt lâu:* Nhóm người trẻ có nhu cầu giải trí cao (`vn_fb_004` - sinh viên xem Reels và `vn_fb_003` - bảo vệ đọc tin) ở lại lâu hơn đáng kể, trung bình từ 21 đến 23 phút mỗi lần với 92 đến 103 thao tác. Nhân viên văn phòng (`vn_fb_001`) duy trì thời lượng vừa phải khoảng 17 phút.

2. **Thói quen cuộn trang:**
   - *Nhóm cuộn trang nhiều:* Những người có thói quen lướt bảng tin để duyệt nhiều tin tức (`vn_fb_001`, `vn_fb_005`, `vn_fb_003`) cuộn từ 11,000 đến gần 16,000 px mỗi phiên.
   - *Nhóm ít cuộn trang:* Người chuyên xem video ngắn (`vn_fb_004`) chỉ cuộn khoảng 726 px, vì khi xem Reels thao tác chủ yếu là chuyển sang video tiếp theo thay vì cuộn dọc trên dòng tin.
"""

# CELL 15: Cấp độ 2 Surface & Intent
cell_15_content = """---
### Nhận định về Nơi Hoạt động và Hành động Chính:

1. **Màn hình hoạt động ưa thích của từng người:**
   - **Xem video ngắn (`Reels`):** `vn_fb_004` dành phần lớn thời gian (**87.4%**) trên màn hình Reels, rất ít khi ra bảng tin thông thường (chỉ 4.4%). Người làm kinh doanh/nội trợ (`vn_fb_002`) cũng dành 27.7% thời gian cho video ngắn.
   - **Sinh hoạt trong hội nhóm (`Group`):** `vn_fb_001` dành thời gian nhiều nhất cho các hội nhóm (**42.8%**). Người lao động lớn tuổi (`vn_fb_006`) cũng dành **23.4%** thời gian trong hội nhóm để theo dõi thông tin bất động sản Cần Thơ.
   - **Đọc sâu từng bài viết (`Detail`):** `vn_fb_003` (28.6%) và `vn_fb_005` (30.7%) thường xuyên bấm mở chi tiết bài viết trên bảng tin để đọc kỹ nội dung và xem phần bình luận.
   - **Lướt bảng tin chung (`Feed`):** `vn_fb_002` (52.7%) và `vn_fb_006` (54.0%) dành hơn một nửa thời gian để lướt bảng tin chính.

2. **Mức độ tương tác (bình luận, thả cảm xúc, chia sẻ):**
   - *Nhóm hay tương tác:* `vn_fb_005` (11.8%) và `vn_fb_002` (10.9%) có thói quen cởi mở, thường xuyên để lại bình luận và thả cảm xúc tương tác với các bài viết họ quan tâm.
   - *Nhóm xem thụ động:* `vn_fb_004` (chỉ 2.2%) chủ yếu xem video mà hầu như không bấm thích hay để lại bình luận.
"""

# CELL 17: Cấp độ 3 Kinematics
cell_17_content = """---
### Nhận định về Cách Thao tác Tay trên Trình duyệt:

1. **Nhóm lướt nhanh:**
   - `vn_fb_002` có hơn một nửa số lần cuộn là thao tác lướt nhanh (57.1%), tốc độ vuốt khoảng 3,700 px/giây với thời gian mỗi lần lướt ngắn (~230 mili-giây). Phong cách này thể hiện việc đảo mắt lướt tin rất nhanh.
   - `vn_fb_001` và `vn_fb_005` cũng duy trì tốc độ lướt khoảng 3,800 px/giây khi duyệt tin trên bảng tin.

2. **Nhóm cuộn chậm rãi, từ tốn:**
   - `vn_fb_003` và `vn_fb_006` hoàn toàn không có thao tác cuộn nhanh (0% Fast). Tốc độ cuộn duy trì ở mức vừa phải (~2,500 px/giây), giữ thao tác lâu hơn để đọc kỹ nội dung từng bài viết hoặc tin rao.
   - `vn_fb_004` hầu như không cuộn trang (chỉ 5 lần cuộn trong suốt các phiên) vì chỉ cần bấm xem và chuyển video tiếp theo.
"""

# CELL 19: Cấp độ 4 Dimensions & Working Memory
cell_19_content = """---
### Nhận định về Mối Quan tâm Nội dung và Khả năng Điều chỉnh:

1. **Mỗi nhân vật phản ánh đúng sở thích đời thực:**
   - `vn_fb_004`: Tập trung vào video ngắn và theo dõi bóng đá thể thao.
   - `vn_fb_003`: Tập trung vào ẩm thực Việt Nam, món ăn đường phố và phim ảnh.
   - `vn_fb_006`: Tập trung tìm kiếm và đọc các bài viết về nhà đất, bất động sản tại Cần Thơ.
   - `vn_fb_005`: Thường xuyên đọc các bài viết về đời sống, gia đình và tin tức xã hội.

2. **Khả năng tự điều chỉnh khi gặp nội dung mới:**
   - Khi lướt gặp các chủ đề lạ hấp dẫn, người dùng có thể bị cuốn theo đọc tiếp một vài bài liên quan. Sau đó, hệ thống nhận diện và chủ động điều hướng nhân vật quay trở lại các chủ đề quen thuộc ban đầu.
   - Người thích đọc bài dài (`vn_fb_001`, `vn_fb_005`, `vn_fb_006`) đọc trung bình từ 4.7 đến 5.5 bài mỗi lần vào mạng, trong khi người chỉ xem video (`vn_fb_004`) chỉ đọc lướt 1 bài mỗi phiên.
"""

# CELL 20: H3 Header
cell_20_content = """## 4. QUAN SÁT THÓI QUEN CỦA NHÂN VẬT QUA CÁC PHIÊN KHÁC NHAU

> **Mục tiêu thực tế:** Quan sát xem cùng một nhân vật khi vào mạng ở các phiên khác nhau thì có duy trì được **thói quen thao tác**, **màn hình hay dùng**, **tốc độ cuộn lướt** và **mối quan tâm nội dung** nhất quán hay không, hay mỗi lần vào lại đổi sang một kiểu sử dụng ngẫu nhiên khác.

Để có cái nhìn toàn diện và gần gũi, chúng ta theo dõi hành vi qua **4 góc nhìn chính**:
1. **Cấp phiên (Nhịp độ):** Số lượng thao tác mỗi phút và thời lượng phiên.
2. **Màn hình & Ý định:** Tỷ lệ thời gian ở từng màn hình và cách thức hành động.
3. **Thao tác tay:** Tốc độ cuộn lướt nhanh hay chậm.
4. **Mối quan tâm & Ghi nhớ:** Chủ đề bài viết và các trang/hội nhóm quen thuộc lặp lại.
"""

# CELL 22: H3 Multi-level
cell_22_content = """---
### Nhận định từ Bảng Tổng hợp Độ tương đồng qua các Phiên:

1. **Nhịp độ thao tác qua các phiên:**
   - *Nhóm giữ nhịp độ đều đặn:* `vn_fb_003` (đọc tin) và `vn_fb_004` (xem Reels) duy trì tốc độ thao tác rất ổn định qua các phiên (mức lệch chỉ khoảng 7.0% - 17.8%). Người xem video và người đọc tin thường có tốc độ quen thuộc khi lướt.
   - *Nhóm thay đổi nhịp độ:* `vn_fb_006` có mức lệch nhịp độ lớn hơn (41.0% - 153.8%) do ở phiên thứ 2 và 3 dành nhiều thời gian vào nhóm bất động sản để tìm kiếm và đọc kỹ các bài viết, thay vì chỉ lướt bảng tin như phiên đầu.

2. **Màn hình sử dụng quen thuộc:**
   - Các nhân vật có màn hình yêu thích rõ rệt đều giữ thói quen này rất tốt qua các phiên. Điển hình là `vn_fb_004` luôn gắn liền với video Reels, `vn_fb_002` luôn chia thời gian giữa bảng tin và Reels, còn `vn_fb_005` duy trì nhịp lướt tin rồi mở xem chi tiết bài đọc.

3. **Ghi nhớ và tương tác lặp lại với các Trang và Hội nhóm quen thuộc:**
   - Các nhân vật nhớ và quay lại đúng các trang họ đã quan tâm trước đó:
     * `vn_fb_001`: Tương tác lại với 2 trang về cờ vua (*Chess.com* và *Cờ Vua đam mê*).
     * `vn_fb_006`: Quay lại đúng trang và nhóm *Bất Động Sản Cần Thơ* để xem bài rao bán nhà đất.
"""

# CELL 26: H3 Tổng kết
cell_26_content = """---
### Nhận định Tổng hợp: Hành vi của các Nhân vật qua các Phiên có Giữ được Thói quen Riêng không?

1. **Nhân vật thể hiện thói quen thao tác nhất quán qua các phiên:**
   - Khi cùng một nhân vật được kích hoạt ở các phiên khác nhau, cách thức sử dụng Facebook có mức độ tương đồng cao, vượt trội so với khi so sánh giữa các nhân vật khác nhau.
   - Nổi bật nhất là trường hợp của `vn_fb_004` (chuyên xem video ngắn): ở các phiên, nhân vật này duy trì thói quen xem video đặc thù rất ổn định và hoàn toàn khác biệt với các nhân vật còn lại. Điều này cho thấy mỗi nhân vật đã hình thành phong cách sử dụng riêng, không bị trộn lẫn.

2. **Các thói quen sử dụng màn hình nổi bật:**
   - *Thói quen xem liên tục trên Reels:* Nhân vật `vn_fb_004` một khi đã chuyển sang Reels thì gần như chỉ tiếp tục xem video tiếp theo (chiếm gần trọn vẹn số bước trên Reels), đúng với thói quen lướt video ngắn thực tế.
   - *Thói quen đọc sâu từng bài rồi quay lại bảng tin:* Các nhân vật như `vn_fb_003` và `vn_fb_005` thường xuyên luân chuyển nhịp nhàng: lướt bảng tin $\to$ mở xem bài viết $\to$ đọc kỹ nội dung và xem bình luận $\to$ quay lại bảng tin để lướt tiếp.
   - *Thói quen sinh hoạt trong hội nhóm:* Nhân vật `vn_fb_006` dành nhiều thời gian để hoạt động trong nhóm bất động sản Cần Thơ, trong khi `vn_fb_001` dành thời gian nhiều nhất cho các hội nhóm công việc và sở thích.

3. **Vừa giữ thói quen cũ, vừa làm quen thêm thao tác mới:**
   - Các nhân vật giữ được phần lớn các thao tác cốt lõi quen thuộc qua các phiên (như cuộn, đọc, xem).
   - Đồng thời, ở các phiên sau, nhân vật có xu hướng mở rộng thêm một số thao tác mới tùy theo nội dung bắt gặp (như bắt đầu tìm kiếm từ khóa hoặc thử chia sẻ bài viết). Điều này cho thấy nhân vật có khả năng thích ứng linh hoạt theo tình huống thực tế.

4. **Dấu ấn chuỗi hành động quen thuộc:**
   - Các chuỗi hành động lặp lại phản ánh chân thực thói quen lướt mạng xã hội đời thực:
     * *Chuyển video liên tục (`next → next`)*: Thao tác quen thuộc trên Reels của `vn_fb_004`.
     * *Cuộn lướt dòng tin liên tiếp (`scroll → scroll`)*: Thao tác duyệt tin nhanh của `vn_fb_003`.
     * *Viết bình luận rồi nán lại quan sát (`comment → observe`)*: Xuất hiện nhiều ở `vn_fb_003` khi để lại ý kiến rồi xem phản hồi.
     * *Mở xem thêm bài dài (`read → expand`)*: Xuất hiện ở `vn_fb_005` khi bắt gặp bài viết dài hay.
     * *Tìm tin và đọc bài (`scroll → read → scroll`)*: Xuất hiện đều đặn ở `vn_fb_006` khi duyệt tìm bài rao nhà đất.
     * *Mở xem bình luận cộng đồng (`read → open_comments`)*: Xuất hiện ở `vn_fb_002` khi đọc bài xong thì mở xem mọi người bàn luận.

---

### Bảng Tổng hợp So sánh Hành vi qua các Phiên

| Khía cạnh quan sát | Chỉ số theo dõi | Mức độ ổn định cùng Nhân vật | So với khi khác Nhân vật | Nhận xét thực tế |
| :--- | :--- | :---: | :---: | :--- |
| **Nhịp độ mỗi phiên** | Tốc độ thao tác (bước/phút) | Ổn định ở thói quen cố định (lệch 7% - 18%); thay đổi khi đổi mục tiêu | Khác biệt theo thói quen | Nhóm xem video / đọc tin giữ nhịp đều; nhóm tra cứu hội nhóm thao tác chậm rãi hơn |
| **Màn hình sử dụng** | Tỷ lệ dùng các màn hình | **Tương đồng cao** | Khác biệt rõ rệt | Thể hiện rõ nhất ở người chuyên xem Reels và người hay vào hội nhóm |
| **Ý định thao tác** | Tỷ lệ các loại hành động | **Tương đồng cao** | Khác biệt rõ rệt | Giữ được thói quen thao tác tương tự qua các phiên |
| **Thao tác tay** | Tốc độ cuộn trang | Ổn định cao ở thói quen cố định (lệch 16% - 19%) | Phân hóa 2 nhóm rõ rệt | Nhóm lướt nhanh luôn giữ phong cách lướt nhanh; nhóm đọc chậm duy trì nhịp cuộn từ tốn |
| **Chủ đề quan tâm** | Nội dung bài viết chú ý | **Nhất quán cao** | Khác biệt rõ rệt | Các chủ đề quan tâm thể hiện rất nhất quán |
| **Ghi nhớ lặp lại** | Trang, Hội nhóm quen thuộc | 4 trang + 1 hội nhóm lặp lại | Không bị nhầm lẫn | Nhân vật nhớ và quay lại đúng trang/nhóm trước đó |

> **TỔNG KẾT:**  
> Dữ liệu cho thấy hành vi của các nhân vật qua các phiên duy trì được phong cách sử dụng Facebook riêng biệt, từ nhịp độ, cách cuộn trang, màn hình ưa thích cho đến nội dung bài viết và hội nhóm tương tác.
"""

def to_source_lines(text):
    lines = text.split("\n")
    return [line + "\n" for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])

nb["cells"][10]["source"] = to_source_lines(cell_10_content)
nb["cells"][11]["source"] = to_source_lines(cell_11_content)
nb["cells"][13]["source"] = to_source_lines(cell_13_content)
nb["cells"][15]["source"] = to_source_lines(cell_15_content)
nb["cells"][17]["source"] = to_source_lines(cell_17_content)
nb["cells"][19]["source"] = to_source_lines(cell_19_content)
nb["cells"][20]["source"] = to_source_lines(cell_20_content)
nb["cells"][22]["source"] = to_source_lines(cell_22_content)
nb["cells"][26]["source"] = to_source_lines(cell_26_content)

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✅ Đã cập nhật thành công các cell nhận xét trong notebook!")
