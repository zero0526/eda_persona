import sys
sys.path.append('.')
import pandas as pd
import numpy as np
from collections import Counter
from loaders.action_loader import ActionLoader

sys.stdout.reconfigure(encoding='utf-8')

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

personas = sorted(df_actions['persona_id'].unique())

print("=== THỬ NGHIỆM TÌM CHUỖI HÀNH VI THƯƠNG HIỆU ===")

# Cách 1: Nén các hành động liên tiếp trùng nhau (Run-length Compression)
# Ví dụ: scroll, scroll, read -> scroll, read
def get_compressed_tokens(df_session):
    tokens = []
    prev = None
    for _, r in df_session.sort_values('step_index').iterrows():
        tok = f"{str(r['intent']).strip()}@{str(r['surface']).strip()}"
        if tok != prev:
            tokens.append(tok)
            prev = tok
    return tokens

# Cách 2: Giữ nguyên nhưng lọc bỏ các chuỗi tầm thường (A==B hoặc A==C ping-pong)
def get_diverse_chains(tokens, min_len=2, max_len=3):
    chains = []
    for n in range(min_len, max_len + 1):
        for i in range(len(tokens) - n + 1):
            sub = tokens[i:i+n]
            # Kiểm tra: không có 2 bước liền kề giống nhau
            if any(sub[j] == sub[j+1] for j in range(len(sub)-1)):
                continue
            # Nếu là 3 bước, kiểm tra xem có phải ping-pong thuần túy A -> B -> A không
            # Nếu muốn loại bỏ cả ping-pong:
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

all_chains = set()
for c_list in persona_chains.values():
    all_chains.update(c_list)

print(f"Tổng số chuỗi quy trình đa dạng tìm được: {len(all_chains)}")

# Đánh giá từng chuỗi cho từng Persona:
# 1. Số phiên xuất hiện (persistence >= 2 phiên)
# 2. Tổng số lần xuất hiện
# 3. Tính độc quyền (persona_counts / total_across_all_personas)
results = []
for p in personas:
    for c in set(persona_chains[p]):
        s_counts = [session_chains.get((p, s), []).count(c) for s in [1, 2, 3, 4]]
        n_sessions = sum(1 for cnt in s_counts if cnt > 0)
        p_tot = sum(s_counts)
        
        # Đếm tổng lần xuất hiện của chuỗi này trên TẤT CẢ các persona khác
        other_tot = sum(session_chains.get((other_p, s), []).count(c) for other_p in personas if other_p != p for s in [1, 2, 3, 4])
        all_tot = p_tot + other_tot
        
        exclusivity = p_tot / all_tot if all_tot > 0 else 0
        
        # Tiêu chí chuỗi thương hiệu:
        # - Xuất hiện ở ít nhất 2 phiên khác nhau (n_sessions >= 2)
        # - Tính độc quyền cao (exclusivity >= 0.5)
        # - Tổng số lần >= 3
        if n_sessions >= 2 and p_tot >= 3:
            results.append({
                'persona_id': p,
                'chain': c,
                'n_steps': len(c.split('__THEN__')),
                's_counts': s_counts,
                'n_sessions': n_sessions,
                'total_count': p_tot,
                'all_personas_total': all_tot,
                'exclusivity': exclusivity,
                # Điểm thương hiệu: kết hợp số phiên, độ bền vững, tần suất và tính độc quyền
                'brand_score': round((n_sessions / 4.0) * np.log1p(p_tot) * exclusivity, 3)
            })

df_res = pd.DataFrame(results)
print(f"Số ứng viên chuỗi thương hiệu (xuất hiện >= 2 phiên, tổng >= 3): {len(df_res)}")

def format_chain_label(feat):
    parts = feat.split('__THEN__')
    formatted_parts = [p.replace('@', ' [') + ']' for p in parts]
    return ' ➔ '.join(formatted_parts)

for p in personas:
    sub = df_res[df_res['persona_id'] == p].sort_values(['brand_score', 'n_sessions', 'total_count'], ascending=False)
    print(f"\n==================== {p} ====================")
    if len(sub) == 0:
        print("Không có chuỗi đạt ngưỡng bền vững >= 2 phiên. Đang kiểm tra ngưỡng >= 1 phiên...")
        continue
    for idx, r in sub.head(5).iterrows():
        lbl = format_chain_label(r['chain'])
        print(f"  [{r['n_steps']} bước] {lbl}")
        print(f"     Phiên: {r['s_counts']} | Có mặt: {r['n_sessions']}/4 phiên | Tổng: {r['total_count']} lần | Độc quyền: {r['exclusivity']*100:.1f}% | Điểm thương hiệu: {r['brand_score']}")
