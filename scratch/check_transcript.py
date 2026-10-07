import json

with open(r'C:\Users\KHOENV\.gemini\antigravity-ide\brain\f5404ff5-b699-42a9-9abe-0d48e9402732\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines:
    data = json.loads(line)
    if data.get('type') == 'USER_INPUT':
        txt = str(data.get('content'))[:140].replace('\n', ' ')
        print(f"Step {data.get('step_index')}: {txt.encode('ascii', 'backslashreplace').decode('ascii')}")
