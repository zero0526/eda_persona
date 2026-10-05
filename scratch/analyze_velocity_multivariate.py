import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression

sys.stdout.reconfigure(encoding='utf-8')

from loaders.loaders.persona_action import PersonaActionLoader
from algorithms.temporal_velocity_and_behavior_profiler import compute_temporal_velocity_by_pace

loader = PersonaActionLoader()
df_steps = loader.load_step_records()

res = compute_temporal_velocity_by_pace(df_steps)
df = res["df_processed"]

p_df = df[df["dataset_type"] == "persona"].copy()

print("="*90)
print("1. PHÂN TÍCH NHIỄU (CONFOUNDING EFFECT): VERIFIED TRONG TỪNG NHÓM PACE")
print("="*90)
pace_ver = p_df.groupby(["persona_pace", "verified"]).agg(
    n_steps=("context_action_velocity", "count"),
    mean_vel=("context_action_velocity", "mean"),
    median_vel=("context_action_velocity", "median"),
    std_vel=("context_action_velocity", "std"),
    min_vel=("context_action_velocity", "min"),
    max_vel=("context_action_velocity", "max")
).round(3)
print(pace_ver.to_string())

print("\n" + "="*90)
print("2. QUỸ ĐẠO VẬN TỐC THỰC TẾ KHI KIỂM SOÁT NHIỄU (CHỈ XÉT VERIFIED == TRUE)")
print("="*90)
p_clean = p_df[p_df["verified"] == True].copy()
clean_traj = p_clean.groupby(["persona_pace", "time_bin_4"], observed=False)["context_action_velocity"].agg(
    n=("count"),
    mean=("mean"),
    std=("std"),
    median=("median"),
    iqr=(lambda x: x.quantile(0.75) - x.quantile(0.25))
).round(2)
print(clean_traj.to_string())

print("\n" + "="*90)
print("3. BÓC TÁCH CHI TIẾT TỪNG PHIÊN CỦA PACE 'BALANCED' (vn_000041)")
print("="*90)
bal_df = p_df[p_df["persona_pace"] == "balanced"].copy()
print("Tổng số bước:", len(bal_df))
print("Số bước verified == False:", (bal_df["verified"] == False).sum())
print("Danh sách các bước verified == False:")
failed_bal = bal_df[bal_df["verified"] == False][["step_index", "intent", "tool", "context_action_velocity", "step_progress", "reason"]]
print(failed_bal.to_string())

# Tính elapsed_seconds delta
bal_df = bal_df.sort_values("step_index")
bal_df["delta_sec"] = bal_df["context_elapsed_seconds"].diff()
print("\nThời gian thực thi trung bình mỗi intent (giây) ở nhóm balanced:")
bal_intent_time = bal_df.groupby("intent")["delta_sec"].agg(
    count="count", mean="mean", median="median", std="std", min="min", max="max"
).round(1)
print(bal_intent_time.to_string())

print("\n" + "="*90)
print("4. MÔ HÌNH HÓA ĐA BIẾN (MULTIVARIATE VARIANCE DECOMPOSITION / ANOVA OLS)")
print("="*90)
# Biến phụ thuộc: context_action_velocity
# Các biến giải thích:
# - C(persona_pace)
# - verified
# - step_progress (tiến trình phiên)
# - C(intent)
# - model_latency_ms

sample_df = p_df[["context_action_velocity", "persona_pace", "verified", "step_progress", "intent", "model_latency_ms"]].dropna().copy()
sample_df["verified_bin"] = sample_df["verified"].astype(int)

# One-hot encoding
X_pace = pd.get_dummies(sample_df["persona_pace"], prefix="pace", drop_first=True, dtype=float)
X_intent = pd.get_dummies(sample_df["intent"], prefix="intent", drop_first=True, dtype=float)
X_num = sample_df[["verified_bin", "step_progress", "model_latency_ms"]]
X_all = pd.concat([X_pace, X_intent, X_num], axis=1)
y = sample_df["context_action_velocity"]

# OLS Fit
lr = LinearRegression().fit(X_all, y)
y_pred = lr.predict(X_all)
ss_total = ((y - y.mean()) ** 2).sum()
ss_res = ((y - y_pred) ** 2).sum()
r2 = 1 - ss_res / ss_total

print(f"Toàn bộ mô hình R-squared: {r2:.4f} (Giải thích được {r2*100:.1f}% phương sai)")

# Bóc tách Type II Sum of Squares bằng cách bỏ từng feature group
factors = {
    "verified": ["verified_bin"],
    "persona_pace": X_pace.columns.tolist(),
    "intent": X_intent.columns.tolist(),
    "step_progress": ["step_progress"],
    "model_latency_ms": ["model_latency_ms"]
}

n = len(y)
p_total = X_all.shape[1]
df_res = n - p_total - 1

results = []
for factor_name, cols in factors.items():
    X_sub = X_all.drop(columns=cols)
    lr_sub = LinearRegression().fit(X_sub, y)
    y_sub_pred = lr_sub.predict(X_sub)
    ss_sub_res = ((y - y_sub_pred) ** 2).sum()
    ss_factor = ss_sub_res - ss_res
    df_factor = len(cols)
    ms_factor = ss_factor / df_factor
    ms_res = ss_res / df_res
    f_stat = ms_factor / ms_res
    p_val = 1 - stats.f.cdf(f_stat, df_factor, df_res)
    eta_sq_part = ss_factor / (ss_factor + ss_res)
    results.append({
        "Yếu tố": factor_name,
        "DF": df_factor,
        "Sum of Sq (SS)": ss_factor,
        "Tỷ trọng SS (%)": (ss_factor / ss_total) * 100,
        "Partial Eta2": eta_sq_part,
        "F-statistic": f_stat,
        "p-value": p_val
    })

res_df = pd.DataFrame(results).sort_values("Sum of Sq (SS)", ascending=False)
print("\nBảng Phân rã Phương sai Đa biến (Multivariate Variance Decomposition):")
print(res_df.round(4).to_string(index=False))

print("\n" + "="*90)
print("5. PHÂN TÍCH TƯƠNG QUAN VẬN TỐC TỰ NHIÊN (CHỈ TRÊN BƯỚC VERIFIED == TRUE)")
print("="*90)
# Chạy lại OLS chỉ trên verified == True
clean_sample = sample_df[sample_df["verified"] == True].copy()
X_pace_c = pd.get_dummies(clean_sample["persona_pace"], prefix="pace", drop_first=True, dtype=float)
X_intent_c = pd.get_dummies(clean_sample["intent"], prefix="intent", drop_first=True, dtype=float)
X_num_c = clean_sample[["step_progress", "model_latency_ms"]]
X_all_c = pd.concat([X_pace_c, X_intent_c, X_num_c], axis=1)
y_c = clean_sample["context_action_velocity"]

lr_c = LinearRegression().fit(X_all_c, y_c)
y_c_pred = lr_c.predict(X_all_c)
ss_c_tot = ((y_c - y_c.mean()) ** 2).sum()
ss_c_res = ((y_c - y_c_pred) ** 2).sum()
r2_c = 1 - ss_c_res / ss_c_tot
print(f"Mô hình trên các bước Verified == True (R2: {r2_c:.4f}):")

factors_c = {
    "persona_pace": X_pace_c.columns.tolist(),
    "intent": X_intent_c.columns.tolist(),
    "step_progress": ["step_progress"],
    "model_latency_ms": ["model_latency_ms"]
}
n_c = len(y_c)
p_total_c = X_all_c.shape[1]
df_res_c = n_c - p_total_c - 1

results_c = []
for factor_name, cols in factors_c.items():
    X_sub = X_all_c.drop(columns=cols)
    lr_sub = LinearRegression().fit(X_sub, y_c)
    y_sub_pred = lr_sub.predict(X_sub)
    ss_sub_res = ((y_c - y_sub_pred) ** 2).sum()
    ss_factor = ss_sub_res - ss_c_res
    df_factor = len(cols)
    ms_factor = ss_factor / df_factor
    ms_res = ss_c_res / df_res_c
    f_stat = ms_factor / ms_res
    p_val = 1 - stats.f.cdf(f_stat, df_factor, df_res_c)
    eta_sq_part = ss_factor / (ss_factor + ss_c_res)
    results_c.append({
        "Yếu tố": factor_name,
        "DF": df_factor,
        "Sum of Sq (SS)": ss_factor,
        "Tỷ trọng SS (%)": (ss_factor / ss_c_tot) * 100,
        "Partial Eta2": eta_sq_part,
        "F-statistic": f_stat,
        "p-value": p_val
    })

res_c_df = pd.DataFrame(results_c).sort_values("Sum of Sq (SS)", ascending=False)
print(res_c_df.round(4).to_string(index=False))
