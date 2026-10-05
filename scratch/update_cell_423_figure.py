import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("notebooks/eda_action_logs.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Tìm cell 4.2.3 code
updated = False
for idx, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    if "4.2.3. Thống kê Độ phủ Danh mục Sở thích Mạnh" in src and cell.get("cell_type") == "code":
        print(f"Found target cell at index {idx}")
        cell["source"] = [
            "# 4.2.3. Thống kê Độ phủ Danh mục Sở thích Mạnh (interests.strong) trong Dimension Evidence\n",
            "from viz.univariate_viz import plot_strong_interests_coverage\n",
            "from IPython.display import Image, display\n",
            "\n",
            "df_strong_cov = pd.read_csv(project_root / \"output\" / \"tables\" / \"step4_strong_interests_coverage.csv\")\n",
            "\n",
            "print(\"=== BẢNG ĐỐI SOÁT ĐỘ PHỦ 12 SỞ THÍCH MẠNH (STRONG INTERESTS COVERAGE & FIDELITY) ===\")\n",
            "cols_show = ['episode_id', 'persona_id', 'total_steps', 'steps_with_evidence', 'evidence_anchoring_pct', 'total_strong_interests', 'covered_strong_count', 'coverage_rate_pct', 'covered_strong_list']\n",
            "display(df_strong_cov[cols_show].style.set_properties(**{'text-align': 'left'}).format({'evidence_anchoring_pct': '{:.1f}%', 'coverage_rate_pct': '{:.1f}%'}))\n",
            "\n",
            "# Vẽ và hiển thị biểu đồ độ phủ sở thích mạnh & tính nhất quán nhận thức\n",
            "fig_strong_path = project_root / \"output\" / \"figures\" / \"step4_strong_interests_coverage.png\"\n",
            "plot_strong_interests_coverage(df_strong_cov, output_path=fig_strong_path)\n",
            "display(Image(filename=str(fig_strong_path)))\n"
        ]
        cell["outputs"] = []
        cell["execution_count"] = None
        updated = True
        break

if updated:
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("Successfully updated notebook cell 4.2.3 to include the figure display!")
else:
    print("Error: Target cell not found!")
