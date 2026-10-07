import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader

loader = ActionLoader()
profiles, contracts = loader.load_persona_profiles_and_contracts()
df_windows = loader.load_activity_windows()

for pid in ['vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']:
    prof = profiles[pid]
    attrs = prof.get('attributes', {})
    contract = contracts.get(pid, {})
    print("=" * 75)
    print(f"PERSONA: {pid} | Tên: {prof.get('name')}")
    print("DEMOGRAPHICS & ATTRIBUTES:")
    for k, v in sorted(attrs.items()):
        print(f"  * {k}: {v}")
    
    print("\nCONTRACT NAVIGATION & BEHAVIOR:")
    print(f"  * Navigation: {json.dumps(contract.get('navigation', {}), ensure_ascii=False, indent=4)}")
    print(f"  * Interaction: {json.dumps(contract.get('interaction', {}), ensure_ascii=False, indent=4)}")

    print("\nSAMPLE WINDOW REASONS CHO TỪNG CA (Sáng, Trưa/Chiều, Tối):")
    sub_w = df_windows[df_windows['persona_id'] == pid]
    for slot_name, (h1, h2) in [("Sáng", (6, 11)), ("Trưa/Chiều", (11, 17)), ("Tối", (17, 24))]:
        slot_w = sub_w[(sub_w['start_hour_local'] >= h1) & (sub_w['start_hour_local'] < h2)]
        print(f"  --- Ca {slot_name} (Số phiên: {len(slot_w)}) ---")
        for idx, row in slot_w.head(2).iterrows():
            print(f"    + [{row['local_date']} @ {row['start_hour_local']:.2f}h, {row['duration_min']:.0f}m]: {row['window_reason']}")
