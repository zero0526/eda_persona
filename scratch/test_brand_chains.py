import sys
sys.path.append('.')
import pandas as pd
import numpy as np
from loaders.action_loader import ActionLoader

sys.stdout.reconfigure(encoding='utf-8')
loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

personas = sorted(df_actions['persona_id'].unique())

def get_compressed_tokens(df_session):
    tokens = []
    prev = None
    for _, r in df_session.sort_values('step_index').iterrows():
        tok = f"{str(r['intent']).strip()}@{str(r['surface']).strip()}"
        if tok != prev:
            tokens.append(tok)
            prev = tok
    return tokens

def get_diverse_chains(tokens, min_len=2, max_len=3):
    chains = []
    for n in range(min_len, max_len + 1):
        for i in range(len(tokens) - n + 1):
            sub = tokens[i:i+n]
            if any(sub[j] == sub[j+1] for j in range(len(sub)-1)):
                continue
            if n == 3 and sub[0] == sub[2]:
                continue
            chains.append('__THEN__'.join(sub))
    return chains

session_chains = {}
persona_chains = {p: [] for p in personas}

for (p, s), grp in df_actions.groupby(['persona_id', 'session_order']):
    comp_tokens = get_compressed_tokens(grp)
    chains = get_diverse_chains(comp_tokens, min_len=2, max_len=3)
    session_chains[(p, s)] = chains
    persona_chains[p].extend(chains)

results = []
for p in personas:
    for c in set(persona_chains[p]):
        s_counts = [session_chains.get((p, s), []).count(c) for s in [1, 2, 3, 4]]
        n_sessions = sum(1 for cnt in s_counts if cnt > 0)
        p_tot = sum(s_counts)
        other_tot = sum(session_chains.get((other_p, s), []).count(c) for other_p in personas if other_p != p for s in [1, 2, 3, 4])
        all_tot = p_tot + other_tot
        exclusivity = p_tot / all_tot if all_tot > 0 else 0
        
        # Tiêu chí: xuất hiện ở ít nhất 2 phiên
        if n_sessions >= 2 and p_tot >= 2:
            results.append({
                'persona_id': p,
                'chain': c,
                'n_steps': len(c.split('__THEN__')),
                's_counts': s_counts,
                'n_sessions': n_sessions,
                'total_count': p_tot,
                'all_personas_total': all_tot,
                'exclusivity': round(exclusivity * 100, 1),
                'brand_score': round((n_sessions / 4.0) * np.log1p(p_tot) * exclusivity, 3)
            })

df_res = pd.DataFrame(results)

def format_chain_label(feat):
    parts = feat.split('__THEN__')
    formatted_parts = [p.replace('@', ' [') + ']' for p in parts]
    return ' ➔ '.join(formatted_parts)

for p in personas:
    print(f"\n==================== {p} ====================")
    sub = df_res[df_res['persona_id'] == p].sort_values('brand_score', ascending=False)
    
    # In cả 2 bước và 3 bước
    for idx, r in sub.head(6).iterrows():
        lbl = format_chain_label(r['chain'])
        print(f"  [{r['n_steps']} bước] {lbl}")
        print(f"     Phiên: {r['s_counts']} | Có mặt: {r['n_sessions']}/4 | Tổng: {r['total_count']} | Độc quyền: {r['exclusivity']}% | Điểm: {r['brand_score']}")
