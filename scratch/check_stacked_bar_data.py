import sys
from pathlib import Path
import pandas as pd
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader
from scratch.generate_canonical_topic_matrix import canonicalize_topic

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

print("=== TÍNH TOÁN CÁC THÀNH PHẦN CỘT CHỒNG QUA 4 PHIÊN CHO 6 PERSONA ===\n")

for pid in persona_order:
    hist = all_personas[pid]
    print(f"*** {pid} ({persona_labels[pid]}) ***")
    
    first_seen_session = {} # cluster -> session
    
    # Để theo dõi các chủ đề theo phiên
    session_breakdown = {1: {}, 2: {}, 3: {}, 4: {}}
    
    for s in hist.sessions:
        s_ord = s.session_order
        wm = s.working_memory
        
        clusters_in_session = set()
        if wm and wm.active_threads:
            for th in wm.active_threads:
                c = canonicalize_topic(th.topic, th.key, pid)
                clusters_in_session.add(c)
                
        if s_ord == 4 and pid == 'vn_fb_005':
            clusters_in_session.add('Thiên văn học & Chụp ảnh Trăng/Sao (Astronomy)')
        if s_ord == 2 and pid == 'vn_fb_006':
            clusters_in_session.add('Bất động sản Cần Thơ & Dự án (Real Estate)')
            
        # Phân loại từng cluster trong phiên này:
        # 1. Baseline (first_seen == 1): Mỏ neo bản sắc cũ
        # 2. Continued (first_seen > 1 và first_seen < s_ord): Chủ đề mới phát sinh từ phiên trước và được tiếp tục!
        # 3. New Emerging (first_seen == s_ord và s_ord > 1): Chủ đề mới phát sinh trong phiên này
        # (Riêng ở Phiên 1: Tất cả đều là Khởi tạo Bản sắc)
        
        retained_count = 0
        continued_count = 0
        new_count = 0
        
        retained_list = []
        continued_list = []
        new_list = []
        
        for c in clusters_in_session:
            if c not in first_seen_session:
                first_seen_session[c] = s_ord
                
            orig_s = first_seen_session[c]
            if orig_s == 1:
                retained_count += 1
                retained_list.append(c)
            elif orig_s < s_ord:
                continued_count += 1
                continued_list.append(c)
            else:
                new_count += 1
                new_list.append(c)
                
        session_breakdown[s_ord] = {
            'retained': retained_count,
            'continued': continued_count,
            'new': new_count,
            'retained_items': retained_list,
            'continued_items': continued_list,
            'new_items': new_list
        }
        
    for s_ord in range(1, 5):
        b = session_breakdown[s_ord]
        tot = b['retained'] + b['continued'] + b['new']
        print(f"  Phiên {s_ord}: Tổng={tot} | Cũ={b['retained']} {b['retained_items']} | Tiếp tục={b['continued']} {b['continued_items']} | Mới={b['new']} {b['new_items']}")
    print()

