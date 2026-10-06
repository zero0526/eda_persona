import sys
import os
sys.path.append(os.path.abspath('.'))
import json
import sqlite3
import pandas as pd
from scipy import stats

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
df_bots = conn.execute("""
    SELECT b.persona_id, pv.content_json 
    FROM bots b 
    JOIN persona_versions pv ON pv.bot_id = b.id
""").fetchall()

personas_dict = {p_id: json.loads(p_json) if p_json else {} for p_id, p_json in df_bots}

freq_map = {'Hàng ngày': 3, 'Vài lần một tuần': 2, 'Vài lần một tháng': 1, 'Rất hiếm khi': 0, 'Không bao giờ': 0}

rows = []
for p_id in sorted(personas_dict.keys()):
    attrs = personas_dict[p_id].get('attributes', {})
    arch = attrs.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.', '')
    cmt_f = attrs.get('Tần suất viết comment trên các bài đăng công khai.', '')
    share_f = attrs.get('Tần suất share lại nội dung của fanpage hoặc người khác về tường.', '')
    post_f = attrs.get('Tần suất tự viết status hoặc đăng nội dung mới lên trang cá nhân.', '')
    
    rows.append({
        'persona_id': p_id,
        'Archetype': arch,
        'cmt_freq_text': cmt_f,
        'cmt_rank': freq_map.get(cmt_f, 0),
        'share_freq_text': share_f,
        'share_rank': freq_map.get(share_f, 0),
        'post_freq_text': post_f,
        'post_rank': freq_map.get(post_f, 0),
    })

df = pd.DataFrame(rows)
print("=== CHI TIẾT HỒ SƠ 6 PERSONA ===")
for _, r in df.iterrows():
    print(f"\nPersona: {r['persona_id']}")
    print(f" - Archetype: {r['Archetype']}")
    print(f" - Tần suất Comment : {r['cmt_freq_text']} (Rank {r['cmt_rank']})")
    print(f" - Tần suất Share   : {r['share_freq_text']} (Rank {r['share_rank']})")
    print(f" - Tần suất Post bài: {r['post_freq_text']} (Rank {r['post_rank']})")
