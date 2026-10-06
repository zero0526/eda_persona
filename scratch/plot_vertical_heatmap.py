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

cur = conn.cursor()
cur.execute("""
    SELECT b.persona_id, pv.content_json
    FROM bots b
    JOIN persona_versions pv ON pv.bot_id = b.id
    ORDER BY b.persona_id
""")

persona_names = {
    "vn_fb_001": "vn_fb_001\n(Nữ 30t, Hybrid, 2 con)",
    "vn_fb_002": "vn_fb_002\n(Nữ 40t, Lưu động, 3 con)",
    "vn_fb_003": "vn_fb_003\n(Nam 21t, Gen Z, độc thân)",
    "vn_fb_004": "vn_fb_004\n(Nam 30t, F&B tự do, độc thân)",
    "vn_fb_005": "vn_fb_005\n(Nam 40t, Văn phòng, 2 con)",
    "vn_fb_006": "vn_fb_006\n(Nam 60t, Gen X, tự do giờ)",
}

profile_dict = {}
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
    
    profile_dict[p_id] = {
        "Độ tuổi (Tuổi TB)": age_val,
        "Thời lượng xem video (h/tuần)": stream_val,
        "Có con nhỏ (1=Có, 0=Không)": has_child,
        "Giới tính nữ (1=Nữ, 0=Nam)": is_female,
        "Nghề tự do / F&B (1=Đúng)": is_fnb,
        "Cao tuổi Gen X 55+ (1=Đúng)": is_gen_x,
    }

df_prof = pd.DataFrame(profile_dict).T

# Windows
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
    "Tỷ trọng phân bổ Reels (bias_reels)",
    "Tỷ trọng phân bổ Feed (bias_feed)",
    "Tỷ lệ Sáng sớm <=8h (%)",
    "Tỷ lệ Đêm muộn >=21h (%)",
    "Thời lượng phiên TB (phút)",
]

# Combined matrix
df_combined = pd.concat([df_prof, df_win_agg], axis=1)

# Format text representation for each cell
text_repr = df_combined.copy()
for col in text_repr.columns:
    if "%" in col:
        text_repr[col] = text_repr[col].apply(lambda v: f"{v:.1f}%")
    elif "Tỷ trọng" in col:
        text_repr[col] = text_repr[col].apply(lambda v: f"{v:.2f}")
    elif "phút" in col or "Tuổi" in col or "h/tuần" in col:
        text_repr[col] = text_repr[col].apply(lambda v: f"{v:.1f}")
    else:
        text_repr[col] = text_repr[col].apply(lambda v: f"{int(v)}")

# Min-max normalize per column (for row display) or transpose
df_norm = (df_combined - df_combined.min()) / (df_combined.max() - df_combined.min() + 1e-9)

# We transpose so that Columns = 6 Personas, Rows = 11 Attributes
df_norm_t = df_norm.T
text_repr_t = text_repr.T

# Rename columns to friendly names
df_norm_t.columns = [persona_names[c] for c in df_norm_t.columns]
text_repr_t.columns = [persona_names[c] for c in text_repr_t.columns]

plt.figure(figsize=(14, 8.5))
sns.heatmap(
    df_norm_t,
    annot=text_repr_t.values,
    fmt="",
    cmap="YlGnBu",
    cbar=True,
    cbar_kws={'label': 'Mức độ chuẩn hóa Min-Max theo thuộc tính (0 = Thấp nhất, 1 = Cao nhất)'},
    linewidths=1.2,
    linecolor='white'
)

plt.title("MA TRẬN HEATMAP ĐỐI CHIẾU THUỘC TÍNH PERSONA VÀ CẤU HÌNH CỬA SỔ HOẠT ĐỘNG ($H_1$)\n(Mỗi ô thể hiện giá trị đo lường thực tế của từng Persona; màu sắc thể hiện cường độ tương đối)", fontsize=12, fontweight='bold', pad=15)
plt.xlabel("Danh Tính Persona (6 Personas Nghiên Cứu)", fontweight='bold', fontsize=11, labelpad=10)
plt.ylabel("Thuộc Tính Hồ Sơ (Profile X) & Cấu Hình Cửa Sổ (Window Behavior Y)", fontweight='bold', fontsize=11)
plt.axhline(6, color='crimson', linewidth=2.5, linestyle='--')
plt.text(0.1, 5.85, "▲ HỒ SƠ NHÂN KHẨU & THÓI QUEN (INDEPENDENT X)", color='darkblue', fontweight='bold', fontsize=10)
plt.text(0.1, 6.25, "▼ CẤU HÌNH CỬA SỔ HOẠT ĐỘNG H1 (DEPENDENT Y)", color='darkred', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig("scratch/persona_unified_vertical_heatmap.png", dpi=200)
print("Saved scratch/persona_unified_vertical_heatmap.png successfully!")

conn.close()
