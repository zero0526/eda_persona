import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("notebooks/eda_action_logs.ipynb")
backup_path = Path("notebooks/eda_action_logs.ipynb.bak5")

# Backup
shutil.copy2(nb_path, backup_path)
print(f"Backed up {nb_path} to {backup_path}")

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

target_idx = None
for idx, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    if "# 5.1" in src and cell.get("cell_type") == "code":
        target_idx = idx
        break

if target_idx is not None:
    print(f"Updating Cell {target_idx} in eda_action_logs.ipynb...")
    nb["cells"][target_idx]["source"] = [
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
        "# 2. Đọc và hiển thị Heatmap Hệ số Vượt trội (Metric Lift = P(Behavior|Phase) / P(Behavior))\n",
        "lift_p = pd.read_csv(project_root / \"output\" / \"tables\" / \"step5_behavior_lift_persona.csv\", index_col=0)\n",
        "lift_np = pd.read_csv(project_root / \"output\" / \"tables\" / \"step5_behavior_lift_nopersona.csv\", index_col=0)\n",
        "\n",
        "print(\"\\n=== HEATMAP CHỈ SỐ LIFT HÀNH VI (BASELINE = 1.00x) - NHÓM CÓ PERSONA ===\")\n",
        "display(\n",
        "    lift_p.style.format(\"{:.2f}x\")\n",
        "    .background_gradient(cmap=\"Blues\", vmin=0.0, vmax=3.5, axis=None)\n",
        "    .set_properties(**{'text-align': 'center'})\n",
        "    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])\n",
        ")\n",
        "\n",
        "print(\"\\n=== HEATMAP CHỈ SỐ LIFT HÀNH VI (BASELINE = 1.00x) - NHÓM KHÔNG CÓ PERSONA ===\")\n",
        "display(\n",
        "    lift_np.style.format(\"{:.2f}x\")\n",
        "    .background_gradient(cmap=\"Reds\", vmin=0.0, vmax=3.5, axis=None)\n",
        "    .set_properties(**{'text-align': 'center'})\n",
        "    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])\n",
        ")\n",
        "\n",
        "# 3. Hiển thị đồ họa Heatmap Lift và Biểu đồ Đối sánh Động lực học Hành vi\n",
        "fig_lift_path = project_root / \"output\" / \"figures\" / \"step5_behavior_lift_heatmap.png\"\n",
        "display(Image(filename=str(fig_lift_path)))\n",
        "\n",
        "fig_beh_path = project_root / \"output\" / \"figures\" / \"step5_temporal_behavior_distribution.png\"\n",
        "display(Image(filename=str(fig_beh_path)))\n"
    ]
    nb["cells"][target_idx]["outputs"] = []
    nb["cells"][target_idx]["execution_count"] = None

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("Notebook updated successfully with Lift Metric Heatmaps!")
else:
    print("Error: Target Cell 5.1 not found!")
