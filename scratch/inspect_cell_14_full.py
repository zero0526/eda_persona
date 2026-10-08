import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from loaders.action_loader import ActionLoader

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)
df_sessions = loader.to_unified_sessions_dataframe(histories)
persona_profiles, contracts_dict = loader.load_persona_profiles_and_contracts()

print("df_actions count:", len(df_actions))
ct_surface_pct = (pd.crosstab(df_actions['surface'], df_actions['persona_id'], normalize='columns') * 100).round(2).drop(index='unknown', errors='ignore')
print("\n=== Surface Crosstab (%) ===")
print(ct_surface_pct.to_string())

# intent crosstab
ct_intent_pct = (pd.crosstab(df_actions['intent'], df_actions['persona_id'], normalize='columns') * 100).round(2)
intent_order = df_actions['intent'].value_counts().index
ct_intent_pct = ct_intent_pct.loc[intent_order]
print("\n=== Top 12 Intents (%) ===")
print(ct_intent_pct.head(12).to_string())

df_actions['is_aer'] = df_actions['intent'].isin(['react', 'comment', 'share'])
aer_df = (df_actions.groupby('persona_id')['is_aer'].mean() * 100).round(2).reset_index()
aer_df.columns = ['Persona ID', 'AER (%)']
print("\n=== AER (%) ===")
print(aer_df.to_string())

print("\n=== Contract Navigation Surface Bias & Social Rates ===")
for pid in sorted(contracts_dict.keys()):
    c = contracts_dict[pid]
    p = persona_profiles[pid]['attributes']
    print(f"\n--- {pid} ---")
    print("Contract surfaceBias:", c.get('navigation', {}).get('surfaceBias'))
    print("Contract social:", c.get('social'))
    print("Contract scanRatio & scrollCadence:", c.get('navigation', {}).get('scanRatio'), c.get('navigation', {}).get('scrollCadence'))
    print("Contract preferredFormats:", c.get('taste', {}).get('preferredFormats'))
    print("Profile Vai trò MXH:", p.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.'))
    print("Profile Sinh hoạt nhóm:", p.get('Mức độ sinh hoạt trong các hội nhóm và cộng đồng mạng xã hội.'))
    print("Profile Tần suất comment:", p.get('Tần suất viết comment trên các bài đăng công khai.'))
    print("Profile Tần suất share:", p.get('Tần suất share lại nội dung của fanpage hoặc người khác về tường.'))
    print("Profile Tần suất post status:", p.get('Tần suất tự viết status hoặc đăng nội dung mới lên trang cá nhân.'))
    print("Profile Tổng giờ video hàng tuần:", p.get('Tổng thời gian xem phim, video và livestream hàng tuần.'))
    print("Profile Thời gian chú ý:", p.get('Độ dài thời gian duy trì sự chú ý sâu vào một việc.'))
    print("Profile Nghề nghiệp & Lĩnh vực:", p.get('Nhóm vai trò công việc hiện tại.'), "-", p.get('Lĩnh vực của công việc chính hiện tại. Phân loại theo nhóm ngành kinh tế.'))
    print("Profile Thiết bị số:", p.get('Độ am hiểu và kỹ năng sử dụng thiết bị số và ứng dụng mạng.'))
