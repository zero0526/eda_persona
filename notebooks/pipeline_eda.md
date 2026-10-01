# Một EDA tốt: các bước chính và việc cần làm

Mục tiêu của EDA là **hiểu dữ liệu đủ sâu để ra quyết định đúng** (chọn metric, chọn mô hình, phát hiện lỗi, đặt giả thuyết), không phải vẽ thật nhiều biểu đồ. Quy trình dưới đây đi theo thứ tự.

## Bước 1. Xác định mục tiêu và câu hỏi
**Việc cần làm:**
- Viết 3-5 câu hỏi cụ thể mà EDA phải trả lời. Ví dụ: "Hành vi của agent khác người thật ở điểm nào?", "Biến nào ảnh hưởng nhất đến nhãn?".
- Ghi giả thuyết kỳ vọng trước khi nhìn dữ liệu, để sau này biết mình có bị confirmation bias không.
- Xác định người đọc (đồng nghiệp kỹ thuật, quản lý, hội đồng) để chọn mức độ chi tiết.

**Đầu ra:** danh sách câu hỏi và giả thuyết.

## Bước 2. Hiểu bối cảnh và nguồn gốc dữ liệu
**Việc cần làm:**
- Ai/cái gì sinh ra dữ liệu, thu thập bằng cách nào, trong khoảng thời gian nào, phiên bản nào.
- Xác định **đơn vị phân tích** (một dòng = một sự kiện, một phiên hay một user?). Sai bước này thì mọi thống kê sau đều lệch.
- Lập **data dictionary**: tên cột, ý nghĩa, kiểu dữ liệu, đơn vị đo, miền giá trị hợp lệ, cột nào là khóa, nhãn, biến điều kiện.
- Ghi lại các quy trình xử lý trước đó (lọc, gộp, làm sạch) vì chúng có thể đã tạo bias.

**Đầu ra:** bảng mô tả schema và sơ đồ nguồn dữ liệu.

## Bước 3. Kiểm tra tổng quan và chất lượng dữ liệu
**Việc cần làm:**
- Kích thước (số dòng, số cột), kiểu dữ liệu thực tế so với kiểu kỳ vọng, dung lượng.
- **Missing:** tỉ lệ theo cột, và quan trọng hơn là *missing có ngẫu nhiên không* (MCAR/MAR/MNAR). Missing theo nhóm hoặc theo thời gian thường mang ý nghĩa.
- **Trùng lặp:** dòng trùng hoàn toàn, trùng khóa.
- **Giá trị bất hợp lệ:** số âm ở chỗ không thể âm, timestamp tương lai, category viết sai chính tả, giá trị placeholder (-1, 999, "N/A", chuỗi rỗng).
- **Nhất quán:** cùng một thực thể có biểu diễn khác nhau không, khóa ngoại có khớp không.
- **Outlier:** phát hiện bằng IQR, z-score hoặc phân vị, rồi *kiểm tra xem là lỗi hay là tín hiệu thật* trước khi xử lý.
- **Thời gian:** có khoảng trống, thay đổi cách ghi log, múi giờ lệch không.

**Đầu ra:** báo cáo chất lượng dữ liệu và danh sách quyết định xử lý (bỏ, sửa, giữ, đánh dấu), mỗi quyết định có lý do.

## Bước 4. Phân tích đơn biến (univariate)
**Việc cần làm:**
- **Numeric:** mean, median, std, min/max, phân vị (p1, p5, p25, p75, p95, p99), skewness, kurtosis. Vẽ histogram, KDE, boxplot, ECDF. Dữ liệu đuôi dài thì dùng log-scale.
- **Categorical:** tần suất, tỉ lệ, số category duy nhất (cardinality), long tail của category hiếm.
- **Thời gian:** số bản ghi theo giờ/ngày/tuần, xu hướng, tính mùa vụ.
- **Text:** độ dài, từ phổ biến, ngôn ngữ, ký tự lạ.
- Với biến nhãn (target): phân phối, mức độ mất cân bằng lớp.

**Đầu ra:** hồ sơ từng biến và nhận xét ngắn (phân phối dạng gì, có gì bất thường, cần biến đổi không).

## Bước 5. Phân tích hai biến và đa biến
**Việc cần làm:**
- **Numeric với numeric:** scatter plot, hệ số tương quan Pearson/Spearman, hexbin khi dữ liệu lớn.
- **Categorical với numeric:** boxplot/violin theo nhóm, so sánh median và phân vị.
- **Categorical với categorical:** bảng chéo (crosstab), chi-square, Cramér's V, heatmap tỉ lệ.
- **Biến với nhãn:** biến nào phân tách nhãn tốt (mutual information, so sánh phân phối theo lớp).
- **Đa biến:** ma trận tương quan, kiểm tra đa cộng tuyến, PCA/UMAP để xem cấu trúc cụm.
- **Tương tác:** hiệu ứng của biến A có đổi theo biến B không.

**Đầu ra:** các quan hệ đáng chú ý, kèm mức độ mạnh (effect size), không chỉ nêu "có tương quan".

## Bước 6. Phân tích theo nhóm/thời gian/chuỗi (nếu dữ liệu có cấu trúc)
**Việc cần làm:**
- **Phân tầng (slice)** theo các thuộc tính quan trọng và xem hiện tượng có đồng nhất giữa các nhóm không.
- **Dữ liệu theo chuỗi/hành vi:** phân phối hành động, transition matrix, n-gram, thời gian giữa các sự kiện, độ dài phiên.
- **Dữ liệu theo thời gian:** xu hướng, mùa vụ, điểm gãy (change point), drift.
- **Dữ liệu theo user/thực thể:** phân phối hoạt động mỗi đơn vị (thường rất lệch), nhóm user hoạt động nhiều và ít.

**Đầu ra:** hiểu được khác biệt đến từ nhóm nào, giai đoạn nào.

## Bước 7. So sánh có kiểm chứng (khi mục tiêu là so sánh)
**Việc cần làm:**
- Đặt hai nhóm trên cùng trục, cùng thang đo, **chuẩn hóa** khi volume khác nhau.
- Đo khoảng cách phân phối (JS divergence, Wasserstein, KS) và **effect size kèm khoảng tin cậy** (bootstrap).
- Dùng kiểm định phù hợp (t-test, Mann-Whitney, chi-square, permutation test) và hiệu chỉnh multiple comparisons.
- Lưu ý n lớn thì p-value gần như luôn nhỏ, nên hãy nhìn độ lớn khác biệt.

**Đầu ra:** bảng so sánh có số liệu, CI và nhận xét mức độ khác biệt.

## Bước 8. Tìm nguyên nhân và kiểm tra confounder
**Việc cần làm:**
- Với mỗi khác biệt phát hiện được, đưa ra giải thích khả dĩ và **một phép kiểm chứng có thể bác bỏ nó**.
- Kiểm tra **Simpson's paradox**: tách nhóm xem kết luận tổng thể có đảo chiều không.
- Kiểm tra confounder (biến cùng ảnh hưởng đến cả hai phía), selection bias, survivorship bias, data leakage.
- Dùng hồi quy hoặc cây quyết định đơn giản để xem biến nào giải thích được phần lớn khác biệt.
- Chỉ nói "phù hợp với giả thuyết" khi không có thí nghiệm can thiệp.

**Đầu ra:** các giải thích được xếp theo mức độ bằng chứng.

## Bước 9. Kiểm tra độ vững (robustness)
**Việc cần làm:**
- Lặp lại phân tích với subsample, seed khác, bỏ outlier, đổi định nghĩa metric, đổi ngưỡng.
- Nếu dữ liệu do LLM hoặc simulator sinh ra, đo **phương sai giữa các lần chạy** trước khi diễn giải sự khác biệt giữa các nhóm.
- Kiểm tra kết quả có phụ thuộc vào một vài đơn vị chiếm đa số dữ liệu không.

**Đầu ra:** kết luận nào vững, kết luận nào nhạy với lựa chọn phân tích.

## Bước 10. Xem mẫu cụ thể (qualitative inspection)
**Việc cần làm:**
- Đọc trực tiếp 20-50 mẫu: mẫu điển hình, mẫu ngoại lai, mẫu gần ranh giới giữa các nhóm.
- Đối chiếu với số liệu: mẫu có khớp với bức tranh thống kê không?
- Ghi lại các lỗi hệ thống (pattern lặp, template, artifact của pipeline).

**Đầu ra:** ví dụ minh họa và phát hiện mà thống kê tổng hợp bỏ sót.

## Bước 11. Hạn chế và rủi ro kết luận
**Việc cần làm:**
- **Construct validity:** metric có đo đúng khái niệm không?
- **External validity:** kết quả khái quát được ra ngoài tập này không?
- Liệt kê những gì không đo được, không kiểm soát được, giả định đã dùng.

## Bước 12. Tổng hợp và đề xuất hành động
**Việc cần làm:**
- 3-5 phát hiện chính, mỗi cái kèm mức độ chắc chắn.
- Hệ quả: cần làm sạch thêm gì, feature nào nên tạo, mô hình nào phù hợp, cần thu thêm dữ liệu nào.
- Câu hỏi mở và thí nghiệm tiếp theo.
- Đảm bảo **tái lập được**: lưu code, seed, phiên bản dữ liệu, môi trường.

## Nguyên tắc xuyên suốt

| Nguyên tắc | Ý nghĩa |
|---|---|
| Câu hỏi → bằng chứng → diễn giải → độ tin cậy | Mỗi biểu đồ phải trả lời một câu hỏi cụ thể |
| Một takeaway cho mỗi biểu đồ | Người đọc không phải tự đoán ý nghĩa |
| Ghi lại mọi quyết định xử lý dữ liệu | Để người khác kiểm tra và tái lập |
| Ưu tiên tỉ lệ và phân phối hơn con số tuyệt đối | Tránh bị đánh lừa bởi volume |
| Nghi ngờ kết quả quá đẹp | Thường là dấu hiệu của leakage hoặc lỗi dữ liệu |
| Tách phần khám phá và phần kết luận | Thứ bạn tìm thấy khi lọc nhiều lần cần được kiểm chứng lại |

## Lỗi thường gặp
- Nhảy vào vẽ biểu đồ khi chưa rõ đơn vị phân tích.
- Chỉ nhìn mean, bỏ qua phân phối và đuôi.
- Kết luận nhân quả từ tương quan.
- Báo cáo p-value mà không có effect size.
- So sánh số đếm tuyệt đối giữa các nhóm có kích thước khác nhau.
- Quên kiểm tra xem khác biệt có đến từ cách thu thập chứ không phải từ hành vi thật.
- Notebook là một chuỗi biểu đồ không có narrative.

Nếu bạn cho mình biết loại dữ liệu cụ thể (log hành vi, bảng tabular, text, chuỗi thời gian) và mục tiêu so sánh, mình có thể chuyển khung này thành checklist metric và biểu đồ cụ thể cho từng bước.