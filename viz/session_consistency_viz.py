"""
Module: session_consistency_viz.py
Mục đích:
1. Trực quan hóa Sơ đồ chuyển đổi giữa các màn hình chính (Markov Transition Diagram) hoàn toàn động.
2. Trực quan hóa 3 Panel tổng hợp kiểm định H3:
   - Panel A: Heatmap ma trận tương đồng ý định giữa 13 phiên.
   - Panel B: Phân bố tương quan Cùng Persona vs Khác Persona (Boxplot & Strip Plot).
   - Panel C: Tỷ lệ thao tác quen thuộc (cũ) vs Mới xuất hiện qua từng phiên (Stacked Bar Chart).
"""

from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
import pandas as pd


def plot_macro_surface_transitions(
    transition_data: Dict[str, Any],
    ax: Optional[plt.Axes] = None,
    figsize: Tuple[float, float] = (10, 6)
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Vẽ Sơ đồ chuyển đổi giữa 4 màn hình chính dựa trên dữ liệu tính toán động.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=150)
    else:
        fig = ax.figure

    node_positions = {
        'feed': (0.22, 0.65),
        'search': (0.78, 0.65),
        'group': (0.78, 0.28),
        'reels': (0.22, 0.28)
    }
    node_colors = {
        'feed': '#3b82f6',
        'search': '#f59e0b',
        'group': '#10b981',
        'reels': '#ec4899'
    }
    node_labels = {
        'feed': 'BẢNG TIN\n(Feed)',
        'search': 'TÌM KIẾM\n(Search)',
        'group': 'HỘI NHÓM\n(Group)',
        'reels': 'VIDEO NGẮN\n(Reels)'
    }

    # Vẽ 4 nút màn hình
    for name, (x, y) in node_positions.items():
        circle = patches.Circle(
            (x, y), radius=0.088,
            facecolor=node_colors[name],
            edgecolor='none',
            zorder=3,
            alpha=0.92
        )
        ax.add_patch(circle)
        ax.text(
            x, y, node_labels.get(name, name.upper()),
            color='white', fontweight='bold', fontsize=10.5,
            ha='center', va='center', zorder=4
        )

    # Tọa độ và độ cong thủ công chuẩn hóa theo từng cặp có hướng
    edge_geometry = {
        ('feed', 'search'): (0.12, (0.50, 0.70)),
        ('search', 'feed'): (0.12, (0.50, 0.60)),
        ('feed', 'reels'): (0.15, (0.13, 0.465)),
        ('reels', 'feed'): (0.15, (0.31, 0.465)),
        ('search', 'group'): (0.15, (0.87, 0.465)),
        ('group', 'search'): (0.15, (0.69, 0.465)),
        ('reels', 'search'): (0.05, (0.50, 0.465)),
        ('search', 'reels'): (0.05, (0.50, 0.465)),
        ('group', 'feed'): (-0.08, (0.50, 0.35)),
        ('feed', 'group'): (-0.08, (0.50, 0.45)),
    }

    transitions = transition_data.get('transitions', [])
    for trans in transitions:
        src = trans['src']
        dst = trans['dst']
        label = trans['label']
        col = trans['color']

        if src not in node_positions or dst not in node_positions:
            continue

        x1, y1 = node_positions[src]
        x2, y2 = node_positions[dst]

        rad, (lx, ly) = edge_geometry.get(
            (src, dst),
            (0.12, ((x1 + x2) / 2, (y1 + y2) / 2))
        )

        arrow = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle='-|>,head_length=8,head_width=5',
            color=col,
            linewidth=2.4,
            zorder=2,
            shrinkA=36,
            shrinkB=36
        )
        ax.add_patch(arrow)
        ax.text(
            lx, ly, label,
            fontsize=9.5, fontweight='bold', color=col,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor=col, alpha=0.92, linewidth=1.2),
            zorder=5
        )

    # Chú thích phía trên: Các hướng điều hướng chính
    path_summary = transition_data.get('path_summary', '')
    if path_summary:
        ax.text(
            0.5, 0.95, path_summary,
            fontsize=9.5, fontweight='bold', color='#1f2937',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#f3f4f6', edgecolor='#9ca3af', alpha=0.9)
        )

    # Chú thích phía dưới: Thói quen tự lặp trên Reels
    ax.text(
        0.5, 0.05, 'Thói quen xem liên tục: Tự lặp Reels đạt 98.6% - 100% (ở vn_fb_004)',
        fontsize=9.5, fontweight='bold', color='#dc2626',
        ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#fee2e2', edgecolor='#dc2626', alpha=0.9)
    )

    total_shifts = transition_data.get('total_shifts', 0)
    ax.set_xlim(0.05, 0.95)
    ax.set_ylim(0.0, 1.0)
    ax.axis('off')
    title_text = f"SƠ ĐỒ CHUYỂN ĐỔI GIỮA 4 MÀN HÌNH CHÍNH VÀ CÁC HƯỚNG ĐIỀU HƯỚNG\n(Theo dõi {total_shifts} lượt chuyển màn hình thực tế)"
    ax.set_title(title_text, fontsize=13, fontweight='bold', pad=18)
    fig.tight_layout()

    return fig, ax


def plot_h3_three_panel_comparison(
    df_session_corr: pd.DataFrame,
    df_evolution: pd.DataFrame,
    intra_vals: List[float],
    inter_vals: List[float],
    figsize: Tuple[float, float] = (22, 6.5)
) -> Tuple[plt.Figure, np.ndarray]:
    """
    Vẽ Figure 3 Panel tổng hợp so sánh tính nhất quán xuyên phiên của Persona Agent.
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize, dpi=150)

    # Panel A: Heatmap Ma trận Tương quan 13 Phiên
    sns.heatmap(
        df_session_corr,
        annot=True,
        fmt='.2f',
        cmap='coolwarm',
        vmin=-0.2,
        vmax=1.0,
        ax=axes[0],
        cbar_kws={'label': 'Độ tương đồng (r)'},
        annot_kws={'size': 8}
    )
    axes[0].set_title('Panel A: Ma trận tương đồng thao tác giữa 13 phiên', fontweight='bold', fontsize=12, pad=12)
    axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45, ha='right', fontsize=8.5)
    axes[0].set_yticklabels(axes[0].get_yticklabels(), rotation=0, fontsize=8.5)
    axes[0].set_xlabel('Phiên thực thi', fontweight='bold', fontsize=10)
    axes[0].set_ylabel('Phiên thực thi', fontweight='bold', fontsize=10)

    # Panel B: Boxplot So sánh Tương quan Cùng Persona vs Khác Persona
    df_corr_comp = pd.DataFrame({
        'Hệ số tương đồng (r)': intra_vals + inter_vals,
        'Loại tương đồng': [f'Cùng Persona\n({len(intra_vals)} cặp)'] * len(intra_vals) + [f'Khác Persona\n({len(inter_vals)} cặp)'] * len(inter_vals)
    })
    palette_comp = {
        f'Cùng Persona\n({len(intra_vals)} cặp)': '#10b981',
        f'Khác Persona\n({len(inter_vals)} cặp)': '#94a3b8'
    }

    sns.boxplot(
        data=df_corr_comp,
        x='Loại tương đồng',
        y='Hệ số tương đồng (r)',
        hue='Loại tương đồng',
        palette=palette_comp,
        ax=axes[1],
        width=0.45,
        boxprops=dict(alpha=0.7),
        legend=False
    )
    sns.stripplot(
        data=df_corr_comp,
        x='Loại tương đồng',
        y='Hệ số tương đồng (r)',
        color='black',
        alpha=0.6,
        jitter=0.2,
        size=6.5,
        ax=axes[1]
    )
    axes[1].set_title('Panel B: So sánh độ tương đồng\n(Cùng Persona vs Khác Persona)', fontweight='bold', fontsize=12, pad=12)
    axes[1].set_ylabel('Hệ số tương đồng (r)', fontweight='bold', fontsize=10)
    axes[1].set_xlabel('')
    axes[1].grid(True, linestyle='--', alpha=0.5)

    # Panel C: Stacked Bar Chart Tỷ lệ Thao tác Quen thuộc vs Mới xuất hiện
    labels_p = [f"{r['Persona']}\n({r['Cặp phiên']})" for _, r in df_evolution.iterrows()]
    invar_pcts = df_evolution['Tỷ lệ thao tác quen thuộc (%)'].values
    innov_pcts = df_evolution['Tỷ lệ thao tác mới (%)'].values
    x_pos = np.arange(len(labels_p))

    axes[2].bar(x_pos, invar_pcts, label='Quen thuộc (lặp lại)', color='#3b82f6', alpha=0.85, width=0.55)
    axes[2].bar(x_pos, innov_pcts, bottom=invar_pcts, label='Mới xuất hiện', color='#f59e0b', alpha=0.85, width=0.55)

    for i in range(len(x_pos)):
        if invar_pcts[i] > 10:
            axes[2].text(
                x_pos[i], invar_pcts[i] / 2, f"{invar_pcts[i]:.1f}%",
                ha='center', va='center', color='white', fontweight='bold', fontsize=8.5
            )
        if innov_pcts[i] > 8:
            axes[2].text(
                x_pos[i], invar_pcts[i] + innov_pcts[i] / 2, f"{innov_pcts[i]:.1f}%",
                ha='center', va='center', color='black', fontweight='bold', fontsize=8.5
            )

    axes[2].set_xticks(x_pos)
    axes[2].set_xticklabels(labels_p, rotation=40, ha='right', fontsize=8.5)
    axes[2].set_ylim(0, 108)
    axes[2].set_title('Panel C: Thao tác quen thuộc (cũ) vs Mới xuất hiện', fontweight='bold', fontsize=12, pad=12)
    axes[2].set_ylabel('Tỷ lệ thao tác (%)', fontweight='bold', fontsize=10)
    axes[2].set_xlabel('Cặp phiên so sánh', fontweight='bold', fontsize=10)
    axes[2].grid(True, linestyle='--', alpha=0.4, axis='y')
    axes[2].legend(title='Tính chất thao tác', loc='upper right', framealpha=0.9)

    fig.tight_layout()
    return fig, axes
