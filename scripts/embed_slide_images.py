import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

md_path = Path('notebooks/slide_scheduler.md')
with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace unfinished mermaid transition
content = content.replace('CH3 -->|"Các giải thiết có "| S15', 'CH3 -->|"Cầu nối 3: Cả 3 giả thuyết đều được chứng minh, mang lại giá trị gì cho thực tế?"| S15')
content = content.replace('CH3 -->|"Các giải thiết có"| S15', 'CH3 -->|"Cầu nối 3: Cả 3 giả thuyết đều được chứng minh, mang lại giá trị gì cho thực tế?"| S15')

# Slide 1 image
content = content.replace(
    '* **Hình ảnh trên slide:** Giao diện Facebook trên điện thoại kèm hình minh họa 6 nhân vật đại diện cho các ngành nghề đời thường tại Việt Nam.',
    '* **Hình ảnh trên slide:**  \n  ![Chu trình vận hành của AI Agent trên Facebook](file:///d:/source_code/eda_persona/output/figures/agent_loop.png)'
)

# Slide 4 image
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ hình tròn hoặc biểu đồ cột phân bổ tỷ lệ 4 khung giờ trong ngày.',
    '* **Hình ảnh trên slide:**  \n  ![Bức tranh 4 khung giờ hoạt động và kiểm định Chi-Square](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/notebook_action_logs_9_6.png)'
)

# Slide 5 image
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ nhiệt (Heatmap) thể hiện tỷ lệ % lượt vào mạng theo từng ca của 6 nhân vật.',
    '* **Hình ảnh trên slide:**  \n  ![Heatmap phần dư chuẩn hóa ca làm việc theo nghề nghiệp](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/notebook_action_logs_9_6.png)'
)

# Slide 6 image
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ thanh so sánh số phút trung bình của 6 nhân vật kèm hộp chốt hạ màu xanh: "H1 ĐÃ ĐƯỢC CHỨNG MINH".',
    '* **Hình ảnh trên slide:**  \n  ![Phân phối 4 biến thời gian và thời lượng phiên](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/notebook_action_logs_7_0.png)'
)

# Slide 7 image
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ đối chiếu 3 chiều: Số phút dùng ➔ Số thao tác ➔ Quãng đường cuộn của từng nhân vật.',
    '* **Hình ảnh trên slide:**  \n  ![Chỉ số vĩ mô cấp phiên: thời lượng, cự ly cuộn và xác minh DOM](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/notebook_action_logs_12_3.png)'
)

# Slide 8 image
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ cột 100% xếp chồng thể hiện tỷ lệ % thời gian dành cho Bảng tin, Reels, Hội nhóm và Đọc bài viết.',
    '* **Hình ảnh trên slide:**  \n  ![Phân bố không gian bề mặt giao diện 100% Stacked](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/notebook_action_logs_14_6.png)'
)

# Slide 9 image
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ so sánh tỷ lệ AER của 6 nhân vật kèm trích dẫn các từ khóa tìm kiếm thực tế.',
    '* **Hình ảnh trên slide:**  \n  ![Tỷ lệ tương tác chủ động AER và tìm kiếm](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/notebook_action_logs_14_6.png)'
)

# Slide 10 image
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ cột so sánh vận tốc cuộn chuột (pixel/giây) phân hóa theo từng nhân vật.',
    '* **Hình ảnh trên slide:**  \n  ![Đo lường cơ học cử chỉ vật lý: Vận tốc cuộn px/s và Chế độ nhịp](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/notebook_action_logs_16_2.png)'
)

# Slide 11 image
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ phân bổ các chiều bản sắc cốt lõi kèm hộp chốt hạ màu xanh: "H2 ĐÃ ĐƯỢC CHỨNG MINH".',
    '* **Hình ảnh trên slide:**  \n  ![Ma trận bản sắc chi phối và tương quan nhận thức](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/notebook_action_logs_18_6.png)'
)

# Slide 12 image
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ so sánh độ tương đồng: Cùng một người ($70.2\\%) vượt trội rõ rệt so với giữa hai người khác nhau ($43.4\\%).',
    '* **Hình ảnh trên slide:**  \n  ![Độ tương đồng hành vi đa phiên và tỷ lệ duy trì thói quen cũ](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/slide12_behavior_consistency_multilevel.png)'
)
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ so sánh độ tương đồng: Cùng một người ($70.2%) vượt trội rõ rệt so với giữa hai người khác nhau ($43.4%).',
    '* **Hình ảnh trên slide:**  \n  ![Độ tương đồng hành vi đa phiên và tỷ lệ duy trì thói quen cũ](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/slide12_behavior_consistency_multilevel.png)'
)

# Slide 13 image
content = content.replace(
    '* **Hình ảnh trên slide:** Bảng thống kê các trang và hội nhóm có tần suất xuất hiện lặp lại qua các phiên kèm biểu tượng nhóm.',
    '* **Hình ảnh trên slide:**  \n  ![Bằng chứng trí nhớ fanpage và hội nhóm xuyên phiên](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/slide13_cross_session_entities.png)'
)

# Slide 14 image
content = content.replace(
    '* **Hình ảnh trên slide:** Biểu đồ đối chiếu điểm thương hiệu và độ độc quyền của 6 chuỗi hành vi kèm hộp chốt hạ màu xanh: "H3 ĐÃ ĐƯỢC CHỨNG MINH".',
    '* **Hình ảnh trên slide:**  \n  ![Top 1 chuỗi hành vi thương hiệu đặc trưng đa phiên](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/notebook_action_logs_24_5.png)'
)

# Slide 15 image
content = content.replace(
    '* **Hình ảnh trên slide:** Bảng checklist hoàn thành 3 Giả thuyết ($H_1, H_2, H_3$) kèm lộ trình phát triển hệ thống và lời cảm ơn.',
    '* **Hình ảnh trên slide:**  \n  ![Bảng chỉ số tuân thủ hợp đồng và bản sắc](file:///d:/source_code/eda_persona/output/figures/step5_persona_adherence_metrics.png)'
)

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated slide_scheduler.md with all image links successfully!')
