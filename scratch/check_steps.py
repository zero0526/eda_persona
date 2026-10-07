import json

with open(r'C:\Users\KHOENV\.gemini\antigravity-ide\brain\f5404ff5-b699-42a9-9abe-0d48e9402732\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        idx = data.get('step_index')
        if idx and idx >= 2715 and idx <= 2743:
            print(f"--- Step {idx} ({data.get('type')}) ---")
            c = str(data.get('content'))
            print(c[:300].encode('ascii', 'backslashreplace').decode('ascii'))
            if data.get('tool_calls'):
                tc = repr(data.get('tool_calls'))
                print("Tool calls:", tc[:300].encode('ascii', 'backslashreplace').decode('ascii'))
