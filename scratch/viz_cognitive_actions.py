import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Ensure utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Ensure font for Vietnamese
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Segoe UI', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

p_dir = Path('data/action_logs')
np_dir = Path('data/no_persona_Action')

def map_to_macro_cat(dim_name, src=''):
    dim = (dim_name or '').lower()
    if dim in ['reading_vs_watching', 'detail_orientation', 'content_consumption_format',
               'readingdepth', 'reading_depth', 'content', 'post_content', 'feed_content']:
        return 'Tiêu thụ nội dung\n(Consumption)'
    elif dim in ['social_engagement_style', 'emotional_expressiveness',
                 'interactionstyle', 'interaction_style', 'personality', 'interaction']:
        return 'Tương tác xã hội\n(Social / React)'
    elif dim in ['curiosity', 'query_complexity',
                 'discoverystyle', 'discovery_style', 'interest', 'searched_topics', 'exploration_state']:
        return 'Khám phá & Tìm kiếm\n(Exploration)'
    elif dim in ['attention_span', 'decision_speed', 'novelty_vs_familiarity',
                 'pace', 'behavior', 'session', 'time_remaining', 'context']:
        return 'Nhịp độ & Điều tiết\n(Pacing & Control)'
    elif dim == 'none':
        return 'Không neo nhận thức\n(None / Baseline)'
    else:
        return 'Khác / Thị giác\n(Other)'

def group_intent(intent):
    if intent in ['scroll', 'scroll_comments']:
        return 'scroll'
    elif intent in ['read', 'expand']:
        return 'read/expand'
    elif intent in ['react', 'like_page', 'share']:
        return 'react/engage'
    elif intent in ['search']:
        return 'search'
    elif intent in ['open', 'open_comments', 'open_reels']:
        return 'open/drill-down'
    elif intent in ['back', 'close', 'home']:
        return 'navigate/close'
    elif intent in ['observe']:
        return 'observe'
    return 'other'

def extract_macro_records(directory, group_name):
    records = []
    for f in sorted(directory.glob('benchmark_eda_*.json')):
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
        ep = data if isinstance(data, dict) else data[0]
        ep_id = ep.get('episode_id')
        for step in ep.get('step_records', []):
            intent = step.get('intent')
            tool = step.get('resolved_tool')
            step_idx = step.get('step_index')
            dim_evidence = step.get('dimension_evidence') or []
            
            if not dim_evidence:
                records.append({
                    'group': group_name,
                    'episode_id': ep_id,
                    'step_index': step_idx,
                    'intent': intent,
                    'tool': tool,
                    'raw_dim': 'none',
                    'macro_cat': 'Không neo nhận thức\n(None / Baseline)'
                })
            else:
                for item in dim_evidence:
                    if isinstance(item, dict):
                        dim = item.get('dimension')
                        src = item.get('source')
                        records.append({
                            'group': group_name,
                            'episode_id': ep_id,
                            'step_index': step_idx,
                            'intent': intent,
                            'tool': tool,
                            'raw_dim': dim,
                            'macro_cat': map_to_macro_cat(dim, src)
                        })
    return pd.DataFrame(records)

df_p = extract_macro_records(p_dir, 'Persona')
df_np = extract_macro_records(np_dir, 'No-Persona')

df_p['action_group'] = df_p['intent'].apply(group_intent)
df_np['action_group'] = df_np['intent'].apply(group_intent)

df_all = pd.concat([df_p, df_np], ignore_index=True)

core_cats = [
    'Tiêu thụ nội dung\n(Consumption)',
    'Tương tác xã hội\n(Social / React)',
    'Khám phá & Tìm kiếm\n(Exploration)',
    'Nhịp độ & Điều tiết\n(Pacing & Control)'
]

df_core = df_all[df_all['macro_cat'].isin(core_cats)].copy()

pct = pd.crosstab([df_core['group'], df_core['macro_cat']], df_core['action_group'], normalize='index') * 100

out_table_path = Path("output/tables/step4_cognitive_to_action_distribution.csv")
out_table_path.parent.mkdir(parents=True, exist_ok=True)
pct.round(2).to_csv(out_table_path, encoding="utf-8-sig")
print("Saved crosstab to:", out_table_path)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), sharey=True)

key_actions = ['scroll', 'read/expand', 'react/engage', 'search', 'open/drill-down', 'navigate/close']
palette = {
    'scroll': '#3b82f6',         # blue
    'read/expand': '#10b981',     # green
    'react/engage': '#ec4899',    # rose
    'search': '#f59e0b',          # amber
    'open/drill-down': '#8b5cf6', # purple
    'navigate/close': '#64748b',  # slate
    'other': '#cbd5e1'
}

pct_np_sub = pct.loc['No-Persona'].reindex(core_cats).fillna(0)
pct_p_sub = pct.loc['Persona'].reindex(core_cats).fillna(0)

for col in key_actions:
    if col not in pct_np_sub.columns:
        pct_np_sub[col] = 0.0
    if col not in pct_p_sub.columns:
        pct_p_sub[col] = 0.0

pct_np_sub = pct_np_sub[key_actions]
pct_p_sub = pct_p_sub[key_actions]

pct_np_sub.plot(kind='barh', stacked=True, ax=ax1, color=[palette[c] for c in key_actions], edgecolor='white', linewidth=0.8)
ax1.set_title("No-Persona (Đối Chứng: Heuristics Trung Tính)", fontsize=12, fontweight='bold', pad=10)
ax1.set_xlabel("Phân bổ hành vi (%)", fontsize=11, fontweight='bold')
ax1.set_xlim(0, 100)
ax1.grid(axis='x', linestyle='--', alpha=0.5)

pct_p_sub.plot(kind='barh', stacked=True, ax=ax2, color=[palette[c] for c in key_actions], edgecolor='white', linewidth=0.8)
ax2.set_title("Persona (Bản Sắc: Hồ Sơ Cá Nhân Hóa)", fontsize=12, fontweight='bold', pad=10)
ax2.set_xlabel("Phân bổ hành vi (%)", fontsize=11, fontweight='bold')
ax2.set_xlim(0, 100)
ax2.grid(axis='x', linestyle='--', alpha=0.5)

ax1.legend().remove()
handles, labels = ax2.get_legend_handles_labels()
ax2.legend(handles, labels, loc='upper center', bbox_to_anchor=(-0.05, -0.15), ncol=6, frameon=True, fontsize=10)

plt.suptitle("SO SÁNH PHÂN BỔ HÀNH VI (SCROLL, REACT, READ...) THEO CHIỀU NHẬN THỨC", fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()

out_fig_path = Path("output/figures/step4_cognitive_to_action_distribution.png")
out_fig_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_fig_path, dpi=300, bbox_inches='tight')
plt.close()
print("Saved figure to:", out_fig_path)
