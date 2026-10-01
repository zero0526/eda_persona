import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import Counter
import pandas as pd

p_dir = Path('data/action_logs')
np_dir = Path('data/no_persona_Action')

def get_stats(directory):
    step_dims = Counter()
    wm_dims = Counter()
    wm_sources = Counter()
    total_steps = 0
    total_threads = 0
    
    for f in sorted(directory.glob('benchmark_eda_*.json')):
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
        ep = data if isinstance(data, dict) else data[0]
        steps = ep.get('step_records', [])
        total_steps += len(steps)
        for s in steps:
            for d in (s.get('dimension_evidence') or []):
                step_dims[(d.get('source'), d.get('dimension'))] += 1
            ctx = s.get('session_context') or {}
            wm = ctx.get('working_memory') or {}
            threads = wm.get('active_threads') or []
            total_threads += len(threads)
            for t in threads:
                for ev in (t.get('evidence') or []):
                    if isinstance(ev, str) and '=' in ev and ':' in ev:
                        pref = ev.split('=', 1)[0]
                        src, dim = pref.split(':', 1)
                        wm_sources[src] += 1
                        wm_dims[(src, dim)] += 1
    return total_steps, total_threads, step_dims, wm_sources, wm_dims

p_steps, p_threads, p_step_dims, p_wm_src, p_wm_dims = get_stats(p_dir)
np_steps, np_threads, np_step_dims, np_wm_src, np_wm_dims = get_stats(np_dir)

print(f"PERSONA: steps={p_steps}, threads={p_threads}, wm_evidences={sum(p_wm_src.values())}, step_dims={sum(p_step_dims.values())}")
print(f"NO PERSONA: steps={np_steps}, threads={np_threads}, wm_evidences={sum(np_wm_src.values())}, step_dims={sum(np_step_dims.values())}")

print(f"\nPERSONA - Avg threads/step: {p_threads/p_steps:.2f}, Avg wm_evidences/step: {sum(p_wm_src.values())/p_steps:.2f}")
print(f"NO PERSONA - Avg threads/step: {np_threads/np_steps:.2f}, Avg wm_evidences/step: {sum(np_wm_src.values())/np_steps:.2f}")

print("\n--- NO PERSONA DIMENSIONS IN WM ---")
for (src, dim), c in np_wm_dims.most_common():
    print(f"  {dim:30s}: {c:3d} ({c/sum(np_wm_dims.values())*100:4.1f}%)")

print("\n--- PERSONA TOP SOURCES IN WM ---")
for src, c in p_wm_src.most_common():
    print(f"  {src:20s}: {c:4d} ({c/sum(p_wm_src.values())*100:4.1f}%)")

print("\n--- PERSONA TOP DIMENSIONS IN WM ---")
for (src, dim), c in p_wm_dims.most_common(12):
    print(f"  {src}:{dim:25s}: {c:4d} ({c/sum(p_wm_dims.values())*100:4.1f}%)")
