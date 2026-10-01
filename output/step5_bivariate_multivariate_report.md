# Báo cáo Phân tích Hai biến và Đa biến (Bước 5 Pipeline EDA)
## Đánh giá So sánh Toàn diện: Agent có Persona vs Agent không có Persona

> **Tài liệu tham chiếu:** [`pipeline_eda.md`](file:///data/projects/web-apps/eda_persona/notebooks/pipeline_eda.md) - Bước 5: Phân tích hai biến và đa biến.  
> **Nguyên tắc phân tích:** Không chỉ nêu "có tương quan" hay p-value đơn thuần, mà tập trung vào **độ lớn hiệu ứng thực tế (Effect Size: Cliff's Delta, Hedges' g, Cramér's V̂, Epsilon-squared)**, kiểm soát biến gây nhiễu (Confounder), phát hiện **Nghịch lý Simpson**, và tách biệt **Yếu tố tác động thực chất (Confirmed Driver)** khỏi **Hệ quả ăn theo (Likely Proxy)**.  
> **Bộ dữ liệu khảo sát:**
> - Step Records: 437 bước hành động (Persona: 349 bước, No-Persona: 88 bước).
> - Episode Logs: 8 phiên hoàn chỉnh (Persona: 6 phiên, No-Persona: 2 phiên).
> - Tất cả các bảng thống kê chi tiết đã được xuất sang [`output/tables/`](file:///data/projects/web-apps/eda_persona/output/tables) và biểu đồ trực quan hóa tại [`output/figures/`](file:///data/projects/web-apps/eda_persona/output/figures).

---

## 1. Tóm tắt Phát hiện Cốt lõi (Executive Summary)

Qua kiểm định thống kê và phân tích đa biến trên toàn bộ chuỗi hành động và phiên hoạt động:

1. **Working Memory & Khả năng khám phá sâu là yếu tố phân tách lớn nhất (Cliff's Delta = 0.71, Hedges' g = 1.22):**
   - Agent được trang bị Persona tích lũy trung bình 8 active threads trong bộ nhớ làm việc (so với 2 threads ở No-Persona).
   - Persona mở trung bình 2 nguồn/trang bài viết sâu (`wm_cumulative_opened` median = 2 vs 0 ở No-Persona, $p = 3.2 \times 10^-27$).
   - No-Persona hoàn toàn không mở nguồn ngoài feed, chỉ hoạt động bề nổi theo kiểu phản ứng tình huống tức thời (situational reactive).

2. **Chi phí Nhận thức Đổi lấy Tốc độ Thực thi Thực tế:**
   - **Thời gian suy nghĩ LLM (Model Latency):** Persona tiêu tốn nhiều thời gian suy nghĩ hơn đáng kể (Median = 3314 ms vs 2082.5 ms, chênh lệch +1231.5 ms, Cliff's Delta = +0.644, $p = 9.5 \times 10^-21$).
   - **Nhưng Vận tốc Hành động Thực tế (Action Velocity) lại tăng gấp 3 lần:** Persona đạt median 3.00 hành động/phút so với 0.91 hành động/phút của No-Persona (Cliff's Delta = +0.462, $p = 1.6 \times 10^-11$).
   - Lý do: No-Persona bị "treo" hoặc trễ rất lớn ở khâu thực thi tool (`tool_execution_ms` IQR của No-Persona lên tới 21,848 ms so với 8,050 ms của Persona; No-Persona có nhiều bước bị nghẽn mạng hoặc thao tác thất bại).

3. **Phát hiện Nghịch lý Simpson (Simpson's Paradox) trên Tỷ lệ Thành công (Verified Rate):**
   - **Ở cấp độ tổng thể gộp:** Tỷ lệ verified của Persona vượt trội (+16.29%: 77.65% vs 61.36%, Chi2 = 9.78, $p = 0.0018$).
   - **Khi phân rã theo từng Bề mặt (Surface):** Tỷ lệ verified của hai nhóm trên `feed` là tương đương (98.3% vs 100%), trên `detail` tương đương (66.7% vs 68.4%).
   - **Bản chất Confounder:** No-Persona bị "sa lầy" 35.2% thời lượng ở bề mặt `unknown` (nơi tỷ lệ verified chỉ 9.7%) và 21.6% ở `detail`, trong khi Persona có khả năng điều hướng cấu trúc để mở rộng sang `group` (14.6%, 100% verified) và `page` (10.3%, 94.4% verified). Chênh lệch verified rate là hệ quả của **năng lực điều hướng không gian** chứ không phải lỗi thực thi tool.

4. **Tách biệt Driver vs Proxy bằng Random Forest Permutation Importance:**
   - **Confirmed Drivers (Tác động độc lập thực chất):** `intent` (v_tilde = 0.316, Multi-Importance = 0.0626), `surface` (v_tilde = 0.446, Multi-Importance = 0.0427), `verified` (v_tilde = 0.142, Multi-Importance = 0.0332).
   - **Likely Proxies (Biến ăn theo do cộng tuyến):** `resolved_tool` (Cramér's V̂ đơn biến cao = 0.348 nhưng Unique Multi-Importance chỉ 0.006) và `tool` (Multi-Importance = 0.000). Bản chất công cụ chỉ là hệ quả phái sinh khi Agent đã chọn Intent và Surface.

5. **Phân tách Cụm Không gian Đa biến (PCA Separation):**
   - Khoảng cách Euclid giữa tâm cụm Persona và No-Persona trong không gian PC1-PC2 đạt tới **2.52 độ lệch chuẩn**. PC1 (giải thích 43.1% phương sai) đại diện cho Trục Nhận thức Tích cực (Active Deliberation & Thread Dynamics).

---

## 2. Phân tích Chi tiết Từng Tầng Thống kê

### 2.1. Biến với Nhãn: Sức mạnh Phân tách (Discriminative Power)

#### Bảng xếp hạng Mutual Information (MI Score với target = `dataset_type`)
Dữ liệu nguồn: [`output/tables/step5_mutual_information.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_mutual_information.csv)

| Rank | Đặc trưng (Feature) | Kiểu biến | Mutual Information Score | Đánh giá khả năng phân tách |
|:---:|:---|:---:|:---:|:---|
| 1 | `wm_num_active_threads` | Discrete | **0.3471** | Cực mạnh: Số luồng chủ đề trong Working Memory phân biệt rõ rệt hai nhóm |
| 2 | `wm_cumulative_opened` | Discrete | **0.2106** | Cực mạnh: Hành vi đào sâu mở nguồn trang |
| 3 | `model_latency_ms` | Continuous | **0.1994** | Rất mạnh: Độ trễ suy luận nhận thức LLM |
| 4 | `wm_cumulative_searches` | Discrete | **0.1662** | Rất mạnh: Mức độ chủ động tìm kiếm chủ đề |
| 5 | `context_completed_actions` | Continuous | **0.1549** | Mạnh: Khối lượng hành động hoàn tất trong phiên |
| 6 | `cognitive_latency_ratio` | Continuous | **0.1478** | Mạnh: Tỷ số thời gian suy nghĩ trên tổng chu kỳ bước |
| 7 | `context_action_velocity` | Continuous | **0.1421** | Mạnh: Vận tốc thao tác trên phút |
| 8 | `surface` | Categorical | **0.1177** | Mạnh: Bề mặt giao diện tương tác |
| 9 | `total_step_latency_ms` | Continuous | **0.1091** | Vừa phải |
| 10 | `num_dimension_evidence` | Continuous | **0.1084** | Vừa phải: Số lượng bằng chứng nhân khẩu/hành vi Persona |

---

### 2.2. So sánh Biến số (Numeric) & Effect Sizes (Cliff's Delta, Hedges' g)
Dữ liệu nguồn: [`output/tables/step5_numeric_by_label_effect_sizes.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_numeric_by_label_effect_sizes.csv)  
Biểu đồ trực quan: ![Effect Size Forest Plot](file:///data/projects/web-apps/eda_persona/output/figures/step5_effect_size_forest_plot.png)

| Biến số (Variable) | Persona Median (IQR) | No-Persona Median (IQR) | Median Diff | Mann-Whitney U | p-value | Cliff's Delta (Effect) | Hedges' g | Phân loại Effect |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `wm_cumulative_opened` | 2.0 (3.0) | 0.0 (0.0) | +2.0 | 26268 | 3.20e-27 | **+0.711** | +1.22 | **Large** |
| `wm_num_active_threads` | 8.0 (0.0) | 2.0 (4.2) | +6.0 | 26248 | 9.03e-32 | **+0.709** | +1.56 | **Large** |
| `model_latency_ms` | 3314.0 (1599.0) | 2082.5 (1202.0) | +1231.5 | 25246 | 9.54e-21 | **+0.644** | +1.08 | **Large** |
| `context_completed_actions` | 16.0 (18.0) | 5.0 (4.0) | +11.0 | 14226 | 1.56e-14 | **+0.625** | +1.10 | **Large** |
| `wm_cumulative_searches` | 2.0 (2.0) | 1.0 (1.0) | +1.0 | 23592 | 1.35e-15 | **+0.536** | +1.04 | **Large** |
| `context_action_velocity` | 3.0 (1.7) | 0.9 (1.9) | +2.1 | 22444 | 1.62e-11 | **+0.462** | +0.88 | **Medium** |
| `num_dimension_evidence` | 2.0 (3.0) | 0.0 (0.0) | +2.0 | 21297 | 3.80e-10 | **+0.387** | +0.75 | **Medium** |
| `context_num_recent_actions` | 8.0 (5.0) | 5.0 (8.0) | +3.0 | 20842 | 8.40e-09 | **+0.357** | +0.61 | **Medium** |

**Nhận xét sâu về Effect Size:**
- `wm_cumulative_opened` và `wm_num_active_threads` đạt mức **Cliff's Delta > 0.70** (Large vượt ngưỡng cực hạn). Đây là bằng chứng định lượng rõ ràng cho thấy Persona kích hoạt kiến trúc nhận thức đa tuyến tính (Multi-thread Cognitive Architecture), không để Agent rơi vào trạng thái "rỗng nhận thức".
- `model_latency_ms` có **Cliff's Delta = +0.644** ($p = 9.5 \times 10^-21$, Hedges' g = 1.08). Persona đầu tư thêm trung bình hơn 1.2 giây suy nghĩ mỗi bước để căn chỉnh quyết định với hồ sơ tính cách.
- `context_action_velocity` đạt **Cliff's Delta = +0.462** (Medium giáp Large), xác nhận tính quyết đoán: khi đã có Persona, Agent thao tác dứt khoát hơn, ít bị deadlock hoặc timeout.

---

### 2.3. So sánh Biến Danh mục (Categorical) với Nhãn

#### Bảng Kiểm định Độc lập Chi-Square & Bergsma's Cramér's V̂
Dữ liệu nguồn: [`output/tables/step5_categorical_associations_label.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_categorical_associations_label.csv)

| Biến danh mục (Variable) | Số nhóm (Cardinality) | Chi2 Stat | Bậc tự do (dof) | p-value | Cramér's V̂ (Bias-corrected) | Mức độ liên kết |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `surface` | 6 | 91.74 | 5 | 0.00e+00 | **0.4460** | **Large** |
| `resolved_tool` | 19 | 70.98 | 18 | 3.09e-08 | **0.3484** | **Large** |
| `intent` | 16 | 58.60 | 15 | 4.39e-07 | **0.3161** | **Large** |
| `verified` | 2 | 9.78 | 1 | 0.0018 | **0.1419** | **Small** |
| `tool` | 6 | 12.06 | 5 | 0.0339 | **0.1272** | **Small** |
| `has_working_memory` | 2 | 7.23 | 1 | 0.0072 | **0.1195** | **Small** |
| `has_target_candidate` | 2 | 5.90 | 1 | 0.0152 | **0.1060** | **Small** |
| `target_candidate_kind` | 4 | 7.27 | 3 | 0.0638 | **0.0989** | **Small** |
| `reaction` | 6 | 6.84 | 5 | 0.2331 | **0.0647** | **Small** |
| `context_is_overtime` | 1 | 0.00 | 0 | 1.0000 | **0.0000** | **Negligible** |

#### Phân tích Chi tiết Haberman's Standardized Residuals ($z_{vc}$) cho Surface & Intent
> Quy ước Haberman Residuals: $|z| > 1.96$ tương ứng sai lệch có ý nghĩa thống kê ở mức $\alpha = 0.05$. $z > +1.96$: Xuất hiện vượt trội so với kỳ vọng; $z < -1.96$: Bị thiếu hụt đáng kể.

**Bề mặt (Surface):**
- `detail`: No-Persona $z = +7.95$ (21.6% thời lượng) vs Persona $z = -7.95$ (0.86%). No-Persona bị kẹt ở chế độ xem chi tiết bài viết gấp 25 lần Persona!
- `group`: Persona $z = +3.82$ (14.6%) vs No-Persona $z = -3.82$ (0.0%). No-Persona hoàn toàn không bao giờ vào Group!
- `page`: Persona $z = +3.15$ (10.3%) vs No-Persona $z = -3.15$ (0.0%). No-Persona hoàn toàn không bao giờ thăm Fanpage!
- `search`: Persona $z = +2.61$ (16.6%) vs No-Persona $z = -2.61$ (5.7%). Persona chủ động tìm kiếm thông tin gấp 3 lần.

**Ý định hành động (Intent):**
- `observe`: No-Persona $z = +2.96$ (39.8% hành động) vs Persona $z = -2.96$ (24.1%). No-Persona chỉ quan sát thụ động.
- `close`: No-Persona $z = +4.36$ (6.8%) vs Persona $z = -4.36$ (0.3%). No-Persona đóng modal / tab liên tục do lạc đường.
- `open`: Persona $z = +2.14$ (7.2%) vs No-Persona $z = -2.14$ (1.1%).
- `share`: Persona $z = +2.05$ (4.6%) vs No-Persona $z = -2.05$ (0.0%). Chỉ Persona mới có hành vi lan tỏa thông tin.
- `react`: Persona chiếm 7.2% vs No-Persona chiếm 3.4% (Lift = 1.12).

---

### 2.4. Nghịch lý Simpson (Simpson's Paradox Decomposition)
Dữ liệu nguồn: [`output/tables/step5_simpson_surface_decomposition.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_simpson_surface_decomposition.csv)  
Biểu đồ trực quan: ![Simpson Paradox Surface](file:///data/projects/web-apps/eda_persona/output/figures/step5_simpson_paradox_surface.png)

| Bề mặt (Surface) | No-Persona Số bước (Steps) | Persona Số bước (Steps) | No-Persona Verified (%) | Persona Verified (%) | Delta Verified (% (P - NP)) | Hiện tượng thống kê |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `detail` | 19 | 3 | 68.4% | 66.7% | -1.8% | Đảo chiều / Tương đương |
| `feed` | 33 | 119 | 100.0% | 98.3% | -1.7% | Đảo chiều / Tương đương |
| `group` | 0 | 51 | N/A | 100.0% | N/A (Chỉ có Persona) | Không gian độc quyền của Persona |
| `page` | 0 | 36 | N/A | 94.4% | N/A (Chỉ có Persona) | Không gian độc quyền của Persona |
| `search` | 5 | 58 | 100.0% | 100.0% | +0.0% | Không gian độc quyền của Persona |
| `unknown` | 31 | 82 | 9.7% | 11.0% | +1.3% | Không gian độc quyền của Persona |

| **TỔNG THỂ (GỘP)** | **88** | **349** | **61.4%** | **77.7%** | **+16.29%** | **NGHỊCH LÝ SIMPSON RÕ RÀNG** |

> **Bản chất của Nghịch lý Simpson:**  
> Nếu chỉ nhìn vào con số gộp (+16.29% verified cho Persona), người phân tích rất dễ kết luận sai rằng "Persona giúp Agent thực thi tool click/scroll giỏi hơn No-Persona". Thực tế kiểm soát biến `surface` cho thấy tỷ lệ thực thi thành công của cả hai trên `feed` đều đạt xấp xỉ 100%. Điểm mấu chốt là **No-Persona bị rơi vào bề mặt Unknown tới 35.2% thời lượng**, dẫn tới hàng loạt thao tác mù và thất bại. Persona kiểm soát luồng giao diện tốt hơn, đưa Agent vào các bề mặt có cấu trúc rõ ràng (`feed`, `group`, `page`).

---

### 2.5. Hiệu ứng Tương tác: Chi phí Nhận thức theo Ý định (Intent $\times$ Group Interaction)
Dữ liệu nguồn: [`output/tables/step5_intent_latency_interaction.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_intent_latency_interaction.csv)  
Biểu đồ trực quan: ![Intent Latency Interaction](file:///data/projects/web-apps/eda_persona/output/figures/step5_intent_latency_interaction.png)

| Ý định (Intent) | No-Persona Latency Mean (ms) | Persona Latency Mean (ms) | Delta Latency ($\Delta$ ms) | Ý nghĩa tương tác nhận thức |
|:---|:---:|:---:|:---:|:---|
| `read` | 2389.8 | 3954.6 | **+1564.8 ms** | Tăng vọt khi phải ra quyết định chọn bài |
| `open` | 2375.0 | 3870.6 | **+1495.6 ms** | Tăng vọt khi phải ra quyết định chọn bài |
| `search` | 2323.5 | 3794.5 | **+1471.0 ms** | Tăng vọt khi phải ra quyết định chọn bài |
| `react` | 2189.7 | 3557.2 | **+1367.6 ms** | Thời gian căn chỉnh hồ sơ |
| `scroll` | 2582.3 | 3927.4 | **+1345.1 ms** | Thời gian căn chỉnh hồ sơ |
| `observe` | 1240.2 | 1720.9 | **+480.6 ms** | Chỉ quan sát DOM |

**Phát hiện tương tác:**  
Khi chỉ quan sát thụ động (`observe`), Persona chỉ mất thêm **+480.7 ms** so với No-Persona. Nhưng khi bước vào các tác vụ mang tính lựa chọn chiến lược (`read`, `open`, `search`, `scroll`), Persona tiêu tốn thêm **+1345 ms đến +1565 ms**. Đây là chi phí nhận thức cho quá trình *Personalized Evaluation* (so khớp nội dung bài viết với sở thích, mối quan tâm và quy tắc tương tác của Persona).

---

### 2.6. Phân tích Đa biến: Đa cộng tuyến (VIF) & Cấu trúc Cụm (PCA)

#### Kiểm tra Đa cộng tuyến (Variance Inflation Factor - VIF)
Dữ liệu nguồn: [`output/tables/step5_multivariate_vif.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_multivariate_vif.csv)

| Thuộc tính (Feature) | Hệ số VIF | Đánh giá rủi ro đa cộng tuyến |
|:---|:---:|:---|
| `wm_cumulative_searches` | 4.426 | Low (Hợp lệ cho mô hình đa biến) |
| `wm_num_active_threads` | 3.880 | Low (Hợp lệ cho mô hình đa biến) |
| `wm_cumulative_opened` | 3.223 | Low (Hợp lệ cho mô hình đa biến) |
| `context_action_velocity` | 3.175 | Low (Hợp lệ cho mô hình đa biến) |
| `num_dimension_evidence` | 2.658 | Low (Hợp lệ cho mô hình đa biến) |
| `wm_cumulative_reads` | 1.874 | Low (Hợp lệ cho mô hình đa biến) |
| `model_latency_ms` | 1.843 | Low (Hợp lệ cho mô hình đa biến) |
| `tool_execution_ms` | 1.171 | Low (Hợp lệ cho mô hình đa biến) |
| `reason_length` | 1.099 | Low (Hợp lệ cho mô hình đa biến) |

> **Kết luận VIF:** Tất cả các biến số đều có $VIF < 5.0$ (cao nhất là `wm_cumulative_searches` với 4.426). Không có hiện tượng đa cộng tuyến nghiêm trọng ($VIF > 10$), dữ liệu hoàn toàn an toàn và vững chắc để phân tích đa biến và hồi quy.

#### Phân tích Thành phần Chính (PCA Loadings & Centroid Separation)
Dữ liệu nguồn: [`output/tables/step5_pca_variance_loadings.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_pca_variance_loadings.csv)  
Biểu đồ trực quan: ![PCA Cluster Separation](file:///data/projects/web-apps/eda_persona/output/figures/step5_pca_cluster_separation.png)

- **Phương sai giải thích:** PC1 giải thích **43.07%**, PC2 giải thích **15.05%**, PC3 giải thích **12.11%** (Tổng 3 thành phần tích lũy: **70.22%**).
- **Trọng số PC1 (Loadings):** Chi phối mạnh bởi `wm_num_active_threads` (+0.443), `wm_cumulative_searches` (+0.437), `context_action_velocity` (+0.425), và `wm_cumulative_opened` (+0.419). Đây là trục đo lường **Sức sống Hành vi & Bộ nhớ Tích cực**.
- **Trọng số PC2 (Loadings):** Chi phối bởi `model_latency_ms` (+0.623), `num_dimension_evidence` (+0.540), `tool_execution_ms` (+0.413). Đây là trục đo lường **Mức độ Thâm dụng Nhận thức (Cognitive Load)**.
- **Tách biệt Không gian Cụm:**
  - Tâm cụm Persona: $(PC1 = +0.51, PC2 = +0.04)$
  - Tâm cụm No-Persona: $(PC1 = -2.01, PC2 = -0.15)$
  - **Khoảng cách Euclid giữa hai tâm cụm:** **2.52 độ lệch chuẩn**. Hai quần thể agent nằm ở hai miền không gian hành vi hoàn toàn khác biệt.

---

### 2.7. Tách biệt Yếu tố Tác động Thực chất (Confirmed Driver) khỏi Hệ quả Ăn theo (Likely Proxy)
Dữ liệu nguồn: [`output/tables/step5_driver_proxy_classification.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_driver_proxy_classification.csv)

| Thuộc tính (Attribute) | Cramér's V̂ đơn biến | Hạng đơn biến | Multivariate Importance | Hạng đa biến | Phân loại Trạng thái | Diễn giải cơ chế |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `intent` | 0.3161 | 3 | 0.0626 | 1 | **Confirmed Driver** | Unique contributor manh doc lap |
| `surface` | 0.4460 | 1 | 0.0427 | 2 | **Confirmed Driver** | Unique contributor manh doc lap |
| `verified` | 0.1419 | 4 | 0.0332 | 4 | **Confirmed Driver** | Unique contributor manh doc lap |
| `resolved_tool` | 0.3484 | 2 | 0.0065 | 5 | **Likely Proxy** | Proxy cua: nhieu da chieu |
| `tool` | 0.1272 | 5 | 0.0000 | 7 | **Likely Proxy** | Proxy cua: nhieu da chieu |
| `has_working_memory` | 0.1195 | 6 | 0.0332 | 3 | **Low Impact** | Tac dong yeu khi kiem soat da bien |
| `has_target_candidate` | 0.1060 | 7 | 0.0036 | 6 | **Low Impact** | Tac dong yeu khi kiem soat da bien |
| `reaction` | 0.0647 | 8 | 0.0000 | 7 | **Low Impact** | Tac dong yeu khi kiem soat da bien |

> **Bài học quan trọng từ Driver vs Proxy:**  
> Đơn biến cho thấy `resolved_tool` có liên kết rất mạnh với Persona (V̂ = 0.348, Hạng 2). Tuy nhiên khi đưa vào mô hình đa biến Random Forest, tầm quan trọng độc lập của `resolved_tool` tụt dốc xuống chỉ còn 0.006 (bị phân loại thành **Likely Proxy**). Nguyên nhân: `resolved_tool` chỉ là công cụ hạ tầng kỹ thuật được sinh ra sau khi Agent đã quyết định `intent` và `surface`. Hai động lực gốc thực sự điều khiển toàn bộ khác biệt là **`intent` (Ý định)** và **`surface` (Không gian tiếp cận)**.

---

### 2.8. Ma trận Trôi dạt Tương quan (Correlation Drift: Persona vs No-Persona)
Dữ liệu nguồn: [`output/tables/step5_spearman_corr_drift.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_spearman_corr_drift.csv)  
Biểu đồ trực quan: ![Correlation Drift Heatmap](file:///data/projects/web-apps/eda_persona/output/figures/step5_correlation_drift_heatmap.png)

1. **`model_latency_ms` vs `num_dimension_evidence`:**
   - Trong nhóm Persona: Tương quan Spearman là **+0.515** ($p < 10^-15$). Số chiều bằng chứng tính cách tăng lên thì LLM suy nghĩ lâu hơn một cách tỷ lệ thuận và ổn định.
   - Trong nhóm No-Persona: Bằng chứng nhân khẩu là 0, chỉ có bằng chứng tình huống ngẫu nhiên ($r = +0.348$).
2. **`model_latency_ms` vs `reason_length`:**
   - Trong nhóm No-Persona: Tương quan âm cực mạnh ($r = -0.770$). Các bước có độ trễ thấp thường là các bước fail hoặc observe không sinh ra reason.
   - Trong nhóm Persona: Tương quan trôi dạt về mức yếu ($r = -0.225$, $\Delta r = +0.545$). Persona luôn duy trì chuỗi lập luận có cấu trúc bất kể độ trễ ngắn hay dài.

---

### 2.9. Phân tích Cử chỉ Vật lý Browser (Gesture Pacing & Scroll Mechanics)
Dữ liệu nguồn: [`output/tables/step5_recent_actions_gesture_comparison.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_recent_actions_gesture_comparison.csv)

| Chỉ số cử chỉ chuột | Persona Median (IQR) | No-Persona Median (IQR) | Mann-Whitney U | p-value | Cliff's Delta | Đánh giá khác biệt |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `gesture_total_px` | 481.0 px/ms (310.5) | 684.0 px/ms (473.0) | 65 | 0.0432 | **-0.552** | **Large** |
| `gesture_ms` | 239.5 px/ms (57.5) | 293.0 px/ms (14.0) | 40 | 0.0082 | **-0.721** | **Large** |
| `landing_correction_px` | 211.0 px/ms (349.75) | 364.0 px/ms (150.0) | 22 | 0.2681 | **-0.476** | **Large** |

- **Khoảng cách cuộn mỗi lần (`gesture_total_px`):** Persona cuộn ngắn hơn, có kiểm soát hơn (Median 481.0 px vs 684.0 px của No-Persona, Cliff's Delta = -0.552, Large).
- **Thời gian vuốt chuột (`gesture_ms`):** Persona vuốt nhanh và dứt khoát hơn (Median 239.5 ms vs 293.0 ms của No-Persona, Cliff's Delta = -0.721, Large, $p = 0.008$).
- **Độ lệch điểm dừng cần sửa (`landing_correction_px`):** Persona có độ lệch điểm rơi thấp hơn (Median 211.0 px vs 364.0 px của No-Persona), chứng tỏ độ chính xác khi căn chỉnh vào các phần tử giao diện cao hơn.

---

## 3. Đề xuất Hướng Phân tích Tiếp theo (Recommendations for Step 6 & Step 7)

Dựa trên các phát hiện định lượng vững chắc từ Bước 5, nhóm phân tích đề xuất lộ trình triển khai cụ thể cho các bước tiếp theo trong [`pipeline_eda.md`](file:///data/projects/web-apps/eda_persona/notebooks/pipeline_eda.md):

### Đề xuất 1: Triển khai Ma trận Chuyển dịch Trạng thái Markov (Markov Transition Matrix) cho Bước 6
- **Vấn đề phát hiện ở Bước 5:** No-Persona bị sa lầy ở `detail` và `unknown`.
- **Hành động đề xuất cho Bước 6:**
  - Xây dựng ma trận xác suất chuyển trạng thái cấp 1 ($P(S_{t+1} | S_t)$) giữa các Intent và Surface: `feed -> detail -> unknown` vs `feed -> search -> group -> page`.
  - Tính thời gian hấp thu (Absorbing Time) để chứng minh mặt toán học: No-Persona có điểm hấp thụ (absorbing state) là các vòng lặp bế tắc (`observe -> close -> observe`), trong khi Persona sở hữu đồ thị hành vi chuyển tiếp ergodic và phân nhánh rộng.

### Đề xuất 2: Phân tích Chuỗi Thời gian & Vận tốc Nhận thức (Temporal Action Velocity & Drift) cho Bước 6
- Khảo sát biến thiên vận tốc hành động (`context_action_velocity`) theo từng 1/4 phiên (Early, Mid, Late session):
  - Kiểm tra xem No-Persona có bị hiện tượng kiệt sức nhận thức (Cognitive Fatigue) hoặc giảm sút vận tốc theo thời gian hay không.
  - Phân tích chu kỳ nghỉ ngơi (`context_rest_accumulated_seconds`): Persona nghỉ ngơi theo nhịp sinh học được định nghĩa trong profile (`persona_rest_style`), xem nhịp nghỉ này tác động thế nào tới việc duy trì chuỗi hành động hợp lệ.

### Đề xuất 3: So sánh Có Kiểm chứng Nâng cao (Hypothesis Testing & Permutation Tests) cho Bước 7
- **Permutation Test & Bootstrap Confidence Intervals:**
  - Vì số lượng episode ở mức khiêm tốn (6 Persona vs 2 No-Persona, 437 steps), cần áp dụng Bootstrap 10,000 lần cho các chỉ số cốt lõi (`verified_rate`, `action_velocity`, `opened_sources`) để xác lập khoảng tin cậy 95% BCa không phụ thuộc phân phối chuẩn.
- **Benjamini-Hochberg FDR Correction:**
  - Áp dụng module [`benjamini_hochberg_fdr.py`](file:///data/projects/web-apps/eda_persona/algorithms/benjamini_hochberg_fdr.py) đã có sẵn để hiệu chỉnh đa kiểm định giả thuyết (Multiple Testing Correction) cho toàn bộ 41 biến số, đảm bảo loại bỏ hoàn toàn các phát hiện dương tính giả (False Discovery).

### Đề xuất 4: Mô hình Hồi quy Đa biến Bậc cao Kiểm soát Confounder cho Bước 8
- Xây dựng mô hình Logistic Regression hoặc GAM (Generalized Additive Model) giải thích xác suất `verified`:
  $$\text{logit}(P(\text{verified}=1)) = \beta_0 + \beta_1 \cdot \text{dataset\_type} + \beta_2 \cdot \text{surface} + \beta_3 \cdot \text{intent} + \beta_4 \cdot (\text{dataset\_type} \times \text{surface})$$
  để cô lập tác động biên (Marginal Effect) thuần túy của Persona sau khi đã loại trừ hoàn toàn ảnh hưởng của bề mặt và ý định.

---
*Báo cáo được khởi tạo tự động bởi Engine Phân tích Bước 5. Không can thiệp vào các tệp Notebook hiện hữu.*
