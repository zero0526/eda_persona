"""
Module: univariate_viz.py
Mục đích: Trực quan hóa so sánh tập trung (FOCUSED GROUP COMPARISON) giữa nhóm Persona vs No-Persona
trên các trường tiêu biểu nhất đại diện cho: Vận tốc, Sa đà nhận thức, Tải suy luận,
Độ dài lập luận, Quãng cuộn chuột và Phân bổ ý định/bề mặt.
Tuân thủ quy chuẩn: Module trực quan hóa độc lập trong viz/, xuất ảnh sang output/figures/.
"""

from pathlib import Path
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def plot_top_numeric_comparison(
    df_steps: pd.DataFrame,
    output_path: Path = None
) -> plt.Figure:
    """
    Vẽ 4 subplot so sánh tập trung cho 4 biến định lượng CÓ TÍNH SUY LUẬN HÀNH VI SÂU SẮC NHẤT:
    1. Dung lượng Mạch Nhận thức Đa nhiệm trong Bộ nhớ Làm việc (wm_num_active_threads)
    2. Cơ học Vi thao tác Cuộn chuột Chuẩn người dùng (recent_last_gesture_px)
    3. Chiều sâu Tiêu dùng Nội dung Thực chất (wm_cumulative_reads)
    4. Khả năng Bứt phá Khám phá Nguồn trang Ngoại vi (wm_cumulative_opened)
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))

    configs = [
        (
            "wm_num_active_threads",
            "1. Dung Lượng Mạch Nhận Thức Đa Nhiệm (Active Threads)\n[Persona duy trì 8 mạch song song vs No-Persona đơn tuyến 2 mạch]",
            axes[0, 0],
            "mạch chủ đề",
            True
        ),
        (
            "recent_last_gesture_px",
            "2. Cơ Học Vi Thao Tác Cuộn Chuột (Scroll Distance - px)\n[Persona cuộn vừa tầm mắt 463px (N=104) vs No-Persona cuộn tuột 684px (N=7)]",
            axes[0, 1],
            "pixels",
            False
        ),
        (
            "wm_cumulative_reads",
            "3. Chiều Sâu Tiêu Dùng Nội Dung Thực Chất (Cumulative Reads)\n[Persona đọc sâu 1-6 bài viết vs No-Persona không đọc (0 bài)]",
            axes[1, 0],
            "bài viết đã đọc",
            True
        ),
        (
            "wm_cumulative_opened",
            "4. Khả Năng Mở Rộng Không Gian Ngoại Vi (Cumulative Opened Sources)\n[Persona mở 2-4 Page/Group vs No-Persona 100% bị giam cầm trên Feed]",
            axes[1, 1],
            "nguồn/trang đã mở",
            True
        )
    ]

    palette = {"persona": "#2b5c8f", "no_persona": "#d95f02"}

    for col, title, ax, unit, is_discrete in configs:
        valid_df = df_steps.dropna(subset=[col])
        if len(valid_df) == 0:
            continue

        p_s = valid_df[valid_df["dataset_type"] == "persona"][col]
        np_s = valid_df[valid_df["dataset_type"] == "no_persona"][col]

        p_med = p_s.median()
        np_med = np_s.median()

        if is_discrete:
            # Vẽ histogram chuẩn hóa tỷ lệ theo nhóm cho biến rời rạc
            sns.histplot(
                data=valid_df,
                x=col,
                hue="dataset_type",
                discrete=True,
                stat="probability",
                common_norm=False,
                palette=palette,
                multiple="dodge",
                shrink=0.75,
                alpha=0.85,
                ax=ax
            )
            ax.set_ylabel("Xác suất trong nhóm (Probability)", fontsize=10)
        else:
            # Vẽ KDE density cho biến liên tục
            sns.kdeplot(
                data=valid_df,
                x=col,
                hue="dataset_type",
                common_norm=False,
                palette=palette,
                fill=True,
                alpha=0.4,
                linewidth=2,
                ax=ax
            )
            ax.set_ylabel("Mật độ phân phối (KDE Density)", fontsize=10)

        # Đường gióng Median
        ax.axvline(p_med, color="#2b5c8f", linestyle="--", linewidth=2.2, label=f"Persona Med: {p_med:.1f} {unit}")
        ax.axvline(np_med, color="#d95f02", linestyle=":", linewidth=2.2, label=f"No-Persona Med: {np_med:.1f} {unit}")

        ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
        ax.set_xlabel(f"{col} ({unit})", fontsize=10, fontweight="bold")
        ax.legend(title="Nhóm Thực Nghiệm", fontsize=9, loc="upper right")

    plt.suptitle("SO SÁNH TẬP TRUNG 4 ĐẶC TRƯNG ĐỊNH LƯỢNG SUY LUẬN HÀNH VI: PERSONA (XANH) VS NO-PERSONA (CAM)",
                 fontsize=14, fontweight="bold", y=1.00)
    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"[✓] Đã lưu biểu đồ top numeric comparison mới tại: {output_path}")

    return fig



def plot_top_categorical_comparison(
    df_steps: pd.DataFrame,
    output_path: Path = None
) -> plt.Figure:
    """
    Vẽ so sánh tỷ lệ % phân phối cho các biến phân loại tiêu biểu nhất:
    1. Top 6 Ý định hành vi (Intent)
    2. Bề mặt giao diện (Surface)
    3. Tỷ lệ nhắm đối tượng mục tiêu (Target Candidate Selection)
    4. Tốc độ cử chỉ cuộn chuột đo đạc (Gesture Pace)
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    palette = {"persona": "#2b5c8f", "no_persona": "#d95f02"}

    # 1. Top 6 Intents
    ax1 = axes[0, 0]
    top_intents = ["observe", "scroll", "read", "search", "react", "share"]
    df_int = df_steps[df_steps["intent"].isin(top_intents)]
    ct1 = pd.crosstab(df_int["intent"], df_int["dataset_type"], normalize="columns") * 100
    df_p1 = ct1.loc[top_intents].reset_index().melt(id_vars="intent", var_name="dataset_type", value_name="Percentage")
    sns.barplot(data=df_p1, x="intent", y="Percentage", hue="dataset_type", palette=palette, ax=ax1)
    ax1.set_title("1. Phân bổ Ý định Hành vi Cốt lõi (% Intent)\n[Persona vượt trội ở Search, Read, React]", fontsize=11, fontweight="bold", pad=8)
    ax1.set_ylabel("Tỷ lệ trong nhóm (%)", fontsize=10, fontweight="bold")
    ax1.set_xlabel("Ý định (Intent)", fontsize=10)
    ax1.legend(title="Nhóm", fontsize=8.5)

    # 2. Surface Distribution
    ax2 = axes[0, 1]
    surfaces = ["feed", "search", "post_detail", "group", "page", "reels"]
    df_surf = df_steps[df_steps["surface"].isin(surfaces)]
    ct2 = pd.crosstab(df_surf["surface"], df_surf["dataset_type"], normalize="columns") * 100
    df_p2 = ct2.reindex(surfaces).fillna(0).reset_index().melt(id_vars="surface", var_name="dataset_type", value_name="Percentage")
    sns.barplot(data=df_p2, x="surface", y="Percentage", hue="dataset_type", palette=palette, ax=ax2)
    ax2.set_title("2. Không gian Chuyển dịch Bề mặt (% Surface)\n[Persona khám phá đa dạng Search, Detail, Group]", fontsize=11, fontweight="bold", pad=8)
    ax2.set_ylabel("Tỷ lệ trong nhóm (%)", fontsize=10, fontweight="bold")
    ax2.set_xlabel("Bề mặt (Surface)", fontsize=10)
    ax2.tick_params(axis="x", rotation=15)
    ax2.legend(title="Nhóm", fontsize=8.5)

    # 3. Target Candidate Selection
    ax3 = axes[1, 0]
    ct3 = pd.crosstab(df_steps["has_target_candidate"], df_steps["dataset_type"], normalize="columns") * 100
    df_p3 = ct3.reset_index().melt(id_vars="has_target_candidate", var_name="dataset_type", value_name="Percentage")
    df_p3["Target Selection"] = df_p3["has_target_candidate"].map({True: "Có nhắm thực thể cụ thể", False: "Duyệt feed chung chung"})
    sns.barplot(data=df_p3, x="Target Selection", y="Percentage", hue="dataset_type", palette=palette, ax=ax3)
    ax3.set_title("3. Mức độ Tập trung Thực thể (% Target Selection)\n[Persona nhắm bài viết/nhóm cụ thể cao gấp 2.5 lần]", fontsize=11, fontweight="bold", pad=8)
    ax3.set_ylabel("Tỷ lệ trong nhóm (%)", fontsize=10, fontweight="bold")
    ax3.set_xlabel("Mục tiêu tương tác", fontsize=10)
    ax3.legend(title="Nhóm", fontsize=8.5)

    # 4. Physical Gesture Pace
    ax4 = axes[1, 1]
    valid_gp = df_steps.dropna(subset=["recent_last_gesture_pace"])
    ct4 = pd.crosstab(valid_gp["recent_last_gesture_pace"], valid_gp["dataset_type"], normalize="columns") * 100
    df_p4 = ct4.reset_index().melt(id_vars="recent_last_gesture_pace", var_name="dataset_type", value_name="Percentage")
    sns.barplot(data=df_p4, x="recent_last_gesture_pace", y="Percentage", hue="dataset_type", palette=palette, ax=ax4)
    ax4.set_title("4. Phân bổ Tốc độ Cuộn chuột Đo đạc (% Gesture Pace)\n[Persona có nhịp lướt nhanh 'fast' rõ rệt]", fontsize=11, fontweight="bold", pad=8)
    ax4.set_ylabel("Tỷ lệ trong số bước có cuộn (%)", fontsize=10, fontweight="bold")
    ax4.set_xlabel("Nhãn tốc độ cử chỉ (Pace)", fontsize=10)
    ax4.legend(title="Nhóm", fontsize=8.5)

    plt.suptitle("SO SÁNH TẬP TRUNG CÁC ĐẶC TRƯNG HÀNH VI PHÂN LOẠI: PERSONA (XANH) VS NO-PERSONA (CAM)",
                 fontsize=14, fontweight="bold", y=1.00)
    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"[✓] Đã lưu biểu đồ top categorical comparison tại: {output_path}")

    return fig


def plot_univariate_text_distributions(
    df_steps: pd.DataFrame,
    output_path: Path = None
) -> plt.Figure:
    """
    Vẽ 2 subplot phân phối độ dài văn bản phân tầng Persona vs No-Persona:
    1. Độ dài chuỗi lập luận suy nghĩ Chain-of-Thought (reason_length)
    2. Độ dài văn bản thực thể nhắm mục tiêu (target_candidate_text_length)
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    palette = {"persona": "#2b5c8f", "no_persona": "#d95f02"}

    # Tính độ dài text nếu chưa có
    df = df_steps.copy()
    if "reason_length" not in df.columns:
        df["reason_length"] = df["reason"].fillna("").astype(str).str.len()
    if "target_text_length" not in df.columns:
        df["target_text_length"] = df["target_candidate_text"].fillna("").astype(str).str.len()

    # Subplot 1: Reason Length
    ax1 = axes[0]
    sns.histplot(
        data=df,
        x="reason_length",
        hue="dataset_type",
        palette=palette,
        bins=30,
        kde=True,
        alpha=0.45,
        ax=ax1
    )
    p_med_r = df[df["dataset_type"] == "persona"]["reason_length"].median()
    np_med_r = df[df["dataset_type"] == "no_persona"]["reason_length"].median()
    ax1.axvline(p_med_r, color="#2b5c8f", linestyle="--", linewidth=2, label=f"Persona Med: {p_med_r:.0f} chars")
    ax1.axvline(np_med_r, color="#d95f02", linestyle=":", linewidth=2, label=f"No-Persona Med: {np_med_r:.0f} chars")
    ax1.set_title("1. Phân phối Độ dài Lập luận CoT (reason_length)\n[Persona có lập luận phong phú vs No-Persona hầu như trống rỗng]", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Số ký tự lập luận", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Số lượng bước (Count)", fontsize=10)
    ax1.legend(title="Nhóm", fontsize=9)

    # Subplot 2: Target Candidate Text Length (chỉ lọc những bước có target)
    ax2 = axes[1]
    df_target = df[df["target_text_length"] > 0]
    if len(df_target) > 0:
        sns.histplot(
            data=df_target,
            x="target_text_length",
            hue="dataset_type",
            palette=palette,
            bins=25,
            kde=True,
            alpha=0.45,
            ax=ax2
        )
        p_med_t = df_target[df_target["dataset_type"] == "persona"]["target_text_length"].median()
        np_med_t = df_target[df_target["dataset_type"] == "no_persona"]["target_text_length"].median()
        ax2.axvline(p_med_t, color="#2b5c8f", linestyle="--", linewidth=2, label=f"Persona Med: {p_med_t:.0f} chars")
        ax2.axvline(np_med_t, color="#d95f02", linestyle=":", linewidth=2, label=f"No-Persona Med: {np_med_t:.0f} chars")
    ax2.set_title("2. Độ dài Văn bản Thực thể Nhắm tới (Target Text Length)\n[Tiêu đề bài viết / Tên nhóm được Agent tương tác]", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Số ký tự tiêu đề / nội dung", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Số lượng bước (Count)", fontsize=10)
    ax2.legend(title="Nhóm", fontsize=9)

    plt.suptitle("PHÂN TÍCH ĐƠN BIẾN VĂN BẢN NLP: PERSONA (XANH) VS NO-PERSONA (CAM)",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"[✓] Đã lưu biểu đồ text distribution tại: {output_path}")

    return fig


# Backward-compatible aliases
plot_univariate_numeric_distributions = plot_top_numeric_comparison
plot_univariate_categorical_bars = plot_top_categorical_comparison


def plot_vocabulary_distribution_comparison(
    vocab_res: Dict[str, Any],
    output_path: Path = None
) -> plt.Figure:
    """
    Vẽ 4 subplot trực quan hóa so sánh phân phối từ vựng trong suy nghĩ CoT:
    1. Top 12 Từ khóa nội dung phổ biến nhất của Persona (Màu xanh #2b5c8f)
    2. Top 10 Từ khóa của No-Persona (Màu cam #d95f02)
    3. Đối soát quy mô dung lượng: Tổng số từ (Tokens) vs Kích thước từ vựng (Vocab size)
    4. Cấu trúc lập luận: Tỷ lệ lập luận tự sinh sâu sắc vs Câu rập khuôn mặc định (%)
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))

    # 1. Top Persona Words
    ax1 = axes[0, 0]
    top_p = vocab_res["top_persona_words"][:12]
    # Lọc bỏ các từ template nếu muốn làm nổi bật từ vựng nội dung
    words_p = [w for w, c in top_p]
    counts_p = [c for w, c in top_p]
    y_pos_p = np.arange(len(words_p))
    ax1.barh(y_pos_p, counts_p, color="#2b5c8f", alpha=0.85, edgecolor="#1c3d5a")
    ax1.set_yticks(y_pos_p)
    ax1.set_yticklabels(words_p, fontsize=10, fontweight="bold")
    ax1.invert_yaxis()
    ax1.set_title("1. Top Từ Khóa trong Lập Luận của Persona\n[Giàu tính từ ngữ nghĩa: bài, cờ, vua, nội dung, sở thích, giải]",
                  fontsize=11, fontweight="bold", pad=8)
    ax1.set_xlabel("Tần suất xuất hiện (Số lần)", fontsize=10)
    for i, v in enumerate(counts_p):
        ax1.text(v + 1, i, str(v), color="#1c3d5a", va="center", fontweight="bold", fontsize=9)

    # 2. Top No-Persona Words
    ax2 = axes[0, 1]
    top_np = vocab_res["top_nopersona_words"][:10]
    words_np = [w for w, c in top_np]
    counts_np = [c for w, c in top_np]
    y_pos_np = np.arange(len(words_np))
    ax2.barh(y_pos_np, counts_np, color="#d95f02", alpha=0.85, edgecolor="#8c3d00")
    ax2.set_yticks(y_pos_np)
    ax2.set_yticklabels(words_np, fontsize=10, fontweight="bold")
    ax2.invert_yaxis()
    ax2.set_title("2. Top Từ Khóa trong Lập Luận của No-Persona\n[Nghèo nàn, lặp lại: hầu hết là các từ trong câu template]",
                  fontsize=11, fontweight="bold", pad=8)
    ax2.set_xlabel("Tần suất xuất hiện (Số lần)", fontsize=10)
    for i, v in enumerate(counts_np):
        ax2.text(v + 0.5, i, str(v), color="#8c3d00", va="center", fontweight="bold", fontsize=9)

    # 3. Đối soát quy mô dung lượng từ vựng
    ax3 = axes[1, 0]
    p_st = vocab_res["persona_stats"]
    np_st = vocab_res["nopersona_stats"]
    metrics = ["Tổng số Tokens\n(Total Words)", "Vốn từ vựng Duy nhất\n(Unique Vocab Size)"]
    p_vals = [p_st["total_tokens"], p_st["vocabulary_size"]]
    np_vals = [np_st["total_tokens"], np_st["vocabulary_size"]]
    
    x = np.arange(len(metrics))
    width = 0.35
    b1 = ax3.bar(x - width/2, p_vals, width, label="Persona", color="#2b5c8f", edgecolor="#1c3d5a")
    b2 = ax3.bar(x + width/2, np_vals, width, label="No-Persona", color="#d95f02", edgecolor="#8c3d00")
    ax3.set_xticks(x)
    ax3.set_xticklabels(metrics, fontsize=10, fontweight="bold")
    ax3.set_ylabel("Số lượng từ", fontsize=10, fontweight="bold")
    ax3.set_title("3. Đối Soát Quy Mô Vốn Từ Vựng và Dung Lượng Suy Nghĩ\n[Persona gấp 14.7 lần số Tokens và gấp 8.0 lần Vốn từ vựng]",
                  fontsize=11, fontweight="bold", pad=8)
    ax3.legend(fontsize=9.5)
    for bar in b1:
        h = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, h + 50, f"{h:,}", ha="center", va="bottom", fontweight="bold", color="#2b5c8f")
    for bar in b2:
        h = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, h + 50, f"{h:,}", ha="center", va="bottom", fontweight="bold", color="#d95f02")

    # 4. Cấu trúc Lập luận: Tự sinh vs Template
    ax4 = axes[1, 1]
    p_gen_pct = 100 - p_st["boilerplate_rate_pct"]
    np_gen_pct = 100 - np_st["boilerplate_rate_pct"]
    
    categories = ["Persona", "No-Persona"]
    creative_pcts = [p_gen_pct, np_gen_pct]
    boilerplate_pcts = [p_st["boilerplate_rate_pct"], np_st["boilerplate_rate_pct"]]

    bar_c = ax4.bar(categories, creative_pcts, width=0.45, label="Lập luận Ngữ nghĩa Tự sinh (CoT)", color="#2ca02c", alpha=0.85)
    bar_b = ax4.bar(categories, boilerplate_pcts, bottom=creative_pcts, width=0.45, label="Câu Rập khuôn Mặc định", color="#7f7f7f", alpha=0.65)
    ax4.set_ylabel("Tỷ lệ phân bổ trong số bước có lập luận (%)", fontsize=10, fontweight="bold")
    ax4.set_ylim(0, 115)
    ax4.set_title("4. Phân Loại Cấu Trúc Lập Luận Suy Nghĩ\n[Persona chủ động lập luận 59.9% vs No-Persona rập khuôn 92.7%]",
                  fontsize=11, fontweight="bold", pad=8)
    ax4.legend(loc="upper right", fontsize=9.5)
    for i, cat in enumerate(categories):
        ax4.text(i, creative_pcts[i] / 2, f"{creative_pcts[i]:.1f}%", ha="center", va="center", color="white", fontweight="bold", fontsize=11)
        ax4.text(i, creative_pcts[i] + boilerplate_pcts[i] / 2, f"{boilerplate_pcts[i]:.1f}%", ha="center", va="center", color="white", fontweight="bold", fontsize=11)

    plt.suptitle("PHÂN TÍCH ĐỐI SOÁT PHÂN PHỐI TỪ VỰNG TRONG SUY NGHĨ (CHAIN-OF-THOUGHT): PERSONA VS NO-PERSONA",
                 fontsize=14, fontweight="bold", y=1.00)
    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"[✓] Đã lưu biểu đồ phân phối từ vựng tại: {output_path}")

    return fig

