import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

t_num = pd.read_csv('output/tables/step4_all_numeric_significance_screening.csv')
num_fields = t_num[['Field', 'Group', 'Meaning', 'p_value', 'cliffs_delta', 'effect_size']].copy()

print("=== ALL 40 NUMERIC FIELDS TESTED IN STEP 4.1 ===")
for i, r in num_fields.iterrows():
    print(f"{i+1:2d}. {r['Field']} ({r['Group']}): Delta={r['cliffs_delta']:.3f}, p={r['p_value']:.2e} [{r['effect_size']}]")
