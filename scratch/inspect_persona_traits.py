import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open('data/selected_6_facebook_personas_description.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        pid = d['persona_id']
        att = d['attributes']
        print(f"=== {pid} ===")
        keys = [
            'Nhóm vai trò công việc hiện tại.',
            'Lĩnh vực của công việc chính hiện tại. Phân loại theo nhóm ngành kinh tế.',
            'Nhóm tuổi',
            'Nhóm thế hệ dựa trên thời kỳ họ sinh ra, thường được dùng để mô tả những trải nghiệm xã hội và công nghệ chung.',
            'Tín ngưỡng tôn giáo',
            'Mức độ tín ngưỡng',
            'Đặc điểm nổi bật nhất theo nhóm tính cách Big Five',
            'Mức độ muốn khám phá, đặt câu hỏi và tìm hiểu những điều mới.',
            'Độ dài thời gian duy trì sự chú ý sâu vào một việc.',
            'Mức độ duy trì thói quen, nguyên tắc và làm những việc cần làm ngay cả khi thiếu động lực.',
            'Phương thức xử lý vấn đề dựa trên số liệu logic hay linh cảm trực giác.',
            'Sự ưu tiên khi hoàn thành công việc.',
            'Mức độ coi trọng sự nghiệp và tích lũy tài sản.',
            'Loại hình nội dung yêu thích nhất',
            'Mức độ quan tâm đến thị trường địa ốc và không gian sống.',
            'Mức độ quan tâm đến thiết bị thông minh và công nghệ mới.',
            'Mức độ quan tâm, yêu thích thể thao',
            'Mức độ tập gym & calisthenics',
            'Thói quen giải trí bằng game trên điện thoại, máy tính hoặc console.',
            'Tâm trạng nổi bật tại thời điểm tương tác trực tuyến.'
        ]
        for k in keys:
            print(f"  {k}: {att.get(k)}")
        print()
