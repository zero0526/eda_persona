import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency

sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader

loader = ActionLoader()
df_w = loader.load_activity_windows()

def assign_peak_slot(h):
    if 6 <= h < 11:
        return "Ca Sáng (6h - 11h)"
    elif 11 <= h < 17:
        return "Ca Trưa & Chiều (11h - 17h)"
    else:
        return "Ca Tối (17h - 23h)"

df_w['time_slot'] = df_w['start_hour_local'].apply(assign_peak_slot)

# Bảng chéo quan sát
ct = pd.crosstab(df_w['persona_id'], df_w['time_slot'])
order_cols = ["Ca Sáng (6h - 11h)", "Ca Trưa & Chiều (11h - 17h)", "Ca Tối (17h - 23h)"]
ct = ct[order_cols]

chi2, p_val, dof, expected = chi2_contingency(ct)
n = ct.values.sum()
cramers_v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))

# Haberman Adjusted Residuals
row_sums = ct.sum(axis=1).values
col_sums = ct.sum(axis=0).values
adj_res = pd.DataFrame(index=ct.index, columns=ct.columns, dtype=float)
for i in range(len(row_sums)):
    for j in range(len(col_sums)):
        exp = expected[i, j]
        adj = (ct.iloc[i, j] - exp) / np.sqrt(exp * (1 - row_sums[i] / n) * (1 - col_sums[j] / n))
        adj_res.iloc[i, j] = adj

# Pearson residuals
std_res = (ct - expected) / np.sqrt(expected)

print("Observed:")
print(ct)
print("\nExpected:")
print(pd.DataFrame(expected, index=ct.index, columns=ct.columns).round(2))
print(f"\nChi-Square = {chi2:.4f}, p = {p_val:.4f}, df = {dof}, Cramer's V = {cramers_v:.4f}")
print("\nAdjusted Residuals:")
print(adj_res.round(2))
