import json
import subprocess
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parent.parent

# Step 1: Fix notebook markdown image path and box drawing characters
nb_path = project_root / 'notebooks' / 'eda_action_logs.ipynb'
print(f"[1/4] Đang chuẩn hóa ký tự Unicode và đường dẫn ảnh trong {nb_path.name}...")
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        new_source = []
        for line in cell['source']:
            # Replace box-drawing chars with ASCII
            line = line.replace('───[1:N]───>', '---[1:N]--->')
            line = line.replace('├───[1:N]───>', '+---[1:N]--->')
            line = line.replace('└───[1:N]───>', '\\---[1:N]--->')
            # Fix leading slash image path
            line = line.replace('../output/figures/agent_loop.png', 'output/figures/agent_loop.png')
            line = line.replace('/output/figures/agent_loop.png', 'output/figures/agent_loop.png')
            new_source.append(line)
        cell['source'] = new_source

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

# Step 2: Run jupyter nbconvert to latex
print("[2/4] Chuyển đổi notebook sang LaTeX (jupyter nbconvert)...")
cmd_nbconvert = [
    str(project_root / '.venv' / 'Scripts' / 'jupyter.exe'),
    'nbconvert',
    '--to', 'latex',
    '--output-dir', str(project_root / 'notebooks'),
    str(nb_path)
]
res_nbconvert = subprocess.run(cmd_nbconvert, capture_output=True, text=True, cwd=str(project_root))
print("nbconvert status:", res_nbconvert.returncode)
if res_nbconvert.returncode != 0:
    print(res_nbconvert.stderr)

# Step 3: Patch notebooks/eda_action_logs.tex
tex_file = project_root / 'notebooks' / 'eda_action_logs.tex'
print(f"[3/4] Tinh chỉnh file LaTeX {tex_file.name}...")
with open(tex_file, 'r', encoding='utf-8') as f:
    tex_content = f.read()

# 3.1. Define missing counter 'none'
if r'\newcounter{none}' not in tex_content:
    tex_content = tex_content.replace(r'\begin{document}', "\\newcounter{none}\n\\begin{document}")

# 3.2. Fix image path /output/figures to ../output/figures
tex_content = re.sub(r'\{/output/figures/(.*?)\}', r'{../output/figures/\1}', tex_content)
tex_content = re.sub(r'\{output/figures/(.*?)\}', r'{../output/figures/\1}', tex_content)

# 3.3. Add graphicspath so LaTeX finds images both locally and in root
graphicspath_def = r"\graphicspath{{../output/figures/}{output/figures/}{../}{./}{eda_action_logs_files/}}"
if r'\graphicspath' not in tex_content:
    tex_content = tex_content.replace(r'\begin{document}', f"{graphicspath_def}\n\\begin{{document}}")

# 3.4. Support checkmark ✓ and monospace font if xetex
font_patch = r"""
\usepackage{newunicodechar}
\newunicodechar{✓}{\ensuremath{\checkmark}}
\newunicodechar{─}{-}
\newunicodechar{├}{|}
\newunicodechar{└}{\textbackslash}
"""
if r'\newunicodechar{✓}' not in tex_content:
    tex_content = tex_content.replace(r'\begin{document}', f"{font_patch}\n\\begin{{document}}")

with open(tex_file, 'w', encoding='utf-8') as f:
    f.write(tex_content)

# Also ensure output/figures/agent_loop.png is copied to notebooks/ if needed
(project_root / 'notebooks' / 'output' / 'figures').mkdir(parents=True, exist_ok=True)
import shutil
shutil.copy2(project_root / 'output' / 'figures' / 'agent_loop.png', project_root / 'notebooks' / 'output' / 'figures' / 'agent_loop.png')

print("Patching complete!")
