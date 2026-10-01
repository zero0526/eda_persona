"""
Module: underthesea_log_ratio_profiler.py
Mục đích: Tách từ tiếng Việt bằng underthesea (Vietnamese Word Segmentation),
tính toán phân phối xác suất token P_P(w), P_N(w) giữa 2 nhóm thực nghiệm:
- Group P: Agent được trang bị Persona
- Group N: Agent không có Persona
và tính Log-Odds Ratio:
    LR(w) = log( (P_P(w) + epsilon) / (P_N(w) + epsilon) )
để phát hiện các token/từ ghép đặc trưng phân hóa tư duy suy nghĩ CoT của từng nhóm.

Tuân thủ quy chuẩn: Thuật toán độc lập trong algorithms/, phục vụ Bước 4 Pipeline EDA.
"""

from typing import Dict, Any, List, Optional
import math
import re
from collections import Counter
import pandas as pd
from underthesea import word_tokenize


# Danh sách stopwords ngữ pháp tiếng Việt / Anh và các từ điều hướng / thao tác chung chung
VI_EN_STOPWORDS = {
    # Các từ người dùng yêu cầu lọc
    "page", "group", "mở", "home", "sở_thích", "khám_phá", "like", "liên_quan", "đúng", "có",
    # Từ chức năng, ngữ pháp, trợ từ tiếng Việt
    "và", "của", "là", "để", "trong", "cho", "với", "được", "các", "một", "này",
    "khi", "đã", "thì", "sẽ", "đang", "ở", "ra", "vào", "từ", "lại", "nhiều", "như",
    "những", "người", "không", "nên", "bởi", "vì", "theo", "sau", "trên", "dưới",
    "chỉ", "về", "nhưng", "cũng", "rồi", "quá", "rất", "chưa", "phải", "đủ",
    "xem", "lướt", "trang", "bài", "viết", "tiếp_tục", "hiện_tại",
    # Tiếng Anh cơ bản
    "the", "and", "to", "of", "a", "in", "for", "is", "on", "that", "by", "this", "with", "react"
}


def compute_underthesea_log_ratio(
    df: pd.DataFrame,
    text_col: str = "reason",
    group_col: str = "dataset_type",
    p_label: str = "persona",
    np_label: str = "no_persona",
    epsilon: float = 1e-5,
    min_count: int = 2,
    filter_stopwords: bool = True,
    custom_stopwords: Optional[set] = None
) -> Dict[str, Any]:

    """
    Pipeline phân tích phân phối token bằng underthesea và tính Log-ratio:

    1. Tách từ tiếng Việt (Word Segmentation) bằng underthesea.word_tokenize(..., format='text').
    2. Đếm số lần xuất hiện count_P(w) và count_N(w).
    3. Tính xác suất tương đối:
       P_P(w) = count_P(w) / sum(count_P)
       P_N(w) = count_N(w) / sum(count_N)
    4. Tính Log-ratio:
       LR(w) = ln( (P_P(w) + epsilon) / (P_N(w) + epsilon) )
    5. Phân loại hướng phân hóa: Persona-oriented vs No-Persona-oriented vs Neutral.
    """
    p_series = df[df[group_col] == p_label][text_col].dropna()
    np_series = df[df[group_col] == np_label][text_col].dropna()

    effective_stopwords = set(VI_EN_STOPWORDS)
    if custom_stopwords:
        effective_stopwords.update(custom_stopwords)

    def tokenize_text_series(series: pd.Series) -> List[str]:
        tokens = []
        for raw_text in series:
            text = str(raw_text).strip()
            if not text:
                continue
            # Tách từ tiếng Việt bằng underthesea
            segmented = word_tokenize(text, format="text")
            words = segmented.split()
            for w in words:
                w_clean = w.lower().strip()
                # Loại bỏ dấu câu ở đầu/cuối
                w_clean = re.sub(r'^[^\w]+|[^\w]+$', '', w_clean)
                if not w_clean or len(w_clean) <= 1 or w_clean.isdigit():
                    continue
                if filter_stopwords and w_clean in effective_stopwords:
                    continue
                tokens.append(w_clean)
        return tokens


    tokens_p = tokenize_text_series(p_series)
    tokens_np = tokenize_text_series(np_series)

    total_tokens_p = len(tokens_p)
    total_tokens_np = len(tokens_np)

    count_p = Counter(tokens_p)
    count_np = Counter(tokens_np)

    all_vocab = set(count_p.keys()).union(set(count_np.keys()))

    records = []
    for w in all_vocab:
        c_p = count_p.get(w, 0)
        c_np = count_np.get(w, 0)
        total_occurrences = c_p + c_np

        if total_occurrences < min_count:
            continue

        prob_p = c_p / total_tokens_p if total_tokens_p > 0 else 0.0
        prob_np = c_np / total_tokens_np if total_tokens_np > 0 else 0.0

        # Log ratio cơ số e
        lr = math.log((prob_p + epsilon) / (prob_np + epsilon))
        # Log2 ratio cơ số 2 để đọc tỷ lệ gấp đôi
        lr2 = math.log2((prob_p + epsilon) / (prob_np + epsilon))

        # Phân loại hướng phân hóa
        if lr > 1.0:
            orientation = "Thiên về Persona (LR > +1.0)"
        elif lr < -1.0:
            orientation = "Thiên về No-Persona (LR < -1.0)"
        else:
            orientation = "Trung lập / Dùng chung (-1.0 <= LR <= +1.0)"

        records.append({
            "token": w,
            "count_persona": c_p,
            "count_nopersona": c_np,
            "total_count": total_occurrences,
            "prob_persona": round(prob_p, 6),
            "prob_nopersona": round(prob_np, 6),
            "log_ratio": round(lr, 4),
            "log2_ratio": round(lr2, 4),
            "orientation": orientation
        })

    df_result = pd.DataFrame(records).sort_values(by="log_ratio", ascending=False).reset_index(drop=True)

    # Lọc Top Persona (LR cao nhất) và Top No-Persona (LR thấp nhất)
    top_persona = df_result[df_result["log_ratio"] > 0].head(15)
    top_nopersona = df_result[df_result["log_ratio"] < 0].tail(15).iloc[::-1]

    return {
        "log_ratio_table": df_result,
        "total_tokens_persona": total_tokens_p,
        "total_tokens_nopersona": total_tokens_np,
        "vocab_size_persona": len(count_p),
        "vocab_size_nopersona": len(count_np),
        "total_unique_vocab": len(all_vocab),
        "top_persona_tokens": top_persona,
        "top_nopersona_tokens": top_nopersona
    }
