import sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

loader = ActionLoader()
df = loader.to_unified_actions_dataframe()

personas = sorted(df['persona_id'].unique())

# Thử nghiệm với các n-gram: 2-step và 3-step
def evaluate_patterns(min_sessions=2):
    persona_docs = {p: [] for p in personas}
    persona_session_counts = {p: {} for p in personas}
    
    for (p, s_ord), grp in df.groupby(['persona_id', 'session_order']):
        grp_sorted = grp.sort_values('step_index')
        raw_acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
        
        # Nén lặp liên tiếp
        acts = []
        prev = None
        for a in raw_acts:
            if a != prev:
                acts.append(a)
                prev = a
                
        session_tokens = []
        for n in [2, 3]:
            for i in range(len(acts) - n + 1):
                sub = acts[i:i+n]
                if any(sub[j] == sub[j+1] for j in range(len(sub)-1)):
                    continue
                if n == 3 and sub[0] == sub[2]:
                    continue
                token = '__THEN__'.join(sub)
                session_tokens.append(token)
                
        persona_docs[p].extend(session_tokens)
        persona_session_counts[p][s_ord] = Counter(session_tokens)
        
    corpus = [' '.join(persona_docs[p]) for p in personas]
    vec = TfidfVectorizer(token_pattern=r'(?u)\S+', lowercase=False, sublinear_tf=True)
    X_tfidf = vec.fit_transform(corpus).toarray()
    features = np.array(vec.get_feature_names_out())
    
    print(f"=== TOP TF-IDF PATTERNS (CÓ MẶT >= {min_sessions} PHIÊN) ===")
    
    top_candidates = {}
    for idx, p in enumerate(personas):
        print(f"\n==================== {p} ====================")
        top_indices = np.argsort(X_tfidf[idx])[::-1]
        
        candidates = []
        for i in top_indices:
            feat = features[i]
            score = X_tfidf[idx][i]
            
            s_cnts = [persona_session_counts[p].get(s, Counter())[feat] for s in [1, 2, 3, 4]]
            tot = sum(s_cnts)
            n_sess = sum(1 for c in s_cnts if c > 0)
            
            if n_sess < min_sessions:
                continue
                
            other_tot = sum(persona_session_counts[other_p].get(s, Counter())[feat] 
                            for other_p in personas if other_p != p 
                            for s in [1, 2, 3, 4])
            excl = (tot / (tot + other_tot)) * 100.0 if (tot + other_tot) > 0 else 0
            
            # Composite Distinctiveness Score = TF-IDF * (exclusivity / 100) * (n_sess / 4.0)
            comp_score = score * (excl / 100.0) * (n_sess / 4.0)
            
            parts = feat.split('__THEN__')
            disp = ' ➔ '.join([pt.replace('@', ' [') + ']' for pt in parts])
            
            candidates.append({
                'feat': feat,
                'disp': disp,
                'n_steps': len(parts),
                'tfidf': round(score, 3),
                'comp_score': round(comp_score, 3),
                'counts': s_cnts,
                'tot': tot,
                'n_sess': n_sess,
                'excl': round(excl, 1)
            })
            
        # Sắp xếp theo comp_score giảm dần
        candidates.sort(key=lambda c: c['comp_score'], reverse=True)
        top_candidates[p] = candidates
        
        for c in candidates[:8]:
            print(f"  [{c['n_steps']}-step] {c['disp']}")
            print(f"     TF-IDF={c['tfidf']} | Composite={c['comp_score']} | Độc quyền={c['excl']}% | Phiên={c['counts']} (Tổng {c['tot']}, {c['n_sess']}/4)")

evaluate_patterns(min_sessions=2)
