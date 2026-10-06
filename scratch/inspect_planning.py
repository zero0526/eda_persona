import sqlite3, json

conn = sqlite3.connect(r'D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite')
cursor = conn.cursor()
r = cursor.execute("SELECT response_json FROM planning_attempts LIMIT 1").fetchone()
if r:
    d = json.loads(r[0])
    print('response_json type:', type(d))
    if isinstance(d, list) and d:
        print('response_json[0] keys:', d[0].keys())
        print('response_json[0]:', d[0])
