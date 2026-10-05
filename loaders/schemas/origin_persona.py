import json
with open("./data/selected_6_facebook_personas_description.jsonl", "r", encoding="utf-8") as f:
    for line in f.readlines():
        data = json.loads(line)
        print(data['attributes'].keys())
        print(len(data['attributes'].keys()))
        break

import pandas as pd

dimensions = pd.read_csv('./data/persona_Dimension_v2.csv', header=1, encoding="utf-8")
print(dimensions.head())
with open("./data/natural_field_map.json", "r", encoding="utf-8") as f:
    natural_field_map = json.load(f)
final_schema= {}

for index, row in dimensions.iterrows():
    final_schema[row[4]]= natural_field_map[row[6].split()]

with open("./data/final_schema.json", "w", encoding="utf-8") as f:
    json.dump(final_schema, f, ensure_ascii=False, indent=4)