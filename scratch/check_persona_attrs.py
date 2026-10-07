import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
cur = conn.cursor()
cur.execute('SELECT b.persona_id, pv.content_json, c.contract_json FROM bots b JOIN persona_versions pv ON b.id = pv.bot_id JOIN behavioral_contracts c ON pv.id = c.persona_version_id')

for pid, pjson, cjson in cur.fetchall():
    data = json.loads(pjson)
    attrs = data.get('attributes', {})
    contract = json.loads(cjson) if cjson else {}
    nav = contract.get('navigation', {})
    print(f"=== {pid} ===")
    print(f"Tuổi: {attrs.get('Nhóm tuổi')}")
    print(f"Giới tính: {attrs.get('Giới tính')}")
    print(f"Nghề nghiệp: {attrs.get('Nhóm vai trò công việc hiện tại.')}")
    print(f"Địa bàn: {attrs.get('Tỉnh / Thành phố')} ({attrs.get('Vùng miền')})")
    print(f"Định dạng ưa thích: {attrs.get('Định dạng nội dung tiêu thụ chính')}")
    print(f"Mức độ nhóm: {attrs.get('Mức độ sinh hoạt trong các hội nhóm và cộng đồng mạng xã hội.')}")
    print(f"Tần suất FB: {attrs.get('Tần suất sử dụng Facebook')}")
    print(f"Hợp đồng cadence: {nav.get('scrollCadence')}")
