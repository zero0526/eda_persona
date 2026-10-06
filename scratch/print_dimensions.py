import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd

df = pd.read_csv('d:/source_code/eda_persona/data/persona_Dimension_v2.csv')
for i, r in df.iloc[:18].iterrows():
    print(f"{i:3d} | {str(r['Group']):15s} | {str(r['Category']):25s} | {str(r['Dimension']):35s} | {r['Label']}")
