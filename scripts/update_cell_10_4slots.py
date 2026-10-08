import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

notebook_path = Path("notebooks/notebook_action_logs.ipynb")
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cell_10_content = """---
### Nhận định về 4 Khung giờ Hoạt động trong ngày của các Nhân vật:

1. **Đánh giá Tổng quan về Phân bổ 4 Khung giờ (95 lượt hoạt động):**
   - Dữ liệu 95 cửa sổ hoạt động được chia chi tiết theo **4 khung giờ sinh hoạt thực tế**:
     * **Ca Sáng (06h – 11h):** 29 lượt ($30.5\%$) — giờ khởi đầu ngày mới.
     * **Ca Trưa (11h – 14h):** 18 lượt ($18.9\%$) — giờ ăn trưa và giải lao giữa ngày.
     * **Ca Chiều (14h – 18h):** 12 lượt ($12.6\%$) — giờ xế chiều và tan tầm.
     * **Ca Tối (18h – 23h):** 36 lượt ($37.9\%$) — khung giờ giải trí chính trong ngày.
   - Khi tách riêng buổi Trưa và buổi Chiều thành hai khung độc lập, dữ liệu làm lộ rõ các thói quen sinh hoạt và lịch trình rất khác nhau giữa các nhóm nhân vật:

---

2. **Chi tiết Thiên hướng Sinh hoạt theo 4 Khung giờ của Từng Nhân vật:**

#### A. `vn_fb_004` — Không dùng Buổi Trưa, Tập trung Chiều và Tối
**Nữ 18–24 tuổi, sinh viên tại Hà Nội (16 lượt)**
* **Thói quen thực tế:** Buổi trưa hoàn toàn **không mở mạng** (0 lượt, $0.0\%$). Ngược lại, nhân vật này hoạt động rất mạnh vào **Buổi Chiều** (5 lượt, $31.2\%$), **Buổi Tối** (6 lượt, $37.5\%$) và **Buổi Sáng** (5 lượt, $31.2\%$).
* **Lý do thực tế:** Sinh viên thường có lịch học buổi sáng kéo dài hoặc giờ nghỉ trưa ăn cơm/nghỉ ngơi; thời gian rảnh rỗi lướt xem video Reels tập trung nhiều vào buổi chiều tan học và buổi tối ở phòng.

#### B. `vn_fb_003` — Hai Đỉnh Sáng & Tối, Hầu như Vắng bóng Ban Ngày
**Nam 18–24 tuổi, bảo vệ trực ca tại Đà Nẵng (12 lượt)**
* **Thói quen thực tế:** Dồn phần lớn thời gian vào **Buổi Sáng** (5 lượt, $41.7\%$) và **Buổi Tối** (6 lượt, $50.0\%$). Giờ hành chính ban ngày gần như không xuất hiện: Buổi Trưa chỉ có đúng 1 lượt ($8.3\%$) và Buổi Chiều hoàn toàn không vào (0 lượt, $0.0\%$).
* **Lý do thực tế:** Đặc thù ca trực ban ngày hạn chế dùng điện thoại. Nhân vật chỉ mở ứng dụng lúc chuẩn bị giao ca sáng sớm hoặc sau khi hết ca làm việc buổi tối để đọc tin tức và nghe nhạc.

#### C. `vn_fb_006` — Rất ít dùng Buổi Sáng, Dồn vào Trưa và Tối
**Nam 55–64 tuổi, lao động tự do tại Cần Thơ (13 lượt)**
* **Thói quen thực tế:** Buổi Sáng chỉ xuất hiện đúng **1 lần** ($7.7\%$). Toàn bộ thời gian còn lại tập trung vào **Buổi Trưa** (5 lượt, $38.5\%$) và **Buổi Tối** (6 lượt, $46.2\%$), buổi chiều chỉ 1 lượt ($7.7\%$).
* **Lý do thực tế:** Người lớn tuổi thường dậy sớm bận công việc ngoài trời hoặc sinh hoạt gia đình, đến giờ ăn trưa nghỉ ngơi và buổi tối mới mở điện thoại xem tin tức nhà đất và thời sự.

#### D. `vn_fb_001` — Hoạt động Đều Đặn, Nhỉnh hơn vào Buổi Sáng
**Nữ 25–34 tuổi, nhân viên văn phòng (22 lượt)**
* **Thói quen thực tế:** Có số lượt nhiều nhất hệ thống, vào mạng rải đều cả ngày nhưng tập trung nhiều nhất vào **Buổi Sáng** (8 lượt, $36.4\%$), tiếp theo là **Buổi Tối** (7 lượt, $31.8\%$) và **Buổi Trưa** (5 lượt, $22.7\%$), buổi chiều ít hơn (2 lượt, $9.1\%$).
* **Lý do thực tế:** Nhịp làm việc văn phòng thường tranh thủ đọc tin tức đầu ngày trước khi vào việc, ăn trưa và giải trí buổi tối tại nhà.

#### E. `vn_fb_005` — Tập trung Giờ Nghỉ Trưa và Tối Sau Giờ Làm
**Nam 35–44 tuổi, thợ kỹ thuật tại Đà Nẵng (17 lượt)**
* **Thói quen thực tế:** Phân bổ khá đều ở **Buổi Tối** (6 lượt, $35.3\%$), **Buổi Sáng** (5 lượt, $29.4\%$), **Buổi Trưa** (4 lượt, $23.5\%$) và buổi chiều 2 lượt ($11.8\%$).
* **Lý do thực tế:** Công việc kỹ thuật bận rộn ban ngày, thời gian nghỉ giữa ca trưa và sau giờ làm buổi tối là thời điểm thuận tiện nhất để xem tin tức.

#### F. `vn_fb_002` — Lịch Trình Linh Hoạt Cả Ngày
**Nữ 35–44 tuổi, nội trợ / kinh doanh online (15 lượt)**
* **Thói quen thực tế:** Rải đều các buổi: Buổi Sáng (5 lượt, $33.3\%$), Buổi Tối (5 lượt, $33.3\%$), Buổi Trưa (3 lượt, $20.0\%$) và Buổi Chiều (2 lượt, $13.3\%$).
* **Lý do thực tế:** Làm việc tự do tại nhà nên thời gian linh hoạt, có thể tranh thủ vào mạng bất kỳ lúc nào rảnh việc.

---

3. **Bảng Đối sánh Lịch trình Hoạt động qua 4 Khung Giờ:**

| Nhân vật | Sáng (06h – 11h) | Trưa (11h – 14h) | Chiều (14h – 18h) | Tối (18h – 23h) | Tổng lượt | Thiên hướng sinh hoạt nổi bật |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`vn_fb_001`** *(Nữ VP)* | **8 lượt** (36.4%) | 5 lượt (22.7%) | 2 lượt (9.1%) | 7 lượt (31.8%) | 22 | Vào mạng nhiều nhất, nhỉnh hơn vào đầu sáng |
| **`vn_fb_002`** *(Nội trợ/KD)* | 5 lượt (33.3%) | 3 lượt (20.0%) | 2 lượt (13.3%) | 5 lượt (33.3%) | 15 | Lịch trình linh hoạt, rải đều các buổi |
| **`vn_fb_003`** *(Bảo vệ)* | **5 lượt** (41.7%) | 1 lượt (8.3%) | **0 lượt (0.0%)** | **6 lượt** (50.0%) | 12 | Hai đỉnh sáng và tối, vắng bóng ban ngày |
| **`vn_fb_004`** *(Sinh viên)* | 5 lượt (31.2%) | **0 lượt (0.0%)** | **5 lượt** (31.2%) | **6 lượt** (37.5%) | 16 | Trưa không vào, tập trung chiều và tối |
| **`vn_fb_005`** *(Kỹ thuật)* | 5 lượt (29.4%) | 4 lượt (23.5%) | 2 lượt (11.8%) | **6 lượt** (35.3%) | 17 | Tập trung vào trưa và tối sau giờ làm |
| **`vn_fb_006`** *(Lao động tự do)* | 1 lượt (7.7%) | **5 lượt** (38.5%) | 1 lượt (7.7%) | **6 lượt** (46.2%) | 13 | Sáng rất ít vào, dồn vào trưa và tối |
| **Toàn hệ thống (TB)** | **29 lượt (30.5%)** | **18 lượt (18.9%)** | **12 lượt (12.6%)** | **36 lượt (37.9%)** | **95** | **Buổi Tối có lượng người dùng đông nhất** |
"""

def to_source_lines(text):
    lines = text.split("\n")
    return [line + "\n" for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])

nb["cells"][10]["source"] = to_source_lines(cell_10_content)

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✅ Đã cập nhật thành công Cell 10 theo 4 khung giờ trong notebook!")
