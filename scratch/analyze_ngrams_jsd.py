import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon

sys.stdout.reconfigure(encoding='utf-8')

from loaders.loaders.persona_action import PersonaActionLoader
from algorithms.temporal_velocity_and_behavior_profiler import compute_temporal_velocity_by_pace

loader = PersonaActionLoader()
df_steps = loader.load_step_records()
res = compute_temporal_velocity_by_pace(df_steps)
df = res["df_processed"]

def map_macro_behavior(row):
    intent = str(row.get("intent", "")).lower()
    tool = str(row.get("tool", "")).lower()
    res_tool = str(row.get("resolved_tool", "")).lower()
    if tool == "end_episode" or res_tool == "end_episode":
        return "End Session"
    if tool in ["rest", "wait_for_feed"]:
        return "Rest/Wait"
    if intent == "read" or "read" in res_tool:
        return "Deep Read"
    if intent in ["react", "share", "like_page"] or "react" in res_tool:
        return "React/Social"
    if intent == "search" or "search" in res_tool:
        return "Search Query"
    if intent == "scroll" or "scroll" in res_tool:
        return "Scroll Feed"
    if intent in ["open", "home", "back", "close"] or res_tool in ["return_home", "close_detail", "open_search_result", "back_to_discovery"]:
        return "Navigate"
    if intent == "observe" or "observe" in res_tool:
        return "Observe"
    return "Other"

df["macro_behavior"] = df.apply(map_macro_behavior, axis=1)

def extract_ngrams(df_input, action_col="macro_behavior", n=2):
    records = []
    for (ep_id, d_type), group in df_input.groupby(["episode_id", "dataset_type"]):
        sorted_group = group.sort_values("step_index")
        actions = sorted_group[action_col].tolist()
        for i in range(len(actions) - n + 1):
            ngram = " -> ".join(actions[i:i+n])
            records.append({
                "episode_id": ep_id,
                "dataset_type": d_type,
                "ngram": ngram
            })
    return pd.DataFrame(records)

print("="*90)
print("1. TRÍCH XUẤT BIGRAMS VÀ TRIGRAMS")
print("="*90)
df_bi = extract_ngrams(df, "macro_behavior", n=2)
df_tri = extract_ngrams(df, "macro_behavior", n=3)

print(f"Tổng số Bigrams: {len(df_bi)} (Persona: {(df_bi['dataset_type']=='persona').sum()}, No-Persona: {(df_bi['dataset_type']=='no_persona').sum()})")
print(f"Tổng số Trigrams: {len(df_tri)} (Persona: {(df_tri['dataset_type']=='persona').sum()}, No-Persona: {(df_tri['dataset_type']=='no_persona').sum()})")

def compute_jsd_and_patterns(ngram_df, top_k=15):
    # Đếm tần suất
    ct = pd.crosstab(ngram_df["ngram"], ngram_df["dataset_type"])
    for col in ["persona", "no_persona"]:
        if col not in ct.columns:
            ct[col] = 0
            
    # Xác suất P và Q
    p = ct["persona"] / ct["persona"].sum()
    q = ct["no_persona"] / ct["no_persona"].sum()
    
    # Jensen-Shannon Divergence
    # scipy.spatial.distance.jensenshannon trả về JSD distance (căn bậc 2 của JSD với cơ số e hoặc 2)
    # Ta tính chuẩn JSD cơ số 2: JSD in [0, 1] bit
    m = 0.5 * (p + q)
    
    def kl_div(a, b):
        mask = (a > 0) & (b > 0)
        return np.sum(a[mask] * np.log2(a[mask] / b[mask]))
    
    kl_pm = kl_div(p.values, m.values)
    kl_qm = kl_div(q.values, m.values)
    jsd = 0.5 * (kl_pm + kl_qm)
    js_distance = np.sqrt(jsd)
    
    # Pointwise contribution to JSD
    pw_p = np.where(p > 0, 0.5 * p * np.log2(p / m), 0.0)
    pw_q = np.where(q > 0, 0.5 * q * np.log2(q / m), 0.0)
    jsd_contrib = pw_p + pw_q
    
    res_df = pd.DataFrame({
        "Count_Persona": ct["persona"],
        "Count_NoPersona": ct["no_persona"],
        "Prob_Persona (%)": (p * 100).round(2),
        "Prob_NoPersona (%)": (q * 100).round(2),
        "Lift_Persona_vs_NoPersona": (p / (q + 1e-9)).round(2),
        "JSD_Contrib": jsd_contrib
    })
    
    # Log-Odds Ratio
    # Haldane-Anscombe correction (+0.5)
    p_cnt = ct["persona"]
    np_cnt = ct["no_persona"]
    tot_p = p_cnt.sum()
    tot_np = np_cnt.sum()
    lor = np.log(((p_cnt + 0.5) / (tot_p - p_cnt + 0.5)) / ((np_cnt + 0.5) / (tot_np - np_cnt + 0.5)))
    res_df["Log_Odds_Ratio"] = lor.round(3)
    
    return jsd, js_distance, res_df

print("\n" + "="*90)
print("2. PHÂN TÍCH JSD VÀ PATTERNS CỦA BIGRAMS")
print("="*90)
jsd_bi, dist_bi, res_bi = compute_jsd_and_patterns(df_bi)
print(f"JSD (Bigrams): {jsd_bi:.4f} bits (Max = 1.0 bit)")
print(f"JS Distance (Bigrams): {dist_bi:.4f}")

print("\nTop 10 Bigrams đặc trưng nhất của PERSONA (theo Log-Odds Ratio & Lift):")
print(res_bi[res_bi["Count_Persona"] >= 5].sort_values("Log_Odds_Ratio", ascending=False).head(10).to_string())

print("\nTop 10 Bigrams đặc trưng nhất của NO-PERSONA (theo Log-Odds Ratio âm):")
print(res_bi[res_bi["Count_NoPersona"] >= 3].sort_values("Log_Odds_Ratio", ascending=True).head(10).to_string())

print("\nTop 10 Bigrams đóng góp lớn nhất vào JSD Divergence:")
print(res_bi.sort_values("JSD_Contrib", ascending=False).head(10)[["Count_Persona", "Count_NoPersona", "Prob_Persona (%)", "Prob_NoPersona (%)", "Lift_Persona_vs_NoPersona", "JSD_Contrib"]].to_string())

print("\n" + "="*90)
print("3. PHÂN TÍCH JSD VÀ PATTERNS CỦA TRIGRAMS")
print("="*90)
jsd_tri, dist_tri, res_tri = compute_jsd_and_patterns(df_tri)
print(f"JSD (Trigrams): {jsd_tri:.4f} bits (Max = 1.0 bit)")
print(f"JS Distance (Trigrams): {dist_tri:.4f}")

print("\nTop 10 Trigrams đặc trưng nhất của PERSONA:")
print(res_tri[res_tri["Count_Persona"] >= 3].sort_values("Log_Odds_Ratio", ascending=False).head(10).to_string())

print("\nTop 10 Trigrams đặc trưng nhất của NO-PERSONA:")
print(res_tri[res_tri["Count_NoPersona"] >= 2].sort_values("Log_Odds_Ratio", ascending=True).head(10).to_string())

print("\nTop 10 Trigrams đóng góp lớn nhất vào JSD Divergence:")
print(res_tri.sort_values("JSD_Contrib", ascending=False).head(10)[["Count_Persona", "Count_NoPersona", "Prob_Persona (%)", "Prob_NoPersona (%)", "Lift_Persona_vs_NoPersona", "JSD_Contrib"]].to_string())

print("\n" + "="*90)
print("4. KIỂM ĐỊNH Ý NGHĨA THỐNG KÊ (PERMUTATION TEST ON JSD)")
print("="*90)
# Hoán vị nhãn episode 500 lần để tính p-value của JSD
np.random.seed(42)
n_permutations = 500
ep_labels = df[["episode_id", "dataset_type"]].drop_duplicates().set_index("episode_id")["dataset_type"]

perm_jsd_bi = []
perm_jsd_tri = []

for _ in range(n_permutations):
    shuffled_labels = pd.Series(np.random.permutation(ep_labels.values), index=ep_labels.index)
    
    # Map to df_bi
    df_bi_perm = df_bi.copy()
    df_bi_perm["dataset_type"] = df_bi_perm["episode_id"].map(shuffled_labels)
    j_b, _, _ = compute_jsd_and_patterns(df_bi_perm)
    perm_jsd_bi.append(j_b)
    
    # Map to df_tri
    df_tri_perm = df_tri.copy()
    df_tri_perm["dataset_type"] = df_tri_perm["episode_id"].map(shuffled_labels)
    j_t, _, _ = compute_jsd_and_patterns(df_tri_perm)
    perm_jsd_tri.append(j_t)

p_val_bi = (np.array(perm_jsd_bi) >= jsd_bi).mean()
p_val_tri = (np.array(perm_jsd_tri) >= jsd_tri).mean()

print(f"Permutation Test Bigram JSD: Obs = {jsd_bi:.4f}, Mean Null = {np.mean(perm_jsd_bi):.4f}, p-value = {p_val_bi:.4f}")
print(f"Permutation Test Trigram JSD: Obs = {jsd_tri:.4f}, Mean Null = {np.mean(perm_jsd_tri):.4f}, p-value = {p_val_tri:.4f}")
