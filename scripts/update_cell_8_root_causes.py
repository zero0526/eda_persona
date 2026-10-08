import json

cell_8_content = """---
### Nhận định từ Dữ liệu Khám phá về Lịch trình và Thời lượng Hoạt động:

#### 1. Bức tranh Tổng quan về Nhịp Vận hành Thực tế:
- **Về Khung giờ sinh hoạt trong ngày:**
  * Toàn bộ các phiên hoạt động phân bổ tự nhiên vào **4 khung giờ sinh hoạt quen thuộc**:
    + **Sáng sớm (khoảng 6h30 – 8h30):** Khởi động ngày mới, kiểm tra nhanh tin tức.
    + **Nghỉ trưa (khoảng 11h30 – 13h30):** Quãng nghỉ giữa ngày, giải lao ngắn.
    + **Buổi chiều (khoảng 15h00 – 17h30):** Thời điểm xế chiều hoặc quãng nghỉ giữa ca.
    + **Buổi tối (khoảng 19h30 – 22h30):** Khung giờ rảnh rỗi chính, mật độ phiên tập trung cao nhất.
- **Về Phân nhóm Thời lượng phiên:**
  * **Nhóm phiên dài và biên độ dao động rộng (`vn_fb_001`, `vn_fb_004`):** Thời lượng trung bình từ 21.2 đến 23.6 phút, dải thời lượng trải dài từ 10 đến 40 phút.
  * **Nhóm thời lượng vừa phải (`vn_fb_003`, `vn_fb_006`):** Thời lượng trung bình từ 13.7 đến 19.2 phút, dao động trong khoảng 8 đến 25 phút.
  * **Nhóm ổn định và kiểm soát chặt chẽ (`vn_fb_005`, `vn_fb_002`):** Thời lượng tập trung rất đều quanh mốc 13 – 19 phút, biên độ dao động nhỏ, không xuất hiện các phiên kéo dài bất thường.
- **Về Tần suất và Khoảng cách giữa các phiên (`gap_hours`):**
  * **Nhóm tần suất cao, khoảng cách ngắn (`vn_fb_001`, `vn_fb_005`, `vn_fb_004`):** Đạt 2.3 – 2.8 phiên/ngày; trung vị khoảng cách giữa các lần vào mạng chỉ từ 7.2 đến 8.0 giờ (thực tế giữa các ca trong ngày từ 5 đến 7 giờ).
  * **Nhóm tần suất thấp, khoảng cách dài (`vn_fb_002`, `vn_fb_003`, `vn_fb_006`):** Chỉ đạt 1.7 – 1.9 phiên/ngày; trung vị khoảng cách lên tới 11.5 đến 12.1 giờ do nhịp cách quãng qua đêm kéo dài.
  * **Lưu ý về các khoảng cách kỹ thuật (> 24 giờ):** Các giá trị từ 25 đến 55.5 giờ xuất hiện đơn lẻ ở mỗi nhân vật phản ánh các đợt ngắt quãng vận hành hệ thống giữa các đợt chạy thử nghiệm (như đợt ngày 05/10 – 06/10), không phải thói quen sinh hoạt liên tục.

---

#### 2. Đối chiếu Căn nguyên từ Hồ sơ Persona và Hợp đồng Hành vi:

Sự phân hóa rõ nét giữa các chỉ số thực tế bắt nguồn trực tiếp từ cấu hình nghề nghiệp, thói quen đời sống và hợp đồng hành vi của từng nhân vật:

##### a. Tại sao `vn_fb_001` và `vn_fb_004` có thời lượng phiên dài và dao động lớn nhất?
- **`vn_fb_004` (Thời lượng trung bình 23.6 phút, dải 10 – 35 phút):**
  * *Hồ sơ đời sống:* Là nhân viên nhà hàng (25–34 tuổi), có thói quen xem video/streaming rất nhiều trong tuần (16–30 giờ/tuần), chơi game hàng ngày và khả năng duy trì tập trung lâu dài.
  * *Hợp đồng hành vi:* Hợp đồng đặt ưu tiên Reels lên tới 80% (`reels: 0.8, feed: 0`), định dạng ưa thích là video và Reels.
  * *Cơ chế thực tế:* Buổi sáng trước giờ làm chỉ vào nhanh 10–18 phút; nhưng đến tối muộn sau giờ phục vụ nhà hàng (21h30–22h30), nhân vật dành 30–35 phút liên tục để xem Reels giải trí. Chính sự chênh lệch giữa phiên lướt nhanh ban ngày và phiên xem video kéo dài ban đêm khiến biên độ thời lượng mở rộng đáng kể.
- **`vn_fb_001` (Thời lượng trung bình 21.2 phút, dải 12 – 40 phút, độ lệch 9.4 phút):**
  * *Hồ sơ đời sống:* Làm thiết kế đồ họa (25–34 tuổi), vai trò "Người sáng tạo nội dung", thường xuyên đăng bài và có tính cách tò mò, thích khám phá nội dung thị giác.
  * *Hợp đồng hành vi:* Phân bổ bề mặt đa dạng (`reels: 0.55, feed: 0.25, search: 0.2`) kết hợp tỷ lệ bình luận (45%) và chia sẻ (35%) đều ở mức tích cực.
  * *Cơ chế thực tế:* Buổi sáng và trưa chỉ là các cữ ghé nhanh 12–15 phút trong quãng nghỉ giữa ca làm việc; đến tối sau giờ làm (19h30–21h00), nhân vật dành trọn 35–40 phút để vừa xem video, vừa theo dõi các hội nhóm và tương tác. Sự phân hóa giữa ca tranh thủ ban ngày và ca chuyên tâm ban tối tạo ra dải dao động rộng nhất hệ thống.

##### b. Tại sao `vn_fb_005` có thời lượng phiên ngắn và ổn định nhất hệ thống?
- **`vn_fb_005` (Thời lượng trung bình 13.1 phút, dải hẹp 10 – 18 phút, độ lệch chỉ 2.3 phút):**
  * *Hồ sơ đời sống:* Là thợ kỹ thuật sửa chữa/bảo dưỡng (35–44 tuổi), làm việc thực tế tại chỗ (on-site). Trạng thái năng lượng cuối ngày thường ở mức thấp, phong cách đưa ra quyết định rất nhanh và tính cách thiên về tính chính xác, thực tế.
  * *Hợp đồng hành vi:* Nhịp cuộn được cấu hình nhanh (`scrollCadence: 'quick'`), định dạng ưa thích là bài viết thông thường và liên kết (`feed_post`, `link`), không thiên lệch quá đà vào video cuốn hút (`feed: 0.4, reels: 0.4`).
  * *Cơ chế thực tế:* Người thợ vào mạng luôn có nhịp điệu dứt khoát: sáng uống cà phê (10–12 phút), trưa nghỉ giữa ca (10–12 phút), tối sau giờ làm việc chân tay chỉ lướt thư giãn vừa phải (12–18 phút) rồi nghỉ ngơi. Việc không bị cuốn vào chuỗi video liên tục giúp thời lượng của nhân vật này luôn ổn định quanh mốc 10–15 phút, hầu như không có biến động.

##### c. Tại sao `vn_fb_002` có thời lượng kiểm soát gọn gàng và tần suất thấp?
- **`vn_fb_002` (Thời lượng trung bình 19.2 phút, dải 10 – 25 phút, tần suất 1.67 phiên/ngày):**
  * *Hồ sơ đời sống:* Là lao động phổ thông (35–44 tuổi), đã có gia đình đông con (từ 3 con trở lên), mức độ duy trì nguyên tắc sống rất cao.
  * *Cơ chế thực tế:* Quỹ thời gian cá nhân bị chi phối chặt chẽ bởi công việc và chăm lo gia đình. Nhân vật chỉ tranh thủ vào mạng 1–2 lần mỗi ngày (thường vào giờ nghỉ trưa và buổi tối sau khi thu xếp việc nhà xong). Tính kỷ luật và thói quen sinh hoạt khiến mỗi phiên được giới hạn gọn gàng trong 15–25 phút, tạo ra khoảng cách nghỉ qua đêm kéo dài đến tận trưa hôm sau (khoảng cách 15–16 giờ), kéo trung vị khoảng cách lên mức 12.1 giờ.

##### d. Tại sao `vn_fb_003` vắng bóng giữa ngày và có khoảng cách phiên dài?
- **`vn_fb_003` (Tần suất 1.71 phiên/ngày, trung vị khoảng cách 11.5 giờ, 0% buổi chiều):**
  * *Hồ sơ đời sống:* Là nhân viên bảo vệ (18–24 tuổi), phong cách "Chiến thần bình luận dạo", trạng thái năng lượng ghi nhận mệt mỏi/căng thẳng do đặc thù công việc.
  * *Hợp đồng hành vi:* Tỷ lệ thả cảm xúc rất cao (`reactionRate: 0.8`) và bình luận tích cực (45%).
  * *Cơ chế thực tế:* Ca trực ban ngày nghiêm ngặt khiến nhân vật hầu như không thể vào mạng vào buổi trưa và chiều (0% ca chiều, chỉ 8.3% ca trưa). Hai cữ hoạt động dồn trọn vẹn vào sáng sớm trước khi vào ca (6h30–7h00) và tối muộn sau khi tan ca (20h00–21h30). Sự giãn cách giữa hai đầu ca trực tạo nên khoảng cách trung vị 11.5 giờ.

##### e. Tại sao `vn_fb_006` có thời lượng vừa phải và nhịp sinh hoạt chậm?
- **`vn_fb_006` (Thời lượng trung bình 13.7 phút, dải 8 – 22 phút, 7.7% buổi sáng):**
  * *Hồ sơ đời sống:* Thuộc thế hệ Gen X (55–64 tuổi), làm kinh doanh tự do, tính cách thận trọng, thói quen giao tiếp chỉ tập trung vào dữ kiện, không dùng biểu tượng cảm xúc, năng lượng trực tuyến ở mức thấp.
  * *Cơ chế thực tế:* Buổi sáng người lớn tuổi ưu tiên các công việc đời thường hơn là lướt mạng (chỉ chiếm 7.7% phiên). Hoạt động chủ yếu diễn ra vào buổi trưa (ghé nhanh 8–12 phút) và buổi tối (xem video tin tức 15–22 phút). Năng lượng thấp cuối ngày khiến nhân vật dừng phiên đúng lúc, không kéo dài quá 22 phút."""

with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Update cell 8
nb['cells'][8]['source'] = [line + '\n' for line in cell_8_content.split('\n')]
# Ensure last line doesn't have double newline
nb['cells'][8]['source'][-1] = nb['cells'][8]['source'][-1].rstrip('\n')

with open('notebooks/notebook_action_logs.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cell 8 updated successfully!")
