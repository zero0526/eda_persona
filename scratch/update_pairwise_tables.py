# -*- coding: utf-8 -*-
"""
Update Slide 2.5.1, 2.5.2, 2.5.3 with clean 4-column tables (no CoT quote column)
"""

import os

slide_path = os.path.abspath("notebooks/slide.md")

with open(slide_path, "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "## 🖥️ SLIDE 2.5.1: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CHỦ ĐỘNG GÕ PHÍM (`SEARCH` & `COMMENT`)"
end_marker = "## 🖥️ SLIDE 2.6: TÍNH LIÊN KẾT THÔNG TIN XUYÊN PHIÊN (CROSS-SESSION MEMORY & CONTINUITY)"

assert start_marker in content, "start_marker not found"
assert end_marker in content, "end_marker not found"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

new_content = """## 🖥️ SLIDE 2.5.1: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CHỦ ĐỘNG GÕ PHÍM (`SEARCH` & `COMMENT`)

### 1. Hình ảnh Trực quan Slide
![Đối sánh Động lực Hành vi Chủ động Gõ phím](../output/figures/slide2_5_1_search_and_comment.png)

### 2. Nội dung Trình chiếu trên Slide
* **Tiêu đề:** ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CHỦ ĐỘNG GÕ PHÍM: `SEARCH` & `COMMENT`
* **Thông điệp cốt lõi:** `SEARCH` và `COMMENT` là hai hành vi chủ động tiêu tốn chi phí nhận thức cao nhất trên mạng xã hội; thay vì thụ động tiếp nhận, Agent phải tự sinh câu lệnh truy vấn hoặc tự viết phản hồi bằng tiếng Việt; cơ cấu các lý do viện dẫn nội tại bộc lộ mục đích thực sự và bản sắc giao tiếp độc bản của từng Persona.

* **BẢNG 1: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI TÌM KIẾM CHỦ ĐỘNG (`SEARCH`)**

| Persona | Top Các Lý Do Được Viện Dẫn Hàng Đầu (% Nội Tại Khi Tìm Kiếm) | Động Lực Chi Phối Chính | Bản Chất Mục Đích Nhận Thức Thực Sự |
| :--- | :--- | :--- | :--- |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **1. Tò mò khoa học vũ trụ** (`curiosity`: 100.0%) | 🔭 **Khoa học thiên văn địa phương** | Bù đắp khoảng trống thông tin khi Newsfeed chưa hiển thị; chủ động tìm kiếm thời điểm quan sát Sao Hỏa đối lập tại Đà Nẵng ngày 4/10 để thỏa mãn đam mê thiên văn. |
| **`vn_fb_006`** *(Gen X BĐS Cần Thơ)* | **1. Khảo sát thị trường BĐS** (`interest_real_estate`: 66.7%)<br>**2. Thận trọng, kiểm chứng quy hoạch** (`skepticism`: 33.3%) | 💼 **Khảo sát dự án BĐS & Quy hoạch** | Động cơ kinh tế thực dụng: Chủ động tra cứu quy hoạch Nam Cần Thơ và giá đất Cái Răng để thẩm định thị trường trước khi xuống tiền đầu tư. |
| **`vn_fb_001`** *(Thiết kế đồ họa TP.HCM)* | **1. Công nghệ mới cho nghề nghiệp** (`interest_technology`: 100.0%) | 💻 **Công cụ AI kiến trúc & Đồ họa** | Động cơ nâng cao năng suất chuyên môn: Chủ động tìm kiếm các phần mềm và công cụ AI mới nhất phục vụ thiết kế kiến trúc và dựng hình 3D. |
| **`vn_fb_003`** *(Bảo vệ Đà Nẵng)* | **1. Ẩm thực đường phố** (`cuisine_street_food`: 50.0%)<br>**2. Giao lưu cởi mở** (`social_engagement_style`: 50.0%) | 🍢 **Ẩm thực đêm & Địa điểm ăn uống** | Nhu cầu đời sống ca trực đêm: Tìm kiếm quán bún trộn Đà Nẵng ngon quanh khu vực trực để đi ăn sau ca làm việc khi bảng tin không gợi ý đúng ý. |
| **`vn_fb_004`** *(Phục vụ trẻ TP.HCM)* | **1. Thể thao bóng đá** (`sport_football`: 100.0%) | ⚽ **Giải trí thể thao tức thời** | Bù đắp nội dung giải trí khi Newsfeed thiếu hụt: Chủ động gõ tìm video highlight bóng đá mới nhất khi lướt Reels nhiều lần không thấy. |
| **`vn_fb_002`** *(Gia đình Nghệ An)* | *(Không phát sinh hành vi tìm kiếm)* | 🏡 **Tiếp nhận thụ động nội dung sẵn có** | Tâm lý người dùng truyền thống lớn tuổi: Hoàn toàn thỏa mãn với bảng tin gợi ý về gia đình, tâm linh; không có nhu cầu tra cứu từ khóa mở rộng. |

* **BẢNG 2: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI VIẾT BÌNH LUẬN (`COMMENT`)**

| Persona | Top Các Lý Do Được Viện Dẫn Hàng Đầu (% Nội Tại Khi Comment) | Động Lực Chi Phối Chính | Bản Chất Mục Đích Nhận Thức Thực Sự |
| :--- | :--- | :--- | :--- |
| **`vn_fb_003`** *(Bảo vệ Đà Nẵng)* | **1. Món ăn truyền thống Việt** (`cuisine_vietnamese`: 38.9%)<br>**2. Ẩm thực đường phố** (`cuisine_street_food`: 33.3%)<br>**3. Giao lưu cởi mở** (`social_engagement_style`: 11.1%) | 🍜 **Ẩm thực bình dân & Kết nối bạn bè** *(Hơn 72% lý do xoay quanh ăn uống)* | Hỏi địa chỉ quán xá và chia sẻ trải nghiệm ăn uống đời thường; sử dụng bình luận làm công cụ kết nối bạn bè bằng ngôn ngữ thân mật, từ lóng Gen Z và emoji. |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **1. Giá trị truyền thống, tự hào dân tộc** (`value_tradition`: 58.3%)<br>**2. Tò mò tri thức lịch sử** (`curiosity`: 33.3%)<br>**3. Gắn kết địa phương** (`province`: 8.3%) | 🇻🇳 **Tri ân lịch sử & Lòng yêu nước** *(Gần 60% vì đạo lý tiền nhân)* | Bày tỏ lòng biết ơn sâu sắc và tri ân công đức tiền nhân dưới các bài viết về Đại tướng Võ Nguyên Giáp và chiến dịch lịch sử; ngôn từ trang nghiêm, mẫu mực. |
| **`vn_fb_001`** *(Thiết kế đồ họa TP.HCM)* | **1. Tò mò chuyên môn kiến trúc** (`curiosity`: 66.7%)<br>**2. Đánh giá bố cục thiết kế** (`writing_format`: 33.3%) | 🎨 **Góp ý nghiệp vụ & Thẩm mỹ đồ họa** | Đóng góp góc nhìn chuyên môn nghề nghiệp về góc phối cảnh 3D, bố cục ánh sáng và thẩm mỹ thị giác; bình luận mang tính trao đổi học thuật có tính xây dựng. |
| **`vn_fb_006`** *(Gen X BĐS Cần Thơ)* | **1. Đời sống thực tế Nam Bộ** (`cuisine_street_food`: 100.0%) | 💼 **Khảo sát đời sống & Thẩm định địa bàn** | Hỏi thăm thông tin sinh hoạt đời thường cụ thể với giọng điệu người lớn tuổi miền Tây; bình luận mang tính thẩm định thực tế cuộc sống địa phương. |
| **`vn_fb_002`** *(Gia đình Nghệ An)* | **1. Sắc thái ngôn từ hòa nhã** (`tone`: 100.0%) | 🌸 **Gửi lời chúc phúc & Thiện lành** | Duy trì thái độ thiện lương của người phụ nữ đôn hậu; gửi lời chúc an lành, mạnh khỏe tới cộng đồng mà không tham gia tranh luận hay đối đầu. |
| **`vn_fb_004`** *(Phục vụ trẻ TP.HCM)* | *(Không phát sinh hành vi comment)* | 📱 **Tiêu thụ video thụ động** | Thói quen Gen Z xem video ngắn Reels: Lướt nhanh giải trí thuần túy, ngại đầu tư công sức tương tác bằng văn bản chữ viết. |

### 3. Lời thoại Thuyết trình của Người nói (Speaker Script)
> *"Kính thưa Hội đồng,
> 
> Bắt đầu đi vào cặp hành vi chủ động gõ phím tại Slide 2.5.1: **Tìm kiếm (`SEARCH`) và Viết bình luận (`COMMENT`)**. Ở đây, chúng tôi không đi đếm số lượt thuần túy, mà tập trung giải mã: **Khi mỗi Persona quyết định gõ phím, trong tâm trí họ bị thôi thúc bởi những lý do nội tại nào nhất?**
> 
> Nhìn vào **Bảng 1 về Tìm kiếm**:
> - Anh thợ cơ khí `005` khi tìm kiếm thì 100% là vì niềm đam mê khoa học vũ trụ — anh chủ động bù đắp thông tin thiên văn địa phương mà bảng tin chưa có.
> - Bác `006` thì 66.7% vì bất động sản và 33.3% vì thái độ thận trọng — bác tra cứu quy hoạch và giá đất Cái Răng để thẩm định cơ hội đầu tư.
> - Cô bạn thiết kế `001` dành 100% tìm kiếm cho công nghệ AI kiến trúc phục vụ chuyên môn.
> - Anh bảo vệ `003` tìm quán bún trộn Đà Nẵng để ăn đêm sau giờ làm việc.
> - Còn chị `002` hoàn toàn không tìm kiếm vì chị hài lòng với nội dung gia đình trên bảng tin.
> 
> Sang **Bảng 2 về Viết bình luận**, sự phân hóa mục đích nhận thức càng bộc lộ rực rỡ:
> - Anh bảo vệ `003` khi viết bình luận thì hơn 72% lý do là để hỏi địa chỉ ăn uống đường phố và kết nối bạn bè bằng ngôn ngữ thân mật giới trẻ.
> - Trái lại hoàn toàn, anh thợ cơ khí `005` dành tới 58.3% lý do bình luận cho lòng tự hào truyền thống và 33.3% cho tò mò lịch sử — anh bình luận trang nghiêm để tri ân Đại tướng Võ Nguyên Giáp.
> - Cô thiết kế `001` chỉ bình luận khi cần góp ý chuyên môn về phối cảnh 3D; bác `006` hỏi thăm đời sống Nam Bộ; và chị `002` gửi lời chúc sức khỏe bình an.
> 
> Bảng đối sánh này chứng minh: **Mỗi Persona khi gõ phím đều có cơ cấu lý do viện dẫn hoàn toàn khác biệt, phản ánh đúng hoàn cảnh sống và thế giới quan của họ**."*

### 4. Lời thoại Chuyển tiếp sang Slide kế tiếp
> *"Chúng ta đã thấy các lý do thúc đẩy hành vi chủ động gõ phím. Vậy đối với hành vi thẩm định nội dung văn bản — nơi Agent tiếp nhận thông tin chọn lọc để đọc sâu (`READ`) hoặc vượt qua rào cản lười biếng để bấm 'Xem thêm' (`EXPAND`), cơ cấu lý do nội tại diễn ra như thế nào? Xin mời Hội đồng cùng đến với Slide 2.5.2."*

---

## 🖥️ SLIDE 2.5.2: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI THẨM ĐỊNH VĂN BẢN (`READ` & `EXPAND`)

### 1. Hình ảnh Trực quan Slide
![Đối sánh Động lực Hành vi Thẩm định Văn bản](../output/figures/slide2_5_2_read_and_expand.png)

### 2. Nội dung Trình chiếu trên Slide
* **Tiêu đề:** ĐỐI SÁNH ĐỘNG LỰC HÀNH VI THẨM ĐỊNH VĂN BẢN: `READ` & `EXPAND`
* **Thông điệp cốt lõi:** `READ` là trục xương sống tiếp nhận thông tin, trong khi `EXPAND` ("Xem thêm") là bộ lọc nhận thức khắt khe phản ánh mức độ tò mò vượt ngưỡng; phân tích cơ cấu lý do nội tại cho thấy sự tương phản sâu sắc giữa đọc tư duy logic, thẩm định đầu tư thực dụng, đắm chìm lịch sử và lướt tin vắn đời thường.

* **BẢNG 1: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI ĐỌC SÂU TUYỂN CHỌN (`READ`)**

| Persona | Top Các Lý Do Được Viện Dẫn Hàng Đầu (% Nội Tại Khi Đọc Sâu) | Động Lực Chi Phối Chính | Bản Chất Mục Đích Nhận Thức Thực Sự |
| :--- | :--- | :--- | :--- |
| **`vn_fb_001`** *(Thiết kế đồ họa TP.HCM)* | **1. Tò mò logic & giải đố** (`curiosity`: 53.8%)<br>**2. Thị trường BĐS** (`interest_real_estate`: 26.9%)<br>**3. Nghề nghiệp & Công nghệ** (`career_role` / `technology`: 15.4%) | 🧠 **Tư duy logic duy lý & Thẩm định thị trường** | Đọc sâu để giải các bài toán cờ vua thế hiểm, rèn luyện tư duy logic, tìm cảm hứng đồ họa và theo dõi biến động thị trường căn hộ TP.HCM. |
| **`vn_fb_006`** *(Gen X BĐS Cần Thơ)* | **1. Tò mò thương mại** (`curiosity`: 41.9%)<br>**2. Dự án BĐS địa phương** (`interest_real_estate`: 23.3%)<br>**3. Tâm linh & Tích lũy** (`spirituality`: 11.6%, `wealth`: 9.3%) | 💼 **Thẩm định đầu tư & Chiêm nghiệm trung niên** | Đọc chậm rãi, kỹ lưỡng từng thông số giá thuê căn hộ Cái Răng 8.5 triệu/tháng, điều khoản pháp lý dự án và các bài viết về sức khỏe thực dưỡng tuổi già. |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **1. Tò mò khoa học kỹ thuật** (`curiosity`: 62.1%)<br>**2. Ký ức lịch sử hào hùng** (`value_tradition`: 24.1%)<br>**3. Sách & Thể thao** (13.8%) | 🇻🇳 **Nuôi dưỡng lòng yêu nước & Tri thức kỹ thuật** | Nghiền ngẫm từng câu chữ về ký ức chiến hào Điện Biên Phủ, câu chuyện 10 năm của đất nước và các bài viết kiến thức khoa học vũ trụ, thiên văn. |
| **`vn_fb_003`** *(Bảo vệ Đà Nẵng)* | **1. Văn hóa ẩm thực Việt** (`cuisine_vietnamese`: 30.4%)<br>**2. Tham gia hội nhóm địa phương** (`group_community`: 21.7%)<br>**3. Giao lưu cởi mở** (`social_engagement`: 13.0%) | 🍜 **Khám phá ẩm thực & Đời sống hội nhóm** | Đọc kỹ để nắm công thức nấu ăn, địa chỉ các hàng quán bún mắm bình dân ngon bổ rẻ và theo dõi tin tức các hội nhóm thanh niên Đà Nẵng. |
| **`vn_fb_002`** *(Gia đình Nghệ An)* | **1. Bài viết hòa nhã, hướng thiện** (`tone`: 23.8%)<br>**2. Tò mò chuyện nhân văn** (`curiosity`: 23.8%)<br>**3. Phụng dưỡng cha mẹ & Quê hương** (`parenting_family`: 14.3%, `province`: 14.3%) | 🏡 **Đạo hiếu gia đình & Cảm xúc ấm áp** | Tìm hiểu các bài viết về viện dưỡng lão công lập quá tải để chăm lo cho cha mẹ già, các câu chuyện thiện nguyện ấm áp và tin tức xứ Nghệ. |
| **`vn_fb_004`** *(Phục vụ trẻ TP.HCM)* | **1. Thể thao bóng đá** (`sport_football`: 70.0%)<br>**2. Tò mò tin tức nhanh** (`curiosity`: 20.0%)<br>**3. Định dạng bài ngắn** (10.0%) | ⚽ **Cập nhật tỷ số & Tin vắn thể thao** | Đọc lướt nhanh tin tức chuyển nhượng cầu thủ, tỷ số bóng đá đêm qua trước khi quay lại màn hình video ngắn giải trí. |

* **BẢNG 2: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI MỞ RỘNG BÀI VIẾT BỊ ẨN (`EXPAND` — "XEM THÊM")**

| Persona | Top Các Lý Do Được Viện Dẫn Hàng Đầu (% Nội Tại Khi Bấm "Xem Thêm") | Động Lực Chi Phối Chính | Bản Chất Mục Đích Nhận Thức Thực Sự |
| :--- | :--- | :--- | :--- |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **1. Tò mò tri thức khoa học** (`curiosity`: 36.4%)<br>**2. Chiến dịch lịch sử dài** (`value_tradition`: 36.4%)<br>**3. Tư duy logic & Ẩm thực** (27.2%) | 📚 **Khao khát tiếp cận tri thức toàn vẹn** | Không chấp nhận thông tin bị cắt đoạn; chủ động bấm 'Xem thêm' để đọc trọn vẹn diễn biến chiến dịch lịch sử hào hùng và bài phân tích kỹ thuật dài. |
| **`vn_fb_001`** *(Thiết kế đồ họa TP.HCM)* | **1. Tò mò công nghệ mới** (`curiosity`: 71.4%)<br>**2. Quyết định nhanh & Hội nhóm** (28.6%) | 🔬 **Khám phá công nghệ VR & Bài toán tư duy** | Bấm mở rộng các bài viết phân tích sâu về võ thuật Taekwondo ứng dụng công nghệ thực tế ảo VR và các bài toán cờ vua nhiều nước đi phức tạp. |
| **`vn_fb_004`** *(Phục vụ trẻ TP.HCM)* | **1. Tò mò cái kết truyện du ký** (`curiosity`: 100.0%) | 🧭 **Khám phá phiêu lưu mạo hiểm** | Tò mò tức thời muốn xem kết cục bài viết hành trình đi bộ từ Anh đến Việt Nam có phần kết bị ẩn dưới dấu 'Xem thêm'. |
| **`vn_fb_002`** *(Gia đình Nghệ An)* | **1. Tâm linh Phật giáo** (`interest_spirituality`: 100.0%) | 📿 **Đọc trọn vẹn kệ kinh Phật** | Tâm niệm tôn kính, bấm mở rộng để tụng đọc trọn vẹn lời kệ chú Phật mẫu Chuẩn Đề bị thu gọn dưới chân bài viết. |
| **`vn_fb_003`** & **`vn_fb_006`** | *(Không phát sinh hành vi Expand — 0 lượt)* | 📱 **Thói quen tiếp nhận nhanh gọn** | Anh bảo vệ (003) lướt nhanh bằng một tay ngại đọc bài dài; Bác doanh nhân (006) thực dụng chỉ cần các tin BĐS có giá cụ thể sẵn trên feed. |

### 3. Lời thoại Thuyết trình của Người nói (Speaker Script)
> *"Kính thưa quý thầy cô,
> 
> Tiến sang cặp hành vi thứ hai tại Slide 2.5.2: **Đọc sâu (`READ`) và Mở rộng bài viết (`EXPAND`)**, dữ liệu cho thấy sự khác biệt sâu sắc trong cách 6 Persona thẩm định nội dung văn bản:
> 
> Nhìn vào **Bảng 1 về Đọc sâu**:
> - Khi đọc sâu, cô bạn thiết kế `001` dành hơn 53% cho tò mò cờ vua và 26.9% cho thị trường BĐS — đó là một tâm trí duy lý, yêu thích logic và nhạy bén với cơ hội tài sản.
> - Bác doanh nhân `006` dành 41.9% cho tin thương mại và 23.3% cho dự án BĐS — đọc kỹ từng điều khoản giá cả dự án Cái Răng.
> - Anh thợ `005` dành tới 62.1% cho khoa học kỹ thuật và 24.1% cho ký ức chiến hào Điện Biên Phủ.
> - Anh bảo vệ `003` dành hơn 50% cho ẩm thực Việt và tin tức hội nhóm thanh niên.
> - Chị phụ nữ gia đình `002` quan tâm hàng đầu đến đạo hiếu phụng dưỡng cha mẹ già trong viện dưỡng lão.
> - Và cậu phục vụ `004` dành tới 70% lý do đọc sâu cho tin tức bóng đá.
> 
> Đặc biệt, tại **Bảng 2 về hành vi Bấm 'Xem thêm'**:
> - Nút 'Xem thêm' là một bộ lọc nhận thức rất khắt khe. Anh thợ cơ khí `005` bấm xem thêm vì khao khát tri thức lịch sử và khoa học trọn vẹn; cô thiết kế `001` bấm xem thêm vì công nghệ thực tế ảo VR; chị `002` bấm xem thêm để đọc trọn lời kinh Phật.
> - Ngược lại, anh bảo vệ và bác doanh nhân không bao giờ bấm xem thêm: một người ngại đọc văn bản dài khi lướt điện thoại, người kia chỉ ưa chuộng các tin BĐS ngắn gọn hiển thị sẵn giá.
> 
> Rõ ràng, **mỗi Persona tiếp nhận văn bản theo đúng thói quen tư duy và mục đích sống của riêng mình**."*

### 4. Lời thoại Chuyển tiếp sang Slide kế tiếp
> *"Sau khi đã khảo sát các hành vi tiếp nhận văn bản duy lý, chúng ta hãy cùng bước sang góc nhìn giàu cảm xúc và tính lan tỏa xã hội nhất: Thả cảm xúc (`REACT`) và Chia sẻ (`SHARE`) tại Slide 2.5.3."*

---

## 🖥️ SLIDE 2.5.3: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CẢM XÚC & LAN TỎA (`REACT` & `SHARE`)

### 1. Hình ảnh Trực quan Slide
![Đối sánh Động lực Hành vi Cảm xúc & Lan tỏa](../output/figures/slide2_5_3_react_and_share.png)

### 2. Nội dung Trình chiếu trên Slide
* **Tiêu đề:** ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CẢM XÚC & LAN TỎA: `REACT` & `SHARE`
* **Thông điệp cốt lõi:** Thả cảm xúc (`REACT`) là chỉ báo trực tiếp cho sự đồng điệu tâm lý bộc phát, trong khi Chia sẻ (`SHARE`) là hành vi cực kỳ quý hiếm với rào cản xã hội rất cao; phân tích cơ cấu lý do nội tại cho thấy sự phân cực mạnh mẽ giữa biểu đạt tâm linh thiện lương, tán thưởng vẻ đẹp trí tuệ, phản xạ thể thao và tâm lý bảo toàn không gian cá nhân.

* **BẢNG 1: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI THẢ CẢM XÚC (`REACT`)**

| Persona | Top Các Lý Do Được Viện Dẫn Hàng Đầu (% Nội Tại Khi Thả Cảm Xúc) | Động Lực Chi Phối Chính | Bản Chất Mục Đích Nhận Thức Thực Sự |
| :--- | :--- | :--- | :--- |
| **`vn_fb_001`** *(Thiết kế đồ họa TP.HCM)* | **1. Tò mò bài giải cờ vua** (`curiosity`: 52.6%)<br>**2. Thiết kế & Thị trường BĐS** (`real_estate`: 26.3%)<br>**3. Vai trò nghề nghiệp** (`career_role`: 15.8%) | 🎨 **Tán thưởng vẻ đẹp trí tuệ & Thẩm mỹ kiến trúc** | Thả tim/like để ghi nhận lời giải cờ vua mate in 2 thông minh, các bản vẽ thiết kế nội thất tối giản hiện đại và dự án nhà đất tiềm năng. |
| **`vn_fb_002`** *(Gia đình Nghệ An)* | **1. Bài viết hòa nhã, an yên** (`tone`: 42.1%)<br>**2. Cảm xúc tâm linh thành kính** (`emotional_expressiveness`: 26.3%)<br>**3. Quê hương & Gia đình** (15.8%) | 📿 **Đức tin tâm linh thành kính & Tình yêu quê hương** | Thả tim tượng Bồ tát Quán Thế Âm 33m sông Tiền, đền Ông Hoàng Mười Nghệ An để cầu bình an cho gia đình và bày tỏ lòng thành kính với cội nguồn. |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **1. Tò mò hiện tượng vũ trụ** (`curiosity`: 50.0%)<br>**2. Tri ân lịch sử dân tộc** (`value_tradition`: 25.0%)<br>**3. Ẩm thực & Công nghệ** (25.0%) | 🇻🇳 **Tri ân tiền nhân & Đam mê thiên văn học** | Thả like bức ảnh Đại tướng Võ Nguyên Giáp tại Điện Biên Phủ để bày tỏ lòng biết ơn; like ảnh thiên văn kỳ thú ngắm trăng sao Đà Nẵng. |
| **`vn_fb_006`** *(Gen X BĐS Cần Thơ)* | **1. Dự án BĐS Cần Thơ** (`interest_real_estate`: 41.7%)<br>**2. Bảo vệ sức khỏe thực dưỡng** (`value_health`: 25.0%)<br>**3. Tò mò sinh kế Nam Bộ** (`curiosity`: 16.7%) | 💼 **Lưu trữ thông tin kinh tế & Dưỡng sinh trung niên** | Thả like tin nhà đất Cần Thơ giá tốt, vườn trái cây miền Tây 25k/kg và bí quyết thực dưỡng để đánh dấu lưu trữ thông tin hữu ích. |
| **`vn_fb_004`** *(Phục vụ trẻ TP.HCM)* | **1. Định dạng video hài hước** (`content_consumption_format`: 66.7%)<br>**2. Tình huống bóng đá kịch tính** (`sport_football`: 22.2%) | ⚽ **Phản xạ cảm xúc bộc phát trước video giải trí** | Thả haha/like tức thì khi thấy Dembele sút bóng hỏng ăn hoặc các pha bóng kỹ thuật đẹp mắt trong video ngắn Reels. |
| **`vn_fb_003`** *(Bảo vệ Đà Nẵng)* | **1. Định dạng món ăn bắt mắt** (`content_consumption_format`: 66.7%)<br>**2. Tò mò món mới** (`curiosity`: 33.3%) | 🍢 **Kích thích vị giác ẩm thực đường phố** | Cực kỳ tiết kiệm nút like; chỉ thả tim khi món cá rô đồng muối sả hay món ăn bình dân quá hấp dẫn (dành trọn sự tương tác cho viết bình luận). |

* **BẢNG 2: ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CHIA SẺ BÀI VIẾT (`SHARE`)**

| Persona | Top Các Lý Do Được Viện Dẫn Hàng Đầu (% Nội Tại Khi Chia Sẻ) | Động Lực Chi Phối Chính | Bản Chất Mục Đích Nhận Thức Thực Sự |
| :--- | :--- | :--- | :--- |
| **`vn_fb_005`** *(Thợ cơ khí Đà Nẵng)* | **1. Tò mò khoa học & Kết nối hội thiên văn** (`curiosity`: 100.0%) | 🔭 **Lan tỏa tri thức thiên văn học** | Khao khát kết nối cộng đồng lên tới đỉnh điểm; chia sẻ sự kiện Sao Hỏa đối lập lên dòng thời gian cá nhân để hỏi kinh nghiệm quan sát từ hội thiên văn địa phương. |
| **`vn_fb_001, 002, 003, 004, 006`** | *(Không phát sinh hành vi chia sẻ — 0 lượt)* | 🔒 **Bảo toàn không gian riêng tư** | **Phản ánh chuẩn mực tâm lý mạng xã hội hiện đại:** E ngại làm phiền bạn bè (newsfeed clutter), giữ kín quan điểm cá nhân và tránh phán xét xã hội. |

### 3. Lời thoại Thuyết trình của Người nói (Speaker Script)
> *"Kính thưa Hội đồng,
> 
> Chúng ta khép lại phân đoạn 2.5 với cặp hành vi cảm xúc và lan tỏa xã hội tại Slide 2.5.3: **Thả cảm xúc (`REACT`) và Chia sẻ bài viết (`SHARE`)**.
> 
> Nhìn vào **Bảng 1 về Thả cảm xúc**:
> - Hai đỉnh cao tương tác bộc lộ hai thế giới nội tâm hoàn toàn đối lập: Cô gái thiết kế `001` like vì sự tán thưởng vẻ đẹp trí tuệ — hơn 52% là bài giải cờ vua thông minh và phối cảnh kiến trúc. Trong khi đó, chị phụ nữ gia đình `002` like vì sự thành kính tâm linh và lòng hướng thiện — hơn 68% lý do xoay quanh tượng Phật bà sông Tiền, đền Hoàng Mười và lời chúc bình an.
> - Bác doanh nhân `006` like vì lưu trữ thông tin BĐS và sức khỏe; anh thợ `005` like tri ân Đại tướng Giáp; cậu thanh niên `004` thả haha cho video bóng đá; còn anh bảo vệ `003` thì chỉ like khi món ăn quá ngon mắt vì anh ưu tiên viết bình luận.
> 
> Và cuối cùng, hãy nhìn vào **Bảng 2 với hành vi Chia sẻ (`SHARE`)**:
> - Năm trong số sáu Persona hoàn toàn không chia sẻ bất cứ bài viết nào — đây là một phát hiện cực kỳ chân thực về mặt tâm lý xã hội: người dùng hiện đại e ngại spam bảng tin bạn bè và có xu hướng bảo toàn không gian riêng tư.
> - Lượt chia sẻ duy nhất xuất hiện khi lòng say mê thiên văn của anh thợ cơ khí `005` vượt qua rào cản e ngại, thúc đẩy anh chia sẻ sự kiện Sao Hỏa đối lập để kết nối với hội thiên văn Đà Nẵng.
> 
> Thưa Hội đồng, qua các bảng đối sánh vừa rồi, chúng tôi đã chứng minh: **Mỗi hành vi của Agent đều được kích hoạt bởi các lý do nhận thức nội tại chân thực, sống động và nhất quán tuyệt đối với căn tính của từng nhân vật**."*

### 4. Lời thoại Chuyển tiếp sang Slide kế tiếp
> *"Một phiên lướt mạng có nhận thức sâu sắc và động lực phong phú như vậy là rất ấn tượng. Nhưng qua các ngày khác nhau, các phiên khác nhau, liệu Agent có nhớ những gì mình đã đọc hôm qua và duy trì được mạch quan tâm hay không? Hãy cùng đến với Slide 2.6 về Trí nhớ xuyên phiên."*

---

"""

content = content[:start_idx] + new_content + content[end_idx:]

with open(slide_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Slide 2.5.1, 2.5.2, 2.5.3 updated with 4-column tables!")
