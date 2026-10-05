import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

with open('data/original_facebook_persona.json', 'r', encoding='utf-8') as f:
    personas = json.load(f)

rows = []
for p in personas:
    p_id = p.get('persona_id') or p.get('id')
    fb = p.get('facebook_behavior_profile', {})
    beh = fb.get('facebookBehavior', {})
    usage = fb.get('usage', {})
    demo = p.get('demographics', {})
    psy = p.get('psychographics', {})
    habits = {h.get('id'): h.get('claim') for h in fb.get('inferredHabits', [])}
    
    rows.append({
        'persona_id': p_id,
        # facebookBehavior
        'pace': beh.get('pace'),
        'rest_style': beh.get('restStyle'),
        'discovery_style': beh.get('discoveryStyle'),
        'interaction_style': beh.get('interactionStyle'),
        'preferred_surface': beh.get('preferredSurface'),
        'reading_depth': beh.get('readingDepth'),
        # usage
        'attention': usage.get('attention'),
        'energy': usage.get('energy'),
        'engagement_style': usage.get('engagementStyle'),
        'facebook_frequency': usage.get('facebookFrequency'),
        # demographics & psychographics
        'age_bracket': demo.get('age_bracket') or demo.get('age'),
        'gender': demo.get('gender') or demo.get('gender_identity'),
        'tech_savviness': psy.get('tech_savviness') or psy.get('technology_proficiency'),
        'curiosity': psy.get('curiosity'),
        'patience': psy.get('patience'),
        'learning_pace': psy.get('learning_pace'),
        # habits
        'habit_pacing': habits.get('session_pacing', ''),
        'habit_interaction': habits.get('interaction_threshold', ''),
        'habit_content': habits.get('content_selection', ''),
        # interests
        'num_strong_interests': len(fb.get('interests', {}).get('strong', [])),
        'strong_interests': fb.get('interests', {}).get('strong', [])
    })

df_comp = pd.DataFrame(rows)

print("="*100)
print("1. MA TRẬN SO SÁNH 6 PERSONA TRÊN CÁC TRỤ CỘT HÀNH VI CHÍNH")
print("="*100)
cols_show = ['persona_id', 'pace', 'rest_style', 'discovery_style', 'interaction_style', 
             'preferred_surface', 'reading_depth', 'attention', 'energy', 'engagement_style', 'facebook_frequency']
print(df_comp[cols_show].to_string(index=False))

print("\n" + "="*100)
print("2. ĐẶC ĐIỂM TÂM LÝ & NHẬN THỨC (PSYCHOGRAPHICS & HABITS)")
print("="*100)
for _, r in df_comp.iterrows():
    print(f"\n>>> PERSONA {r['persona_id']} (Pace: {r['pace']}, Rest: {r['rest_style']}, Style: {r['interaction_style']}, Surface: {r['preferred_surface']}):")
    print(f"  - Demographics: Age={r['age_bracket']}, Gender={r['gender']}, TechSavviness={r['tech_savviness']}")
    print(f"  - Pacing Habit: {r['habit_pacing']}")
    print(f"  - Interaction Habit: {r['habit_interaction']}")
    print(f"  - Content Selection: {r['habit_content']}")
    print(f"  - Strong Interests ({r['num_strong_interests']}): {r['strong_interests']}")

# 3. Phân nhóm (Archetype Clustering)
print("\n" + "="*100)
print("3. PHÂN TÍCH MA TRẬN KHÁC BIỆT ĐỂ PHÂN NHÓM (CLUSTERING / TAXONOMY)")
print("="*100)
print("Các trục phân hóa lớn nhất giữa 6 Persona:")
for col in ['pace', 'rest_style', 'discovery_style', 'interaction_style', 'preferred_surface', 'reading_depth', 'attention', 'energy', 'engagement_style', 'facebook_frequency']:
    vc = df_comp[col].value_counts().to_dict()
    print(f"  - Trục '{col}': {vc}")

# Lưu bảng so sánh
df_comp.to_csv("output/tables/step5_persona_facebook_profiles_comparison.csv", index=False)
print("\nĐã lưu ma trận so sánh tại: output/tables/step5_persona_facebook_profiles_comparison.csv")
