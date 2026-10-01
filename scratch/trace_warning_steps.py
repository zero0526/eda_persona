import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

f = Path('data/no_persona_Action/benchmark_eda_755b1653.json')
with open(f, 'r', encoding='utf-8') as fp:
    data = json.load(fp)
ep = data if isinstance(data, dict) else data[0]

steps = ep.get('step_records', [])
print('Total steps:', len(steps))
for s in steps:
    ctx = s.get('session_context') or {}
    wm = ctx.get('working_memory') or {}
    nov = wm.get('novelty') or {}
    sit = nov.get('situational_steps', 0)
    g = nov.get('guidance', '')
    warn = 'CẢNH BÁO' in g
    idx = s.get('step_index')
    if sit > 0 or warn:
        print(f"Step {idx:2d}: sit_steps={sit:2d}, warn={warn!s:5s}, intent={str(s.get('intent')):10s}, tool={str(s.get('resolved_tool')):18s}")
        if idx in [15, 16, 25, 41]:
            print(f"    Guidance: {g}")
            print(f"    Reason: {str(s.get('reason'))[:100]}...")
