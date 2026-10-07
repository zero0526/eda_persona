import sys
sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader

loader = ActionLoader()
profiles, contracts = loader.load_persona_profiles_and_contracts()
df_w = loader.load_activity_windows()

for pid in ['vn_fb_003']:
    p = profiles[pid]
    a = p.get('attributes', {})
    c = contracts.get(pid, {})
    nav = c.get('navigation', {})
    w = df_w[df_w['persona_id'] == pid]
    
    print("=" * 80)
    print(f"*** {pid}: {p.get('name')} ***")
    print(f"Demographics: Tuổi={a.get('Nhóm tuổi')}, Giới={a.get('Bản dạng giới')}, Nghề={a.get('Nhóm vai trò công việc hiện tại.')}, TP={a.get('Tỉnh / Thành phố')}")
    print(f"Thói quen FB: Tần suất FB={a.get('Tần suất sử dụng Facebook')}, Đọc bài={a.get('Thói quen đọc sách giấy hoặc ebook nâng cao kiến thức.')}, Video={a.get('Tổng thời gian xem phim, video và livestream hàng tuần.')}")
    print(f"Hợp đồng: Nhịp={nav.get('scrollCadence')}, Surfaces={nav.get('surfaceBias')}, Định dạng={a.get('Loại hình nội dung yêu thích nhất')}")
    print("Window reasons tiêu biểu:")
    for _, row in w[['local_date', 'start_hour_local', 'duration_min', 'window_reason']].iterrows():
        print(f"  [{row['local_date']} @ {row['start_hour_local']:>4.1f}h - {row['duration_min']:>2.0f}m]: {row['window_reason']}")
