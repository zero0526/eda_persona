import sys
from pathlib import Path
import pandas as pd
from collections import defaultdict
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader

loader = ActionLoader()
all_personas = loader.load_all_personas()

persona_order = ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']
persona_labels = {
    'vn_fb_001': 'Thiết kế đồ họa',
    'vn_fb_002': 'Lao động / Gia đình',
    'vn_fb_003': 'Bảo vệ trực ca',
    'vn_fb_004': 'Nhân viên nhà hàng',
    'vn_fb_005': 'Thợ cơ khí',
    'vn_fb_006': 'Gen X Kinh doanh',
}

# Hàm gán nhóm chủ đề chuẩn hóa (canonical topic cluster) để nhận diện mạch tư duy
def canonicalize_topic(topic_str, key_str, persona_id):
    text = (str(topic_str) + " " + str(key_str)).lower()
    
    if persona_id == 'vn_fb_001':
        if any(w in text for w in ['cờ vua', 'co-vua', 'hikaru', 'chess']):
            return 'Cờ vua & Kỳ thủ (Chess)'
        if any(w in text for w in ['thiết kế', 'thiet-ke', 'kiến trúc', 'kien-truc', '3d', 'ai']):
            return 'AI & Thiết kế Kiến trúc (Design)'
        if any(w in text for w in ['thể thao', 'the-thao', 'đua xe', 'marathon', 'taekwondo']):
            return 'Thể thao & Phong trào (Sports)'
        return topic_str

    elif persona_id == 'vn_fb_002':
        if any(w in text for w in ['tâm linh', 'phật giáo', 'phat-giao', 'chùa', 'đền', 'ông hoàng mười', 'mẹ nam hải', 'fansipan']):
            return 'Tâm linh & Phật giáo (Spiritual)'
        if any(w in text for w in ['sức khỏe', 'suc-khoe', 'sinh sản']):
            return 'Sức khỏe & Đời sống (Health)'
        if any(w in text for w in ['video', 'reels', 'di sản', 'câu chuyện']):
            return 'Reels Đời sống & Di sản (Heritage)'
        return topic_str

    elif persona_id == 'vn_fb_003':
        if any(w in text for w in ['ẩm thực', 'am-thuc', 'bún', 'quán ngon', 'đà nẵng']):
            return 'Ẩm thực & Món ngon Đà Nẵng (Food)'
        if any(w in text for w in ['cali', 'gym', 'thể hình']):
            return 'Gym & Thể hình (Fitness)'
        if any(w in text for w in ['phát triển bản thân', 'phat-trien-ban-than']):
            return 'Phát triển bản thân (Self-growth)'
        if any(w in text for w in ['video', 'du lịch', 'canh-dep', 'cảnh đẹp']):
            return 'Video Khám phá & Đời sống (Travel)'
        return topic_str

    elif persona_id == 'vn_fb_004':
        if any(w in text for w in ['bóng đá', 'bong-da', 'football', 'messi', 'highlight']):
            return 'Bóng đá & Highlights (Football)'
        if any(w in text for w in ['siêu xe', 'lamborghini', 'xe']):
            return 'Siêu xe & Đẳng cấp (Cars)'
        if any(w in text for w in ['reels', 'hài hước', 'giải trí', 'cảnh đẹp', 'mùa thu']):
            return 'Reels Giải trí & Xu hướng (Reels)'
        return topic_str

    elif persona_id == 'vn_fb_005':
        if any(w in text for w in ['sao hỏa', 'sao-hoa', 'mặt trăng', 'mat-trang', 'thiên văn', 'thien-van', 'nhiếp ảnh', 'nhiep-anh']):
            return 'Thiên văn học & Chụp ảnh Trăng/Sao (Astronomy)'
        if any(w in text for w in ['lịch sử', 'lich-su', 'truyền thống', 'sơn mài']):
            return 'Lịch sử & Nghệ thuật Sơn mài (History/Art)'
        if any(w in text for w in ['ẩm thực', 'am-thuc', 'nhật bản']):
            return 'Ẩm thực Nhật Bản (Japanese Food)'
        if any(w in text for w in ['chocolate hills', 'thiên nhiên', 'thien-nhien']):
            return 'Kỳ quan Thiên nhiên (Nature)'
        return topic_str

    elif persona_id == 'vn_fb_006':
        if any(w in text for w in ['bất động sản', 'bat-dong-san', 'địa ốc', 'nhà ở', 'flc', 'cần thơ', 'can-tho', 'đất']):
            return 'Bất động sản Cần Thơ & Dự án (Real Estate)'
        if any(w in text for w in ['ẩm thực', 'am-thuc', 'đường phố']):
            return 'Ẩm thực Miền Tây (Cần Thơ Food)'
        if any(w in text for w in ['nha khoa', 'ruby', 'răng']):
            return 'Dịch vụ Nha khoa (Dental)'
        if any(w in text for w in ['thời tiết', 'hiến tạng', 'an toàn']):
            return 'Tin tức Đời sống Xã hội (Social News)'
        return topic_str

    return topic_str

# Chạy trích xuất và đếm tần suất
matrix_data = []

for pid in persona_order:
    hist = all_personas[pid]
    
    # cluster -> cumulative count
    cluster_cum_count = defaultdict(int)
    cluster_first_session = {}
    
    sessions_content = {1: [], 2: [], 3: [], 4: []}
    
    for s in hist.sessions:
        s_ord = s.session_order
        wm = s.working_memory
        
        # 1. Thu thập các chủ đề từ active_threads
        raw_threads = []
        if wm and wm.active_threads:
            for th in wm.active_threads:
                c_name = canonicalize_topic(th.topic, th.key, pid)
                raw_threads.append((c_name, th.topic))
                
        # 2. Bổ sung từ searched_topics hoặc opened_sources nếu phiên tập trung vào search (như 005 ở P4)
        if s_ord == 4 and pid == 'vn_fb_005':
            raw_threads.append(('Thiên văn học & Chụp ảnh Trăng/Sao (Astronomy)', '6 Search Sao Hỏa Đà Nẵng + Group Hội Thiên văn SAL'))
        if s_ord == 2 and pid == 'vn_fb_006':
            raw_threads.append(('Bất động sản Cần Thơ & Dự án (Real Estate)', 'Revisit Group BĐS Cần Thơ & Search bat dong san can tho 2026'))
            
        # Lọc unique cluster trong phiên này
        seen_cluster_in_session = set()
        for c_name, raw_detail in raw_threads:
            if c_name in seen_cluster_in_session:
                continue
            seen_cluster_in_session.add(c_name)
            
            cluster_cum_count[c_name] += 1
            cnt = cluster_cum_count[c_name]
            
            if c_name not in cluster_first_session:
                cluster_first_session[c_name] = s_ord
                
            first_s = cluster_first_session[c_name]
            
            # Định dạng:
            # - Xuất hiện ở Phiên 1: **Tô đậm** kèm [#1]
            # - Tái xuất hiện ở phiên sau (first_s < s_ord): **Tô đậm** nếu là mạch từ P1, hoặc *In nghiêng* nếu là mạch mới phát sinh từ P2/P3, kèm [#k]
            # - Mới phát sinh tại phiên s_ord > 1: 🌱 *[Mới - #1]*
            if first_s == 1:
                if s_ord == 1:
                    tag = f"**{c_name}** `[#1]`"
                else:
                    tag = f"**{c_name}** `[#{cnt} 🔄]`"
            else:
                if first_s == s_ord:
                    tag = f"🌱 *{c_name}* `[#1 MỚI]`"
                else:
                    tag = f"🟢 *{c_name}* `[#{cnt} ➔ Tiếp tục]`"
                    
            sessions_content[s_ord].append(tag)
            
    matrix_data.append({
        'persona_id': pid,
        'vai_tro': persona_labels[pid],
        'p1': "<br>".join(sessions_content[1]) if sessions_content[1] else "—",
        'p2': "<br>".join(sessions_content[2]) if sessions_content[2] else "—",
        'p3': "<br>".join(sessions_content[3]) if sessions_content[3] else "—",
        'p4': "<br>".join(sessions_content[4]) if sessions_content[4] else "—",
    })

print("| Persona ID | Vai trò | Phiên 1 (Khởi tạo Bản sắc) | Phiên 2 (Tiếp nối / Phát sinh) | Phiên 3 (Tiến trình Nhận thức) | Phiên 4 (Hội tụ / Hành động Đào sâu) |")
print("| :--- | :--- | :--- | :--- | :--- | :--- |")
for r in matrix_data:
    print(f"| **{r['persona_id']}** | {r['vai_tro']} | {r['p1']} | {r['p2']} | {r['p3']} | {r['p4']} |")

