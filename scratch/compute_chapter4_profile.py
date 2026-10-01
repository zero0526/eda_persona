import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import pandas as pd
import numpy as np

p_dir = Path('data/action_logs')
np_dir = Path('data/no_persona_Action')

def get_chapter4_univariate_tables():
    ep_rows = []
    step_rows = []
    
    for d, grp in [(p_dir, 'Persona'), (np_dir, 'No-Persona')]:
        for f in sorted(d.glob('benchmark_eda_*.json')):
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            ep = data if isinstance(data, dict) else data[0]
            ep_id = ep.get('episode_id')
            steps = ep.get('step_records', [])
            
            # Step-level extraction
            prev_ts = None
            for s in steps:
                ts = s.get('timestamp')
                # Parse timestamp diff
                delta_sec = None
                if ts and prev_ts:
                    try:
                        t1 = pd.to_datetime(ts)
                        t0 = pd.to_datetime(prev_ts)
                        delta_sec = (t1 - t0).total_seconds()
                    except:
                        pass
                prev_ts = ts
                
                step_rows.append({
                    'group': grp,
                    'episode_id': ep_id,
                    'step_index': s.get('step_index'),
                    'surface': s.get('surface'),
                    'intent': s.get('intent'),
                    'resolved_tool': s.get('resolved_tool'),
                    'reaction': s.get('reaction'),
                    'verified': s.get('verified'),
                    'tool_execution_ms': s.get('tool_execution_ms'),
                    'step_delta_sec': delta_sec
                })
                
            # Episode-level extraction
            last_step = steps[-1] if steps else {}
            last_ctx = last_step.get('session_context') or {}
            last_wm = last_ctx.get('working_memory') or {}
            end_tool = last_step.get('resolved_tool') or last_step.get('tool')
            end_reason = last_step.get('reason', '')
            elapsed = last_ctx.get('elapsed_seconds', 0)
            planned = last_ctx.get('planned_active_seconds', 600)
            overtime = elapsed - planned if elapsed and planned else 0
            
            # Cause
            if 'kẹt' in end_reason.lower() or 'lỗi' in end_reason.lower() or 'không còn affordance' in end_reason.lower():
                cause = 'Bế tắc giao diện (UI Deadlock)'
            elif end_tool != 'end_episode':
                cause = 'Cưỡng bức kết thúc (Timeout Cutoff)'
            elif 'hứng thú giảm' in end_reason.lower() or 'hoàn thành' in end_reason.lower():
                cause = 'Thỏa mãn mục tiêu & Tự dừng'
            else:
                cause = 'Hết ngân sách thời gian (Timeout 600s)'
                
            ep_rows.append({
                'group': grp,
                'episode_id': ep_id,
                'file_name': f.name,
                'total_steps': len(steps),
                'elapsed_seconds': elapsed,
                'planned_seconds': planned,
                'overtime_seconds': overtime,
                'end_tool': end_tool,
                'termination_cause': cause,
                'reads_at_exit': len(last_wm.get('read_posts') or []),
                'searches_at_exit': len(last_wm.get('searched_topics') or []),
                'opened_at_exit': len(last_wm.get('opened_sources') or []),
                'end_reason': end_reason
            })
            
    return pd.DataFrame(ep_rows), pd.DataFrame(step_rows)

df_ep, df_st = get_chapter4_univariate_tables()

# Save tables
out_dir = Path('output/tables')
out_dir.mkdir(parents=True, exist_ok=True)

df_ep.to_csv(out_dir / 'step4_termination_profile.csv', index=False, encoding='utf-8-sig')

# Print summary
print("=== EPISODE STATS BY GROUP ===")
print(df_ep.groupby('group')[['total_steps', 'elapsed_seconds', 'overtime_seconds', 'reads_at_exit', 'searches_at_exit', 'opened_at_exit']].agg(['mean', 'median', 'min', 'max']).T)

print("\n=== TERMINATION CAUSES ===")
print(pd.crosstab(df_ep['group'], df_ep['termination_cause'], margins=True))

print("\n=== STEP DELTA SECONDS (INTER-ACTION LATENCY) ===")
print(df_st.groupby('group')['step_delta_sec'].describe())

print("\n=== TOOL EXECUTION MS ===")
print(df_st.groupby('group')['tool_execution_ms'].describe())
