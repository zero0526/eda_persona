import json

cell_10_content = """---
### Nhận định về 4 Khung giờ Hoạt động trong ngày của các Nhân vật:

1. **Đánh giá Tổng quan về Phân bổ 4 Khung giờ (95 lượt hoạt động):**
   - Dữ liệu 95 cửa sổ hoạt động được chia chi tiết theo **4 khung giờ sinh hoạt thực tế**:
     * **Ca Sáng (06h – 11h):** 29 lượt ($30.5\%$) — giờ khởi đầu ngày mới.
     * **Ca Trưa (11h – 14h):** 18 lượt ($18.9\%$) — giờ ăn trưa và giải lao giữa ngày.
     * **Ca Chiều (14h – 18h):** 12 lượt ($12.6\%$) — giờ xế chiều và tan tầm.
     * **Ca Tối (18h – 23h):** 36 lượt ($37.9\%$) — khung giờ giải trí chính trong ngày.
---

2. **Chi tiết Thiên hướng Sinh hoạt theo 4 Khung giờ của Từng Nhân vật:**

#### A. `vn_fb_004` — Không dùng Buổi Trưa, Tập trung Chiều và Tối
**Nhân viên nhà hàng, 25–34 tuổi tại Đồng Nai (16 lượt)**
* **Thói quen thực tế:** Buổi trưa hoàn toàn **không mở mạng** (0 lượt, $0.0\%$). Ngược lại, nhân vật này hoạt động nhiều vào **Buổi Chiều** (5 lượt, $31.2\%$), **Buổi Tối** (6 lượt, $37.5\%$) và **Buổi Sáng** (5 lượt, $31.2\%$).
* **Lý do thực tế:** Nhân viên ngành dịch vụ ăn uống phải phục vụ khách vào giờ cao điểm ăn trưa nên không thể dùng điện thoại; quãng thời gian rảnh giữa ca rơi vào buổi chiều (14h00–16h00) và xả hơi sau ca làm vào tối muộn (21h30–22h30).

#### B. `vn_fb_003` — Hai Đỉnh Sáng & Tối, Hầu như Vắng bóng Ban Ngày
**Nhân viên bảo vệ, 18–24 tuổi tại Đà Nẵng (12 lượt)**
* **Thói quen thực tế:** Dồn phần lớn thời gian vào **Buổi Sáng** (5 lượt, $41.7\%$) và **Buổi Tối** (6 lượt, $50.0\%$). Giờ hành chính ban ngày gần như không xuất hiện: Buổi Trưa chỉ có đúng 1 lượt ($8.3\%$) và Buổi Chiều hoàn toàn không vào (0 lượt, $0.0\%$).
* **Lý do thực tế:** Ca trực ban ngày nghiêm ngặt hạn chế dùng điện thoại. Nhân vật chỉ mở ứng dụng lúc chuẩn bị vào ca sáng sớm (6h30–7h00) hoặc sau khi hết ca trực buổi tối (20h00–21h30) để bình luận dạo và nghe nhạc.

#### C. `vn_fb_006` — Rất ít dùng Buổi Sáng, Dồn vào Trưa và Tối
**Kinh doanh tự do Gen X, 55–64 tuổi tại Cần Thơ (13 lượt)**
* **Thói quen thực tế:** Buổi Sáng chỉ xuất hiện đúng **1 lần** ($7.7\%$). Toàn bộ thời gian còn lại tập trung vào **Buổi Trưa** (5 lượt, $38.5\%$) và **Buổi Tối** (6 lượt, $46.2\%$), buổi chiều chỉ 1 lượt ($7.7\%$).
* **Lý do thực tế:** Người lớn tuổi thường dậy sớm bận công việc gia đình hoặc hoạt động đời thường ngoài đời thực; đến giờ nghỉ trưa và buổi tối sau bữa cơm mới mở điện thoại xem tin tức và video.

#### D. `vn_fb_001` — Hoạt động Đều Đặn, Nhỉnh hơn vào Buổi Sáng
**Thiết kế đồ họa, 25–34 tuổi tại Hà Nội (22 lượt)**
* **Thói quen thực tế:** Có số lượt nhiều nhất hệ thống, vào mạng rải đều cả ngày nhưng tập trung nhiều nhất vào **Buổi Sáng** (8 lượt, $36.4\%$), tiếp theo là **Buổi Tối** (7 lượt, $31.8\%$) và **Buổi Trưa** (5 lượt, $22.7\%$), buổi chiều ít hơn (2 lượt, $9.1\%$).
* **Lý do thực tế:** Nhịp làm việc thiết kế/văn phòng linh hoạt (hybrid) thường ghé nhanh đầu ngày kiểm tra tin tức trước khi làm việc, nghỉ trưa lướt tin và tối giải trí, sáng tạo nội dung tại nhà.

#### E. `vn_fb_005` — Tập trung Giờ Nghỉ Trưa và Tối Sau Giờ Làm
**Thợ kỹ thuật cơ khí, 35–44 tuổi tại Đà Nẵng (17 lượt)**
* **Thói quen thực tế:** Phân bổ khá đều ở **Buổi Tối** (6 lượt, $35.3\%$), **Buổi Sáng** (5 lượt, $29.4\%$), **Buổi Trưa** (4 lượt, $23.5\%$) và buổi chiều 2 lượt ($11.8\%$).
* **Lý do thực tế:** Công việc kỹ thuật tại xưởng ban ngày bận rộn; cữ uống cà phê sáng sớm, nghỉ giữa ca trưa và sau giờ làm buổi tối là thời điểm cố định để xem tin tức.

#### F. `vn_fb_002` — Lịch Trình Linh Hoạt Theo Sinh Hoạt Gia Đình
**Lao động phổ thông, 35–44 tuổi tại TP.HCM, gia đình đông con (15 lượt)**
* **Thói quen thực tế:** Rải đều các buổi: Buổi Sáng (5 lượt, $33.3\%$), Buổi Tối (5 lượt, $33.3\%$), Buổi Trưa (3 lượt, $20.0\%$) và Buổi Chiều (2 lượt, $13.3\%$).
* **Lý do thực tế:** Tranh thủ vào mạng vào các quãng nghỉ giữa ngày và buổi tối sau khi thu xếp chu toàn công việc nhà và con cái.

---

3. **Bảng Đối sánh Lịch trình Hoạt động qua 4 Khung Giờ:**

| Nhân vật | Sáng (06h – 11h) | Trưa (11h – 14h) | Chiều (14h – 18h) | Tối (18h – 23h) | Tổng lượt | Thiên hướng sinh hoạt nổi bật |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`vn_fb_001`** *(Thiết kế đồ họa)* | **8 lượt** (36.4%) | 5 lượt (22.7%) | 2 lượt (9.1%) | 7 lượt (31.8%) | 22 | Vào mạng nhiều nhất, nhỉnh hơn vào đầu sáng |
| **`vn_fb_002`** *(Lao động phổ thông)* | 5 lượt (33.3%) | 3 lượt (20.0%) | 2 lượt (13.3%) | 5 lượt (33.3%) | 15 | Lịch trình sinh hoạt đều đặn theo ca nghỉ |
| **`vn_fb_003`** *(Bảo vệ)* | **5 lượt** (41.7%) | 1 lượt (8.3%) | **0 lượt (0.0%)** | **6 lượt** (50.0%) | 12 | Hai đỉnh sáng và tối, vắng bóng ban ngày |
| **`vn_fb_004`** *(Nhân viên nhà hàng)* | 5 lượt (31.2%) | **0 lượt (0.0%)** | **5 lượt** (31.2%) | **6 lượt** (37.5%) | 16 | Trưa bận phục vụ khách, dồn chiều và tối |
| **`vn_fb_005`** *(Thợ kỹ thuật)* | 5 lượt (29.4%) | 4 lượt (23.5%) | 2 lượt (11.8%) | **6 lượt** (35.3%) | 17 | Nhịp đều theo cữ sáng, trưa và tối sau giờ làm |
| **`vn_fb_006`** *(Kinh doanh Gen X)* | 1 lượt (7.7%) | **5 lượt** (38.5%) | 1 lượt (7.7%) | **6 lượt** (46.2%) | 13 | Sáng rất ít vào, dồn vào trưa và tối |
| **Toàn hệ thống (TB)** | **29 lượt (30.5%)** | **18 lượt (18.9%)** | **12 lượt (12.6%)** | **36 lượt (37.9%)** | **95** | **Buổi Tối có lượng người dùng đông nhất** |"""

with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

nb['cells'][10]['source'] = [line + '\n' for line in cell_10_content.split('\n')]
nb['cells'][10]['source'][-1] = nb['cells'][10]['source'][-1].rstrip('\n')

with open('notebooks/notebook_action_logs.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cell 10 updated successfully with accurate persona demographics!")
