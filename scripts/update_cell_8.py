import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

notebook_path = Path("notebooks/notebook_action_logs.ipynb")
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cell_8_content = """---
### Nhận định về Đặc điểm Lịch trình và Thời lượng Hoạt động:

1. **Về Giờ bắt đầu vào mạng trong ngày:**
   - Các lần vào mạng phân bổ tập trung vào **4 khung giờ sinh hoạt quen thuộc**:
     * **Sáng sớm (khoảng 6h30 – 8h30):** Thời điểm trước giờ làm việc hoặc đi học, tranh thủ cập nhật tin tức đầu ngày.
     * **Nghỉ trưa (khoảng 11h30 – 13h30):** Giờ ăn trưa và giải lao giữa ngày.
     * **Buổi chiều (khoảng 15h00 – 17h30):** Giờ giải lao xế chiều hoặc chuẩn bị tan ca.
     * **Buổi tối (khoảng 19h30 – 22h30):** Khung giờ rảnh rỗi chính để giải trí cuối ngày.

2. **Về Thời lượng của mỗi lần vào mạng:**
   - **Nhóm ngồi lướt lâu và thời gian dao động nhiều (`vn_fb_001`, `vn_fb_004`):**
     * `vn_fb_004` (sinh viên): Có thời lượng trung bình cao nhất (23.6 phút), mỗi lần vào mạng trải dài từ 10 đến 35 phút (dao động khoảng $\pm 7.1$ phút). Đặc thù xem video ngắn Reels khiến người dùng này dễ bị cuốn theo các video liên tiếp và ngồi lâu hơn.
     * `vn_fb_001` (nhân viên văn phòng): Thời lượng trung bình đạt 21.2 phút, với độ biến động lớn (từ 12 đến tận 40 phút, dao động khoảng $\pm 9.4$ phút). Phiên lướt nhanh hay ngồi lâu phụ thuộc nhiều vào lượng bài thảo luận trong hội nhóm và bảng tin.
   - **Nhóm thời lượng vừa phải, ổn định bình thường (`vn_fb_003`, `vn_fb_006`):**
     * `vn_fb_003` (bảo vệ): Thời lượng trung bình khoảng 19.2 phút, dao động ở mức vừa phải từ 10 đến 25 phút.
     * `vn_fb_006` (lao động tự do): Thời lượng trung bình khoảng 13.7 phút, dao động từ 8 đến 22 phút, phù hợp với thói quen đọc tin vừa phải của người lớn tuổi.
   - **Nhóm thời lượng rất chặt chẽ, ít biến động (`vn_fb_005`, `vn_fb_002`):**
     * `vn_fb_005` (thợ kỹ thuật): Thời lượng trung bình 13.1 phút, gói gọn rất đều trong khoảng 10 đến 18 phút (độ lệch chỉ $\pm 2.3$ phút, ổn định nhất trong hệ thống). Người dùng này luôn giữ thời gian lướt gọn gàng, hết giờ nghỉ là dừng lại.
     * `vn_fb_002` (nội trợ / kinh doanh online): Thời lượng trung bình 19.2 phút, duy trì đều đặn từ 10 đến 25 phút (độ lệch $\pm 4.2$ phút), nhịp độ mỗi lần dùng rất ổn định.

3. **Về Tần suất vào mạng mỗi ngày:**
   - **Nhóm vào mạng thưa hơn hẳn (`vn_fb_002`, `vn_fb_003`):**
     * `vn_fb_002`: Trung bình chỉ vào khoảng **1.67 lần/ngày** (15 lượt qua 9 ngày).
     * `vn_fb_003`: Trung bình chỉ vào khoảng **1.71 lần/ngày** (12 lượt qua 7 ngày).
     * Cả hai người này đều có tần suất mở mạng xã hội ít hơn rõ rệt so với các nhân vật còn lại do bận công việc nội trợ hoặc trực ca ban ngày.
   - **Nhóm vào mạng thường xuyên hơn:**
     * `vn_fb_001` vào nhiều nhất với trung bình **2.75 lần/ngày** (22 lượt).
     * `vn_fb_005` (2.43 lần/ngày) và `vn_fb_004` (2.29 lần/ngày) cũng đều đặn vào mạng từ 2 đến 3 lần mỗi ngày.

4. **Về Khoảng cách giữa các lần vào mạng liên tiếp:**
   - **Nhóm có khoảng cách ngắn hơn (`vn_fb_004`, `vn_fb_005`):**
     * Khoảng cách trung bình giữa các lần vào mạng của `vn_fb_004` (10.6 giờ) và `vn_fb_005` (11.3 giờ) ngắn hơn so với các nhân vật còn lại (cùng với `vn_fb_001` là 9.8 giờ). Nhờ vào mạng đều 2 đến 3 lần mỗi ngày, thời gian chờ giữa các lần dùng chỉ xoay quanh nửa ngày.
   - **Nhóm có khoảng cách dài hơn:**
     * `vn_fb_002` (trung bình 14.2 giờ) và `vn_fb_003` (trung bình 14.5 giờ) có thời gian giãn cách giữa các lần vào mạng lâu hơn rõ rệt do số lần dùng trong ngày ít hơn.
   - **Nhịp sinh hoạt thường ngày và các khoảng ngắt quãng:**
     * Đa số các lần vào mạng cách nhau từ 5 đến 13 giờ (tương ứng với nhịp sáng – trưa – tối và giấc ngủ qua đêm).
     * Một số khoảng cách dài vượt quá 24 giờ xuất hiện là do hệ thống tạm dừng giữa ngày 05/10 và 06/10 (kết thúc sớm hôm trước và bắt đầu muộn vào chiều hôm sau), chứ không phải do người dùng bỏ mạng nhiều ngày.
"""

def to_source_lines(text):
    lines = text.split("\n")
    return [line + "\n" for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])

nb["cells"][8]["source"] = to_source_lines(cell_8_content)

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✅ Đã cập nhật thành công Cell 8 trong notebook!")
