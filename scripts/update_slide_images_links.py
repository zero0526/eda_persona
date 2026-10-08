import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

md_path = Path('notebooks/slide_scheduler.md')
with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Slide 4
    if 'notebook_action_logs_files/notebook_action_logs_9_6.png' in line and i < 150:
        new_lines.append('  ![Bức tranh 4 khung giờ hoạt động trong ngày và mật độ 24 giờ](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/slide4_four_shifts_distribution.png)\n')
    # Slide 5
    elif 'notebook_action_logs_files/notebook_action_logs_9_6.png' in line and i >= 150:
        new_lines.append('  ![Giờ cao điểm và vắng bóng theo nghề nghiệp](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/slide5_shift_by_profession.png)\n')
    # Slide 6
    elif 'notebook_action_logs_files/notebook_action_logs_7_0.png' in line:
        new_lines.append('  ![Thời lượng trung bình mỗi lần vào mạng và tần suất ngày](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/slide6_duration_and_frequency.png)\n')
    # Slide 8
    elif 'notebook_action_logs_files/notebook_action_logs_14_6.png' in line and i < 230:
        new_lines.append('  ![Địa bàn hoạt động: Phân bố bề mặt giao diện 100% Stacked](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/slide8_surface_distribution.png)\n')
    # Slide 9
    elif 'notebook_action_logs_files/notebook_action_logs_14_6.png' in line and i >= 230:
        new_lines.append('  ![Tỷ lệ tương tác chủ động AER và bảng tìm kiếm chủ động](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/slide9_aer_and_search_intent.png)\n')
    # Slide 12
    elif '* **Hình ảnh trên slide:** Biểu đồ so sánh độ tương đồng:' in line:
        new_lines.append('* **Hình ảnh trên slide:**  \n  ![Độ tương đồng hành vi đa phiên và tỷ lệ duy trì thói quen cũ](file:///d:/source_code/eda_persona/notebooks/notebook_action_logs_files/slide12_behavior_consistency_multilevel.png)\n')
    else:
        new_lines.append(line)

with open(md_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Đã cập nhật liên kết ảnh toàn bộ Slide 4 đến Slide 14 thành công!")
