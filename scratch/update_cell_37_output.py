import sys
import json
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("notebooks/eda_action_logs.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

csv_path = Path("output/tables/step5_prominent_trigram_patterns.csv")
df = pd.read_csv(csv_path)

# Tạo html table đẹp cho Cell 37
html_table = df.style\
    .set_properties(subset=['Ý nghĩa Chu trình'], **{'font-weight': 'bold'})\
    .format({\
        'Tỷ trọng Persona (%)': '{:.2f}%',\
        'Tỷ trọng No-Persona (%)': '{:.2f}%',\
        'Log_Odds_Ratio': '{:+0.2f}'\
    })\
    .background_gradient(subset=['Log_Odds_Ratio'], cmap='coolwarm', vmin=-4.0, vmax=3.0)\
    .set_properties(**{'text-align': 'center'})\
    .set_properties(subset=['Ý nghĩa Chu trình'], **{'text-align': 'left'})\
    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])\
    .to_html()

new_output = [
    {
        "name": "stdout",
        "output_type": "stream",
        "text": [
            "=== BẢNG 10 CHUỖI HÀNH VI (TRIGRAMS) ĐẶC TRƯNG NỔI BẬT NHẤT GIỮA HAI NHÓM ===\n",
            "Phương pháp Thống kê: Log-Odds Ratio (LOR) | Dương: Nghiêng về Persona, Âm: Nghiêng về No-Persona\n",
            "\n"
        ]
    },
    {
        "data": {
            "text/html": [html_table + "\n"],
            "text/plain": [df.to_string()]
        },
        "metadata": {},
        "output_type": "display_data"
    }
]

# Giữ nguyên display image nếu có ở output cũ
old_outputs = nb["cells"][37].get("outputs", [])
for out in old_outputs:
    if out.get("output_type") == "display_data" and "image/png" in out.get("data", {}):
        new_output.append(out)
        break

nb["cells"][37]["outputs"] = new_output

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Đã cập nhật hoàn toàn cell output của Cell 37 không còn dính JSD!")
