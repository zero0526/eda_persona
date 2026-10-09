import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.decomposition import PCA

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader
loader = ActionLoader()
df = loader.to_unified_actions_dataframe()

# Tập tương tác (N = 110)
interactions = df[df['intent'].isin(['react', 'comment', 'share'])].copy()

def get_sub_type(row):
    if row['intent'] == 'comment': return 'Comment'
    if row['intent'] == 'share': return 'Share'
    rx = str(row.get('reaction', 'LIKE')).upper()
    if 'LOVE' in rx: return 'Love'
    if 'CARE' in rx: return 'Care'
    if 'HAHA' in rx: return 'Haha'
    if 'WOW' in rx: return 'Wow'
    if 'SAD' in rx: return 'Sad'
    if 'ANGRY' in rx: return 'Angry'
    return 'Like'

interactions['sub_type'] = interactions.apply(get_sub_type, axis=1)

# Bảng chéo Contingency table: Persona vs Interaction Sub-type
ct = pd.crosstab(interactions['persona_id'], interactions['sub_type'])
print("Contingency table shape:", ct.shape)
print(ct)

# 1. Chi-square & Cramer's V
chi2, p, dof, expected = stats.chi2_contingency(ct)
n = ct.values.sum()
min_dim = min(ct.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim))
print(f"\n1. CHI-SQUARE TEST:")
print(f"   Chi2 = {chi2:.2f}, p-value = {p:.4e}, dof = {dof}")
print(f"   Cramer's V = {cramers_v:.3f}")
print(f"   Cramer's V^2 (tỷ lệ liên kết / biến thiên giải thích) = {cramers_v**2 * 100:.1f}%")

# 2. PCA trên Ma trận tỷ lệ tương tác của 6 Persona
pct_mat = pd.crosstab(interactions['persona_id'], interactions['sub_type'], normalize='index')
pca = PCA()
pca.fit(pct_mat)
print(f"\n2. PHÂN TÍCH THÀNH PHẦN CHÍNH (PCA) TRÊN VECTOR TƯƠNG TÁC 6 PERSONA:")
for i, var in enumerate(pca.explained_variance_ratio_):
    print(f"   PC{i+1}: {var*100:.1f}% (Tích lũy: {sum(pca.explained_variance_ratio_[:i+1])*100:.1f}%)")

# 3. Phân tích 3 Nhóm hình mẫu (Archetypes):
# Nhóm 1 (Đàm luận): 003, 005
# Nhóm 2 (Ấm áp): 002
# Nhóm 3 (Chuẩn mực/Giải trí): 001, 004, 006
group_map = {
    'vn_fb_003': 'Nhom_Dam_Luan',
    'vn_fb_005': 'Nhom_Dam_Luan',
    'vn_fb_002': 'Nhom_Am_Ap',
    'vn_fb_001': 'Nhom_Chuan_Muc',
    'vn_fb_004': 'Nhom_Chuan_Muc',
    'vn_fb_006': 'Nhom_Chuan_Muc'
}
interactions['group'] = interactions['persona_id'].map(group_map)
ct_group = pd.crosstab(interactions['group'], interactions['sub_type'])
chi2_g, p_g, dof_g, exp_g = stats.chi2_contingency(ct_group)
cramers_v_g = np.sqrt(chi2_g / (n * (min(ct_group.shape) - 1)))
print(f"\n3. CHI-SQUARE CHO 3 NHÓM HÌNH MẪU:")
print(f"   Chi2 = {chi2_g:.2f}, p-value = {p_g:.4e}")
print(f"   Cramer's V = {cramers_v_g:.3f}")
print(f"   Cramer's V^2 = {cramers_v_g**2 * 100:.1f}%")

# 4. Tỷ lệ tập trung của các hành vi đặc trưng:
# Trong 35 comment: 003 + 005 chiếm bao nhiêu?
cmt_share = (interactions[interactions['sub_type'] == 'Comment']['persona_id'].isin(['vn_fb_003', 'vn_fb_005'])).mean()
# Trong Love/Care: 002 chiếm bao nhiêu?
love_care_share = (interactions[interactions['sub_type'].isin(['Love', 'Care'])]['persona_id'] == 'vn_fb_002').mean()
# Trong Like: 001, 004, 006 chiếm bao nhiêu?
like_share = (interactions[interactions['sub_type'] == 'Like']['persona_id'].isin(['vn_fb_001', 'vn_fb_004', 'vn_fb_006'])).mean()

print(f"\n4. TỶ LỆ TẬP TRUNG HÀNH VI ĐẶC TRƯNG:")
print(f"   - Tỷ lệ Comment tập trung ở Nhóm Đàm luận (003, 005): {cmt_share*100:.1f}% (30/35 lượt)")
print(f"   - Tỷ lệ Love + Care tập trung ở 002: {love_care_share*100:.1f}% (7/9 lượt)")
print(f"   - Tỷ lệ Like tập trung ở Nhóm Chuẩn mực (001, 004, 006): {like_share*100:.1f}% (37/56 lượt)")
