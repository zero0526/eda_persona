import sys
import difflib

sys.stdout.reconfigure(encoding='utf-8')

with open('notebooks/slide.md', 'r', encoding='utf-8') as f:
    current_content = f.read()

start_marker = '## 🖥️ SLIDE 2.5: TỔNG QUAN MA TRẬN PHÂN HÓA ĐỘNG LỰC TOÀN HỆ THỐNG & NGUYÊN TẮC NHẬN THỨC 1-1'
end_marker = '\n---\n\n## 🖥️ SLIDE 2.6: TÍNH LIÊN KẾT THÔNG TIN XUYÊN PHIÊN'

start_idx = current_content.find(start_marker)
end_idx = current_content.find(end_marker)

existing_section = current_content[start_idx:end_idx].strip()

# Read the target text from user prompt (saved in scratch)
with open('scratch/user_target_s25.txt', 'r', encoding='utf-8') as f:
    user_target = f.read().strip()

diff = list(difflib.unified_diff(
    existing_section.splitlines(keepends=True),
    user_target.splitlines(keepends=True),
    fromfile='file_on_disk',
    tofile='user_target'
))

if not diff:
    print('EXACT MATCH! No differences found at all!')
else:
    print('Found differences:')
    for line in diff:
        print(line, end='')
