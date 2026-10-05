import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.stdout.reconfigure(encoding='utf-8')

# 1. Đọc dữ liệu n-gram đã trích xuất
df_tri = pd.read_csv("output/tables/step5_ngram_trigram_distribution_jsd.csv", index_col=0)

# 2. Chọn lọc 10 patterns đặc trưng và có ý nghĩa thống kê / nhận thức cao nhất
selected_patterns = [
    # Top 5 Persona Signatures (Dương mạnh)
    "React/Social -> Observe -> React/Social",
    "Scroll Feed -> Scroll Feed -> Scroll Feed",
    "Scroll Feed -> Search Query -> Search Query",
    "Deep Read -> React/Social -> Scroll Feed",
    "Scroll Feed -> Deep Read -> React/Social",
    # Top 5 No-Persona Signatures (Âm mạnh)
    "Observe -> Deep Read -> Observe",
    "Deep Read -> Observe -> Navigate",
    "Observe -> Other -> Observe",
    "Scroll Feed -> Observe -> Deep Read",
    "Deep Read -> Observe -> Scroll Feed"
]

sub = df_tri.loc[selected_patterns].copy()

# Đặt nhãn thân thiện và ngắn gọn
pattern_labels = {
    "React/Social -> Observe -> React/Social": "React -> Observe -> React (Tương tác bùng nổ liên hoàn)",
    "Scroll Feed -> Scroll Feed -> Scroll Feed": "Scroll -> Scroll -> Scroll (Lướt dòng chảy liên tục)",
    "Scroll Feed -> Search Query -> Search Query": "Scroll -> Search -> Search (Tìm kiếm chủ động khi cạn feed)",
    "Deep Read -> React/Social -> Scroll Feed": "Read -> React -> Scroll (Chu trình: Đọc -> Like -> Cuộn)",
    "Scroll Feed -> Deep Read -> React/Social": "Scroll -> Read -> React (Chu trình: Lướt -> Đọc -> Like)",
    "Observe -> Deep Read -> Observe": "Observe -> Read -> Observe (Vòng lặp Kẹt Modal kinh điển)",
    "Deep Read -> Observe -> Navigate": "Read -> Observe -> Nav (Bế tắc tìm cách đóng modal)",
    "Observe -> Other -> Observe": "Observe -> Other -> Observe (Đứng nhìn thụ động / Thao tác thừa)",
    "Scroll Feed -> Observe -> Deep Read": "Scroll -> Observe -> Read (Cuộn ngập ngừng rồi kẹt modal)",
    "Deep Read -> Observe -> Scroll Feed": "Read -> Observe -> Scroll (Thoát modal sau thời gian đứng nhìn)"
}

sub["Label"] = [pattern_labels[p] for p in sub.index]
sub["Group"] = ["Persona" if l > 0 else "No-Persona" for l in sub["Log_Odds_Ratio"]]
sub = sub.sort_values("Log_Odds_Ratio", ascending=True)

# 3. Vẽ biểu đồ 2 Panel chất lượng cao
fig, axes = plt.subplots(1, 2, figsize=(18, 8), gridspec_kw={'width_ratios': [1.2, 1]})
plt.subplots_adjust(wspace=0.35)

# Panel 1: Biểu đồ Thanh Đối nghịch Thống kê (Diverging Log-Odds Ratio)
colors = ["#c53030" if x < 0 else "#2b6cb0" for x in sub["Log_Odds_Ratio"]]
y_pos = np.arange(len(sub))

bars = axes[0].barh(y_pos, sub["Log_Odds_Ratio"], color=colors, height=0.65, edgecolor='black', linewidth=0.5)
axes[0].set_yticks(y_pos)
axes[0].set_yticklabels(sub["Label"], fontsize=10.5, fontweight='semibold')
axes[0].axvline(0, color='black', linewidth=1.2, linestyle='--')
axes[0].set_xlabel("Hệ số Log-Odds Ratio (Âm: Nghiêng về No-Persona | Dương: Nghiêng về Persona)", fontsize=11, fontweight='bold', labelpad=10)
axes[0].set_title("A. Mức độ Nghiêng Hành vi Đặc trưng (Log-Odds Ratio Contrast)", fontsize=12, fontweight='bold', pad=12)

# Thêm giá trị trên thanh
for bar, val in zip(bars, sub["Log_Odds_Ratio"]):
    offset = 0.12 if val >= 0 else -0.12
    align = 'left' if val >= 0 else 'right'
    axes[0].text(val + offset, bar.get_y() + bar.get_height()/2, f"{val:+.2f}", 
                 va='center', ha=align, fontsize=10, fontweight='bold',
                 color="#2b6cb0" if val >= 0 else "#c53030")

axes[0].set_xlim(-4.6, 3.5)
axes[0].grid(axis='x', linestyle=':', alpha=0.6)

# Panel 2: Biểu đồ Thanh Ghép So sánh Tỷ trọng Xác suất Thực tế (%)
bar_width = 0.38
y_pos2 = np.arange(len(sub))

rects1 = axes[1].barh(y_pos2 + bar_width/2, sub["Prob_Persona (%)"], height=bar_width, 
                      label="Có Persona", color="#2b6cb0", edgecolor='black', linewidth=0.5)
rects2 = axes[1].barh(y_pos2 - bar_width/2, sub["Prob_NoPersona (%)"], height=bar_width, 
                      label="Không có Persona", color="#e53e3e", edgecolor='black', linewidth=0.5)

axes[1].set_yticks(y_pos2)
axes[1].set_yticklabels(["" for _ in y_pos2]) # Ẩn nhãn trục y vì đã có ở Panel 1
axes[1].set_xlabel("Tỷ trọng Xuất hiện trong Toàn bộ Trigrams (%)", fontsize=11, fontweight='bold', labelpad=10)
axes[1].set_title("B. Đối sánh Tỷ trọng Xác suất Thực tế (Probability %)", fontsize=12, fontweight='bold', pad=12)
axes[1].legend(loc="lower right", frameon=True, fontsize=11, shadow=True)

# Thêm nhãn % ở đầu thanh
for rect in rects1:
    w = rect.get_width()
    if w > 0:
        axes[1].text(w + 0.3, rect.get_y() + rect.get_height()/2, f"{w:.1f}%", va='center', ha='left', fontsize=9, color="#1a365d", fontweight='bold')

for rect in rects2:
    w = rect.get_width()
    if w > 0:
        axes[1].text(w + 0.3, rect.get_y() + rect.get_height()/2, f"{w:.1f}%", va='center', ha='left', fontsize=9, color="#9b2c2c", fontweight='bold')

axes[1].set_xlim(0, 16.5)
axes[1].grid(axis='x', linestyle=':', alpha=0.6)

# Lưu biểu đồ
plt.suptitle("ĐỐI SOÁT CÁC CHUỖI HÀNH VI ĐẶC TRƯNG NỔI BẬT NHẤT (PROMINENT TRIGRAM PATTERNS)\n"
             "Jensen-Shannon Divergence: JSD = 0.729 bit (Distance = 0.854, p = 0.044)", 
             fontsize=14, fontweight='bold', y=0.98)

out_file = "output/figures/step5_prominent_behavioral_patterns.png"
plt.savefig(out_file, dpi=300, bbox_inches='tight')
plt.close()
print(f"Đã xuất biểu đồ nổi bật tại: {out_file}")

# Lưu bảng tổng hợp các pattern nổi bật
sub_export = sub[["Label", "Count_Persona", "Count_NoPersona", "Prob_Persona (%)", "Prob_NoPersona (%)", "Lift_P_vs_NP", "Log_Odds_Ratio", "JSD_Contrib"]]
sub_export.to_csv("output/tables/step5_prominent_trigram_patterns.csv")
print("Đã lưu bảng dữ liệu tại: output/tables/step5_prominent_trigram_patterns.csv")
