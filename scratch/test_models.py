import sqlite3
import sys
from pathlib import Path

# Workspace sys.path
sys.path.insert(0, r"d:\source_code\eda_persona")

from loaders.models import table_models

DB_PATH = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cursor.fetchall()]
    
    # Models map
    all_models = {k: getattr(table_models, k) for k in dir(table_models) if k.endswith('Model')}
    print(f"Tổng số bảng trong SQLite: {len(tables)}")
    print(f"Tổng số Model classes: {len(all_models)}")

    # Let's map each table name to its Model
    # Some tables use snake_case to PascalCase + Model
    def table_to_model_name(tbl):
        # account_relationships -> AccountRelationshipModel
        parts = tbl.split('_')
        # Handle special cases if needed:
        # sqlite_sequence -> SqliteSequenceModel
        # if plural, some classes might be singularized
        name = "".join(p.capitalize() for p in parts)
        if name.endswith("s"):
            singular = name[:-1]
        else:
            singular = name
        return [f"{name}Model", f"{singular}Model"]

    mapped = {}
    unmapped = []
    for t in tables:
        candidates = table_to_model_name(t)
        found = None
        for c in candidates:
            if c in all_models:
                found = all_models[c]
                break
        # also try checking docstring or explicit match
        if not found:
            for m_name, m_cls in all_models.items():
                if f"`{t}`" in (m_cls.__doc__ or "") or t in m_name.lower():
                    found = m_cls
                    break
        if found:
            mapped[t] = found
        else:
            unmapped.append(t)

    print("\nMapping kết quả:")
    for t in tables:
        m = mapped.get(t)
        m_name = m.__name__ if m else "CHƯA CÓ"
        print(f"  {t:<28} -> {m_name}")

    if unmapped:
        print(f"\nCác bảng chưa map ({len(unmapped)}): {unmapped}")
        # print all models remaining
        used_models = set(m.__name__ for m in mapped.values())
        unused_models = [m for m in all_models if m not in used_models]
        print(f"Các models chưa dùng ({len(unused_models)}): {unused_models}")

    # Test validation on rows
    print("\n" + "="*70)
    print("Kiểm tra validate dữ liệu thực tế:")
    for t, m in mapped.items():
        cursor.execute(f"SELECT * FROM {t} LIMIT 3")
        rows = cursor.fetchall()
        if not rows:
            print(f" [Trống (0 dòng)] {t:<26} -> {m.__name__}")
            continue
        for row in rows:
            row_dict = dict(row)
            instance = m.model_validate(row_dict)
            assert instance is not None
        print(f" [OK - {len(rows)} dòng]   {t:<26} -> {m.__name__}")

if __name__ == "__main__":
    main()
