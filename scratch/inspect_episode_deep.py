import sqlite3
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

target_ep_id = "9e8baabb-5691-4c15-b278-0b5534c6ee08"
print(f"Targeting episode: {target_ep_id}")

# 1. Episode row
cur.execute("SELECT * FROM episodes WHERE id = ?", (target_ep_id,))
ep_row = dict(cur.fetchone())

# 2. Associated bot
bot_row = None
if ep_row.get("bot_id"):
    cur.execute("SELECT * FROM bots WHERE id = ?", (ep_row["bot_id"],))
    b = cur.fetchone()
    if b:
        bot_row = dict(b)

# 3. Associated persona version
persona_row = None
if bot_row:
    cur.execute("SELECT * FROM persona_versions WHERE bot_id = ? ORDER BY version DESC LIMIT 1", (bot_row["id"],))
    p = cur.fetchone()
    if p:
        persona_row = dict(p)

# 4. Behavioral contract
contract_row = None
if ep_row.get("contract_id"):
    cur.execute("SELECT * FROM behavioral_contracts WHERE id = ?", (ep_row["contract_id"],))
    c = cur.fetchone()
    if c:
        contract_row = dict(c)

# 5. Activity window
window_row = None
if ep_row.get("window_id"):
    cur.execute("SELECT * FROM activity_windows WHERE id = ?", (ep_row["window_id"],))
    w = cur.fetchone()
    if w:
        window_row = dict(w)

# 6. agent_live_runs
cur.execute("SELECT * FROM agent_live_runs WHERE episode_id = ?", (target_ep_id,))
run_row = cur.fetchone()
run_dict = dict(run_row) if run_row else None

# 7. episode_working_memory
cur.execute("SELECT * FROM episode_working_memory WHERE episode_id = ?", (target_ep_id,))
wm_row = cur.fetchone()
wm_dict = dict(wm_row) if wm_row else None

# 8. agent_live_steps
cur.execute("SELECT * FROM agent_live_steps WHERE episode_id = ? ORDER BY step_index", (target_ep_id,))
steps = [dict(r) for r in cur.fetchall()]

# 9. decision_evidence
cur.execute("SELECT * FROM decision_evidence WHERE episode_id = ? ORDER BY step_index", (target_ep_id,))
evidences = [dict(r) for r in cur.fetchall()]

# 10. episode_events
cur.execute("SELECT * FROM episode_events WHERE episode_id = ? ORDER BY created_at", (target_ep_id,))
events = [dict(r) for r in cur.fetchall()]

# 11. search_history
cur.execute("SELECT * FROM search_history WHERE episode_id = ? ORDER BY step_index", (target_ep_id,))
searches = [dict(r) for r in cur.fetchall()]

# 12. memory_consolidation_runs
cur.execute("SELECT * FROM memory_consolidation_runs WHERE episode_id = ?", (target_ep_id,))
consolidation = [dict(r) for r in cur.fetchall()]

# 13. memory_delta_ledger
cur.execute("SELECT * FROM memory_delta_ledger WHERE episode_id = ? ORDER BY created_at", (target_ep_id,))
deltas = [dict(r) for r in cur.fetchall()]

# 14. habit_facts
cur.execute("SELECT * FROM habit_facts WHERE episode_id = ?", (target_ep_id,))
habits = [dict(r) for r in cur.fetchall()]

# 15. benchmark_trials
cur.execute("SELECT * FROM benchmark_trials WHERE episode_id = ?", (target_ep_id,))
benchmarks = [dict(r) for r in cur.fetchall()]

def safe_json(val):
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return val

deep_summary = {
    "target_episode_id": target_ep_id,
    "ep_row": ep_row,
    "bot_row": bot_row,
    "persona_row_preview": {k: (safe_json(v) if "json" in k else v) for k, v in (persona_row or {}).items()},
    "contract_row_preview": {k: (safe_json(v) if "json" in k else v) for k, v in (contract_row or {}).items()},
    "window_row": window_row,
    "run_row_preview": {k: (safe_json(v) if "json" in k else v) for k, v in (run_dict or {}).items()},
    "working_memory_preview": safe_json(wm_dict["snapshot_json"]) if wm_dict and wm_dict.get("snapshot_json") else None,
    "sample_step_payload": safe_json(steps[0]["payload_json"]) if steps else None,
    "step_count": len(steps),
    "sample_evidence": {
        "step_index": evidences[0]["step_index"],
        "action": evidences[0]["action"],
        "payload": safe_json(evidences[0]["evidence_json"])
    } if evidences else None,
    "evidence_count": len(evidences),
    "sample_event": {
        "kind": events[0]["kind"],
        "payload": safe_json(events[0]["payload_json"])
    } if events else None,
    "event_count": len(events),
    "search_count": len(searches),
    "sample_search": searches[0] if searches else None,
    "consolidation_count": len(consolidation),
    "sample_consolidation": {k: (safe_json(v) if "json" in k else v) for k, v in consolidation[0].items()} if consolidation else None,
    "delta_count": len(deltas),
    "sample_delta": {
        "record_type": deltas[0]["record_type"],
        "record_key": deltas[0]["record_key"],
        "operation": deltas[0]["operation"],
        "before": safe_json(deltas[0]["before_json"]),
        "after": safe_json(deltas[0]["after_json"]),
        "evidence": safe_json(deltas[0]["evidence_json"]),
    } if deltas else None,
    "habit_count": len(habits),
    "benchmark_count": len(benchmarks),
}

with open("scratch/episode_deep_summary.json", "w", encoding="utf-8") as f:
    json.dump(deep_summary, f, indent=2, ensure_ascii=False)

print("Saved scratch/episode_deep_summary.json successfully.")
