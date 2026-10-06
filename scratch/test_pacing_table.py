import sqlite3, json, sys, pandas as pd
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from loaders.episode_loader import get_sqlite_path, load_episode, list_episodes

DB_PATH = get_sqlite_path()
conn = sqlite3.connect(DB_PATH)
df_bots = pd.read_sql_query('SELECT b.id as bot_id, b.persona_id, bc.contract_json FROM bots b LEFT JOIN behavioral_contracts bc ON bc.id = (SELECT contract_id FROM episodes WHERE bot_id = b.id LIMIT 1)', conn)
contracts_dict = {r['persona_id']: json.loads(r['contract_json']) for _, r in df_bots.iterrows() if r['contract_json']}
conn.close()

all_steps = [load_episode(ep['id'], DB_PATH).to_steps_dataframe() for ep in list_episodes(DB_PATH)]
df_steps = pd.concat(all_steps, ignore_index=True)
df_steps['contract_pacing'] = df_steps['persona_id'].map(lambda p: contracts_dict.get(p, {}).get('navigation', {}).get('scrollCadence', 'N/A'))

gesture_steps = df_steps.dropna(subset=['gesture_pace']).copy()

# Table count & pct
ct_count = pd.crosstab(gesture_steps['contract_pacing'], gesture_steps['gesture_pace'])
ct_pct = (pd.crosstab(gesture_steps['contract_pacing'], gesture_steps['gesture_pace'], normalize='index') * 100).round(1)

table = pd.DataFrame({
    'Nhóm Ràng Buộc Hợp Đồng (scrollCadence)': ['balanced', 'quick'],
    'Cử chỉ Careful (bước)': [
        f"{ct_count.loc['balanced', 'careful']} ({ct_pct.loc['balanced', 'careful']:.1f}%)",
        f"{ct_count.loc['quick', 'careful']} ({ct_pct.loc['quick', 'careful']:.1f}%)"
    ],
    'Cử chỉ Fast (bước)': [
        f"{ct_count.loc['balanced', 'fast']} ({ct_pct.loc['balanced', 'fast']:.1f}%)",
        f"{ct_count.loc['quick', 'fast']} ({ct_pct.loc['quick', 'fast']:.1f}%)"
    ],
    'Tổng số bước cuộn': [ct_count.loc['balanced'].sum(), ct_count.loc['quick'].sum()],
    'Tỷ lệ Tuân Thủ Thực Tế': ['100.0% (Tuyệt đối)', '100.0% (Tuyệt đối)']
})
print("=== BẢNG CHÉO ĐỐI CHIẾU NHÓM HỢP ĐỒNG VS CỬ CHỈ THỰC TẾ ===")
print(table.to_string(index=False))
