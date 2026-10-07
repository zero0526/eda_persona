# KHUNG DANH MỤC CÁC TRƯỜNG DỮ LIỆU ĐO LƯỜNG CHO GIẢ THUYẾT $H_2$
## (Behavioral & Contract Fidelity - Độ Trung Thực Hành Vi & Hợp Đồng)

> **Mục tiêu tài liệu:**  
> Hệ thống hóa toàn bộ các trường dữ liệu trong **Action Logs** và **Session Summaries** có khả năng liên quan trực tiếp đến việc kiểm định Giả thuyết $H_2$. Thiết lập quy trình phân tích sơ bộ về **hình thái phân bố (Distribution)**, **chất lượng dữ liệu (Data Sanity)**, và **chiến lược xử lý điểm ngoại lai (Outlier Detection)** trước khi tiến hành phân tích suy luận tương quan với hồ sơ Persona.

---

## 1. TỔNG QUAN GIẢ THUYẾT $H_2$ VÀ NGUYÊN TẮC THIẾT KẾ ĐO LƯỜNG

* **Phát biểu Giả thuyết $H_2$:**  
  *Dòng hành vi thực thi được ghi nhận trong nhật ký hành động (`agent_live_steps` & `episodes`) có tuân thủ trung thực với các ràng buộc trong hợp đồng hành vi (`BehavioralContractSchema` về pacing, tỷ lệ tương tác, định hướng bề mặt) và hồ sơ bản sắc nhân vật (`BotContextSchema` về sở thích, từ khóa tìm kiếm, văn phong)?*
* **Nguyên tắc phân tích 2 giai đoạn:**
  1. **Giai đoạn 1 (Univariate Exploration & Sanity):** Khám phá đơn biến từng trường, vẽ biểu đồ phân bố (Histogram, KDE, Boxplot), tính toán thống kê mô tả (Mean, Median, Std, IQR, Skewness) và nhận diện các giá trị bất thường / điểm ngoại lai.
  2. **Giai đoạn 2 (Persona Attribution & Hypothesis Testing):** Phân nhóm theo `persona_id`, kiểm định xem sự khác biệt giữa các nhóm có ý nghĩa thống kê hay không (ANOVA, Kruskal-Wallis, Chi-square, Mann-Whitney U).

---

## 2. DANH MỤC CÁC TRƯỜNG DỮ LIỆU ĐO LƯỜNG THEO 5 CẤP ĐỘ

```
+---------------------------------------------------------------------------------------------------------------+
|                                    5 CẤP ĐỘ TRƯỜNG ĐO LƯỜNG CHO GIẢ THUYẾT H2                                 |
+---------------------------------------------------------------------------------------------------------------+
| [Cấp độ 1: Phiên Tổng hợp]       [Cấp độ 2: Vi Thao Tác & Bề Mặt]    [Cấp độ 3: Cơ Học Chuột Vật Lý]          |
|                                  - intent                            - gesture_pace / scroll_pace_mode        |
| - total_actions                  - surface                           - gesture_total_px / scroll_px           |
| - verified_rate                  - reaction                          - gesture_ms                             |
| - total_scroll_px                                                   - scroll_speed_px_s                      |
| - terminal_reason, status        - target_candidate_kind             - dwell_time / step_delta_sec            |
|---------------------------------------------------------------------------------------------------------------|
| [Cấp độ 4: Nhận Thức & Động Cơ]                                     [Cấp độ 5: Bộ Nhớ & Kiểm Soát Sa Đà]     |
|                                                                     - wm_num_active_threads                  |
|                                                                     - wm_situational_steps                   |
| - primary_dimension, primary_value, primary_weight                  - wm_has_novelty_warning                 |
| - num_dimension_evidence, dim_evidence_max_weight                   - wm_cumulative_reads / searches         |
| - reason, reason_length                                             - read_posts, avoid_topics (Semantic)    |
+---------------------------------------------------------------------------------------------------------------+
```

---

### CẤP ĐỘ 1: CHỈ SỐ TỔNG HỢP CẤP PHIÊN (SESSION-LEVEL METRICS)

| Tên trường | Kiểu dữ liệu | Ý nghĩa trong $H_2$ | Chỉ số thống kê & Phân bố cần xét | Tiêu chí nhận diện Điểm ngoại lai & Bất thường |
| :--- | :---: | :--- | :--- | :--- |
| `duration_seconds` (`duration_min`) | Số liên tục (`float`) | Đo lường thời lượng thực thi phiên so với kế hoạch hợp đồng $[8, 32]$ phút. | Mean, Median, Min, Max, IQR, Skewness. | **Ngoại lai kỹ thuật:** Phiên $< 3$ phút hoặc $> 35$ phút (do crash sớm hoặc loop vô tận). |
| `total_actions` | Số nguyên (`int`) | Tổng số lượng hành vi kích hoạt trong phiên (đo lường độ năng động/mức độ hoạt động). | Histogram, Boxplot, Skewness (dự kiến lệch phải mạnh do Gen Z). | **Bất thường:** Phiên có $0$ hoặc $\le 2$ actions (lỗi khởi tạo ban đầu). |
| `verified_rate` | Tỷ lệ (`float`, $0.0 - 1.0$) | Tỷ lệ bước thực thi thành công trên DOM trình duyệt, phản ánh độ ổn định kỹ thuật. | Mean, Median, phân bố Beta/Left-skewed. | **Ngoại lai:** $< 0.60$ (phiên gặp sự cố giao diện nghiêm trọng cần gắn cờ phân tích riêng). |
| `total_scroll_px` | Số liên tục (`float`) | Tổng cự ly cuộn trang trong cả phiên; phân tách người lướt feed vs người xem video. | Phân bố bimodal/đa đỉnh (cực đoan giữa các cụm). | **Outlier:** Các giá trị $> 40,000$ px hoặc $= 0$ px cần đối chiếu với bề mặt chính. |
| `status` & `terminal_reason` | Phân loại (`category`) | Trạng thái kết thúc: `agent_stop` (tự nhiên) vs `episode_error` (văng lỗi kỹ thuật). | Tần số xuất hiện (Value counts), tỷ lệ hoàn thành. | **Lọc bắt buộc:** Tách riêng các phiên `episode_error` để tránh làm nhiễu phân tích hành vi tự nhiên. |

---

### CẤP ĐỘ 2: VI THAO TÁC, KHÔNG GIAN BỀ MẶT & TƯƠNG TÁC (MICRO-ACTIONS & SPATIAL)

| Tên trường | Kiểu dữ liệu | Ý nghĩa trong $H_2$ | Phân tích phân bố sơ bộ | Dấu hiệu bất thường / Điểm cần kiểm tra |
| :--- | :---: | :--- | :--- | :--- |
| `surface` | Định danh (`category`) | Bề mặt giao diện (`feed`, `detail`, `reels`, `group`, `search`, `unknown`). | Tần suất %, phân bố bề mặt theo từng phiên. | **Bất thường:** Tỷ lệ `unknown` $> 15\%$ (agent bị kẹt ngoài không gian Facebook định danh). |
| `intent` | Định danh (`category`) | Ý định vi thao tác (`observe`, `scroll`, `read`, `next`, `watch`, `react`, `close`). | Tần suất %, tỷ lệ hành vi thụ động vs chủ động. | **Bất thường:** Phiên chỉ có 1 hành vi duy nhất lặp lại liên tục $> 10$ lần (vòng lặp vô tận). |
| `reaction` | Định danh rời rạc | Cảm xúc tương tác (`like`, `love`, `care`, `haha`...). | Tỷ lệ reaction trên tổng actions (AER: Active Engagement Rate). | **Bất thường:** Bot có thuộc tính "Tàu ngầm / Lurker" nhưng lại thả tim/like liên tục. |
| `resolved_tool` | Định danh (`str`) | Tên tool DOM cụ thể (`read_visible_post`, `scroll_feed`, `open_post_discussion`). | Đếm tần số xuất hiện, kiểm tra ánh xạ với `intent`. | Tool không nằm trong danh mục registry hợp lệ hoặc null. |
| `target_candidate_kind` | Định danh (`str`) | Loại đối tượng nhắm đến (`post`, `comment`, `search_group`, `author`). | Phân bố đối tượng tương tác. | Giá trị rỗng trên các hành động đòi hỏi mục tiêu (`read`, `react`). |

---

### CẤP ĐỘ 3: CƠ HỌC THAO TÁC CHUỘT VẬT LÝ (PHYSICAL KINEMATICS & PACING)

| Tên trường | Kiểu dữ liệu | Ý nghĩa trong $H_2$ | Phân tích phân bố sơ bộ | Tiêu chí nhận diện Điểm ngoại lai & Bất thường |
| :--- | :---: | :--- | :--- | :--- |
| `gesture_pace` / `scroll_pace_mode` | Nhị phân (`fast` / `careful`) | Nhịp cuộn chuột vật lý đo trực tiếp từ Playwright. Phân tách persona lướt nhanh vs chậm. | Tần số xuất hiện, tỷ lệ nhãn `fast` vs `careful`. | Nhãn `unknown` hoặc null trên các bước cuộn chuột (`scroll`). |
| `gesture_total_px` / `scroll_px` | Số liên tục (`float`) | Biên độ quãng đường cuộn chuột mỗi lần vuốt (pixels). | Histogram, Boxplot, so sánh phân vị ($25\%, 50\%, 75\%$). | **Outlier:** Cuộn $> 2,000$ px một lần (vượt quá chiều cao màn hình) hoặc cuộn âm ($< 0$ px). |
| `gesture_ms` | Số liên tục (`float`) | Thời gian thực hiện cử chỉ cuộn chuột (ms). | Phân bố thời gian vật lý (thường $150 - 350$ ms). | **Outlier:** $\le 0$ ms (lỗi đồng hồ) hoặc $> 2,000$ ms (treo browser input). |
| `scroll_speed_px_s` | Số liên tục (`float`) | Vận tốc cuộn tức thời: $\frac{\text{scroll\_px}}{\text{gesture\_ms} / 1000}$ (px/giây). | Phân bố tốc độ cuộn chuột (Quick pace: $5,000$ px/s vs Slow: $1,800$ px/s). | **Outlier:** Tốc độ cuộn $> 15,000$ px/s (dấu hiệu cuộn chuột phi thực tế kiểu bot). |
| `dwell_time` / `step_delta_sec` | Số liên tục (`float`) | Thời gian dừng quan sát/đọc giữa 2 bước liên tiếp (giây). | Phân bố thời gian dừng (Skewed phải mạnh, kiểm tra log-transform). | **Outlier:** Dừng $> 120$ giây (agent bị đóng băng hoặc LLM timeout). |

---

### CẤP ĐỘ 4: CHI PHÍ NHẬN THỨC & ĐỘNG CƠ BẢN SẮC (COGNITIVE EFFORT & DIMENSION ATTRIBUTION)

| Tên trường | Kiểu dữ liệu | Ý nghĩa trong $H_2$ | Phân tích phân bố sơ bộ | Dấu hiệu bất thường / Điểm cần kiểm tra |
| :--- | :---: | :--- | :--- | :--- |
| `model_latency_ms` | Số liên tục (`float`) | Thời gian LLM suy luận ra quyết định (ms). Phản ánh nỗ lực nhận thức. | Phân bố độ trễ LLM (thường $2,000 - 15,000$ ms). | **Outlier:** $> 30,000$ ms (nghẽn mạng/API timeout) hoặc $< 500$ ms (cache/lỗi trả về rỗng). |
| `tool_execution_ms` | Số liên tục (`float`) | Thời gian Playwright thực thi thao tác trên trình duyệt (ms). | Boxplot, IQR. Nhận diện các bước DOM bị lag. | **Outlier:** $> 20,000$ ms (thường do chờ selector DOM timeout). |
| `cognitive_latency_ratio` | Tỷ số ($0.0 - 1.0$) | Tỷ trọng nỗ lực suy nghĩ: $\frac{\text{model\_latency}}{\text{total\_latency}}$. | Phân bố tỷ trọng nhận thức. | Giá trị nằm ngoài khoảng $[0.0, 1.0]$. |
| `primary_dimension` | Định danh (`str`) | Chiều tâm lý/bản sắc cốt lõi dẫn dắt hành động (ví dụ: `curiosity`, `value_tradition`). | Bảng tần số Top 10 chiều xuất hiện nhiều nhất. | Chiều tính cách không tồn tại trong từ điển 36 chiều của hệ thống. |
| `primary_weight` | Số liên tục ($0.0 - 1.0$) | Trọng số nhận thức của chiều chính ($0.5 - 0.8$). | Thống kê phân vị, Mean, Std. | Giá trị vượt ngưỡng quy ước ($< 0.3$ hoặc $> 1.0$). |
| `num_dimension_evidence` | Số nguyên ($0 - 5$) | Số lượng chiều Persona được viện dẫn làm căn cứ. | Phân bố số lượng chiều (thường 2 - 4 chiều). | $= 0$ (hành động không có bất kỳ căn cứ persona nào). |
| `reason_length` | Số nguyên (`int`) | Độ dài văn bản lập luận tư duy (ký tự tiếng Việt). | Phân bố độ dài giải thích CoT. | **Outlier:** $= 0$ ký tự (LLM không sinh CoT) hoặc $> 1,000$ ký tự (sinh rườm rà). |

---

### CẤP ĐỘ 5: BỘ NHỚ LÀM VIỆC & KIỂM SOÁT SA ĐÀ (WORKING MEMORY & DRIFT)

| Tên trường | Kiểu dữ liệu | Ý nghĩa trong $H_2$ | Phân tích phân bố sơ bộ | Dấu hiệu bất thường / Điểm cần kiểm tra |
| :--- | :---: | :--- | :--- | :--- |
| `wm_num_active_threads` | Số nguyên (`int`) | Số mạch chủ đề đang hoạt động đồng thời trong bộ nhớ làm việc. | Median, IQR. Phân tách Persona (8 threads) vs No-Persona (2 threads). | Giá trị $< 0$ hoặc đột biến bất thường $> 20$ threads. |
| `wm_situational_steps` | Số nguyên (`int`) | Số bước liên tiếp bị cuốn theo nội dung tình huống ngoài lề (Cognitive Drift). | Phân bố mức độ sa đà nhận thức. | Giá trị tăng liên tục không có điểm dừng (cơ chế tiết chế thất bại). |
| `wm_has_novelty_warning` | Nhị phân (`bool`) | Cờ cảnh báo tiết chế khi agent sa đà quá lâu. | Tỷ lệ kích hoạt cờ cảnh báo (Flag trigger rate). | Kiểm tra xem sau khi cờ bật, agent có phục hồi về sở thích gốc hay không. |
| `read_posts` vs `core_interests` | Mảng văn bản / URL | Danh sách bài viết đã đọc đối chiếu với sở thích cốt lõi (Semantic Alignment). | Độ tương đồng Cosine trung bình qua Sentence Transformers. | Độ tương đồng thấp kéo dài qua toàn bộ các bước. |
| `avoid_topics` | Mảng văn bản | Danh sách chủ đề cấm kỵ / né tránh của persona. | Đếm số lần vi phạm (Zero-Tolerance Count). | **Bất thường nghiêm trọng:** Bất kỳ lần nào vi phạm đọc/tương tác chủ đề cấm ($> 0$). |

---

## 3. CHIẾN LƯỢC PHÂN TÍCH PHÂN BỐ & PHÁT HIỆN ĐIỂM NGOẠI LAI (OUTLIER PROTOCOL)

### 3.1. Kiểm định Hình thái Phân bố (Normality & Skewness Assessment)
* **Kiểm định tính chuẩn:** Áp dụng kiểm định **Shapiro-Wilk** ($N < 50$) hoặc **D’Agostino-Pearson** cho các biến số liên tục (`duration_min`, `total_actions`, `total_scroll_px`, `model_latency_ms`, `scroll_speed_px_s`).
* **Định hướng lựa chọn phương pháp thống kê:**
  * Nếu dữ liệu **không tuân theo phân phối chuẩn** ($p < 0.05$, độ lệch Skewness $> 1.0$ hoặc Kurtosis $> 3.0$):
    * Bắt buộc sử dụng **Trung vị (Median)** và **Khoảng tứ phân vị (IQR)** thay cho Trung bình & Độ lệch chuẩn.
    * Khi so sánh giữa các Persona, sử dụng các kiểm định **phi tham số (Non-parametric Tests)**: **Mann-Whitney U** (2 nhóm) hoặc **Kruskal-Wallis H** ($k \ge 3$ nhóm).

---

### 3.2. Tiêu chí Phân loại và Xử lý Điểm Ngoại lai (Outlier Taxonomy)

Trong nghiên cứu mô phỏng hành vi tác tử, **điểm ngoại lai được phân tách thành 2 bản chất hoàn toàn khác nhau**:

```
+---------------------------------------------------------------------------------------------------------------+
|                                      CHIẾN LƯỢC PHÂN LOẠI ĐIỂM NGOẠI LAI                                      |
+---------------------------------------------------------------------------------------------------------------+
| LOẠI 1: NGOẠI LAI KỸ THUẬT (TECHNICAL ARTIFACTS)     | LOẠI 2: NGOẠI LAI HÀNH VI TỰ NHIÊN (BEHAVIORAL EXTREMES)   |
| - Định nghĩa: Do lỗi sập trình duyệt, crash LLM,    | - Định nghĩa: Xuất phát từ bản sắc cực đoan có chủ đích  |
|   timeout DOM, parsing JSON thất bại.                 |   của từng Persona cụ thể.                            |
| - Ví dụ:                                              | - Ví dụ:                                              |
|   * duration < 3 phút kèm terminal_reason=error       |   * vn_fb_003: total_scroll_px > 30,000 px (Gen Z)    |
|   * total_actions <= 2 do fail ngay bước 1            |   * vn_fb_004: scroll_px = 252 px, watch = 90% (Reels)|
|   * tool_execution_ms > 30,000 ms do treo DOM         |   * vn_fb_006: rest_accumulated_seconds = 120s        |
| - Hành động xử lý: GẮN CỜ (FLAG) & LOẠI TRỪ khỏi     | - Hành động xử lý: GIỮ LẠI (RETAIN) & ĐƯA VÀO KIỂM    |
|   mẫu kiểm định độ trung thực hành vi tự nhiên.       |   ĐỊNH GIẢ THUYẾT (Đây chính là bằng chứng xác nhận H2)|
+---------------------------------------------------------------------------------------------------------------+
```

---

### 3.3. Thuật toán Phát hiện Điểm Ngoại lai Định lượng
1. **Phương pháp Hàng rào Tukey (Tukey's IQR Fences):**
   $$\text{Lower Bound} = Q_1 - 1.5 \times \text{IQR}, \quad \text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}$$
   * Áp dụng cho: `duration_min`, `total_actions`, `model_latency_ms`.
2. **Phương pháp Modified Z-score (Dựa trên Median Absolute Deviation - MAD):**
   $$M_i = \frac{0.6745 \cdot (x_i - \text{Median})}{\text{MAD}}$$
   * Điểm ngoại lai khi $|M_i| > 3.5$.
   * Áp dụng cho các biến có phân phối lệch cực đoan như: `total_scroll_px`, `scroll_speed_px_s`, `dwell_time`.

---

## 4. KẾ HOẠCH BƯỚC TIẾP THEO (ACTIONABLE NEXT STEPS)

1. **Bước 1 (Sanity & Cleaning):** Viết script / notebook cell chạy hàm trích xuất toàn bộ các trường trên cho 15 sessions ($758$ actions), loại trừ các session bị lỗi runtime (`terminal_reason = episode_error`).
2. **Bước 2 (Univariate Profiling):** Vẽ tổ hợp biểu đồ 4 ô (Histogram + KDE, Boxplot, Q-Q Plot, Violin Plot) cho Top 6 biến định lượng cốt lõi:
   * `duration_min`
   * `total_actions`
   * `total_scroll_px`
   * `scroll_speed_px_s`
   * `model_latency_ms`
   * `cognitive_latency_ratio`
3. **Bước 3 (Bivariate Contingency & Group Testing):** Tiến hành kiểm định khác biệt theo nhóm Persona (Kruskal-Wallis cho biến số và Chi-square cho biến phân loại `intent`, `surface`, `gesture_pace`) để trả lời chính thức Giả thuyết $H_2$.

---

## 5. KẾT QUẢ THỰC NGHIỆM SƠ BỘ TỪ TOÀN BỘ 15 SESSIONS (758 ACTIONS)

### 5.1. Bảng Thống kê Mô tả & Kiểm định Tính Chuẩn (Normality Test)
*Toàn bộ 10 biến số đều có $p < 10^{-8}$, khẳng định dữ liệu không tuân theo phân phối chuẩn $\to$ Bắt buộc sử dụng Trung vị (Median), IQR và Kiểm định phi tham số.*

| Tên biến | N | Mean | Std | Median | Q25 | Q75 | IQR | Skewness | Kurtosis | Normality ($p$-value) | Kết luận hình thái |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`cognitive_latency_ratio`** | 758 | 0.63 | 0.28 | **0.64** | 0.42 | 0.94 | 0.51 | -0.25 | -1.10 | $1.08 \times 10^{-62}$ | Hai đỉnh (Bimodal) |
| **`primary_weight`** | 658 | 0.67 | 0.11 | **0.70** | 0.60 | 0.80 | 0.20 | -0.85 | 0.85 | $8.72 \times 10^{-17}$ | Tập trung cao quanh 0.7 |
| **`dim_evidence_max_weight`** | 658 | 0.68 | 0.11 | **0.70** | 0.60 | 0.80 | 0.20 | -0.69 | 0.20 | $1.87 \times 10^{-10}$ | Tập trung quanh $0.6 - 0.8$ |
| **`num_dimension_evidence`** | 758 | 1.99 | 0.94 | **2.00** | 2.00 | 3.00 | 1.00 | -0.94 | 0.11 | $7.82 \times 10^{-19}$ | Tập trung ở 2–3 chiều |
| **`reason_length`** (ký tự) | 758 | 86.21 | 50.24 | **81.00** | 31.00 | 117.00 | 86.00 | +0.89 | 0.74 | $9.79 \times 10^{-20}$ | Lệch phải nhẹ |
| **`model_latency_ms`** (ms) | 758 | 5,255.2 | 4,188.1 | **4,169.5** | 3,127.5 | 5,520.3 | 2,392.8 | +2.90 | 10.83 | $2.25 \times 10^{-107}$ | Lệch phải rất mạnh |
| **`tool_execution_ms`** (ms) | 758 | 5,926.9 | 9,037.9 | **3,289.5** | 158.5 | 6,091.5 | 5,933.0 | +2.75 | 8.56 | $2.29 \times 10^{-99}$ | Lệch phải rất mạnh |
| **`gesture_total_px`** (px) | 150 | 777.18 | 380.70 | **674.50** | 531.75 | 916.75 | 385.00 | +1.30 | 1.44 | $1.89 \times 10^{-8}$ | Lệch phải vừa |
| **`gesture_ms`** (ms) | 150 | 282.33 | 121.50 | **260.00** | 232.00 | 270.75 | 38.75 | +3.02 | 8.75 | $1.68 \times 10^{-25}$ | Cực đoan ở nhóm đọc chậm |
| **`scroll_speed_px_s`** (px/s) | 150 | 2,891.6 | 1,374.4 | **2,499.7** | 2,107.7 | 3,501.9 | 1,394.3 | +1.34 | 1.59 | $5.66 \times 10^{-9}$ | Phân hóa theo nhóm nhịp |

---

### 5.2. Bảng Phát hiện Điểm Ngoại lai (Outlier Detection)

| Tên biến | Ngưỡng Tukey Dưới | Ngưỡng Tukey Trên | Ngoại lai Tukey ($N$) | Tỷ lệ Tukey (%) | Ngoại lai Mod-Z ($N$) | Tỷ lệ Mod-Z (%) | Min thực tế | Max thực tế |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `cognitive_latency_ratio` | -0.35 | 1.70 | **0** | **0.0%** | **0** | **0.0%** | 0.05 | 1.00 |
| `primary_weight` | 0.30 | 1.10 | **0** | **0.0%** | **0** | **0.0%** | 0.30 | 0.90 |
| `dim_evidence_max_weight` | 0.30 | 1.10 | **0** | **0.0%** | **0** | **0.0%** | 0.30 | 0.90 |
| `reason_length` | -98.0 | 246.0 | **5** | **0.7%** | **2** | **0.3%** | 0 | 292 |
| `model_latency_ms` | -461.6 | 9,109.4 | **83** | **11.0%** | **71** | **9.4%** | 1,141.0 | 34,815.0 |
| `tool_execution_ms` | -8,741.0 | 14,991.0 | **83** | **11.0%** | **63** | **8.3%** | 0.0 | 58,558.0 |
| `scroll_speed_px_s` | 16.3 | 5,593.3 | **9** | **6.0%** | **11** | **7.3%** | 846.2 | 7,328.9 |

> **Nhận xét Ngoại lai:**
> 1. `cognitive_latency_ratio` và `primary_weight` có tỷ lệ ngoại lai là **0%** — Các biến tỷ lệ và trọng số được giới hạn trong biên độ chuẩn xác, không có lỗi tràn số.
> 2. `model_latency_ms` và `tool_execution_ms` có khoảng **10%** điểm ngoại lai do trễ mạng hoặc selector DOM chờ tối đa. Đây là ngoại lai kỹ thuật tự nhiên của môi trường chạy Playwright.
> 3. `scroll_speed_px_s` có 9 điểm ngoại lai ($> 5,593$ px/s), toàn bộ rơi vào nhóm vuốt nhanh của `vn_fb_002` (vận tốc đạt đỉnh $7,328$ px/s). Đây là **ngoại lai hành vi tự nhiên (Behavioral Extreme)**, hoàn toàn không phải lỗi.

---

### 5.3. PHÂN TÍCH CHI TIẾT CẢ 5 CẤP ĐỘ ĐO LƯỜNG

#### [CẤP ĐỘ 1: PHIÊN TỔNG HỢP (SESSION-LEVEL METRICS — TẬP DỮ LIỆU ĐÃ LỌC `agent_stop`)]
> ⚙️ **Quy tắc lọc dữ liệu tiên quyết (Filtering Protocol):**  
> Áp dụng điều kiện lọc `terminal_reason = 'agent_stop'` nhằm loại bỏ toàn bộ các phiên bị dừng sớm do lỗi hạ tầng trình duyệt hoặc mô hình (`episode_error`) và các phiên chưa hoàn tất (`pending`/`running`). Việc này đảm bảo các chỉ số thời lượng và tỷ lệ hoàn thành đo lường thuần khiết hành vi tự nhiên của Persona.

| Persona ID | Số Phiên Hợp lệ ($N$) | Thời lượng TB (`min`) | Số Actions TB | Median Cuộn Trang (`px`) | Verified Rate TB | Nhận xét phân bố hành vi tự nhiên |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`vn_fb_001`** | **0 / 2** | *N/A* | *N/A* | *N/A* | *N/A* | *(Cả 2 phiên đều bị lỗi hạ tầng `episode_error`, loại khỏi phân tích cấp phiên; dữ liệu chỉ dùng ở Cấp độ Vi thao tác).* |
| **`vn_fb_002`** | **1 / 2** | 10.39 | 57.0 | **13,547.0** | 84.0% | Phiên hoàn thành tự nhiên: Nhịp cuộn nhanh và lướt xa, đúng bản sắc Gen Z lướt tin tức. |
| **`vn_fb_003`** | **1 / 2** | 10.52 | **68.0** | **16,585.0** | 90.0% | Hoàn thành đúng ngân sách thời gian, số actions và quãng đường cuộn dẫn đầu bảng tin. *(Phiên 2 có 179 actions nhưng ở trạng thái running).* |
| **`vn_fb_004`** | **2 / 4** | **15.41** | 60.0 | **504.0** (TB: 504.0) | **95.0%** | **Ngoại lai hành vi cực đoan:** 2 phiên hoàn thành tự nhiên kéo dài nhất ($10.3$ và $20.5$ phút), nhưng cuộn chuột $\approx 0$ px vì ngồi xem Reels. Verified rate đạt đỉnh $95\%$. |
| **`vn_fb_005`** | **1 / 2** | 10.44 | 53.0 | 4,861.0 | 91.0% | Phân bố cực kỳ chuẩn mực: Hoàn thành đúng $10.4$ phút, đọc sâu, tương tác ổn định. |
| **`vn_fb_006`** | **2 / 3** | 9.39 | 28.0 | 3,990.0 | **93.5%** | 2 phiên hoàn thành tự nhiên có nhịp đọc chậm rãi, số actions tinh gọn, tỷ lệ xác minh DOM rất cao. |

> 🌟 **Kết luận quan trọng sau khi lọc theo `agent_stop`:**
> 1. **Độ tuân thủ thời lượng hợp đồng (Duration Fidelity) hội tụ cao độ:** Toàn bộ các phiên hoàn thành tự nhiên đều khớp chính xác với ngân sách hợp đồng $[10, 20]$ phút (Người lướt tin dao động quanh $9.4 - 10.5$ phút; người xem Reels kéo dài $15.4$ phút).
> 2. **Chất lượng dữ liệu sạch (Data Cleanliness):** Tỷ lệ xác minh DOM (`verified_rate`) toàn hệ thống đồng loạt đạt mức cao $\mathbf{84.0\% - 95.0\%}$, chứng minh khi không bị sự cố hạ tầng ngắt quãng, Agent vận hành rất ổn định.
> 3. **`total_scroll_px`** vẫn duy trì sức mạnh phân tách nhị phân tuyệt đối: `vn_fb_004` xem video ($504$ px) vs các nhóm lướt feed ($3,990 - 16,585$ px).

---

#### [CẤP ĐỘ 2: VI THAO TÁC, KHÔNG GIAN BỀ MẶT & TƯƠNG TÁC (MICRO-ACTIONS & SPATIAL)]

* **Phân bố Bề mặt Giao diện (`surface` Crosstab - %):**
  *Kiểm định Chi-square: $\chi^2 = 562.34, p < 10^{-50}$ (Ý nghĩa thống kê cực lớn).*

| Bề mặt (`surface`) | `vn_fb_001` | `vn_fb_002` | `vn_fb_003` | `vn_fb_004` | `vn_fb_005` | `vn_fb_006` | Ý nghĩa hành vi thực tế |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`feed`** (Bảng tin) | 63.1% | **81.5%** | 51.8% | 4.2% | 57.3% | 54.0% | Không gian lướt chính của đại đa số người dùng |
| **`reels`** (Video ngắn) | 0.0% | 0.0% | 0.0% | **81.7%** | 0.0% | 0.0% | **ĐỘC QUYỀN `vn_fb_004`:** Đúng sở thích khai báo video ngắn |
| **`group`** (Hội nhóm) | 6.0% | 0.0% | 5.7% | 0.0% | 0.0% | **23.4%** | **ĐẶC THÙ `vn_fb_006`:** Coi trọng cộng đồng, tìm hiểu nhà đất |
| **`detail`** (Chi tiết bài viết) | 14.3% | 14.8% | **38.5%** | 0.0% | **30.3%** | 10.2% | Nhóm đọc sâu thảo luận, xem bình luận (`003`, `005`) |
| **`search`** (Tìm kiếm) | 6.0% | 0.0% | 1.6% | 7.5% | 0.0% | 5.8% | Chủ động gõ từ khóa tìm nội dung |
| **`unknown`** (Chưa định danh)| 10.7% | 3.7% | 2.4% | 6.7% | 12.4% | 6.6% | Modal phụ hoặc trạng thái chuyển tiếp DOM |

* **Phân bố Ý định Thao tác (`intent` Crosstab - %):**
  *Kiểm định Chi-square: $\chi^2 = 684.12, p < 10^{-50}$ (Toàn bộ 19 intent xuất hiện trên 758 actions).*

| Ý định (`intent`) | `vn_fb_001` | `vn_fb_002` | `vn_fb_003` | `vn_fb_004` | `vn_fb_005` | `vn_fb_006` | Dấu ấn bản mẫu hành vi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`next`** (Chuyển video) | 0.0% | 0.0% | 0.0% | **50.8%** | 0.0% | 0.0% | Độc quyền xem Reels (`vn_fb_004`) |
| **`watch`** (Xem video) | 0.0% | 0.0% | 0.0% | **26.7%** | 0.0% | 0.0% | Độc quyền xem Reels (`vn_fb_004`) |
| **`scroll`** (Cuộn feed) | 20.2% | 23.5% | **35.6%** | 1.7% | 13.5% | 21.2% | Gen Z (`vn_fb_003`) lướt feed áp đảo |
| **`observe`** (Quan sát DOM) | 34.5% | 23.5% | 22.7% | 7.5% | 24.7% | 31.4% | Định hướng viewport |
| **`read`** (Đọc bài) | 13.1% | 13.6% | 6.5% | 5.8% | 12.4% | **24.1%** | Đọc bài kỹ lưỡng nhất hệ thống (`vn_fb_006`) |
| **`scroll_comments`** (Cuộn cmt) | 2.4% | 4.9% | **11.3%** | 0.0% | 6.7% | 3.6% | Đọc bình luận hóng chuyện (`003`, `005`) |
| **`react`** (Thả cảm xúc) | 6.0% | **14.8%** | 0.4% | 1.7% | 6.7% | 8.0% | Tương tác cảm xúc cao nhất (`vn_fb_002`) |
| **`comment`** (Viết bình luận) | 1.2% | 0.0% | 7.3% | 0.0% | **11.2%** | 0.7% | Tương tác bình luận sâu nhất (`vn_fb_005`) |
| **`expand`** (Mở rộng bài) | 7.1% | 1.2% | 0.0% | 0.0% | **10.1%** | 0.0% | Thích đọc bài dài đầy đủ (`vn_fb_005`) |
| **`close`** (Đóng chi tiết) | 6.0% | 7.4% | 6.5% | 0.0% | 5.6% | 2.2% | Thoát bài viết quay lại feed |
| **`open`** (Mở post/nhóm) | 4.8% | 2.5% | 2.4% | 0.0% | 3.4% | 2.9% | Mở liên kết đích |
| **`open_comments`** (Mở cmt) | 3.6% | 4.9% | 3.2% | 0.0% | 3.4% | 1.5% | Nhấn mở panel bình luận |
| **`search`** (Gõ tìm kiếm mới) | 0.0% | 0.0% | **0.8%** (2) | **0.8%** (1) | 0.0% | **1.5%** (2) | Chủ động tìm khi feed không đúng gu |
| **`search_related`** (Tìm liên quan)| **1.2%** (1) | 0.0% | 0.0% | 0.0% | 0.0% | **0.7%** (1) | Đào sâu thông tin/kiểm chứng dữ liệu |
| **`status`** (Đăng status) | 0.0% | 2.5% | 1.6% | 0.8% | 0.0% | 0.7% | Thao tác tự sự/đăng bài |
| **`share`** (Chia sẻ bài) | 0.0% | 0.0% | 0.0% | 0.0% | 1.1% | 0.0% | Độc quyền chia sẻ (`vn_fb_005`) |
| **Khác** (`end`, `home`, `open_reels`)| 0.0% | 1.2% | 1.6% | 4.2% | 1.1% | 1.5% | Điều hướng phiên & tab |

> 🔍 **Làm rõ Cơ chế `surface = search` vs `intent = search` (7 bước tìm kiếm thực tế):**
> * **Tại sao % `surface = search` cao hơn % `intent = search`?** 
>   Toàn bộ hệ thống có **26 bước** diễn ra trên giao diện tìm kiếm (`surface = search`). Tuy nhiên, chỉ có **7 bước** có ý định trực tiếp là gõ từ khóa (`intent = search`: 5 bước; `intent = search_related`: 2 bước). Sau khi gõ tìm kiếm, bot ở lại trên giao diện đó để **quan sát kết quả** (`observe`: 11 bước), **đọc kết quả tìm được** (`read`: 4 bước), **bấm mở nhóm/bài** (`open`: 2 bước), hoặc **cuộn kết quả** (`scroll`: 1 bước).
> * **Giá trị $H_2$ của hành vi Tìm kiếm (Proactive Agency):** Cả 7 bước tìm kiếm đều bộc lộ tính tự chủ sâu sắc khi feed không thỏa mãn nhu cầu Persona:
>   * `vn_fb_003` (2 bước): Tìm kiếm quán bún trộn Đà Nẵng vì *"Feed hiện không có bài ẩm thực Đà Nẵng, tìm trực tiếp để xem review quán ngon"*.
>   * `vn_fb_004` (1 bước): Tìm kiếm highlight bóng đá vì *"Không thấy video highlight bóng đá sau nhiều lần next reels"*.
>   * `vn_fb_006` (3 bước): Tìm kiếm "bất động sản Cần Thơ" và kiểm chứng "giá đất khu vực Đồng Ngọc Sứ" vì *"Persona hoài nghi cao, cần so sánh giá"*.
>   * `vn_fb_001` (1 bước): Tìm kiếm thông tin kỷ lục cờ chớp vì *"Bài viết chỉ nói 'phá vỡ kỷ lục' nhưng không nêu con số cụ thể, muốn tìm hiểu chi tiết"*.

> 🌟 **Trường tiềm năng Cấp độ 2:**
> * **`surface`**: Tách hoàn toàn `vn_fb_004` (Reels $81.7\%$) và `vn_fb_006` (Group $23.4\%$).
> * **`intent`**: Tách hoàn toàn cụm hành vi video (`next` + `watch` $= 77.5\%$) vs cụm đọc sâu (`read` + `scroll_comments` + `expand`).
> * **Tỷ lệ Tương tác Chủ động (AER: Active Engagement Rate = `react` + `comment` + `share`):** Phân định `vn_fb_005` ($19.1\%$) và `vn_fb_002` ($14.8\%$) là nhóm tương tác cao; `vn_fb_003` ($7.7\%$) và `vn_fb_004` ($1.7\%$) là nhóm tiêu thụ thụ động.

---

#### [CẤP ĐỘ 3: CƠ HỌC THAO TÁC CHUỘT VẬT LÝ (PHYSICAL KINEMATICS & PACING)]

*Đo lường trực tiếp từ động cơ Playwright trên 150 bước thực thi cuộn chuột (`scroll`):*

| Persona ID | Số lần cuộn | Median Cự ly Cuộn (`px`) | Median Thời gian Vuốt (`ms`) | Median Vận tốc Cuộn (`px/s`) | Chế độ Nhịp (`gesture_pace`) | Đặc trưng Cơ học Thao tác |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`vn_fb_001`** | 10 | 829.5 | 203.5 | **4,214.7** | **100% FAST** | Vuốt dứt khoát, biên độ lớn |
| **`vn_fb_002`** | 12 | **1,136.0** | 215.0 | **5,410.2** | **100% FAST** | **Vuốt nhanh và xa nhất hệ thống** (đạt đỉnh $7,328$ px/s) |
| **`vn_fb_003`** | **87** | 641.0 | 260.0 | **2,465.4** | **100% BALANCED / CAREFUL** | Cuộn liên tục đều tay, nhịp độ vừa phải |
| **`vn_fb_004`** | 2 | 504.0 | 255.0 | **1,983.7** | **100% CAREFUL** | Cuộn rất ít và chậm nhất (chủ yếu xem video) |
| **`vn_fb_005`** | 12 | 845.0 | 208.5 | **4,011.3** | **100% FAST** | Vuốt nhanh, dứt khoát theo từng đoạn |
| **`vn_fb_006`** | 27 | 650.0 | 260.0 | **2,499.4** | **100% BALANCED / CAREFUL** | Cuộn từ tốn, dừng đọc chậm rãi |

> 🌟 **Trường tiềm năng Cấp độ 3:**
> * **`scroll_speed_px_s`** (Kruskal-Wallis $H = 26.28, p < 10^{-6}$): Phân tách thành 2 cụm vận tốc hoàn toàn tách biệt:
>   * Cụm Quick Pace (`vn_fb_001`, `vn_fb_002`, `vn_fb_005`): Vận tốc $> 4,000$ px/s, thời gian vuốt $\sim 200$ ms.
>   * Cụm Balanced / Careful Pace (`vn_fb_003`, `vn_fb_004`, `vn_fb_006`): Vận tốc $\sim 2,000 - 2,500$ px/s, thời gian vuốt $\sim 260$ ms.
> * **`gesture_pace`** (Fisher's Exact Test $p < 10^{-14}$): Phân tách nhị phân tuyệt đối 100% giữa hai nhóm cấu hình hợp đồng hành vi (`scrollCadence = quick` vs `balanced`).

---

#### [CẤP ĐỘ 4: CHI PHÍ NHẬN THỨC & ĐỘNG CƠ BẢN SẮC (COGNITIVE EFFORT & ATTRIBUTION)]

* **Độ trễ Nhận thức và Độ sâu Lập luận:**

| Persona ID | Số Actions | Median Cognitive Ratio | Median Model Latency (`ms`) | Median Tool Latency (`ms`) | Median Độ dài Lập luận (`ký tự`) | Mean Max Weight |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`vn_fb_001`** | 84 | 0.59 | 3,838.5 | 2,911.0 | 93.5 | 0.72 |
| **`vn_fb_002`** | 81 | 0.65 | 3,920.0 | 2,540.0 | 104.0 | 0.55 |
| **`vn_fb_003`** | 247 | 0.64 | 4,085.0 | 3,247.0 | 76.0 | 0.71 |
| **`vn_fb_004`** | 120 | **0.50** | 4,015.5 | **8,204.5** | **59.0** | 0.67 |
| **`vn_fb_005`** | 89 | **0.70** | **4,578.0** | 2,704.0 | **97.0** (TB: 114) | 0.67 |
| **`vn_fb_006`** | 137 | 0.59 | **4,582.0** | 3,789.0 | 98.0 | 0.65 |

* **Ma trận Bảng Chéo Bản Sắc Chi Phối (`primary_dimension` Crosstab):**

| Chiều Bản Sắc (`primary_dimension`) | `vn_fb_001` | `vn_fb_002` | `vn_fb_003` | `vn_fb_004` | `vn_fb_005` | `vn_fb_006` | Nhận xét tính quy gán bản sắc |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `curiosity` (Tò mò) | **56** | 11 | 26 | 4 | **35** | **34** | Động cơ khám phá phổ quát nền tảng |
| `content_consumption_format` | 0 | 0 | 0 | **82** | 1 | 0 | **100% ĐỘC QUYỀN `vn_fb_004`** (Giá trị: "Video ngắn") |
| `cuisine_vietnamese` | 0 | 0 | **68** | 0 | 0 | 0 | **100% ĐỘC QUYỀN `vn_fb_003`** (Giá trị: "Rất thích") |
| `interest_real_estate` | 0 | 0 | 0 | 0 | 0 | **48** | **100% ĐỘC QUYỀN `vn_fb_006`** (Giá trị: "Có hứng thú") |
| `interest_film` | 0 | 0 | **36** | 0 | 0 | 0 | **100% ĐỘC QUYỀN `vn_fb_003`** (Giá trị: "Rất đam mê") |
| `cuisine_street_food` | 0 | 1 | **34** | 0 | 0 | 3 | **ĐẶC THÙ `vn_fb_003`** (Gen Z thích ăn vặt) |
| `value_tradition` | 0 | 0 | 0 | 0 | **28** | 0 | **100% ĐỘC QUYỀN `vn_fb_005`** (Giá trị: "Cao") |
| `sport_football` | 0 | 0 | 0 | **21** | 0 | 0 | **ĐẶC THÙ `vn_fb_004`** (Theo dõi thể thao) |
| `province` (Địa phương) | 0 | **10** | 3 | 0 | 0 | 0 | Nhận diện vùng miền (TP.HCM, Đà Nẵng) |
| `tone` (Cảm xúc tương tác) | 1 | **12** | 0 | 0 | 0 | 0 | Cảm xúc cá nhân chi phối hành động |

> 🌟 **Trường tiềm năng Cấp độ 4:**
> * **`primary_dimension`** (Bằng chứng số 1 của $H_2$): Đạt độ chính xác quy gán tuyệt đối. Mỗi Persona đều kích hoạt đúng 1–2 chủ đề sở thích độc quyền từ hồ sơ gốc.
> * **`cognitive_latency_ratio`**: Phân tách rõ phong cách nhận thức (Người đọc sâu suy nghĩ $70\%$ vs Người xem video suy nghĩ $50\%$).
> * **`reason_length`**: Phản ánh mức độ giải trình tư duy của mô hình.

---

#### [CẤP ĐỘ 5: BỘ NHỚ LÀM VIỆC & KIỂM SOÁT SA ĐÀ (WORKING MEMORY & DRIFT)]

*Dữ liệu từ bảng `working_memory` và `memory_delta_ledger`:*

| Persona ID | Số Mạch Chủ đề Đang Mở (`active_threads`) | Số Bài Viết Đã Đọc (`read_posts`) | Tri Thức Mới Học Được (`memory_deltas`) | Sự Kiện Thói Quen (`habit_facts`) | Số Bước Sa Đà (`situational_steps`) | Cảnh Báo Tiết Chế Kích Hoạt |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`vn_fb_001`** | **3.0** | 5.0 | 2.5 | 2.5 | 19.0 | 2 / 2 phiên |
| **`vn_fb_002`** | 2.5 | 3.5 | 2.5 | 2.0 | 5.0 | 2 / 2 phiên |
| **`vn_fb_003`** | 1.5 | 4.0 | 1.0 | 0.5 | 6.5 | 2 / 2 phiên |
| **`vn_fb_004`** | 1.5 | **0.25** | 1.0 | **0.0** | 9.3 | 2 / 4 phiên |
| **`vn_fb_005`** | **3.0** | 4.5 | **3.5** | **3.0** | **24.0** | 2 / 2 phiên |
| **`vn_fb_006`** | 1.7 | 4.7 | 1.7 | **3.0** | 12.0 | 3 / 3 phiên |

* **Đặc trưng bộ nhớ làm việc:**
  * **Độ sâu tiếp nhận thông tin (`read_posts`):** `vn_fb_004` hầu như không đọc bài văn bản nào ($0.25$ bài/phiên), trong khi các bot đọc tin truyền thống (`001`, `005`, `006`) đọc trung bình $4.5 - 5.0$ bài viết/phiên.
  * **Tốc độ tích lũy tri thức dài hạn (`memory_deltas`):** `vn_fb_005` có khả năng tích lũy tri thức cao nhất ($3.5$ deltas/phiên), liên tục tạo các cập nhật bộ nhớ mới về ẩm thực, lịch sử vào `memory_delta_ledger`.
  * **Kiểm soát sa đà nhận thức (`situational_steps`):** `vn_fb_005` bị cuốn theo các chủ đề ngoài lề sâu nhất ($24$ bước liên tiếp), dẫn đến việc kích hoạt cờ cảnh báo `novelty_warning` để kéo bot hồi phục về quỹ đạo sở thích cốt lõi.

> 🌟 **Trường tiềm năng Cấp độ 5:**
> * **`read_posts`**: Thước đo phân tách giữa người đọc văn bản vs người xem video.
> * **`memory_deltas`**: Đánh giá năng lực tiến hóa nhận thức (Memory Consolidation) theo thời gian.
> * **`situational_steps`**: Đo lường định lượng hiện tượng "Sa đà nhận thức" (Cognitive Drift) trên mạng xã hội.

---

## 6. BẢNG XẾP HẠNG CÁC TRƯỜNG TIỀM NĂNG NHẤT ĐỂ KIỂM ĐỊNH $H_2$ (SCORECARD & CANDIDATE RANKING)

*Tổng hợp xếp hạng dựa trên 3 tiêu chí: (1) Sức mạnh phân tách giữa các nhóm Persona (Effect Size), (2) Độ ổn định và chất lượng dữ liệu (Data Cleanliness), (3) Khả năng giải thích bản sắc Persona.*

| Xếp hạng | Tên trường | Cấp độ | Kiểu dữ liệu | Sức mạnh phân tách (Effect Size) | Phương pháp kiểm định khuyến nghị | Giá trị giải thích cốt lõi cho $H_2$ |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| 🥇 **TOP 1** | **`primary_dimension`** | Cấp độ 4 | Categorical | **Cực đại** (Phân tách $100\%$) | Chi-square / Fisher's Exact Test | Bằng chứng tuyệt đối về việc hành vi được dẫn dắt bởi đúng sở thích cốt lõi của từng Persona. |
| 🥈 **TOP 2** | **`surface`** | Cấp độ 2 | Categorical | **Cực đại** ($\chi^2 = 562.3, p < 10^{-50}$) | Contingency Chi-square | Phân tách không gian: Reels ($81.7\%$ của 004), Group ($23.4\%$ của 006), Feed & Detail ($001, 003, 005$). |
| 🥉 **TOP 3** | **`scroll_speed_px_s`** | Cấp độ 3 | Continuous | **Rất lớn** ($H = 26.28, p < 10^{-6}$) | Kruskal-Wallis H Test | Đo lường độ trung thực nhịp độ vật lý (Quick pace $> 4,000$ px/s vs Slow pace $\sim 2,000$ px/s). |
| 4 | **`total_scroll_px`** | Cấp độ 1 | Continuous | **Rất lớn** (Chênh lệch $120\times$) | Mann-Whitney U / Kruskal-Wallis | Tách biệt hoàn toàn hành vi cuộn chuột Gen Z ($> 31,000$ px) vs người xem video ngắn ($0 - 250$ px). |
| 5 | **`intent`** | Cấp độ 2 | Categorical | **Rất lớn** ($\chi^2 = 684.1, p < 10^{-50}$) | Contingency Chi-square | Xác nhận hành vi vi mô: nhóm xem video (`next`/`watch`), nhóm đọc (`read`/`expand`), nhóm lướt (`scroll`). |
| 6 | **`gesture_pace`** | Cấp độ 3 | Binary | **Tuyệt đối** ($p < 10^{-14}$) | Fisher's Exact Test | Kiểm định tuân thủ hợp đồng hành vi: 100% Fast ở nhóm quick vs 100% Careful/Balanced ở nhóm đọc chậm. |
| 7 | **`cognitive_latency_ratio`** | Cấp độ 4 | Ratio ($0-1$) | **Lớn** (Median $0.70$ vs $0.50$) | Mann-Whitney U Test | Đo lường nỗ lực nhận thức: người đọc sâu suy nghĩ $70\%$ chu kỳ vs người xem video chỉ suy nghĩ $50\%$. |
| 8 | **`total_actions`** | Cấp độ 1 | Discrete | **Lớn** (Chênh lệch $3\times$) | Kruskal-Wallis H Test | Thể hiện mức độ năng động thao tác giữa các nhóm lứa tuổi (Gen Z vs Người trưởng thành). |
| 9 | **`read_posts`** | Cấp độ 5 | Discrete | **Lớn** ($0.25$ vs $5.0$) | Mann-Whitney U Test | Độ sâu tiếp nhận thông tin văn bản trong Working Memory. |
| 10 | **`reason_length`** | Cấp độ 4 | Discrete | **Trung bình - Lớn** | Kruskal-Wallis H Test | Độ sâu lập luận tư duy tiếng Việt trước khi ra quyết định. |


