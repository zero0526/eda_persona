import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

notebook_path = Path("notebooks/notebook_action_logs.ipynb")
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cell_8_content = """---
### Nhận định từ Dữ liệu Khám phá về Lịch trình và Thời lượng Hoạt động:

1. **Về Giờ bắt đầu vào mạng trong ngày:**
   - Dữ liệu ghi nhận sự phân bổ tập trung vào **4 khung giờ sinh hoạt trong ngày**:
     * **Sáng sớm (khoảng 6h30 – 8h30):** Thời điểm đầu ngày.
     * **Nghỉ trưa (khoảng 11h30 – 13h30):** Giữa ngày.
     * **Buổi chiều (khoảng 15h00 – 17h30):** Xế chiều.
     * **Buổi tối (khoảng 19h30 – 22h30):** Khung giờ có mật độ phiên cao nhất.

2. **Về Thời lượng của mỗi phiên:**
   - **Nhóm có thời lượng phiên dài và dải dao động rộng (`vn_fb_001`, `vn_fb_004`):**
     * `vn_fb_004`: Thời lượng trung bình cao nhất hệ thống (23.6 phút), dải thời lượng trải rộng từ 10 đến 35 phút (độ lệch khoảng 7.1 phút), ghi nhận nhiều phiên kéo dài trên 30 phút.
     * `vn_fb_001`: Thời lượng trung bình đạt 21.2 phút, với dải dao động rộng nhất (từ 12 đến 40 phút, độ lệch 9.4 phút).
   - **Nhóm có thời lượng vừa phải (`vn_fb_003`, `vn_fb_006`):**
     * `vn_fb_003`: Thời lượng trung bình 19.2 phút, dao động trong khoảng 10 đến 25 phút (độ lệch 4.7 phút).
     * `vn_fb_006`: Thời lượng trung bình 13.7 phút, dải thời lượng từ 8 đến 22 phút (độ lệch 4.7 phút), không ghi nhận phiên nào vượt quá 22 phút.
   - **Nhóm có thời lượng tập trung và biên độ hẹp (`vn_fb_005`, `vn_fb_002`):**
     * `vn_fb_005`: Thời lượng trung bình 13.1 phút, tập trung rất chặt chẽ trong khoảng 10 đến 18 phút (độ lệch chỉ 2.3 phút, ổn định nhất hệ thống), không có phiên nào kéo dài đột biến.
     * `vn_fb_002`: Thời lượng trung bình 19.2 phút, phân bố đều trong khoảng 10 đến 25 phút (độ lệch 4.2 phút).

3. **Về Tần suất phiên mỗi ngày:**
   - **Nhóm có tần suất phiên trung bình thấp hơn (`vn_fb_002`, `vn_fb_003`):**
     * `vn_fb_002`: Trung bình 1.67 phiên/ngày (tổng 15 cửa sổ qua 9 ngày ghi nhận).
     * `vn_fb_003`: Trung bình 1.71 phiên/ngày (tổng 12 cửa sổ qua 7 ngày ghi nhận).
     * Mức tần suất này thấp hơn rõ rệt so với các nhân vật còn lại.
   - **Nhóm có tần suất phiên trung bình cao hơn (`vn_fb_001`, `vn_fb_005`, `vn_fb_004`):**
     * `vn_fb_001`: Trung bình 2.75 phiên/ngày (tổng 22 cửa sổ qua 8 ngày).
     * `vn_fb_005`: Trung bình 2.43 phiên/ngày (tổng 17 cửa sổ qua 7 ngày).
     * `vn_fb_004`: Trung bình 2.29 phiên/ngày (tổng 16 cửa sổ qua 7 ngày).
     * `vn_fb_006`: Trung bình 1.86 phiên/ngày (tổng 13 cửa sổ qua 7 ngày).

4. **Về Khoảng cách giữa các lần thực thi liên tiếp (`gap_hours`):**
   - **Nhóm có khoảng cách ngắn hơn (`vn_fb_001`, `vn_fb_004`, `vn_fb_005`):**
     * Trung vị khoảng cách (Median) của nhóm này chỉ từ **7.2 đến 8.0 giờ** (trung bình từ 9.8 đến 11.3 giờ).
     * Phần lớn các khoảng cách thực tế nằm trong khoảng 5 đến 11 giờ, phản ánh nhịp luân chuyển giữa các ca sáng, trưa, chiều và tối trong cùng chu kỳ vận hành.
   - **Nhóm có khoảng cách dài hơn (`vn_fb_002`, `vn_fb_003`, `vn_fb_006`):**
     * Trung vị khoảng cách (Median) của nhóm này lên tới **11.5 đến 12.1 giờ** (trung bình từ 13.1 đến 14.5 giờ).
     * Khoảng thời gian giãn cách giữa các phiên dài hơn tương ứng với tần suất phiên ít hơn trong ngày.
   - **Lưu ý về các khoảng cách kéo dài (> 24 giờ):**
     * Dữ liệu ghi nhận một số giá trị khoảng cách đơn lẻ vượt mốc 24 giờ (từ 25 đến 55.5 giờ) ở mỗi nhân vật. Đây là các khoảng ngắt quãng vận hành hệ thống giữa các đợt thử nghiệm (ví dụ giữa ngày 05/10 và 06/10), chứ không phản ánh nhịp sinh hoạt liên tục thường nhật. Những giá trị này kéo giá trị trung bình (mean) lên cao hơn đáng kể so với trung vị (median) thực tế của các phiên.
"""

def to_source_lines(text):
    lines = text.split("\n")
    return [line + "\n" for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])

nb["cells"][8]["source"] = to_source_lines(cell_8_content)

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✅ Đã cập nhật thành công Cell 8 theo bản sửa đổi logic và phương pháp luận mới!")
