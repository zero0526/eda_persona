import sys
from pathlib import Path
import json
import sqlite3
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from loaders.action_loader import ActionLoader
loader = ActionLoader()
df_actions = loader.to_unified_actions_dataframe()

session_id = '53a21bfd-97c0-426f-b2d6-8312d37ecf2d'
session_steps = df_actions[(df_actions['session_id'] == session_id) & (df_actions['step_index'].between(65, 72))].sort_values('step_index')

print("=== 1. CÁC BƯỚC HÀNH ĐỘNG XUNG QUANH BƯỚC 68 ===")
for _, r in session_steps.iterrows():
    print(f"Bước {r['step_index']}: intent={r['intent']} | surface={r['surface']} | reaction={r.get('reaction', '')}")
    print(f"   Summary: {r.get('action_summary', '')}")
    print(f"   Reason (CoT): {r.get('reason', '')}")
    print(f"   Target ID: {r.get('target_id', '')}")
    print()

# Kiểm tra nội dung chi tiết bài viết trong DB nếu có
db_path = Path("data/persona_history.db")
if not db_path.exists():
    db_paths = list(Path("data").glob("*.db")) + list(Path(".").glob("*.db"))
    print("DB paths found:", db_paths)
    if db_paths:
        db_path = db_paths[0]

print(f"=== 2. TRUY VẤN NỘI DUNG BÀI VIẾT TỪ DB ({db_path}) ===")
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Tìm bảng có bài viết hoặc log chi tiết
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cur.fetchall()]
    print("Tables:", tables)
    
    # Tìm post hoặc raw data liên quan đến step 68 hoặc target_id
    if 'action_logs' in tables:
        cur.execute("SELECT * FROM action_logs WHERE session_id = ? AND step_index = 68", (session_id,))
        row = cur.fetchone()
        if row:
            print("Action log row columns:", [d[0] for d in cur.description])
            print("Action log row:", row)
    
    conn.close()
except Exception as e:
    print("DB query error:", e)

# 3. Kiểm tra hồ sơ persona vn_fb_006
print("\n=== 3. HỒ SƠ PERSONA vn_fb_006 ===")
profiles, contracts = loader.load_persona_profiles_and_contracts()
p6 = profiles.get('vn_fb_006', {})
attrs6 = p6.get('attributes', {})
print("Họ tên / Vai trò:", p6.get('name', ''), p6.get('demographics', {}))
for k, v in attrs6.items():
    if any(term in k.lower() for term in ['tuổi', 'nghề', 'giá trị', 'tính cách', 'quan điểm', 'phản', 'thái độ', 'sức khỏe']):
        print(f"  - {k}: {v}")
