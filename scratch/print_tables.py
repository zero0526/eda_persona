import json

with open("scratch/db_schema_summary.json", "r", encoding="utf-8") as f:
    d = json.load(f)

for table in sorted(d.keys()):
    info = d[table]
    col_names = [c["name"] for c in info["columns"]]
    print(f"{table} ({info['count']} rows):")
    print("   ", ", ".join(col_names))
