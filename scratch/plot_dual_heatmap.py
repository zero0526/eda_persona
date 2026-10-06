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
persona_labels = {
    "vn_fb_001": "vn_fb_001 (Nữ 30t, Hybrid, 2 con)",
    "vn_fb_002": "vn_fb_002 (Nữ 40t, Lưu động, 3 con)",
    "vn_fb_003": "vn_fb_003 (Nam 21t, Gen Z, độc thân)",
    "vn_fb_004": "vn_fb_004 (Nam 30t, F&B tự do, độc thân)",
    "vn_fb_005": "vn_fb_005 (Nam 40t, Toàn thời gian, 2 con)",
    "vn_fb_006": "vn_fb_006 (Nam 60t, Gen X, tự do giờ)",
}

for r in cur.fetchall():
    d = json.loads(r["content_json"]) if r["content_json"] else {}
    attrs = d.get("attributes", {})
    p_id = r["persona_id"]
    
    age_str = attrs.get("Nhóm tuổi", "")
    age_map = {"18-24 tuổi": 21.0, "25-34 tuổi": 29.5, "35-44 tuổi": 39.5, "45-54 tuổi": 49.5, "55-64 tuổi": 59.5}
    age_val = age_map.get(age_str, 30.0)
    
    child_str = attrs.get("Số con", "")
    has_child = 0 if "Chưa có con" in child_str else 1
    
    stream_str = str(attrs.get("Tổng thời gian xem phim, video và livestream hàng tuần.", ""))
    stream_val = 5.0 if "3-7" in stream_str else (11.5 if "8-15" in stream_str else 23.0)
    
    is_female = 1 if attrs.get("Bản dạng giới") == "Nữ" else 0
    is_fnb = 1 if p_id == "vn_fb_004" else 0
    is_gen_x = 1 if age_val >= 55 else 0
    
    profile_list.append({
        "persona_id": persona_labels.get(p_id, p_id),
        "Độ tuổi (Tuổi)": age_val,
        "Xem video (h/tuần)": stream_val,
        "Có con nhỏ (0/1)": has_child,
        "Nữ giới (0/1)": is_female,
        "Nghề tự do/F&B (0/1)": is_fnb,
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

df_w['persona_label'] = df_w['persona_id'].map(persona_labels)

df_win_agg = df_w.groupby('persona_label').agg(
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

# Chuẩn hóa Min-Max từng cột để tô màu heatmap (0 -> 1)
df_prof_norm = (df_prof - df_prof.min()) / (df_prof.max() - df_prof.min() + 1e-9)
df_win_norm = (df_win_agg - df_win_agg.min()) / (df_win_agg.max() - df_win_agg.min() + 1e-9)

# Vẽ Figure với 2 Heatmaps liên kết ngang
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6), gridspec_kw={'width_ratios': [1.1, 1.0]})

# Heatmap 1: Hồ sơ Persona
sns.heatmap(
    df_prof_norm,
    annot=df_prof.values,
    fmt="",
    cmap="YlGnBu",
    cbar=True,
    cbar_kws={'label': 'Mức độ chuẩn hóa (Min-Max)'},
    ax=ax1,
    linewidths=1,
    linecolor='white'
)
ax1.set_title("BẢNG 1: MA TRẬN HỒ SƠ THUỘC TÍNH PERSONA (INDEPENDENT X)\n(Số liệu hiển thị trong ô là giá trị thực tế của từng nhân vật)", fontsize=11, fontweight='bold', pad=12)
ax1.set_ylabel("Persona Định Danh", fontweight='bold')
ax1.tick_params(axis='x', rotation=30)

# Heatmap 2: Cấu hình Cửa sổ Hoạt động H1
sns.heatmap(
    df_win_norm,
    annot=df_win_agg.values,
    fmt="",
    cmap="OrRd",
    cbar=True,
    cbar_kws={'label': 'Mức độ chuẩn hóa (Min-Max)'},
    ax=ax2,
    linewidths=1,
    linecolor='white'
)
ax2.set_title("BẢNG 2: MA TRẬN CẤU HÌNH CỬA SỔ HOẠT ĐỘNG $H_1$ (DEPENDENT Y)\n(Phản ánh nhịp sinh học, bề mặt phân bổ và thời lượng phiên)", fontsize=11, fontweight='bold', pad=12)
ax2.set_ylabel("")
ax2.tick_params(axis='x', rotation=30)

plt.tight_layout()
plt.savefig("scratch/persona_attributes_dual_heatmap.png", dpi=200)
print("Saved scratch/persona_attributes_dual_heatmap.png successfully!")

conn.close()
