import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient

sys.stdout.reconfigure(encoding='utf-8')

notebook_path = Path("notebooks/notebook_action_logs.ipynb")
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

client = NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': str(notebook_path.parent)}})
print("Bắt đầu thực thi toàn bộ notebook để làm mới biểu đồ và bảng số liệu...")
client.execute()

with open(notebook_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("✅ Đã thực thi và lưu lại toàn bộ notebook với số liệu mới thành công!")
