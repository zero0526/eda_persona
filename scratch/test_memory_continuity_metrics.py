import sys
from pathlib import Path
import pandas as pd
import json
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader

loader = ActionLoader()
all_personas = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe()

print("================================================================================")
print("  KIỂM CHỨNG THỐNG KÊ TOÀN DIỆN: VAI TRÒ BỘ NHỚ XUYÊN PHIÊN (CROSS-SESSION MEMORY)")
print("================================================================================\n")

persona_order = ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']
persona_labels = {
    'vn_fb_001': 'Thiết kế đồ họa',
    'vn_fb_002': 'Lao động / Gia đình',
    'vn_fb_003': 'Bảo vệ trực ca',
    'vn_fb_004': 'Nhân viên nhà hàng',
    'vn_fb_005': 'Thợ cơ khí',
    'vn_fb_006': 'Gen X Kinh doanh',
}

summary_rows = []
evolution_details = []

for pid in persona_order:
    hist = all_personas[pid]
    p_act = df_actions[df_actions['persona_id'] == pid]
    
    # 1. Thu thập Baseline & Prior Known Threads
    prior_threads_baseline = set()
    if hist.sessions and hist.sessions[0].prior_memory:
        for th in hist.sessions[0].prior_memory.known_interest_threads:
            prior_threads_baseline.add(th.thread_key)
            
    # 2. Theo dõi tiến trình từng phiên
    all_read_urls_by_session = {}
    threads_by_session = {}
    deltas_by_session = {}
    searches_by_session = {}
    sources_by_session = {}
    
    for s in hist.sessions:
        s_ord = s.session_order
        wm = s.working_memory
        
        # Read posts
        read_urls = [rp.url for rp in wm.read_posts] if wm else []
        all_read_urls_by_session[s_ord] = read_urls
        
        # Active threads
        threads = []
        if wm and wm.active_threads:
            for th in wm.active_threads:
                threads.append({
                    'key': th.key,
                    'topic': th.topic,
                    'origin': th.origin,
                    'state': th.state
                })
        threads_by_session[s_ord] = threads
        
        # Deltas
        deltas = []
        if wm and wm.memory_deltas:
            for d in wm.memory_deltas:
                deltas.append({
                    'type': d.record_type,
                    'key': d.record_key,
                    'op': d.operation
                })
        deltas_by_session[s_ord] = deltas
        
        # Searches
        searches = [st.query for st in wm.searched_topics] if wm else []
        searches_by_session[s_ord] = searches
        
        # Opened sources
        sources = [os.target for os in wm.opened_sources] if wm else []
        sources_by_session[s_ord] = sources

    # 3. Tính toán các chỉ số
    # A. Tổng số bài đọc và Tỷ lệ đọc trùng lặp xuyên phiên
    total_reads = sum(len(urls) for urls in all_read_urls_by_session.values())
    seen_urls = set()
    duplicate_reads = 0
    for s_ord in sorted(all_read_urls_by_session.keys()):
        curr_urls = all_read_urls_by_session[s_ord]
        for u in curr_urls:
            if u in seen_urls:
                duplicate_reads += 1
            else:
                seen_urls.add(u)
    dup_read_rate = round(duplicate_reads / total_reads * 100, 1) if total_reads > 0 else 0.0

    # B. Luồng chủ đề: Duy trì chủ đề cũ vs Tiếp nhận chủ đề mới
    total_active_threads_count = 0
    retained_threads_count = 0
    emerging_threads_count = 0
    followed_through_count = 0
    
    # Theo dõi các chủ đề đã từng xuất hiện
    history_known_keys = set(prior_threads_baseline)
    
    # Xét các chủ đề mới ở phiên s và xem có xuất hiện ở phiên s+1 (hoặc các phiên sau) không
    emerging_to_next = []
    
    for s_ord in range(1, len(hist.sessions) + 1):
        curr_th = threads_by_session.get(s_ord, [])
        next_th = threads_by_session.get(s_ord + 1, [])
        next_deltas = deltas_by_session.get(s_ord + 1, [])
        next_searches = searches_by_session.get(s_ord + 1, [])
        next_sources = sources_by_session.get(s_ord + 1, [])
        
        # Tập hợp các từ khóa/key của phiên s+1
        next_keys_all = set([th['key'] for th in next_th if th['key']])
        next_keys_all.update([d['key'] for d in next_deltas if d['key']])
        next_text_all = " ".join([th['topic'] for th in next_th if th['topic']] + next_searches + next_sources).lower()
        
        for th in curr_th:
            total_active_threads_count += 1
            th_key = th['key'] or ''
            th_top = th['topic'] or ''
            th_origin = th['origin']
            
            # Kiểm tra xem đây là chủ đề kế thừa (retained) hay mới phát sinh (emerging)
            is_retained = (
                th_origin == 'persona' or 
                th_key in history_known_keys or
                any(pk in th_key or th_key in pk for pk in history_known_keys if pk)
            )
            
            if is_retained:
                retained_threads_count += 1
                history_known_keys.add(th_key)
            else:
                # Chủ đề mới phát sinh (từ situational feed)
                emerging_threads_count += 1
                history_known_keys.add(th_key)
                
                # Kiểm tra xem phiên tiếp theo có tiếp tục theo đuổi không
                continued_in_next = False
                if s_ord < len(hist.sessions):
                    # Khớp key trực tiếp
                    if th_key in next_keys_all:
                        continued_in_next = True
                    # Hoặc từ khóa chủ đề xuất hiện trong active threads/search/delta của phiên s+1
                    words = [w for w in th_key.replace('-', ' ').split() if len(w) > 3]
                    if any(w in next_text_all for w in words):
                        continued_in_next = True
                        
                if continued_in_next:
                    followed_through_count += 1
                    emerging_to_next.append((s_ord, th_top, s_ord + 1))

    # Tỷ lệ kế thừa bản sắc cũ (%)
    retention_rate = round(retained_threads_count / total_active_threads_count * 100, 1) if total_active_threads_count > 0 else 0.0
    
    # Tỷ lệ chủ đề mới được theo đuổi tiếp ở phiên sau (%)
    adoption_followthrough_rate = round(followed_through_count / emerging_threads_count * 100, 1) if emerging_threads_count > 0 else 0.0

    # C. Kiểm tra Revisit URLs & Queries (> 1 session)
    url_sub = p_act.dropna(subset=['action_url'])
    url_spec = url_sub[~url_sub['action_url'].isin(['https://www.facebook.com/', 'https://www.facebook.com'])]
    url_sess = url_spec.groupby('action_url')['session_id'].nunique()
    revisited_urls_count = int((url_sess > 1).sum())
    
    # Search queries revisited
    all_searches_list = []
    for s_ord, sqs in searches_by_session.items():
        for q in sqs:
            all_searches_list.append({'session': s_ord, 'query': q.strip().lower()})
    df_sq = pd.DataFrame(all_searches_list)
    revisited_searches_count = 0
    if not df_sq.empty:
        q_sess = df_sq.groupby('query')['session'].nunique()
        revisited_searches_count = int((q_sess > 1).sum())

    # D. Sổ cái biến đổi bộ nhớ (Memory deltas count)
    total_deltas = sum(len(d) for d in deltas_by_session.values())
    thread_deltas = sum(sum(1 for x in d if x['type'] == 'thread') for d in deltas_by_session.values())
    entity_deltas = sum(sum(1 for x in d if x['type'] == 'entity') for d in deltas_by_session.values())

    summary_rows.append({
        'persona_id': pid,
        'vai_tro': persona_labels[pid],
        'so_phien': len(hist.sessions),
        'tong_bai_doc': total_reads,
        'doc_trung_lap_xuyen_phien': duplicate_reads,
        'ty_le_doc_trung_pct': dup_read_rate,
        'tong_active_threads': total_active_threads_count,
        'so_luong_ke_thua_cu': retained_threads_count,
        'ty_le_ke_thua_cu_pct': retention_rate,
        'so_chu_de_moi_phat_sinh': emerging_threads_count,
        'so_chu_de_moi_duoc_tiep_tuc': followed_through_count,
        'ty_le_nuoi_duong_chu_de_moi_pct': adoption_followthrough_rate,
        'revisited_urls_count': revisited_urls_count,
        'revisited_searches_count': revisited_searches_count,
        'tong_memory_deltas': total_deltas,
        'thread_deltas': thread_deltas,
        'entity_deltas': entity_deltas,
        'emerging_details': emerging_to_next
    })

df_res = pd.DataFrame(summary_rows)

print("--- 1. BẢNG THỐNG KÊ TỔNG HỢP 6 PERSONA (EXACT METRICS) ---")
display_cols = [
    'persona_id', 'vai_tro', 'tong_bai_doc', 'ty_le_doc_trung_pct',
    'tong_active_threads', 'ty_le_ke_thua_cu_pct',
    'so_chu_de_moi_phat_sinh', 'so_chu_de_moi_duoc_tiep_tuc', 'ty_le_nuoi_duong_chu_de_moi_pct',
    'revisited_urls_count', 'tong_memory_deltas'
]
print(df_res[display_cols].to_string(index=False))

print("\n--- 2. CHI TIẾT CÁC CHỦ ĐỀ MỚI PHÁT SINH ĐƯỢC TIẾP TỤC ĐÀO SÂU Ở PHIÊN TIẾP THEO ---")
for _, r in df_res.iterrows():
    print(f"\nPersona: {r['persona_id']} ({r['vai_tro']})")
    if r['emerging_details']:
        for orig_s, top, next_s in r['emerging_details']:
            print(f"  🌱 [Phiên {orig_s} Phát sinh] '{top}' ➔ [Phiên {next_s} Tiếp tục đào sâu / tìm kiếm]")
    else:
        print("  (Không có chủ đề mới phát sinh tiếp nối; 100% thời gian duy trì mỏ neo bản sắc cũ)")

print("\n================================================================================")
