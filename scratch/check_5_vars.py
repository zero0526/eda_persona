import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from loaders.loaders.persona_action import PersonaActionLoader

loader = PersonaActionLoader()
df = loader.load_step_records()

cols = [
    "wm_situational_steps",
    "wm_situational_threads_count",
    "wm_summary_searched_topics",
    "context_rest_accumulated_seconds",
    "context_rest_count"
]

print(f"Tổng số records: {len(df)}")
for col in cols:
    print("=" * 60)
    print(f"BIẾN: {col}")
    print(f"Kiểu dữ liệu: {df[col].dtype}, Missing: {df[col].isna().sum()} ({df[col].isna().mean()*100:.2f}%)")
    for group in ["persona", "no_persona"]:
        sub = df[df["dataset_type"] == group][col].dropna()
        print(f"  [{group.upper()} - N={len(sub)}]")
        print(f"    Min: {sub.min()}, Max: {sub.max()}, Mean: {sub.mean():.2f}, Median: {sub.median():.2f}")
        print(f"    Value counts:\n{sub.value_counts().sort_index().to_dict()}")
