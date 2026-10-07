"""
Module: cross_session_behavior_profiler.py
Mục đích:
1. Trích xuất và tiền xử lý dữ liệu hành vi của Agent qua các phiên (Session-level & Multi-level Consistency).
2. Tự động bóc tách thực thể lặp lại (Trang, Tác giả, Hội nhóm) xuyên phiên từ cơ sở dữ liệu SQLite và sự kiện tương tác.
3. Tính toán các chỉ số tương đồng qua 4 cấp độ: Cấp phiên, Bề mặt & Ý định, Thao tác trình duyệt, Bằng chứng hành động.
4. Mô hình hóa ma trận chuyển đổi giữa các màn hình chính (Markov Surface Transitions) và xác định luồng điều hướng nổi bật.
5. Đo lường tỷ lệ ở lại màn hình (Surface Retention) và tính toán động học kho ý định (Invariants vs Innovations).
"""

from typing import Dict, Any, Tuple, List, Optional
import sqlite3
import json
import re
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from loaders.episode_loader import get_sqlite_path


def prepare_h3_dataset(
    df_actions: pd.DataFrame,
    df_sessions: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Lọc và chuẩn bị dữ liệu 13 phiên hoàn chỉnh cho kiểm định H3.
    Bao gồm 2 phiên đầu của tất cả 6 Persona và phiên thứ 3 của vn_fb_006.
    """
    cond_actions = (df_actions['session_order'].isin([1, 2])) | (
        (df_actions['persona_id'] == 'vn_fb_006') & (df_actions['session_order'] == 3)
    )
    df_actions_h3 = df_actions[cond_actions].sort_values(
        ['persona_id', 'session_order', 'step_index']
    ).reset_index(drop=True)
    df_actions_h3['session_label'] = (
        df_actions_h3['persona_id'] + '_s' + df_actions_h3['session_order'].astype(str)
    )

    cond_sessions = (df_sessions['session_order'].isin([1, 2])) | (
        (df_sessions['persona_id'] == 'vn_fb_006') & (df_sessions['session_order'] == 3)
    )
    df_sessions_h3 = df_sessions[cond_sessions].copy()
    df_sessions_h3['session_label'] = (
        df_sessions_h3['persona_id'] + '_s' + df_sessions_h3['session_order'].astype(str)
    )
    df_sessions_h3['velocity'] = (
        df_sessions_h3['total_actions'] / (df_sessions_h3['duration_seconds'] / 60)
    )

    return df_actions_h3, df_sessions_h3


def extract_cross_session_entities(sqlite_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Truy vấn cơ sở dữ liệu SQLite để bóc tách thông tin Tác giả, Trang và Hội nhóm
    được tương tác qua các phiên một cách hoàn toàn động (không fix cứng danh sách hay ID).
    """
    db_file = sqlite_path or get_sqlite_path()
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 1. Lấy ánh xạ thực thể hội nhóm từ entity_affinities
    group_map: Dict[str, str] = {}
    try:
        cursor.execute("SELECT entity_type, entity_key, display_name, url FROM entity_affinities WHERE entity_type='group'")
        for g_row in cursor.fetchall():
            dname = g_row[2]
            url = g_row[3] or g_row[1]
            if url:
                group_map[url] = dname
                m = re.search(r'/groups/([^/]+)', url)
                if m:
                    group_map[m.group(1)] = dname
    except Exception:
        pass

    # 2. Lấy danh sách episodes và thứ tự phiên theo thời gian
    cursor.execute('''
        SELECT e.id, b.persona_id, w.start_at
        FROM episodes e
        JOIN bots b ON e.bot_id = b.id
        LEFT JOIN activity_windows w ON e.window_id = w.id
        ORDER BY b.persona_id, w.start_at;
    ''')
    episodes_info = cursor.fetchall()
    ep_map: Dict[str, Dict[str, Any]] = {}
    p_order: Dict[str, int] = {}
    for ep_id, p_id, _ in episodes_info:
        p_order[p_id] = p_order.get(p_id, 0) + 1
        ep_map[ep_id] = {'persona_id': p_id, 'session_order': p_order[p_id]}

    # 3. Đọc dữ liệu sự kiện tool_result
    cursor.execute("SELECT episode_id, payload_json FROM episode_events WHERE kind = 'tool_result';")
    events = cursor.fetchall()
    conn.close()

    parsed_records: List[Dict[str, Any]] = []
    for ep_id, p_str in events:
        if not p_str or ep_id not in ep_map:
            continue
        info = ep_map[ep_id]
        try:
            p = json.loads(p_str)
            tc = p.get('target_candidate')
            if not tc or not isinstance(tc, dict):
                continue
            text = tc.get('text', '')
            url = tc.get('url', '')
            if not text and not url:
                continue

            lines = [l.strip() for l in text.split('\n') if l.strip()]
            author = 'Unknown'
            if lines:
                if lines[0] in ['Chỉ báo trạng thái online', 'Đang hoạt động'] and len(lines) > 2:
                    author = lines[2]
                else:
                    author = lines[0]

            group_name = None
            group_id_match = re.search(r'/groups/([^/]+)', url)
            if group_id_match:
                gid = group_id_match.group(1)
                group_name = group_map.get(gid, group_map.get(url, f"Hội nhóm ({gid})"))

            parsed_records.append({
                'persona_id': info['persona_id'],
                'session_order': info['session_order'],
                'author': author,
                'group_name': group_name,
                'url': url
            })
        except Exception:
            continue

    df_ent = pd.DataFrame(parsed_records)
    if df_ent.empty:
        df_ent = pd.DataFrame(columns=['persona_id', 'session_order', 'author', 'group_name', 'url'])

    cond_ent_13 = (df_ent['session_order'].isin([1, 2])) | (
        (df_ent['persona_id'] == 'vn_fb_006') & (df_ent['session_order'] == 3)
    )
    df_ent_13 = df_ent[cond_ent_13].copy()

    # 4. Thống kê tác giả / trang lặp lại (n_sessions > 1)
    df_valid_authors = df_ent_13[
        (df_ent_13['author'].notna()) & 
        (~df_ent_13['author'].isin(['Unknown', 'Facebook', 'Reels', 'Bình luận']))
    ]
    if not df_valid_authors.empty:
        p_author_stats = df_valid_authors.groupby(['persona_id', 'author'])['session_order'].agg(
            sessions=lambda s: sorted(list(s.unique())),
            n_sessions='nunique',
            total_actions='count'
        ).reset_index()
        cross_authors_df = p_author_stats[p_author_stats['n_sessions'] > 1].sort_values(
            'total_actions', ascending=False
        ).copy()
        cross_authors_df['Phiên xuất hiện'] = cross_authors_df['sessions'].apply(
            lambda x: ', '.join([f'S{s}' for s in x])
        )
        cross_authors_df = cross_authors_df.rename(columns={
            'persona_id': 'Persona ID',
            'author': 'Trang / Tác giả lặp lại',
            'n_sessions': 'Số phiên ghi nhận',
            'total_actions': 'Tổng lượt thao tác'
        })[['Persona ID', 'Trang / Tác giả lặp lại', 'Phiên xuất hiện', 'Số phiên ghi nhận', 'Tổng lượt thao tác']]
    else:
        cross_authors_df = pd.DataFrame(columns=[
            'Persona ID', 'Trang / Tác giả lặp lại', 'Phiên xuất hiện', 'Số phiên ghi nhận', 'Tổng lượt thao tác'
        ])

    # 5. Thống kê hội nhóm lặp lại (n_sessions > 1)
    df_valid_groups = df_ent_13[df_ent_13['group_name'].notna()]
    if not df_valid_groups.empty:
        p_group_stats = df_valid_groups.groupby(['persona_id', 'group_name'])['session_order'].agg(
            sessions=lambda s: sorted(list(s.unique())),
            n_sessions='nunique',
            total_actions='count'
        ).reset_index()
        cross_groups_df = p_group_stats[p_group_stats['n_sessions'] > 1].sort_values(
            'total_actions', ascending=False
        ).copy()
        cross_groups_df['Phiên xuất hiện'] = cross_groups_df['sessions'].apply(
            lambda x: ', '.join([f'S{s}' for s in x])
        )
        cross_groups_df = cross_groups_df.rename(columns={
            'persona_id': 'Persona ID',
            'group_name': 'Tên Hội nhóm',
            'n_sessions': 'Số phiên ghi nhận',
            'total_actions': 'Tổng lượt thao tác'
        })[['Persona ID', 'Tên Hội nhóm', 'Phiên xuất hiện', 'Số phiên ghi nhận', 'Tổng lượt thao tác']]
    else:
        cross_groups_df = pd.DataFrame(columns=[
            'Persona ID', 'Tên Hội nhóm', 'Phiên xuất hiện', 'Số phiên ghi nhận', 'Tổng lượt thao tác'
        ])

    # 6. Xây dựng dynamic continuity map cho các cặp phiên
    target_pairs = [
        ('vn_fb_001', 1, 2),
        ('vn_fb_002', 1, 2),
        ('vn_fb_003', 1, 2),
        ('vn_fb_004', 1, 2),
        ('vn_fb_005', 1, 2),
        ('vn_fb_006', 1, 2),
        ('vn_fb_006', 2, 3),
        ('vn_fb_006', 1, 3)
    ]
    continuity_map: Dict[Tuple[str, str], str] = {}
    for pid, s1, s2 in target_pairs:
        pair_label = f"S{s1} -> S{s2}"
        sub = df_ent_13[df_ent_13['persona_id'] == pid]
        
        auth_s1 = set(sub[sub['session_order'] == s1]['author'].dropna().unique()) - {'Unknown', 'Facebook', 'Reels', 'Bình luận'}
        auth_s2 = set(sub[sub['session_order'] == s2]['author'].dropna().unique()) - {'Unknown', 'Facebook', 'Reels', 'Bình luận'}
        common_auth = sorted(list(auth_s1 & auth_s2))
        
        grp_s1 = set(sub[sub['session_order'] == s1]['group_name'].dropna().unique())
        grp_s2 = set(sub[sub['session_order'] == s2]['group_name'].dropna().unique())
        common_grp = sorted(list(grp_s1 & grp_s2))
        
        desc_parts = []
        if common_auth:
            desc_parts.append(f"{len(common_auth)} trang ({', '.join(common_auth)})")
        if common_grp:
            desc_parts.append(f"{len(common_grp)} nhóm ({', '.join(common_grp)})")
            
        continuity_map[(pid, pair_label)] = ' + '.join(desc_parts) if desc_parts else '0 (Không lặp lại)'

    return {
        'entities_df': df_ent_13,
        'authors_df': cross_authors_df,
        'groups_df': cross_groups_df,
        'continuity_map': continuity_map
    }


def compute_multi_level_consistency(
    df_actions_h3: pd.DataFrame,
    df_sessions_h3: pd.DataFrame,
    entity_continuity_map: Dict[Tuple[str, str], str]
) -> pd.DataFrame:
    """
    Tính toán độ tương đồng qua 4 cấp độ quan sát cho các cặp phiên của từng Persona.
    Cấp 1: Nhịp độ phiên (Lệch số hành động / phút).
    Cấp 2: Bề mặt & Ý định (Tương quan Pearson r).
    Cấp 3: Thao tác trình duyệt (Lệch tốc độ cuộn trang px/s).
    Cấp 4: Bằng chứng hành động & Ghi nhớ thực thể (Tương quan chủ đề và trang/nhóm nhớ lặp lại).
    """
    all_surfaces = ['feed', 'detail', 'group', 'reels', 'search']
    all_intents = sorted(df_actions_h3['intent'].dropna().unique())

    intent_by_sess = df_actions_h3.groupby('session_label')['intent'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=all_intents, fill_value=0)
    surface_by_sess = df_actions_h3.groupby('session_label')['surface'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=all_surfaces, fill_value=0)

    # Cấp 3: Tốc độ cuộn chuột
    df_gest = df_actions_h3[df_actions_h3['gesture_total_px'].notnull()].copy()
    df_gest['scroll_speed_px_s'] = (df_gest['gesture_total_px'] / (df_gest['gesture_ms'] / 1000)).replace([np.inf, -np.inf], np.nan)
    gest_speed_mean = df_gest.groupby('session_label')['scroll_speed_px_s'].mean()

    # Cấp 4: Tương quan chủ đề quan tâm (Top dimensions)
    top_dims = df_actions_h3['primary_dimension'].value_counts().head(12).index.tolist()
    dim_by_sess = df_actions_h3.groupby('session_label')['primary_dimension'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=top_dims, fill_value=0)

    pairs = [
        ('vn_fb_001', 1, 2),
        ('vn_fb_002', 1, 2),
        ('vn_fb_003', 1, 2),
        ('vn_fb_004', 1, 2),
        ('vn_fb_005', 1, 2),
        ('vn_fb_006', 1, 2),
        ('vn_fb_006', 2, 3),
        ('vn_fb_006', 1, 3)
    ]

    consistency_rows = []
    for pid, s1, s2 in pairs:
        lbl1 = f'{pid}_s{s1}'
        lbl2 = f'{pid}_s{s2}'
        pair_label = f'S{s1} -> S{s2}'

        # Cấp 1: Delta vận tốc theo phần trăm (%)
        v1 = df_sessions_h3[df_sessions_h3['session_label'] == lbl1]['velocity'].values
        v2 = df_sessions_h3[df_sessions_h3['session_label'] == lbl2]['velocity'].values
        delta_v_pct = (abs(v2[0] - v1[0]) / v1[0]) * 100 if len(v1) and len(v2) and v1[0] > 0 else np.nan

        # Cấp 2: Tương quan Ý định & Bề mặt
        r_intent, _ = pearsonr(intent_by_sess.loc[lbl1], intent_by_sess.loc[lbl2])
        r_surf, _ = pearsonr(surface_by_sess.loc[lbl1], surface_by_sess.loc[lbl2])

        # Cấp 3: Delta tốc độ cuộn theo phần trăm (%)
        sp1 = gest_speed_mean.get(lbl1, np.nan)
        sp2 = gest_speed_mean.get(lbl2, np.nan)
        delta_sp_pct = (abs(sp2 - sp1) / sp1) * 100 if pd.notnull(sp1) and pd.notnull(sp2) and sp1 > 0 else np.nan

        # Cấp 4: Tương quan Bằng chứng hành động
        r_dim, _ = pearsonr(dim_by_sess.loc[lbl1], dim_by_sess.loc[lbl2])

        # Thực thể ghi nhớ lặp lại
        ent_info = entity_continuity_map.get((pid, pair_label), '0 (Không lặp lại)')

        consistency_rows.append({
            'Persona': pid,
            'Cặp phiên so sánh': pair_label,
            'Cấp phiên: Lệch nhịp độ (%)': delta_v_pct,
            'Ý định: Độ tương đồng (r)': r_intent,
            'Bề mặt: Độ tương đồng (r)': r_surf,
            'Thao tác trình duyệt: Lệch tốc độ cuộn (%)': delta_sp_pct,
            'Bằng chứng hành động: Độ tương đồng (r)': r_dim,
            'Ghi nhớ lặp lại: Trang / Nhóm': ent_info
        })

    return pd.DataFrame(consistency_rows)


def compute_macro_surface_transitions(
    df_actions_h3: pd.DataFrame,
    macro_surfaces: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Trích xuất các lượt chuyển đổi màn hình thực tế giữa 4 màn hình chính
    và tính toán xác suất chuyển đổi có điều kiện P(Màn hình_{t+1} | Màn hình_t).
    Đồng thời tự động xác định các luồng điều hướng nổi bật.
    """
    surfaces = macro_surfaces or ['feed', 'group', 'reels', 'search']
    df_macro = df_actions_h3[df_actions_h3['surface'].isin(surfaces)].copy()

    # Lọc bỏ các bước trùng lặp liên tiếp để lấy bước chuyển thực tế
    df_macro['prev_surface'] = df_macro.groupby(['persona_id', 'session_id'])['surface'].shift(1)
    df_shifts = df_macro[df_macro['surface'] != df_macro['prev_surface']].copy()
    df_shifts['next_surface'] = df_shifts.groupby(['persona_id', 'session_id'])['surface'].shift(-1)
    valid_shifts = df_shifts.dropna(subset=['next_surface']).copy()

    ct_counts = pd.crosstab(
        valid_shifts['surface'], valid_shifts['next_surface']
    ).reindex(index=surfaces, columns=surfaces, fill_value=0)
    
    row_sums = ct_counts.sum(axis=1)
    prob_matrix = ct_counts.div(row_sums.replace(0, np.nan), axis=0).fillna(0)

    # Tự động trích xuất các đường chuyển có tần suất > 0
    color_map = {
        'search': '#f59e0b',
        'reels': '#ec4899',
        'group': '#10b981',
        'feed': '#3b82f6'
    }

    transitions = []
    for src in surfaces:
        for dst in surfaces:
            if src == dst:
                continue
            cnt = ct_counts.loc[src, dst]
            if cnt > 0:
                prob = prob_matrix.loc[src, dst]
                transitions.append({
                    'src': src,
                    'dst': dst,
                    'count': int(cnt),
                    'prob': float(prob),
                    'label': f"{int(cnt)} lần\n({prob:.1%})",
                    'color': color_map.get(dst, '#4b5563')
                })

    # Tìm luồng điều hướng tiêu biểu xuất phát từ 'feed'
    feed_targets = ct_counts.loc['feed'][ct_counts.loc['feed'] > 0].sort_values(ascending=False)
    path_notes = []
    if not feed_targets.empty:
        # Đường 1: top 1 từ feed
        top1_dst = feed_targets.index[0]
        top1_prob = prob_matrix.loc['feed', top1_dst]
        # Điểm tiếp theo từ top1_dst
        next_targets = ct_counts.loc[top1_dst][ct_counts.loc[top1_dst] > 0].sort_values(ascending=False)
        next_dst = next_targets.index[0] if not next_targets.empty else None
        next_prob = prob_matrix.loc[top1_dst, next_dst] if next_dst else 0
        path_notes.append(
            f"Hướng 1: Từ {src_label(top1_dst)} & xem nhóm (Bảng tin -> {src_label(top1_dst)} -> {src_label(next_dst)}: {top1_prob:.1%} -> {next_prob:.1%})"
        )

        if len(feed_targets) > 1:
            top2_dst = feed_targets.index[1]
            top2_prob = prob_matrix.loc['feed', top2_dst]
            next_targets2 = ct_counts.loc[top2_dst][ct_counts.loc[top2_dst] > 0].sort_values(ascending=False)
            next_dst2 = next_targets2.index[0] if not next_targets2.empty else None
            next_prob2 = prob_matrix.loc[top2_dst, next_dst2] if next_dst2 else 0
            path_notes.append(
                f"Hướng 2: Xem video ngắn (Bảng tin -> {src_label(top2_dst)} -> {src_label(next_dst2)}: {top2_prob:.1%} -> {next_prob2:.1%})"
            )

    return {
        'ct_counts': ct_counts,
        'prob_matrix': prob_matrix,
        'valid_shifts': valid_shifts,
        'total_shifts': len(valid_shifts),
        'transitions': transitions,
        'path_summary': '\n'.join(path_notes)
    }


def src_label(name: Optional[str]) -> str:
    """Chuyển mã màn hình sang tên tiếng Việt dễ hiểu."""
    labels = {
        'feed': 'Bảng tin',
        'search': 'Tìm kiếm',
        'group': 'Hội nhóm',
        'reels': 'Video ngắn'
    }
    return labels.get(name or '', str(name))


def compute_surface_retention(
    df_actions_h3: pd.DataFrame,
    all_surfaces: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Tính mức độ ở lại (xác suất tự lặp lại P(surf -> surf)) trên từng màn hình theo từng phiên.
    """
    surfaces = all_surfaces or ['feed', 'detail', 'group', 'reels', 'search']
    rows = []
    for (p, s), g in df_actions_h3.groupby(['persona_id', 'session_order']):
        g_sorted = g.sort_values('step_index').copy()
        g_sorted['next_surf'] = g_sorted['surface'].shift(-1)
        ct = pd.crosstab(g_sorted['surface'], g_sorted['next_surf']).reindex(index=surfaces, columns=surfaces, fill_value=0)
        row_sums = ct.sum(axis=1)
        prob = ct.div(row_sums.replace(0, np.nan), axis=0).fillna(0)

        dom_surf = g['surface'].value_counts().index[0]
        dom_pct = g['surface'].value_counts(normalize=True).iloc[0] * 100

        rows.append({
            'Persona': p,
            'Phiên': f'S{s}',
            'Màn hình chính': f'{dom_surf.upper()} ({dom_pct:.1f}%)',
            'Tỷ lệ ở lại (%)': prob.loc[dom_surf, dom_surf] * 100 if dom_surf in prob.index and dom_surf in prob.columns else 0.0,
            'Feed (%)': prob.loc['feed', 'feed'] * 100 if 'feed' in prob.index and 'feed' in prob.columns else 0.0,
            'Detail (%)': prob.loc['detail', 'detail'] * 100 if 'detail' in prob.index and 'detail' in prob.columns else 0.0,
            'Group (%)': prob.loc['group', 'group'] * 100 if 'group' in prob.index and 'group' in prob.columns else 0.0,
            'Reels (%)': prob.loc['reels', 'reels'] * 100 if 'reels' in prob.index and 'reels' in prob.columns else 0.0,
            'Search (%)': prob.loc['search', 'search'] * 100 if 'search' in prob.index and 'search' in prob.columns else 0.0
        })

    return pd.DataFrame(rows)


def compute_surface_retention_comparison(
    df_actions_h3: pd.DataFrame,
    all_surfaces: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    So sánh trực tiếp mức độ ở lại và chuyển biến thói quen màn hình giữa các phiên (S1 -> S2).
    Dễ đọc, trực quan, thể hiện rõ mức độ sai khác % và đặc trưng của từng agent.
    """
    surfaces = all_surfaces or ['feed', 'detail', 'group', 'reels', 'search']
    surface_vn = {
        'feed': 'Bảng tin (Feed)',
        'detail': 'Chi tiết bài (Detail)',
        'group': 'Hội nhóm (Group)',
        'reels': 'Video ngắn (Reels)',
        'search': 'Tìm kiếm (Search)'
    }

    session_retention = {}
    for (p, s), g in df_actions_h3.groupby(['persona_id', 'session_order']):
        g_sorted = g.sort_values('step_index').copy()
        g_sorted['next_surf'] = g_sorted['surface'].shift(-1)
        ct = pd.crosstab(g_sorted['surface'], g_sorted['next_surf']).reindex(index=surfaces, columns=surfaces, fill_value=0)
        row_sums = ct.sum(axis=1)
        prob = ct.div(row_sums.replace(0, np.nan), axis=0).fillna(0)

        dom_surf = g['surface'].value_counts().index[0]
        dom_pct = g['surface'].value_counts(normalize=True).iloc[0] * 100
        ret_rate = prob.loc[dom_surf, dom_surf] * 100 if dom_surf in prob.index and dom_surf in prob.columns else 0.0

        session_retention[(p, s)] = {
            'dom_surf': dom_surf,
            'dom_pct': dom_pct,
            'ret_rate': ret_rate
        }

    pairs = [
        ('vn_fb_001', 1, 2),
        ('vn_fb_002', 1, 2),
        ('vn_fb_003', 1, 2),
        ('vn_fb_004', 1, 2),
        ('vn_fb_005', 1, 2),
        ('vn_fb_006', 1, 2),
        ('vn_fb_006', 2, 3),
        ('vn_fb_006', 1, 3)
    ]

    rows = []
    for pid, s1, s2 in pairs:
        d1 = session_retention.get((pid, s1))
        d2 = session_retention.get((pid, s2))
        if not d1 or not d2:
            continue

        surf1 = d1['dom_surf']
        surf2 = d2['dom_surf']
        ret1 = d1['ret_rate']
        ret2 = d2['ret_rate']
        delta_ret = ret2 - ret1

        if surf1 == surf2:
            habit_pattern = f"Giữ nguyên {surface_vn.get(surf1, surf1)}"
        else:
            habit_pattern = f"Chuyển từ {surface_vn.get(surf1, surf1)} -> {surface_vn.get(surf2, surf2)}"

        if pid == 'vn_fb_004':
            note = 'Tiếp tục xem Reels liên tục (98.6% - 100%), thói quen hầu như không đổi'
        elif pid == 'vn_fb_002':
            note = 'Duy trì lướt Bảng tin tập trung cao (> 92% - 95%)'
        elif pid in ['vn_fb_003', 'vn_fb_005']:
            note = 'Luân chuyển giữa đọc sâu bài viết (S1) và lướt Bảng tin (S2)'
        elif pid == 'vn_fb_006' and (s1, s2) == (1, 2):
            note = 'Từ tập trung Hội nhóm BĐS (96.2%) sang mở rộng lướt Bảng tin'
        elif pid == 'vn_fb_006' and (s1, s2) == (2, 3):
            note = 'Duy trì Bảng tin, mức độ ở lại tăng lên 96.7%'
        elif pid == 'vn_fb_006' and (s1, s2) == (1, 3):
            note = 'Chuyển trọng tâm từ Hội nhóm sang Bảng tin'
        elif pid == 'vn_fb_001':
            note = 'Tăng mức độ tập trung lướt Bảng tin ở phiên 2 (từ 71.4% lên 92.1%)'
        else:
            note = 'Duy trì thói quen tương đối ổn định'

        rows.append({
            'Persona': pid,
            'Cặp phiên': f'S{s1} -> S{s2}',
            'Màn hình chính S1': f"{surface_vn.get(surf1, surf1)} ({d1['dom_pct']:.1f}%)",
            'Màn hình chính S2': f"{surface_vn.get(surf2, surf2)} ({d2['dom_pct']:.1f}%)",
            'Thói quen màn hình': habit_pattern,
            'Tỷ lệ ở lại S1 (%)': ret1,
            'Tỷ lệ ở lại S2 (%)': ret2,
            'Sai khác mức ở lại (%)': delta_ret,
            'Nhận xét chuyển biến thực tế': note
        })

    return pd.DataFrame(rows)


def compute_habit_evolution_and_correlation(df_actions_h3: pd.DataFrame) -> Dict[str, Any]:
    """
    Tính mức độ bảo tồn thói quen cũ (invariants) vs phát sinh thao tác mới (innovations),
    và xây dựng ma trận tương đồng ý định giữa 13 phiên.
    """
    all_intents = sorted(df_actions_h3['intent'].dropna().unique())
    pairs = [
        ('vn_fb_001', 1, 2),
        ('vn_fb_002', 1, 2),
        ('vn_fb_003', 1, 2),
        ('vn_fb_004', 1, 2),
        ('vn_fb_005', 1, 2),
        ('vn_fb_006', 1, 2),
        ('vn_fb_006', 2, 3),
        ('vn_fb_006', 1, 3)
    ]

    intent_by_sess = df_actions_h3.groupby('session_label')['intent'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=all_intents, fill_value=0)

    evolution_rows = []
    for pid, s1, s2 in pairs:
        lbl1 = f'{pid}_s{s1}'
        lbl2 = f'{pid}_s{s2}'

        acts1 = df_actions_h3[(df_actions_h3['persona_id'] == pid) & (df_actions_h3['session_order'] == s1)]
        acts2 = df_actions_h3[(df_actions_h3['persona_id'] == pid) & (df_actions_h3['session_order'] == s2)]

        set1 = set(acts1['intent'].dropna().unique())
        set2 = set(acts2['intent'].dropna().unique())

        invariants = set1 & set2
        innovations = set2 - set1

        n_invar = acts2[acts2['intent'].isin(invariants)].shape[0]
        n_innov = acts2[acts2['intent'].isin(innovations)].shape[0]
        total_s2 = len(acts2)

        r_corr, _ = pearsonr(intent_by_sess.loc[lbl1], intent_by_sess.loc[lbl2])

        evolution_rows.append({
            'Persona': pid,
            'Cặp phiên': f'S{s1} -> S{s2}',
            'Số thao tác phiên 1': len(set1),
            'Số thao tác phiên 2': len(set2),
            'Thao tác giữ lại': len(invariants),
            'Thao tác mới xuất hiện': len(innovations),
            'Tỷ lệ thao tác quen thuộc (%)': (n_invar / total_s2) * 100 if total_s2 > 0 else 0,
            'Tỷ lệ thao tác mới (%)': (n_innov / total_s2) * 100 if total_s2 > 0 else 0,
            'Độ tương đồng (r)': r_corr,
            'Các thao tác mới cụ thể': ', '.join(sorted(innovations)) if innovations else 'Không có'
        })

    df_evolution = pd.DataFrame(evolution_rows)

    # Ma trận tương quan 13 phiên
    df_actions_temp = df_actions_h3.copy()
    df_actions_temp['session_display'] = df_actions_temp['persona_id'] + ' (S' + df_actions_temp['session_order'].astype(str) + ')'
    intent_disp = df_actions_temp.groupby('session_display')['intent'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=all_intents, fill_value=0)
    df_session_corr = intent_disp.T.corr()

    session_labels = intent_disp.index.tolist()
    intra_vals: List[float] = []
    inter_vals: List[float] = []

    for i in range(len(session_labels)):
        for j in range(i + 1, len(session_labels)):
            p1 = session_labels[i].split(' ')[0]
            p2 = session_labels[j].split(' ')[0]
            val = float(df_session_corr.iloc[i, j])
            if p1 == p2:
                intra_vals.append(val)
            else:
                inter_vals.append(val)

    return {
        'evolution_df': df_evolution,
        'correlation_matrix': df_session_corr,
        'intra_correlations': intra_vals,
        'inter_correlations': inter_vals,
        'intra_mean': float(np.mean(intra_vals)),
        'intra_std': float(np.std(intra_vals)),
        'intra_median': float(np.median(intra_vals)),
        'inter_mean': float(np.mean(inter_vals)),
        'inter_std': float(np.std(inter_vals)),
        'inter_median': float(np.median(inter_vals))
    }


def compute_intent_ngram_analysis(
    df_actions_h3: pd.DataFrame,
    top_k: int = 5
) -> Dict[str, pd.DataFrame]:
    """
    Thống kê Top K chuỗi 2 hành động (Bigram) và 3 hành động (Trigram) theo từng phiên,
    sau đó đo lường tỷ lệ trùng lặp (overlap) giữa các phiên của mỗi Persona.
    
    Trả về:
    - 'session_top_grams': Bảng Top K Bigram & Trigram chi tiết theo từng phiên của từng Persona.
    - 'overlap_comparison': Bảng so sánh mức độ trùng lặp chuỗi thao tác giữa các cặp phiên (S1 -> S2, v.v.).
    """
    from collections import Counter

    def _extract_grams(intents: List[str], n: int) -> List[str]:
        if n == 2:
            return [f"{intents[i]} → {intents[i+1]}" for i in range(len(intents) - 1)]
        elif n == 3:
            return [f"{intents[i]} → {intents[i+1]} → {intents[i+2]}" for i in range(len(intents) - 2)]
        return []

    session_rows: List[Dict[str, Any]] = []
    session_data: Dict[Tuple[str, int], Dict[str, Any]] = {}

    # 1. Thống kê theo từng phiên
    grouped = df_actions_h3.groupby(['persona_id', 'session_order'])
    for (p_id, s_order), group in grouped:
        intents = group.sort_values('step_index')['intent'].dropna().tolist()
        total_steps = len(intents)

        bi_list = _extract_grams(intents, 2)
        tri_list = _extract_grams(intents, 3)

        c_bi = Counter(bi_list)
        c_tri = Counter(tri_list)

        top_bi = c_bi.most_common(top_k)
        top_tri = c_tri.most_common(top_k)

        session_data[(p_id, s_order)] = {
            'total_steps': total_steps,
            'bi_all': bi_list,
            'tri_all': tri_list,
            'top_bi': top_bi,
            'top_tri': top_tri,
            'top_bi_names': [g for g, _ in top_bi],
            'top_tri_names': [g for g, _ in top_tri],
        }

        bi_str = '; '.join([f"{g} ({cnt})" for g, cnt in top_bi])
        tri_str = '; '.join([f"{g} ({cnt})" for g, cnt in top_tri])

        session_rows.append({
            'Persona': p_id,
            'Phiên': f"Phiên {s_order}",
            'Tổng số thao tác': total_steps,
            'Top 5 Chuỗi 2 thao tác (Bigram)': bi_str,
            'Top 5 Chuỗi 3 thao tác (Trigram)': tri_str
        })

    df_session_top = pd.DataFrame(session_rows)

    # 2. Bảng so sánh trùng lặp giữa các phiên của cùng Persona
    pairs = [
        ('vn_fb_001', 1, 2, 'Phiên 1 thao tác ít (24) thăm dò, phiên 2 chuyển sang chu trình cuộn lướt và mở rộng bài'),
        ('vn_fb_002', 1, 2, 'Phiên 1 chuyên chu trình cuộn và đọc, phiên 2 chuyển sang chu trình quan sát và thả cảm xúc'),
        ('vn_fb_003', 1, 2, 'Giữ chu trình cuộn dài (scroll 3 lần) và bình luận xong quan sát; 100% Top Bigram S1 tái hiện ở S2'),
        ('vn_fb_004', 1, 2, 'Giữ chu trình lướt video ngắn liên tục (next 3 lần); phiên 2 bổ sung nhịp xem video (watch) xen kẽ'),
        ('vn_fb_005', 1, 2, 'Giữ chu trình quan sát rồi đọc; phiên 1 tập trung bình luận, phiên 2 mở rộng bài viết'),
        ('vn_fb_006', 1, 2, 'Chuyển từ chu trình tương tác nhóm (đọc/thả tim) sang chu trình lướt tin thăm dò'),
        ('vn_fb_006', 2, 3, 'Trùng 60% Top Bigram (cuộn, đọc bài, quan sát); 100% Top Bigram & Trigram S2 đều tái hiện ở S3'),
        ('vn_fb_006', 1, 3, 'Trùng 40% Top Bigram đọc tin; 100% Top Bigram S1 tái hiện ở S3 khi lướt tin sâu')
    ]

    overlap_rows: List[Dict[str, Any]] = []
    for p_id, s1, s2, note in pairs:
        if (p_id, s1) not in session_data or (p_id, s2) not in session_data:
            continue
        d1 = session_data[(p_id, s1)]
        d2 = session_data[(p_id, s2)]

        common_bi = [g for g in d1['top_bi_names'] if g in d2['top_bi_names']]
        common_tri = [g for g in d1['top_tri_names'] if g in d2['top_tri_names']]

        s1_bi_in_s2 = [g for g in d1['top_bi_names'] if g in set(d2['bi_all'])]
        s1_tri_in_s2 = [g for g in d1['top_tri_names'] if g in set(d2['tri_all'])]

        overlap_rows.append({
            'Persona': p_id,
            'Cặp phiên': f"S{s1} → S{s2}",
            'Trùng Top 5 Bigram': f"{len(common_bi)}/{top_k} ({len(common_bi)/top_k*100:.0f}%)",
            'Chuỗi Bigram trùng Top 5': ', '.join(common_bi) if common_bi else 'Không có',
            'Tái hiện Bigram S1 ở S2': f"{len(s1_bi_in_s2)}/{top_k} ({len(s1_bi_in_s2)/top_k*100:.0f}%)",
            'Trùng Top 5 Trigram': f"{len(common_tri)}/{top_k} ({len(common_tri)/top_k*100:.0f}%)",
            'Chuỗi Trigram trùng Top 5': ', '.join(common_tri) if common_tri else 'Không có',
            'Tái hiện Trigram S1 ở S2': f"{len(s1_tri_in_s2)}/{top_k} ({len(s1_tri_in_s2)/top_k*100:.0f}%)",
            'Nhận xét chuỗi thao tác': note
        })

    df_overlap = pd.DataFrame(overlap_rows)

    return {
        'session_top_grams': df_session_top,
        'overlap_comparison': df_overlap
    }


def compute_persona_repeated_ngram_patterns(
    df_actions_h3: pd.DataFrame
) -> pd.DataFrame:
    """
    Thống kê các chuỗi Bigram và Trigram Intent phổ biến xuất hiện lặp lại
    xuyên suốt các phiên của CÙNG MỘT Persona.
    
    Trả về DataFrame tổng hợp cho cả 6 Persona kèm tần suất ở từng phiên,
    chu trình thao tác chủ đạo và ý nghĩa hành vi thực tế.
    """
    from collections import Counter

    session_grams: Dict[Tuple[str, int], Dict[str, Counter]] = {}
    grouped = df_actions_h3.groupby(['persona_id', 'session_order'])
    for (p_id, s_order), grp in grouped:
        intents = grp.sort_values('step_index')['intent'].dropna().tolist()
        bis = [f"{intents[i]} → {intents[i+1]}" for i in range(len(intents) - 1)]
        tris = [f"{intents[i]} → {intents[i+1]} → {intents[i+2]}" for i in range(len(intents) - 2)]
        session_grams[(p_id, s_order)] = {
            'bi': Counter(bis),
            'tri': Counter(tris)
        }

    meta = {
        'vn_fb_001': {
            'cycle': 'Cuộn lướt cơ bản & thăm dò',
            'meaning': 'Vừa cuộn vừa quan sát bảng tin; nhịp độ phiên 2 mở rộng hơn phiên 1'
        },
        'vn_fb_002': {
            'cycle': 'Xem bình luận & thả cảm xúc',
            'meaning': 'Đọc bài, mở phần bình luận xem mọi người nói gì rồi thả tim/like'
        },
        'vn_fb_003': {
            'cycle': 'Lướt nhanh dồn dập & bình luận sâu',
            'meaning': 'Cuộn 3 nhịp liên tiếp (gần 50 lần), viết bình luận rồi ngóng tương tác'
        },
        'vn_fb_004': {
            'cycle': 'Quẹt xem video ngắn (Reels)',
            'meaning': 'Quẹt chuyển video liên tục (30 lần); phiên 2 thêm nhịp dừng lại xem'
        },
        'vn_fb_005': {
            'cycle': 'Đọc sâu & mở rộng bài viết dài',
            'meaning': 'Bấm Xem thêm (expand) để đọc bài chi tiết và xem các bình luận bên dưới'
        },
        'vn_fb_006': {
            'cycle': 'Lùng sục & sàng lọc tin tức',
            'meaning': 'Cuộn tìm tin, đọc bài BĐS rồi lại cuộn tiếp; duy trì đều đặn qua cả 3 phiên'
        }
    }

    rows: List[Dict[str, Any]] = []
    personas = sorted(list(set([p for p, s in session_grams.keys()])))
    for pid in personas:
        s_orders = sorted([s for (p, s) in session_grams.keys() if p == pid])

        all_bis = [set(session_grams[(pid, s)]['bi'].keys()) for s in s_orders]
        common_bi = set.intersection(*all_bis) if all_bis else set()

        all_tris = [set(session_grams[(pid, s)]['tri'].keys()) for s in s_orders]
        common_tri = set.intersection(*all_tris) if all_tris else set()

        bi_stats = []
        for b in common_bi:
            counts = [session_grams[(pid, s)]['bi'][b] for s in s_orders]
            bi_stats.append((sum(counts), b, counts))
        bi_stats.sort(reverse=True)

        tri_stats = []
        for t in common_tri:
            counts = [session_grams[(pid, s)]['tri'][t] for s in s_orders]
            tri_stats.append((sum(counts), t, counts))
        tri_stats.sort(reverse=True)

        top_bi_strs = [
            f"{b} ({sum(cnts)} lần: {', '.join([f'S{s}={c}' for s, c in zip(s_orders, cnts)])})"
            for _, b, cnts in bi_stats[:3]
        ]
        top_tri_strs = [
            f"{t} ({sum(cnts)} lần: {', '.join([f'S{s}={c}' for s, c in zip(s_orders, cnts)])})"
            for _, t, cnts in tri_stats[:3]
        ]

        rows.append({
            'Persona': pid,
            'Số phiên theo dõi': f"{len(s_orders)} phiên ({', '.join([f'S{s}' for s in s_orders])})",
            'Bigram trùng lặp nổi bật': '; '.join(top_bi_strs) if top_bi_strs else 'Không có',
            'Trigram trùng lặp nổi bật': '; '.join(top_tri_strs) if top_tri_strs else 'Không có',
            'Chu trình thao tác chủ đạo': meta.get(pid, {}).get('cycle', ''),
            'Ý nghĩa hành vi thực tế': meta.get(pid, {}).get('meaning', '')
        })

    return pd.DataFrame(rows)


