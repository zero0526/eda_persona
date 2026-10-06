import sys
sys.path.insert(0, '.')
import sqlite3, json
import pandas as pd
from loaders.episode_loader import get_sqlite_path, list_episodes, load_episode

DB_PATH = get_sqlite_path()
conn = sqlite3.connect(DB_PATH)
df_bots = pd.read_sql_query('''
    SELECT b.persona_id, pv.content_json
    FROM bots b
    JOIN persona_versions pv ON pv.bot_id = b.id
''', conn)
conn.close()

episodes = list_episodes(DB_PATH)
df_steps = pd.concat([load_episode(e['id'], DB_PATH).to_steps_dataframe() for e in episodes], ignore_index=True)
surface_pct = pd.crosstab(df_steps['persona_id'], df_steps['surface'].fillna('unknown'), normalize='index') * 100

attrs_by_p = {}
for _, row in df_bots.iterrows():
    attrs_by_p[row['persona_id']] = json.loads(row['content_json']).get('attributes', {})

candidate_fields = [
    ('Nội dung ưa thích', 'Loại hình nội dung yêu thích nhất'),
    ('Thời lượng video', 'Tổng thời gian xem phim, video và livestream hàng tuần.'),
    ('Sinh hoạt Hội nhóm', 'Mức độ sinh hoạt trong các hội nhóm và cộng đồng mạng xã hội.'),
    ('Tư duy Tổng quan/Chi tiết', 'Xu hướng nhìn nhận bức tranh toàn cảnh hay đi sâu vào chi tiết nhỏ.'),
    ('Kiểm chứng / Hoài nghi', 'Thói quen đặt câu hỏi và đòi hỏi chứng cứ trước thông tin mới.'),
    ('Nguồn cập nhật tin tức', 'Loại nguồn mà thường sử dụng nhất để cập nhật kiến thức và thông tin.'),
    ('Thế hệ', 'Nhóm thế hệ dựa trên thời kỳ họ sinh ra, thường được dùng để mô tả những trải nghiệm xã hội và công nghệ chung.'),
    ('Độ tuổi', 'Nhóm tuổi'),
    ('Khả năng tập trung', 'Độ dài thời gian duy trì sự chú ý sâu vào một việc.'),
    ('Phong cách tham gia MXH', 'Cách thường tham gia và tương tác trên các nền tảng trực tuyến.')
]

rows = []
for pid in sorted(surface_pct.index):
    item = {'persona_id': pid}
    for col in ['feed', 'reels', 'group', 'detail', 'search']:
        item[f'surf_{col}_pct'] = round(surface_pct.loc[pid, col], 1) if col in surface_pct.columns else 0.0
    
    for label, field in candidate_fields:
        item[label] = attrs_by_p[pid].get(field, 'N/A')
    rows.append(item)

df_comp = pd.DataFrame(rows)
print(df_comp.to_string())
