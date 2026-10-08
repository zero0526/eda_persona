import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

notebook_path = Path("notebooks/notebook_action_logs.ipynb")
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cell_10_content = """---
### Nhận định về Khung giờ Hoạt động của các Nhân vật:

1. **Đánh giá Tổng quan về Phân bổ Khung giờ (95 lượt hoạt động):**
   - Dữ liệu hiện tại đã ghi nhận đầy đủ **95 lượt hoạt động** trên cả 6 nhân vật (dao động từ 12 đến 22 lượt mỗi người). Hai nhân vật trước đây còn ít dữ liệu là `vn_fb_001` và `vn_fb_002` nay đã có dữ liệu hoàn chỉnh, giúp bức tranh thói quen sinh hoạt trở nên cân bằng và rõ nét.
   - Nhìn chung trên toàn hệ thống, các lượt vào mạng được phân bổ tương đối đồng đều quanh mức bình quân: **Ca Sáng** chiếm khoảng $30.5\%$ (29 lượt), **Ca Trưa & Chiều** chiếm $31.6\%$ (30 lượt) và **Ca Tối** chiếm $37.9\%$ (36 lượt). 
   - Tuy nhiên, khi quan sát từng người cụ thể, số lần vào mạng thực tế so với mức bình quân cho thấy **mỗi nhân vật đều có một nhịp sinh hoạt riêng biệt**, phản ánh sát với đặc điểm công việc và lứa tuổi ngoài đời thực.

---

2. **Chi tiết Thiên hướng Sinh hoạt của Từng Nhân vật:**

#### A. `vn_fb_003` — Thói quen Hai Đỉnh (Sáng sớm & Tối muộn)
**Nam 18–24 tuổi, bảo vệ trực ca tại Đà Nẵng (12 lượt)**
* **Thói quen thực tế:** Tập trung nhiều vào Ca Sáng (5 lượt, $41.7\%$) và Ca Tối (6 lượt, $50.0\%$). Ca Trưa & Chiều chỉ xuất hiện đúng **1 lần** ($8.3\%$, thấp hơn nhiều so với mức bình quân kỳ vọng là 3.8 lượt).
* **Lý do thực tế:** Tính chất công việc trực ca ban ngày khiến nhân vật này bị hạn chế dùng điện thoại trong giờ làm việc. Do đó, thời gian mở mạng xã hội dồn vào hai đầu ca: sáng sớm lúc chuẩn bị giao ca và buổi tối khi đã xong việc để nghe nhạc, xem tin tức và giải trí.

#### B. `vn_fb_006` — Dồn vào Buổi Trưa/Chiều & Buổi Tối
**Nam 55–64 tuổi, lao động tự do tại Cần Thơ (13 lượt)**
* **Thói quen thực tế:** Ca Sáng chỉ xuất hiện đúng **1 lần** ($7.7\%$, thấp hơn đáng kể so với mức bình quân kỳ vọng là 4.0 lượt). Toàn bộ thời gian còn lại chia đều cho Ca Trưa & Chiều (6 lượt, $46.2\%$) và Ca Tối (6 lượt, $46.2\%$).
* **Lý do thực tế:** Người lao động lớn tuổi thường bận việc cá nhân hoặc công việc ngoài trời vào buổi sáng sớm. Họ thường chỉ mở Facebook vào giờ nghỉ trưa và buổi tối để đọc tin tức nhà đất, tin thời sự trong khu vực.

#### C. `vn_fb_002` — Cân bằng Đều Đặn Cả Ngày
**Nữ 35–44 tuổi, nội trợ / kinh doanh online (15 lượt)**
* **Thói quen thực tế:** Phân bổ hoàn toàn đồng đều giữa cả 3 ca trong ngày (mỗi ca đúng 5 lượt, tương đương $33.3\%$).
* **Lý do thực tế:** Làm việc tự do tại nhà kết hợp chăm lo gia đình giúp nhân vật này có thời gian linh hoạt, không bị ràng buộc vào khung giờ hành chính. Nhờ vậy, người dùng có thể tranh thủ mở ứng dụng bất kỳ lúc nào rảnh tay.

#### D. `vn_fb_001` — Vào Mạng Thường Xuyên và Nhỉnh hơn Buổi Sáng
**Nữ 25–34 tuổi, nhân viên văn phòng (22 lượt)**
* **Thói quen thực tế:** Có số lượt theo dõi nhiều nhất hệ thống (22 lượt), trải đều cả ngày nhưng nhỉnh hơn vào Ca Sáng (8 lượt, $36.4\%$), Ca Trưa & Chiều có 7 lượt ($31.8\%$) và Ca Tối có 7 lượt ($31.8\%$).
* **Lý do thực tế:** Thói quen của dân văn phòng thường mở mạng xã hội vào đầu giờ sáng để cập nhật tin tức trong ngày và trao đổi thông tin trong các hội nhóm công việc.

#### E. `vn_fb_004` — Rải Đều Cả Ngày và Ưa Chuộng Buổi Tối
**Nữ 18–24 tuổi, sinh viên tại Hà Nội (16 lượt)**
* **Thói quen thực tế:** Vào mạng đều ở các buổi (Sáng 5 lượt, Trưa 5 lượt, Tối 6 lượt), trong đó buổi tối chiếm tỷ lệ cao nhất ($37.5\%$).
* **Lý do thực tế:** Ban ngày có các khoảng nghỉ giữa các tiết học để vào lướt nhanh, nhưng buổi tối mới là thời gian rảnh rỗi chính để ngồi xem video Reels giải trí.

#### F. `vn_fb_005` — Tập trung Giờ Nghỉ Trưa và Tối Sau Giờ Làm
**Nam 35–44 tuổi, thợ kỹ thuật tại Đà Nẵng (17 lượt)**
* **Thói quen thực tế:** Tập trung nhiều hơn vào Ca Trưa & Chiều (6 lượt, $35.3\%$) và Ca Tối (6 lượt, $35.3\%$), Ca Sáng ít hơn (5 lượt, $29.4\%$).
* **Lý do thực tế:** Công việc kỹ thuật đòi hỏi tập trung vào buổi sáng, các khung giờ giải lao giữa ngày và sau giờ làm là thời điểm thuận tiện nhất để mở máy xem bài viết ngắn và cập nhật tin tức.

---

3. **Bảng Đối sánh Lịch trình Hoạt động Giữa Thực tế và Mức Bình quân:**

| Nhân vật | Ca Sáng (06h – 11h) | Ca Trưa & Chiều (11h – 17h) | Ca Tối (17h – 23h) | Tổng lượt | Thiên hướng sinh hoạt nổi bật |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`vn_fb_001`** *(Nữ VP)* | **8 lượt** (36.4%) | 7 lượt (31.8%) | 7 lượt (31.8%) | 22 | Vào mạng nhiều nhất, nhỉnh hơn vào đầu ngày |
| **`vn_fb_002`** *(Nội trợ/KD)* | 5 lượt (33.3%) | 5 lượt (33.3%) | 5 lượt (33.3%) | 15 | Phân bổ cân bằng đều cả 3 buổi |
| **`vn_fb_003`** *(Bảo vệ)* | **5 lượt** (41.7%) | 1 lượt (8.3%) | **6 lượt** (50.0%) | 12 | Hai đỉnh sáng sớm và tối, rất ít dùng ban ngày |
| **`vn_fb_004`** *(Sinh viên)* | 5 lượt (31.2%) | 5 lượt (31.2%) | **6 lượt** (37.5%) | 16 | Rải rác cả ngày, tập trung xem video buổi tối |
| **`vn_fb_005`** *(Kỹ thuật)* | 5 lượt (29.4%) | **6 lượt** (35.3%) | **6 lượt** (35.3%) | 17 | Tập trung vào giờ nghỉ trưa và sau giờ làm |
| **`vn_fb_006`** *(Lao động tự do)* | 1 lượt (7.7%) | **6 lượt** (46.2%) | **6 lượt** (46.2%) | 13 | Rất ít dùng buổi sáng, dồn vào chiều và tối |
| **Toàn hệ thống (TB)** | **29 lượt (30.5%)** | **30 lượt (31.6%)** | **36 lượt (37.9%)** | **95** | **Khung giờ tối có lượng sử dụng cao nhất** |
"""

def to_source_lines(text):
    lines = text.split("\n")
    return [line + "\n" for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])

nb["cells"][10]["source"] = to_source_lines(cell_10_content)

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✅ Đã cập nhật thành công Cell 10 trong notebook!")
