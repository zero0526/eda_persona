import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path('.').resolve()))
sys.stdout.reconfigure(encoding='utf-8')

from loaders.action_loader import ActionLoader

loader = ActionLoader()
df = loader.to_unified_actions_dataframe()

FIGURES_DIR = Path("output/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Matplotlib configuration
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Liberation Sans']
plt.rcParams['axes.edgecolor'] = '#7f8c8d'
plt.rcParams['axes.linewidth'] = 1.0

PERSONA_ORDER = ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']
PERSONA_LABELS = {
    'vn_fb_001': 'vn_fb_001\n(Thiết kế đồ họa)',
    'vn_fb_002': 'vn_fb_002\n(Gia đình / Nghệ An)',
    'vn_fb_003': 'vn_fb_003\n(Bảo vệ ca đêm)',
    'vn_fb_004': 'vn_fb_004\n(Phục vụ nhà hàng)',
    'vn_fb_005': 'vn_fb_005\n(Thợ cơ khí)',
    'vn_fb_006': 'vn_fb_006\n(Gen X BĐS)',
}

# Bảng màu cố định cho từng primary_dimension chính xác từ CSDL
DIM_COLORS = {
    'curiosity': '#2980b9',                       # Xanh dương đậm
    'interest_real_estate': '#16a085',            # Xanh ngọc
    'value_tradition': '#c0392b',                 # Đỏ thẫm
    'cuisine_street_food': '#e67e22',             # Cam đậm
    'cuisine_vietnamese': '#d35400',              # Cam gạch
    'tone': '#27ae60',                            # Xanh lá
    'sport_football': '#e74c3c',                  # Đỏ tươi
    'content_consumption_format': '#f39c12',      # Vàng nghệ
    'interest_technology': '#3498db',             # Xanh biển sáng
    'social_engagement_style': '#8e44ad',         # Tím đậm
    'interest_spirituality': '#9b59b6',           # Tím nhạt
    'skepticism': '#34495e',                      # Xám đen
    'group_community_participation': '#1abc9c',   # Xanh lục sáng
    'career_role': '#2c3e50',                     # Xanh đậm
    'province': '#e84393',                        # Hồng đậm
    'writing_format': '#00cec9',                  # Xanh lam
    'value_health': '#00b894',                    # Xanh bạc hà
    'value_wealth': '#fdcb6e',                    # Vàng đất
    'interest_parenting_family_life': '#6c5ce7',  # Tím oải hương
    'emotional_expressiveness': '#fd79a8',        # Hồng phấn
    'other': '#95a5a6',                           # Xám
}

def get_dimension_breakdown(intent_name):
    sub = df[df['intent'] == intent_name]
    breakdown = {}
    for p in PERSONA_ORDER:
        sp = sub[sub['persona_id'] == p]
        n = len(sp)
        if n == 0:
            breakdown[p] = {'n': 0, 'segments': []}
        else:
            vc = sp['primary_dimension'].value_counts()
            # Lấy top segments, các mục nhỏ < 5% gom vào other nếu nhiều
            segments = []
            accum_other = 0.0
            accum_other_cnt = 0
            for dim, cnt in vc.items():
                pct = cnt / n * 100.0
                if pct >= 8.0 or len(vc) <= 3:
                    segments.append({
                        'dimension': dim,
                        'count': cnt,
                        'pct': pct,
                        'color': DIM_COLORS.get(dim, '#95a5a6')
                    })
                else:
                    accum_other += pct
                    accum_other_cnt += cnt
            if accum_other > 0:
                segments.append({
                    'dimension': 'other_dimensions',
                    'count': accum_other_cnt,
                    'pct': accum_other,
                    'color': '#95a5a6'
                })
            breakdown[p] = {'n': n, 'segments': segments}
    return breakdown

print("Tính toán dữ liệu 6 hành vi:")
for act in ['search', 'comment', 'read', 'expand', 'react', 'share']:
    bd = get_dimension_breakdown(act)
    print(f"Hành vi: {act}")
    for p in PERSONA_ORDER:
        segs = bd[p]['segments']
        seg_str = ", ".join([f"{s['dimension']} ({s['pct']:.1f}%)" for s in segs]) if segs else "0 lượt"
        print(f"  {p}: {seg_str}")
