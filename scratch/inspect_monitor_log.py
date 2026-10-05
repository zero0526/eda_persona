import json
from pathlib import Path

logs_dir = Path('data/action_logs')
sample_mon = next(logs_dir.glob('monitor_log_*.json'))
with open(sample_mon, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"=== {sample_mon.name} ===")
if isinstance(data, list):
    print("List of length:", len(data))
    if data:
        print("Sample item keys:", list(data[0].keys()))
elif isinstance(data, dict):
    print("Dict keys:", list(data.keys()))
