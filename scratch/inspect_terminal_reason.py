import sqlite3, json, pandas as pd

conn = sqlite3.connect('data/persona-runner.sqlite')
df = pd.read_sql_query('SELECT id, bot_id, status, terminal_reason, summary, started_at, ended_at FROM episodes ORDER BY bot_id, id', conn)

print("--- 15 EPISODES TERMINAL REASONS & DETAILS ---")
for idx, r in df.iterrows():
    s_text = ""
    if r['summary']:
        try:
            s_obj = json.loads(r['summary'])
            s_text = s_obj.get('terminal_error', '') or s_obj.get('message', '') or str(s_obj)[:100]
        except:
            s_text = str(r['summary'])[:100]
    print(f"Persona: {r['bot_id']} | ID: {r['id'][:8]} | Status: {r['status']:7s} | Reason: {str(r['terminal_reason']):13s} | Error/Detail: {s_text[:80]}")

print("\n--- SUMMARY OF TERMINAL REASONS PER PERSONA ---")
ct = pd.crosstab(df['terminal_reason'].fillna('None (pending/running)'), df['bot_id'], margins=True)
print(ct.to_string())
