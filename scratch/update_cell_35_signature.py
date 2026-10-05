import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("notebooks/eda_action_logs.ipynb")
backup_path = Path("notebooks/eda_action_logs.ipynb.bak3")

# Backup
shutil.copy2(nb_path, backup_path)
print(f"Backed up {nb_path} to {backup_path}")

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Tìm cell code 5.1 (thường là cell cuối cùng)
updated = False
for idx, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    if "# 5.1. Đối soát Phân bố Hành vi theo Tiến trình Thời gian" in src and cell.get("cell_type") == "code":
        print(f"Found target Cell 5.1 code at index {idx}")
        cell["source"] = [
            "# 5.1. Đối soát Hành vi Đặc trưng theo Tiến trình Thời gian (Persona vs No-Persona)\n",
            "from IPython.display import Image, display\n",
            "\n",
            "# 1. Đọc và hiển thị Bảng Đối soát Hành vi Đặc trưng của từng Pha\n",
            "df_sig = pd.read_csv(project_root / \"output\" / \"tables\" / \"step5_signature_behaviors_by_phase.csv\")\n",
            "\n",
            "print(\"=== BẢNG ĐỐI SOÁT HÀNH VI ĐẶC TRƯNG QUA 4 GIAI ĐOẠN (HABERMAN RESIDUALS & LIFT RATIO) ===\")\n",
            "display(\n",
            "    df_sig.style\n",
            "    .set_properties(subset=['Giai đoạn', 'Đối tượng', 'Hành vi Đặc trưng', 'Tỷ trọng (%)'], **{'font-weight': 'bold'})\n",
            "    .set_properties(**{'text-align': 'left'})\n",
            "    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'left')]}])\n",
            ")\n",
            "\n",
            "# 2. Hiển thị biểu đồ trực quan hóa đối sánh động lực học hành vi theo thời gian\n",
            "fig_beh_path = project_root / \"output\" / \"figures\" / \"step5_temporal_behavior_distribution.png\"\n",
            "display(Image(filename=str(fig_beh_path)))\n"
        ]
        cell["outputs"] = []
        cell["execution_count"] = None
        updated = True
        break

if updated:
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("Successfully updated Cell 5.1 in eda_action_logs.ipynb!")
else:
    print("Error: Target Cell 5.1 not found!")
