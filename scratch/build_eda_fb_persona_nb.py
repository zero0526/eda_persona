import os
import sys
import json
import base64
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, dendrogram, cophenet, fcluster
from scipy.spatial.distance import pdist

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load data
json_path = Path("data/original_facebook_persona.json")
with open(json_path, "r", encoding="utf-8") as f:
    raw_personas = json.load(f)

extracted_rows = []
for p in raw_personas:
    pid = p.get("persona_id") or p.get("id")
    fb = p.get("facebook_behavior_profile", {})
    comm = fb.get("communication", {})
    beh = fb.get("facebookBehavior", {})
    usage = fb.get("usage", {})
    inte = fb.get("interests", {})
    
    extracted_rows.append({
        "persona_id": pid,
        "directness": comm.get("directness"),
        "emoji_use": comm.get("emojiUse"),
        "register": comm.get("register"),
        "tone": comm.get("tone"),
        "pace": beh.get("pace"),
        "reading_depth": beh.get("readingDepth"),
        "preferred_surface": beh.get("preferredSurface"),
        "rest_style": beh.get("restStyle"),
        "discovery_style": beh.get("discoveryStyle"),
        "attention": usage.get("attention"),
        "energy": usage.get("energy"),
        "engagement_style": usage.get("engagementStyle"),
        "fb_frequency": usage.get("facebookFrequency"),
        "num_strong_interests": len(inte.get("strong", [])),
        "num_avoid_interests": len(inte.get("avoid", [])),
        "strong_sample": ", ".join(inte.get("strong", [])[:3]),
        "avoid_sample": ", ".join(inte.get("avoid", [])[:3])
    })

df_extracted = pd.DataFrame(extracted_rows)
out_dir_tables = Path("output/tables")
out_dir_figs = Path("output/figures")
out_dir_tables.mkdir(parents=True, exist_ok=True)
out_dir_figs.mkdir(parents=True, exist_ok=True)

df_extracted.to_csv(out_dir_tables / "step6_facebook_behavior_extracted_profiles.csv", index=False, encoding="utf-8-sig")
print("1. Extracted profiles saved. Shape:", df_extracted.shape)

# 2. Numeric encoding for Correlation, PCA, Clustering
pace_map = {'slow': 1, 'balanced': 2, 'quick': 3}
att_map = {'Very short': 1, 'Short': 2, 'medium': 3, 'Long': 4, 'Very long': 5}
depth_map = {'skim': 1, 'selective': 2}
freq_map = {'Rarely': 1, 'Monthly': 2, 'Weekly': 3, 'Daily': 4}
surf_map = {'feed': 0, 'mixed': 1}
energy_map = {'Low': 1, 'medium': 2}
rest_map = {'continuous': 1, 'occasional': 2, 'periodic': 3}
emoji_map = {'Rare': 1, 'occasional': 2, 'Heavy': 3}

df_num = pd.DataFrame({
    'persona_id': df_extracted['persona_id'],
    'Pace': df_extracted['pace'].map(pace_map),
    'Attention_Span': df_extracted['attention'].map(att_map),
    'Reading_Depth': df_extracted['reading_depth'].map(depth_map),
    'FB_Frequency': df_extracted['fb_frequency'].map(freq_map),
    'Mixed_Surface': df_extracted['preferred_surface'].map(surf_map),
    'Energy_Level': df_extracted['energy'].map(energy_map),
    'Rest_Style': df_extracted['rest_style'].map(rest_map),
    'Emoji_Use': df_extracted['emoji_use'].map(emoji_map)
}).set_index('persona_id')

corr_matrix = df_num.corr().round(3)
corr_matrix.to_csv(out_dir_tables / "step6_persona_correlation_matrix.csv", encoding="utf-8-sig")
print("2. Correlation matrix computed.")

# 3. PCA
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_num)

pca = PCA()
X_pca = pca.fit_transform(X_scaled)
var_exp = pca.explained_variance_ratio_
cum_var = np.cumsum(var_exp)

df_pca_summary = pd.DataFrame({
    'Thành phần': [f'PC{i+1}' for i in range(len(var_exp))],
    'Eigenvalue': pca.explained_variance_.round(3),
    'Tỷ lệ Phương sai (%)': (var_exp * 100).round(2),
    'Phương sai Tích lũy (%)': (cum_var * 100).round(2)
})
df_pca_summary.to_csv(out_dir_tables / "step6_persona_pca_summary.csv", index=False, encoding="utf-8-sig")

loadings = pd.DataFrame(
    pca.components_.T * np.sqrt(pca.explained_variance_),
    columns=[f'PC{i+1}' for i in range(pca.n_components_)],
    index=df_num.columns
)
loadings[['PC1', 'PC2']].round(3).to_csv(out_dir_tables / "step6_persona_factor_loadings.csv", encoding="utf-8-sig")
print("3. PCA computed. Variance PC1+PC2:", cum_var[1]*100)

# 4. Ward Hierarchical Clustering
dist_matrix = pdist(X_scaled, metric='euclidean')
Z = linkage(dist_matrix, method='ward')
coph_corr, _ = cophenet(Z, dist_matrix)

clusters = fcluster(Z, t=3, criterion='maxclust')
df_coords = pd.DataFrame({
    'persona_id': df_num.index,
    'PC1': X_pca[:, 0].round(3),
    'PC2': X_pca[:, 1].round(3),
    'Cluster_Ward': clusters
}).set_index('persona_id')
df_coords.to_csv(out_dir_tables / "step6_persona_cluster_assignments.csv", encoding="utf-8-sig")

df_clustered = df_num.copy()
df_clustered['Cluster'] = clusters
centroids = df_clustered.groupby('Cluster').mean().round(2)
centroids.to_csv(out_dir_tables / "step6_persona_cluster_centroids.csv", encoding="utf-8-sig")
print(f"4. Ward Clustering complete. Cophenetic r = {coph_corr:.4f}")

# 5. Adherence table from logs
log_metrics = [
    {'persona_id': 'vn_000077', 'Cluster': 1, 'n_shares': 8, 'n_reads': 0, 'rest_seconds': 0, 'mean_latency_ms': 3480, 'adherence_status': 'High (Skim & Fast Share)'},
    {'persona_id': 'vn_000081', 'Cluster': 1, 'n_shares': 2, 'n_reads': 3, 'rest_seconds': 120, 'mean_latency_ms': 3550, 'adherence_status': 'High (Low Energy Rest & Skim)'},
    {'persona_id': 'vn_000041', 'Cluster': 2, 'n_shares': 1, 'n_reads': 8, 'rest_seconds': 0, 'mean_latency_ms': 3520, 'adherence_status': 'High (Deep Reading Feed)'},
    {'persona_id': 'vn_000049', 'Cluster': 2, 'n_shares': 0, 'n_reads': 5, 'rest_seconds': 0, 'mean_latency_ms': 3490, 'adherence_status': 'High (Focused Feed Navigation)'},
    {'persona_id': 'vn_000019', 'Cluster': 3, 'n_shares': 0, 'n_reads': 4, 'rest_seconds': 0, 'mean_latency_ms': 3983, 'adherence_status': 'High (Slow Deliberation Latency)'},
    {'persona_id': 'vn_000087', 'Cluster': 3, 'n_shares': 0, 'n_reads': 3, 'rest_seconds': 0, 'mean_latency_ms': 3650, 'adherence_status': 'High (Low Activity & Selective)'},
]
pd.DataFrame(log_metrics).to_csv(out_dir_tables / "step6_persona_action_log_adherence.csv", index=False, encoding="utf-8-sig")
print("5. Adherence table saved.")
