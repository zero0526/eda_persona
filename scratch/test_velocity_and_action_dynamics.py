import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

from loaders.loaders.persona_action import PersonaActionLoader

loader = PersonaActionLoader()
df_steps = loader.load_step_records()
df_ep = loader.load_action_logs()

print("Columns in df_steps:", df_steps.columns.tolist())
print("\nUnique tools:", df_steps["tool"].value_counts().to_dict())
print("\nUnique resolved tools:", df_steps["resolved_tool"].value_counts().to_dict())
print("\nUnique intents:", df_steps["intent"].value_counts().to_dict())

# Check step_delta_sec calculation
if "step_delta_sec" not in df_steps.columns:
    df_steps["timestamp_dt"] = pd.to_datetime(df_steps["timestamp"])
    df_steps["step_delta_sec"] = df_steps.groupby("episode_id")["timestamp_dt"].diff().dt.total_seconds()
    # Or from context_elapsed_seconds
    df_steps["elapsed_delta_sec"] = df_steps.groupby("episode_id")["context_elapsed_seconds"].diff()

print("\nPвающих context_action_velocity by dataset_type:")
print(df_steps.groupby("dataset_type")["context_action_velocity"].describe())

p_steps = df_steps[df_steps["dataset_type"] == "persona"]
print("\nPersona pace values:")
print(p_steps["persona_pace"].value_counts(dropna=False))

print("\nMean velocity by persona_pace:")
print(p_steps.groupby("persona_pace")["context_action_velocity"].describe())
