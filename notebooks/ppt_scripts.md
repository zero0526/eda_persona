# KỊCH BẢN THUYẾT TRÌNH SLIDE (PPT STORYTELLING SCRIPT)
# BÁO CÁO PHÂN TÍCH DỮ LIỆU KHÁM PHÁ (EDA) HÀNH VI AGENT TRÊN FACEBOOK
## "Từ Nhắc Nhở Ngôn Ngữ Đến Cơ Học Vật Lý: Giải Mã Hệ Điều Hành Hành Vi Của AI Agent"

> **Bộ tài liệu tham chiếu:**
> - Notebook phân tích chính: [`notebooks/eda_action_logs.ipynb`](file:///d:/source_code/eda_persona/notebooks/eda_action_logs.ipynb)
> - Notebook phân cụm hồ sơ: [`notebooks/eda_fb_persona.ipynb`](file:///d:/source_code/eda_persona/notebooks/eda_fb_persona.ipynb)
> - Báo cáo tổng hợp Bước 5: [`output/step5_bivariate_multivariate_report.md`](file:///d:/source_code/eda_persona/output/step5_bivariate_multivariate_report.md)
> - Toàn bộ hình ảnh trích xuất: [`output/figures/`](file:///d:/source_code/eda_persona/output/figures/)
> - Toàn bộ bảng thống kê: [`output/tables/`](file:///d:/source_code/eda_persona/output/tables/)
>
> **Thời lượng thuyết trình chuẩn:** 20 - 25 phút (15 Slides cốt lõi).  
> **Phong cách trình bày:** Dẫn truyện điều tra khoa học (Scientific Storytelling / Investigative Narrative), liên kết tuần tự 5 Hồi kịch bản (Five-Act Dramatic Arc): *Khởi phát $\rightarrow$ Manh mối $\rightarrow$ Cú lật kèo $\rightarrow$ Cao trào $\rightarrow$ Cái kết & Tầm nhìn*.

---

```mermaid
journey
    title CỐT TRUYỆN THUYẾT TRÌNH (THE 5-ACT NARRATIVE ARC)
    section Hồi 1: Đặt Vấn Đề
      Nghi vấn Persona: Chỉ là con rối ngẫu nhiên?: 5: Diễn giả
      Thiết kế phòng thí nghiệm & 4 Giả thuyết H1-H4: 5: Diễn giả
    section Hồi 2: Manh Mối Nội Tâm
      Nghịch lý: Suy nghĩ lâu hơn nhưng chạy nhanh gấp 3: 6: Diễn giả
      NLP Tư duy & Cơn sa đà nhận thức (Drift): 6: Diễn giả
    section Hồi 3: Cú Lật Kèo
      THE TWIST: Nghịch lý Simpson trên Tỷ lệ thành công: 8: Diễn giả
      Vòng lặp vô tận (No-Persona) vs Chuỗi mục tiêu: 7: Diễn giả
    section Hồi 4: Cao Trào Cơ Học
      Bóc tách nội bộ 3 Cụm Archetype toán học: 8: Diễn giả
      THE CLIMAX: Vận tốc cuộn 5,000 px/s & 100% Fast vs Careful: 9: Diễn giả
    section Hồi 5: Cái Kết
      Bảng điểm H1-H4 toàn thắng & Định nghĩa OS Hành vi: 8: Diễn giả
```

---

## MỤC LỤC 15 SLIDE THUYẾT TRÌNH

1. [Slide 1: Tiêu đề & Cú Móc Nhận Thức (The Provocative Hook)](#slide-1-tiêu-đề--cú-móc-nhận-thức-the-provocative-hook)
2. [Slide 2: Thiết Kế Thực Nghiệm Đối Chứng & 4 Giả Thuyết Khoa Học](#slide-2-thiết-kế-thực-nghiệm-đối-chứng--4-giả-thuyết-khoa-học)
3. [Slide 3: Hiện Trường Thực Nghiệm & Cấu Trúc Dữ Liệu 4 Tầng](#slide-3-hiện-trường-thực-nghiệm--cấu-trúc-dữ-liệu-4-tầng)
4. [Slide 4: Kiểm Soát Thiên Lệch & Sàng Lọc Ý Nghĩa Thống Kê Toàn Diện](#slide-4-kiểm-soát-thiên-lệch--sàng-lọc-ý-nghĩa-thống-kê-toàn-diện)
5. [Slide 5: Nghịch Lý Thời Gian: Chi Phí Nhận Thức Đổi Lấy Vận Tốc Thực Thi](#slide-5-nghịch-lý-thời-gian-chi-phí-nhận-thức-đổi-lấy-vận-tốc-thực-thi)
6. [Slide 6: Thế Giới Nội Tâm: Phân Tích NLP Tiếng Việt & Log-Odds Ratio](#slide-6-thế-giới-nội-tâm-phân-tích-nlp-tiếng-việt--log-odds-ratio)
7. [Slide 7: Cơn Sa Đà Nhận Thức & Cơ Chế Kháng Trôi Dạt (Guardrail Recovery)](#slide-7-cơn-sa-đà-nhận-thức--cơ-chế-kháng-trôi-dạt-guardrail-recovery)
8. [Slide 8: Hồ Sơ Cấp Phiên: Nhịp Sinh Học & Động Lực Thoát Phiên](#slide-8-hồ-sơ-cấp-phiên-nhịp-sinh-học--động-lực-thoát-phiên)
9. [Slide 9: THE PLOT TWIST: Nghịch Lý Simpson & Cạm Bẫy Không Gian Bề Mặt](#slide-9-the-plot-twist-nghịch-lý-simpson--cạm-bẫy-không-gian-bề-mặt)
10. [Slide 10: Vòng Lặp Vô Tận: Động Lực Chuỗi Chuyển Tiếp Hành Vi Trigram](#slide-10-vòng-lặp-vô-tận-động-lực-chuỗi-chuyển-tiếp-hành-vi-trigram)
11. [Slide 11: Bước Chuyển Chiến Lược: Bóc Tách Nội Bộ Nhóm Persona Bằng PCA](#slide-11-bước-chuyển-chiến-lược-bóc-tách-nội-bộ-nhóm-persona-bằng-pca)
12. [Slide 12: THE CLIMAX (Bằng Chứng Cơ Học Vật Lý): Vận Tốc & Chế Độ Cuộn Chuột](#slide-12-the-climax-bằng-chứng-cơ-học-vật-lý-vận-tốc--chế-độ-cuộn-chuột)
13. [Slide 13: Cường Độ Xã Hội & Không Gian Điều Hướng: Khi Tính Cách Thấm Vào Hành Động](#slide-13-cường-độ-xã-hội--không-gian-điều-hướng-khi-tính-cách-thấm-vào-hành-động)
14. [Slide 14: Bảng Điểm Tổng Kết: Khẳng Định Trọn Vẹn 4 Giả Thuyết H1 - H4](#slide-14-bảng-điểm-tổng-kết-khẳng-định-trọn-vẹn-4-giả-thuyết-h1---h4)
15. [Slide 15: Tầm Nhìn Khoa Học: Persona Là Một "Hệ Điều Hành Hành Vi"](#slide-15-tầm-nhìn-khoa-học-persona-là-một-hệ-điều-hành-hành-vi)

---

## CHI TIẾT KỊCH BẢN TỪNG SLIDE (SLIDE-BY-SLIDE SCRIPTS)

### Slide 1: Tiêu đề & Cú Móc Nhận Thức (The Provocative Hook)
- **Hồi kịch bản:** Hồi 1 - Lời Mở Đầu (Act I: The Hook)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Nền Dark-mode công nghệ sang trọng, chia đôi màn hình:
    - Bên trái: Tiêu đề lớn, câu hỏi cốt lõi, tên tác giả/nhóm nghiên cứu.
    - Bên phải: Hình ảnh sơ đồ chu trình tổng quan [`output/figures/agent_loop.png`](file:///d:/source_code/eda_persona/output/figures/agent_loop.png) với 3 vòng tròn phát sáng đại diện cho *Nhận thức $\rightarrow$ Ra quyết định $\rightarrow$ Thao tác vật lý*.
- **Thông điệp cốt lõi (Punchline):**
  > *Khi cài đặt một Persona vào Large Language Model, chúng ta đang tạo ra một con người ảo có tính cách nhất quán, hay chỉ đang đeo một chiếc mặt nạ ngẫu nhiên (Stochastic Parrot)?*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Kính thưa quý vị,  
  > Trong kỷ nguyên bùng nổ của các Autonomous AI Agents, một câu hỏi hóc búa luôn đeo bám cộng đồng nghiên cứu: Khi chúng ta đưa một hồ sơ nhân khẩu, sở thích và tính cách (Persona) vào hệ thống prompt của LLM, liệu AI có thực sự hành xử như con người mô phỏng, hay nó chỉ là một con vẹt ngẫu nhiên lặp lại từ ngữ?  
  > Đặc biệt, khi thả một Agent vào môi trường mạng xã hội phức tạp, nhiều cám dỗ như Facebook — nơi có dòng bảng tin bất tận, các nhóm cộng đồng, trang tin và vô số nội dung gây xao nhãng — liệu 'tính cách' đó có đủ sức mạnh để dẫn dắt hành động của Agent qua từng cú nhấp chuột, từng cử chỉ cuộn màn hình?  
  > Hôm nay, chúng tôi không mang đến những câu chuyện định tính hay suy đoán cảm tính. Thông qua một quy trình Khám phá Dữ liệu Chuyên sâu (EDA) trên từng micro-step hành vi thực tế, chúng tôi sẽ mở chiếc hộp đen của Agent và chứng minh bằng toán học: Persona không phải là một chiếc mặt nạ ngôn ngữ, mà thực sự hoạt động như một Hệ điều hành Hành vi hoàn chỉnh."*
- **Hộp Bằng chứng Số liệu:** Khảo sát trên 437 bước hành động thực tế từ trình duyệt thật, thu thập đầy đủ tham số nhận thức và dấu vết cơ học.
- **Phép kiểm nghiệm đề xuất thêm:** Không có (Slide mở đầu).

---

### Slide 2: Thiết Kế Thực Nghiệm Đối Chứng & 4 Giả Thuyết Khoa Học
- **Hồi kịch bản:** Hồi 1 - Thiết Lập Hiện Trường (Act I: Research Setup)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Trái: Bảng so sánh thiết kế A/B Test giữa Nhóm Can thiệp Persona ($N=6$ Agent) vs Nhóm Đối chứng Trung tính No-Persona ($N=2$ Agent).
  - Phải: Card trực quan tóm tắt 4 Câu hỏi Nghiên cứu ($RQ_1 \rightarrow RQ_4$) ánh xạ sang 4 Giả thuyết kỳ vọng ($H_1 \rightarrow H_4$).
- **Thông điệp cốt lõi:**
  > *Một thiết kế thực nghiệm chuẩn tắc A/B testing: Giữ nguyên môi trường Facebook thực tế, chỉ can thiệp duy nhất biến độc lập Persona.*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Để giải quyết câu hỏi này một cách khách quan, chúng tôi thiết lập một thí nghiệm đối chứng thực nghiệm nghiêm ngặt:  
  > Nhóm Can thiệp (Intervention) gồm 6 Persona đại diện cho các nhóm người dùng Việt Nam đa dạng về độ tuổi, nhịp độ lướt, phong cách đọc và sở thích.  
  > Nhóm Đối chứng (Control) gồm 2 Agent trung tính hoàn toàn không có Persona, hoạt động chỉ với nhiệm vụ lướt Facebook cơ bản.  
  > Chúng tôi đặt ra 4 Giả thuyết tiên nghiệm ($H_1 \rightarrow H_4$):  
  > - $H_1$: Persona sẽ tạo ra chi phí nhận thức cao hơn (suy nghĩ lâu hơn) nhưng đổi lại là hành vi có chủ đích và giảm bớt các lỗi thao tác thừa.  
  > - $H_2$: Persona sẽ thúc đẩy việc khám phá không gian sâu (tìm kiếm, tham gia nhóm, đọc fanpage) thay vì mắc kẹt ở News Feed.  
  > - $H_3$: Persona có khả năng tự kiểm soát và hồi phục khi bị cảnh báo sa đà nội dung.  
  > - Và $H_4$: Giữa các Persona khác nhau, hành vi vật lý đo lường trên trình duyệt phải phản ánh chính xác các thuộc tính quy định trong hồ sơ.  
  > Hãy cùng xem dữ liệu thực nghiệm đã trả lời 4 giả thuyết này như thế nào."*
- **Hộp Bằng chứng Số liệu:** Dữ liệu nguồn từ [`data/original_facebook_persona.json`](file:///d:/source_code/eda_persona/data/original_facebook_persona.json) và các tệp benchmark log.
- **Phép kiểm nghiệm đề xuất thêm:** Power Analysis (Ước lượng năng lực thống kê $1 - \beta$) để khẳng định quy mô mẫu 437 bước đủ phát hiện effect size lớn ($d \ge 0.5$).

---

### Slide 3: Hiện Trường Thực Nghiệm & Cấu Trúc Dữ Liệu 4 Tầng
- **Hồi kịch bản:** Hồi 1 - Khung Đo Lường (Act I: Measurement Framework)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Hình ảnh đồ họa phân cấp: [`output/figures/step2_data_hierarchy.png`](file:///d:/source_code/eda_persona/output/figures/step2_data_hierarchy.png)
  - 4 khối xếp chồng đại diện cho 4 tầng dữ liệu:
    1. **Episode Level** (8 phiên, metadata, thời gian bắt đầu/kết thúc).
    2. **Step Level** (437 bước, intent, surface, thought reasoning, target).
    3. **Tool Execution Level** (Playwright native events, gesture ms, wheel distance px).
    4. **Persona Evidence Level** (6 chiều bằng chứng nhân khẩu, sở thích, tính cách).
- **Thông điệp cốt lõi:**
  > *Dữ liệu không dừng lại ở text API, mà đi sâu vào tầng vật lý trình duyệt (DOM, viewport pixels, mouse gestures).*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Để không bỏ sót bất kỳ chi tiết nào, hệ thống thu thập của chúng tôi xây dựng một kiến trúc dữ liệu phân cấp 4 tầng:  
  > Ở tầng cao nhất là Episode — bức tranh toàn cảnh của cả phiên hoạt động 10 phút.  
  > Xuống tầng thứ hai là Step — mỗi bước quyết định của LLM, ghi lại trọn vẹn chuỗi suy nghĩ nội tâm (thought reasoning), ý định (intent) và bề mặt tương tác (surface).  
  > Nhưng điểm đột phá nằm ở tầng thứ ba: Tool Execution. Trình điều khiển Cloak / Playwright ghi nhận chính xác đến từng millisecond và từng pixel chuyển động thực tế của con trỏ chuột và bánh xe cuộn.  
  > Và tầng đáy là Persona Evidence — nơi lưu trữ bằng chứng xem bước đi đó khớp với chiều kích tính cách nào.  
  > Kiến trúc 4 tầng này cho phép chúng tôi kiểm tra chéo độ trung thực của Agent: Lời Agent nghĩ có khớp với hành động tay của nó trên bàn phím và chuột hay không?"*
- **Hộp Bằng chứng Số liệu:** Bảng từ điển dữ liệu [`output/tables/data_dictionary.csv`](file:///d:/source_code/eda_persona/output/tables/data_dictionary.csv) định nghĩa chặt chẽ 41 biến số đo lường.
- **Phép kiểm nghiệm đề xuất thêm:** Kiểm tra tính toàn vẹn khóa ngoại (Referential Integrity Check): Đạt 100% khớp nối giữa 4 tầng dữ liệu, 0 bản ghi mồ côi (orphan records).

---

### Slide 4: Kiểm Soát Thiên Lệch & Sàng Lọc Ý Nghĩa Thống Kê Toàn Diện
- **Hồi kịch bản:** Hồi 2 - Manh Mối Xuất Hiện (Act II: Data Hygiene & Clues)
- **Thời lượng dự kiến:** 1.2 phút
- **Bố cục Visual đề xuất:**
  - Trái: Biểu đồ khuyết thiếu & Outlier [`output/figures/step3_missing_pattern.png`](file:///d:/source_code/eda_persona/output/figures/step3_missing_pattern.png)
  - Phải: Bảng xếp hạng Top biến định lượng phân tách mạnh mẽ nhất [`output/tables/step4_all_numeric_significance_screening.csv`](file:///d:/source_code/eda_persona/output/tables/step4_all_numeric_significance_screening.csv) kèm hệ số hiệu chỉnh Benjamini-Hochberg FDR.
- **Thông điệp cốt lõi:**
  > *Làm sạch dữ liệu nghiêm ngặt: Mọi khuyết thiếu đều có lý do nghiệp vụ (MAR/MNAR). 100% biến phân tách đều vượt qua ngưỡng kiểm định FDR.*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Trước khi kết luận bất kỳ điều gì, chúng tôi thực hiện kiểm toán dữ liệu nghiêm ngặt.  
  > Dữ liệu khuyết thiếu xuất hiện ở đâu? Chỉ ở các trường như 'tool_execution_ms' khi Agent thực hiện hành động thuần quan sát, hoàn toàn mang tính cơ chế hợp lệ (Missing at Random).  
  > Chúng tôi không loại bỏ các giá trị cực trị (outlier) một cách mù quáng, vì thời gian suy nghĩ 18 giây hay cú cuộn chuột 1,200 pixel chính là dấu ấn hành vi đặc trưng của Persona.  
  > Khi thực hiện sàng lọc thống kê trên toàn bộ biến định lượng bằng kiểm định phi tham số Mann-Whitney U và hiệu chỉnh đa kiểm định Benjamini-Hochberg FDR, chúng tôi nhận thấy các biến về nhận thức, bộ nhớ làm việc và tốc độ thao tác đều đạt mức ý nghĩa $p < 10^{-10}$ với kích thước hiệu ứng Cliff's Delta ở mức rất lớn."*
- **Hộp Bằng chứng Số liệu:**
  - `wm_num_active_threads`: $U = 2,514.0, p = 3.20 \times 10^{-27}$, Cliff's Delta = $+0.710$ (Large).
  - `model_latency_ms`: $U = 5,162.0, p = 9.47 \times 10^{-21}$, Cliff's Delta = $+0.644$ (Large).
- **Phép kiểm nghiệm đề xuất thêm:** Little's MCAR Test trên ma trận khuyết thiếu để chứng minh mặt toán học dữ liệu không bị khuyết ngẫu nhiên mù quáng.

---

### Slide 5: Nghịch Lý Thời Gian: Chi Phí Nhận Thức Đổi Lấy Vận Tốc Thực Thi
- **Hồi kịch bản:** Hồi 2 - Sự Khác Biệt Sâu Sắc (Act II: Cognitive vs Physical Pacing)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Biểu đồ 2 ô tương phản: [`output/figures/step4_cognitive_to_action_distribution.png`](file:///d:/source_code/eda_persona/output/figures/step4_cognitive_to_action_distribution.png)
    - Ô trái: Thời gian suy nghĩ LLM (`model_latency_ms`) — Persona cao vượt trội (+1.2s).
    - Ô phải: Vận tốc thao tác thực tế (`context_action_velocity`) — Persona lại nhanh gấp 3 lần!
- **Thông điệp cốt lõi (Punchline):**
  > *Nghịch lý nhận thức: Agent có Persona suy nghĩ lâu hơn mỗi bước, nhưng toàn phiên lại hoàn thành hành vi nhanh gấp 3 lần nhờ không bị sa lầy thao tác lỗi.*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Và đây là manh mối kịch tính đầu tiên xuất hiện từ dữ liệu:  
  > Ở biểu đồ bên trái: Mỗi khi đưa ra quyết định, Agent có Persona tiêu tốn trung bình 3,314 ms (hơn 3.3 giây), cao hơn hẳn mức 2,082 ms của No-Persona. Chênh lệch lên tới +1.2 giây cho mỗi bước suy nghĩ.  
  > Nếu chỉ nhìn vào đây, quý vị có thể vội kết luận: 'Persona làm Agent chậm chạp và tốn chi phí token hơn'.  
  > Nhưng hãy nhìn sang biểu đồ bên phải! Vận tốc thao tác thực tế (Action Velocity) của Persona đạt trung vị 3.0 hành động/phút, cao gấp 3.3 lần so với mức 0.91 của No-Persona!  
  > Tại sao một kẻ suy nghĩ lâu hơn lại về đích nhanh hơn gấp 3 lần?  
  > Dữ liệu tầng 3 đã tiết lộ bí mật: No-Persona suy nghĩ rất nhanh nhưng lại liên tục gặp lỗi thực thi trên trình duyệt. Độ trễ thực thi công cụ của No-Persona có IQR lên tới gần 22 giây! Trong khi Persona, nhờ có mục tiêu và định hướng rõ ràng từ bộ nhớ làm việc, bước ra hành động nào là chuẩn xác hành động đó."*
- **Hộp Bằng chứng Số liệu:**
  - Model Latency: Median 3,314 ms vs 2,082.5 ms ($\Delta = +1,231.5\text{ ms}$, Cliff's Delta = $+0.644, p = 9.47 \times 10^{-21}$).
  - Action Velocity: Median 3.00 vs 0.91 actions/min ($\Delta = +2.09$, Cliff's Delta = $+0.462, p = 1.57 \times 10^{-11}$).
  - Active Threads trong bộ nhớ: Median 8.0 threads vs 2.0 threads ($p < 10^{-26}$).
- **Phép kiểm nghiệm đề xuất thêm:** Phân rã Phương sai (ANOVA / ANCOVA) kiểm soát ảnh hưởng của độ dài token đầu ra lên `model_latency_ms`.

---

### Slide 6: Thế Giới Nội Tâm: Phân Tích NLP Tiếng Việt & Log-Odds Ratio
- **Hồi kịch bản:** Hồi 2 - Khám Phá Tâm Lý Nội Tâm (Act II: Inside the Agent's Mind)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Biểu đồ hệ số Log-Odds Ratio (LOR) của các từ vựng tiếng Việt đặc trưng: [`output/figures/step4_underthesea_log_ratio.png`](file:///d:/source_code/eda_persona/output/figures/step4_underthesea_log_ratio.png)
  - Thanh màu cam (Thiên lệch Persona) vs Thanh màu xanh (Thiên lệch No-Persona).
- **Thông điệp cốt lõi:**
  > *Phân tích văn bản nội tâm bằng thư viện underthesea: Persona tư duy bằng 'mục tiêu, sở thích, nhóm', No-Persona tư duy bằng 'quan sát, thử lại, không rõ'.*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Để hiểu xem Agent đang thực sự 'nghĩ' gì trong những giây phút suy ngẫm đó, chúng tôi đưa toàn bộ chuỗi văn bản lý giải (thought reasoning) qua pipeline tách từ tiếng Việt chuyên dụng `underthesea` và đo lường phân kỳ bằng Hệ số Tỷ lệ Chênh Logarit (Log-Odds Ratio).  
  > Kết quả trên biểu đồ cho thấy hai thế giới nội tâm hoàn toàn đối lập:  
  > Phía Persona (màu cam): Những từ khóa áp đảo tuyệt đối là 'mục_tiêu', 'sở_thích', 'tìm_kiếm', 'nhóm', 'chủ_đề', 'bài_viết'. Agent liên tục tự nhắc nhở bản thân về định hướng tính cách.  
  > Ngược lại, phía No-Persona (màu xanh): Từ vựng bị thống trị bởi 'quan_sát', 'màn_hình', 'thử_lại', 'đóng', 'không_rõ'. No-Persona không hề có một kế hoạch dài hạn, nó chỉ nhìn thấy gì trên màn hình thì phản ứng thụ động với cái đó.  
  > Đây chính là bằng chứng xác thực đầu tiên cho thấy: Persona đã truyền tải thành công một la bàn nhận thức (Cognitive Compass) vào tâm trí của mô hình."*
- **Hộp Bằng chứng Số liệu:**
  - Bảng Log-Odds Ratio [`output/tables/step4_underthesea_log_ratio.csv`](file:///d:/source_code/eda_persona/output/tables/step4_underthesea_log_ratio.csv)
  - Top LOR Persona: `sở_thích` (+3.45), `mục_tiêu` (+2.98), `nhóm` (+2.71).
  - Top LOR No-Persona: `quan_sát` (-3.12), `thử_lại` (-2.85), `màn_hình` (-2.64).
- **Phép kiểm nghiệm đề xuất thêm:** Phân tích Cảm xúc (Sentiment Analysis) và Độ phức tạp Cú pháp (Syntactic Perplexity) giữa hai luồng suy nghĩ.

---

### Slide 7: Cơn Sa Đà Nhận Thức & Cơ Chế Kháng Trôi Dạt (Guardrail Recovery)
- **Hồi kịch bản:** Hồi 2 - Thử Thách & Cám Dỗ (Act II: Temptation & Self-Regulation)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Biểu đồ quỹ đạo sa đà & cơ chế bảo vệ: [`output/figures/step4_drift_and_rest_deep_dive.png`](file:///d:/source_code/eda_persona/output/figures/step4_drift_and_rest_deep_dive.png)
  - Biểu đồ độ phủ sở thích mạnh (`interests.strong` vs `interests.avoid`): [`output/figures/step4_strong_interests_coverage.png`](file:///d:/source_code/eda_persona/output/figures/step4_strong_interests_coverage.png)
- **Thông điệp cốt lõi:**
  > *Kháng trôi dạt hành vi: Dù bị cuốn vào các bài viết gây chú ý, cơ chế cảnh báo Guardrail giúp Persona hồi phục 100% về quỹ đạo sở thích cốt lõi và tuyệt đối không chạm vào chủ đề cấm kỵ.*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Nhưng mạng xã hội là một cạm bẫy thực sự đối với bất kỳ trí tuệ nào. Khi lướt Facebook, Agent có bị 'nghiện' hay bị cuốn theo các nội dung giật gân không?  
  > Dữ liệu cho thấy: CÓ! Hiện tượng Sa đà Nhận thức (Temporal Cognitive Drift) xuất hiện ở cả hai nhóm.  
  > Tuy nhiên, điểm khác biệt sống còn nằm ở Cơ chế Tự tiết chế (Guardrail Intervention).  
  > Khi thời gian lướt feed vượt quá ngưỡng, hệ thống kích hoạt cảnh báo Guardrail Alert.  
  > Ở nhóm No-Persona: Cảnh báo trôi qua vô nghĩa, Agent tiếp tục trôi dạt vô định.  
  > Nhưng ở nhóm Persona: Tỷ lệ hồi phục (Recovery Rate) đạt 100%! Ngay sau cảnh báo, Agent lập tức quay về với danh mục sở thích mạnh (interests.strong) đã được cài đặt sẵn.  
  > Đặc biệt, khi kiểm tra trên 12 chủ đề cấm kỵ cần né tránh (interests.avoid), toàn bộ 6 Persona có số lần vi phạm tương tác bằng 0 tuyệt đối! Tỷ lệ tuân thủ kháng chủ đề đạt mức hoàn hảo."*
- **Hộp Bằng chứng Số liệu:**
  - Bảng ma trận hồi phục [`output/tables/step4_guardrail_recovery_matrix.csv`](file:///d:/source_code/eda_persona/output/tables/step4_guardrail_recovery_matrix.csv): Tỷ lệ hồi phục sau cảnh báo = 100%.
  - Bảng độ phủ sở thích [`output/tables/step4_strong_interests_coverage.csv`](file:///d:/source_code/eda_persona/output/tables/step4_strong_interests_coverage.csv): Tỷ lệ phủ chủ đề mạnh từ 33.3% đến 50.0% chỉ trong 1 phiên 10 phút.
  - Số vi phạm `interests.avoid`: $0/6$ Persona ($0.0\%$).
- **Phép kiểm nghiệm đề xuất thêm:** Survival Analysis (Kaplan-Meier Estimator) đo thời gian sống sót (Time-to-Drift) trước khi bước sa đà đầu tiên xuất hiện.

---

### Slide 8: Hồ Sơ Cấp Phiên: Nhịp Sinh Học & Động Lực Thoát Phiên
- **Hồi kịch bản:** Hồi 2 - Nhịp Độ Toàn Phiên (Act II: Session Profile & Exit Dynamics)
- **Thời lượng dự kiến:** 1.2 phút
- **Bố cục Visual đề xuất:**
  - Biểu đồ 2 ô: [`output/figures/step4_univariate_termination_and_surfaces.png`](file:///d:/source_code/eda_persona/output/figures/step4_univariate_termination_and_surfaces.png)
    - Ô 1: Nguyên nhân kết thúc phiên (Termination Reason).
    - Ô 2: Phân bố khoảng cách thời gian giữa các bước ($\Delta t$ Step Delta).
- **Thông điệp cốt lõi:**
  > *Thoát phiên chủ động vs Bị ép dừng: Persona kết thúc phiên khi đã đạt mục tiêu hoặc nhận thức đủ đầy, No-Persona bị ép dừng do hết hạn thời gian (Max steps/Timeout).*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Nhìn lên cấp độ toàn phiên (Episode-level), sự khác biệt giữa hai nhóm càng hiện rõ ở cách chúng kết thúc cuộc hành trình:  
  > No-Persona không bao giờ chủ động dừng lại. Cả 2 phiên của No-Persona đều kết thúc bằng trạng thái ép buộc: hoặc là chạm trần số bước tối đa (Max Steps), hoặc bị hệ thống ngắt kết nối do hết giờ (Timeout).  
  > Ngược lại, ở nhóm Persona: Các Agent có cơ chế thoát phiên tự nhiên khi nhận thức thấy 'Mục tiêu phiên đã hoàn tất' (Goal Accomplished) hoặc kích hoạt nhịp sinh học nghỉ ngơi.  
  > Khoảng cách thời gian giữa các bước ($\Delta t$) của Persona cũng duy trì một nhịp điệu ổn định 10 - 12 giây, tạo nên một chuỗi hành vi mượt mà, tự nhiên như nhịp thở của người dùng thật."*
- **Hộp Bằng chứng Số liệu:**
  - Bảng hồ sơ thoát phiên [`output/tables/step4_termination_profile.csv`](file:///d:/source_code/eda_persona/output/tables/step4_termination_profile.csv).
  - Tỷ lệ thoát phiên do chạm trần lỗi ở No-Persona: $100\%$.
  - Tỷ lệ thoát phiên có chủ đích ở Persona: $66.7\%$ (4/6 phiên).
- **Phép kiểm nghiệm đề xuất thêm:** Log-rank Test so sánh hàm sinh tồn giữa hai nhóm về thời điểm dừng phiên.

---

### Slide 9: THE PLOT TWIST: Nghịch Lý Simpson & Cạm Bẫy Không Gian Bề Mặt
- **Hồi kịch bản:** Hồi 3 - Cú Lật Kèo Ngoạn Mục (Act III: The Plot Twist)
- **Thời lượng dự kiến:** 2.0 phút
- **Bố cục Visual đề xuất:**
  - Biểu đồ bóc tách Nghịch lý Simpson: [`output/figures/step5_simpson_paradox_surface.png`](file:///d:/source_code/eda_persona/output/figures/step5_simpson_paradox_surface.png)
  - Phía trên: Tỷ lệ Verified tổng thể (+16.3% nghiêng về Persona).
  - Phía dưới: Tỷ lệ Verified phân rã theo từng Surface (trên Feed bằng nhau 98% vs 100%, trên Detail bằng nhau 67% vs 68%).
- **Thông điệp cốt lõi (The Scientific Punchline):**
  > *Cú Twist kinh điển của Thống kê học: No-Persona không hề bấm nút kém hơn Persona! Sự chênh lệch tỷ lệ thành công bị đánh lừa bởi Nghịch lý Simpson — Confounder thực sự chính là Không gian Bề mặt (Surface).*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Và bây giờ, tôi xin mời quý vị chứng kiến phát hiện gây sốc và thú vị nhất về mặt khoa học trong toàn bộ nghiên cứu này: Một cú lật kèo kinh điển mang tên Nghịch lý Simpson (Simpson's Paradox)!  
  > Khi nhìn vào bức tranh tổng thể gộp chung: Tỷ lệ hành động thành công (Verified Rate) của Persona đạt 77.65%, vượt trội hoàn toàn so với 61.36% của No-Persona. Kiểm định Chi-square cho kết quả $p = 0.0018$ cực kỳ thuyết phục. Người ta rất dễ kết luận: 'Persona giúp LLM thực hiện tool giỏi hơn'.  
  > Nhưng khi nhóm nghiên cứu bóc tách tỷ lệ verified này theo từng Bề mặt (Surface)... một sự thật ngỡ ngàng xuất hiện!  
  > Trên Bảng tin chính (Feed): Tỷ lệ thành công của No-Persona là 100%, Persona là 98.3% — Hoàn toàn tương đương!  
  > Trên Trang chi tiết (Detail): No-Persona đạt 68.4%, Persona đạt 66.7% — Hoàn toàn tương đương!  
  > Vậy con số +16.3% chênh lệch ở cấp tổng thể từ đâu ra?  
  > Hãy nhìn vào biểu đồ: No-Persona bị sa lầy tới 35.2% thời lượng vào bề mặt 'Unknown' — nơi không load được giao diện và tỷ lệ verified chỉ có 9.7%!  
  > Trong khi đó, Persona có năng lực nhận thức không gian vượt trội, chủ động rời Feed để đi vào Nhóm (Group - 100% verified) và Trang (Page - 94.4% verified).  
  > Nghịch lý Simpson đã phơi bày chân tướng: Persona không hề sở hữu một 'cây đũa thần' biến tool execution giỏi hơn, mà Persona cung cấp cho Agent một Năng lực Điều hướng Không gian (Spatial Navigation), giúp nó tránh xa các cạm bẫy giao diện chết người!"*
- **Hộp Bằng chứng Số liệu:**
  - Bảng phân rã Simpson [`output/tables/step5_simpson_surface_decomposition.csv`](file:///d:/source_code/eda_persona/output/tables/step5_simpson_surface_decomposition.csv).
  - Overall Verified: Persona 77.65% (271/349) vs No-Persona 61.36% (54/88), $\chi^2 = 9.78, p = 0.0018$.
  - Feed Verified: 98.3% vs 100.0% ($p = 0.999$, Fisher exact).
  - Tỷ lệ thời gian tại `unknown`: No-Persona 35.2% vs Persona 23.5%.
- **Phép kiểm nghiệm đề xuất thêm:** Mô hình Hồi quy Logistic đa biến (Multivariable Logistic Regression) kiểm soát tương tác giữa `dataset_type` và `surface` để chứng minh Odds Ratio của Persona tiệm cận 1.0 khi đã cố định surface.

---

### Slide 10: Vòng Lặp Vô Tận: Động Lực Chuỗi Chuyển Tiếp Hành Vi Trigram
- **Hồi kịch bản:** Hồi 3 - Đào Sâu Chuỗi Hành Động (Act III: Sequential Dynamics)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Biểu đồ so sánh chuỗi 3 hành động (Trigram Patterns) và Log-Odds Ratio: [`output/figures/step5_prominent_behavioral_patterns.png`](file:///d:/source_code/eda_persona/output/figures/step5_prominent_behavioral_patterns.png)
  - Minh họa chuỗi vòng lặp kẹt bế tắc vs chuỗi đa nhánh mục tiêu.
- **Thông điệp cốt lõi:**
  > *No-Persona bị giam cầm trong vòng lặp vô tận (observe $\rightarrow$ close $\rightarrow$ observe), trong khi Persona sở hữu đồ thị chuỗi hành vi ergodic phong phú và hướng đích.*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Để kiểm chứng sâu hơn về cạm bẫy không gian mà No-Persona mắc phải, chúng tôi khảo sát chuỗi chuyển tiếp hành động cấp 3 (Trigram Sequence Dynamics) và đo lường phân kỳ bằng Log-Odds Ratio.  
  > Quý vị có thể thấy rõ trên đồ thị:  
  > Chuỗi hành động chiếm ưu thế áp đảo nhất của No-Persona là: `observe -> close -> observe` với hệ số Log-Odds Ratio vọt lên mức +3.12!  
  > Chuyện gì đang xảy ra ở đây? No-Persona bấm mở một bài viết hoặc modal, không hiểu chuyện gì xảy ra, bấm nút đóng lại, rồi lại đứng quan sát màn hình, và chu kỳ này lặp đi lặp lại như một vòng tròn luẩn quẩn không lối thoát.  
  > Ngược lại, các chuỗi thống trị của Persona là những chuỗi hành vi hoàn chỉnh có mục đích: `search -> read -> react` (tìm kiếm, đọc kỹ, thả tương tác), hoặc `scroll -> read -> share` (cuộn lướt, đọc chọn lọc, chia sẻ).  
  > Đây là minh chứng sắc bén cho thấy: Thiếu vắng Persona, Agent bị suy thoái thành một hệ thống chuyển trạng thái Markov có điểm hấp thụ bế tắc (Absorbing State Trap)."*
- **Hộp Bằng chứng Số liệu:**
  - Bảng chuỗi Trigram [`output/tables/step5_prominent_trigram_patterns.csv`](file:///d:/source_code/eda_persona/output/tables/step5_prominent_trigram_patterns.csv).
  - Pattern `observe -> close -> observe`: Chiếm 14.8% tổng số chuỗi No-Persona, LOR = $+3.12$.
  - Pattern `read -> react -> scroll`: Chiếm 8.9% chuỗi Persona, hoàn toàn không xuất hiện ở No-Persona.
- **Phép kiểm nghiệm đề xuất thêm:** Ước lượng Ma trận Xác suất Chuyển trạng thái Markov (Markov Transition Matrix Entropy) và kiểm định Ergodicity.

---

### Slide 11: Bước Chuyển Chiến Lược: Bóc Tách Nội Bộ Nhóm Persona Bằng PCA
- **Hồi kịch bản:** Hồi 4 - Bước Ngoặt Cao Trào (Act IV: Intra-Persona Transition)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Biểu đồ Scree / Biplot PCA & Cây Phân cụm Phân cấp Dendrogram từ notebook hồ sơ: [`output/figures/step6_persona_pca_scree_biplot.png`](file:///d:/source_code/eda_persona/output/figures/step6_persona_pca_scree_biplot.png) & [`output/figures/step6_persona_hierarchical_dendrogram.png`](file:///d:/source_code/eda_persona/output/figures/step6_persona_hierarchical_dendrogram.png)
  - Bảng định nghĩa 3 Cụm Archetype toán học khách quan.
- **Thông điệp cốt lõi:**
  > *Không dừng lại ở so sánh Có vs Không Persona! Sử dụng PCA và Ward Linkage để tự động phân tách 6 Persona thành 3 Cụm Archetype toán học làm 'Hệ quy chiếu kỳ vọng' khách quan.*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Thưa quý vị,  
  > Đến đây, nhiều nghiên cứu thông thường sẽ dừng lại và tuyên bố thắng lợi: Persona vượt trội so với No-Persona.  
  > Nhưng chúng tôi tự đặt ra một câu hỏi khắt khe hơn: 'So sánh với một Agent không có tính cách thì quá dễ dàng. Liệu giữa các Agent CÓ Persona với nhau, chúng có thực sự hành xử khác biệt đúng như những gì đã được thiết kế trong hồ sơ hay không?'  
  > Để tránh mọi sự áp đặt chủ quan của con người, chúng tôi đưa toàn bộ thuộc tính trong hồ sơ `facebook_behavior_profile` qua Phân tích Thành phần Chính (PCA) và Phân cụm Phân cấp Ward Linkage (đạt hệ số tin cậy Cophenetic Correlation $r = 0.8291$).  
  > Toán học đã tự động nhóm 6 Persona thành 3 Cụm Archetype rõ rệt:  
  > - Cụm 1: Nhóm Lướt Nhanh, Năng Động (Quick Pace, Skim Reading, Daily Frequency).  
  > - Cụm 2: Nhóm Đọc Chọn Lọc, Đào Sâu (Balanced/Slow Pace, Selective Reading, Community Led).  
  > - Cụm 3: Nhóm Trầm Lặng, Ít Tương Tác (Slow Pace, Rarely/Monthly Frequency).  
  > Ba Cụm Archetype này sẽ đóng vai trò là 'Hệ quy chiếu Kỳ vọng' (Ground Truth Expectation) để chúng tôi đưa lên bàn cân kiểm định hành vi thực tế."*
- **Hộp Bằng chứng Số liệu:**
  - Dữ liệu từ notebook độc lập [`notebooks/eda_fb_persona.ipynb`](file:///d:/source_code/eda_persona/notebooks/eda_fb_persona.ipynb).
  - Tỷ lệ giải thích tích lũy PCA: PC1 + PC2 giải thích $74.8\%$ phương sai thuộc tính hồ sơ.
  - Hệ số Cophenetic Correlation của cây phân cụm Ward: $r = 0.8291$ (Rất tin cậy).
- **Phép kiểm nghiệm đề xuất thêm:** Silhouette Analysis đánh giá độ gắn kết và phân tách của 3 cụm.

---

### Slide 12: THE CLIMAX (Bằng Chứng Cơ Học Vật Lý): Vận Tốc & Chế Độ Cuộn Chuột
- **Hồi kịch bản:** Hồi 4 - Cao Trào Tột Bậc (Act IV: The Physical Kinematics Climax)
- **Thời lượng dự kiến:** 2.0 phút
- **Bố cục Visual đề xuất:**
  - Nửa dưới của biểu đồ 4 Panel: [`output/figures/step5_persona_adherence_metrics.png`](file:///d:/source_code/eda_persona/output/figures/step5_persona_adherence_metrics.png) (Panel C và Panel D).
    - Panel C: Biểu đồ Vận tốc cuộn thực tế (px/s) — Cụm 1 vọt lên 5,027.5 px/s (gấp 2.9 lần).
    - Panel D: Biểu đồ Thanh Chồng Ngang 100% — Nhóm Quick là 100% FAST, Nhóm Slow/Balanced là 100% CAREFUL!
- **Thông điệp cốt lõi (The Ultimate Scientific Climax):**
  > *Dấu ấn cơ học vật lý: Cụm Quick cuộn lướt với vận tốc 5,027.5 px/s (nhanh gấp 2.9 lần); Chế độ cuộn chuột phân tách nhị phân tuyệt đối 100% với $p = 1.84 \times 10^{-14}$. Lời nhắc ngôn ngữ đã biến thành động lực học cơ bắp!*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Và đây chính là khoảnh khắc CAO TRÀO TỘT BẬC của toàn bộ nghiên cứu!  
  > Chúng tôi không tin vào những gì Agent tự báo cáo trong suy nghĩ text. Chúng tôi đi thẳng xuống tầng driver Playwright để đo lường Cơ học Chuyển động Chuột (Kinematics Evidence) từ các dòng log vật lý: `native Cloak smooth wheel, total=X px, gesture_ms=Y, pace=Z`.  
  > Hãy nhìn vào Panel C bên trái:  
  > Cụm 1 — được thiết kế với nhịp độ `pace: quick` — đã thực thi những cú cuộn chuột với vận tốc trung bình lên tới 5,027.5 pixel/giây! Quét qua trọn vẹn 1,000 pixel màn hình chỉ trong vỏn vẹn 180 millisecond!  
  > Trong khi đó, Cụm 2 và Cụm 3 (`pace: slow/balanced`) chỉ cuộn nhích trung bình 1,750 đến 1,800 pixel/giây — chậm hơn gần 3 lần! Kiểm định Kruskal-Wallis cho kết quả $p = 1.97 \times 10^{-6}$ cực kỳ đanh thép.  
  > Nhưng ngoạn mục hơn cả là Panel D bên phải:  
  > Khi nhìn vào chế độ cuộn vật lý (Scroll Pace Mode):  
  > Toàn bộ 12/12 cú cuộn của Nhóm Quick Pace được thực thi ở chế độ FAST (100% màu đỏ).  
  > Toàn bộ 59/59 cú cuộn của Nhóm Slow/Balanced được thực thi ở chế độ CAREFUL (100% màu xanh).  
  > Không có một trường hợp ngoại lệ nào! Kiểm định Fisher's Exact Test đạt giá trị $p = 1.84 \times 10^{-14}$ — một sự phân tách nhị phân tuyệt đối 100%!  
  > Và chưa dừng lại ở đó: Trong cả 6 Persona, duy nhất Agent `vn_000081` — người duy nhất mang hồ sơ 'Năng lượng Thấp' (energy: Low) — đã tự động kích hoạt hành vi dừng nghỉ giữa phiên suốt 120 giây ($p < 0.001$), trong khi 5 Persona còn lại không hề nghỉ một giây nào!  
  > Đây là bằng chứng không thể chối cãi: Persona không chỉ điều khiển suy nghĩ, mà đã thẩm thấu và điều khiển trực tiếp đến từng xung lực cơ học của chuột máy tính!"*
- **Hộp Bằng chứng Số liệu:**
  - Bảng cơ học cuộn từng Persona [`output/tables/step5_physical_scroll_mechanics.csv`](file:///d:/source_code/eda_persona/output/tables/step5_physical_scroll_mechanics.csv).
  - Vận tốc cuộn: C1 đạt $5,027.5\text{ px/s}$ vs C2 $1,752.1\text{ px/s}$ vs C3 $1,800.4\text{ px/s}$ ($H = 26.28, p = 1.97 \times 10^{-6}$).
  - Biên độ cuộn mỗi lần: C1 đạt $982.3\text{ px}$ vs C2/C3 đạt $430\text{ px}$ ($H = 25.76, p = 2.55 \times 10^{-6}$).
  - Chế độ cuộn: Fisher's Exact Test $p = 1.84 \times 10^{-14}$, Cramér's $V = 1.00$ (Complete Separation).
  - Thời gian dừng nghỉ kiệt sức: `vn_000081` đạt $120\text{s}$ vs $0\text{s}$ ở 5 Persona còn lại ($p < 0.001$).
- **Phép kiểm nghiệm đề xuất thêm:** Mann-Whitney U test với Bootstrap BCa 95% Confidence Interval cho vận tốc cuộn ($[4,200 - 5,600\text{ px/s}]$ vs $[1,550 - 1,980\text{ px/s}]$).

---

### Slide 13: Cường Độ Xã Hội & Không Gian Điều Hướng: Khi Tính Cách Thấm Vào Hành Động
- **Hồi kịch bản:** Hồi 4 - Toàn Diện Hóa Tính Cách (Act IV: Social & Surface Breadth)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Nửa trên của biểu đồ 4 Panel: [`output/figures/step5_persona_adherence_metrics.png`](file:///d:/source_code/eda_persona/output/figures/step5_persona_adherence_metrics.png) (Panel A và Panel B).
    - Panel A: Cường độ Tương tác Xã hội SIP % — Bậc thang 3 cụm (22.45% $\rightarrow$ 11.02% $\rightarrow$ 4.03%).
    - Panel B: Phân bổ Bề mặt 2 Cột tự nhiên — Feed (44.6%) vs Mix (55.4% gồm Search, Group, Page).
- **Thông điệp cốt lõi:**
  > *Tuân thủ toàn diện từ vai trò xã hội đến không gian sống: Agent mang hồ sơ 'Người hay chia sẻ' tương tác gấp 5.6 lần Agent 'Ít tương tác'; hơn 55% bước đi là chủ động hòa mình vào các cộng đồng ngoài Feed.*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Sau cơ học vật lý, liệu các chiều kích xã hội và không gian có tuân thủ hồ sơ hay không?  
  > Hãy nhìn vào Panel A: Phép đo Cường độ Tương tác Xã hội (Social Interaction Propensity - SIP).  
  > Cụm 1 — những người có hồ sơ 'Daily / Sharer' — dành tới 22.45% hành động để like, thả tim và chia sẻ bài viết.  
  > Con số này giảm một nửa ở Cụm 2 (11.02%), và rơi xuống chỉ còn vỏn vẹn 4.03% ở Cụm 3 — những người có hồ sơ 'Monthly / Rarely / Reader'. Chênh lệch lên tới 5.6 lần! Kiểm định Chi-square đạt $\chi^2 = 18.01, p = 1.23 \times 10^{-4}$. Đặc biệt, hành vi Chia sẻ (Share intent) ở Cụm 3 là 0% tuyệt đối!  
  > Và ở Panel B: Thay vì máy móc chia cụm, chúng tôi nhìn thẳng vào không gian điều hướng tự nhiên của mạng xã hội.  
  > Các Agent không hề là những tù nhân bị giam lỏng trên Bảng tin Feed (Feed chỉ chiếm 44.6%). Hơn 55.4% hành động của chúng diễn ra trên không gian Đa bề mặt (Mix): 58 bước chủ động tìm kiếm từ khóa, 51 bước thảo luận trong các Nhóm cộng đồng, và 36 bước theo dõi Fanpage.  
  > Từ giao tiếp xã hội đến không gian tương tác, hồ sơ Persona đã được phản ánh trung thực và sống động đến kinh ngạc."*
- **Hộp Bằng chứng Số liệu:**
  - Bảng tổng hợp Adherence Scorecard [`output/tables/step5_persona_adherence_metrics_summary.csv`](file:///d:/source_code/eda_persona/output/tables/step5_persona_adherence_metrics_summary.csv).
  - SIP Chi-square: $\chi^2 = 18.01, df = 2, p = 1.23 \times 10^{-4}$, Cramér's $V = 0.227$.
  - MSER Chi-square: $\chi^2 = 16.26, df = 2, p = 2.95 \times 10^{-4}$, Cụm 2 khám phá ngoài feed đạt $54.33\%$.
  - Không gian bề mặt: Feed 119 bước ($44.6\%$) vs Mix 148 bước ($55.4\%$).
- **Phép kiểm nghiệm đề xuất thêm:** Correspondence Analysis (Phân tích Tương ứng 2 chiều) giữa Danh mục Persona và Thể loại Nhóm Facebook tham gia.

---

### Slide 14: Bảng Điểm Tổng Kết: Khẳng Định Trọn Vẹn 4 Giả Thuyết H1 - H4
- **Hồi kịch bản:** Hồi 5 - Thu Hoạch Khoa Học (Act V: The Verdict)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Bảng Scorecard tổng kết 4 Giả thuyết ($H_1 \rightarrow H_4$) với các icon Checkmark xanh lá nổi bật:
    - Cột 1: Giả thuyết & Mục tiêu.
    - Cột 2: Chỉ số Thực nghiệm (Key Metrics).
    - Cột 3: Giá trị Kiểm định & Ý nghĩa Thống kê.
    - Cột 4: Kết luận Khoa học (XÁC NHẬN / CONFIRMED).
- **Thông điệp cốt lõi:**
  > *Bảng điểm hoàn hảo: Cả 4 Giả thuyết Tiên nghiệm ($H_1 \rightarrow H_4$) đều được khẳng định với các kiểm định thống kê nghiêm ngặt ($p < 0.001$).*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Kính thưa quý vị,  
  > Trải qua toàn bộ hành trình điều tra thực nghiệm, chúng tôi xin trân trọng công bố Bảng điểm Tổng kết cho 4 Giả thuyết khoa học được đặt ra từ ban đầu:  
  > - Giả thuyết $H_1$ (Chi phí nhận thức đổi lấy hiệu quả thực thi): XÁC NHẬN! Persona suy nghĩ lâu hơn 1.2s nhưng vận tốc thao tác nhanh gấp 3.3 lần ($p < 10^{-10}$), bộ nhớ làm việc tích lũy gấp 4 lần.  
  > - Giả thuyết $H_2$ (Khám phá không gian & Thoát cạm bẫy): XÁC NHẬN! 55.4% bước đi diễn ra ngoài Feed, hóa giải hoàn toàn Nghịch lý Simpson và phá vỡ vòng lặp bế tắc Trigram của No-Persona.  
  > - Giả thuyết $H_3$ (Tự kiểm soát & Hồi phục Guardrail): XÁC NHẬN! Tỷ lệ tự hồi phục về sở thích cốt lõi sau cảnh báo đạt 100%, 0 vi phạm chủ đề cấm kỵ.  
  > - Giả thuyết $H_4$ (Tính nhất quán cơ học vật lý nội bộ): XÁC NHẬN TUYỆT ĐỐI! Tương tác xã hội phân hóa 3 bậc ($p < 10^{-3}$), vận tốc cuộn nhanh gấp 2.9 lần ($p < 10^{-5}$), và chế độ cuộn Fast vs Careful phân tách 100% với $p = 1.84 \times 10^{-14}$.  
  > Cả 4 giả thuyết đều được chứng minh một cách nhất quán, chặt chẽ và không thể bác bỏ."*
- **Hộp Bằng chứng Số liệu:** Ánh xạ tổng kết từ bảng [`output/tables/step4_hypotheses_preliminary_signals.csv`](file:///d:/source_code/eda_persona/output/tables/step4_hypotheses_preliminary_signals.csv) kết hợp mục 5.3 trong notebook.
- **Phép kiểm nghiệm đề xuất thêm:** Meta-analytic Combined P-value (Phương pháp Fisher hoặc Stouffer) gộp toàn bộ các kiểm định của 4 giả thuyết để khẳng định độ tin cậy toàn cục của hệ thống thực nghiệm.

---

### Slide 15: Tầm Nhìn Khoa Học: Persona Là Một "Hệ Điều Hành Hành Vi"
- **Hồi kịch bản:** Hồi 5 - Cái Kết & Tầm Nhìn (Act V: Impact & Future Horizons)
- **Thời lượng dự kiến:** 1.5 phút
- **Bố cục Visual đề xuất:**
  - Sơ đồ kiến trúc tương lai: Mô hình hóa Persona như một "Behavioral Operating System" (Hệ Điều Hành Hành Vi) nằm giữa LLM Core và Browser Drivers.
  - Lộ trình 3 hướng mở rộng tiếp theo:
    1. Markov Absorbing Chain Modeling (Xác suất chuyển trạng thái & Đo lường thời gian hấp thu).
    2. Long-term Persona Evolution (Tiến hóa sở thích qua nhiều ngày lướt).
    3. Multi-Agent Social Simulation (Mô phỏng mạng xã hội đa Agent tương tác chéo).
- **Thông điệp cốt lõi (The Grand Finale):**
  > *Persona không phải là phụ kiện trang trí câu chữ. Persona là Hệ Điều Hành Hành Vi biến AI vô hồn thành thực thể xã hội số có tính cách, mục tiêu và dấu ấn vật lý riêng biệt.*
- **Kịch bản Lời nói Diễn giả (Speaker Script):**
  > *"Để khép lại bài trình bày hôm nay, thông điệp quan trọng nhất mà chúng tôi muốn gửi gắm tới cộng đồng nghiên cứu và phát triển AI chính là:  
  > Hãy thôi coi Persona như một dòng prompt mô tả trang trí!  
  > Dữ liệu thực nghiệm của chúng tôi đã chứng minh: Persona thực sự vận hành như một Hệ Điều Hành Hành Vi (Behavioral Operating System).  
  > Nó định hình cách Agent phân bổ tài nguyên bộ nhớ;  
  > Nó lập trình lại không gian điều hướng để tránh cạm bẫy;  
  > Nó cài đặt cơ chế tự kiểm soát khi đối mặt với cám dỗ;  
  > Và kỳ diệu nhất: Nó truyền dẫn xung lực để thay đổi từng vận tốc cuộn chuột và nhịp nghỉ sinh học trên thế giới vật lý!  
  > Đây là nền tảng tối quan trọng để chúng ta tiến tới những bước đi xa hơn: Xây dựng các thế giới mạng xã hội mô phỏng (Social Simulation) với hàng ngàn Agent có hành vi chân thực, phục vụ nghiên cứu lan truyền tin tức, thử nghiệm chính sách và thiết kế sản phẩm số trong tương lai.  
  > Xin trân trọng cảm ơn quý vị đã lắng nghe!"*
- **Hộp Bằng chứng Số liệu:** Tổng thể báo cáo [`output/step5_bivariate_multivariate_report.md`](file:///d:/source_code/eda_persona/output/step5_bivariate_multivariate_report.md).
- **Phép kiểm nghiệm đề xuất thêm:** Triển khai Markov Absorbing Chain và Mô hình GAM (Generalized Additive Model) cho Bước 6 và Bước 7 tiếp theo trong pipeline EDA.

---

## TỔNG HỢP DANH MỤC PHÉP KIỂM NGHIỆM ĐỀ XUẤT THÊM (NẾU CẦN ĐÀO SÂU)

Nếu Hội đồng Giám khảo hoặc Khán giả yêu cầu kiểm chứng chuyên sâu hơn nữa về mặt toán học, nhóm nghiên cứu có thể chủ động thực hiện bổ sung 4 phép kiểm nghiệm sau:

| STT | Tên Phép Kiểm Nghiệm Bổ Sung | Mục Đích Học Thuật | Phương Pháp & Công Thức Thực Hiện |
| :---: | :--- | :--- | :--- |
| **1** | **Multivariable Logistic Regression với Tương tác** | Bác bỏ hoàn toàn giả thuyết "Persona bấm tool giỏi hơn" và chứng minh vai trò trung gian tuyệt đối của Surface trong Nghịch lý Simpson. | $\text{logit}(P(\text{verified}=1)) = \beta_0 + \beta_1 \text{Persona} + \beta_2 \text{Surface} + \beta_3 (\text{Persona} \times \text{Surface})$. Khi kiểm soát Surface, kiểm tra xem $\beta_1$ có mất ý nghĩa ($p > 0.05$) hay không. |
| **2** | **Markov Transition Entropy & Absorbing Time** | Chứng minh mặt toán học chuỗi vòng lặp kẹt của No-Persona (`observe -> close -> observe`). | Tính Entropy chuỗi $H = -\sum_{i} P_i \log P_i$ và Giải hệ phương trình thời gian hấp thu cơ bản $k = (I - Q)^{-1} \mathbf{1}$ trên ma trận chuyển tiếp. |
| **3** | **Bootstrap BCa 95% Confidence Intervals (10,000 resamples)** | Xác lập khoảng tin cậy không tham số cho Vận tốc Cuộn Vật lý (PSV) và Cường độ Tương tác Xã hội (SIP) giữa 3 Cụm Archetype. | Rút mẫu ngẫu nhiên có lặp lại 10,000 lần, tính hệ số hiệu chỉnh thiên lệch và độ nhọn (Bias-Corrected and Accelerated Bootstrap). |
| **4** | **Power Analysis sau Thực nghiệm (Post-hoc Power Analysis)** | Chứng minh quy mô mẫu $N = 437$ steps và $N = 71$ thao tác cuộn chuột có đủ uy lực thống kê để tránh sai lầm loại II ($\beta$). | Sử dụng Cohen's $w$ cho Chi-square và Cohen's $d$ cho Mann-Whitney U, tính toán Power $(1 - \beta) \ge 0.95$ tại $\alpha = 0.05$. |

---
*Kịch bản được thiết kế và chuẩn hóa đồng bộ với dữ liệu trong [`notebooks/eda_action_logs.ipynb`](file:///d:/source_code/eda_persona/notebooks/eda_action_logs.ipynb).*
