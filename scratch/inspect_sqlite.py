import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = r'D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite'
print('Exists:', os.path.exists(db_path))
if not os.path.exists(db_path):
    print("Database does not exist at:", db_path)
    sys.exit(1)

print('Size:', os.path.getsize(db_path), 'bytes')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Tables:', tables)

for (tname,) in tables:
    cursor.execute(f"PRAGMA table_info({tname});")
    cols = cursor.fetchall()
    print(f"\n==================================================")
    print(f"Table: {tname} (columns: {len(cols)})")
    print(f"==================================================")
    for c in cols:
        # cid, name, type, notnull, dflt_value, pk
        cid, name, ctype, notnull, dflt_val, pk = c
        pk_str = " [PRIMARY KEY]" if pk else ""
        nn_str = " NOT NULL" if notnull else ""
        dflt_str = f" DEFAULT {dflt_val}" if dflt_val is not None else ""
        print(f"  - {name}: {ctype}{nn_str}{dflt_str}{pk_str}")
    
    cursor.execute(f"SELECT COUNT(*) FROM {tname};")
    cnt = cursor.fetchone()[0]
    print(f"Total rows: {cnt}")
    
    if cnt > 0:
        cursor.execute(f"SELECT * FROM {tname} LIMIT 1;")
        sample = cursor.fetchone()
        col_names = [col[1] for col in cols]
        sample_dict = dict(zip(col_names, sample))
        print("Sample row:")
        for k, v in sample_dict.items():
            val_str = str(v)
            if len(val_str) > 100:
                val_str = val_str[:100] + "... (truncated)"
            print(f"    {k}: {val_str}")

conn.close()
