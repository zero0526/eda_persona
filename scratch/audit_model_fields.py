import sqlite3
import sys

sys.path.insert(0, r"d:\source_code\eda_persona")
from loaders.models import table_models

DB_PATH = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cursor.fetchall()]

all_models = {k: getattr(table_models, k) for k in dir(table_models) if k.endswith('Model')}

# Mapping table to model
def find_model(tbl):
    for m_name, m_cls in all_models.items():
        if f"`{tbl}`" in (m_cls.__doc__ or ""):
            return m_cls
    return None

print("SO SÁNH CỘT SQLITE VỚI MODEL FIELDS:")
for tbl in tables:
    m = find_model(tbl)
    if not m:
        print(f"Không tìm thấy model cho {tbl}")
        continue
    
    cols = cursor.execute(f"PRAGMA table_info({tbl})").fetchall()
    # (cid, name, type, notnull, dflt_value, pk)
    db_col_names = set(c[1] for c in cols)
    model_field_names = set(m.model_fields.keys())

    missing_in_model = db_col_names - model_field_names
    extra_in_model = model_field_names - db_col_names

    # Check required fields in extra
    extra_required = [f for f in extra_in_model if m.model_fields[f].is_required()]

    if missing_in_model or extra_required:
        print(f"\n Bảng [{tbl}] -> Model [{m.__name__}]:")
        if missing_in_model:
            print(f"   - Thiếu trong Model: {missing_in_model}")
        if extra_required:
            print(f"   - Thừa (Required) trong Model: {extra_required}")
        if extra_in_model - set(extra_required):
            print(f"   - Thừa (Optional) trong Model: {extra_in_model - set(extra_required)}")
