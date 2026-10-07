"""Thực thi notebook notebooks/notebook_action_logs.ipynb và lưu lại outputs."""

import nbformat
from nbclient import NotebookClient
from pathlib import Path

nb_path = Path("notebooks/notebook_action_logs.ipynb")
nb = nbformat.read(nb_path, as_version=4)

client = NotebookClient(nb, timeout=600, kernel_name="python3")
print("Executing notebook cells...")
client.execute()

nbformat.write(nb, nb_path)
print("Notebook executed successfully and saved with outputs!")
