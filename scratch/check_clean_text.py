import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('notebooks/slide.md', encoding='utf-8') as f:
    text = f.read()

bad_words = ['Nam Bộ', 'lịch sử dân tộc', 'bịa', 'sinh kế', 'Tò mò Lịch sử', 'đời sống thực tế Nam Bộ', 'Tò mò bài giải']
for w in bad_words:
    for i, line in enumerate(text.splitlines(), 1):
        if w.lower() in line.lower():
            print(f'Found "{w}" at L{i}: {line[:100]}')
print("Check completed.")
