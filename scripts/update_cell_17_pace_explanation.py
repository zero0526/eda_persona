import json

cell_17_content = """---
### Nhận định về Cách Thao tác Tay trên Trình duyệt:

#### 1. Sự phân tách rõ rệt giữa hai trường phái nhịp thao tác:
- **Nhóm lướt nhanh (`vn_fb_001`, `vn_fb_005` và phiên đầu của `vn_fb_002`):**
  * Tốc độ cuộn chuột vật lý đạt trung vị từ 3,800 đến 4,760 px/giây.
  * Biên độ mỗi lần cuộn dài (trung vị từ 1,000 đến 1,750 px), thao tác vuốt dứt khoát. Phong cách này phản ánh việc lướt nhanh qua nhiều bài viết để quét tiêu đề và hình ảnh.
- **Nhóm cuộn từ tốn, đọc kỹ (`vn_fb_003`, `vn_fb_004`, `vn_fb_006` và các phiên sau của `vn_fb_002`):**
  * Tốc độ cuộn duy trì ở mức vừa phải (trung vị khoảng 2,480 đến 2,810 px/giây).
  * Biên độ cuộn ngắn và đều (khoảng 650 đến 700 px/lần), giữ màn hình ổn định để đọc kỹ nội dung bài viết, tin rao hoặc phần bình luận.
  * Riêng `vn_fb_004` hầu như không cuộn trang (chỉ 5 lần cuộn trong suốt các phiên) vì dành hơn 87% thời gian xem Reels và chuyển video bằng phím chuyển tiếp.

---

#### 2. Giải thích về tính nhất quán theo phiên và hiện tượng "một người có 2 nhãn nhịp độ":

Nhiều người quan sát thấy trên biểu đồ Cấp độ 3 (Panel B), mỗi nhân vật lại xuất hiện 2 nhãn nhịp độ (`quick`/`fast` hoặc `balanced`/`careful`). Dữ liệu thực tế cho thấy cơ chế vận hành như sau:

* **Tính nhất quán tuyệt đối trong từng phiên (100% Within-Session Consistency):**
  - Trong **từng phiên chạy đơn lẻ**, toàn bộ các thao tác cuộn chuột đều đồng nhất 100% một nhãn duy nhất. Không hề có hiện tượng trong cùng một phiên mà lúc thì cuộn nhanh, lúc lại cuộn chậm.
  - Ví dụ:
    + `vn_fb_001` ở phiên `773d113e`: 52/52 lần cuộn đều là `quick` (100%).
    + `vn_fb_003` ở phiên `a27a406f`: 64/64 lần cuộn đều là `balanced` (100%).
    + `vn_fb_005` ở phiên `397f1fb0`: 18/18 lần cuộn đều là `quick` (100%).
    + `vn_fb_006` ở phiên `3122847b`: 29/29 lần cuộn đều là `balanced` (100%).

* **Tại sao trên biểu đồ tổng hợp lại xuất hiện 2 nhãn?**
  - **Sự tiến hóa quy ước đặt tên nhãn của Runner Engine:**
    + Ở đợt thử nghiệm ngày 05/10: Hệ thống ghi nhận nhịp độ theo nhãn `fast` (cho hợp đồng `quick`) và `careful` (cho hợp đồng `balanced`).
    + Ở các đợt thử nghiệm ngày 06/10 – 08/10: Hệ thống chuẩn hóa để ghi nhận trực tiếp theo tên hợp đồng là `quick` và `balanced`.
    + Về mặt cơ học cử chỉ: `fast` và `quick` thuộc cùng một gia đình **Nhịp Nhanh**; `careful` và `balanced` thuộc cùng một gia đình **Nhịp Cân bằng/Từ tốn**.
  - **Sự phân tách hoàn toàn giữa hai nhóm:**
    + `vn_fb_001` và `vn_fb_005` hoàn toàn 100% thuộc nhóm Nhanh (`fast`/`quick`), không có bất kỳ thao tác nào thuộc nhóm chậm.
    + `vn_fb_003`, `vn_fb_004` và `vn_fb_006` hoàn toàn 100% thuộc nhóm Cân bằng (`careful`/`balanced`), không có bất kỳ thao tác nào thuộc nhóm nhanh.
  - **Trường hợp cập nhật hợp đồng của `vn_fb_002`:**
    + Ở đợt 1 (ngày 05/10), `vn_fb_002` chạy thử với hợp đồng `quick` (sinh nhãn `fast`). Sau đó, hệ thống đã tinh chỉnh hợp đồng sang `balanced` để khớp đúng hồ sơ lao động phổ thông, nên các phiên ngày 07/10 đều chạy ổn định dưới nhãn `balanced`."""

with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

nb['cells'][17]['source'] = [line + '\n' for line in cell_17_content.split('\n')]
nb['cells'][17]['source'][-1] = nb['cells'][17]['source'][-1].rstrip('\n')

with open('notebooks/notebook_action_logs.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cell 17 updated successfully with explanation of session pacing consistency and 2-label phenomenon!")
