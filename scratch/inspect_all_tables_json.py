import sys, os, sqlite3, json
sys.path.append(os.path.abspath('.'))
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [r[0] for r in cur.fetchall()]

schema_map = {}

for t in tables:
    cur.execute(f"PRAGMA table_info(`{t}`);")
    cols = [dict(c) for c in cur.fetchall()]
    cur.execute(f"SELECT * FROM `{t}` LIMIT 10;")
    sample_rows = [dict(r) for r in cur.fetchall()]
    
    json_cols_info = {}
    for c in cols:
        c_name = c['name']
        is_json = 'json' in c_name.lower()
        if not is_json and sample_rows:
            v = sample_rows[0].get(c_name)
            if isinstance(v, str) and (v.strip().startswith('{') or v.strip().startswith('[')):
                is_json = True
                
        if is_json:
            # Analyze all samples for this column
            parsed_samples = []
            for r in sample_rows:
                raw_val = r.get(c_name)
                if raw_val:
                    try:
                        parsed = json.loads(raw_val)
                        parsed_samples.append(parsed)
                    except Exception:
                        pass
            
            # Extract structure
            keys = set()
            types = set()
            for ps in parsed_samples:
                types.add(type(ps).__name__)
                if isinstance(ps, dict):
                    keys.update(ps.keys())
                elif isinstance(ps, list) and ps and isinstance(ps[0], dict):
                    keys.update(ps[0].keys())
                    
            json_cols_info[c_name] = {
                'types': list(types),
                'sample_count': len(parsed_samples),
                'keys': sorted(list(keys))
            }
            
    schema_map[t] = {
        'cols': cols,
        'count': len(sample_rows),
        'json_cols': json_cols_info
    }

print(f"=== TỔNG HỢP {len(tables)} BẢNG TRONG DATABASE ===")
for t, s in schema_map.items():
    print(f"\nTABLE: {t} ({len(s['cols'])} columns)")
    for c in s['cols']:
        is_pk = ' [PK]' if c['pk'] else ''
        not_null = ' [NOT NULL]' if c['notnull'] else ''
        j_info = ''
        if c['name'] in s['json_cols']:
            info = s['json_cols'][c['name']]
            j_info = f" ---> JSON ({info['types']}) keys: {info['keys'][:8]}..."
        print(f"  - {c['name']:30s} {c['type']:10s}{is_pk}{not_null}{j_info}")
