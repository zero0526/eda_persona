import sqlite3
import re

conn = sqlite3.connect('data/persona-runner.sqlite')
cursor = conn.cursor()

tables = ['episodes', 'episode_events', 'agent_live_runs', 'agent_live_steps', 'benchmark_trials', 'decision_evidence']
for t in tables:
    cursor.execute(f"PRAGMA table_info({t});")
    cols = [c[1] for c in cursor.fetchall()]
    text_cols = [c for c in cols if 'json' in c.lower() or 'summary' in c.lower() or 'state' in c.lower() or 'report' in c.lower()]
    for tc in text_cols:
        cursor.execute(f"SELECT COUNT(*) FROM {t} WHERE {tc} LIKE '%pace=%';")
        cnt = cursor.fetchone()[0]
        if cnt > 0:
            print(f"Table {t}, col {tc}: {cnt} rows contain 'pace='")
