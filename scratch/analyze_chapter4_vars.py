import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import Counter, defaultdict
import pandas as pd
import numpy as np

p_dir = Path('data/action_logs')
np_dir = Path('data/no_persona_Action')

def analyze_chapter4_candidates(directory, group_name):
    episodes = []
    steps_list = []
    
    for f in sorted(directory.glob('benchmark_eda_*.json')):
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
        ep = data if isinstance(data, dict) else data[0]
        ep_id = ep.get('episode_id')
        steps = ep.get('step_records', [])
        
        last_step = steps[-1] if steps else {}
        last_ctx = (last_step.get('session_context') or {})
        last_wm = last_ctx.get('working_memory') or {}
        
        # Termination analysis
        end_tool = last_step.get('resolved_tool') or last_step.get('tool')
        end_reason = last_step.get('reason', '')
        elapsed = last_ctx.get('elapsed_seconds', 0)
        planned = last_ctx.get('planned_active_seconds', 600)
        remaining = last_ctx.get('remaining_seconds', 0)
        overtime = (elapsed - planned) if elapsed and planned else 0
        
        # Categorize termination cause
        cause = 'Timeout / Hết thời gian'
        if 'kẹt' in end_reason.lower() or 'lỗi' in end_reason.lower() or 'không còn affordance' in end_reason.lower():
            cause = 'Bế tắc giao diện (UI Deadlock) + Timeout'
        elif end_tool != 'end_episode':
            cause = 'Cưỡng bức kết thúc (Forced Step Cutoff)'
        elif 'hứng thú giảm' in end_reason.lower() or 'hoàn thành' in end_reason.lower():
            cause = 'Thỏa mãn mục tiêu & Hết thời lượng'
            
        reads = len(last_wm.get('read_posts') or [])
        searches = len(last_wm.get('searched_topics') or [])
        opened = len(last_wm.get('opened_sources') or [])
        
        episodes.append({
            'group': group_name,
            'episode_id': ep_id,
            'file': f.name,
            'total_steps': len(steps),
            'elapsed_seconds': elapsed,
            'planned_seconds': planned,
            'overtime_seconds': overtime,
            'end_tool': end_tool,
            'termination_cause': cause,
            'reads_at_exit': reads,
            'searches_at_exit': searches,
            'opened_at_exit': opened,
            'end_reason': end_reason
        })
        
        for s in steps:
            steps_list.append({
                'group': group_name,
                'episode_id': ep_id,
                'surface': s.get('surface'),
                'intent': s.get('intent'),
                'resolved_tool': s.get('resolved_tool'),
                'reaction': s.get('reaction'),
                'verified': s.get('verified'),
                'tool_execution_ms': s.get('tool_execution_ms')
            })
            
    return pd.DataFrame(episodes), pd.DataFrame(steps_list)

df_p_ep, df_p_st = analyze_chapter4_candidates(p_dir, 'Persona')
df_np_ep, df_np_st = analyze_chapter4_candidates(np_dir, 'No-Persona')

print("=== EPISODE-LEVEL TERMINATION & EXIT PROFILE ===")
df_ep_all = pd.concat([df_p_ep, df_np_ep], ignore_index=True)
print(df_ep_all[['group', 'file', 'total_steps', 'elapsed_seconds', 'overtime_seconds', 'end_tool', 'termination_cause', 'reads_at_exit', 'searches_at_exit']])

print("\n=== TERMINATION CAUSE DISTRIBUTION ===")
print(pd.crosstab(df_ep_all['group'], df_ep_all['termination_cause'], margins=True))

print("\n=== SURFACE DISTRIBUTION (CATEGORICAL UNIVARIATE) ===")
df_st_all = pd.concat([df_p_st, df_np_st], ignore_index=True)
ct_surf = pd.crosstab(df_st_all['group'], df_st_all['surface'], normalize='index') * 100
print(ct_surf.round(2))

print("\n=== REACTION DISTRIBUTION (CATEGORICAL UNIVARIATE) ===")
ct_react = pd.crosstab(df_st_all['group'], df_st_all['reaction'].fillna('none'), normalize='index') * 100
print(ct_react.round(2))

print("\n=== VERIFIED ACTION RATIO (CATEGORICAL UNIVARIATE) ===")
ct_ver = pd.crosstab(df_st_all['group'], df_st_all['verified'], normalize='index') * 100
print(ct_ver.round(2))
