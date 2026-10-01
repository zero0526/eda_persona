import json
import sys
from pathlib import Path
from collections import Counter

# Set utf-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

persona_dir = Path('data/action_logs')
no_persona_dir = Path('data/no_persona_Action')

def scan_evidences(directory):
    wm_evidences = []
    dim_evidences = []
    for f in sorted(directory.glob('benchmark_eda_*.json')):
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
        for ep in (data if isinstance(data, list) else [data]):
            for step in ep.get('step_records', []):
                # Check working_memory in session_context
                ctx = step.get('session_context') or {}
                wm = ctx.get('working_memory') or {}
                threads = wm.get('active_threads') or []
                for t in threads:
                    for ev in t.get('evidence', []):
                        wm_evidences.append((ep.get('episode_id'), step.get('step_index'), ev))
                # Check dimension_evidence directly
                for item in (step.get('dimension_evidence') or []):
                    dim_evidences.append((ep.get('episode_id'), step.get('step_index'), item))
    return wm_evidences, dim_evidences

p_wm_ev, p_dim_ev = scan_evidences(persona_dir)
np_wm_ev, np_dim_ev = scan_evidences(no_persona_dir)

print(f"Persona - Total WM Evidences: {len(p_wm_ev)}, Total Dim Evidences: {len(p_dim_ev)}")
print(f"No Persona - Total WM Evidences: {len(np_wm_ev)}, Total Dim Evidences: {len(np_dim_ev)}")

def analyze_ev_list(ev_list, group_name):
    print(f"\n==================== {group_name} WM EVIDENCES ====================")
    source_counter = Counter()
    dim_counter = Counter()
    sample_by_dim = {}

    for ep_id, step_idx, ev in ev_list:
        if isinstance(ev, str) and '=' in ev:
            prefix, value = ev.split('=', 1)
            if ':' in prefix:
                source, dim = prefix.split(':', 1)
            else:
                source, dim = prefix, ''
            source_counter[source] += 1
            dim_counter[(source, dim)] += 1
            if (source, dim) not in sample_by_dim:
                sample_by_dim[(source, dim)] = (value, ev)

    print("\n--- By Source ---")
    for s, c in source_counter.most_common():
        print(f"  {s}: {c} ({c/len(ev_list)*100:.1f}%)")

    print("\n--- By Source:Dimension (All) ---")
    for (s, d), c in dim_counter.most_common():
        print(f"  {s}:{d} -> {c} occurrences")
        sample_val = sample_by_dim[(s, d)][0][:100]
        print(f"      Example: {sample_val}")

analyze_ev_list(p_wm_ev, "PERSONA GROUP")
analyze_ev_list(np_wm_ev, "NO PERSONA GROUP (CONTROL)")
