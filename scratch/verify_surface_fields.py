import sys, os
sys.path.append(os.path.abspath('.'))
import json, sqlite3, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
df_bots = conn.execute('SELECT b.persona_id, pv.content_json FROM bots b JOIN persona_versions pv ON pv.bot_id = b.id').fetchall()
personas_dict = {p_id: json.loads(p_json) if p_json else {} for p_id, p_json in df_bots}

p_ids = sorted(personas_dict.keys())
first_attrs = personas_dict[p_ids[0]].get('attributes', {})

# Mapping between English Dimension concepts and exact Vietnamese field names
surface_drivers = {
    'Reels (Video ngắn)': [
        'Loại hình nội dung yêu thích nhất',
        'Tổng thời gian xem phim, video và livestream hàng tuần.',
        'Tần suất sử dụng TikTok',
        'Tần suất sử dụng YouTube',
        'Nhóm thế hệ dựa trên thời kỳ họ sinh ra, thường được dùng để mô tả những trải nghiệm xã hội và công nghệ chung.',
        'Độ dài thời gian duy trì sự chú ý sâu vào một việc.',
        'Thói quen thưởng thức âm nhạc trong sinh hoạt.'
    ],
    'Group (Hội nhóm cộng đồng)': [
        'Mức độ sinh hoạt trong các hội nhóm và cộng đồng mạng xã hội.',
        'Nhóm tuổi',
        'Nhóm thế hệ dựa trên thời kỳ họ sinh ra, thường được dùng để mô tả những trải nghiệm xã hội và công nghệ chung.',
        'Xu hướng nhìn nhận bức tranh toàn cảnh hay đi sâu vào chi tiết nhỏ.',
        'Mức độ quan tâm và tham gia các hoạt động đóng góp cho cộng đồng.',
        'Mức độ coi trọng tổ ấm và các mối quan hệ ruột thịt.'
    ],
    'Detail (Xem chi tiết, đọc bình luận, thảo luận)': [
        'Cách thường tham gia và tương tác trên các nền tảng trực tuyến.',
        'Tần suất viết comment trên các bài đăng công khai.',
        'Thói quen đọc sách giấy hoặc ebook nâng cao kiến thức.',
        'Thói quen viết bài hoặc bình luận ngắn gọn hay dài dòng.',
        'Tâm trạng nổi bật tại thời điểm tương tác trực tuyến.',
        'Mức độ tò mò, thích khám phá điều mới và đặt câu hỏi về thế giới xung quanh.'
    ],
    'Search (Tìm kiếm, tra cứu, đối chiếu)': [
        'Thói quen đặt câu hỏi và đòi hỏi chứng cứ trước thông tin mới.',
        'Xu hướng nhìn nhận bức tranh toàn cảnh hay đi sâu vào chi tiết nhỏ.',
        'Mức độ thành thạo trong việc phân tích lập luận, kiểm tra giả định và đánh giá thông tin một cách có lý trí',
        'Mức độ thành thạo trong việc suy luận có hệ thống và xác định quan hệ logic giữa các thông tin.',
        'Độ am hiểu và kỹ năng sử dụng thiết bị số và ứng dụng mạng.',
        'Loại nguồn mà thường sử dụng nhất để cập nhật kiến thức và thông tin.'
    ],
    'Feed (Lướt bảng tin tổng quan)': [
        'Xu hướng nhìn nhận bức tranh toàn cảnh hay đi sâu vào chi tiết nhỏ.',
        'Loại nguồn mà thường sử dụng nhất để cập nhật kiến thức và thông tin.',
        'Tần suất sử dụng Facebook',
        'Tâm trạng nổi bật tại thời điểm tương tác trực tuyến.',
        'Thói quen nước đến chân mới nhảy hay làm việc ngay.',
        'Đặc điểm nổi bật nhất theo nhóm tính cách Big Five'
    ]
}

print("=== KIỂM TRA TỒN TẠI CỦA CÁC TRƯỜNG ===")
for surf, fields in surface_drivers.items():
    print(f"\n[{surf}]")
    for f in fields:
        exists = f in first_attrs
        val_sample = [personas_dict[pid]['attributes'].get(f, 'N/A') for pid in p_ids]
        print(f" - {f}: {'OK' if exists else 'MISSING'}")
        print(f"   Values: {val_sample[:3]} ...")
