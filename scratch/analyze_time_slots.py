import sys
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader

loader = ActionLoader()
df_w = loader.load_activity_windows()

print("Toàn bộ phân bổ start_hour_local theo bins 1h:")
bins = list(range(6, 25))
df_w['hour_int'] = df_w['start_hour_local'].astype(int)
print(df_w['hour_int'].value_counts().sort_index())

# Thử phân loại theo 3 khung giờ đỉnh:
# Sáng: 6h - 10h (hoặc 6h - 11h)
# Trưa/Chiều: 11h - 16h (hoặc 11h - 14h)
# Tối: 17h - 23h (hoặc 18h - 23h)
def assign_3_slots(h):
    if 6 <= h < 11:
        return "1. Ca Sáng (6h - 11h)"
    elif 11 <= h < 17:
        return "2. Ca Trưa & Chiều (11h - 17h)"
    else:
        return "3. Ca Tối (17h - 23h)"

def assign_4_slots(h):
    if 6 <= h < 11:
        return "1. Sáng (6h-11h)"
    elif 11 <= h < 14:
        return "2. Trưa (11h-14h)"
    elif 14 <= h < 18:
        return "3. Chiều (14h-18h)"
    else:
        return "4. Tối (18h-23h)"

df_w['slot_3'] = df_w['start_hour_local'].apply(assign_3_slots)
df_w['slot_4'] = df_w['start_hour_local'].apply(assign_4_slots)

print("\n--- TỔNG KẾT THEO 3 KHUNG GIỜ ---")
print(df_w['slot_3'].value_counts().sort_index())

print("\n--- BẢNG CHÉO (PERSONA x 3 KHUNG GIỜ) ---")
ct3 = pd.crosstab(df_w['persona_id'], df_w['slot_3'])
print(ct3)

chi2_3, p_3, dof_3, expected_3 = chi2_contingency(ct3)
print(f"Chi2 = {chi2_3:.4f}, p-value = {p_3:.4f}, dof = {dof_3}")

# Tính Standardized Pearson Residuals: (O - E) / sqrt(E)
residuals_3 = (ct3 - expected_3) / np.sqrt(expected_3)
print("\n--- PEARSON RESIDUALS (3 SLOTS) ---")
print(residuals_3.round(2))

# Tính Haberman's Adjusted Residuals:
row_sums = ct3.sum(axis=1).values
col_sums = ct3.sum(axis=0).values
n_total = ct3.values.sum()
adj_residuals_3 = pd.DataFrame(index=ct3.index, columns=ct3.columns)
for i in range(len(row_sums)):
    for j in range(len(col_sums)):
        exp = expected_3[i, j]
        adj = (ct3.iloc[i, j] - exp) / np.sqrt(exp * (1 - row_sums[i] / n_total) * (1 - col_sums[j] / n_total))
        adj_residuals_3.iloc[i, j] = adj
print("\n--- HABERMAN ADJUSTED RESIDUALS (3 SLOTS) ---")
print(adj_residuals_3.astype(float).round(2))

print("\n--- BẢNG CHÉO (PERSONA x 4 KHUNG GIỜ) ---")
ct4 = pd.crosstab(df_w['persona_id'], df_w['slot_4'])
print(ct4)
chi2_4, p_4, dof_4, expected_4 = chi2_contingency(ct4)
print(f"Chi2 = {chi2_4:.4f}, p-value = {p_4:.4f}, dof = {dof_4}")
residuals_4 = (ct4 - expected_4) / np.sqrt(expected_4)
print("\n--- PEARSON RESIDUALS (4 SLOTS) ---")
print(residuals_4.round(2))
