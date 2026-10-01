import pandas as pd
from pathlib import Path

data = [
    {
        "category": "Tiêu thụ nội dung (Consumption)",
        "no_persona_dimension": "reading_vs_watching, detail_orientation, content_consumption_format",
        "no_persona_description": "Cân nhắc đọc/xem thuần dựa trên độ dài và định dạng văn bản; đọc hết bài để hiểu bối cảnh; không có preference áp đặt",
        "persona_equivalent_dimension": "persona:readingDepth, persona:reading_depth, viewport:content",
        "persona_description": "Đọc lướt (skim) hoặc đọc sâu (deep) phụ thuộc tuyệt đối vào độ khớp giữa bài viết với sở thích cá nhân (Chess, Meditation...)",
        "cognitive_contrast": "No-Persona phụ thuộc vào hình thức bên ngoài; Persona phụ thuộc vào giá trị nội dung đối với bản sắc cá nhân"
    },
    {
        "category": "Tương tác xã hội (Social Interaction)",
        "no_persona_dimension": "social_engagement_style, emotional_expressiveness",
        "no_persona_description": "Không có lý do tương tác xã hội rõ ràng từ nội dung, chỉ đọc rồi lướt tiếp; chỉ phản hồi care/tim khi bài viết có tính cảm động phổ quát",
        "persona_equivalent_dimension": "persona:interactionStyle, persona:interaction_style, persona:personality",
        "persona_description": "Tương tác có chọn lọc (selective/active); chỉ like/react khi bài viết trúng đam mê và phù hợp với vai trò cộng đồng",
        "cognitive_contrast": "No-Persona thụ động, thờ ơ; Persona gắn kết mạnh mẽ và phản hồi có động cơ bản sắc rõ ràng"
    },
    {
        "category": "Khám phá & Tìm kiếm (Exploration & Search)",
        "no_persona_dimension": "curiosity, query_complexity",
        "no_persona_description": "Tò mò ngẫu nhiên khi feed lặp lại; truy vấn các sự kiện trung tính thời sự (sự kiện tháng 9 2026)",
        "persona_equivalent_dimension": "persona:discoveryStyle, persona:interest, session_memory:searched_topics",
        "persona_description": "Khám phá theo chủ đề chủ động (topic_led); truy vấn các ngách sở thích cụ thể (cờ vua toàn quốc, thiền cho người mới)",
        "cognitive_contrast": "No-Persona tìm kiếm cơ học để giải tỏa bế tắc feed; Persona tìm kiếm có chủ đích để thỏa mãn đam mê"
    },
    {
        "category": "Đổi mới vs Quen thuộc (Novelty vs Familiarity)",
        "no_persona_dimension": "novelty_vs_familiarity",
        "no_persona_description": "Coi chủ đề mới là ngẫu nhiên trong phiên, tiếp nhận tự nhiên không có thiên kiến",
        "persona_equivalent_dimension": "persona:Interest (mạch chính vs phụ), session_memory:exploration_state",
        "persona_description": "Ý thức rõ mạch sở thích nào đã khám phá (Chess), mạch nào chưa chạm tới (Cycling, Magic tricks) để chuyển dịch",
        "cognitive_contrast": "No-Persona không có khái niệm quen/lạ theo sở thích; Persona quản lý danh mục sở thích đa tầng"
    },
    {
        "category": "Quản lý nhịp độ & Thời gian (Pacing & Attention)",
        "no_persona_dimension": "attention_span",
        "no_persona_description": "Lướt tự nhiên dựa trên cảm giác chung về thời gian còn nhiều hay ít",
        "persona_equivalent_dimension": "persona:pace, persona:attention, session_memory:time_remaining",
        "persona_description": "Điều tiết tốc độ (quick vs moderate) và dừng đọc bài dựa trên quỹ thời gian đếm ngược chính xác và mức năng lượng",
        "cognitive_contrast": "No-Persona lướt trôi dạt theo quán tính; Persona điều phối phiên có chiến lược kết thúc rõ ràng"
    }
]

df_map = pd.DataFrame(data)
out_path = Path("output/tables/step4_cognitive_dimension_mapping.csv")
out_path.parent.mkdir(parents=True, exist_ok=True)
df_map.to_csv(out_path, index=False, encoding="utf-8-sig")
print("Saved cognitive dimension mapping to:", out_path)
