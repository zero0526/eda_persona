"""Xây dựng và thực thi notebooks/notebook_action_logs.ipynb hoàn chỉnh với:
- Phần mở đầu trình bày 3 giả thuyết nghiên cứu (H1, H2, H3)
- Bảng tổng quan hệ thống & bảng đối soát 6 Persona
- Phần 2: Kiểm tra chất lượng (Data Health Check) & hình thái phân phối 3 biến thời gian (start_hour_local, duration_min, frequency)
- Trực quan hóa 3 biến thời gian trên 3 subplots chuẩn mực
- Nhận định sơ bộ về độ sẵn sàng của dữ liệu cho Giả thuyết 1 (H1)
"""

import sys
import json
from pathlib import Path

# Đảm bảo mã hóa console UTF-8 an toàn
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

cells = []

# ==============================================================================
# CELL 0: MARKDOWN - TIÊU ĐỀ BÁO CÁO VÀ BỐI CẢNH NGHIÊN CỨU
# ==============================================================================
cell_0_md = """# BÁO CÁO PHÂN TÍCH DỮ LIỆU KHÁM PHÁ (EXPLORATORY DATA ANALYSIS - EDA)
## KIỂM ĐỊNH TÍNH THÍCH ỨNG LỊCH TRÌNH ($H_1$), ĐỘ TUÂN THỦ HỒ SƠ & HỢP ĐỒNG ($H_2$) VÀ DẤU ẤN HÀNH VI N-GRAM ($H_3$) CỦA TÁC TỬ TỰ TRỊ FACEBOOK (AUTONOMOUS AGENTS)

---

### Bối cảnh Thực nghiệm
Hệ thống thử nghiệm vận hành **6 Persona độc lập** (`vn_fb_001` đến `vn_fb_006`) mô phỏng người dùng mạng xã hội Facebook tại Việt Nam với các đặc trưng đa dạng về nhân khẩu học (Gen Z, thanh niên đi làm, trung niên gia đình), địa bàn sinh sống (Đà Nẵng, Cần Thơ, TP.HCM, Hà Nội, Đồng Nai), nhịp sinh học (cú đêm vs dậy sớm), thói quen tiêu thụ nội dung (Reels video ngắn vs Newsfeed video dài vs Hội nhóm chuyên sâu) và hợp đồng hành vi (pacing nhanh vs cân bằng, mức độ tương tác xã hội từ tàu ngầm đến tích cực).

Dữ liệu được thu thập từ cơ sở dữ liệu SQLite sản xuất `persona-runner.sqlite` bao gồm:
1. **Lịch trình hoạt động**: 79 cửa sổ hoạt động (`activity_windows`) do hệ thống lập lịch tự động (LLM Scheduler) khởi tạo (trong đó 13 kịch bản đã thực hiện).
2. **Nhật ký hành động**: 758 bước thao tác thực tế (`agent_live_steps`) trên trình duyệt chống phát hiện (anti-detect browser) trải dài qua 15 phiên chạy (`episodes`).
3. **Cơ chế 2 tầng bộ nhớ phiên**:
   - **Bộ nhớ dài hạn đầu phiên (`PriorLongTermMemory`)**: Sở thích cốt lõi (`core_interests`), chủ đề né tránh (`avoid_topics`), luồng khám phá ban đầu (`exploration_threads`), trang/nhóm quen thuộc (`known_affinities`) và ảnh chụp thói quen tương tác (`prior_habit_snapshot`).
   - **Bộ nhớ ngắn hạn trong phiên (`ShortTermWorkingMemory`)**: Các luồng quan tâm phát sinh trong phiên (`active_threads`), bài viết đã đọc kèm dwell time thực tế (`read_posts`), hành vi mở nguồn (`opened_sources`), tìm kiếm trong phiên (`searched_topics`), nhịp nghỉ (`rest`), sự kiện thói quen (`habit_facts`) và cập nhật tri thức dài hạn (`memory_deltas`).
"""

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [line + "\n" for line in cell_0_md.split("\n")]
})

# ==============================================================================
# CELL 1: MARKDOWN - ĐỊNH NGHĨA 3 GIẢ THUYẾT NGHIÊN CỨU CỐT LÕI (H1, H2, H3)
# ==============================================================================
cell_1_md = r"""---
## 1. KHUNG LÝ THUYẾT VÀ 3 GIẢ THUYẾT NGHIÊN CỨU CỐT LÕI ($H_1, H_2, H_3$)

Để đánh giá tính xác thực, độ tin cậy và khả năng mô phỏng hành vi người thật của các tác tử tự trị, nghiên cứu thiết lập và kiểm định **3 giả thuyết chính**:

```
+---------------------------------------------------------------------------------------------------+
|                                 3 GIẢ THUYẾT NGHIÊN CỨU CỐT LÕI (EDA)                            |
+---------------------------------------------------------------------------------------------------+
|  [H1: Activity Window Alignment]           [H2: Behavioral Fidelity]       [H3: Behavioral Signatures] |
|  - Phân bổ giờ 24h vs Nghề nghiệp          - scrollCadence vs gesture_pace  - Markov Transition Matrix  |
|  - Ràng buộc thời lượng [8, 32] phút       - Social Archetype vs React/Cmt  - TF-IDF N-grams (2,3)      |
|  - Tần suất ngày vs facebook_frequency     - surface_bias vs Thực tế        - Intra vs Inter Similarity |
|  - surface_bias vs Định dạng yêu thích     - Bộ nhớ dài hạn vs Query/Read   - Không gian 2D Projection  |
+---------------------------------------------------------------------------------------------------+
```

---

### Giả thuyết 1 ($H_1$ - Activity Window Alignment)
> **Phát biểu**: *Các cửa sổ hoạt động (`ActivityWindowSchema` trong bảng `activity_windows`) được sinh ra bởi hệ thống lập lịch tự động (LLM Scheduler) có phù hợp với đặc tính nhân khẩu học, nhịp sinh học (circadian rhythm), nghề nghiệp và ràng buộc thời lượng của từng Persona hay không?*

* **Các câu hỏi và chỉ số kiểm định cụ thể**:
  1. **Nhịp sinh học 24 giờ (`start_hour_local`)**: Giờ bắt đầu cửa sổ (tính theo giờ địa phương Việt Nam UTC+7) có phản ánh đúng nhịp sống nghề nghiệp không?
     - Sinh viên / Gen Z (`vn_fb_003`): Có tập trung vào khung giờ đêm muộn (21h - 1h sáng)?
     - Nhân viên văn phòng / Thiết kế (`vn_fb_001`): Có xuất hiện các đỉnh hoạt động vào giờ nghỉ trưa (11h30 - 13h) và sau giờ tan sở (19h - 22h)?
     - Người trung niên / Gia đình (`vn_fb_005`, `vn_fb_006`): Có xu hướng hoạt động sáng sớm (6h - 8h) và buổi tối vừa phải?
  2. **Tuân thủ giới hạn thời lượng phiên (`duration_min`)**: Toàn bộ các cửa sổ lập lịch có tuân thủ nghiêm ngặt ràng buộc hợp đồng trong khoảng $[8, 32]$ phút không (Tỷ lệ vi phạm $< 8$m hoặc $> 32$m = 0%)?
  3. **Tần suất hoạt động theo ngày (`windows_per_day`)**: Số cửa sổ được xếp lịch mỗi ngày có tương xứng với mức độ sử dụng Facebook khai báo (`facebook_frequency`: Thấp, Trung bình, Cao) trong hồ sơ persona?
  4. **Thiên hướng bề mặt lập lịch (`surface_bias`)**: Tỷ trọng phân bổ các bề mặt (Reels, Newsfeed, Search, Groups) có tương thích với định dạng nội dung ưa thích (`content_consumption_format`) của từng Persona không?

---

### Giả thuyết 2 ($H_2$ - Persona & Contract Behavioral Fidelity)
> **Phát biểu**: *Dòng hành vi thực thi được ghi nhận trong nhật ký hành động (`agent_live_steps`) có tuân thủ trung thực với các ràng buộc trong hợp đồng hành vi (`BehavioralContractSchema` về pacing, tỷ lệ tương tác, định hướng bề mặt) và hồ sơ bản sắc nhân vật (`BotContextSchema` về sở thích, từ khóa tìm kiếm, văn phong)?*

* **Các câu hỏi và chỉ số kiểm định cụ thể**:
  1. **Độ trung thực về nhịp độ vật lý (Pacing Fidelity)**:
     - Nhóm Persona có hợp đồng `scrollCadence = "quick"` (`vn_fb_001`, `vn_fb_002`, `vn_fb_005`) có phản ánh đúng nhãn cử chỉ thực tế `gesture_pace = "fast"` với thời gian thực hiện cuộn chuột (`gesture_ms`) ngắn hơn có ý nghĩa thống kê?
     - Nhóm Persona có hợp đồng `scrollCadence = "balanced"` (`vn_fb_003`, `vn_fb_004`, `vn_fb_006`) có phản ánh nhãn `gesture_pace = "careful"` với `gesture_ms` dài hơn?
  2. **Độ trung thực về mức độ tương tác xã hội (Social Archetypes)**:
     - Nhóm "Tàu ngầm chỉ hóng chuyện" (`vn_fb_004`, `vn_fb_006`) có tỷ lệ tương tác chủ động (`react`, `comment`, `share`) thấp hơn đáng kể so với nhóm tích cực (`vn_fb_001`, `vn_fb_002`, `vn_fb_003`, `vn_fb_005`)?
  3. **Độ trung thực về bề mặt thực thi (`surface`)**:
     - Tỷ lệ bước thực thi thực tế trên `reels`, `feed`, `group`, `detail`, `search` có bám sát thiên hướng của Persona (ví dụ `vn_fb_004` thích video ngắn có tỷ lệ `reels` vượt trội; `vn_fb_006` thích hội nhóm có tỷ lệ `group`/`detail` vượt trội)?
  4. **Độ khớp ngữ nghĩa giữa hành vi và bộ nhớ dài hạn**:
     - 100% các từ khóa tìm kiếm (`query`) và bài viết đã đọc (`read_posts`) có thuộc về sở thích cốt lõi (`core_interests`) và luồng khám phá (`exploration_threads`) không?
     - Có xảy ra bất kỳ vi phạm nào với danh mục chủ đề né tránh (`avoid_topics`) không?
  5. **Văn phong và ngôn ngữ phát ngôn**:
     - Các đoạn bình luận do agent tự sáng tác (`comments_generated` / `recent_own_writing`) có khớp với đại từ xưng hô, độ tuổi và phương ngữ vùng miền không?

---

### Giả thuyết 3 ($H_3$ - Persona Behavioral Signatures & N-grams)
> **Phát biểu**: *Sau các phiên chạy của cùng một Persona, có xuất hiện các mẫu chuỗi hành động tuần tự (bigram, trigram) mang tính đặc trưng ổn định (behavioral signatures), phân tách rõ rệt giữa các Persona khác nhau (inter-persona distinctiveness) và tái lặp giữa các phiên của cùng một Persona (intra-persona consistency) hay không?*

* **Các câu hỏi và chỉ số kiểm định cụ thể**:
  1. **Mô hình hóa chuỗi Markov (Markov Transition Probabilities)**:
     - Xác suất chuyển trạng thái $P(S_{t+1} \mid S_t)$ trên không gian `intent@surface` có tạo nên các ma trận chuyển trạng thái đặc thù cho từng Persona (ví dụ: `scroll -> scroll` lướt nhanh vs `scroll -> read` đọc kỹ vs `read -> scroll_comments` đào sâu thảo luận)?
  2. **Dấu ấn hành vi qua cụm N-gram (Bigram & Trigram TF-IDF)**:
     - Sử dụng TF-IDF trích xuất top cụm hành động đặc trưng nhất của từng Persona (ví dụ `next@reels -> next@reels` của `vn_fb_004`, `scroll@feed -> read@detail -> scroll_comments@detail` của `vn_fb_001`, `search@search -> open@group` của `vn_fb_006`).
  3. **Khoảng cách tương đồng liên phiên (Cosine Similarity Matrix)**:
     - Vector hóa chuỗi hành động từng Episode bằng N-gram TF-IDF.
     - Kiểm định: Độ tương đồng nội bộ giữa các phiên của cùng một Persona ($Similarity_{\text{intra}}$) có cao hơn đáng kể so với độ tương đồng giữa các Persona khác nhau ($Similarity_{\text{inter}}$) hay không?
"""

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [line + "\n" for line in cell_1_md.split("\n")]
})

# ==============================================================================
# CELL 2: CODE - THIẾT LẬP MÔI TRƯỜNG, THƯ VIỆN & CẤU HÌNH ĐỒ HỌA
# ==============================================================================
cell_2_code = """# ==============================================================================
# BƯỚC 1: THIẾT LẬP MÔI TRƯỜNG, THƯ VIỆN & CẤU HÌNH ĐỒ HỌA
# ==============================================================================

import os
import sys
import json
import warnings
from datetime import datetime
from pathlib import Path
from collections import Counter

# Khoa học dữ liệu & Thống kê
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA

# Đồ họa & Trực quan hóa
import matplotlib.pyplot as plt
import seaborn as sns

# Tự động nạp cấu hình thư mục gốc vào sys.path để import loaders
CURRENT_DIR = Path.cwd()
PROJECT_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name == "notebooks" else CURRENT_DIR
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Cấu hình nạp ActionLoader chuyên dụng (đã đóng gói toàn bộ logic truy vấn SQL)
from loaders.action_loader import ActionLoader, SessionLog, PersonaActionHistory

# Tắt cảnh báo không cần thiết
warnings.filterwarnings('ignore')

# Thiết lập hiển thị bảng Pandas
pd.set_option('display.max_columns', 35)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: f'{x:.4f}' if abs(x) < 100 else f'{x:.2f}')

# Thiết lập phong cách đồ họa Seaborn & Matplotlib chuẩn khoa học
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'sans-serif']
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['figure.dpi'] = 120
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10

# Bảng màu đại diện đồng nhất cho 6 Persona xuyên suốt báo cáo
PERSONA_PALETTE = {
    'vn_fb_001': '#1f77b4',  # Lam đậm
    'vn_fb_002': '#ff7f0e',  # Cam
    'vn_fb_003': '#2ca02c',  # Lục
    'vn_fb_004': '#d62728',  # Đỏ
    'vn_fb_005': '#9467bd',  # Tím
    'vn_fb_006': '#8c564b',  # Nâu
}

print("✅ Môi trường phân tích và đồ họa đã sẵn sàng!")
print(f"   - Thư mục dự án: {PROJECT_ROOT}")
"""

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [line + "\n" for line in cell_2_code.split("\n")]
})

# ==============================================================================
# CELL 3: CODE - NẠP DỮ LIỆU ĐA TẦNG VÀ THỐNG KÊ TỔNG QUAN (KHÔNG CHỨA SQL TRỰC TIẾP)
# ==============================================================================
cell_3_code = """# ==============================================================================
# BƯỚC 2: NẠP DỮ LIỆU ĐA TẦNG VÀ THỐNG KÊ TỔNG QUAN HỆ THỐNG
# ==============================================================================

# 1. Khởi tạo ActionLoader (toàn bộ logic truy vấn SQL đã được đóng gói bên ngoài)
loader = ActionLoader()

# 2. Nạp dữ liệu đa tầng thông qua các hàm tiện ích
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)
df_sessions = loader.to_unified_sessions_dataframe(histories)
df_memory = loader.to_unified_memory_evolution_dataframe(histories)
df_windows = loader.load_activity_windows()
persona_profiles, contracts_dict = loader.load_persona_profiles_and_contracts()

# 3. Thống kê nhanh ở dạng bảng: Số persona, số session, số lượng bước hành động,
#    số kịch bản đã lên kế hoạch và số kịch bản đã thực hiện
df_summary_total, df_summary_by_persona = loader.get_dataset_summary_tables(
    personas_history=histories,
    df_windows=df_windows
)

print("=== 1. BẢNG THỐNG KÊ TỔNG QUAN HỆ THỐNG (EXECUTIVE SUMMARY) ===")
display(df_summary_total)

print("\\n=== 2. BẢNG THỐNG KÊ CHI TIẾT THEO TỪNG PERSONA ===")
display(df_summary_by_persona)
"""

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [line + "\n" for line in cell_3_code.split("\n")]
})

# ==============================================================================
# CELL 4: CODE - BẢNG ĐỐI SOÁT HỒ SƠ 6 PERSONA & KIỂM TRA TÍNH TOÀN VẸN
# ==============================================================================
cell_4_code = """# ==============================================================================
# BƯỚC 3: BẢNG ĐỐI SOÁT HỒ SƠ 6 PERSONA & KIỂM TRA TÍNH TOÀN VẸN (SANITY CHECK)
# ==============================================================================

# Lấy bảng đối soát thuộc tính đầy đủ qua hàm của ActionLoader
df_persona_overview = loader.get_persona_overview_dataframe(
    persona_profiles=persona_profiles,
    contracts_dict=contracts_dict,
    personas_history=histories,
    df_windows=df_windows
)

print("=== BẢNG TỔNG QUAN THUỘC TÍNH 6 PERSONA VÀ CỠ MẪU SUPPORT (N=6) ===")
display(df_persona_overview)

# Kiểm tra phân bổ nhóm độc lập để đảm bảo cỡ mẫu support
print("\\n=== KIỂM TRA PHÂN BỔ CÁC NHÓM THUỘC TÍNH CHÍNH ===")
print("1. Phân bổ Định dạng Nội dung Ưa thích:")
print(df_persona_overview['Định dạng ưa thích'].value_counts().to_string())

print("\\n2. Phân bổ Mức độ Sinh hoạt Hội nhóm:")
print(df_persona_overview['Mức độ nhóm'].value_counts().to_string())

print("\\n3. Phân bổ Hợp đồng Nhịp độ Pacing (scrollCadence):")
print(df_persona_overview['Nhịp Pacing'].value_counts().to_string())

print("\\n4. Phân bổ Giới tính:")
print(df_persona_overview['Giới tính'].value_counts().to_string())
"""

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [line + "\n" for line in cell_4_code.split("\n")]
})

# ==============================================================================
# CELL 5: MARKDOWN - PHẦN 2: KIỂM TRA CHẤT LƯỢNG & PHÂN PHỐI CÁC BIẾN THỜI GIAN (H1)
# ==============================================================================
cell_5_md = """---
## 2. KIỂM TRA CHẤT LƯỢNG DỮ LIỆU & HÌNH THÁI PHÂN PHỐI CÁC BIẾN THỜI GIAN ($H_1$)

Trước khi tiến hành kiểm định các giả thuyết sâu về tính thích ứng lịch trình ($H_1$), bước khảo sát này tập trung đánh giá nhanh tính toàn vẹn (Data Health Check) và hình thái phân phối (Distribution Profiling) của **4 biến thời gian cốt lõi**:
1. **`start_hour_local`**: Giờ bắt đầu phiên hoạt động (quy đổi theo giờ địa phương Việt Nam UTC+7).
2. **`duration_min`**: Thời lượng cửa sổ hoạt động (phút) đối soát với giới hạn hợp đồng $[8, 32]$ phút.
3. **`daily_windows`**: Tần suất số phiên mỗi ngày của từng Persona.
4. **`gap_hours`**: Khoảng cách thời gian (giờ) giữa các lần thực thi liên tiếp của cùng một Persona.
"""

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [line + "\n" for line in cell_5_md.split("\n")]
})

# ==============================================================================
# CELL 6: CODE - DATA HEALTH CHECK & THAM SỐ HÌNH THÁI PHÂN PHỐI
# ==============================================================================
cell_6_code = """# ==============================================================================
# BƯỚC 4: DATA HEALTH CHECK & BẢNG THAM SỐ HÌNH THÁI PHÂN PHỐI (DISTRIBUTION PROFILE)
# ==============================================================================

# 1. Đánh giá tính toàn vẹn & kiểm tra vi phạm biên hợp đồng
df_health, df_dist_stats = loader.get_temporal_data_health_check(df_windows)

print("=== BẢNG 1: ĐÁNH GIÁ TÍNH TOÀN VẸN & MIỀN GIÁ TRỊ HỢP LỆ (DATA HEALTH CHECK) ===")
display(df_health)

print("\\n=== BẢNG 2: THAM SỐ HÌNH THÁI PHÂN PHỐI CÁC BIẾN THỜI GIAN (DISTRIBUTION PROFILE) ===")
display(df_dist_stats)

# 2. Phân rã tham số thời gian chi tiết theo từng Persona
df_temporal_by_persona = loader.get_temporal_by_persona_stats(df_windows)
print("\\n=== BẢNG 3: ĐẶC TRƯNG THỜI GIAN PHÂN RÃ THEO TỪNG PERSONA ===")
display(df_temporal_by_persona)
"""

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [line + "\n" for line in cell_6_code.split("\n")]
})

# ==============================================================================
# CELL 7: CODE - TRỰC QUAN HÓA HÌNH THÁI PHÂN PHỐI (4 SUBPLOTS - 2x2 GRID)
# ==============================================================================
cell_7_code = """# ==============================================================================
# BƯỚC 5: TRỰC QUAN HÓA HÌNH THÁI PHÂN PHỐI 4 BIẾN THỜI GIAN (2x2 GRID)
# ==============================================================================

fig = loader.plot_temporal_distribution_overview(
    df_windows=df_windows,
    palette=PERSONA_PALETTE
)
plt.show()
"""

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [line + "\n" for line in cell_7_code.split("\n")]
})

cell_8_md = r"""---
### Nhận định Nhanh từ Thống kê Mô tả & Hình thái Phân phối:

1. **Về Giờ bắt đầu phiên (`start_hour_local`) - Tính Đa đỉnh (Multimodality)**:
   - Phân phối giờ bắt đầu có tính **đa đỉnh (multimodal)** rõ rệt ($\text{Kurtosis} = -1.58$, $\text{Skewness} = -0.04$).
   - Dữ liệu tập trung vào 3 cụm đỉnh sinh hoạt: Sáng sớm ($7 - 8$h), Nghỉ trưa ($12 - 13$h) và Buổi tối ($20 - 21$h), phản ánh sự tồn tại của các nhóm đối tượng với khung giờ hoạt động ưu thích khác nhau trong ngày.

2. **Về Cỡ mẫu và Thời lượng của `vn_fb_001` & `vn_fb_002`**:
   - Hai Persona `vn_fb_001` và `vn_fb_002` có số lượng cửa sổ lập lịch thấp hơn rất nhiều ($N = 2$ cửa sổ mỗi Persona) so với 4 Persona còn lại ($N = 17 - 20$).
   - Thời lượng trung bình của hai Persona này cũng thấp hơn đáng kể ($\mu = 13.5$ phút ở `vn_fb_001` và $\mu = 14.0$ phút ở `vn_fb_002`), không ghi nhận phiên nào vượt quá $18$ phút.

3. **Về Độ phân tán (Dispersion) của Thời lượng phiên**:
   - **Nhóm phân tán cao (`vn_fb_003`, `vn_fb_004`)**:
     - `vn_fb_003`: Độ lệch chuẩn lớn nhất hệ thống ($\sigma = 8.0$ phút), dải thời lượng trải rộng từ $10$ đến $35$ phút ($IQR = 13.0$ phút).
     - `vn_fb_004`: Thời lượng trung bình cao nhất ($\mu = 24.6$ phút, $\sigma = 6.6$ phút), dải thời lượng từ $10$ đến $35$ phút với nhiều điểm kéo dài $\ge 30$ phút (trong đó có 2 phiên đạt mức tối đa $35$ phút).
   - **Nhóm phân tán thấp (`vn_fb_005`, `vn_fb_006`)**:
     - Dù số lượng cửa sổ tương đương ($N = 19$ và $N = 20$), `vn_fb_005` có độ phân tán rất hẹp ($\sigma = 3.4$ phút), thời lượng bị bó chặt trong khoảng $[10, 20]$ phút quanh mức $\mu = 14.0$ phút.
     - `vn_fb_006` cũng có độ phân tán hẹp hơn đáng kể ($\sigma = 5.0$ phút), dải thời lượng $[8, 25]$ phút và không có phiên nào vượt quá $25$ phút.

4. **Về Khoảng cách giữa các lần thực thi liên tiếp (`gap_hours`)**:
   - **Khoảng cách sinh hoạt thường nhật ($5 - 13$ giờ, Median $8.0$ giờ)**:
     - Chiếm đại đa số ($> 86\%$ các phiên, đặc biệt trong giai đoạn vận hành ổn định từ 07/10 đến 12/10 có Mean $= 9.16$h, Median $= 8.00$h).
     - Phản ánh đúng 2 nhịp sinh hoạt tự nhiên: Giãn cách trong ngày ($5 - 8$ giờ giữa ca sáng, trưa, tối) và Giãn cách qua đêm ($10 - 13$ giờ khi bot đi ngủ).
   - **Giải thích cụ thể các điểm dị biệt lớn ($28 - 36.75$ giờ trên biểu đồ Cell 7 - Subplot 4)**:
     - Trên biểu đồ Boxplot Cell 7, xuất hiện 5 điểm ngoại lai vượt hẳn mốc 24h: `vn_fb_002` ($31.5$h), `vn_fb_003` ($36.8$h), `vn_fb_004` ($34.7$h), `vn_fb_005` ($32.0$h), `vn_fb_006` ($28.3$h).
     - **Nguyên nhân thực tế từ dữ liệu**: Đây là khoảng ngắt quãng chuyển giao hệ thống giữa ngày 05/10 và 06/10. Cụ thể: vào ngày 05/10 hệ thống chỉ lập lịch phiên buổi sáng/trưa rồi dừng lại, sang ngày 06/10 các phiên chỉ bắt đầu từ chiều tối muộn (bỏ trống toàn bộ ca sáng và trưa ngày 06/10). Khoảng trống kéo dài hơn $28 - 36$ giờ đồng hồ này đã tạo ra các điểm ngoại lai lớn trên biểu đồ, chứ không phải do bot có thói quen sinh hoạt cách ngày.
"""

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [line + "\n" for line in cell_8_md.split("\n")]
})

# ==============================================================================
# CELL 9: CODE - BƯỚC 6: KIỂM ĐỊNH ĐỘC LẬP CHI-SQUARE & HEATMAP PHẦN DƯ THEO 3 KHUNG GIỜ
# ==============================================================================
cell_9_code = """# ==============================================================================
# BƯỚC 6: KIỂM ĐỊNH ĐỘC LẬP CHI-SQUARE & HEATMAP PHẦN DƯ CHUẨN HÓA (RESIDUAL ANALYSIS)
# ==============================================================================

# 1. Tính toán bảng chéo tần số, tần số kỳ vọng, phần dư chuẩn hóa và thống kê kiểm định Chi-square
df_obs, df_exp, df_adj_res, test_stats = loader.get_temporal_contingency_and_residuals(df_windows)

# 2. Tính bảng tỷ lệ phần trăm phân bổ theo hàng (Persona)
df_pct = (df_obs.div(df_obs.sum(axis=1), axis=0) * 100).round(1)
df_pct["Tổng Windows"] = df_obs.sum(axis=1)

print("=== 1. KẾT QUẢ KIỂM ĐỊNH TÍNH ĐỘC LẬP CHI-SQUARE (CHI-SQUARE TEST OF INDEPENDENCE) ===")
display(pd.DataFrame([test_stats]))

print("\\n=== 2. BẢNG TỶ LỆ PHÂN BỔ % CÁC KHUNG GIỜ THEO TỪNG PERSONA (%) ===")
display(df_pct)

print("\\n=== 3. BẢNG PHẦN DƯ CHUẨN HÓA HIỆU CHỈNH HABERMAN (ADJUSTED STANDARDIZED RESIDUALS) ===")
display(df_adj_res.round(2))

# 3. Trực quan hóa Heatmap đối sánh 2 panel: Quan sát vs Kỳ vọng & Phần dư chuẩn hóa
fig = loader.plot_temporal_residual_heatmap(df_windows)
plt.show()
"""

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [line + "\n" for line in cell_9_code.split("\n")]
})

# ==============================================================================
# CELL 10: MARKDOWN - NHẬN ĐỊNH KIỂM ĐỊNH CHI-SQUARE & PHÂN TÍCH THIÊN HƯỚNG TƯƠNG ĐỐI
# ==============================================================================
cell_10_md = r"""---
### Nhận định từ Kiểm định Độc lập Chi-Square & Phân tích Chuyên sâu Thiên hướng Tương đối:

1. **Giới hạn Cỡ mẫu & Mức độ Khẳng định (Sample Support & Epistemic Caution)**:
   - Dù kiểm định Chi-Square cho giá trị $\chi^2 = 4.9346$ với $p = 0.8955 \gg 0.05$ và toàn bộ phần dư hiệu chỉnh đều nằm trong dải an toàn $[-1.12, +0.97]$ ($|z| < 1.96$), **chúng ta chưa đưa ra khẳng định tuyệt đối** rằng hệ thống hoàn toàn không có sự phân hóa lịch trình.
   - **Lý do**: Cỡ mẫu support hiện tại còn khá nhỏ ($N = 79$ cửa sổ trên 6 Persona; đặc biệt `vn_fb_001` và `vn_fb_002` mới chỉ có $N = 2$ cửa sổ mỗi bot). Với dung lượng mẫu này, sức mạnh thống kê (Statistical Power) của phép thử $\chi^2$ chưa đủ nhạy để phát hiện các hiệu ứng phân hóa kích thước nhỏ hoặc vừa. Do đó, đây là **quan sát thực nghiệm sơ bộ**, cần tiếp tục theo dõi khi dữ liệu tích lũy thêm.

2. **Phân tích Chuyên sâu Thiên hướng Tương đối & Nguyên nhân Cốt lõi của Từng Persona**:
   Dù các Persona có đủ dữ liệu đều tham gia vào cả 3 khung giờ (hệ thống duy trì nhịp sinh học toàn diện), khi bóc tách **tỷ lệ phần trăm phân bổ nội bộ (%)**, **dấu phần dư chuẩn hóa ($z$)**, đối soát với **hồ sơ nhân khẩu học, đặc thù công việc** và **lý do sinh cửa sổ (`window_reason`)**, ta thấy các cơ chế phân hóa rất rõ nét:

   ---
   #### A. `vn_fb_004` (Nữ 18-24 tuổi, Gen Z / Sinh viên tại Hà Nội) - Thiên hướng Ban Tối Vượt Trội (Night-skewed):
   - **Đặc trưng hành vi & hợp đồng**: Thích Video ngắn / Reels, khả năng tập trung sâu tốt, theo dõi nhiều hội nhóm giải trí.
   - **Biểu hiện dữ liệu**: Dẫn đầu toàn hệ thống về độ lệch ca tối: **$47.4\%$ tổng số phiên** ($9/19$ phiên, $z = +0.97$, $O = 9$ vs $E = 7.2$). Thời lượng trung bình cao nhất ($\mu = 24.6$ phút, có tới 6 phiên $\ge 30$ phút, đỉnh điểm đạt mức trần $35$ phút).
   - **Nguyên nhân sâu xa**:
     - *Ban ngày bị ràng buộc việc học*: Ban ngày sinh viên phải lên lớp, các phiên sáng ($07\text{h}15$) và trưa ($12\text{h}45 - 13\text{h}00$) chỉ đóng vai trò kiểm tra nhanh (`thời lượng ngắn-vừa, phù hợp kiểm tra nhanh trước khi bắt đầu ngày`).
     - *Buổi tối là thời gian rảnh rỗi chính*: Sau khi hoàn thành việc học, khung giờ $20\text{h}30 - 22\text{h}30$ là khoảng thời gian rảnh duy nhất trong ngày (`khung tối muộn tiếp tục phù hợp cho hoạt động giải trí; thời lượng dài vì đây là khung rảnh rỗi chính trong ngày`).
     - *Hiệu ứng cuốn hút của Video ngắn*: Định dạng ưa thích là Reels kết hợp với sự tập trung sâu vào ban đêm khiến thời lượng phiên bị kéo dài cực đại ($30 - 35$ phút) để xả hơi giải trí trước khi ngủ.

   ---
   #### B. `vn_fb_003` (Nam 18-24 tuổi, Bảo vệ trực on-site tại Đà Nẵng) - Hình thái Lưỡng Đỉnh (Bimodal: Sáng sớm & Tối muộn):
   - **Đặc trưng hành vi & hợp đồng**: Lao động ca trực on-site nghiêm ngặt, sở thích nghe nhạc/âm thanh, game streaming ($8-15$h/tuần), hợp đồng ưu tiên Reels ($55\%$).
   - **Biểu hiện dữ liệu**: Cấu trúc thời gian dồn mạnh vào hai đầu ngày: **Sáng sớm $41.2\%$** ($7/17$ phiên, $z = +0.69$) và **Tối muộn $41.2\%$** ($7/17$ phiên, $z = +0.31$). Ngược lại, Ca Trưa & Chiều bị nén chặt xuống mức thấp nhất hệ thống: chỉ **$17.6\%$** ($3/17$ phiên, $z = -1.06$).
   - **Nguyên nhân sâu xa**:
     - *Ràng buộc trực giác on-site giờ hành chính*: Nghề bảo vệ/an ninh đòi hỏi phải trực chốt nghiêm ngặt tại hiện trường vào ban ngày, không thể tự do mở điện thoại lướt mạng xã hội liên tục. Điều này giải thích tại sao ca Trưa & Chiều bị né tránh rõ rệt ($z = -1.06$).
     - *Thói quen kiểm tra nhanh đầu ngày*: Thức dậy sớm chuẩn bị vào ca trực, bot mở Facebook lướt tin tức trong $10 - 12$ phút (`phiên nhanh trước khi bắt đầu công việc on-site`).
     - *Xả hơi sau ca trực buổi tối*: Sau khi hết ca trực về nhà, buổi tối là khoảng thời gian an toàn duy nhất để bot thỏa mãn nhu cầu giải trí số (nghe nhạc, game, streaming, Reels). Bộ lập lịch chủ động bố trí các phiên dài $25 - 35$ phút vào tối thứ Sáu và thứ Bảy (`phù hợp khung giải trí cuối tuần và streaming 8-15 giờ/tuần`).

   ---
   #### C. `vn_fb_005` (Nam 35-44 tuổi, Thợ kỹ thuật tại Đà Nẵng) - Cân Bằng Đều Đặn Tuyệt Đối & Bó Hẹp Thời Lượng:
   - **Đặc trưng hành vi & hợp đồng**: Lao động kỹ thuật theo ca, nhịp lướt nhanh (`quick`), định dạng thích Video dài nhưng thời gian xem video thấp ($3-7$h/tuần), thể trạng ghi nhận: "Năng lượng thấp / Mệt mỏi sau ngày làm".
   - **Biểu hiện dữ liệu**: Phân bổ 3 ca đều đặn gần như tuyệt đối: **Sáng $31.6\%$**, **Trưa/Chiều $31.6\%$**, **Tối $36.8\%$** ($z$ cả 3 ca đều sát mốc 0: $-0.27, +0.42, -0.12$). Thời lượng phiên cực kỳ ổn định, bị bó hẹp trong dải $[10, 20]$ phút ($\mu = 14.0$m, $\sigma = 3.4$m - độ lệch chuẩn nhỏ nhất hệ thống).
   - **Nguyên nhân sâu xa**:
     - *Thời gian biểu cố định theo ca kỹ thuật*: Lịch trình của thợ kỹ thuật chia ca rất đều: Uống cà phê sáng trước giờ làm ($06\text{h}15$, $10-12$m), Nghỉ giải lao giữa ca lúc ăn trưa ($12\text{h}15 - 12\text{h}30$, $10-12$m), và Thư giãn ngắn sau giờ làm ($20\text{h}00 - 20\text{h}30$, $15-20$m).
     - *Rào cản thể lực & năng lượng thấp*: Khác với thanh niên Gen Z, người thợ trung niên lao động thể lực có mức năng lượng thấp sau ngày làm việc. `window_reason` chỉ rõ: `thời lượng vừa phải cân đối với mức năng lượng thấp ghi nhận trong dữ liệu`. Do đó, persona này không bao giờ "ngồi cày mạng" kéo dài (tuyệt đối không có phiên nào $> 20$ phút), duy trì nhịp lướt nhanh (`quick`) để kiểm tra tin tức rồi đi nghỉ ngơi.

   ---
   #### D. `vn_fb_006` (Nam 55-64 tuổi, Người lớn tuổi làm tự do tại Cần Thơ) - Lệch Mạnh Ban Ngày & Giờ Sinh Hoạt Phổ Thông:
   - **Đặc trưng hành vi & hợp đồng**: Trung cao tuổi miền Tây, thích xem Feed truyền thống ($75\%$), rất ghét Reels ($5\%$), thích Video dài ($16-30$h/tuần), thể trạng: "Năng lượng kiệt sức / Hết pin", thói quen dậy sớm.
   - **Biểu hiện dữ liệu**: Hoạt động áp đảo vào ban ngày: **Ca Sáng $35.0\%$** ($7/20$ phiên, $z = +0.09$) và **Ca Trưa & Chiều $35.0\%$** ($7/20$ phiên, $z = +0.83$, $O = 7$ vs $E = 5.6$). Ngược lại, **Ca Tối thấp nhất hệ thống: chỉ $30.0\%$** ($6/20$ phiên, $z = -0.85$, thấp hơn kỳ vọng).
   - **Nguyên nhân sâu xa**:
     - *Thói quen dậy sớm của người lớn tuổi*: Sinh hoạt sáng bắt đầu từ rất sớm ($06\text{h}15$, sớm nhất trong 6 persona) để lướt tin tức đầu ngày (`khung sáng sớm phù hợp thói quen dậy sớm của người lớn tuổi`).
     - *Quỹ thời gian rảnh phân tán vào ban ngày*: Với tính chất lao động tự do/bán nghỉ hưu, persona này có nhiều thời gian rảnh vào đầu giờ chiều sau bữa trưa. Đây là lúc bot rảnh rỗi nằm xem các video dài (tin tức, tài liệu miền Tây) với thời lượng $15 - 20$ phút.
     - *Đi ngủ sớm & suy giảm thể lực vào buổi tối*: Người cao tuổi có chu kỳ sinh học đi ngủ sớm. Bộ lập lịch ghi nhận rõ: `thời lượng vừa phải, cân bằng với tình trạng kiệt sức cuối ngày`. Các phiên tối kết thúc sớm (trước $21\text{h}00$) và ít được bố trí thêm phiên đêm, tạo ra độ lệch âm rõ rệt cho ca tối ($z = -0.85$).

   ---
   #### E. `vn_fb_001` & `vn_fb_002` (Nhóm Support Quá Bé, $N = 2$ Cửa Sổ):
   - `vn_fb_001` (Nữ 25-34 tuổi, NVVP hybrid) mới có 2 phiên ngày 05/10 (sáng, trưa).
   - `vn_fb_002` (Nữ 35-44 tuổi, Nội trợ/Kinh doanh) mới có 2 phiên (1 trưa ngày 05/10, 1 tối ngày 06/10).
   - Do hệ thống dừng kích hoạt sớm ở 2 bot này, các tỷ lệ $0\%$ hay $50\%$ hoàn toàn là tính chất ngẫu nhiên của lượt chạy thử ban đầu, chưa đủ cơ sở để đánh giá bất kỳ thiên hướng sinh hoạt nào.
"""

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [line + "\n" for line in cell_10_md.split("\n")]
})

# Đóng gói Notebook theo định dạng nbformat v4
notebook_dict = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (.venv)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": 3
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbformat_minor": 5,
            "pygments_lexer": "ipython3",
            "version": "3.14"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

output_path = Path("notebooks/notebook_action_logs.ipynb")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, ensure_ascii=False, indent=2)

print(f"Successfully written notebook: {output_path} ({len(cells)} cells)")
