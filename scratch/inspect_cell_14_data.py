import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from loaders.action_loader import ActionLoader

loader = ActionLoader()
df_episodes, df_actions, df_gestures, df_windows = loader.load_all()

# Filter df_actions by episodes completed naturally (agent_stop) if required, or see how cell 14 does it
print("df_actions total rows:", len(df_actions))
print("df_actions surfaces:", df_actions['surface'].value_counts())

# Crosstab surface
ct_surface_pct = (pd.crosstab(df_actions['surface'], df_actions['persona_id'], normalize='columns') * 100).round(2).drop(index='unknow', errors='ignore')
print("\n=== Surface Crosstab (%) ===")
print(ct_surface_pct)

# Crosstab intent
ct_intent_pct = (pd.crosstab(df_actions['intent'], df_actions['persona_id'], normalize='columns') * 100).round(2)
print("\n=== Top Intents Crosstab (%) ===")
print(ct_intent_pct.head(15))

# Active engagement rate (AER)
# react, comment, share intents or action types
engagement_intents = ['react', 'comment', 'share', 'create_post']
df_actions['is_engaged'] = df_actions['intent'].str.lower().apply(lambda x: any(e in str(x) for e in ['react', 'comment', 'share', 'post']))
aer = (df_actions.groupby('persona_id')['is_engaged'].mean() * 100).round(2)
print("\n=== AER (%) ===")
print(aer)

# Profiles and Contracts
profiles, contracts = loader.load_persona_profiles_and_contracts()
for pid in sorted(profiles.keys()):
    prof = profiles[pid]
    c = contracts.get(pid, {})
    attrs = prof.get('attributes', {})
    print(f"\n*** {pid} ***")
    print("  Contract surfaceBias:", c.get('navigation', {}).get('surfaceBias'))
    print("  Contract social rates:", c.get('social'))
    print("  Contract taste preferredFormats:", c.get('taste', {}).get('preferredFormats'))
    print("  Profile MXH role:", attrs.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.'))
    print("  Profile Groups:", attrs.get('Mức độ sinh hoạt trong các hội nhóm và cộng đồng mạng xã hội.'))
    print("  Profile Comment freq:", attrs.get('Tần suất viết comment trên các bài đăng công khai.'))
    print("  Profile Share freq:", attrs.get('Tần suất share lại nội dung của fanpage hoặc người khác về tường.'))
    print("  Profile Video weekly hours:", attrs.get('Tổng thời gian xem phim, video và livestream hàng tuần.'))
    print("  Profile Attention:", attrs.get('Độ dài thời gian duy trì sự chú ý sâu vào một việc.'))
