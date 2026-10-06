import sqlite3, json

conn = sqlite3.connect(r'D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite')
cursor = conn.cursor()
for r in cursor.execute("SELECT snapshot_json FROM episode_working_memory").fetchall():
    d = json.loads(r[0])
    wm = d.get('working_memory', {})
    for field in ['opened_sources', 'searched_topics']:
        items = wm.get(field)
        if items and isinstance(items[0], dict):
            print(field, 'dict keys:', items[0].keys())
