"""
Vẽ Heatmap Trực Quan Hóa Phân Bổ Evidence Theo Tầng Category (6 Persona Facebook).
- Nguồn dữ liệu: output/tables/interest_category_distribution.csv
- Xuất biểu đồ 300 DPI ra: output/figures/
    1. heatmap_category_combined.png (Biểu đồ kép: Số lượng tuyệt đối & Tỉ trọng %)
    2. heatmap_category_counts.png (Số lượng lượt viện dẫn)
    3. heatmap_category_percent.png (Tỉ trọng % trong từng Persona)
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Đảm bảo in tiếng Việt chuẩn trên Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Cấu hình font chữ hiển thị tốt tiếng Anh và biểu đồ
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Segoe UI", "Tahoma"]
plt.rcParams["axes.unicode_minus"] = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "output" / "tables" / "interest_category_distribution.csv"
FIGURES_DIR = PROJECT_ROOT / "output" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

PERSONA_COLS = ["vn_fb_001", "vn_fb_002", "vn_fb_003", "vn_fb_004", "vn_fb_005", "vn_fb_006"]
PERSONA_LABELS = [
    "vn_fb_001\n(Đồ họa, 26t)",
    "vn_fb_002\n(Gia đình, 42t)",
    "vn_fb_003\n(Bảo vệ, 28t)",
    "vn_fb_004\n(Nhà hàng, 22t)",
    "vn_fb_005\n(Cơ khí, 31t)",
    "vn_fb_006\n(BĐS, 52t)",
]


def generate_heatmaps():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy tệp {CSV_PATH}. Hãy chạy notebooks/interest.py trước để tạo bảng phân bổ!"
        )

    df = pd.read_csv(CSV_PATH)
    # Loại bỏ 3 category không cần vẽ
    exclude_cats = ["Social Media Platforms", "Social Perspectives", "Language Competency"]
    df = df[~df["Category"].isin(exclude_cats)].reset_index(drop=True)
    print(f"[+] Đã lọc còn {len(df)} categories (đã bỏ qua: {', '.join(exclude_cats)})")

    # Nhãn hiển thị cho trục tung (Y-axis) kèm phân nhóm Subgroup
    cat_labels = [f"[{r['Subgroup']}] {r['Category']}" for _, r in df.iterrows()]

    # 1. Ma trận số lượng tuyệt đối (Raw Counts)
    matrix_counts = df[PERSONA_COLS].values

    # 2. Ma trận tỉ trọng phần trăm chuẩn hóa theo từng cột Persona (Column Share %)
    col_sums = matrix_counts.sum(axis=0, keepdims=True)
    matrix_pct = (matrix_counts / col_sums) * 100

    # =========================================================================
    # 1. BIỂU ĐỒ KẾP COMBINED (Raw Counts bên trái & Percentage Share bên phải)
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(21, 11), sharey=True)

    # Subplot 1: Raw Counts (Bảng màu YlGnBu)
    sns.heatmap(
        matrix_counts,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        xticklabels=PERSONA_LABELS,
        yticklabels=cat_labels,
        cbar_kws={"label": "Số lượt viện dẫn Evidence (Counts)"},
        ax=ax1,
        linewidths=0.6,
        linecolor="#e0e0e0",
    )
    ax1.set_title(
        "1. SỐ LƯỢNG LƯỢT VIỆN DẪN EVIDENCE (RAW COUNTS)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax1.set_xlabel("Persona Facebook", fontsize=11, fontweight="bold", labelpad=10)
    ax1.set_ylabel("Subgroup & Category", fontsize=11, fontweight="bold")

    # Subplot 2: Share Percentage % (Bảng màu OrRd)
    sns.heatmap(
        matrix_pct,
        annot=True,
        fmt=".1f",
        cmap="OrRd",
        xticklabels=PERSONA_LABELS,
        yticklabels=cat_labels,
        cbar_kws={"label": "Tỉ trọng đóng góp trong Persona (%)"},
        ax=ax2,
        linewidths=0.6,
        linecolor="#e0e0e0",
    )
    ax2.set_title(
        "2. TỈ TRỌNG ĐÓNG GÓP EVIDENCE TRONG MỖI PERSONA (%)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax2.set_xlabel("Persona Facebook", fontsize=11, fontweight="bold", labelpad=10)

    plt.suptitle(
        "HEATMAP PHÂN BỔ EVIDENCE THEO TẦNG CATEGORY CỦA 6 PERSONA FACEBOOK",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    combined_png = FIGURES_DIR / "heatmap_category_combined.png"
    plt.savefig(combined_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[✓] Đã tạo biểu đồ kép Combined: {combined_png}")

    # =========================================================================
    # 2. BIỂU ĐỒ ĐƠN: RAW COUNTS
    # =========================================================================
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        matrix_counts,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        xticklabels=PERSONA_LABELS,
        yticklabels=cat_labels,
        cbar_kws={"label": "Số lượt viện dẫn (Counts)"},
        ax=ax,
        linewidths=0.6,
        linecolor="#e0e0e0",
    )
    ax.set_title(
        "HEATMAP SỐ LƯỢT VIỆN DẪN EVIDENCE THEO CATEGORY",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.tight_layout()
    counts_png = FIGURES_DIR / "heatmap_category_counts.png"
    plt.savefig(counts_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[✓] Đã tạo biểu đồ Counts: {counts_png}")

    # =========================================================================
    # 3. BIỂU ĐỒ ĐƠN: PERCENTAGE SHARE %
    # =========================================================================
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        matrix_pct,
        annot=True,
        fmt=".1f",
        cmap="OrRd",
        xticklabels=PERSONA_LABELS,
        yticklabels=cat_labels,
        cbar_kws={"label": "Tỉ trọng (%) trong Persona"},
        ax=ax,
        linewidths=0.6,
        linecolor="#e0e0e0",
    )
    ax.set_title(
        "HEATMAP TỈ TRỌNG (%) EVIDENCE THEO CATEGORY TRONG MỖI PERSONA",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    percent_png = FIGURES_DIR / "heatmap_category_percent.png"
    plt.savefig(percent_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[✓] Đã tạo biểu đồ Percent: {percent_png}")

    # Đồng bộ sang brain artifact dir nếu tồn tại
    brain_dir = Path(r"C:\Users\KHOENV\.gemini\antigravity-ide\brain\636efee4-4250-47e5-8378-a81c3f79aa95")
    if brain_dir.exists():
        import shutil
        shutil.copy(combined_png, brain_dir / "heatmap_category_combined.png")
        shutil.copy(counts_png, brain_dir / "heatmap_category_counts.png")
        shutil.copy(percent_png, brain_dir / "heatmap_category_percent.png")


def main():
    print("==========================================================================================")
    print(" KHỞI CHẠY XUẤT HEATMAP TRỰC QUAN HÓA THEO CATEGORY")
    print("==========================================================================================")
    generate_heatmaps()
    print("==========================================================================================")
    print(" [HOÀN TẤT] TẤT CẢ BIỂU ĐỒ 300 DPI ĐÃ ĐƯỢC LƯU TRONG THƯ MỤC OUTPUT/FIGURES/")
    print("==========================================================================================")


if __name__ == "__main__":
    main()
