import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import silhouette_score

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader
loader = ActionLoader()
df = loader.to_unified_actions_dataframe()

focused_intents = ['read', 'comment', 'react', 'expand', 'search', 'share']
sub = df[df['intent'].isin(focused_intents)].copy()

top_dims = sub['primary_dimension'].value_counts()
valid_dims = top_dims[top_dims >= 2].index.tolist()

# Feature matrix: tỷ lệ xuất hiện theo từng Persona và từng Intent
ct_pers = pd.crosstab(sub['primary_dimension'], sub['persona_id'], normalize='index').loc[valid_dims]
ct_act = pd.crosstab(sub['primary_dimension'], sub['intent'], normalize='index').loc[valid_dims]
feature_mat = pd.concat([ct_pers, ct_act], axis=1)

print('Feature matrix shape:', feature_mat.shape)

# Tìm k tối ưu bằng Silhouette Score
Z = linkage(feature_mat, method='ward')
best_k = 2
best_score = -1
for k in range(2, 8):
    labels = fcluster(Z, t=k, criterion='maxclust')
    score = silhouette_score(feature_mat, labels)
    print(f'k={k}: Silhouette Score = {score:.4f}')
    if score > best_score:
        best_score = score
        best_k = k

print(f'\n-> k tối ưu toán học: {best_k} (Silhouette = {best_score:.4f})')

# In kết quả phân cụm với k=best_k và k=4
for k_val in [best_k, 4]:
    print(f"\n==========================================")
    print(f"=== KẾT QUẢ PHÂN CỤM DỮ LIỆU ĐỊNH LƯỢNG (k={k_val}) ===")
    labels = fcluster(Z, t=k_val, criterion='maxclust')
    res = pd.DataFrame({
        'dimension': valid_dims,
        'count': [top_dims[d] for d in valid_dims],
        'cluster': labels
    })
    for c in sorted(res['cluster'].unique()):
        dims_in_c = res[res['cluster'] == c]
        tot = dims_in_c['count'].sum()
        pct = tot / len(sub) * 100
        print(f"\n--- Cụm {c} (Tổng {tot} lượt, chiếm {pct:.1f}%): ---")
        for _, r in dims_in_c.iterrows():
            print(f"   * {r['dimension']}: {r['count']} lượt")
