import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("notebooks/eda_action_logs.ipynb")
print(f"Reading notebook: {nb_path}...")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

client = NotebookClient(nb, timeout=600, kernel_name="python3")
print("Executing notebook...")
try:
    client.execute()
    print("Notebook executed successfully without errors!")
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print("Saved executed notebook with outputs!")
except Exception as e:
    print(f"[!] Error during execution: {e}")
    sys.exit(1)
