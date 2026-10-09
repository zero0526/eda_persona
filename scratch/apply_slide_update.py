# -*- coding: utf-8 -*-
"""
Script to update notebooks/slide.md with the new 4-slide structure for Slide 2.5, 2.5.1, 2.5.2, 2.5.3.
"""

import os

slide_path = os.path.abspath("notebooks/slide.md")

with open(slide_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update TOC
old_toc = """    * [Slide 2.4: Thói quen Cuộn trang & Động lực học Thao tác (Scroll Dynamics)](#-slide-24-thói-quen-cuộn-trang--động-lực-học-thao-tác-scroll-dynamics)
    * [Slide 2.5: Thống kê Căn cứ Nhận thức Vĩ mô (Macro Decision Evidence) & Ma trận Liên kết Hành vi](#-slide-25-thống-kê-căn-cứ-nhận-thức-vĩ-mô-macro-decision-evidence--ma-trận-liên-kết-hành-vi)
    * [Slide 2.5-Chi Tiết: Đối sánh Ma trận Nhận thức 6 Persona theo 2 Nhóm Bản sắc](#-slide-25-chi-tiết-đối-sánh-ma-trận-nhận-thức-6-persona-theo-2-nhóm-bản-sắc)
  * *Phân đoạn 2.C: Trí Nhớ Xuyên Phiên, Chuỗi Hành Vi Thương Hiệu & Tiền Đề Tương Tác*"""

new_toc = """    * [Slide 2.4: Thói quen Cuộn trang & Động lực học Thao tác (Scroll Dynamics)](#-slide-24-thói-quen-cuộn-trang--động-lực-học-thao-tác-scroll-dynamics)
    * [Slide 2.5: Tổng quan Ma trận Phân hóa Động lực Toàn Hệ thống & Nguyên tắc Nhận thức 1-1](#-slide-25-tổng-quan-ma-trận-phân-hóa-động-lực-toàn-hệ-thống--nguyên-tắc-nhận-thức-1-1)
    * [Slide 2.5.1: Đối sánh Động lực Hành vi Chủ động Gõ phím (`SEARCH` & `COMMENT`)](#-slide-251-đối-sánh-động-lực-hành-vi-chủ-động-gõ-phím-search--comment)
    * [Slide 2.5.2: Đối sánh Động lực Hành vi Thẩm định Văn bản (`READ` & `EXPAND`)](#-slide-252-đối-sánh-động-lực-hành-vi-thẩm-định-văn-bản-read--expand)
    * [Slide 2.5.3: Đối sánh Động lực Hành vi Cảm xúc & Lan tỏa (`REACT` & `SHARE`)](#-slide-253-đối-sánh-động-lực-hành-vi-cảm-xúc--lan-tỏa-react--share)
  * *Phân đoạn 2.C: Trí Nhớ Xuyên Phiên, Chuỗi Hành Vi Thương Hiệu & Tiền Đề Tương Tác*"""

assert old_toc in content, "Old TOC not found in content!"
content = content.replace(old_toc, new_toc, 1)

# 2. Update Slide 2.5 sections
start_marker = """### 4. Lời thoại Chuyển tiếp sang Slide kế tiếp
> *"Thao tác cuộn và dừng đọc đều rất tự nhiên. Nhưng điều gì ẩn sâu bên trong tâm trí đã thúc đẩy họ dừng lại ở bài viết đó? Hãy cùng khám phá Căn cứ nhận thức vĩ mô tại Slide 2.5."*

---

## 🖥️ SLIDE 2.5: THỐNG KÊ CĂN CỨ NHẬN THỨC VĨ MÔ (MACRO DECISION EVIDENCE) & MA TRẬN LIÊN KẾT HÀNH VI"""

end_marker = """### 3. Lời thoại Chuyển tiếp sang Slide kế tiếp
> *"Một phiên lướt mạng có suy nghĩ như vậy là rất ấn tượng. Nhưng qua các ngày khác nhau, các phiên khác nhau, liệu Agent có nhớ những gì mình đã đọc và duy trì được mạch quan tâm hay không? Hãy cùng đến với Slide 2.6 về Trí nhớ xuyên phiên."*

---

## 🖥️ SLIDE 2.6: TÍNH LIÊN KẾT THÔNG TIN XUYÊN PHIÊN (CROSS-SESSION MEMORY & CONTINUITY)"""

assert start_marker in content, "Start marker for Slide 2.5 not found!"
assert end_marker in content, "End marker for Slide 2.5 not found!"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker) + len(end_marker) - len("""\n\n## 🖥️ SLIDE 2.6: TÍNH LIÊN KẾT THÔNG TIN XUYÊN PHIÊN (CROSS-SESSION MEMORY & CONTINUITY)""")

slide_replacement = """### 4. Lời thoại Chuyển tiếp sang Slide kế tiếp
> *"Thao tác cuộn và dừng đọc đều rất tự nhiên. Nhưng điều gì ẩn sâu bên trong tâm trí đã thúc đẩy họ dừng lại ở bài viết đó? Đâu là mục đích thực sự của từng persona? Hãy cùng khám phá Tổng quan Ma trận Phân hóa Động lực tại Slide 2.5."*

---

## 🖥️ SLIDE 2.5: TỔNG QUAN MA TRẬN PHÂN HÓA ĐỘNG LỰC TOÀN HỆ THỐNG & NGUYÊN TẮC NHẬN THỨC 1-1

### 1. Hình ảnh Trực quan Slide
![Tổng quan Căn cứ Nhận thức Vĩ mô & Ma trận Phân hóa Động lực](../output/figures/slide2_5_macro_decision_evidence_overview.png)

### 2. Nội dung Trình chiếu trên Slide
* **Tiêu đề:** TỔNG QUAN MA TRẬN PHÂN HÓA ĐỘNG LỰC TOÀN HỆ THỐNG & NGUYÊN TẮC NHẬN THỨC 1-1
* **Thông điệp cốt lõi:** Điều gì ẩn sâu bên trong nhận thức đã thúc đẩy Agent dừng lại và đưa ra hành vi có chủ đích? Thay vì gom cụm 2 nhóm gượng ép thiếu căn cứ thực nghiệm, dữ liệu chứng minh mỗi Persona là một vector động lực độc lập; 100% quyết định tập trung ($N = 325$) đều tuân thủ nguyên tắc 1-1 qua Chain-of-Thought (CoT), kết nối trực tiếp căn tính nhân vật với 6 hành vi cụ thể.
* **Tập dữ liệu khảo sát:** $N = 325$ hành vi tập trung cao (`read`: 178, `react`: 74, `comment`: 35, `expand`: 20, `search`: 17, `share`: 1).

* **PHẦN 1: NGUYÊN TẮC NHẬN THỨC 1-1 & TÔN TRỌNG TÍNH PHÂN HÓA ĐA CHIỀU (BÁC BỎ GOM CỤM 2 NHÓM)**
  * **Nguyên tắc quyết định nhận thức 1-1:** Trong kiến trúc nhận thức của hệ thống, mỗi hành vi tập trung đưa ra bắt buộc phải có **đúng 1 lý do chính (`primary_evidence` / `primary_dimension`)** được trích xuất từ hồ sơ Persona thông qua chuỗi suy luận Chain-of-Thought (CoT). $100\%$ quyết định đều có căn cứ nhận thức minh bạch, hoàn toàn loại bỏ yếu tố ngẫu nhiên vô thức.
  * **Bác bỏ gom cụm 2 nhóm gượng ép — Sự thật từ dữ liệu thực nghiệm:**
    * Phân tích khoảng cách cosine trên không gian động lực cho thấy: Bộ ba `001, 005, 006` có mức độ tương đồng nhất định về nhu cầu tìm tòi tri thức/đầu tư ($d_{cos} = 0.11 - 0.35$), nhưng phương thức hành động lại hoàn toàn rẽ nhánh: `001` thiên về đọc sâu duy lý & thả tim (86.6%), `005` bùng nổ tìm kiếm & bình luận tri ân (44.6% hành vi chủ động), trong khi `006` tập trung thẩm định BĐS chậm rãi (72.9% đọc sâu).
    * Ngược lại, bộ ba `002, 003, 004` hoàn toàn phân tán xa nhau trên không gian vector ($d_{cos} = 0.83 - 0.87$): `002` hướng nội về tâm linh/gia đình, `003` cuồng nhiệt ẩm thực đường phố và dẫn đầu về bình luận (39.1%), còn `004` chỉ quan tâm bóng đá và video ngắn (81.0%).
    * Do đó, việc gom cụm 2 nhóm là thiếu bằng chứng khoa học vững chắc. Hệ thống lựa chọn phương pháp **đối sánh trực diện 6 Persona trên từng cặp hành vi cụ thể (2 hành vi / slide)** để phản ánh trung thực bản sắc từng cá nhân.

* **PHẦN 2: BẢNG MA TRẬN PHÂN HÓA ĐỘNG LỰC & HÀNH VI 6 PERSONA TOÀN HỆ THỐNG**

| Persona | Số Hành Vi Tập Trung | Top 3 Động Lực Nhận Thức Chi Phối | Hành Vi Bộc Lộ Mạnh Nhất | Phong Cách Nhận Thức Chủ Đạo |
| :--- | :---: | :--- | :--- | :--- |
| **`vn_fb_001`** *(Thiết kế đồ họa, 26t, HCM)* | 82 (25.2%) | 🧠 `curiosity` (54.9%), 💼 `real_estate` (23.2%), 🎨 `career_role` (8.5%) | 📖 Read: 63.4%, ❤️ React: 23.2% | **Duy lý & Thẩm mỹ:** Đọc sâu cờ vua, tìm tòi công nghệ AI kiến trúc, thẩm định BĐS. |
| **`vn_fb_002`** *(Lao động tự do, 42t, Nghệ An)* | 42 (12.9%) | 🌸 `tone` (33.3%), 📿 `spirituality` (16.7%), 🏡 `parenting_family` (14.3%) | 📖 Read: 50.0%, ❤️ React: 45.2% | **Tâm linh & Gia đình:** Cầu an tượng Phật bà, đọc về viện dưỡng lão, chúc phúc an lành. |
| **`vn_fb_003`** *(Bảo vệ trực ca, 28t, Đà Nẵng)* | 46 (14.2%) | 🍜 `cuisine_vn` (30.4%), 🍢 `street_food` (19.6%), 💬 `social_engagement` (13.0%) | 📖 Read: 50.0%, 💬 Comment: 39.1% | **Ẩm thực & Giao tiếp đường phố:** Tỷ lệ comment cao nhất mạng (39.1%), tìm quán ăn ca đêm. |
| **`vn_fb_004`** *(Nhân viên quán, 22t, HCM)* | 21 (6.5%) | ⚽ `sport_football` (47.6%), 📱 `content_format` (33.3%), 🧠 `curiosity` (14.3%) | 📖 Read: 47.6%, ❤️ React: 42.9% | **Thể thao & Video ngắn:** Chỉ tương tác với highlight bóng đá và video hài, lướt nhanh thụ động. |
| **`vn_fb_005`** *(Thợ cơ khí, 34t, Đà Nẵng)* | 74 (22.8%) | 🧠 `curiosity` (56.8%), 🇻🇳 `value_tradition` (28.4%), 🍜 `cuisine_japan` (2.7%) | 📖 Read: 39.2%, 💬 Comment: 16.2%, 🔍 Expand: 14.9%, 🔎 Search: 12.2% | **Khám phá kỹ thuật & Tri ân lịch sử:** Hành vi đa dạng nhất, dẫn đầu tìm kiếm và xem thêm. |
| **`vn_fb_006`** *(Nhà đầu tư Gen X, 52t, Cần Thơ)* | 59 (18.2%) | 💼 `real_estate` (28.8%), 🧠 `curiosity` (25.4%), 🌿 `value_health` (10.2%) | 📖 Read: 72.9%, ❤️ React: 20.3% | **Thực dụng & Thận trọng:** Tỷ lệ đọc sâu cao nhất (72.9%), khảo sát giá căn hộ Cái Răng. |

* **PHẦN 3: PHÂN BỔ CÁC ĐỘNG LỰC CỐT LÕI VÀO 6 HÀNH VI (PANEL A & PANEL B - HEATMAP)**
  * **Top 8 động lực chi phối toàn mạng:** `curiosity` (119 lượt — 36.6%), `interest_real_estate` (36 lượt — 11.1%), `value_tradition` (21 lượt — 6.5%), `cuisine_vietnamese` (14 lượt — 4.3%), `tone` (14 lượt — 4.3%), `content_consumption_format` (13 lượt — 4.0%), `sport_football` (10 lượt — 3.1%), `career_role` (7 lượt — 2.2%).
  * **Quy luật chuyển hóa động lực sang hành vi:**
    * Động lực `curiosity` kích hoạt mạnh nhất ở **Đọc sâu (`read` - 82 lượt)**, **Mở rộng ("Xem thêm" `expand` - 12 lượt)** và **Tìm kiếm chủ động (`search` - 12 lượt)**.
    * Động lực đời thường, ẩm thực và cảm xúc chuyển hóa trực tiếp thành **Thả cảm xúc (`react` - 31 lượt)** và **Viết bình luận (`comment` - 17 lượt)**.
    * Đặc biệt, lòng tự hào dân tộc `value_tradition` có tỷ lệ chuyển hóa thành bình luận tri ân cao nhất toàn hệ thống ($11/21 = 52.4\%$).

### 3. Lời thoại Thuyết trình của Người nói (Speaker Script)
> *"Kính thưa Hội đồng,
> 
> Bắt đầu đi sâu vào phân tích nhận thức tại Slide 2.5, câu hỏi trọng tâm đặt ra là: **Điều gì ẩn sâu bên trong tâm trí đã thôi thúc các Agent dừng lại và đưa ra hành vi có chủ đích? Đâu là mục đích thực sự của họ?**
> 
> Nguyên tắc nền tảng đầu tiên của hệ thống là: **Mỗi hành vi tập trung đưa ra đều gắn với đúng một lý do chính (`primary_evidence`)** được trích xuất tường minh từ hồ sơ cá nhân qua chuỗi suy luận Chain-of-Thought (CoT). Trong toàn bộ 325 hành vi tập trung cao được ghi nhận, 100% quyết định đều có căn cứ nhận thức minh bạch, không hề có hành vi ngẫu nhiên mù quáng.
> 
> Ban đầu, một giả định thông thường có thể nghĩ đến việc gom 6 Persona thành 2 nhóm lớn. Tuy nhiên, khi kiểm tra khoảng cách cosine trên không gian động lực thực nghiệm, chúng tôi nhận thấy việc gom nhóm như vậy là thiếu căn cứ vững chắc:
> - Ba nhân vật `001, 005, 006` dù cùng có điểm tựa tò mò tri thức, nhưng hành vi thực tế lại rẽ thành ba ngả: cô thiết kế đọc sâu thẩm mỹ, anh thợ cơ khí bùng nổ tìm kiếm và bình luận tri ân, còn bác doanh nhân lớn tuổi chỉ tập trung khảo sát bất động sản.
> - Trong khi đó, ba nhân vật `002, 003, 004` hoàn toàn phân tán xa nhau: một người hướng về tâm linh gia đình, một người đam mê ẩm thực đường phố và chăm viết bình luận nhất mạng, và một cậu thanh niên chỉ quan tâm đến video highlight bóng đá.
> 
> Nhìn vào Ma trận nhiệt phân hóa tại Panel A và Panel B:
> - Top 8 động lực cốt lõi thể hiện rõ các nhu cầu căn bản của con người: từ tò mò tri thức, khảo sát tài sản, tri ân cội nguồn, đến ẩm thực, thể thao và giải trí.
> - Mỗi Persona sở hữu một cơ cấu hành vi hoàn toàn độc bản: Bác `006` dẫn đầu về tỷ lệ đọc sâu tới 72.9%; anh `003` dẫn đầu toàn mạng về tỷ lệ bình luận tới 39.1%; anh thợ `005` là người có hành vi đa dạng nhất khi chiếm hơn một nửa lượng tìm kiếm và xem thêm toàn hệ thống.
> 
> Để làm sáng tỏ sự khác biệt về động lực này một cách khoa học và trực quan nhất, chúng tôi không chia nhóm chung chung mà sẽ **đối sánh trực diện cả 6 Persona trên từng cặp hành vi cụ thể (2 hành vi mỗi slide)**: Bắt đầu từ 2 hành vi chủ động gõ phím `SEARCH` & `COMMENT` tại Slide 2.5.1, tiếp đến 2 hành vi thẩm định văn bản `READ` & `EXPAND` tại Slide 2.5.2, và cuối cùng là 2 hành vi cảm xúc `REACT` & `SHARE` tại Slide 2.5.3."*

### 4. Lời thoại Chuyển tiếp sang Slide kế tiếp
> *"Sau khi đã nắm vững bức tranh tổng thể về ma trận động lực toàn hệ thống, chúng ta hãy cùng bắt đầu giải phẫu 2 hành vi đòi hỏi nỗ lực nhận thức chủ động cao nhất — nơi Agent phải trực tiếp gõ phím: Tìm kiếm (`SEARCH`) và Viết bình luận (`COMMENT`) tại Slide 2.5.1."*

---

## 🖥️ SLIDE 2.5.1: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CHỦ ĐỘNG GÕ PHÍM (`SEARCH` & `COMMENT`)

### 1. Hình ảnh Trực quan Slide
![Đối sánh Động lực Hành vi Chủ động Gõ phím](../output/figures/slide2_5_1_search_and_comment.png)

### 2. Nội dung Trình chiếu trên Slide
* **Tiêu đề:** ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CHỦ ĐỘNG GÕ PHÍM: `SEARCH` & `COMMENT`
* **Thông điệp cốt lõi:** `SEARCH` (17 lượt) và `COMMENT` (35 lượt) là hai hành vi chủ động tiêu tốn chi phí nhận thức cao nhất trên mạng xã hội; thay vì thụ động tiếp nhận, Agent phải tự sinh câu lệnh truy vấn hoặc tự viết phản hồi bằng tiếng Việt; mỗi Persona bộc lộ động lực và phong cách giao tiếp hoàn toàn khác biệt.

* **BẢNG 1: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI TÌM KIẾM CHỦ ĐỘNG (`SEARCH` — 17 LƯỢT)**

| Persona | Số Lượt (% Hành Vi) | Động Lực Chi Phối Hàng Đầu | Từ Khóa / Nội Dung Tìm Kiếm | Trích Dẫn Chain-of-Thought (CoT) Nguyên Văn | Phân Tích Mục Đích Thực Sự |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **9** *(52.9%)* | 🧠 `curiosity` (8)<br>📍 `province` (1) | *"thời điểm quan sát Sao Hỏa đối lập Đà Nẵng 4/10"* | *"Muốn tìm thông tin cụ thể về thời điểm tốt nhất để quan sát Sao Hỏa đối lập tại Đà Nẵng vào ngày 4/10..."* | Chủ động bù đắp thông tin chuyên sâu mà Newsfeed chưa có; thỏa mãn niềm đam mê thiên văn học gắn với vị trí địa phương. |
| **`vn_fb_006`** *(Gen X BĐS Cần Thơ)* | **3** *(17.6%)* | 💼 `real_estate` (2)<br>🧠 `curiosity` (1) | *"quy hoạch Nam Cần Thơ", "giá đất Cái Răng"* | *"Tìm kiếm thông tin quy hoạch và giá đất khu đô thị Nam Cần Thơ để cập nhật biến động thị trường..."* | Khảo sát thực địa phục vụ đầu tư dòng tiền; tìm kiếm có mục đích kinh tế và tài chính cụ thể. |
| **`vn_fb_001`** *(Thiết kế đồ họa TP.HCM)* | **2** *(11.8%)* | 🎨 `career_role` (1)<br>💻 `technology` (1) | *"công cụ AI mới cho thiết kế kiến trúc"* | *"Tìm hiểu các công cụ AI mới cho thiết kế kiến trúc, lĩnh vực mình đang làm việc..."* | Cập nhật công nghệ nghề nghiệp đồ họa/thiết kế; nâng cao năng suất chuyên môn thiết thực. |
| **`vn_fb_003`** *(Bảo vệ Đà Nẵng)* | **2** *(11.8%)* | 🍢 `street_food` (2) | *"quán bún trộn Đà Nẵng ngon"* | *"Feed hiện không có nội dung phù hợp sở thích; tìm kiếm quán bún trộn Đà Nẵng để khám phá ẩm thực đường phố..."* | Giải tỏa nhu cầu ăn uống đời thường; tìm quán ăn đêm lân cận ca trực khi Newsfeed không hiển thị. |
| **`vn_fb_004`** *(Phục vụ trẻ TP.HCM)* | **1** *(5.9%)* | ⚽ `sport_football` (1) | *"video highlight bóng đá mới nhất"* | *"Không thấy video highlight bóng đá sau nhiều lần next, tìm kiếm trực tiếp để xem nội dung phù hợp..."* | Hành vi bộc phát khi Newsfeed thiếu hụt nội dung giải trí thể thao ngắn hạn. |
| **`vn_fb_002`** *(Gia đình Nghệ An)* | **0** *(0.0%)* | *(Không phát sinh)* | *(Không tìm kiếm)* | *(Tiếp nhận thụ động nội dung gia đình, tâm linh có sẵn trên feed)* | Tâm lý người dùng lớn tuổi: hoàn toàn thỏa mãn với bảng tin gợi ý, không có nhu cầu tra cứu từ khóa mở rộng. |

* **BẢNG 2: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI VIẾT BÌNH LUẬN (`COMMENT` — 35 LƯỢT)**

| Persona | Số Lượt (% Hành Vi) | Động Lực Chi Phối Hàng Đầu | Ngữ Điệu & Phong Cách Ngôn Ngữ | Trích Dẫn Chain-of-Thought (CoT) Nguyên Văn | Phân Tích Mục Đích Thực Sự |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **`vn_fb_003`** *(Bảo vệ Đà Nẵng)* | **18** *(51.4%)* | 🍢 `street_food` (9)<br>🍜 `cuisine_vn` (5)<br>💬 `social_eng` (4) | Thân mật, dùng từ lóng Gen Z, hỏi địa chỉ giòn giã | *"Bài review tokbokki phomai hấp dẫn, muốn hỏi địa chỉ quán. Giọng thẳng thắn, dùng từ lóng và emoji thanh niên..."* | Chiếm hơn một nửa số comment toàn mạng; mục đích hỏi địa chỉ ăn uống và kết nối cộng đồng bằng ngôn ngữ đường phố. |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **12** *(34.3%)* | 🇻🇳 `value_tradition` (11)<br>💻 `technology` (1) | Trang nghiêm, triân sâu sắc, tự hào dân tộc | *"Bài viết về Đại tướng Võ Nguyên Giáp và chiến thắng lịch sử rất ý nghĩa, muốn bày tỏ tri ân..."* | Viết bình luận tri ân công ơn tiền nhân; động lực truyền thống có tỷ lệ chuyển hóa thành bình luận cao nhất hệ thống. |
| **`vn_fb_001`** *(Thiết kế đồ họa TP.HCM)* | **3** *(8.6%)* | 🎨 `career_role` (2)<br>🧠 `curiosity` (1) | Chuyên nghiệp, nhã nhặn, góp ý kỹ thuật | *"Góp ý về góc phối cảnh 3D và bố cục ánh sáng trong bài thiết kế nội thất, trao đổi chuyên môn..."* | Trao đổi nghiệp vụ thiết kế; bình luận mang tính đóng góp giá trị chuyên môn trí thức. |
| **`vn_fb_006`** *(Gen X BĐS Cần Thơ)* | **1** *(2.9%)* | 💼 `real_estate` (1) | Thẳng thắn miền Tây, hỏi giá cụ thể | *"Đang xem căn hộ Cara River Park tại Cần Thơ. Muốn xem video thực tế và hỏi rõ về giá để cân nhắc..."* | Hỏi giá giao dịch thực tế dự án BĐS; bình luận mang tính thẩm định thương mại. |
| **`vn_fb_002`** *(Gia đình Nghệ An)* | **1** *(2.9%)* | 🌸 `tone` (1) | Đôn hậu, từ tốn, chúc an lành | *"Bình luận tích cực chúc mọi người mạnh khỏe, phù hợp với tính cách đôn hậu..."* | Gửi lời chúc phúc bình an đến cộng đồng; giữ thái độ thiện lương của người phụ nữ gia đình. |
| **`vn_fb_004`** *(Phục vụ trẻ TP.HCM)* | **0** *(0.0%)* | *(Không phát sinh)* | *(Không bình luận)* | *(Chỉ xem video giải trí thụ động, không tham gia tranh luận)* | Người xem video ngắn thuần túy; ngại viết chữ và chỉ tương tác bằng cử chỉ lướt. |

### 3. Lời thoại Thuyết trình của Người nói (Speaker Script)
> *"Thưa Hội đồng,
> 
> Bắt đầu đi vào cặp hành vi chủ động đầu tiên tại Slide 2.5.1: **Tìm kiếm (`SEARCH`) và Viết bình luận (`COMMENT`)**. Đây là hai hành vi đòi hỏi nỗ lực nhận thức cao nhất của Agent — bởi họ phải tự mình gõ chữ thay vì chỉ bấm nút có sẵn.
> 
> Tại Bảng 1 về hành vi **Tìm kiếm (17 lượt)**:
> - Người tìm kiếm tích cực nhất là anh thợ cơ khí `vn_fb_005` chiếm tới 52.9% (9 lượt). Anh tìm kiếm vì động lực tò mò khoa học: khi Newsfeed chưa có, anh chủ động gõ tìm *'thời điểm ngắm Sao Hỏa đối lập tại Đà Nẵng'*.
> - Bác `006` tìm kiếm có mục đích đầu tư thực dụng: gõ từ khóa *'quy hoạch Nam Cần Thơ'* và *'giá đất Cái Răng'*.
> - Cô bạn thiết kế `001` tìm công cụ *'AI thiết kế kiến trúc'* phục vụ công việc.
> - Anh bảo vệ `003` tìm *'quán bún trộn Đà Nẵng'* cho ca trực đêm.
> - Cậu phục vụ trẻ `004` tìm *'video highlight bóng đá'* khi lướt mãi không thấy.
> - Còn chị `002` hoàn toàn không tìm kiếm — chị bằng lòng với nội dung gia đình trên feed.
> 
> Chuyển sang Bảng 2 về hành vi **Viết bình luận (35 lượt)**, tính cách nhân vật bộc lộ rực rỡ qua từng câu chữ:
> - Anh bảo vệ `003` dẫn đầu áp đảo với 18 lượt comment (chiếm 51.4% toàn mạng). Anh vào các bài review tokbokki, hỏi địa chỉ bằng từ lóng và emoji thanh niên cực kỳ sinh động.
> - Trong khi đó, anh thợ `005` chiếm 34.3% (12 lượt comment) nhưng với một tâm thế hoàn toàn khác: 11 lần là bình luận tri ân trang nghiêm dưới các bài viết về Đại tướng Võ Nguyên Giáp và lịch sử dân tộc.
> - Cô bạn `001` chỉ comment góp ý về góc phối cảnh 3D; bác `006` hỏi thẳng giá bán căn hộ Cara River Park; và chị `002` gửi lời chúc sức khỏe bình an.
> 
> Hai bảng đối sánh này chứng minh: **Cùng là gõ phím, nhưng mục đích thúc đẩy và ngôn ngữ của 6 Persona hoàn toàn khác biệt, phản ánh trung thực căn tính từng người**."*

### 4. Lời thoại Chuyển tiếp sang Slide kế tiếp
> *"Chúng ta đã thấy sự phân hóa sâu sắc trong các hành vi chủ động gõ phím. Vậy đối với hành vi tiếp nhận văn bản — nơi Agent thẩm định thông tin để đọc sâu hoặc mở rộng bài viết, sự phân hóa đó diễn ra như thế nào? Xin mời Hội đồng cùng đến với Slide 2.5.2 về `READ` và `EXPAND`."*

---

## 🖥️ SLIDE 2.5.2: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI THẨM ĐỊNH VĂN BẢN (`READ` & `EXPAND`)

### 1. Hình ảnh Trực quan Slide
![Đối sánh Động lực Hành vi Thẩm định Văn bản](../output/figures/slide2_5_2_read_and_expand.png)

### 2. Nội dung Trình chiếu trên Slide
* **Tiêu đề:** ĐỐI SÁNH ĐỘNG LỰC HÀNH VI THẨM ĐỊNH VĂN BẢN: `READ` & `EXPAND`
* **Thông điệp cốt lõi:** `READ` là xương sống tiếp nhận thông tin chiếm 54.8% toàn hệ thống (178 lượt), trong khi `EXPAND` ("Xem thêm" - 20 lượt) là bộ lọc nhận thức khắt khe phản ánh mức độ tò mò vượt ngưỡng; 6 Persona bộc lộ sự tương phản sâu sắc giữa đọc tư duy logic, thẩm định đầu tư thực dụng, đắm chìm lịch sử và lướt tin vắn đời thường.

* **BẢNG 1: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI ĐỌC SÂU TUYỂN CHỌN (`READ` — 178 LƯỢT)**

| Persona | Số Lượt (% Hành Vi) | Động Lực Chi Phối Hàng Đầu | Chủ Đề Đọc Sâu Trọng Tâm | Trích Dẫn Chain-of-Thought (CoT) Nguyên Văn | Phân Tích Mục Đích Thực Sự |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **`vn_fb_001`** *(Thiết kế đồ họa TP.HCM)* | **52** *(29.2%)* | 🧠 `curiosity` (36)<br>💼 `real_estate` (13)<br>🎨 `career_role` (3) | Cờ vua logic, thế cờ hiểm, xu hướng kiến trúc & giá đất | *"Bài viết về cờ vua với tiêu đề gợi sự tò mò, phù hợp tính cách khám phá và trò chơi tư duy..."* | Đọc sâu duy lý: rèn luyện trí tuệ, tìm cảm hứng sáng tạo đồ họa và theo dõi thị trường BĐS. |
| **`vn_fb_006`** *(Gen X BĐS Cần Thơ)* | **43** *(24.2%)* | 💼 `real_estate` (15)<br>🧠 `curiosity` (15)<br>📿 `spirituality` (5)<br>🌿 `value_health` (4) | Căn hộ Cái Răng 8.5tr, pháp lý dự án, sức khỏe thực dưỡng | *"Bài đăng về căn hộ tại Quận Cái Răng, Cần Thơ với giá 8.5 triệu/tháng. Cần đọc chi tiết để hiểu giá cả..."* | Tỷ lệ đọc sâu cao nhất hệ thống (72.9%): thẩm định kỹ lưỡng giá trị thương mại, dòng tiền và dưỡng sinh trung niên. |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **29** *(16.3%)* | 🧠 `curiosity` (20)<br>🇻🇳 `value_tradition` (9) | Ký ức chiến hào Điện Biên, "Chuyện 10 năm", thiên văn | *"Bài viết 'Chuyện 10 năm' và ký ức chiến hào Điện Biên, nội dung hào hùng thôi thúc đọc từng chữ..."* | Đọc sâu để nuôi dưỡng lòng tự hào dân tộc và trau dồi tri thức khoa học kỹ thuật. |
| **`vn_fb_003`** *(Bảo vệ Đà Nẵng)* | **23** *(12.9%)* | 🍜 `cuisine_vn` (9)<br>🧠 `curiosity` (4)<br>🍢 `street_food` (4)<br>👥 `group_comm` (3) | Review quán bún mắm, bí quyết nấu ăn, đời sống đường phố | *"Bài review đồ ăn Việt, hợp sở thích ẩm thực. Muốn xem chi tiết và địa chỉ quán bún mắm..."* | Đọc để tìm kiếm địa chỉ ăn uống thực tế, thỏa mãn sở thích ẩm thực bình dân trong giờ nghỉ. |
| **`vn_fb_002`** *(Gia đình Nghệ An)* | **21** *(11.8%)* | 🌸 `tone` (13)<br>🏡 `parenting_family` (3)<br>🧠 `curiosity` (2)<br>💖 `emotional_exp` (2) | Viện dưỡng lão quá tải, chăm sóc cha mẹ già, chuyện thiện nguyện | *"Bài về dưỡng lão công lập quá tải liên quan đến chăm sóc người cao tuổi trong gia đình, muốn đọc để hiểu tình hình..."* | Đọc chậm rãi các vấn đề gia đình, đạo hiếu phụng dưỡng cha mẹ và các câu chuyện nhân văn ấm áp. |
| **`vn_fb_004`** *(Phục vụ trẻ TP.HCM)* | **10** *(5.6%)* | 🧠 `curiosity` (3)<br>📱 `content_format` (3)<br>⚽ `sport_football` (3)<br>⏱️ `reading_freq` (1) | Hành trình đi bộ Anh - Việt, tin chuyển nhượng bóng đá | *"Bài viết về hành trình đi bộ từ Anh đến Việt Nam, gợi tò mò muốn lướt đọc nội dung ngắn trước khi tiếp tục..."* | Đọc lướt tin vắn, cập nhật nhanh thông tin thể thao trước khi chuyển tiếp sang video giải trí. |

* **BẢNG 2: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI MỞ RỘNG BÀI VIẾT BỊ ẨN (`EXPAND` — 20 LƯỢT)**

| Persona | Số Lượt (% Hành Vi) | Động Lực Chi Phối Hàng Đầu | Lý Do Bấm "Xem Thêm" | Trích Dẫn Chain-of-Thought (CoT) Nguyên Văn | Phân Tích Mục Đích Thực Sự |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **11** *(55.0%)* | 🧠 `curiosity` (10)<br>🇻🇳 `value_tradition` (1) | Muốn đọc trọn vẹn văn bản dài về phân tích chiến dịch lịch sử & khoa học | *"Văn bản dài phân tích chiến dịch lịch sử bị ẩn đi, tò mò muốn đọc trọn vẹn bối cảnh và diễn biến nên bấm Xem thêm..."* | Bấm "Xem thêm" nhiều nhất toàn mạng (55%); khao khát tiếp cận tri thức toàn vẹn, không chấp nhận thông tin đứt đoạn. |
| **`vn_fb_001`** *(Thiết kế đồ họa TP.HCM)* | **7** *(35.0%)* | 🧠 `curiosity` (6)<br>💼 `real_estate` (1) | Tìm hiểu chi tiết bài viết công nghệ mới và phân tích tư duy bị cắt ngắn | *"Bài viết về Taekwondo ứng dụng công nghệ thực tế ảo VR bị cắt ngắn; bấm Xem thêm để tìm hiểu chi tiết ứng dụng..."* | Đọc sâu bài toán logic và ứng dụng công nghệ đồ họa/VR đòi hỏi nội dung văn bản dài. |
| **`vn_fb_004`** *(Phục vụ trẻ TP.HCM)* | **1** *(5.0%)* | 📱 `content_format` (1) | Tò mò cái kết của câu chuyện du ký mạo hiểm | *"Bài viết hành trình đi bộ Anh - Việt có phần kết bị ẩn; bấm Xem thêm để xem kết cục câu chuyện..."* | Tò mò tức thời về hồi kết câu chuyện phiêu lưu kỳ thú. |
| **`vn_fb_002`** *(Gia đình Nghệ An)* | **1** *(5.0%)* | 📿 `spirituality` (1) | Đọc trọn vẹn đoạn kinh chú tâm linh | *"Bài giảng về Phật mẫu Chuẩn Đề có đoạn kệ chú bị thu gọn; bấm Xem thêm để đọc trọn lời răn..."* | Tâm niệm tôn kính, muốn đọc trọn vẹn câu kệ kinh Phật. |
| **`vn_fb_003`** *(Bảo vệ Đà Nẵng)* | **0** *(0.0%)* | *(Không phát sinh)* | *(Chỉ xem tiêu đề và ảnh)* | *(Lướt nhanh điện thoại, không kiên nhẫn mở bài dài)* | Thói quen lướt nhanh bằng một tay trong ca trực; bài viết dài bị ẩn sẽ bị bỏ qua. |
| **`vn_fb_006`** *(Gen X BĐS Cần Thơ)* | **0** *(0.0%)* | *(Không phát sinh)* | *(Chỉ đọc tin có sẵn)* | *(Ưa chuộng tin BĐS súc tích, hiển thị giá ngay)* | Thực dụng và quyết đoán: tin rao BĐS chuẩn mực phải có giá ngay trên feed, không click xem thêm các bài dài dòng. |

### 3. Lời thoại Thuyết trình của Người nói (Speaker Script)
> *"Kính thưa quý thầy cô,
> 
> Tiến sang cặp hành vi thứ hai tại Slide 2.5.2: **Đọc sâu (`READ`) và Mở rộng bài viết (`EXPAND`)**, chúng ta chứng kiến sự phân hóa ngoạn mục trong cách mà 6 bộ óc này xử lý văn bản:
> 
> Ở Bảng 1 về **Đọc sâu (178 lượt — chiếm 54.8% toàn hệ thống)**:
> - Cô bạn thiết kế `vn_fb_001` dẫn đầu về số lượt đọc (52 bài). Cô bị thu hút bởi các thế cờ vua hiểm hóc và bài phân tích kiến trúc — nơi kích thích mạnh mẽ tư duy logic và thẩm mỹ.
> - Bác doanh nhân `vn_fb_006` có tỷ trọng đọc sâu cao nhất toàn mạng (72.9% hành vi của bác). Bác dừng lại đọc từng con số: từ căn hộ Cái Răng giá 8.5 triệu đến quy hoạch đất đai, thể hiện sự cẩn trọng tối đa của một nhà đầu tư lớn tuổi.
> - Anh thợ `005` đắm chìm vào các bài ký ức chiến hào Điện Biên Phủ, đọc từng dòng chữ lịch sử hào hùng.
> - Anh bảo vệ `003` đọc kỹ địa chỉ các quán bún mắm, quán ăn đêm để phục vụ sở thích ẩm thực.
> - Chị phụ nữ gia đình `002` đọc bài về viện dưỡng lão quá tải với sự trăn trở của người con có cha mẹ già.
> - Và cậu thanh niên `004` chỉ đọc lướt các tin vắn thể thao ngắn trước khi xem video.
> 
> Sự phân hóa càng trở nên kịch tính ở Bảng 2 với hành vi **Mở rộng ("Xem thêm" `EXPAND` — 20 lượt)**:
> - Nút 'Xem thêm' là một bộ lọc nhận thức khắt khe: người dùng chỉ click khi bài viết thực sự thôi thúc họ vượt qua rào cản lười biếng.
> - Và ở đây, anh thợ cơ khí `005` chiếm tới 55% toàn mạng (11 lượt), cùng với cô thiết kế `001` chiếm 35% (7 lượt). Hai nhân vật trí thức và kỹ thuật này khao khát tiếp cận thông tin toàn vẹn, không chấp nhận việc kiến thức khoa học hay tư liệu lịch sử bị cắt ngắn.
> - Trong khi đó, anh bảo vệ `003` và bác doanh nhân `006` đạt con số 0 tròn trĩnh: anh bảo vệ lướt nhanh điện thoại nên ngại bài dài; còn bác doanh nhân chỉ ưa chuộng các tin rao BĐS súc tích có giá sẵn, không click vào những bài dài dòng rườm rà.
> 
> Rõ ràng, **việc đọc sâu hay mở rộng bài không hề ngẫu nhiên, mà tuân thủ chặt chẽ nguyên tắc nhận thức và thói quen tiêu thụ thông tin của từng cá nhân**."*

### 4. Lời thoại Chuyển tiếp sang Slide kế tiếp
> *"Sau khi đã khảo sát các hành vi xử lý văn bản duy lý, chúng ta hãy cùng bước sang góc nhìn giàu cảm xúc và tính lan tỏa xã hội nhất: Thả cảm xúc (`REACT`) và Chia sẻ (`SHARE`) tại Slide 2.5.3."*

---

## 🖥️ SLIDE 2.5.3: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CẢM XÚC & LAN TỎA (`REACT` & `SHARE`)

### 1. Hình ảnh Trực quan Slide
![Đối sánh Động lực Hành vi Cảm xúc & Lan tỏa](../output/figures/slide2_5_3_react_and_share.png)

### 2. Nội dung Trình chiếu trên Slide
* **Tiêu đề:** ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CẢM XÚC & LAN TỎA: `REACT` & `SHARE`
* **Thông điệp cốt lõi:** Thả cảm xúc (`REACT` - 74 lượt) là chỉ báo trực tiếp cho sự đồng điệu tâm lý bộc phát, trong khi Chia sẻ (`SHARE` - 1 lượt) là hành vi cực kỳ quý hiếm với rào cản xã hội rất cao; 6 Persona bộc lộ sự phân cực mạnh mẽ giữa biểu đạt tâm linh thiện lương, tán thưởng vẻ đẹp trí tuệ, bộc phát thể thao và tâm lý bảo toàn không gian cá nhân.

* **BẢNG 1: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI THẢ CẢM XÚC (`REACT` — 74 LƯỢT)**

| Persona | Số Lượt (% Hành Vi) | Động Lực Chi Phối Hàng Đầu | Đối Tượng Nội Dung Kích Hoạt Like / Tim | Trích Dẫn Chain-of-Thought (CoT) Nguyên Văn | Phân Tích Mục Đích Thực Sự |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **`vn_fb_001`** *(Thiết kế đồ họa TP.HCM)* | **19** *(25.7%)* | 🧠 `curiosity` (8)<br>💼 `real_estate` (5)<br>🎨 `career_role` (2)<br>💻 `technology` (2) | Thế cờ thế hiểm mate in 2, bản vẽ kiến trúc tinh tế, nhà đẹp | *"Bài toán mate in 2 thú vị, phù hợp với tính cách thích thử thách. Thả cảm xúc tán thưởng..."* | Tán thưởng vẻ đẹp trí tuệ, giải pháp đồ họa xuất sắc và cơ hội BĐS tiềm năng. |
| **`vn_fb_002`** *(Gia đình Nghệ An)* | **19** *(25.7%)* | 📿 `spirituality` (7)<br>💖 `emotional_exp` (5)<br>📍 `province` (3)<br>🏡 `parenting_family` (3) | Tượng Bồ tát Quán Thế Âm 33m sông Tiền, đền Hoàng Mười Nghệ An | *"Hình ảnh tượng 33m hướng sông Tiền gợi cảm giác bình an. Thả like tôn trọng và kết nối tâm linh..."* | Biểu đạt đức tin tâm linh thành kính, cầu chúc gia đạo an lành và thể hiện tình yêu quê hương xứ Nghệ. |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **12** *(16.2%)* | 🧠 `curiosity` (11)<br>🇻🇳 `value_tradition` (1) | Chân dung Đại tướng Võ Nguyên Giáp, ảnh trăng sao Đà Nẵng | *"Bức ảnh Đại tướng Võ Nguyên Giáp tại Điện Biên Phủ, thả like tri ân công ơn tiền nhân; thả like ảnh thiên văn..."* | Tri ân sâu sắc công ơn tiền nhân và bày tỏ sự khâm phục trước các hiện tượng khoa học kỳ thú. |
| **`vn_fb_006`** *(Gen X BĐS Cần Thơ)* | **12** *(16.2%)* | 🧠 `curiosity` (4)<br>💼 `real_estate` (4)<br>📿 `spirituality` (2)<br>🌿 `value_health` (1) | Vườn trái cây miền Tây 25k/kg, tin rao nhà đất Cần Thơ, thực dưỡng | *"Hình ảnh vườn trái cây miền Tây 25k/kg và nhà phố Cần Thơ giá tốt; thả like lưu lại mối quan tâm..."* | Đánh dấu thông tin sinh kế Nam Bộ thực dụng, nông sản giá tốt và cơ hội tài sản đáng tin cậy. |
| **`vn_fb_004`** *(Phục vụ trẻ TP.HCM)* | **9** *(12.2%)* | ⚽ `sport_football` (6)<br>📱 `content_format` (3) | Dembele bỏ lỡ cơ hội, pha bóng hài hước, video bàn thắng | *"Tình huống bóng đá thú vị, Dembele lỡ cơ hội ngon ăn. Thích xem thêm highlight nên thả cảm xúc tương tác..."* | Cảm xúc bộc phát tức thì trước các pha bóng đá kịch tính và video giải trí ngắn. |
| **`vn_fb_003`** *(Bảo vệ Đà Nẵng)* | **3** *(4.1%)* | 🍢 `street_food` (2)<br>🍜 `cuisine_vn` (1) | Đĩa cá rô đồng muối sả giòn rụm, món ăn bình dân miền Trung | *"Món cá rô đồng muối sả chiên giòn quá bắt mắt; thả tim ủng hộ ẩm thực dân dã..."* | Tương tác chọn lọc khắt khe; tiết kiệm nút like và chỉ thả tim khi món ăn thực sự kích thích vị giác (ưu tiên bình luận). |

* **BẢNG 2: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CHIA SẺ BÀI VIẾT (`SHARE` — 1 LƯỢT)**

| Persona | Số Lượt (% Hành Vi) | Động Lực Chi Phối | Nội Dung Bài Viết Được Chia Sẻ | Trích Dẫn Chain-of-Thought (CoT) Nguyên Văn | Phân Tích Mục Đích Thực Sự |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **1** *(100.0%)* | 🧠 `curiosity` (1) | Hiện tượng thiên văn Sao Hỏa đối lập hiếm gặp tại Đà Nẵng | *"Sự kiện thiên văn hấp dẫn, muốn chia sẻ và hỏi kinh nghiệm từ cộng đồng địa phương."* | Động lực kết nối cộng đồng tri thức lên đến đỉnh điểm; muốn lưu lại trên dòng thời gian để thảo luận với hội thiên văn. |
| **`vn_fb_001, 002, 003, 004, 006`** | **0** *(0.0%)* | *(Không phát sinh)* | *(Không chia sẻ)* | *(Không phát sinh nhu cầu chia sẻ công khai lên trang cá nhân)* | **Phản ánh chuẩn mực tâm lý mạng xã hội hiện đại:** E ngại làm rác dòng thời gian của bạn bè, giữ kín không gian riêng tư và tránh phán xét xã hội. |

### 3. Lời thoại Thuyết trình của Người nói (Speaker Script)
> *"Kính thưa Hội đồng,
> 
> Chúng ta khép lại phân đoạn 2.5 với cặp hành vi cảm xúc và lan tỏa xã hội tại Slide 2.5.3: **Thả cảm xúc (`REACT`) và Chia sẻ bài viết (`SHARE`)**.
> 
> Nhìn vào Bảng 1 về hành vi **Thả cảm xúc (74 lượt)**, chúng ta thấy hai đỉnh cao tương tác thuộc về hai thế giới tâm lý hoàn toàn trái ngược:
> - Một đỉnh cao là cô gái thiết kế `vn_fb_001` (19 lượt — 25.7%): Cô like vì sự tán thưởng vẻ đẹp trí tuệ — một thế cờ thế hiểm, một phối cảnh 3D tinh gọn, hay một góc nhìn BĐS sắc sảo.
> - Đỉnh cao tương đương là chị phụ nữ gia đình `vn_fb_002` (19 lượt — 25.7%): Nhưng chị thả tim vì sự thành kính tâm linh và đạo hiếu — tượng Bồ tát Quán Thế Âm 33m hướng sông Tiền, đền Hoàng Mười Nghệ An, và những lời răn bình an gia đình.
> - Bác doanh nhân `006` like vườn trái cây miền Tây 25k và nhà đất Cái Răng; anh thợ `005` like tri ân Đại tướng Giáp; cậu thanh niên `004` thả haha cho pha bóng Dembele bỏ lỡ; còn anh bảo vệ `003` thì cực kỳ tiết kiệm nút like (chỉ 3 lượt) vì anh dành trọn tâm sức cho việc viết comment.
> 
> Và cuối cùng, hãy nhìn vào Bảng 2 với hành vi **Chia sẻ (`SHARE` — duy nhất 1 lượt)**:
> - Toàn bộ 5 Persona còn lại đều không chia sẻ bất cứ bài viết nào. Đây là một phát hiện cực kỳ chân thực: Trên mạng xã hội ngày nay, nút Share có rào cản tâm lý rất lớn. Người dùng không muốn làm phiền bạn bè, không muốn lộ quan điểm cá nhân, và có xu hướng giữ kín dòng thời gian của mình.
> - Lượt chia sẻ duy nhất thuộc về anh thợ cơ khí `vn_fb_005`: Khi gặp bài viết về hiện tượng Sao Hỏa đối lập tại Đà Nẵng, lòng say mê thiên văn và mong muốn hỏi kinh nghiệm từ cộng đồng địa phương đã vượt qua rào cản e ngại, thúc đẩy anh chia sẻ bài viết lên trang cá nhân.
> 
> Thưa Hội đồng, qua cả 4 slide vừa rồi (từ 2.5 đến 2.5.3), chúng tôi đã chứng minh một cách tường minh và thuyết phục: **Mỗi hành động của Agent đều có nguyên do thúc đẩy xác thực, và sự phân hóa động lực giữa 6 Persona là hoàn toàn chân thực, sống động như con người ngoài đời thực**."*

### 4. Lời thoại Chuyển tiếp sang Slide kế tiếp
> *"Một phiên lướt mạng có nhận thức sâu sắc và động lực phong phú như vậy là rất ấn tượng. Nhưng qua các ngày khác nhau, các phiên khác nhau, liệu Agent có nhớ những gì mình đã đọc hôm qua và duy trì được mạch quan tâm hay không? Hãy cùng đến với Slide 2.6 về Trí nhớ xuyên phiên."*

---"""

content = content[:start_idx] + slide_replacement + content[end_idx:]

# 3. Update Master Transitions
old_transitions = """```mermaid
flowchart TD
    M0["MỞ MÀN (Slide 0)"] -->|"Cầu nối 1: Người thật hay máy? Nhịp sinh học 24h ra sao?"| S11["SLIDE 1.1: 4 Khung giờ 24h"]
    S11 -->|"Cầu nối 2: Biết khung giờ rồi, vậy một ngày vào mấy lần, mỗi lần bao lâu?"| S12["SLIDE 1.2: Tần suất & Thời lượng"]
    S12 -->|"Cầu nối 3: H1 ĐẠT! Nhưng khi màn hình mở ra, họ lướt đi đâu?"| S21["SLIDE 2.1: Phân bổ Bề mặt Surface"]
    S21 -->|"Cầu nối 4: Đến đúng chỗ rồi, họ tương tác thế nào? Like hay Comment?"| S22["SLIDE 2.2: Cường độ Tương tác"]
    S22 -->|"Cầu nối 5: Tương tác vậy họ có thực sự đọc bài không hay chỉ lướt qua?"| S23["SLIDE 2.3: Scanning vs Deep Reading"]
    S23 -->|"Cầu nối 6: Đọc sâu rồi, vậy ngón tay họ cuộn màn hình ra sao?"| S24["SLIDE 2.4: Động lực học Cuộn"]
    S24 -->|"Cầu nối 7: Cuộn dừng lại, điều gì trong tâm trí thúc đẩy họ hành động?"| S25["SLIDE 2.5: Căn cứ Nhận thức Vĩ mô"]
    S25 -->|"Cầu nối 8: Nhận thức từng phiên rồi, qua nhiều ngày họ có nhớ mạch tư duy?"| S26["SLIDE 2.6: Trí nhớ Xuyên phiên"]
    S26 -->|"Cầu nối 9: Nhớ mạch tư duy, họ hình thành chuỗi thói quen 3 bước nào?"| S27["SLIDE 2.7: Chuỗi Hành vi 3 Bước"]
    S27 -->|"Cầu nối 10: Chuỗi thao tác vậy, tiền đề trực tiếp kích hoạt Like & Comment là gì?"| S28["SLIDE 2.8: Giải mã Tiền đề Tương tác"]
    S28 -->|"Cầu nối 11: Toàn bộ H1 & H2 được chứng minh, tổng kết lại điều gì?"| S30["SLIDE 3.0: Nghiệm thu & Ứng dụng"]
```

### 1. Cầu nối Mở màn $\longrightarrow$ Slide 1.1 (Từ Giới thiệu bài toán đến Bức tranh 24 giờ)
> *"Kính thưa Hội đồng, để trả lời câu hỏi các AI Agent này hành xử có giống người thật hay không, phép thử đầu tiên và trực quan nhất chính là chiếc đồng hồ sinh học: Liệu họ có biết lúc nào cần online, lúc nào phải nghỉ ngơi theo đúng công việc của mình? Chúng ta hãy cùng nhìn vào Bức tranh 4 khung giờ sinh hoạt 24h tại Slide 1.1."*

### 2. Cầu nối Slide 1.1 $\longrightarrow$ Slide 1.2 (Từ Khung giờ sang Tần suất & Thời lượng phiên)
> *"Chúng ta đã thấy các nhân vật phân chia ca sáng, trưa, tối rất khớp với công việc. Nhưng câu hỏi đặt ra tiếp theo là: Mỗi ngày họ cầm điện thoại lên bao nhiêu lần? Và mỗi lần lướt trong bao lâu? Liệu người bận rộn việc nhà có ngồi lâu như cậu thanh niên rảnh rỗi hay không? Chúng ta hãy cùng đến với Slide 1.2."*

### 3. Cầu nối Slide 1.2 $\longrightarrow$ Slide 2.1 (Chốt Giả thuyết $H_1$, Mở màn Giả thuyết $H_2$)
> *"Như vậy, Giả thuyết $H_1$ đã được kiểm chứng xuất sắc: Agent có nhịp sinh hoạt và thời lượng chuẩn mực đời thực. Nhưng một câu hỏi lớn hơn mở ra: Khi giao diện Facebook đã sáng lên, họ sẽ đi về đâu? Họ vào Bảng tin, xem Video ngắn hay tìm đến các Hội nhóm? Hãy cùng bước vào Tầng 2 ($H_2$) với góc nhìn không gian bề mặt tại Slide 2.1."*

### 4. Cầu nối Slide 2.1 $\longrightarrow$ Slide 2.2 (Từ Bề mặt không gian sang Cường độ tương tác)
> *"Mỗi Persona đã chọn cho mình một sân chơi riêng: người ở Reels, người ở Group, người ở Feed. Vậy khi đứng trước nội dung, họ phản ứng như thế nào? Họ thả tim, để lại bình luận hay chỉ âm thầm quan sát? Mời quý vị cùng khám phá phong cách tương tác tại Slide 2.2."*

### 5. Cầu nối Slide 2.2 $\longrightarrow$ Slide 2.3 (Từ Cường độ tương tác sang Độ sâu đọc bài)
> *"Những con số tương tác đã bộc lộ rõ cá tính. Tuy nhiên, một hội đồng khoa học chắc chắn sẽ đặt câu hỏi: Liệu Agent có thực sự đọc nội dung bài viết hay chỉ nhìn lướt qua tiêu đề rồi bấm bừa? Tỷ lệ giữa việc đọc sâu và quét nhanh tại Slide 2.3 sẽ làm sáng tỏ điều này."*

### 6. Cầu nối Slide 2.3 $\longrightarrow$ Slide 2.4 (Từ Đọc sâu sang Động lực học vuốt cuộn)
> *"Sự phân hóa về thời gian đọc bài là rất rõ nét. Nhưng bên cạnh nhịp độ nhận thức, cử chỉ vật lý của ngón tay khi vuốt màn hình cũng mang đậm dấu ấn phong cách: Người vuốt mạnh dứt khoát, người cuộn ngắn dè dặt, người dừng lại đọc chậm. Hãy cùng kiểm chứng Động lực học cuộn trang tại Slide 2.4."*

### 7. Cầu nối Slide 2.4 $\longrightarrow$ Slide 2.5 (Từ Thao tác cuộn sang Căn cứ nhận thức vĩ mô)
> *"Thao tác vuốt cuộn màn hình đã thể hiện rõ tác phong nhân vật. Nhưng điều gì ẩn sâu bên trong suy nghĩ đã thúc đẩy họ dừng tay và quyết định tương tác? Hãy cùng mở chiếc hộp đen tư duy với 4 trụ cột căn cứ nhận thức tại Slide 2.5."*

### 8. Cầu nối Slide 2.5 $\longrightarrow$ Slide 2.6 (Từ Nhận thức trong phiên sang Trí nhớ xuyên phiên)
> *"Chúng ta đã thấy các suy luận nhận thức trong từng phiên hoạt động rất sống động. Nhưng một con người thực sự không bao giờ bắt đầu mỗi ngày như một trang giấy trắng. Họ phải nhớ những gì mình đã đọc hôm qua và tiếp tục sở thích của mình. Liệu Agent có làm được điều đó? Slide 2.6 về Trí nhớ xuyên phiên sẽ trả lời câu hỏi này."*

### 9. Cầu nối Slide 2.6 $\longrightarrow$ Slide 2.7 (Từ Trí nhớ xuyên phiên sang Chuỗi hành vi 3 bước)
> *"Sự liền mạch của trí nhớ đã hình thành nên những thói quen lặp lại bền vững. Khi xâu chuỗi 3 thao tác liên tiếp, mỗi nhân vật bộc lộ một chuỗi hành vi thương hiệu mang tính độc quyền cao. Mời quý vị cùng theo dõi các chuỗi 3 bước tại Slide 2.7."*

### 10. Cầu nối Slide 2.7 $\longrightarrow$ Slide 2.8 (Từ Chuỗi thao tác sang Tiền đề trực tiếp kích hoạt Like/Comment)
> *"Mỗi nhân vật đều có chuỗi hành động thương hiệu riêng. Nhưng đối với hai hành động xã hội quan trọng nhất là Thả cảm xúc và Viết bình luận, điều gì đã kích hoạt chúng ngay ở bước liền trước? Liệu có ai like mù quáng hay không? Chúng ta cùng giải mã tiền đề tương tác tại Slide 2.8."*

### 11. Cầu nối Slide 2.8 $\longrightarrow$ Slide 3.0 (Chốt Tầng 2, Tổng kết nghiệm thu & Ứng dụng thực tiễn)
> *"Thưa Hội đồng, toàn bộ 8 góc nhìn chuyên sâu của Tầng 2 đã kiểm chứng toàn diện Giả thuyết $H_2$. Giờ đây, chúng tôi xin trân trọng kính mời quý thầy cô cùng nhìn lại bảng nghiệm thu tổng thể và những giá trị ứng dụng thực tiễn của công trình tại Slide 3.0."*"""

new_transitions = """```mermaid
flowchart TD
    M0["MỞ MÀN (Slide 0)"] -->|"Cầu nối 1: Người thật hay máy? Nhịp sinh học 24h ra sao?"| S11["SLIDE 1.1: 4 Khung giờ 24h"]
    S11 -->|"Cầu nối 2: Biết khung giờ rồi, vậy một ngày vào mấy lần, mỗi lần bao lâu?"| S12["SLIDE 1.2: Tần suất & Thời lượng"]
    S12 -->|"Cầu nối 3: H1 ĐẠT! Nhưng khi màn hình mở ra, họ lướt đi đâu?"| S21["SLIDE 2.1: Phân bổ Bề mặt Surface"]
    S21 -->|"Cầu nối 4: Đến đúng chỗ rồi, họ tương tác thế nào? Like hay Comment?"| S22["SLIDE 2.2: Cường độ Tương tác"]
    S22 -->|"Cầu nối 5: Tương tác vậy họ có thực sự đọc bài không hay chỉ lướt qua?"| S23["SLIDE 2.3: Scanning vs Deep Reading"]
    S23 -->|"Cầu nối 6: Đọc sâu rồi, vậy ngón tay họ cuộn màn hình ra sao?"| S24["SLIDE 2.4: Động lực học Cuộn"]
    S24 -->|"Cầu nối 7: Cuộn dừng lại, điều gì trong tâm trí thúc đẩy họ hành động?"| S25["SLIDE 2.5: Tổng quan Ma trận Phân hóa Động lực"]
    S25 -->|"Cầu nối 8: Nhìn bức tranh chung rồi, hành vi chủ động gõ phím SEARCH & COMMENT phân hóa ra sao?"| S251["SLIDE 2.5.1: Đối sánh SEARCH & COMMENT"]
    S251 -->|"Cầu nối 9: Gõ phím chủ động đã rõ, còn hành vi thẩm định văn bản READ & EXPAND có gì khác biệt?"| S252["SLIDE 2.5.2: Đối sánh READ & EXPAND"]
    S252 -->|"Cầu nối 10: Đọc bài kỹ rồi, còn những tương tác cảm xúc bộc phát REACT & SHARE xuất phát từ đâu?"| S253["SLIDE 2.5.3: Đối sánh REACT & SHARE"]
    S253 -->|"Cầu nối 11: Động lực từng phiên đã chứng minh rõ nét, qua nhiều ngày họ có duy trì mạch tư duy?"| S26["SLIDE 2.6: Trí nhớ Xuyên phiên"]
    S26 -->|"Cầu nối 12: Nhớ mạch tư duy, họ hình thành chuỗi thói quen 3 bước nào?"| S27["SLIDE 2.7: Chuỗi Hành vi 3 Bước"]
    S27 -->|"Cầu nối 13: Chuỗi thao tác vậy, tiền đề trực tiếp kích hoạt Like & Comment là gì?"| S28["SLIDE 2.8: Giải mã Tiền đề Tương tác"]
    S28 -->|"Cầu nối 14: Toàn bộ H1 & H2 được chứng minh, tổng kết lại điều gì?"| S30["SLIDE 3.0: Nghiệm thu & Ứng dụng"]
```

### 1. Cầu nối Mở màn $\longrightarrow$ Slide 1.1 (Từ Giới thiệu bài toán đến Bức tranh 24 giờ)
> *"Kính thưa Hội đồng, để trả lời câu hỏi các AI Agent này hành xử có giống người thật hay không, phép thử đầu tiên và trực quan nhất chính là chiếc đồng hồ sinh học: Liệu họ có biết lúc nào cần online, lúc nào phải nghỉ ngơi theo đúng công việc của mình? Chúng ta hãy cùng nhìn vào Bức tranh 4 khung giờ sinh hoạt 24h tại Slide 1.1."*

### 2. Cầu nối Slide 1.1 $\longrightarrow$ Slide 1.2 (Từ Khung giờ sang Tần suất & Thời lượng phiên)
> *"Chúng ta đã thấy các nhân vật phân chia ca sáng, trưa, tối rất khớp với công việc. Nhưng câu hỏi đặt ra tiếp theo là: Mỗi ngày họ cầm điện thoại lên bao nhiêu lần? Và mỗi lần lướt trong bao lâu? Liệu người bận rộn việc nhà có ngồi lâu như cậu thanh niên rảnh rỗi hay không? Chúng ta hãy cùng đến với Slide 1.2."*

### 3. Cầu nối Slide 1.2 $\longrightarrow$ Slide 2.1 (Chốt Giả thuyết $H_1$, Mở màn Giả thuyết $H_2$)
> *"Như vậy, Giả thuyết $H_1$ đã được kiểm chứng xuất sắc: Agent có nhịp sinh hoạt và thời lượng chuẩn mực đời thực. Nhưng một câu hỏi lớn hơn mở ra: Khi giao diện Facebook đã sáng lên, họ sẽ đi về đâu? Họ vào Bảng tin, xem Video ngắn hay tìm đến các Hội nhóm? Hãy cùng bước vào Tầng 2 ($H_2$) với góc nhìn không gian bề mặt tại Slide 2.1."*

### 4. Cầu nối Slide 2.1 $\longrightarrow$ Slide 2.2 (Từ Bề mặt không gian sang Cường độ tương tác)
> *"Mỗi Persona đã chọn cho mình một sân chơi riêng: người ở Reels, người ở Group, người ở Feed. Vậy khi đứng trước nội dung, họ phản ứng như thế nào? Họ thả tim, để lại bình luận hay chỉ âm thầm quan sát? Mời quý vị cùng khám phá phong cách tương tác tại Slide 2.2."*

### 5. Cầu nối Slide 2.2 $\longrightarrow$ Slide 2.3 (Từ Cường độ tương tác sang Độ sâu đọc bài)
> *"Những con số tương tác đã bộc lộ rõ cá tính. Tuy nhiên, một hội đồng khoa học chắc chắn sẽ đặt câu hỏi: Liệu Agent có thực sự đọc nội dung bài viết hay chỉ nhìn lướt qua tiêu đề rồi bấm bừa? Tỷ lệ giữa việc đọc sâu và quét nhanh tại Slide 2.3 sẽ làm sáng tỏ điều này."*

### 6. Cầu nối Slide 2.3 $\longrightarrow$ Slide 2.4 (Từ Đọc sâu sang Động lực học vuốt cuộn)
> *"Sự phân hóa về thời gian đọc bài là rất rõ nét. Nhưng bên cạnh nhịp độ nhận thức, cử chỉ vật lý của ngón tay khi vuốt màn hình cũng mang đậm dấu ấn phong cách: Người vuốt mạnh dứt khoát, người cuộn ngắn dè dặt, người dừng lại đọc chậm. Hãy cùng kiểm chứng Động lực học cuộn trang tại Slide 2.4."*

### 7. Cầu nối Slide 2.4 $\longrightarrow$ Slide 2.5 (Từ Thao tác cuộn sang Tổng quan Ma trận Phân hóa Động lực & Nguyên tắc 1-1)
> *"Thao tác vuốt cuộn màn hình đã thể hiện rõ tác phong nhân vật. Nhưng điều gì ẩn sâu bên trong suy nghĩ đã thúc đẩy họ dừng tay và quyết định tương tác? Cơ chế nào quy định mỗi hành vi tập trung bắt buộc phải có 1 lý do chính qua chuỗi Chain-of-Thought, và ma trận động lực 6 Persona phản ánh bản sắc độc bản của từng người ra sao? Hãy cùng mở chiếc hộp đen tư duy tại Slide 2.5."*

### 8. Cầu nối Slide 2.5 $\longrightarrow$ Slide 2.5.1 (Từ Ma trận tổng quan sang Đối sánh Hành vi Gõ phím chủ động `SEARCH` & `COMMENT`)
> *"Chúng ta đã thấy bức tranh toàn cảnh về ma trận động lực toàn hệ thống. Giờ là lúc đi sâu giải phẫu 2 hành vi đòi hỏi nỗ lực nhận thức chủ động cao nhất — nơi Agent phải trực tiếp gõ phím tiếng Việt thay vì chỉ bấm nút: Tìm kiếm (`SEARCH`) và Viết bình luận (`COMMENT`). Sáu Persona đã bộc lộ mục đích thực sự và phong cách ngôn ngữ ra sao? Mời quý vị cùng theo dõi tại Slide 2.5.1."*

### 9. Cầu nối Slide 2.5.1 $\longrightarrow$ Slide 2.5.2 (Từ Gõ phím chủ động sang Đối sánh Thẩm định văn bản `READ` & `EXPAND`)
> *"Hành vi chủ động gõ phím đã bộc lộ rõ cá tính. Vậy đối với hành vi thẩm định nội dung văn bản — nơi Agent tiếp nhận thông tin chọn lọc để đọc sâu (`READ`) hoặc vượt qua rào cản lười biếng để bấm 'Xem thêm' (`EXPAND`), động lực thúc đẩy họ là gì? Mời Hội đồng cùng đến với Slide 2.5.2."*

### 10. Cầu nối Slide 2.5.2 $\longrightarrow$ Slide 2.5.3 (Từ Thẩm định văn bản sang Đối sánh Cảm xúc & Lan tỏa `REACT` & `SHARE`)
> *"Sau khi đã khảo sát các hành vi tiếp nhận văn bản duy lý, chúng ta hãy cùng bước sang góc nhìn giàu cảm xúc và tính lan tỏa xã hội nhất: Thả cảm xúc (`REACT`) và Chia sẻ (`SHARE`). Đâu là lý do khiến người thả tim đền chùa, người like cờ vua, và tại sao nút Share lại cực kỳ quý hiếm? Xin mời quý thầy cô cùng theo dõi tại Slide 2.5.3."*

### 11. Cầu nối Slide 2.5.3 $\longrightarrow$ Slide 2.6 (Từ Động lực trong phiên sang Trí nhớ xuyên phiên)
> *"Chúng ta đã thấy các suy luận nhận thức và động lực trong từng phiên hoạt động rất sống động, chân thực. Nhưng một con người thực sự không bao giờ bắt đầu mỗi ngày như một trang giấy trắng. Họ phải nhớ những gì mình đã đọc hôm qua và tiếp tục duy trì mạch quan tâm của mình. Liệu Agent có làm được điều đó? Slide 2.6 về Trí nhớ xuyên phiên sẽ trả lời câu hỏi này."*

### 12. Cầu nối Slide 2.6 $\longrightarrow$ Slide 2.7 (Từ Trí nhớ xuyên phiên sang Chuỗi hành vi 3 bước)
> *"Sự liền mạch của trí nhớ đã hình thành nên những thói quen lặp lại bền vững. Khi xâu chuỗi 3 thao tác liên tiếp, mỗi nhân vật bộc lộ một chuỗi hành vi thương hiệu mang tính độc quyền cao. Mời quý vị cùng theo dõi các chuỗi 3 bước tại Slide 2.7."*

### 13. Cầu nối Slide 2.7 $\longrightarrow$ Slide 2.8 (Từ Chuỗi thao tác sang Tiền đề trực tiếp kích hoạt Like/Comment)
> *"Mỗi nhân vật đều có chuỗi hành động thương hiệu riêng. Nhưng đối với hai hành động xã hội quan trọng nhất là Thả cảm xúc và Viết bình luận, điều gì đã kích hoạt chúng ngay ở bước liền trước? Liệu có ai like mù quáng hay không? Chúng ta cùng giải mã tiền đề tương tác tại Slide 2.8."*

### 14. Cầu nối Slide 2.8 $\longrightarrow$ Slide 3.0 (Chốt Tầng 2, Tổng kết nghiệm thu & Ứng dụng thực tiễn)
> *"Thưa Hội đồng, toàn bộ 8 góc nhìn chuyên sâu của Tầng 2 đã kiểm chứng toàn diện Giả thuyết $H_2$. Giờ đây, chúng tôi xin trân trọng kính mời quý thầy cô cùng nhìn lại bảng nghiệm thu tổng thể và những giá trị ứng dụng thực tiễn của công trình tại Slide 3.0."*"""

assert old_transitions in content, "Old Master Transitions not found in content!"
content = content.replace(old_transitions, new_transitions, 1)

# Write back
with open(slide_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: notebooks/slide.md updated successfully!")
