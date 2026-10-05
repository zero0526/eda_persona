import pandas as pd
from pathlib import Path

project_root = Path('.')
table_path = project_root / "output" / "tables" / "step5_signature_behaviors_by_phase.csv"

data = [
    {
        "Giai đoạn": "Q1 (0-25% Early)",
        "Đối tượng": "Có Persona",
        "Hành vi Đặc trưng": "Tìm kiếm chủ đề & Điều hướng (Search & Navigate)",
        "Tỷ trọng (%)": "38.4% (Search: 27.9%, Nav: 10.5%)",
        "Chỉ số Vượt trội (Lift / z-score)": "Lift = 2.03x (z = +4.39, p < 0.0001)",
        "Bản chất Nhận thức & Ý nghĩa Thực nghiệm": "Chủ động 'săn tìm' nguồn bài viết, nạp các luồng chủ đề quan tâm vào Working Memory."
    },
    {
        "Giai đoạn": "Q1 (0-25% Early)",
        "Đối tượng": "Không Persona",
        "Hành vi Đặc trưng": "Cuộn lướt feed bề nổi (Scroll Feed)",
        "Tỷ trọng (%)": "28.6% (kèm Observe: 33.3%)",
        "Chỉ số Vượt trội (Lift / z-score)": "Lift = 1.93x (z = +2.04, p = 0.041)",
        "Bản chất Nhận thức & Ý nghĩa Thực nghiệm": "Lướt ngẫu nhiên bề nổi feed, thụ động do thiếu hồ sơ mục tiêu dẫn dắt ban đầu."
    },
    {
        "Giai đoạn": "Q2 (25-50% Mid-Early)",
        "Đối tượng": "Có Persona",
        "Hành vi Đặc trưng": "Đọc sâu bài viết (Deep Read)",
        "Tỷ trọng (%)": "13.8% (Đạt đỉnh cao nhất phiên)",
        "Chỉ số Vượt trội (Lift / z-score)": "Lift = 1.72x (z = +2.29, p = 0.022)",
        "Bản chất Nhận thức & Ý nghĩa Thực nghiệm": "Dành phần lớn nỗ lực để đọc sâu nội dung các bài viết tìm thấy từ Q1, chuyển hóa thông tin."
    },
    {
        "Giai đoạn": "Q2 (25-50% Mid-Early)",
        "Đối tượng": "Không Persona",
        "Hành vi Đặc trưng": "Quan sát màn hình thụ động (Observe)",
        "Tỷ trọng (%)": "40.9% (Chiếm đa số thời lượng)",
        "Chỉ số Vượt trội (Lift / z-score)": "Lift = 1.03x (z = +0.13, Không đặc trưng)",
        "Bản chất Nhận thức & Ý nghĩa Thực nghiệm": "Không có luồng đọc có chủ đích; thời gian chết nhìn màn hình bắt đầu phình to."
    },
    {
        "Giai đoạn": "Q3 (50-75% Mid-Late)",
        "Đối tượng": "Có Persona",
        "Hành vi Đặc trưng": "Tương tác xã hội (React, Like, Share)",
        "Tỷ trọng (%)": "14.9% (Tăng lũy tiến)",
        "Chỉ số Vượt trội (Lift / z-score)": "Lift = 1.24x (z = +0.96)",
        "Bản chất Nhận thức & Ý nghĩa Thực nghiệm": "Nội dung được thẩm thấu -> bộc lộ cảm xúc, like, react, share phù hợp với sở thích cá nhân."
    },
    {
        "Giai đoạn": "Q3 (50-75% Mid-Late)",
        "Đối tượng": "Không Persona",
        "Hành vi Đặc trưng": "Kẹt trong Modal bài viết (Deep Read thụ động)",
        "Tỷ trọng (%)": "27.3% (Tăng giả tạo)",
        "Chỉ số Vượt trội (Lift / z-score)": "Lift = 1.85x (z = +1.91, p = 0.056)",
        "Bản chất Nhận thức & Ý nghĩa Thực nghiệm": "Thời gian đọc tăng giả tạo do kẹt trong modal chi tiết, cố đóng nhưng không thành công."
    },
    {
        "Giai đoạn": "Q4 (75-100% Late)",
        "Đối tượng": "Có Persona",
        "Hành vi Đặc trưng": "Chủ động Kết thúc phiên (End Session)",
        "Tỷ trọng (%)": "22.5% (Search giảm về 0.0%)",
        "Chỉ số Vượt trội (Lift / z-score)": "Lift = 3.27x (z = +6.74, p = 1.6e-11)",
        "Bản chất Nhận thức & Ý nghĩa Thực nghiệm": "Đặc trưng áp đảo: Agent tự chủ gọi lệnh thoát phiên khi đã thỏa mãn mục tiêu khám phá."
    },
    {
        "Giai đoạn": "Q4 (75-100% Late)",
        "Đối tượng": "Không Persona",
        "Hành vi Đặc trưng": "Nghỉ ngơi buông xuôi (Rest / Passive Idling)",
        "Tỷ trọng (%)": "8.7% Rest (kèm 39.1% Observe)",
        "Chỉ số Vượt trội (Lift / z-score)": "Lift = 3.83x (z = +2.40, p = 0.016)",
        "Bản chất Nhận thức & Ý nghĩa Thực nghiệm": "'Chán chường buông xuôi, không làm gì chỉ nằm đợi hết giờ' sau chuỗi lỗi giao diện liên tiếp."
    }
]

df_sig = pd.DataFrame(data)
df_sig.to_csv(table_path, index=False, encoding="utf-8-sig")
print("Saved step5_signature_behaviors_by_phase.csv successfully!")
