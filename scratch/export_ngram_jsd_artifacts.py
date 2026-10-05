import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

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

df_bi = extract_ngrams(df, "macro_behavior", n=2)
df_tri = extract_ngrams(df, "macro_behavior", n=3)

def compute_jsd_and_patterns(ngram_df):
    ct = pd.crosstab(ngram_df["ngram"], ngram_df["dataset_type"])
    for col in ["persona", "no_persona"]:
        if col not in ct.columns:
            ct[col] = 0
            
    p = ct["persona"] / ct["persona"].sum()
    q = ct["no_persona"] / ct["no_persona"].sum()
    
    m = 0.5 * (p + q)
    
    def kl_div(a, b):
        mask = (a > 0) & (b > 0)
        return np.sum(a[mask] * np.log2(a[mask] / b[mask]))
    
    kl_pm = kl_div(p.values, m.values)
    kl_qm = kl_div(q.values, m.values)
    jsd = 0.5 * (kl_pm + kl_qm)
    js_distance = np.sqrt(jsd)
    
    pw_p = np.where(p > 0, 0.5 * p * np.log2(p / m), 0.0)
    pw_q = np.where(q > 0, 0.5 * q * np.log2(q / m), 0.0)
    jsd_contrib = pw_p + pw_q
    
    p_cnt = ct["persona"]
    np_cnt = ct["no_persona"]
    tot_p = p_cnt.sum()
    tot_np = np_cnt.sum()
    lor = np.log(((p_cnt + 0.5) / (tot_p - p_cnt + 0.5)) / ((np_cnt + 0.5) / (tot_np - np_cnt + 0.5)))
    
    res_df = pd.DataFrame({
        "Ngram": ct.index,
        "Count_Persona": ct["persona"].values,
        "Count_NoPersona": ct["no_persona"].values,
        "Prob_Persona (%)": (p.values * 100).round(2),
        "Prob_NoPersona (%)": (q.values * 100).round(2),
        "Lift_P_vs_NP": (p.values / (q.values + 1e-9)).round(2),
        "Log_Odds_Ratio": lor.values.round(3),
        "JSD_Contrib": jsd_contrib.round(5)
    }).set_index("Ngram")
    
    return jsd, js_distance, res_df

jsd_bi, dist_bi, df_bi_res = compute_jsd_and_patterns(df_bi)
jsd_tri, dist_tri, df_tri_res = compute_jsd_and_patterns(df_tri)

# Export tables
df_bi_res.sort_values("Log_Odds_Ratio", ascending=False).to_csv("output/tables/step5_ngram_bigram_distribution_jsd.csv")
df_tri_res.sort_values("Log_Odds_Ratio", ascending=False).to_csv("output/tables/step5_ngram_trigram_distribution_jsd.csv")

# Bảng tổng hợp các Signature Patterns
sig_p_bi = df_bi_res[df_bi_res["Count_Persona"] >= 5].sort_values("Log_Odds_Ratio", ascending=False).head(5)
sig_np_bi = df_bi_res[df_bi_res["Count_NoPersona"] >= 3].sort_values("Log_Odds_Ratio", ascending=True).head(5)
sig_p_tri = df_tri_res[df_tri_res["Count_Persona"] >= 3].sort_values("Log_Odds_Ratio", ascending=False).head(5)
sig_np_tri = df_tri_res[df_tri_res["Count_NoPersona"] >= 2].sort_values("Log_Odds_Ratio", ascending=True).head(5)

print(f"JSD Bigrams: {jsd_bi:.4f} (Distance: {dist_bi:.4f})")
print(f"JSD Trigrams: {jsd_tri:.4f} (Distance: {dist_tri:.4f})")

# Vẽ biểu đồ đối sánh
sns.set_theme(style="whitegrid", font="sans-serif")
fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# 1. Top Bigrams Persona vs NoPersona
top_bi_p = df_bi_res[df_bi_res["Count_Persona"] >= 5].sort_values("Log_Odds_Ratio", ascending=False).head(8)
sns.barplot(
    data=top_bi_p.reset_index(),
    x="Log_Odds_Ratio",
    y="Ngram",
    ax=axes[0, 0],
    palette="Blues_r"
)
axes[0, 0].set_title(f"A. Top Bigrams Đặc trưng của PERSONA (JSD = {jsd_bi:.3f})", fontsize=12, fontweight="bold")
axes[0, 0].set_xlabel("Log-Odds Ratio (Dương: Nghiêng hẳn về Persona)", fontsize=10, fontweight="bold")
axes[0, 0].set_ylabel("")

top_bi_np = df_bi_res[df_bi_res["Count_NoPersona"] >= 3].sort_values("Log_Odds_Ratio", ascending=True).head(8)
sns.barplot(
    data=top_bi_np.reset_index(),
    x="Log_Odds_Ratio",
    y="Ngram",
    ax=axes[0, 1],
    palette="Reds"
)
axes[0, 1].set_title("B. Top Bigrams Đặc trưng của NO-PERSONA", fontsize=12, fontweight="bold")
axes[0, 1].set_xlabel("Log-Odds Ratio (Âm: Nghiêng hẳn về No-Persona)", fontsize=10, fontweight="bold")
axes[0, 1].set_ylabel("")

# 2. Top Trigrams Persona vs NoPersona
top_tri_p = df_tri_res[df_tri_res["Count_Persona"] >= 3].sort_values("Log_Odds_Ratio", ascending=False).head(8)
sns.barplot(
    data=top_tri_p.reset_index(),
    x="Log_Odds_Ratio",
    y="Ngram",
    ax=axes[1, 0],
    palette="Blues_r"
)
axes[1, 0].set_title(f"C. Top Trigrams Đặc trưng của PERSONA (JSD = {jsd_tri:.3f})", fontsize=12, fontweight="bold")
axes[1, 0].set_xlabel("Log-Odds Ratio (Dương: Nghiêng hẳn về Persona)", fontsize=10, fontweight="bold")
axes[1, 0].set_ylabel("")

top_tri_np = df_tri_res[df_tri_res["Count_NoPersona"] >= 2].sort_values("Log_Odds_Ratio", ascending=True).head(8)
sns.barplot(
    data=top_tri_np.reset_index(),
    x="Log_Odds_Ratio",
    y="Ngram",
    ax=axes[1, 1],
    palette="Reds"
)
axes[1, 1].set_title("D. Top Trigrams Đặc trưng của NO-PERSONA", fontsize=12, fontweight="bold")
axes[1, 1].set_xlabel("Log-Odds Ratio (Âm: Nghiêng hẳn về No-Persona)", fontsize=10, fontweight="bold")
axes[1, 1].set_ylabel("")

plt.tight_layout()
fig_path = "output/figures/step5_ngram_patterns_and_jsd.png"
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"Exported {fig_path} successfully!")
