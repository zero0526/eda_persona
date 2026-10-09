import sys
from pathlib import Path
import pandas as pd
from collections import defaultdict

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

print("=== TRÍCH XUẤT MA TRẬN TIẾN TRÌNH LUỒNG TƯ DUY (SESSIONS 1 -> 4) ===\n")

matrix_rows = []

for pid in persona_order:
    hist = all_personas[pid]
    
    # Theo dõi tần suất xuất hiện tích lũy của từng topic
    # topic_key -> count
    topic_cum_count = defaultdict(int)
    topic_first_seen_session = {}
    
    session_cells = {1: [], 2: [], 3: [], 4: []}
    
    for s in hist.sessions:
        s_ord = s.session_order
        wm = s.working_memory
        
        # Lấy danh sách luồng trong phiên
        threads = wm.active_threads if wm and wm.active_threads else []
        
        # Nếu phiên không có active_threads (như 005 ở P4), lấy từ searched_topics hoặc memory_deltas
        if not threads:
            if wm and wm.searched_topics:
                # Dùng chủ đề tìm kiếm làm đại diện
                unique_searches = list(dict.fromkeys([st.purpose or st.query for st in wm.searched_topics]))
                for q in unique_searches[:2]:
                    # chuẩn hóa key
                    k = "tim-kiem-sao-hoa-doi-lap" if "sao hỏa" in q.lower() else q[:30]
                    topic_cum_count[k] += 1
                    cnt = topic_cum_count[k]
                    if k not in topic_first_seen_session:
                        topic_first_seen_session[k] = s_ord
                        session_cells[s_ord].append(f"🌱 **{q[:35]}** (Lần {cnt})")
                    else:
                        session_cells[s_ord].append(f"★ **{q[:35]}** (Lần {cnt})")
            continue
            
        seen_in_this_session = set()
        for th in threads:
            t_key = th.key or th.topic
            t_top = th.topic or th.key
            if not t_top or t_top in seen_in_this_session:
                continue
            seen_in_this_session.add(t_top)
            
            topic_cum_count[t_top] += 1
            cnt = topic_cum_count[t_top]
            
            if t_top not in topic_first_seen_session:
                topic_first_seen_session[t_top] = s_ord
                
            first_s = topic_first_seen_session[t_top]
            
            # Quy tắc định dạng:
            # - Nếu xuất hiện ở Phiên 1: Tô đậm **...** kèm (Lần 1)
            # - Nếu xuất hiện ở phiên sau nhưng đã có từ phiên trước: Ghi tên kèm (Lần k)
            # - Nếu mới xuất hiện ở phiên sau (s_ord > 1 và first_s == s_ord): Ghi 🌱 *Mới: ...* (Lần 1)
            if first_s == 1:
                if s_ord == 1:
                    fmt = f"**{t_top}** (Lần {cnt})"
                else:
                    fmt = f"**{t_top}** (Lần {cnt} 🔄)"
            else:
                if first_s == s_ord:
                    fmt = f"🌱 *{t_top}* (Lần {cnt} mới)"
                else:
                    fmt = f"*{t_top}* (Lần {cnt} ➔)"
            
            session_cells[s_ord].append(fmt)
            
    matrix_rows.append({
        'persona_id': pid,
        'vai_tro': persona_labels[pid],
        'session_1': "<br>• ".join(session_cells[1]) if session_cells[1] else "—",
        'session_2': "<br>• ".join(session_cells[2]) if session_cells[2] else "—",
        'session_3': "<br>• ".join(session_cells[3]) if session_cells[3] else "—",
        'session_4': "<br>• ".join(session_cells[4]) if session_cells[4] else "—",
    })

# In bảng Markdown
print("| Persona ID | Vai trò | Phiên 1 (Khởi tạo) | Phiên 2 (Tiến trình) | Phiên 3 (Tiến trình) | Phiên 4 (Hội tụ / Hành động) |")
print("| :--- | :--- | :--- | :--- | :--- | :--- |")
for r in matrix_rows:
    p1 = ("• " + r['session_1']) if r['session_1'] != "—" else "—"
    p2 = ("• " + r['session_2']) if r['session_2'] != "—" else "—"
    p3 = ("• " + r['session_3']) if r['session_3'] != "—" else "—"
    p4 = ("• " + r['session_4']) if r['session_4'] != "—" else "—"
    print(f"| **{r['persona_id']}** | {r['vai_tro']} | {p1} | {p2} | {p3} | {p4} |")

