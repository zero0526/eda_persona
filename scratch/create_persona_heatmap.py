import sqlite3
import json
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# 1. Trích xuất thuộc tính của 6 Personas
cur = conn.cursor()
cur.execute("""
    SELECT b.persona_id, pv.content_json
    FROM bots b
    JOIN persona_versions pv ON pv.bot_id = b.id
    ORDER BY b.persona_id
""")

profile_list = []
for r in cur.fetchall():
    d = json.loads(r["content_json"]) if r["content_json"] else {}
    attrs = d.get("attributes", {})
    p_id = r["persona_id"]
    
    # Độ tuổi
    age_str = attrs.get("Nhóm tuổi", "")
    age_map = {"18-24 tuổi": 21.0, "25-34 tuổi": 29.5, "35-44 tuổi": 39.5, "45-54 tuổi": 49.5, "55-64 tuổi": 59.5}
    age_val = age_map.get(age_str, 30.0)
    
    # Con cái
    child_str = attrs.get("Số con", "")
    has_child = 0 if "Chưa có con" in child_str else 1
    
    # Streaming
    stream_str = str(attrs.get("Tổng thời gian xem phim, video và livestream hàng tuần.", ""))
    stream_val = 5.0 if "3-7" in stream_str else (11.5 if "8-15" in stream_str else 23.0)
    
    # Giới tính & Nghề nghiệp
    is_female = 1 if attrs.get("Bản dạng giới") == "Nữ" else 0
    work_str = attrs.get("Hình thức làm việc hoặc trạng thái nghề nghiệp hiện tại", "")
    is_fnb_freelance = 1 if p_id == "vn_fb_004" else 0
    is_gen_x = 1 if age_val >= 55 else 0
    
    profile_list.append({
        "persona_id": p_id,
        "Độ tuổi (Tuổi TB)": age_val,
        "Xem video (h/tuần)": stream_val,
        "Có con nhỏ (0/1)": has_child,
        "Nữ giới (0/1)": is_female,
        "Nghề tự do/F&B (0/1)": is_fnb_freelance,
        "Nhóm Gen X 55+ (0/1)": is_gen_x,
    })

df_prof = pd.DataFrame(profile_list).set_index("persona_id")

# 2. Trích xuất cửa sổ hoạt động
df_w = pd.read_sql_query("""
    SELECT 
        b.persona_id,
        w.start_at,
        w.end_at,
        w.surface_bias
    FROM activity_windows w
    JOIN bots b ON b.id = w.bot_id
""", conn)

df_w['start_dt'] = pd.to_datetime(df_w['start_at'])
df_w['end_dt'] = pd.to_datetime(df_w['end_at'])
df_w['start_local'] = df_w['start_dt'].dt.tz_convert('Asia/Ho_Chi_Minh')
df_w['start_hour_local'] = df_w['start_local'].dt.hour
df_w['is_late_night'] = (df_w['start_hour_local'] >= 21).astype(int)
df_w['is_early_morning'] = (df_w['start_hour_local'] <= 8).astype(int)
df_w['duration_min'] = (df_w['end_dt'] - df_w['start_dt']).dt.total_seconds() / 60.0

def parse_surface_bias(b):
    if not b:
        return {'bias_feed': 0.0, 'bias_reels': 0.0}
    try:
        data = json.loads(b) if isinstance(b, str) else b
        return {
            'bias_feed': float(data.get('feed', 0.0)),
            'bias_reels': float(data.get('reels', 0.0)),
        }
    except Exception:
        return {'bias_feed': 0.0, 'bias_reels': 0.0}

bias_df = pd.DataFrame(df_w['surface_bias'].apply(parse_surface_bias).tolist())
df_w = pd.concat([df_w, bias_df], axis=1)

df_win_agg = df_w.groupby('persona_id').agg(
    bias_reels=('bias_reels', 'mean'),
    bias_feed=('bias_feed', 'mean'),
    pct_early_morning=('is_early_morning', lambda x: x.mean() * 100),
    pct_late_night=('is_late_night', lambda x: x.mean() * 100),
    mean_duration=('duration_min', 'mean'),
).round(2)

df_win_agg.columns = [
    "Tỷ trọng Reels",
    "Tỷ trọng Feed",
    "Sáng sớm <=8h (%)",
    "Đêm muộn >=21h (%)",
    "Thời lượng TB (phút)",
]

# Kết hợp thành 1 bảng Persona Profile & Behavior Matrix
df_matrix = pd.concat([df_prof, df_win_agg], axis=1)
print("=== UNIFIED MATRIX ===")
print(df_matrix.to_string())

conn.close()
