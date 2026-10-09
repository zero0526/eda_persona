import sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader
import pandas as pd

loader = ActionLoader()
df = loader.to_unified_actions_dataframe()

print("Columns in df_actions:", df.columns.tolist())
print("\nSample row:")
print(df.iloc[0].to_dict())

print("\nUnique surfaces:", df['surface'].unique())
print("Unique intents:", df['intent'].unique())
print("Unique action_types:", df['action_type'].unique() if 'action_type' in df.columns else "N/A")
