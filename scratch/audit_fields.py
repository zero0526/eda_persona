import json
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

dd = pd.read_csv('output/tables/data_dictionary.csv')
num_df = pd.read_csv('output/tables/step4_all_numeric_significance_screening.csv')
mi_df = pd.read_csv('output/tables/step5_mutual_information.csv')
driver_df = pd.read_csv('output/tables/step5_driver_proxy_classification.csv')
gesture_df = pd.read_csv('output/tables/step5_recent_actions_gesture_comparison.csv')

print(f"Total in Data Dictionary: {len(dd)}")
print(f"Total Numeric Tested in Step 4: {len(num_df)}")
print(f"Total in MI Ranking: {len(mi_df)}")
print(f"Total Categorical in Driver/Proxy: {len(driver_df)}")

# Let's see the metadata fields
metadata_fields = dd[dd['Group'].str.contains('Metadata', case=False)]['Field'].tolist()
print("\n=== METADATA FIELDS (TO OMIT) ===")
print(metadata_fields)

# Let's inspect the numeric features tested in Step 4
print("\n=== NUMERIC FEATURES SCREENED (TOP 20) ===")
for i, r in num_df.head(20).iterrows():
    print(f"{i+1:2d}. {r['Field']} | Delta={r['cliffs_delta']:.3f} | p={r['p_value']:.2e} | Effect={r['effect_size']}")

# Let's see all unique features used in key analyses
key_features = set()
key_features.update(num_df[num_df['p_value'] < 0.05]['Field'].tolist())
key_features.update(mi_df.iloc[:, 0].tolist())
key_features.update(driver_df.iloc[:, 0].tolist())
key_features.update(['intent', 'surface', 'verified', 'reaction', 'reason', 'scroll_speed_px_s', 'scroll_pace_mode', 'scroll_px', 'gesture_ms'])

# Remove metadata
clean_key_features = [f for f in key_features if f not in metadata_fields and not f.startswith('file_') and not f.startswith('episode_')]

print(f"\nTotal Clean Key Features (Excluding Metadata): {len(clean_key_features)}")
print(sorted(clean_key_features))

