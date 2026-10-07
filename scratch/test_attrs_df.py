import sqlite3, json, sys, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
cur = conn.cursor()
cur.execute('SELECT b.persona_id, pv.content_json, c.contract_json FROM bots b JOIN persona_versions pv ON b.id = pv.bot_id JOIN behavioral_contracts c ON pv.id = c.persona_version_id ORDER BY b.persona_id')

records = []
for pid, pjson, cjson in cur.fetchall():
    data = json.loads(pjson)
    attrs = data.get('attributes', {})
    contract = json.loads(cjson) if cjson else {}
    nav = contract.get('navigation', {})
    
    records.append({
        'Persona ID': pid,
        'Tuổi': attrs.get('Nhóm tuổi'),
        'Giới tính': attrs.get('Bản dạng giới'),
        'Nghề nghiệp': attrs.get('Nhóm vai trò công việc hiện tại.'),
        'Địa bàn': f"{attrs.get('Tỉnh / Thành phố')} ({attrs.get('Vùng miền')})",
        'Định dạng ưa thích': attrs.get('Loại hình nội dung yêu thích nhất'),
        'Mức độ nhóm': attrs.get('Mức độ sinh hoạt trong các hội nhóm và cộng đồng mạng xã hội.'),
        'Tần suất FB': attrs.get('Tần suất sử dụng Facebook'),
        'Hình thái tương tác': attrs.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.'),
        'Nhịp Pacing': nav.get('scrollCadence'),
    })

df = pd.DataFrame(records)
print(df.to_string())

print("\n--- Value counts: Định dạng ưa thích ---")
print(df['Định dạng ưa thích'].value_counts())
print("\n--- Value counts: Nhịp Pacing ---")
print(df['Nhịp Pacing'].value_counts())
print("\n--- Value counts: Giới tính ---")
print(df['Giới tính'].value_counts())
print("\n--- Value counts: Mức độ nhóm ---")
print(df['Mức độ nhóm'].value_counts())
