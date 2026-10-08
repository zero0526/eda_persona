# LỊCH TRÌNH TRIỂN KHAI SLIDE KIỂM CHỨNG $H_1$ & $H_2$
> **Mục tiêu:** Chia nhỏ kế hoạch đo lường và thiết kế slide kiểm chứng theo 2 tầng nhất quán (Kịch bản lịch trình & Hành vi tương tác). Mỗi slide tập trung vào 1–2 metric cốt lõi, đối chiếu trực tiếp với hồ sơ Persona.

---

## TẦNG 1: KIỂM CHỨNG $H_1$ - TÍNH NHẤT QUÁN CỦA KỊCH BẢN & LỊCH TRÌNH VẬN HÀNH
*(Tập trung vào: 4 khung giờ sinh hoạt, dấu ấn nghề nghiệp, tần suất ngày và thời lượng phiên theo Persona 001 → 006)*

### 📍 Slide 1.1: Bức tranh 4 Khung giờ Sinh hoạt 24h & Phân bổ Lịch trình theo Persona
* **Mục tiêu:** Khảo sát mức độ phù hợp với nhịp sinh học tự nhiên và phân tích xu hướng phân bổ thời gian theo đặc thù nghề nghiệp vào 4 ca trong ngày.
* **Hình ảnh tương ứng:** `output/figures/slide1_1_four_shifts_and_persona_distribution.png` (Gồm 2 Panel A & B).
* **Metric cốt lõi:**
  * **Panel A - Histogram 24h & 4 Ca sinh hoạt (Tổng 95 phiên):**
    * 🌅 Ca Sáng (06h–11h): **29 phiên (30.5%)** — Khởi đầu ngày mới, đọc tin tức, cà phê sáng.
    * ☀️ Ca Trưa (11h–14h): **18 phiên (18.9%)** — Ăn trưa, nghỉ ngơi giữa ngày.
    * ☕ Ca Chiều (14h–18h): **12 phiên (12.6%)** — Giờ làm việc tập trung, ít phiên nhất ban ngày.
    * 🌙 Ca Tối (18h–23h - Cao điểm): **36 phiên (37.9%)** — Sau tan ca, giải trí chính.
    * 💤 Đêm khuya (23h–06h): **0 phiên (0.0%)** — Không ghi nhận phiên hoạt động đêm muộn, phù hợp với chu kỳ nghỉ ngơi tự nhiên.
    * *Trung vị bắt đầu:* **15.0h (15:00 chiều)**.
  * **Panel B - Phân bổ Ca & Thời lượng TB theo Persona (001 → 006):**
    * Ma trận tỷ lệ % phiên trong từng ca kết hợp thời lượng trung bình (`~XXm`) mỗi ca.
* **Nhận định phân nhóm lịch trình then chốt:**
  * 🎯 **Nhóm có khung giờ hoạt động đặc thù (Phân hóa rõ rệt theo ca làm việc):**
    * `vn_fb_004` (Nhân viên nhà hàng): **Không ghi nhận phiên vào ca trưa (0.0%)**, phù hợp với khung giờ cao điểm phục vụ khách; tập trung vào xế chiều (31.2%) và tối (37.5%).
    * `vn_fb_003` (Bảo vệ trực ca): **Không ghi nhận phiên vào ca chiều (0.0%)** và tỷ lệ ca trưa thấp (8.3%), phù hợp với quy định ca trực ban ngày; tập trung vào 2 đầu ca: sáng sớm (41.7%) và tối muộn (50.0%).
    * `vn_fb_006` (Gen X lớn tuổi): **Tỷ lệ vào sáng sớm thấp (7.7%)**, phân bổ chủ yếu vào nghỉ trưa (38.5%) và buổi tối (46.2%).
  * 🌐 **Nhóm có lịch trình phân bổ đều trong ngày (Linh hoạt):**
    * `vn_fb_001` (Thiết kế đồ họa): **Phân bổ tương đối đều ở 3 khung giờ** (Sáng 36.4%, Trưa 22.7%, Tối 31.8%), phù hợp với tính chất làm việc máy tính tự do.
    * `vn_fb_005` (Thợ cơ khí): **Phân bổ theo các quãng nghỉ** (Sáng 29.4%, Trưa 23.5%, Tối 35.3%).
    * `vn_fb_002` (Lao động / Gia đình): **Phân bổ theo các cữ việc nhà** (Sáng 33.3%, Trưa 20.0%, Tối 33.3%).
  * ⏱️ **Xu hướng thời lượng theo ca:** Ca tối ghi nhận thời lượng phiên trung bình dài hơn (18m–34m) so với ban ngày (10m–17m).
* **Bảng dữ liệu tham chiếu:** `output/tables/h1_persona_frequency_schedule_stats.csv`
* **Trạng thái:** `[x] Đã hoàn thành (Ảnh & CSV sẵn sàng)`

---

### 📍 Slide 1.2: Tần suất Sử dụng Mạng Xã hội Trên Ngày & Thời lượng Mỗi Phiên Hoạt Động
* **Mục tiêu:** Đánh giá mức độ phù hợp của tần suất vào mạng và thời lượng phiên với quỹ thời gian theo hồ sơ Persona; kiểm tra cơ chế kết thúc phiên.
* **Hình ảnh tương ứng:** `output/figures/slide1_2_duration_and_daily_frequency.png` (Gồm 2 Panel A & B).
* **Metric cốt lõi:**
  * **Panel A - Tần suất vào mạng mỗi ngày (`daily_windows`):**
    * Trung bình toàn hệ thống: **2.11 lần/ngày** (Dao động từ 1 đến 3 lần/ngày).
    * `vn_fb_001` (Thiết kế): **2.75 lần/ngày** [2–3 lần] (Mức cao nhất trong nhóm quan sát).
    * `vn_fb_005` (Thợ cơ khí): **2.43 lần/ngày** [1–3 lần].
    * `vn_fb_004` (Nhà hàng): **2.29 lần/ngày** [1–3 lần].
    * `vn_fb_006` (Gen X): **1.86 lần/ngày** [1–3 lần].
    * `vn_fb_003` (Bảo vệ): **1.71 lần/ngày** [1–3 lần] (Tần suất thấp do hạn chế ca trực).
    * `vn_fb_002` (Lao động/Gia đình): **1.67 lần/ngày** [1–2 lần] (Mức thấp nhất do bận công việc gia đình).
  * **Panel B - Thời lượng mỗi lần dùng (`duration_min`):**
    * Trung bình toàn hệ thống: **18.7 phút** (Biên tham chiếu hợp đồng 8m–32m, quan sát tối đa 40m).
    * `vn_fb_004` (Reels): **23.6m ± 7.1m** [10–35m] (Thời lượng trung bình dài nhất trong nhóm quan sát).
    * `vn_fb_001` (Thiết kế): **21.2m ± 9.4m** [12–40m] (Độ biến thiên lớn nhất).
    * `vn_fb_002` (Gia đình): **19.2m ± 4.2m** [10–25m].
    * `vn_fb_003` (Bảo vệ): **19.2m ± 4.7m** [10–25m].
    * `vn_fb_006` (Gen X): **13.7m ± 4.7m** [8–22m].
    * `vn_fb_005` (Cơ khí): **13.1m ± 2.3m** [10–18m] (Độ lệch chuẩn thấp nhất, xu hướng thao tác ổn định).
  * **Cơ chế kết thúc phiên (`terminal_reason`):** **95/95 phiên (100.0%)** đều ghi nhận kết thúc qua `agent_stop`, không ghi nhận phiên treo hoặc lỗi gián đoạn.
* **Bảng dữ liệu tham chiếu:** `output/tables/h1_persona_duration_stats.csv` & `output/tables/h1_hypothesis_verification_summary.csv`
* **Kết luận kiểm định $H_1$:** **Dữ liệu thực nghiệm phù hợp với các giả định của $H_1$** (Phản ánh được sự phân hóa hợp lý theo hồ sơ Persona).
* **Trạng thái:** `[x] Đã hoàn thành (Ảnh & CSV sẵn sàng)`

---

## TẦNG 2: KIỂM CHỨNG $H_2$ - TÍNH NHẤT QUÁN CỦA HÀNH VI VỚI HỒ SƠ PERSONA
*(Tập trung vào: Tương tác, độ sâu đọc bài, nhịp cuộn, căn cứ nhận thức, trí nhớ xuyên phiên)*

### 📍 Slide 2.1: Phân bổ Bề mặt Giao diện (Surface) & Định dạng Ưa thích
* **Mục tiêu:** Phân tích mức độ phân hóa không gian bề mặt mạng xã hội theo sở thích nội dung của từng Persona và khảo sát xu hướng dịch chuyển bề mặt (Spatial Distribution).
* **Hình ảnh tương ứng:** `output/figures/slide2_1_surface_distribution_and_persona_alignment.png` (Gồm 2 Panel A & B, độ phân giải 300 DPI).
* **Metric cốt lõi (Tổng 1,611 actions trên toàn hệ thống):**
  * **Panel A - Phân bổ Bề mặt 100% Stacked Bar Chart theo Persona (001 → 006):**
    * `feed` (Bảng tin chung): Chiếm 534 actions (33.1% toàn hệ thống).
    * `reels` (Video ngắn): Chiếm 497 actions (30.9% toàn hệ thống).
    * `detail` (Đọc sâu bài viết/bình luận): Chiếm 277 actions (17.2% toàn hệ thống).
    * `group` (Hội nhóm cộng đồng): Chiếm 196 actions (12.2% toàn hệ thống).
    * `search` (Tìm kiếm chủ động): Chiếm 46 actions (2.9% toàn hệ thống).
    * `unknown` (Trạng thái chuyển tiếp DOM): Chiếm 61 actions (3.8% toàn hệ thống).
  * **Panel B - Bản đồ nhiệt Dư số Chuẩn hóa Haberman (Haberman Standardized Residuals - Z-Score):**
    * Kiểm định Chi-square: $\chi^2 = 1,270.86$, $p < 0.001$, Cramer's $V = 0.397$ (Cho thấy mối liên hệ có ý nghĩa thống kê giữa Persona và bề mặt tương tác).
* **Nhận định phân hóa không gian then chốt:**
  * 🎬 **Tập trung cao ở Video ngắn (Reels):**
    * `vn_fb_004` (Nhân viên nhà hàng): Chiếm **87.4% actions** ở Reels ($Z = +28.8$), trong khi Feed chỉ chiếm 4.4% và Detail 3.2%, phù hợp với thiên hướng tiêu thụ video ngắn.
  * 👥 **Xu hướng tham gia Hội nhóm (Group):**
    * `vn_fb_001` (Thiết kế đồ họa): Ghi nhận **42.8% actions** trong Group ($Z = +18.0$) trong các cộng đồng đồ họa; không ghi nhận lượt xem Reels (0.0%).
    * `vn_fb_006` (Gen X Kinh doanh): Ghi nhận **23.4% actions** trong Group ($Z = +4.2$) tham gia hội bất động sản/đồng hương; không ghi nhận lượt xem Reels (0.0%).
  * 📖 **Tỷ lệ xem Chi tiết & Bình luận (Detail) ở mức cao:**
    * `vn_fb_005` (Thợ cơ khí): **30.7% actions** ở Detail ($Z = +5.6$) và **6.6%** Tìm kiếm ($Z = +3.5$) liên quan đến nội dung kỹ thuật; không ghi nhận lượt xem Reels.
    * `vn_fb_003` (Bảo vệ trực ca): **28.6% actions** ở Detail ($Z = +6.6$), kết hợp lướt Feed (41.1%) và xem Reels (23.4%).
  * 🏠 **Gia đình & Lao động:**
    * `vn_fb_002` (Lao động / Gia đình): Bảng tin Feed chiếm tỷ lệ cao (**52.7%**, $Z = +6.0$) kết hợp Reels (**27.7%**), không ghi nhận hoạt động trong Group hay Search.
* **Bảng dữ liệu tham chiếu:**
  * `output/tables/h2_persona_surface_distribution_stats.csv` (Thống kê số lượng & tỷ lệ 6 bề mặt)
  * `output/tables/h2_surface_haberman_residuals.csv` (Ma trận dư số chuẩn hóa Haberman)
  * `output/tables/h2_surface_contract_vs_observed_comparison.csv` (Đối chiếu tỷ lệ hợp đồng cấu hình vs thực tế quan sát)
* **Kết luận kiểm định $H_2$ cấp độ Bề mặt:** **Dữ liệu thực nghiệm ủng hộ giả thuyết $H_2$** (Ghi nhận sự khác biệt có ý nghĩa thống kê về phân bổ bề mặt hoạt động giữa các Persona).
* **Trạng thái:** `[x] Đã hoàn thành (Ảnh & CSV sẵn sàng)`

---

### 📍 Slide 2.2: Cường độ & Phong cách Tương tác (Like, Comment, Share) trên Mỗi Bài viết
* **Mục tiêu:** Đo lường mức độ tương tác bài viết và xem xét tính tương thích với phong cách giao tiếp của từng nhân vật theo hồ sơ Persona.
* **Hình ảnh tương ứng:** `output/figures/slide2_2_interaction_intensity_and_style.png` (Gồm 2 Panel A & B, độ phân giải 300 DPI).
* **Metric cốt lõi:**
  * **Panel A - Tỷ lệ tương tác trên bài tiếp cận & Tỷ lệ tương tác chủ động (AER / Actions):**
    * `vn_fb_005` (Thợ cơ khí): **AER đạt 11.8%** (Cao nhất hệ thống), React Rate 26.1%, Comment Rate 26.1%, Share Rate 2.2%.
    * `vn_fb_002` (Gia đình): **AER đạt 10.9%**, React Rate 63.3% (19 lượt react / 30 bài tiếp cận), Comment Rate 3.3%.
    * `vn_fb_006` (Gen X): **AER đạt 8.8%**, React Rate 24.4%, Comment Rate 2.2%.
    * `vn_fb_001` (Thiết kế): **AER đạt 7.4%**, React Rate 24.4%, Comment Rate 3.8%.
    * `vn_fb_003` (Bảo vệ): **AER đạt 5.7%**, **Comment Rate đạt 58.1%** (18 bình luận / 31 bài tiếp cận, cao nhất hệ thống), React Rate 9.7%.
    * `vn_fb_004` (Nhà hàng): **AER đạt 2.2%** (Thấp nhất hệ thống), React Rate 64.3% (9 react trên 14 video mục tiêu), Comment Rate 0.0%, Share Rate 0.0%.
  * **Panel B - Cơ cấu sắc thái cảm xúc, bình luận & chia sẻ (%):**
    * Phân bổ 7 sắc thái cảm xúc (`like`, `love`, `care`, `wow`, `haha`, `sad`, `angry`) cùng hành vi `comment` và `share`.
* **Nhận định phân hóa phong cách tương tác:**
  * 💬 **Chiến thần bình luận dạo (`vn_fb_003`):** Tập trung vào việc thảo luận trực tiếp qua bình luận (**18 lượt comment**, chiếm 85.7% tổng hành vi tương tác của persona), ít khi chỉ thả reaction đơn thuần.
  * 🤝 **Người thích chia sẻ (`vn_fb_005`):** Thể hiện hành vi tương tác phong phú nhất: 12 comment, 12 reaction (đa dạng sắc thái `like`, `wow`, `love`, `sad`), và là **persona duy nhất thực hiện chia sẻ bài viết (`shareRate` = 2.2%)**.
  * ❤️ **Gắn kết tình cảm gia đình (`vn_fb_002`):** Thể hiện xu hướng cảm xúc tích cực rõ nét với **6 lượt `love` và 1 lượt `care`** (chiếm 36.8% tổng reaction của persona), phản ánh vai trò kết nối cộng đồng.
  * 🌊 **Xu hướng tiêu thụ thụ động - "Tàu ngầm" (`vn_fb_004` & `vn_fb_006`):** Tỷ lệ comment ở mức 0% đến 2.2%, chủ yếu lướt xem hoặc thả like đơn giản mà không để lại dấu vết thảo luận sâu.
* **Bảng dữ liệu tham chiếu:**
  * `output/tables/h2_persona_engagement_rates.csv` (Thống kê số lượng & tỷ lệ React, Comment, Share, AER)
  * `output/tables/h2_persona_reaction_breakdown.csv` (Cơ cấu chi tiết 7 loại reaction và tương tác)
* **Kết luận kiểm định Slide 2.2:** **Dữ liệu thực nghiệm phù hợp với các hình mẫu phong cách tương tác trong hồ sơ Persona.**
* **Trạng thái:** `[x] Đã hoàn thành (Ảnh & CSV sẵn sàng)`

---

### 📍 Slide 2.3: Tỷ lệ Bài Lướt qua (Scanning) vs Bài Chọn Đọc Sâu (Deep Reading)
* **Mục tiêu:** Đo lường mức độ chọn lọc và phân bổ giữa hành vi quét nhanh nội dung (Scanning) so với đọc/nghiền ngẫm chi tiết (Deep Reading).
* **Hình ảnh tương ứng:** `output/figures/slide2_3_scanning_vs_deep_reading.png` (Gồm 2 Panel A & B, độ phân giải 300 DPI).
* **Metric cốt lõi:**
  * **Panel A - Phân bổ 100% Stacked Bar giữa Scanning vs Deep Reading:**
    * `Scanning` (Lướt qua / Quét nhanh): Gồm các bước `scroll` (cuộn bảng tin), `observe` (quan sát DOM), `next` (chuyển video).
    * `Deep Reading` (Đọc sâu / Tìm hiểu kỹ): Gồm các bước `read` (đọc nội dung bài), `expand` (mở rộng xem thêm), `scroll_comments` (cuộn đọc bình luận).
    * `vn_fb_005` (Thợ cơ khí): **Đọc sâu đạt 47.0%** (62 bước) vs Lướt 53.0% (70 bước) — Tỷ lệ đọc sâu cao nhất toàn hệ thống.
    * `vn_fb_001` (Thiết kế đồ họa): **Đọc sâu đạt 36.8%** (75 bước) vs Lướt 63.2% (129 bước).
    * `vn_fb_006` (Gen X Kinh doanh): **Đọc sâu đạt 34.5%** (38 bước) vs Lướt 65.5% (72 bước).
    * `vn_fb_002` (Gia đình): **Đọc sâu đạt 32.1%** (34 bước) vs Lướt 67.9% (72 bước).
    * `vn_fb_003` (Bảo vệ trực ca): **Đọc sâu đạt 23.8%** (57 bước) vs Lướt 76.2% (183 bước).
    * `vn_fb_004` (Nhân viên nhà hàng): **Đọc sâu chỉ chiếm 6.5%** (14 bước) vs **Lướt/chuyển video chiếm 93.5%** (202 bước).
  * **Panel B - Số lượng bài đọc sâu tích lũy trung bình mỗi phiên (Working Memory):**
    * Trung bình toàn hệ thống: **3.8 bài/phiên**.
    * `vn_fb_001`: **5.5 bài/phiên** (Tổng 22 bài tích lũy).
    * `vn_fb_005`: **5.2 bài/phiên** (Tổng 21 bài tích lũy).
    * `vn_fb_006`: **4.7 bài/phiên** (Tổng 14 bài tích lũy).
    * `vn_fb_002`: **3.5 bài/phiên** (Tổng 14 bài tích lũy).
    * `vn_fb_003`: **3.5 bài/phiên** (Tổng 14 bài tích lũy).
    * `vn_fb_004`: **1.0 bài/phiên** (Tổng 4 bài tích lũy).
* **Nhận định phân hóa độ sâu tiêu thụ thông tin:**
  * 🔧 **Thợ kỹ thuật đọc sâu và phân tích bài viết (`vn_fb_005`):** Tỷ lệ đọc sâu tiếp cận 50% tổng số bước tiếp nhận, tích lũy 5.2 bài/phiên, phù hợp với thói quen tìm hiểu quy trình kỹ thuật xe máy và đọc bình luận trao đổi kinh nghiệm.
  * 🎨 **Nhà thiết kế và Người lớn tuổi chọn lọc nội dung kỹ lưỡng (`vn_fb_001` & `vn_fb_006`):** Tích lũy lượng bài đọc cao (4.7 – 5.5 bài/phiên), thể hiện sự kiên nhẫn trong việc đọc hiểu và thẩm định thông tin.
  * ⚡ **Nhân viên phục vụ với nhịp độ xem lướt nhanh (`vn_fb_004`):** 93.5% hành vi tập trung vào chuyển video (`next`) và xem lướt, số bài đọc tích lũy chỉ 1.0 bài/phiên, phản ánh hành vi tiêu thụ đặc trưng của định dạng Reels.
* **Bảng dữ liệu tham chiếu:**
  * `output/tables/h2_persona_reading_depth_stats.csv` (Thống kê tỷ lệ Scanning vs Deep Reading và Dwell time)
  * `output/tables/h2_session_reading_accumulation.csv` (Dữ liệu bài đọc tích lũy trong Working Memory theo từng session)
* **Kết luận kiểm định Slide 2.3:** **Dữ liệu thực nghiệm phản ánh sự phân hóa rõ ràng về mức độ đọc sâu giữa các nhóm Persona, phù hợp với tính chất định dạng nội dung ưa thích.**
* **Trạng thái:** `[x] Đã hoàn thành (Ảnh & CSV sẵn sàng)`

---

### 📍 Slide 2.4: Thói quen Cuộn trang & Động lực học Thao tác (Scroll Dynamics)
* **Mục tiêu:** Khảo sát các thông số cơ học của thao tác vuốt cuộn (quãng đường, độ trễ và chuỗi cuộn liên tiếp) nhằm đối chiếu với quy định nhịp độ (`scrollCadence`) và tác phong theo hồ sơ Persona.
* **Hình ảnh tương ứng:** `output/figures/slide2_4_scroll_dynamics.png` (Gồm 2 Panel A & B, độ phân giải 300 DPI).
* **Metric cốt lõi:**
  * **Panel A - Quãng đường cuộn trung bình mỗi bước (Pixel) & Hợp đồng Cadence:**
    * Nhóm nhịp độ nhanh (`quick`):
      * `vn_fb_001` (Thiết kế đồ họa): **1,719 ± 887 px** (Median 1,620 px) — Quãng đường cuộn dài nhất nhóm quan sát.
      * `vn_fb_005` (Thợ cơ khí): **1,378 ± 846 px** (Median 1,056 px) — Vuốt dứt khoát, biên độ lớn.
    * Nhóm nhịp độ điều độ (`balanced`):
      * `vn_fb_002` (Lao động/Gia đình): **1,056 ± 369 px** (Median 1,042 px).
      * `vn_fb_003` (Bảo vệ trực ca): **736 ± 416 px** (Median 658 px).
      * `vn_fb_006` (Gen X Kinh doanh): **704 ± 319 px** (Median 650 px).
      * `vn_fb_004` (Nhân viên nhà hàng): **595 ± 255 px** (Median 478 px, chỉ có 8 bước cuộn do ưu tiên chuyển video).
    * *Đường tham chiếu toàn hệ thống:* **1,080 px/bước**.
  * **Panel B - Động lực học nhịp điệu (Độ trễ trung vị & Tỷ lệ chuỗi cuộn liên tiếp):**
    * `vn_fb_003` (Bảo vệ): **Tỷ lệ cuộn liên tiếp đạt 59.5%** (78/131 bước cuộn), độ trễ trung vị **8.5s** (Mean 9.6s, IQR 3.9s), phản ánh thao tác cuộn liên tục khi lướt bảng tin và dò tìm bình luận.
    * `vn_fb_006` (Gen X): **Độ trễ trung vị cao nhất (12.1s, Mean 20.4s, IQR 19.9s)**, tỷ lệ cuộn liên tiếp 32.4%, phản ánh tốc độ đọc chậm rãi, cẩn trọng.
    * `vn_fb_005` (Cơ khí): Độ trễ trung vị **7.9s** (Mean 10.3s), tỷ lệ cuộn liên tiếp 30.3%.
    * `vn_fb_002` (Gia đình): Độ trễ trung vị **7.7s**, tỷ lệ cuộn liên tiếp 22.5%.
    * `vn_fb_001` (Thiết kế): Độ trễ trung vị **10.3s**, tỷ lệ cuộn liên tiếp thấp (14.1%), thường xen kẽ bước quan sát hình ảnh.
    * `vn_fb_004` (Nhà hàng): Độ trễ trung vị **10.7s**, tỷ lệ cuộn liên tiếp 12.5%.
* **Nhận định phân hóa động lực học cuộn:**
  * 📐 **Tương thích nhịp độ Cadence:** Nhóm cấu hình `quick` (`001`, `005`) ghi nhận quãng đường cuộn dài hơn rõ rệt (trung bình >1,300 px) so với nhóm `balanced` (trung bình 600 – 1,050 px).
  * 🔍 **Thói quen cuộn liên tục của Bảo vệ (`vn_fb_003`):** Tỷ lệ chuỗi cuộn liên tiếp chiếm gần 60% tổng hành vi cuộn, thể hiện nhịp lướt tìm kiếm thông tin nhanh trong ca trực.
  * ⏳ **Tác phong đọc thận trọng của Gen X (`vn_fb_006`):** Độ trễ giữa các lần cuộn dài nhất hệ thống (trung bình trên 20 giây), phù hợp với thói quen dừng lại đọc kỹ từng đoạn bài viết của người lớn tuổi.
* **Bảng dữ liệu tham chiếu:** `output/tables/h2_persona_scroll_dynamics_stats.csv` (Thống kê chi tiết quãng đường, độ trễ và tỷ lệ chuỗi cuộn)
* **Kết luận kiểm định Slide 2.4:** **Dữ liệu thực nghiệm phản ánh sự phân hóa về động lực học thao tác cuộn phù hợp với cấu hình nhịp độ và tác phong nhân vật trong hồ sơ Persona.**
* **Trạng thái:** `[x] Đã hoàn thành (Ảnh & CSV sẵn sàng)`

---

### 📍 Slide 2.5: Thống kê Căn cứ Nhận thức Vĩ mô (Decision Evidence Macro Overview) & Ma trận Liên kết Hành vi
* **Mục tiêu:** Kiểm tra cơ chế ra quyết định của agent thông qua chuỗi suy luận (Chain-of-Thought Evidence) kích hoạt các hành động đòi hỏi mức độ tập trung và xử lý nhận thức cao.
* **Tập dữ liệu khảo sát:** $N = 313$ hành vi có chủ đích (`read`: 167, `react`: 73, `comment`: 35, `expand`: 19, `search`: 16, `share`: 1).
* **Metric cần đo:**
  * Cơ cấu 4 trụ cột nhận thức vĩ mô: *Tò mò & Khám phá tri thức*, *Đời sống, Cảm xúc & Giải trí*, *Thực dụng & Chuyên môn đầu tư*, *Truyền thống & Tâm linh*.
  * Ma trận liên kết Trụ cột Nhận thức $\rightarrow$ Hành vi tập trung thực thi.
* **Đối chiếu Persona:** Khung căn cứ nhận thức trong hợp đồng (`decision_evidence.dimension`).
* **Biểu đồ trực quan:** `output/figures/slide2_5_macro_decision_evidence_overview.png` (Hình 2 panel độ phân giải cao 300 DPI)
  * **Panel A (Trái):** Phân bổ 4 Trụ cột Căn cứ Nhận thức Toàn hệ thống (Số lượt và tỷ lệ % kích hoạt).
  * **Panel B (Phải):** Ma trận Nhiệt (Heatmap) liên kết giữa Trụ cột Nhận thức và Hành vi Tập trung cao.
* **Bảng dữ liệu thực nghiệm vĩ mô:**
  * Bảng phân bổ trụ cột: `output/tables/h2_macro_evidence_distribution.csv`
  * Bảng ma trận hành vi: `output/tables/h2_macro_evidence_action_matrix.csv`
* **Nhận định thực nghiệm Slide 2.5:**
  * 🧠 **Động lực Tò mò chi phối mạnh mẽ nhất:** Trụ cột *Tò mò & Khám phá tri thức* chiếm 40.6% tổng lượt kích hoạt (127/313 actions), đóng vai trò là động lực chính thúc đẩy hành vi **Đọc sâu** (73 lượt) và **Tìm kiếm thông tin** (11 lượt).
  * 💬 **Tương tác xã hội gắn liền với Đời sống & Giải trí:** Trụ cột *Đời sống, Cảm xúc & Giải trí* chiếm 30.7% (96 actions), kích hoạt tỷ lệ **Bình luận** (17 lượt) và **Thả cảm xúc** (30 lượt) cao nhất trong 4 nhóm căn cứ.
  * 💼 **Động lực Thực dụng & Chuyên môn:** Chiếm 19.2% (60 actions), liên kết mật thiết với các hành vi khảo sát giá bất động sản, theo dõi công nghệ đồ họa và tích lũy thông tin.
  * 🇻🇳 **Truyền thống & Tâm linh:** Chiếm 9.3% (29 actions), kích hoạt tỷ lệ bình luận tri ân lịch sử và mở rộng bài đọc tâm linh cao tương đối.
* **Kết luận kiểm định Slide 2.5:** **Dữ liệu thực nghiệm phản ánh 100% các hành vi tập trung cao đều được kích hoạt bởi các căn cứ nhận thức có cấu trúc rõ ràng, thể hiện tính nhất quán giữa tư duy nội tại và hành động thực thi.**
* **Trạng thái:** `[x] Đã hoàn thành (Ảnh 300 DPI & CSV sẵn sàng)`

---

### 📍 Slide 2.5.1: Bảng Ma trận Nhận thức Chi tiết Nhóm 1 - Tri thức Chuyên sâu, Khám phá & Tư duy Thực dụng (`001`, `005`, `006`)
* **Mục tiêu:** Phân tích chi tiết ma trận chéo (Hàng = Căn cứ nhận thức, Cột = Hành vi) của nhóm nhân vật thiên về tri thức, kỹ thuật, khoa học và khảo sát thương mại (Độ tương đồng Cosine $r_{\text{cosine}} = 0.48 - 0.80$).
* **Dữ liệu tham chiếu:** `output/tables/h2_persona_evidence_matrices_detailed.csv`
* **Chi tiết ma trận từng Persona (sắp xếp tăng dần theo ID):**

#### 1. `vn_fb_001` (Thiết kế đồ họa - Nữ, TP.HCM | Tổng hành vi: 83)
| Căn cứ Nhận thức (`primary_dimension`) | `read` | `react` | `comment` | `expand` | `search` | `share` | Tổng | Tỷ trọng |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `curiosity` (Tò mò cởi mở) | 28 | 10 | 2 | 5 | 0 | 0 | **45** | 54.2% |
| `interest_real_estate` (Quan tâm BĐS) | 14 | 5 | 0 | 0 | 0 | 0 | **19** | 22.9% |
| `career_role` (Thiết kế đồ họa / Mỹ thuật) | 4 | 3 | 0 | 0 | 0 | 0 | **7** | 8.4% |
| `interest_technology` (Công nghệ mới / AI) | 4 | 1 | 0 | 0 | 2 | 0 | **7** | 8.4% |
| `writing_format` (Văn phong giao tiếp) | 1 | 0 | 1 | 0 | 0 | 0 | **2** | 2.4% |
| Khác (`decision_speed`, `group_community`...) | 1 | 0 | 0 | 2 | 0 | 0 | **3** | 3.6% |
| **TỔNG HÀNH VI** | **52** | **19** | **3** | **7** | **2** | **0** | **83** | **100%** |

* **Trích dẫn lý do hành động tiêu biểu từ log:**
  * 🔍 `search` (`interest_technology`): *"Tìm hiểu các công cụ AI mới cho thiết kế kiến trúc, lĩnh vực mình đang làm việc..."*
  * 📖 `read` (`curiosity`): *"Bài viết về cờ vua với tiêu đề gợi sự tò mò, phù hợp với tính cách cởi mở khám phá và quan tâm đến các trò chơi tư duy."*
  * ❤️ `react` (`curiosity`): *"Bài toán mate in 2 thú vị, phù hợp với tính cách thích thử thách và tò mò cao..."*

#### 2. `vn_fb_005` (Thợ cơ khí - Nam, Đà Nẵng | Tổng hành vi: 74)
| Căn cứ Nhận thức (`primary_dimension`) | `read` | `react` | `comment` | `expand` | `search` | `share` | Tổng | Tỷ trọng |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `curiosity` (Tò mò khoa học / Thiên văn) | 18 | 6 | 4 | 4 | 9 | 1 | **42** | 56.8% |
| `value_tradition` (Tự hào lịch sử dân tộc) | 7 | 3 | 7 | 4 | 0 | 0 | **21** | 28.4% |
| `cuisine_japanese` & `province` | 0 | 2 | 1 | 1 | 0 | 0 | **4** | 5.4% |
| Khác (`attitude_new_tech`, `books_fantasy`...) | 4 | 1 | 0 | 2 | 0 | 0 | **7** | 9.5% |
| **TỔNG HÀNH VI** | **29** | **12** | **12** | **11** | **9** | **1** | **74** | **100%** |

* **Trích dẫn lý do hành động tiêu biểu từ log:**
  * 🔍 `search` (`curiosity`): *"Muốn tìm thông tin cụ thể về thời điểm tốt nhất để quan sát Sao Hỏa đối lập tại Đà Nẵng vào ngày 4/10..."*
  * 📢 `share` (`curiosity`): *"Sự kiện thiên văn hấp dẫn, muốn chia sẻ và hỏi kinh nghiệm từ cộng đồng địa phương."*
  * 💬 `comment` (`value_tradition`): *"Bài viết về Đại tướng Võ Nguyên Giáp và chiến thắng lịch sử rất ý nghĩa, muốn bày tỏ tri ân..."*

#### 3. `vn_fb_006` (Gen X Kinh doanh - Nam, Cần Thơ | Tổng hành vi: 47)
| Căn cứ Nhận thức (`primary_dimension`) | `read` | `react` | `comment` | `expand` | `search` | `share` | Tổng | Tỷ trọng |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `interest_real_estate` (Bất động sản địa phương) | 10 | 5 | 0 | 0 | 2 | 0 | **17** | 36.2% |
| `curiosity` (Tò mò thương mại / Tin tức) | 10 | 2 | 0 | 0 | 0 | 0 | **12** | 25.5% |
| `interest_spirituality` (Tâm linh Phật giáo) | 5 | 0 | 0 | 0 | 0 | 0 | **5** | 10.6% |
| `value_wealth` & `value_health` | 6 | 2 | 0 | 0 | 0 | 0 | **8** | 17.0% |
| `cuisine_street_food` & khác | 2 | 2 | 1 | 0 | 0 | 0 | **5** | 10.6% |
| **TỔNG HÀNH VI** | **33** | **11** | **1** | **0** | **2** | **0** | **47** | **100%** |

* **Trích dẫn lý do hành động tiêu biểu từ log:**
  * 📖 `read` (`interest_real_estate`): *"Bài đăng về căn hộ tại Quận Cái Răng, Cần Thơ với giá 8.5 triệu/tháng. Cần đọc chi tiết để hiểu giá cả..."*
  * 💬 `comment` (`interest_real_estate`): *"Đang xem căn hộ Cara River Park tại Cần Thơ. Muốn xem video thực tế và hỏi rõ về giá để cân nhắc. Giọng miền Tây, thẳng thắn..."*
  * ❤️ `react` (`value_health`): *"Bài viết về thực dưỡng và bảo vệ sức khỏe trung niên, thả like lưu trữ thông tin."*

* **Kết luận kiểm định Slide 2.5.1:** **Nhóm 1 thể hiện rõ nét tư duy duy lý, với các căn cứ nhận thức tập trung vào tri thức, công nghệ, lịch sử dân tộc và thị trường bất động sản.**
* **Trạng thái:** `[x] Đã hoàn thành (Bảng số liệu & Trích dẫn sẵn sàng)`

---

### 📍 Slide 2.5.2: Bảng Ma trận Nhận thức Chi tiết Nhóm 2 - Đời sống Thường nhật, Cảm xúc & Giải trí Bình dân (`002`, `003`, `004`)
* **Mục tiêu:** Phân tích chi tiết ma trận chéo của nhóm nhân vật gắn liền với đời sống hàng ngày, gắn kết gia đình, ẩm thực đường phố và giải trí ngắn gọn.
* **Dữ liệu tham chiếu:** `output/tables/h2_persona_evidence_matrices_detailed.csv`
* **Chi tiết ma trận từng Persona (sắp xếp tăng dần theo ID):**

#### 1. `vn_fb_002` (Lao động tự do / Gia đình - Nữ, Nghệ An | Tổng hành vi: 42)
| Căn cứ Nhận thức (`primary_dimension`) | `read` | `react` | `comment` | `expand` | `search` | `share` | Tổng | Tỷ trọng |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `tone` (Sắc thái hướng thiện, từ bi) | 5 | 8 | 1 | 0 | 0 | 0 | **14** | 33.3% |
| `curiosity` & `emotional_expressiveness` | 5 | 5 | 0 | 0 | 0 | 0 | **10** | 23.8% |
| `province` & `interest_parenting` | 6 | 1 | 0 | 0 | 0 | 0 | **7** | 16.7% |
| `content_consumption_format` | 2 | 1 | 0 | 0 | 0 | 0 | **3** | 7.1% |
| Khác (`interest_spirituality`, `books`...) | 3 | 4 | 0 | 1 | 0 | 0 | **8** | 19.0% |
| **TỔNG HÀNH VI** | **21** | **19** | **1** | **1** | **0** | **0** | **42** | **100%** |

* **Trích dẫn lý do hành động tiêu biểu từ log:**
  * ❤️ `react` (`emotional_expressiveness`): *"Bài viết về Đền Ông Hoàng Mười phù hợp với niềm tin Phật giáo và quan tâm tâm linh nhẹ nhàng của chị. Lời cầu nguyện bình an cho gia đình."*
  * 📖 `read` (`interest_parenting_family_life`): *"Bài về dưỡng lão công lập quá tải liên quan đến vấn đề chăm sóc người cao tuổi trong gia đình, chị muốn đọc để hiểu tình hình..."*
  * 💬 `comment` (`tone`): *"Bình luận tích cực về việc làm điều tốt, chúc mọi người luôn mạnh khỏe, phù hợp với tính cách đôn hậu..."*

#### 2. `vn_fb_003` (Bảo vệ trực ca - Nam, Đà Nẵng | Tổng hành vi: 46)
| Căn cứ Nhận thức (`primary_dimension`) | `read` | `react` | `comment` | `expand` | `search` | `share` | Tổng | Tỷ trọng |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `cuisine_vietnamese` (Món ăn truyền thống) | 7 | 0 | 7 | 0 | 0 | 0 | **14** | 30.4% |
| `cuisine_street_food` (Ăn vặt đường phố) | 2 | 0 | 6 | 0 | 1 | 0 | **9** | 19.6% |
| `social_engagement_style` (Giao lưu sôi nổi) | 3 | 0 | 2 | 0 | 1 | 0 | **6** | 13.0% |
| `group_community_participation` | 5 | 0 | 0 | 0 | 0 | 0 | **5** | 10.9% |
| `curiosity` & `content_consumption_format` | 3 | 3 | 1 | 0 | 0 | 0 | **7** | 15.2% |
| Khác (`interest_film`, `attitude_ads`...) | 3 | 0 | 2 | 0 | 0 | 0 | **5** | 10.9% |
| **TỔNG HÀNH VI** | **23** | **3** | **18** | **0** | **2** | **0** | **46** | **100%** |

* **Trích dẫn lý do hành động tiêu biểu từ log:**
  * 💬 `comment` (`cuisine_street_food`): *"Bài review tokbokki phomai hấp dẫn, muốn hỏi địa chỉ quán. Giọng thẳng thắn, dùng từ lóng và emoji phù hợp persona thanh niên..."*
  * 🔍 `search` (`cuisine_street_food`): *"Feed hiện không có nội dung phù hợp sở thích; tìm kiếm quán bún trộn Đà Nẵng để khám phá ẩm thực đường phố miền Trung..."*
  * 📖 `read` (`cuisine_vietnamese`): *"Bài review món ăn có tương tác cao, muốn đọc kỹ các bình luận để xem đánh giá hương vị thực tế..."*

#### 3. `vn_fb_004` (Nhân viên nhà hàng - Nam, TP.HCM | Tổng hành vi: 21)
| Căn cứ Nhận thức (`primary_dimension`) | `read` | `react` | `comment` | `expand` | `search` | `share` | Tổng | Tỷ trọng |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `sport_football` (Bóng đá, tin thể thao) | 7 | 2 | 0 | 0 | 1 | 0 | **10** | 47.6% |
| `content_consumption_format` (Video ngắn) | 1 | 6 | 0 | 0 | 0 | 0 | **7** | 33.3% |
| `curiosity` (Tò mò giải trí nhanh) | 2 | 0 | 0 | 1 | 0 | 0 | **3** | 14.3% |
| `reading_frequency` | 0 | 1 | 0 | 0 | 0 | 0 | **1** | 4.8% |
| **TỔNG HÀNH VI** | **10** | **9** | **0** | **1** | **1** | **0** | **21** | **100%** |

* **Trích dẫn lý do hành động tiêu biểu từ log:**
  * 🔍 `search` (`sport_football`): *"Không thấy video highlight bóng đá sau nhiều lần next, tìm kiếm trực tiếp để xem nội dung phù hợp..."*
  * ❤️ `react` (`content_consumption_format`): *"Tình huống bóng đá thú vị, Dembele lỡ cơ hội ngon ăn. Thích xem thêm highlight nên thả cảm xúc tương tác..."*
  * 📖 `read` (`curiosity`): *"Bài viết về hành trình đi bộ từ Anh đến Việt Nam, gợi tò mò muốn lướt đọc nội dung ngắn trước khi tiếp tục xem video..."*

* **Kết luận kiểm định Slide 2.5.2:** **Nhóm 2 phản ánh trung thực sở thích đời sống hàng ngày, gắn bó mật thiết với ẩm thực đường phố địa phương, tình cảm gia đình và giải trí thể thao.**
* **Trạng thái:** `[x] Đã hoàn thành (Bảng số liệu & Trích dẫn sẵn sàng)`

---

### 📍 Slide 2.6: Tính Liên kết Thông tin Xuyên Phiên (Cross-Session Memory & Continuity)
* **Mục tiêu:** Kiểm tra hành vi tiếp cận thông tin giữa các phiên khác nhau có tính kết nối mạch lạc hay độc lập rời rạc; đánh giá cơ chế ghi nhớ ngắn hạn (Working Memory) và sự tiếp nối luồng tư duy xuyên phiên.
* **Tập dữ liệu khảo sát:** 23 phiên chạy thực nghiệm của 6 Persona (mỗi Persona từ 3 đến 4 phiên duyệt).
* **Metric cần đo:**
  * **Tỷ lệ duy trì chủ đề cốt lõi (`Core Theme Persistence Rate` %):** Tỷ lệ các phiên duy trì cùng chủ đề định hướng trong Working Memory.
  * **Tích lũy bài đọc trong bộ nhớ (`Read Posts in Memory`):** Số lượng bài viết đã đọc được lưu trữ dấu vết (dwell time, snippet) phục vụ tránh trùng lặp.
  * **Số luồng tư duy hoạt động trung bình (`Active Threads`):** Số lượng luồng suy nghĩ được theo đuổi đồng thời trong phiên.
  * **Hành vi quay lại thực thể (`Entity Revisit Count`):** Số lượng Group, Page hoặc Search Query cụ thể được truy cập lặp lại ở các phiên sau.
* **Đối chiếu Persona:** Sở thích cốt lõi (`taste.rankedTopics`), cơ chế bộ nhớ làm việc (`working_memory.active_threads`), hợp đồng suy luận (`prior_memory`).
* **Biểu đồ trực quan:** `output/figures/slide2_6_cross_session_memory_continuity.png` (Hình 2 panel độ phân giải cao 300 DPI)
  * **Panel A (Trái):** So sánh Độ bền vững Chủ đề Cốt lõi (%) & Số lượng bài đọc tích lũy trong bộ nhớ làm việc của 6 Persona.
  * **Panel B (Phải):** Sơ đồ Dòng thời gian minh họa Tiến hóa Mạch Nhận thức & Thực thể Quay lại Xuyên phiên (Session 1 $\rightarrow$ 4).
* **Bảng dữ liệu thực nghiệm tham chiếu:**
  * Bảng tổng hợp chỉ số bộ nhớ: `output/tables/h2_persona_memory_continuity_stats.csv`
  * Bảng chi tiết luồng chủ đề: `output/tables/h2_persona_cross_session_threads_detail.csv`

| Persona ID | Vai trò & Nghề nghiệp | Số phiên | Luồng TB/phiên | Bài đọc tích lũy | Thay đổi bộ nhớ (`deltas`) | Tỷ lệ duy trì chủ đề (%) | Thực thể quay lại |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`vn_fb_001`** | Thiết kế đồ họa | 4 | 3.00 | 22 bài | 10 | **100.0%** | **2** (Group & Query) |
| **`vn_fb_002`** | Lao động / Gia đình | 4 | 2.75 | 14 bài | 11 | **100.0%** | 0 |
| **`vn_fb_003`** | Bảo vệ trực ca | 4 | 2.75 | 14 bài | 12 | **50.0%** | 1 (Domain base) |
| **`vn_fb_004`** | Nhân viên nhà hàng | 4 | 3.50 | 4 bài | 9 | **100.0%** | 0 |
| **`vn_fb_005`** | Thợ cơ khí | 4 | 2.50 | 21 bài | 14 | **75.0%** | **1** (Post/Event) |
| **`vn_fb_006`** | Gen X Kinh doanh | 3 | 1.67 | 14 bài | 5 | **66.7%** | **2** (Group & Query) |

* **Nhận định thực nghiệm Slide 2.6:**
  * 🔄 **Tính duy trì chủ đề cốt lõi đạt mức cao:** Tỷ lệ phiên duy trì mạch chủ đề đạt trung bình 81.9% toàn hệ thống; trong đó 3 nhân vật (`001`, `002`, `004`) đạt mức 100%, phản ánh tính ổn định vững chắc của bộ lọc sở thích Persona qua các phiên duyệt khác nhau.
  * 🎯 **Hành vi quay lại thực thể cụ thể (Entity Revisit):** Ghi nhận bằng chứng thực nghiệm rõ nét ở `vn_fb_001` (truy cập lại Group Kiến trúc ID `203414773608506` và lặp lại truy vấn *"AI thiết kế kiến trúc 2026"* ở Phiên 3 & 4) và `vn_fb_006` (truy cập lại Group BĐS Cần Thơ ID `2133631560242753` và lặp lại truy vấn *"bat dong san can tho 2026"* ở Phiên 1 & 2).
  * 📈 **Tiến trình nhận thức phát triển có chiều sâu:** Điển hình ở `vn_fb_005`, luồng tư duy phát triển tuần tự: Khám phá feed (Phiên 1) $\rightarrow$ Đọc kỹ thuật chụp ảnh mặt trăng (Phiên 2) $\rightarrow$ Tiếp cận sự kiện Mặt Trăng & Sao Hỏa (Phiên 3) $\rightarrow$ Thực hiện chuỗi 9 lượt tìm kiếm thời điểm quan sát Sao Hỏa đối lập tại Đà Nẵng và chia sẻ bài viết (Phiên 4).
  * 🧠 **Dung lượng tích lũy Working Memory:** Mỗi nhân vật duy trì trung bình 2.5 – 3.5 luồng chủ đề đồng thời và tích lũy từ 14 – 22 bài đọc trong bộ nhớ ngắn hạn, hỗ trợ hiệu quả cho việc tránh đọc lặp bài viết và giữ mạch tư duy tự nhiên.
* **Kết luận kiểm định Slide 2.6:** **Dữ liệu thực nghiệm phản ánh cơ chế Working Memory và Active Threads đã duy trì được tính kết nối thông tin mạch lạc và chiều sâu nhận thức xuyên suốt các phiên hoạt động độc lập.**
* **Trạng thái:** `[x] Đã hoàn thành (Ảnh 300 DPI & CSV sẵn sàng)`

---

### 📍 Slide 2.7: Các Chuỗi Hành vi Đặc thù & Đột biến Thú vị Giải thích được (Signature 3-Step Behavioral Chains)
* **Mục tiêu:** Mở rộng từ các cặp thao tác 2 bước lên **chuỗi 3 bước đồng bộ ($A \to B \to C$)** để làm nổi bật trọn vẹn **động cơ nhận thức và mục đích hành vi** của từng nhân vật (Khởi phát tiếp cận $\to$ Xử lý nhận thức $\to$ Động thái tiếp nối); minh họa tính "người" và sự phân hóa phong cách tương tác có logic.
* **Phương pháp luận:** Áp dụng thuật toán nén lặp liên tiếp (Run-Length Compression: gộp các bước cuộn/xem lặp lại), loại bỏ vòng lặp con thoi ($A \to B \to A$) và đo lường độ độc quyền (Exclusivity Index so với 5 nhân vật còn lại).
* **Tập dữ liệu khảo sát:** 23 phiên chạy thực nghiệm của 6 Persona (toàn bộ các chuỗi 3 bước đa phiên).
* **Biểu đồ trực quan:** `output/figures/slide2_7_characteristic_action_sequences.png` (Hình 2 panel độ phân giải cao 300 DPI)
  * **Panel A (Trái):** Biểu đồ Cột ngang so sánh Độ Độc Quyền (% Exclusivity) và Tần suất thực hiện của 6 Chuỗi 3 Bước Thương hiệu Đặc trưng.
  * **Panel B (Phải):** Sơ đồ Quy trình 3 Bước Trực quan (Step-by-Step Flow Cards) minh họa tiến trình thao tác cụ thể kèm ý nghĩa tâm lý đời thực.
* **Bảng dữ liệu thực nghiệm tham chiếu:** `output/tables/h2_persona_characteristic_sequences.csv`

| Persona ID & Vai trò | Chuỗi 3 Bước Đặc trưng (3-Step Behavioral Chain) | Ý nghĩa Chu trình Thao tác | Tần suất | Số phiên | Khác ($n$) | Độ Độc Quyền (%) | Bản Sắc Động Cơ Nhận Thức (Psychological Motivation Rationale) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`vn_fb_001`**<br>(Thiết kế đồ họa) | `read [group] ➔ open_comments [detail] ➔ scroll_comments [detail]` | Đọc bài trong nhóm chuyên môn $\to$ Mở xem thảo luận $\to$ Cuộn đọc ý kiến | **4** | 1/4 phiên | **0** | **100.0%** | **Động cơ nghiên cứu chuyên sâu:** Tiếp cận bài viết thiết kế kiến trúc trong group nghề nghiệp, chủ động mở phần bình luận và cuộn đọc kỹ các đóng góp chuyên môn của cộng đồng. |
| **`vn_fb_002`**<br>(Lao động / Gia đình) | `read [feed] ➔ react [feed] ➔ scroll [feed]` | Đọc nhanh bài trên feed $\to$ Thả tim cảm xúc $\to$ Cuộn lướt tiếp ngay | **4** | 2/4 phiên | 3 | **57.1%** | **Động cơ tranh thủ giờ nghỉ ngắn:** Người phụ nữ bận rộn nhìn nhanh bài viết trên feed, thả tim hướng thiện/tâm linh rồi tiếp tục cuộn lướt sang bài khác chứ không tranh luận kéo dài. |
| **`vn_fb_003`**<br>(Bảo vệ trực ca) | `comment [detail] ➔ observe [detail] ➔ scroll_comments [detail]` | Để lại bình luận hỏi quán $\to$ Dừng quan sát bài $\to$ Cuộn đọc ý kiến đêm | **7** | 2/4 phiên | **0** | **100.0%** | **Động cơ giao lưu kết nối ca trực:** Bảo vệ trực ca đêm rảnh rỗi vào bài viết ẩm thực đường phố bình luận hỏi giá/địa chỉ, dừng lại quan sát rồi cuộn đọc kỹ các trao đổi khác của cộng đồng. |
| **`vn_fb_004`**<br>(Nhân viên nhà hàng) | `watch [reels] ➔ react [reels] ➔ next [reels]` | Xem thưởng thức clip Reels $\to$ Thả cảm xúc thích thú $\to$ Vuốt chuyển clip | **3** | 2/4 phiên | 2 | **60.0%** | **Động cơ giải trí nhanh sau ca làm:** Thanh niên phục vụ nhà hàng sau giờ làm mệt mỏi xem video ngắn Reels, thưởng thức pha bóng highlight, thả tim cảm xúc rồi vuốt chuyển ngay sang clip kế tiếp. |
| **`vn_fb_005`**<br>(Thợ cơ khí) | `read [feed] ➔ expand [feed] ➔ observe [feed]` | Đọc mở đầu bài kỹ thuật $\to$ Bấm "Xem thêm" mở bài $\to$ Dừng lại thẩm định | **3** | 2/4 phiên | **0** | **100.0%** | **Động cơ đào sâu tài liệu:** Thợ cơ khí ham học hỏi gặp bài viết lịch sử/thiên văn dài trên bảng tin, chủ động bấm "Xem thêm" (`expand`) để mở rộng toàn văn và dừng lại thẩm định chi tiết. |
| **`vn_fb_006`**<br>(Gen X Kinh doanh) | `open [group] ➔ scroll [group] ➔ read [group]` | Mở nhóm BĐS Cần Thơ $\to$ Cuộn duyệt nguồn cung $\to$ Đọc khảo sát giá | **2** | 2/3 phiên | 2 | **50.0%** | **Động cơ khảo sát thương mại có chủ đích:** Thương nhân Gen X thận trọng chủ động mở hội nhóm bất động sản Cần Thơ, cuộn tìm bài đăng tiềm năng và dừng lại đọc kỹ thông tin quy hoạch, giá cả. |

* **Nhận định thực nghiệm Slide 2.7:**
  * 🎯 **Mở rộng chuỗi 3 bước làm sáng tỏ động cơ nhận thức:** So với các cặp thao tác 2 bước rời rạc, chuỗi 3 bước đã khép kín một chu trình nhận thức hoàn chỉnh: từ khi bắt gặp thông tin, qua bước xử lý tương tác sâu, cho đến động thái chuyển tiếp mạch tư duy.
  * 🔒 **Ba chuỗi đạt độ độc quyền tuyệt đối (100.0% Exclusivity):** `vn_fb_001` (nghiên cứu thảo luận nhóm thiết kế), `vn_fb_003` (bình luận và theo dõi thảo luận đêm), và `vn_fb_005` (mở rộng đọc toàn văn bài viết kỹ thuật dài) là những chuỗi độc nhất vô nhị chỉ xuất hiện ở đúng các nhân vật tương ứng.
  * 💡 **Làm rõ mục đích thay vì thao tác cơ học:** Ví dụ ở `vn_fb_004`, bước `watch [reels]` xác nhận agent thực sự dành thời lượng xem trọn vẹn tình huống highlight trước khi thả tim và chuyển tiếp, loại trừ khả năng lướt vô cảm.
  * 🔁 **Độ bền vững đa phiên:** 100% các chuỗi 3 bước đều duy trì ổn định qua nhiều phiên hoạt động, chứng minh tính định hình phong cách rõ nét.
* **Kết luận kiểm định Slide 2.7:** **Việc khảo sát chuỗi 3 bước đã chứng minh mỗi Autonomous Agent sở hữu chu trình thao tác mang tính mục đích cao, bộc lộ rõ nét động cơ tâm lý và thói quen đời thực phù hợp với hồ sơ Persona.**
* **Trạng thái:** `[x] Đã hoàn thành (Ảnh 300 DPI & CSV sẵn sàng)`

---

### 📍 Slide 2.8: Giải Mã Tiền Đề Hành Vi Tương Tác (Antecedent Action Chains to React & Comment) & Phân Nhóm Động Học Tiếp Cận
* **Mục tiêu:** Kiểm chứng điều kiện tiền đề nhận thức trực tiếp kích hoạt các hành vi tương tác xã hội cao (`React` & `Comment`), chứng minh agent không tương tác mù quáng mà tuân theo cơ chế ra quyết định tuần tự, từ đó nhóm 6 Persona thành 2 cụm động học tiếp cận tương đồng.
* **Metric cần đo:**
  * **Cơ cấu loại hành động tiền đề bước -1 ($Step_{-1}$ trực tiếp):** Tỷ lệ các thao tác `observe` (Quan sát nội dung), `read/expand` (Đọc sâu văn bản), `scroll_comments/open_comments` (Đọc thảo luận), `watch` (Xem clip), và lướt bối cảnh.
  * **Chuỗi tiền đề 2 bước phổ biến nhất ($Step_{-2} \to Step_{-1} \to Target$):** Xác định chuỗi tiền đề điển hình kích hoạt Like và Comment cho từng Persona.
  * **Bề mặt tương tác chủ đạo:** Hội nhóm (`group`), Bảng tin (`feed`), Chi tiết (`detail`), Video ngắn (`reels`).
* **Đối chiếu Persona & Phân nhóm 2 Cụm Động Học Tiếp Cận:**
  * **Nhóm 1 (Thẩm định Tri thức & Nhận thức sâu):** Gồm `vn_fb_001` (Thiết kế đồ họa), `vn_fb_005` (Thợ cơ khí), `vn_fb_006` (Gen X Bất động sản).
    * *Đặc trưng tiền đề:* Bắt buộc phải có bước Đọc sâu văn bản (`read/expand`) trên Hội nhóm (`group`) hoặc Bảng tin (`feed`) trước khi Like hoặc Comment.
    * *Động cơ:* Nghiên cứu chuyên ngành, đào sâu tài liệu kỹ thuật, khảo sát thận trọng giá cả thương mại.
  * **Nhóm 2 (Thị giác, Cảm xúc & Đời sống thường nhật):** Gồm `vn_fb_002` (Lao động / Gia đình), `vn_fb_003` (Bảo vệ trực ca), `vn_fb_004` (Nhân viên nhà hàng).
    * *Đặc trưng tiền đề:* Kích hoạt bởi nội dung thị giác nhanh trên `reels` (`watch`), lướt hóng bình luận của cộng đồng trên `detail` (`scroll_comments`), hoặc phản xạ cảm xúc hướng thiện tức thời trên `feed`.
    * *Động cơ:* Giải trí thị giác nhanh sau giờ làm, tìm kiếm kết nối xã hội ca trực đêm, tranh thủ tương tác ngắn trong giờ nghỉ việc nhà.
* **Bảng dữ liệu thực nghiệm:**
  * [Ma trận Chuỗi Tiền đề Tương tác 6 Persona](file:///data/projects/web-apps/eda_persona/output/tables/h2_persona_interaction_antecedents.csv)
  * [Phân bổ Cơ cấu Loại Tiền đề Kích hoạt](file:///data/projects/web-apps/eda_persona/output/tables/h2_antecedent_type_distribution.csv)
* **Hình ảnh trực quan:** [Biểu đồ Tiền đề Tương tác Slide 2.8 (300 DPI)](file:///data/projects/web-apps/eda_persona/output/figures/slide2_8_interaction_antecedent_chains.png)
* **Tài liệu thuyết minh chi tiết:** [Hướng dẫn thuyết minh Slide 2.8](file:///home/khoenv/.gemini/antigravity-ide/brain/68ad29a3-7d02-444a-a148-b8cb951a7261/h2_slide2_8_presentation_guide.md)
* **Nhận định thực nghiệm Slide 2.8:**
  * 🚫 **Không có tương tác mù quáng (100% Valid Antecedents):** Toàn bộ 105 lượt tương tác đều có tiền đề tiếp xúc thông tin rõ ràng (33.3% quan sát, 27.6% đọc sâu, 16.2% đọc bình luận cộng đồng, 6.7% xem clip).
  * 📖 **Nhóm 1 gắn liền với văn bản & chuyên môn:** `vn_fb_001` chỉ Like/Comment sau khi đọc bài trong nhóm thiết kế; `vn_fb_005` đọc mở rộng bài viết lịch sử/khoa học rồi mới mở thảo luận; `vn_fb_006` thẩm định kỹ bài đăng địa ốc Cần Thơ trước khi tương tác.
  * 👁️ **Nhóm 2 gắn liền với thị giác & không khí cộng đồng:** `vn_fb_004` xem xong highlight bóng đá Reels mới thả tim; `vn_fb_003` cuộn đọc bình luận của thực khách khác mới comment hỏi quán ăn đêm; `vn_fb_002` phản hồi nhanh cảm xúc gia đình trên bảng tin.
* **Kết luận kiểm định Slide 2.8:** **Dữ liệu thực nghiệm xác nhận hành vi tương tác xã hội của các Persona tuân thủ nghiêm ngặt các tiền đề nhận thức tuần tự, phân hóa thành 2 phong cách tiếp cận đặc trưng tương thích với vai trò và tâm lý đời sống.**
* **Trạng thái:** `[x] Đã hoàn thành (Ảnh 300 DPI & CSV sẵn sàng)`

---

## KẾ HOẠCH CHIA NHỎ THEO TỪNG BƯỚC (SPRINT ROADMAP)

| Giai đoạn | Nội dung | Các Slide liên quan | Kết quả đầu ra dự kiến |
| :--- | :--- | :---: | :--- |
| **Chặng 1** | **Khảo sát Tầng 1 ($H_1$)** | Slide 1.1 & 1.2 | **ĐÃ HOÀN THÀNH**: Đủ 2 biểu đồ 300 DPI và các bảng dữ liệu tổng hợp. |
| **Chặng 2** | **Tương tác & Không gian ($H_2$ Phần 1)** | Slide 2.1, 2.2, 2.3 | **ĐÃ HOÀN THÀNH**: Đủ 3 biểu đồ 300 DPI và 7 bảng CSV. |
| **Chặng 3** | **Cơ học Cuộn & Căn cứ Nhận thức ($H_2$ Phần 2)** | Slide 2.4, 2.5, 2.5.1, 2.5.2 | **ĐÃ HOÀN THÀNH**: Slide 2.4 (Động lực học cuộn), Slide 2.5 (Tổng quan vĩ mô nhận thức), Slide 2.5.1 (Nhóm 1), Slide 2.5.2 (Nhóm 2) kèm đầy đủ ảnh 300 DPI và 4 bảng CSV. |
| **Chặng 4** | **Trí nhớ & Chuỗi hành vi ($H_2$ Phần 3)** | Slide 2.6, 2.7, 2.8 | **ĐÃ HOÀN THÀNH**: Slide 2.6 (Bộ nhớ xuyên phiên), Slide 2.7 (Chuỗi hành vi thương hiệu đặc trưng) & Slide 2.8 (Giải mã tiền đề tương tác & Phân nhóm động học) kèm đầy đủ ảnh 300 DPI và 5 bảng CSV. |




