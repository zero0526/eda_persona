import sqlite3, json

conn = sqlite3.connect(r'D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite')
cursor = conn.cursor()
for r in cursor.execute("SELECT payload_json FROM episode_events WHERE payload_json LIKE '%\"args\"%' LIMIT 5").fetchall():
    d = json.loads(r[0])
    print('args:', type(d.get('args')), d.get('args'))
