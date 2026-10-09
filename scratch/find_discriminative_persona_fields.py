import sys
import json
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = Path(__file__).resolve().parent.parent

jsonl_file = PROJECT_ROOT / "data" / "selected_6_facebook_personas_description.jsonl"

personas = []
with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            personas.append(json.loads(line))

print(f"Loaded {len(personas)} personas.")

# Lấy các trường tương tác quan trọng
interesting_keys = [
    "Cách thường tham gia và tương tác trên các nền tảng trực tuyến.",
    "Tần suất viết comment trên các bài đăng công khai.",
    "Tần suất share lại nội dung của fanpage hoặc người khác về tường.",
    "Loại hình nội dung yêu thích nhất",
    "Tổng thời gian xem phim, video và livestream hàng tuần.",
    "Tín ngưỡng tôn giáo",
    "Mức độ tín ngưỡng",
    "Tâm trạng nổi bật tại thời điểm tương tác trực tuyến.",
    "Phương thức xử lý vấn đề dựa trên số liệu logic hay linh cảm trực giác.",
    "Thói quen viết bài hoặc bình luận ngắn gọn hay dài dòng.",
    "Nhóm thế hệ dựa trên thời kỳ họ sinh ra, thường được dùng để mô tả những trải nghiệm xã hội và công nghệ chung.",
    "Nhóm vai trò công việc hiện tại."
]

data = []
for p in personas:
    pid = p["persona_id"]
    attrs = p["attributes"]
    row = {"persona_id": pid}
    for k in interesting_keys:
        row[k] = attrs.get(k, "N/A")
    data.append(row)

df_attrs = pd.DataFrame(data).set_index("persona_id")
print("\n=== GIÁ TRỊ CÁC TRƯỜNG TIÊU BIỂU CỦA 6 PERSONA ===")
for k in interesting_keys:
    print(f"\n--- TRƯỜNG: [{k}] ---")
    for pid, val in df_attrs[k].items():
        print(f"  * {pid}: {val}")
