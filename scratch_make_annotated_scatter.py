import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

PERSONA_PALETTE = {
    'vn_fb_001': '#1f77b4',
    'vn_fb_002': '#ff7f0e',
    'vn_fb_003': '#2ca02c',
    'vn_fb_004': '#d62728',
    'vn_fb_005': '#9467bd',
    'vn_fb_006': '#8c564b'
}

curiosity_scale = {'Rất thấp': 1, 'Thấp': 2, 'Trung bình': 3, 'Cao': 4, 'Rất cao': 5}
persona_curiosity_map = {}
with open('data/selected_6_facebook_personas_description.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        p = json.loads(line)
        pid = p['persona_id']
        c_text = p['attributes'].get('Mức độ muốn khám phá, đặt câu hỏi và tìm hiểu những điều mới.', 'Trung bình')
        persona_curiosity_map[pid] = {
            'curiosity_text': c_text,
            'curiosity_score': curiosity_scale.get(c_text, 3)
        }

wm_records = []
for pid, h in histories.items():
    c_info = persona_curiosity_map.get(pid, {'curiosity_text': 'Trung bình', 'curiosity_score': 3})
    for s in h.sessions:
        wm = s.working_memory
        if wm:
            s_actions = df_actions[df_actions['session_id'] == s.session_id]
            total_act = len(s_actions)
            curiosity_count = len(s_actions[s_actions['primary_dimension'] == 'curiosity'])
            curiosity_ratio = curiosity_count / total_act if total_act > 0 else 0.0
            
            wm_records.append({
                'persona_id': pid,
                'session_id': s.session_id[:8],
                'curiosity_score': c_info['curiosity_score'],
                'curiosity_actions': curiosity_count,
                'curiosity_ratio': curiosity_ratio,
                'situational_steps': wm.novelty.situational_steps if wm.novelty else 0,
                'active_threads': len(wm.active_threads) if wm.active_threads else 0,
                'read_posts': len(wm.read_posts) if wm.read_posts else 0,
                'memory_deltas': len(wm.memory_deltas) if wm.memory_deltas else 0,
                'total_actions': total_act
            })

df_wm = pd.DataFrame(wm_records)

# Create Storytelling Scatter Plot prototype
plt.figure(figsize=(9.5, 7.5), dpi=120)
ax = plt.subplot(1, 1, 1)

# 1. Shaded Zones
# Zone Safe/Disciplined (Y <= 15)
ax.axhspan(-2, 16, color='#e8f5e9', alpha=0.5, zorder=0)
ax.text(0.1, 1.5, 'VÙNG KỶ LUẬT / KHÁM PHÁ ĐÚNG SỞ THÍCH\n(Situational Steps ≤ 15)', 
        fontsize=9, color='#2e7d32', fontweight='bold', alpha=0.85)

# Zone Rabbit Hole (Y >= 25)
ax.axhspan(25, 40, color='#ffebee', alpha=0.5, zorder=0)
ax.text(0.1, 26, 'VÙNG HANG THỎ NHẬN THỨC (RABBIT HOLE)\n(High Drift Zone: Situational Steps ≥ 25)', 
        fontsize=9, color='#c62828', fontweight='bold', alpha=0.85)

# 2. Ceiling Threshold Line
ax.axhline(35, color='#d32f2f', linestyle=':', linewidth=1.8, zorder=1)
ax.text(3.5, 36.5, '⚡ Ngưỡng Kích Hoạt Cảnh Báo novelty_warning (~35 bước)', 
        fontsize=8.5, color='#b71c1c', fontweight='bold', 
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffebee', edgecolor='#d32f2f', alpha=0.9))

# 3. Scatter points with jitter
np.random.seed(42)
jitter_x = np.random.uniform(-0.12, 0.12, size=len(df_wm))
jitter_y = np.random.uniform(-0.4, 0.4, size=len(df_wm))

for pid, group in df_wm.groupby('persona_id'):
    p_color = PERSONA_PALETTE.get(pid, '#333333')
    idx = group.index
    ax.scatter(
        group['read_posts'] + jitter_x[idx], 
        group['situational_steps'] + jitter_y[idx],
        color=p_color, label=pid, s=130, alpha=0.9, edgecolors='black', linewidth=1.0, zorder=3
    )

# 4. Trendline
r_val, p_val = stats.pearsonr(df_wm['read_posts'], df_wm['situational_steps'])
slope, intercept, _, _, _ = stats.linregress(df_wm['read_posts'], df_wm['situational_steps'])
x_vals = np.array([0, 6.2])
ax.plot(x_vals, intercept + slope * x_vals, color='#b71c1c', linestyle='--', linewidth=2, zorder=2,
        label=f'Hồi quy tuyến tính (r = {r_val:.2f})')

# 5. Callout Annotations
# Callout 1: Point vn_fb_006 at (6, 0)
ax.annotate('vn_fb_006: Đọc 6 bài BĐS\nnhưng 0 bước sa đà\n(Khám phá đúng sở thích)',
            xy=(5.9, 0), xytext=(4.2, 5),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6),
            fontsize=8.5, bbox=dict(boxstyle='round,pad=0.4', facecolor='#fffde7', edgecolor='#fbc02d', alpha=0.95))

# Callout 2: Outlier vn_fb_004 at (1, 31)
ax.annotate('vn_fb_004: Sa đà qua Video\n(31 bước quẹt Reels ngoài lề,\nkhông đọc văn bản)',
            xy=(0.95, 31), xytext=(1.5, 32),
            arrowprops=dict(facecolor='#d32f2f', shrink=0.08, width=1, headwidth=6),
            fontsize=8.5, bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffebee', edgecolor='#ef5350', alpha=0.95))

# Callout 3: Group vn_fb_004 at (0, 0)
ax.annotate('vn_fb_004: Chuyên xem Reels,\nhầu như 0 bài đọc văn bản',
            xy=(0, 0), xytext=(0.5, -4),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6),
            fontsize=8.5, bbox=dict(boxstyle='round,pad=0.4', facecolor='#f5f5f5', edgecolor='#9e9e9e', alpha=0.95))

ax.set_title('(C) Độ Sâu Đọc Bài vs Số Bước Sa Đà Tình Huống Cấp Phiên\n(Information Depth vs Cognitive Drift per Session)', 
             fontweight='bold', fontsize=13, pad=15)
ax.set_xlabel('Số Bài Viết Đã Đọc (read_posts — đơn vị: bài)', fontsize=11)
ax.set_ylabel('Số Bước Sa Đà Tình Huống (situational_steps — đơn vị: bước)', fontsize=11)
ax.set_ylim(-6, 42)
ax.set_xlim(-0.5, 6.8)
ax.grid(True, linestyle=':', alpha=0.5)
ax.legend(frameon=True, fontsize=9.5, loc='upper left')

plt.tight_layout()
plt.savefig('scratch/prototype_annotated_scatter.png', dpi=120)
print("SUCCESS: Prototype saved to scratch/prototype_annotated_scatter.png")
