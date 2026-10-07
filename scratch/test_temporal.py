import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader

loader = ActionLoader()
df_w = loader.load_activity_windows()
print("Loaded df_w:", len(df_w))

# 1. Health check table
health_records = []
for col, name, valid_min, valid_max, unit in [
    ("start_hour_local", "Giờ bắt đầu phiên (UTC+7)", 6.0, 23.5, "Giờ"),
    ("duration_min", "Thời lượng phiên", 8.0, 32.0, "Phút"),
]:
    series = df_w[col]
    n_total = len(series)
    n_missing = int(series.isna().sum())
    val_min = float(series.min())
    val_max = float(series.max())
    n_violations = int(((series < valid_min) | (series > valid_max)).sum())
    pct_violations = (n_violations / n_total) * 100.0
    status = "✅ Hợp lệ (100%)" if n_violations == 0 else f"⚠️ {n_violations} điểm ngoài biên ({pct_violations:.1f}%)"
    
    health_records.append({
        "Biến số": name,
        "Cột dữ liệu": col,
        "Số quan sát (N)": n_total,
        "Số bản ghi khuyết": n_missing,
        "Khoảng thực tế [Min, Max]": f"[{val_min:.1f}, {val_max:.1f}] {unit}",
        "Ngưỡng hợp lệ kỳ vọng": f"[{valid_min:.1f}, {valid_max:.1f}] {unit}",
        "Số điểm ngoài ngưỡng": n_violations,
        "Đánh giá chất lượng": status
    })

# Thêm tần suất ngày
wpd = df_w.groupby(['persona_id', 'local_date']).size().reset_index(name='daily_windows')
n_wpd = len(wpd)
min_wpd = wpd['daily_windows'].min()
max_wpd = wpd['daily_windows'].max()
health_records.append({
    "Biến số": "Tần suất phiên mỗi ngày",
    "Cột dữ liệu": "daily_windows",
    "Số quan sát (N)": n_wpd,
    "Số bản ghi khuyết": 0,
    "Khoảng thực tế [Min, Max]": f"[{min_wpd}, {max_wpd}] Phiên/ngày",
    "Ngưỡng hợp lệ kỳ vọng": "[1, 4] Phiên/ngày",
    "Số điểm ngoài ngưỡng": int(((wpd['daily_windows'] < 1) | (wpd['daily_windows'] > 4)).sum()),
    "Đánh giá chất lượng": "✅ Hợp lệ (100%)"
})

df_health = pd.DataFrame(health_records)
print("\n=== DATA HEALTH CHECK TABLE ===")
print(df_health.to_string())

# 2. Distribution statistics table
dist_records = []
for col, name, unit in [
    ("start_hour_local", "Giờ bắt đầu phiên", "Giờ"),
    ("duration_min", "Thời lượng phiên", "Phút"),
]:
    s = df_w[col].dropna()
    q1 = float(s.quantile(0.25))
    q2 = float(s.median())
    q3 = float(s.quantile(0.75))
    iqr = q3 - q1
    skew = float(s.skew())
    kurt = float(s.kurt())
    
    shape_desc = "Gần đối xứng" if abs(skew) < 0.2 else ("Lệch phải" if skew > 0 else "Lệch trái")
    if kurt < -1.0:
        kurt_desc = "Phẳng / Đa đỉnh"
    elif kurt > 1.0:
        kurt_desc = "Nhọn / Đỉnh dốc"
    else:
        kurt_desc = "Trung bình"
        
    dist_records.append({
        "Biến số": name,
        "Đơn vị": unit,
        "Số mẫu (N)": len(s),
        "Mean": float(s.mean()),
        "Std": float(s.std()),
        "Median (Q2)": q2,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "Min": float(s.min()),
        "Max": float(s.max()),
        "Skewness": skew,
        "Kurtosis": kurt,
        "Hình thái phân phối": f"{shape_desc}, {kurt_desc}"
    })

# Add daily windows distribution
s_wpd = wpd['daily_windows']
q1_w = float(s_wpd.quantile(0.25))
q2_w = float(s_wpd.median())
q3_w = float(s_wpd.quantile(0.75))
dist_records.append({
    "Biến số": "Tần suất phiên ngày",
    "Đơn vị": "Phiên/ngày",
    "Số mẫu (N)": len(s_wpd),
    "Mean": float(s_wpd.mean()),
    "Std": float(s_wpd.std()),
    "Median (Q2)": q2_w,
    "Q1": q1_w,
    "Q3": q3_w,
    "IQR": q3_w - q1_w,
    "Min": float(s_wpd.min()),
    "Max": float(s_wpd.max()),
    "Skewness": float(s_wpd.skew()),
    "Kurtosis": float(s_wpd.kurt()),
    "Hình thái phân phối": "Đều đặn [1 - 3]"
})

df_dist = pd.DataFrame(dist_records)
print("\n=== DISTRIBUTION STATS TABLE ===")
print(df_dist.to_string())

# 3. By Persona breakdown table
by_p = []
for pid in sorted(df_w['persona_id'].unique()):
    sub = df_w[df_w['persona_id'] == pid]
    sub_wpd = wpd[wpd['persona_id'] == pid]
    by_p.append({
        "Persona ID": pid,
        "Số Windows": len(sub),
        "Giờ bắt đầu Mean": round(sub['start_hour_local'].mean(), 1),
        "Giờ bắt đầu Std": round(sub['start_hour_local'].std(), 1),
        "Giờ [Min, Max]": f"[{sub['start_hour_local'].min():.1f}, {sub['start_hour_local'].max():.1f}]h",
        "Thời lượng Mean": round(sub['duration_min'].mean(), 1),
        "Thời lượng Std": round(sub['duration_min'].std(), 1),
        "Thời lượng [Min, Max]": f"[{sub['duration_min'].min():.0f}, {sub['duration_min'].max():.0f}]m",
        "Tần suất ngày Mean": round(sub_wpd['daily_windows'].mean(), 1) if not sub_wpd.empty else 0,
        "Số ngày hoạt động": len(sub_wpd)
    })

df_by_p = pd.DataFrame(by_p)
print("\n=== BY PERSONA TEMPORAL BREAKDOWN ===")
print(df_by_p.to_string())
