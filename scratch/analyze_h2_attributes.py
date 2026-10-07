import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import numpy as np
import pandas as pd
from scipy import stats
from dotenv import load_dotenv

load_dotenv()
from loaders.action_loader import ActionLoader

def main():
    loader = ActionLoader(os.getenv('SQLITE_PATH'))
    histories = loader.load_all_personas(source='sqlite')
    
    session_rows = []
    action_rows = []
    
    for pid, h in histories.items():
        for sess in h.sessions:
            s_sum = sess.get_summary()
            session_rows.append({
                'session_id': sess.session_id,
                'persona_id': sess.persona_id,
                'status': sess.status,
                'terminal_reason': sess.terminal_reason,
                'duration_min': round(sess.duration_seconds / 60, 2) if sess.duration_seconds else None,
                'duration_seconds': sess.duration_seconds,
                'total_actions': sess.total_actions,
                'verified_rate': sess.verified_rate,
                'total_scroll_px': sess.total_scroll_px,
                'surface_feed': sess.surface_distribution.get('feed', 0),
                'surface_detail': sess.surface_distribution.get('detail', 0),
                'surface_reels': sess.surface_distribution.get('reels', 0),
                'surface_group': sess.surface_distribution.get('group', 0),
                'surface_unknown': sess.surface_distribution.get('unknown', 0),
                'intent_observe': sess.intent_distribution.get('observe', 0),
                'intent_scroll': sess.intent_distribution.get('scroll', 0),
                'intent_read': sess.intent_distribution.get('read', 0),
                'intent_next': sess.intent_distribution.get('next', 0),
                'intent_react': sess.intent_distribution.get('react', 0),
                'intent_watch': sess.intent_distribution.get('watch', 0),
                'intent_close': sess.intent_distribution.get('close', 0),
            })
            
            for a in sess.actions:
                # Max weight from dimension_evidence
                weights = [d.weight for d in a.dimension_evidence if d.weight is not None]
                max_w = max(weights) if weights else (a.primary_weight if a.primary_weight else None)
                avg_w = float(np.mean(weights)) if weights else (a.primary_weight if a.primary_weight else None)
                
                # Cognitive latency ratio
                m_lat = a.model_latency_ms
                t_lat = a.tool_execution_ms
                cog_ratio = None
                tot_step_lat = None
                if m_lat is not None and t_lat is not None:
                    tot_step_lat = m_lat + t_lat
                    if tot_step_lat > 0:
                        cog_ratio = m_lat / tot_step_lat
                
                # Scroll speed
                scroll_spd = None
                if a.gesture_total_px is not None and a.gesture_ms is not None and a.gesture_ms > 0:
                    scroll_spd = (a.gesture_total_px / (a.gesture_ms / 1000.0))
                
                action_rows.append({
                    'session_id': sess.session_id,
                    'persona_id': sess.persona_id,
                    'step_index': a.step_index,
                    'intent': a.intent,
                    'surface': a.surface,
                    'verified': a.verified,
                    'reaction': a.reaction,
                    'model_latency_ms': m_lat,
                    'tool_execution_ms': t_lat,
                    'total_step_latency_ms': tot_step_lat,
                    'cognitive_latency_ratio': cog_ratio,
                    'primary_dimension': a.primary_dimension,
                    'primary_value': a.primary_value,
                    'primary_weight': a.primary_weight,
                    'num_dimension_evidence': len(a.dimension_evidence),
                    'dim_evidence_max_weight': max_w,
                    'dim_evidence_avg_weight': avg_w,
                    'reason': a.reason,
                    'reason_length': len(a.reason) if a.reason else 0,
                    'gesture_pace': a.gesture_pace,
                    'gesture_total_px': a.gesture_total_px,
                    'gesture_ms': a.gesture_ms,
                    'scroll_speed_px_s': scroll_spd,
                })

    df_sessions = pd.DataFrame(session_rows)
    df_actions = pd.DataFrame(action_rows)

    print("================================================================================")
    print("1. TỔNG QUAN DỮ LIỆU THU THẬP ĐƯỢC")
    print("================================================================================")
    print(f"Tổng số Sessions: {len(df_sessions)}")
    print(f"Tổng số Actions: {len(df_actions)}")
    print("Phân bố số Sessions & Actions theo Persona:")
    print(df_sessions.groupby('persona_id').agg(
        n_sessions=('session_id', 'count'),
        total_actions=('total_actions', 'sum'),
        mean_duration=('duration_min', 'mean'),
        median_duration=('duration_min', 'median'),
        mean_scroll=('total_scroll_px', 'mean'),
        median_scroll=('total_scroll_px', 'median'),
        verified_rate=('verified_rate', 'mean')
    ).round(2))

    print("\n================================================================================")
    print("2. PHÂN TÍCH PHÂN BỐ & KIỂM ĐỊNH TÍNH CHUẨN (NORMALITY TESTS)")
    print("================================================================================")
    numeric_cols = [
        'cognitive_latency_ratio',
        'primary_weight',
        'dim_evidence_max_weight',
        'num_dimension_evidence',
        'reason_length',
        'model_latency_ms',
        'tool_execution_ms',
        'gesture_total_px',
        'gesture_ms',
        'scroll_speed_px_s'
    ]
    
    stats_list = []
    for col in numeric_cols:
        series = df_actions[col].dropna()
        n = len(series)
        mean_val = series.mean()
        std_val = series.std()
        median_val = series.median()
        q25, q75 = series.quantile(0.25), series.quantile(0.75)
        iqr = q75 - q25
        skew_val = series.skew()
        kurt_val = series.kurtosis()
        
        # Normality test (D'Agostino or Shapiro)
        norm_stat, norm_p = (np.nan, np.nan)
        if n >= 20:
            norm_stat, norm_p = stats.normaltest(series)
        elif n >= 3:
            norm_stat, norm_p = stats.shapiro(series)
            
        stats_list.append({
            'Tên biến': col,
            'N': n,
            'Mean': round(mean_val, 2),
            'Std': round(std_val, 2),
            'Median': round(median_val, 2),
            'Q25': round(q25, 2),
            'Q75': round(q75, 2),
            'IQR': round(iqr, 2),
            'Skewness': round(skew_val, 2),
            'Kurtosis': round(kurt_val, 2),
            'Normality_p': f"{norm_p:.2e}" if not np.isnan(norm_p) else "N/A",
            'Is_Normal': "Chuẩn (p>=0.05)" if norm_p >= 0.05 else "Lệch/Không chuẩn"
        })
    df_desc = pd.DataFrame(stats_list)
    print(df_desc.to_string(index=False))

    print("\n================================================================================")
    print("3. PHÁT HIỆN ĐIỂM NGOẠI LAI (OUTLIER DETECTION - TUKEY IQR & MODIFIED Z-SCORE)")
    print("================================================================================")
    outlier_list = []
    for col in numeric_cols:
        series = df_actions[col].dropna()
        n = len(series)
        q25, q75 = series.quantile(0.25), series.quantile(0.75)
        iqr = q75 - q25
        lower_tukey = q25 - 1.5 * iqr
        upper_tukey = q75 + 1.5 * iqr
        n_tukey = ((series < lower_tukey) | (series > upper_tukey)).sum()
        
        # Modified Z-score (MAD)
        med = series.median()
        mad = (series - med).abs().median()
        if mad > 0:
            mod_z = 0.6745 * (series - med).abs() / mad
            n_mod_z = (mod_z > 3.5).sum()
        else:
            n_mod_z = 0
            
        outlier_list.append({
            'Tên biến': col,
            'N': n,
            'Lower_Tukey': round(lower_tukey, 2),
            'Upper_Tukey': round(upper_tukey, 2),
            'Tukey_Outliers': n_tukey,
            'Tukey_%': round(n_tukey / n * 100, 2),
            'Mod_Z_Outliers (>3.5)': n_mod_z,
            'Mod_Z_%': round(n_mod_z / n * 100, 2),
            'Min': round(series.min(), 2),
            'Max': round(series.max(), 2),
        })
    df_outliers = pd.DataFrame(outlier_list)
    print(df_outliers.to_string(index=False))

    print("\n================================================================================")
    print("4. PHÂN TÍCH THEO PERSONA (GROUP-LEVEL BREAKDOWN CHO CÁC TRƯỜNG H2)")
    print("================================================================================")
    group_stats = df_actions.groupby('persona_id').agg(
        n_actions=('step_index', 'count'),
        median_cog_ratio=('cognitive_latency_ratio', 'median'),
        mean_cog_ratio=('cognitive_latency_ratio', 'mean'),
        median_reason_len=('reason_length', 'median'),
        mean_reason_len=('reason_length', 'mean'),
        mean_max_weight=('dim_evidence_max_weight', 'mean'),
        median_dim_count=('num_dimension_evidence', 'median'),
        mean_scroll_px=('gesture_total_px', 'mean'),
        median_scroll_spd=('scroll_speed_px_s', 'median')
    ).round(2)
    print(group_stats)

    print("\n================================================================================")
    print("5. TOP PRIMARY DIMENSIONS & PHÂN PHỐI GIÁ TRỊ (PRIMARY VALUE & WEIGHT)")
    print("================================================================================")
    top_dims = df_actions['primary_dimension'].value_counts().head(10)
    print("Top 10 Primary Dimensions xuất hiện nhiều nhất:")
    for dim, count in top_dims.items():
        sub = df_actions[df_actions['primary_dimension'] == dim]
        top_vals = sub['primary_value'].value_counts().head(2).to_dict()
        mean_w = sub['primary_weight'].mean()
        print(f" - {dim:28s}: {count:3d} lần | Mean Weight: {mean_w:.2f} | Top Values: {top_vals}")

    print("\n================================================================================")
    print("6. BẢNG CHÉO (CROSSTAB) TOP PRIMARY DIMENSIONS THEO TỪNG PERSONA")
    print("================================================================================")
    ct = pd.crosstab(df_actions['primary_dimension'], df_actions['persona_id'])
    ct_top = ct.loc[top_dims.index]
    print(ct_top)

if __name__ == '__main__':
    main()
