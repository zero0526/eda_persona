import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

tex_path = Path('notebooks/eda_action_logs.tex')
if not tex_path.exists():
    tex_path = Path('eda_action_logs.tex')

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

images = re.findall(r'\\includegraphics(?:\[.*?\])?\{(.*?)\}', content)
print("All includegraphics in tex:")
for img in images:
    resolved = Path(img)
    exists_as_is = resolved.exists()
    exists_relative_nb = (Path('notebooks') / img).exists()
    exists_from_root = (Path('.') / img.lstrip('/')).exists()
    print(f"  {img:60s} -> as_is: {exists_as_is}, rel_nb: {exists_relative_nb}, from_root: {exists_from_root}")
