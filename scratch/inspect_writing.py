import sqlite3, json

conn = sqlite3.connect(r'D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite')
cursor = conn.cursor()
for r in cursor.execute("SELECT snapshot_json FROM episode_working_memory").fetchall():
    d = json.loads(r[0])
    wm = d.get('working_memory', {})
    row = wm.get('recent_own_writing')
    if row:
        print('subject keys:', row[0].get('subject', {}).keys())
        break
