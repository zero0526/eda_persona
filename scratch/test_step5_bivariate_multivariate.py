import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.feature_selection import mutual_info_classif
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Ensure utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Import loader
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from loaders.loaders.persona_action import PersonaActionLoader

print(">>> [1/7] Nạp toàn bộ dữ liệu step_records...")
loader = PersonaActionLoader(
    persona_path=project_root / "data" / "action_logs",
    no_persona_path=project_root / "data" / "no_persona_Action",
    fb_persona_path=project_root / "data" / "original_facebook_persona.json"
)

df = loader.load_step_records(source="all")
print(f"Tổng số bản ghi steps: {len(df)} dòng, {len(df.columns)} cột.")

# Tính thêm step_delta_sec nếu chưa có
df['timestamp_dt'] = pd.to_datetime(df['timestamp'], errors='coerce')
df['step_delta_sec'] = df.groupby('episode_id')['timestamp_dt'].diff().dt.total_seconds()

# Danh sách biến numeric và categorical chính
numeric_cols = [
    'wm_num_active_threads', 'recent_last_gesture_px', 'wm_cumulative_reads',
    'wm_cumulative_opened', 'wm_situational_steps', 'step_index',
    'model_latency_ms', 'tool_execution_ms', 'cognitive_latency_ratio',
    'context_action_velocity', 'context_elapsed_seconds', 'reason_length',
    'num_dimension_evidence', 'step_delta_sec'
]

categorical_cols = [
    'intent', 'surface', 'resolved_tool', 'verified',
    'wm_has_novelty_warning', 'recent_last_gesture_pace'
]

target_col = 'dataset_type'

print("\n" + "="*80)
print("1. NUMERIC VỚI NUMERIC: TƯƠNG QUAN SPEARMAN & PEARSON")
print("="*80)

# Điền tạm hoặc lọc NA cho tương quan
corr_spearman = df[numeric_cols].corr(method='spearman')
corr_pearson = df[numeric_cols].corr(method='pearson')

# Trích xuất top 10 cặp tương quan Spearman mạnh nhất (loại bỏ đường chéo)
corr_pairs = []
for i in range(len(numeric_cols)):
    for j in range(i+1, len(numeric_cols)):
        c1, c2 = numeric_cols[i], numeric_cols[j]
        val_s = corr_spearman.loc[c1, c2]
        val_p = corr_pearson.loc[c1, c2]
        if not np.isnan(val_s):
            corr_pairs.append((c1, c2, val_s, val_p))

corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
df_corr_top = pd.DataFrame(corr_pairs[:12], columns=['Biến 1', 'Biến 2', 'Spearman_rho', 'Pearson_r'])
print(df_corr_top.to_string(index=False))

print("\n" + "="*80)
print("2. CATEGORICAL VỚI NUMERIC: KRUSKAL-WALLIS & SO SÁNH MEDIAN THEO NHÓM")
print("="*80)

# Khảo sát từng biến numeric theo categorical (ví dụ: surface, intent, dataset_type)
cat_num_results = []
for n_col in ['wm_num_active_threads', 'recent_last_gesture_px', 'wm_cumulative_reads', 'context_action_velocity', 'reason_length']:
    # Theo dataset_type
    p_vals = df[df[target_col] == 'persona'][n_col].dropna()
    np_vals = df[df[target_col] == 'no_persona'][n_col].dropna()
    if len(p_vals) > 0 and len(np_vals) > 0:
        stat_u, p_u = stats.mannwhitneyu(p_vals, np_vals, alternative='two-sided')
        # Rank-biserial correlation as effect size
        n1, n2 = len(p_vals), len(np_vals)
        r_biserial = 1 - (2 * stat_u) / (n1 * n2)
        cat_num_results.append({
            'Categorical': 'dataset_type',
            'Numeric': n_col,
            'Persona_Med': p_vals.median(),
            'NoPersona_Med': np_vals.median(),
            'Test': 'Mann-Whitney U',
            'p_value': p_u,
            'Effect_Size_r': round(r_biserial, 3)
        })

df_cat_num = pd.DataFrame(cat_num_results)
print(df_cat_num.to_string(index=False))

print("\n" + "="*80)
print("3. CATEGORICAL VỚI CATEGORICAL: CHI-SQUARE & CRAMÉR'S V")
print("="*80)

def cramers_v(contingency_table):
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    r, k = contingency_table.shape
    return np.sqrt(chi2 / (n * (min(r, k) - 1))) if min(r, k) > 1 and n > 0 else 0

cat_cat_results = []
for c_col in categorical_cols:
    ct = pd.crosstab(df[c_col], df[target_col])
    if ct.shape[0] > 1 and ct.shape[1] > 1:
        chi2, p_val, dof, _ = stats.chi2_contingency(ct)
        v = cramers_v(ct)
        cat_cat_results.append({
            'Categorical_1': c_col,
            'Categorical_2': target_col,
            'Chi2': round(chi2, 2),
            'dof': dof,
            'p_value': p_val,
            'Cramers_V': round(v, 3)
        })

df_cat_cat = pd.DataFrame(cat_cat_results).sort_values(by='Cramers_V', ascending=False)
print(df_cat_cat.to_string(index=False))

print("\n" + "="*80)
print("4. BIẾN VỚI NHÃN (MUTUAL INFORMATION VÀ TÍNH PHÂN TÁCH LỚP)")
print("="*80)

# Chuẩn bị dữ liệu cho Mutual Information
# Mã hóa target
y = (df[target_col] == 'persona').astype(int)

# Numeric features for MI
X_num = df[numeric_cols].fillna(df[numeric_cols].median())
mi_num = mutual_info_classif(X_num, y, random_state=42)

mi_results = []
for col, score in zip(numeric_cols, mi_num):
    mi_results.append({'Feature': col, 'Type': 'Numeric', 'Mutual_Information': round(score, 4)})

# Categorical features for MI (dummy encoded)
for c_col in categorical_cols:
    X_cat = pd.get_dummies(df[c_col].fillna('Missing'), drop_first=True)
    if not X_cat.empty:
        mi_cat = mutual_info_classif(X_cat, y, discrete_features=True, random_state=42)
        score = mi_cat.mean() # trung bình các dummy
        mi_results.append({'Feature': c_col, 'Type': 'Categorical', 'Mutual_Information': round(score, 4)})

df_mi = pd.DataFrame(mi_results).sort_values(by='Mutual_Information', ascending=False)
print(df_mi.head(10).to_string(index=False))

print("\n" + "="*80)
print("5. ĐA BIẾN: PCA (PHÂN TÁCH CỤM TRÊN KHÔNG GIAN NHẬN THỨC)")
print("="*80)

pca_cols = ['wm_num_active_threads', 'recent_last_gesture_px', 'wm_cumulative_reads', 'wm_cumulative_opened', 'wm_situational_steps', 'reason_length']
X_pca = df[pca_cols].fillna(df[pca_cols].median())
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_pca)

pca = PCA(n_components=3)
X_pca_trans = pca.fit_transform(X_scaled)
print(f"PCA Explained Variance Ratio: PC1={pca.explained_variance_ratio_[0]:.3f}, PC2={pca.explained_variance_ratio_[1]:.3f}, PC3={pca.explained_variance_ratio_[2]:.3f}")
print(f"Tổng phương sai tích lũy giải thích: {pca.explained_variance_ratio_.sum()*100:.1f}%")

# Loading của từng biến vào PC1, PC2
df_loadings = pd.DataFrame(pca.components_.T, index=pca_cols, columns=['PC1', 'PC2', 'PC3'])
print("\nPCA Component Loadings:")
print(df_loadings.round(3).to_string())

print("\n" + "="*80)
print("6. HIỆU ỨNG TƯƠNG TÁC (INTERACTION EFFECTS)")
print("="*80)
# Kiểm tra tương tác: surface * dataset_type lên wm_num_active_threads
print("Trung bình wm_num_active_threads theo (surface x dataset_type):")
print(pd.crosstab(df['surface'], df[target_col], values=df['wm_num_active_threads'], aggfunc='mean').round(2))

print("\nTrung bình context_action_velocity theo (surface x dataset_type):")
print(pd.crosstab(df['surface'], df[target_col], values=df['context_action_velocity'], aggfunc='mean').round(2))
