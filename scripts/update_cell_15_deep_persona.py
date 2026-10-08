import json

cell_15_content = """---
### Nhận định về Nơi Hoạt động và Hành động Chính:
*(Bóc tách chi tiết các trường trong Hồ sơ Persona và Hợp đồng Hành vi dẫn đến sự khác biệt)*

Sự phân hóa rõ nét giữa các nhân vật về không gian hoạt động (bề mặt giao diện) và hành vi thao tác không phải ngẫu nhiên, mà phản ánh trung thực các thiết lập hồ sơ đời sống và hợp đồng hành vi:

---

#### 1. Sự Khác biệt về Không gian Bề mặt (Nơi Hoạt động) và Căn nguyên Quy định:

##### a. Màn hình Video ngắn (`Reels`): Phân cực giữa người chuộng video ngắn và người đọc bài viết
- **Biểu hiện dữ liệu:**
  * `vn_fb_004` dành phần lớn hoạt động (**87.4%** bước thao tác) trên màn hình Reels.
  * `vn_fb_002` (27.7%) và `vn_fb_003` (23.4%) cũng dành khoảng một phần tư thời gian cho video ngắn.
  * Ngược lại, `vn_fb_001`, `vn_fb_005` và `vn_fb_006` hoàn toàn **không xuất hiện** trên Reels (0.0%).
- **Các trường Persona & Hợp đồng quyết định:**
  * **Trọng số bề mặt (`navigation.surfaceBias`):** Hợp đồng của `vn_fb_004` và `vn_fb_002` được cấu hình ưu tiên Reels tới 80% (`reels: 0.8, feed: 0, search: 0.2`).
  * **Tổng giờ xem video hàng tuần (`attributes`):** `vn_fb_004` và `vn_fb_002` đều ghi nhận mức tiêu thụ video giải trí rất lớn (**16–30 giờ/tuần**).
  * **Định dạng ưa thích (`taste.preferredFormats`):** `vn_fb_004`, `vn_fb_002` và `vn_fb_003` chọn `['video', 'reels']`. Trong khi đó, `vn_fb_005` và `vn_fb_006` chọn `['feed_post', 'link']` (bài viết thông thường và liên kết báo chí), khiến hai nhân vật này chỉ tập trung vào bảng tin bài viết.

##### b. Màn hình Hội nhóm (`Group`): Phản ánh vai trò nghề nghiệp và mức độ sinh hoạt cộng đồng
- **Biểu hiện dữ liệu:**
  * `vn_fb_001` dành tỷ trọng cao nhất hệ thống cho hội nhóm (**42.8%**).
  * `vn_fb_006` (15.5%) và `vn_fb_005` (10.4%) duy trì thời lượng vừa phải trong hội nhóm.
  * `vn_fb_002` và `vn_fb_004` hoàn toàn không vào nhóm (0.0%).
- **Các trường Persona & Hợp đồng quyết định:**
  * **Mức độ sinh hoạt hội nhóm (`attributes`):** `vn_fb_001` đăng ký mức *"Thường xuyên theo dõi và đọc bài"*. Với nghề thiết kế đồ họa/kiến trúc và vai trò *"Người sáng tạo nội dung"*, các hội nhóm chuyên môn là không gian trao đổi nghiệp vụ và tìm kiếm ý tưởng thiết kế.
  * **Nhu cầu tư vấn đời sống (`attributes`):** `vn_fb_006` và `vn_fb_005` đều ghi nhận mức *"Thỉnh thoảng đặt câu hỏi nhờ tư vấn"*. Thực tế cho thấy `vn_fb_006` vào các nhóm cộng đồng bất động sản Cần Thơ để theo dõi thị trường nhà đất.
  * **Vai trò nằm vùng (`attributes`):** `vn_fb_002` và `vn_fb_004` thuộc nhóm *"Chỉ nằm vùng hóng chuyện"* hoặc lướt video ngắn đơn thuần, không có nhu cầu tham gia vào các không gian cộng đồng khép kín.

##### c. Màn hình Đọc sâu từng bài viết (`Detail`): Thói quen đọc kỹ và nhu cầu tương tác
- **Biểu hiện dữ liệu:**
  * `vn_fb_005` (30.7%) và `vn_fb_003` (28.6%) có tỷ lệ mở chi tiết bài viết cao nhất hệ thống.
  * `vn_fb_001` (16.7%), `vn_fb_002` (16.3%) và `vn_fb_006` (13.6%) ở mức vừa phải.
  * `vn_fb_004` hầu như không mở chi tiết bài viết (chỉ 3.2%).
- **Các trường Persona & Hợp đồng quyết định:**
  * **Phong cách tương tác (`attributes`):** `vn_fb_003` là *"Chiến thần bình luận dạo (Tương tác tích cực các post)"*. Để đọc mạch tranh luận và viết bình luận, thao tác bắt buộc là phải bấm vào bài viết để mở màn hình chi tiết.
  * **Độ tập trung và tính chính xác (`attributes`):** `vn_fb_005` (thợ kỹ thuật cơ khí) có tính cách *"Thiên về độ chính xác"*, thích bài viết kỹ thuật và thích đọc bình luận chuyên sâu (`scroll_comments` chiếm tới 10.4%), đòi hỏi phải mở chi tiết bài viết.
  * **Lối xem lướt (`attributes`):** `vn_fb_004` mang bản sắc *"Tàu ngầm"*, chủ yếu xem lướt Reels chuyển tiếp liên tục nên rất ít khi mở trang chi tiết bài viết.

##### d. Tìm kiếm chủ động (`Search`): Sự phản biện và kiểm chứng thông tin
- **Biểu hiện dữ liệu:**
  * Xuất hiện rõ ở `vn_fb_005` (6.6%), `vn_fb_006` (5.3%) và `vn_fb_001` (3.7%).
- **Các trường Persona & Hợp đồng quyết định:**
  * **Thói quen đặt câu hỏi và đòi chứng cứ (`attributes`):** `vn_fb_006` có mức độ *"Rất hoài nghi / Luôn kiểm chứng nguồn tin"*, dẫn đến hành vi tìm kiếm chủ động để đối chiếu giá đất Cần Thơ và kiểm tra quảng cáo cấy ghép implant giá rẻ.
  * **Tính tò mò khám phá kiến thức:** `vn_fb_005` tìm kiếm các thông tin về hiện tượng thiên văn (quan sát Sao Hỏa, sự kiện tháng 10); `vn_fb_001` tìm hiểu công cụ AI mới phục vụ đồ họa kiến trúc.

---

#### 2. Sự Khác biệt về Hành động Thao tác và Mức độ Tương tác (AER):

##### a. Nhịp lướt video (`watch` & `next`):
- `vn_fb_004` dành tới **83.5%** tổng số thao tác cho chuỗi hành vi xem video (`watch`: 41.0%) và chuyển sang video kế tiếp (`next`: 42.5%), trong khi thao tác cuộn chuột truyền thống (`scroll`) chỉ chiếm 1.2%.
- Điều này phản ánh sự đồng bộ tuyệt đối với cấu hình tiêu thụ Reels của một thanh niên dịch vụ giải trí sau giờ làm việc.

##### b. Nhịp đọc kỹ và quan sát dữ kiện (`read` & `observe`):
- `vn_fb_006` có tổng tỷ lệ đọc và quan sát cao nhất hệ thống (**42.7%**, gồm `read`: 20.9% và `observe`: 21.8%).
- Căn nguyên bắt nguồn từ đặc trưng thế hệ Gen X (55–64 tuổi), phong cách giao tiếp *"Chỉ tập trung vào dữ kiện, không bao giờ dùng emoji"*, chú ý quan sát cẩn trọng trước khi đưa ra quyết định.

##### c. Tỷ lệ Tương tác Chủ động (AER: Thả cảm xúc, Viết bình luận, Chia sẻ):
- **Nhóm tương tác tích cực (`vn_fb_005`: 11.8%, `vn_fb_002`: 10.9%):**
  * `vn_fb_005`: Dẫn đầu với tỷ lệ bình luận đạt 5.7% và thả cảm xúc 5.7%. Bắt nguồn từ vai trò *"Người thích chia sẻ"*, tần suất bình luận và chia sẻ đều ở mức *"Hàng ngày"*, hợp đồng cho phép tỷ lệ tương tác xã hội cao (`reactionRate: 0.5`, `commentRate: 0.45`).
  * `vn_fb_002`: Tương tác chủ yếu bằng thả cảm xúc (**10.3%** `react`), phù hợp với phong cách dùng *"Rất nhiều emoji sinh động"* và thói quen *"Thường xuyên kết nối cộng đồng"*.
- **Nhóm tương tác chuyên biệt theo đúng vai trò (`vn_fb_003`: 5.7%, `vn_fb_001`: 7.4%):**
  * `vn_fb_003`: Dành tới **4.9%** thao tác để viết bình luận (cao nhì hệ thống, vượt trội so với mức thả cảm xúc 0.8%). Đúng với danh xưng *"Chiến thần bình luận dạo"*, khi gặp bài viết quan tâm thì tập trung vào việc gõ bình luận trao đổi.
  * `vn_fb_001`: Có tỷ lệ thao tác bài viết (`act_on_post`: 8.4%) cao nhất, phù hợp với vai trò người sáng tạo nội dung trong các nhóm.
- **Nhóm thụ động (`vn_fb_004`: chỉ 2.2%):**
  * Tỷ lệ tương tác thấp nhất hệ thống, hoàn toàn không có hành vi viết bình luận (0.0%). Thể hiện chính xác bản sắc *"Tàu ngầm (Chỉ xem và like, không post không cmt)"* khi chỉ lướt xem giải trí một chiều."""

with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

nb['cells'][15]['source'] = [line + '\n' for line in cell_15_content.split('\n')]
nb['cells'][15]['source'][-1] = nb['cells'][15]['source'][-1].rstrip('\n')

with open('notebooks/notebook_action_logs.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cell 15 updated successfully with deep persona field explanations!")
