import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, dendrogram, cophenet, fcluster
from scipy.spatial.distance import pdist

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load data
with open('data/original_facebook_persona.json', 'r', encoding='utf-8') as f:
    personas = json.load(f)

# 2. Xây dựng ma trận đặc trưng Profile
pace_map = {'slow': 1, 'balanced': 2, 'quick': 3}
att_map = {'Very short': 1, 'Short': 2, 'medium': 3, 'Long': 4, 'Very long': 5}
depth_map = {'skim': 1, 'selective': 2}
freq_map = {'Rarely': 1, 'Monthly': 2, 'Weekly': 3, 'Daily': 4}
surf_map = {'feed': 0, 'mixed': 1}
energy_map = {'Low': 1, 'medium': 2}
rest_map = {'continuous': 1, 'occasional': 2, 'periodic': 3}

profile_records = []
for p in personas:
    p_id = p.get('persona_id') or p.get('id')
    fb = p.get('facebook_behavior_profile', {})
    beh = fb.get('facebookBehavior', {})
    usage = fb.get('usage', {})
    
    profile_records.append({
        'persona_id': p_id,
        'Pace': pace_map.get(beh.get('pace'), 2),
        'Attention_Span': att_map.get(usage.get('attention'), 3),
        'Reading_Depth': depth_map.get(beh.get('readingDepth'), 2),
        'FB_Frequency': freq_map.get(usage.get('facebookFrequency'), 2),
        'Mixed_Surface': surf_map.get(beh.get('preferredSurface'), 0),
        'Energy_Level': energy_map.get(usage.get('energy'), 2),
        'Rest_Style': rest_map.get(beh.get('restStyle'), 2)
    })

df_prof = pd.DataFrame(profile_records).set_index('persona_id')

print("="*90)
print("1. MA TRẬN TƯƠNG QUAN PEARSON GIỮA CÁC THUỘC TÍNH PROFILE")
print("="*90)
corr_matrix = df_prof.corr().round(3)
print(corr_matrix.to_string())

print("\nCác cặp thuộc tính có tương quan mạnh nhất (|r| >= 0.70):")
pairs = []
for i in range(len(corr_matrix.columns)):
    for j in range(i+1, len(corr_matrix.columns)):
        c1 = corr_matrix.columns[i]
        c2 = corr_matrix.columns[j]
        r = corr_matrix.iloc[i, j]
        if abs(r) >= 0.70:
            pairs.append((c1, c2, r))

pairs_sorted = sorted(pairs, key=lambda x: abs(x[2]), reverse=True)
for c1, c2, r in pairs_sorted:
    print(f"  * {c1} <---> {c2}: r = {r:+.3f}")

print("\n" + "="*90)
print("2. PHÂN TÍCH THÀNH PHẦN CHÍNH (PCA) TRÊN HỒ SƠ PROFILE")
print("="*90)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_prof)

pca = PCA()
X_pca = pca.fit_transform(X_scaled)

var_exp = pca.explained_variance_ratio_
cum_var = np.cumsum(var_exp)

pca_summary = pd.DataFrame({
    'Thành phần': [f'PC{i+1}' for i in range(len(var_exp))],
    'Eigenvalue': pca.explained_variance_.round(3),
    'Tỷ lệ Phương sai (%)': (var_exp * 100).round(2),
    'Phương sai Tích lũy (%)': (cum_var * 100).round(2)
})
print(pca_summary.to_string(index=False))

# Loadings (Hệ số tải nhân tố)
loadings = pd.DataFrame(
    pca.components_.T * np.sqrt(pca.explained_variance_),
    columns=[f'PC{i+1}' for i in range(pca.n_components_)],
    index=df_prof.columns
)
print("\nHệ số tải (Factor Loadings) của các thuộc tính trên PC1 và PC2:")
print(loadings[['PC1', 'PC2']].round(3).to_string())

print("\n" + "="*90)
print("3. TỌA ĐỘ VÀ PHÂN CỤM PHÂN CẤP (HIERARCHICAL CLUSTERING - WARD LINKAGE)")
print("="*90)
coords = pd.DataFrame(X_pca[:, :2], columns=['PC1', 'PC2'], index=df_prof.index)

# Tính khoảng cách Euclidean trên không gian chuẩn hóa
dist_matrix = pdist(X_scaled, metric='euclidean')
Z = linkage(dist_matrix, method='ward')
coph_corr, _ = cophenet(Z, dist_matrix)
print(f"Hệ số tương quan Cophenetic của cây phân cấp: r = {coph_corr:.4f} (Độ tin cậy cấu trúc cụm rất cao)")

# Cắt thành 3 cụm tự động
clusters = fcluster(Z, t=3, criterion='maxclust')
coords['Cluster_Ward'] = clusters
print("\nTọa độ của 6 Persona trên không gian PC1 - PC2 và Cụm được gán:")
print(coords.round(3).to_string())

print("\nĐặc trưng số học trọng tâm (Centroids) của từng Cụm (Giá trị trung bình gốc):")
df_prof_clusters = df_prof.copy()
df_prof_clusters['Cluster'] = clusters
cluster_profile = df_prof_clusters.groupby('Cluster').mean().round(2)
print(cluster_profile.to_string())

print("\nPhân bổ thành viên từng cụm:")
for c_id in sorted(df_prof_clusters['Cluster'].unique()):
    members = df_prof_clusters[df_prof_clusters['Cluster'] == c_id].index.tolist()
    print(f"  - Cụm {c_id}: {members}")
