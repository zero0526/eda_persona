import nbformat
from nbclient import NotebookClient
from pathlib import Path
import sys, io

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

nb_path = Path("notebooks/notebook_action_logs.ipynb")
nb = nbformat.read(nb_path, as_version=4)

print(f"Executing notebook: {nb_path} ({len(nb.cells)} cells)...")
client = NotebookClient(nb, timeout=600, kernel_name="python3")
client.execute()

nbformat.write(nb, nb_path)
print("Notebook executed and saved successfully with all cell outputs!")
