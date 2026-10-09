import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = Path(__file__).resolve().parent.parent

FIGURES_DIR = PROJECT_ROOT / "output" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Liberation Sans']
plt.rcParams['axes.edgecolor'] = '#7f8c8d'
plt.rcParams['axes.linewidth'] = 1.0

PERSONA_ORDER = ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']
PERSONA_LABELS = {
    'vn_fb_001': 'vn_fb_001\n(Thiết kế đồ họa)',
    'vn_fb_002': 'vn_fb_002\n(Gia đình / Nghệ An)',
    'vn_fb_003': 'vn_fb_003\n(Bảo vệ ca đêm)',
    'vn_fb_004': 'vn_fb_004\n(Phục vụ nhà hàng)',
    'vn_fb_005': 'vn_fb_005\n(Thợ cơ khí)',
    'vn_fb_006': 'vn_fb_006\n(Gen X BĐS)',
}

# Dữ liệu cơ cấu % động lực nội tại chính xác theo bảng Slide 2.5.1
DATA_SEARCH = {
    'vn_fb_001': [
        ('Công nghệ AI thiết kế', 100.0, '#3498db', 'Tìm công cụ AI kiến trúc & 3D')
    ],
    'vn_fb_002': [
        ('Không tìm kiếm (Thụ động)', 100.0, '#bdc3c7', 'Thỏa mãn với bảng tin gia đình/tâm linh')
    ],
    'vn_fb_003': [
        ('Ẩm thực đường phố', 50.0, '#e67e22', 'Tìm quán bún trộn Đà Nẵng ăn đêm'),
        ('Giao lưu bạn bè', 50.0, '#9b59b6', 'Kết nối quán xá sau ca trực')
    ],
    'vn_fb_004': [
        ('Thể thao bóng đá', 100.0, '#e74c3c', 'Tìm highlight bóng đá khi Feed thiếu')
    ],
    'vn_fb_005': [
        ('Tò mò Khoa học vũ trụ', 100.0, '#2980b9', 'Tìm giờ ngắm Sao Hỏa đối lập Đà Nẵng')
    ],
    'vn_fb_006': [
        ('Khảo sát BĐS', 66.7, '#16a085', 'Tra cứu quy hoạch & giá đất Cái Răng'),
        ('Thận trọng kiểm chứng', 33.3, '#7f8c8d', 'Thẩm định tính xác thực dự án')
    ]
}

DATA_COMMENT = {
    'vn_fb_001': [
        ('Tò mò chuyên môn 3D', 66.7, '#2980b9', 'Góp ý góc phối cảnh & ánh sáng'),
        ('Bố cục thiết kế', 33.3, '#3498db', 'Trao đổi nghiệp vụ đồ họa')
    ],
    'vn_fb_002': [
        ('Hòa nhã thiện lành', 100.0, '#27ae60', 'Chúc an lành & giữ sự thiện lương')
    ],
    'vn_fb_003': [
        ('Món ăn Việt', 38.9, '#d35400', 'Hỏi công thức & địa chỉ ăn uống'),
        ('Ăn vặt đường phố', 33.3, '#e67e22', 'Hỏi quán tokbokki bằng từ lóng'),
        ('Giao lưu bạn bè', 11.1, '#9b59b6', 'Tương tác thân mật Gen Z'),
        ('Khác', 16.7, '#95a5a6', 'Tò mò & văn phong địa phương')
    ],
    'vn_fb_004': [
        ('Không bình luận (Lướt Reels)', 100.0, '#bdc3c7', 'Xem video thụ động, ngại gõ chữ')
    ],
    'vn_fb_005': [
        ('Tri ân Lịch sử Dân tộc', 58.3, '#c0392b', 'Tri ân Đại tướng Võ Nguyên Giáp'),
        ('Tò mò Lịch sử', 33.3, '#2980b9', 'Tìm hiểu chiến dịch hào hùng'),
        ('Địa phương', 8.3, '#16a085', 'Gắn kết cội nguồn')
    ],
    'vn_fb_006': [
        ('Đời sống Nam Bộ', 100.0, '#e67e22', 'Hỏi thăm thực tế sinh hoạt miền Tây')
    ]
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8.5))
fig.subplots_adjust(left=0.10, right=0.98, top=0.88, bottom=0.10, wspace=0.25)

def render_panel(ax, data_dict, title, is_search=True):
    y_positions = np.arange(len(PERSONA_ORDER))
    
    for y_idx, persona in enumerate(PERSONA_ORDER):
        segments = data_dict[persona]
        current_left = 0.0
        is_inactive = (persona == 'vn_fb_002' and is_search) or (persona == 'vn_fb_004' and not is_search)
        
        for seg_label, pct, color, goal in segments:
            hatch = '///' if is_inactive else None
            alpha = 0.6 if is_inactive else 0.92
            
            bar = ax.barh(
                y_idx, pct, left=current_left, height=0.58,
                color=color, edgecolor='#2c3e50', linewidth=1.1,
                hatch=hatch, alpha=alpha
            )
            
            # Ghi text vào trong thanh nếu đủ rộng
            mid_x = current_left + pct / 2.0
            if pct >= 25.0:
                ax.text(
                    mid_x, y_idx, f"{seg_label}\n{pct:.1f}%",
                    ha='center', va='center',
                    fontsize=8.5, fontweight='bold',
                    color='#ffffff' if not is_inactive else '#2c3e50'
                )
            elif pct >= 15.0:
                ax.text(
                    mid_x, y_idx, f"{pct:.1f}%",
                    ha='center', va='center',
                    fontsize=8.0, fontweight='bold',
                    color='#ffffff' if not is_inactive else '#2c3e50'
                )
                
            current_left += pct
            
        # Thêm ghi chú mục đích nhận thức cốt lõi phía trên hoặc dưới thanh
        primary_goal = segments[0][3]
        ax.text(
            102, y_idx, f"🎯 {primary_goal}",
            ha='left', va='center',
            fontsize=8.5, fontweight='bold', color='#1a365d'
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels([PERSONA_LABELS[p] for p in PERSONA_ORDER], fontsize=10, fontweight='bold', color='#2c3e50')
    ax.invert_yaxis()
    ax.set_xlim(0, 165)  # dành khoảng trống bên phải cho callout mục đích
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xticklabels(['0%', '20%', '40%', '60%', '80%', '100%'], fontsize=9.5, fontweight='bold', color='#34495e')
    ax.set_xlabel('Cơ cấu Động lực Nhận thức Nội tại (%)', fontsize=10.5, fontweight='bold', color='#2c3e50')
    ax.set_title(title, fontsize=12, fontweight='bold', color='#1a365d', pad=12)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.axvline(100, color='#e74c3c', linestyle=':', linewidth=1.2, alpha=0.8)

render_panel(ax1, DATA_SEARCH, 'A. ĐỘNG LỰC HÀNH VI TÌM KIẾM (SEARCH)\n(Cơ cấu lý do thôi thúc Agent chủ động gõ từ khóa)', is_search=True)
render_panel(ax2, DATA_COMMENT, 'B. ĐỘNG LỰC HÀNH VI BÌNH LUẬN (COMMENT)\n(Cơ cấu lý do thôi thúc Agent viết lời phản hồi)', is_search=False)

fig.suptitle('KIỂM CHỨNG H2 (SLIDE 2.5.1): CƠ CẤU ĐỘNG LỰC NỘI TẠI KHI THỰC HIỆN SEARCH & COMMENT', fontsize=14, fontweight='bold', color='#1a365d', y=0.97)

out_test = FIGURES_DIR / "slide2_5_1_search_and_comment_test.png"
fig.savefig(out_test, dpi=300)
plt.close(fig)
print(f"Đã lưu hình test thành công tại: {out_test}")
