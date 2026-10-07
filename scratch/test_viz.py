import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from loaders.action_loader import ActionLoader
from algorithms.cross_session_behavior_profiler import (
    prepare_h3_dataset,
    extract_cross_session_entities,
    compute_multi_level_consistency,
    compute_macro_surface_transitions,
    compute_surface_retention,
    compute_habit_evolution_and_correlation
)

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)
df_sessions = loader.to_unified_sessions_dataframe(histories)

df_actions_h3, df_sessions_h3 = prepare_h3_dataset(df_actions, df_sessions)
print("df_actions_h3 shape:", df_actions_h3.shape)

entity_res = extract_cross_session_entities()
print("entity continuity map entries:", len(entity_res['continuity_map']))
print("authors df count:", len(entity_res['authors_df']))
print("groups df count:", len(entity_res['groups_df']))

df_multi = compute_multi_level_consistency(df_actions_h3, df_sessions_h3, entity_res['continuity_map'])
print("df_multi shape:", df_multi.shape)

trans_res = compute_macro_surface_transitions(df_actions_h3)
print("trans_res total shifts:", trans_res['total_shifts'])
print("trans_res path summary:\n", trans_res['path_summary'])

ret_df = compute_surface_retention(df_actions_h3)
print("ret_df shape:", ret_df.shape)

evo_res = compute_habit_evolution_and_correlation(df_actions_h3)
print("evo_res intra mean:", evo_res['intra_mean'])
print("evo_res inter mean:", evo_res['inter_mean'])
