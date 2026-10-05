import sqlite3

sql = sqlite3.connect('/data/projects/web-apps/agent_in_works/claw-master/data/persona-runner.sqlite')

print(sql.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
