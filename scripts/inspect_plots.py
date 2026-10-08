import sys
import nbformat

sys.stdout.reconfigure(encoding='utf-8')

nb = nbformat.read('notebooks/notebook_action_logs.ipynb', as_version=4)
for i in [6, 7, 9, 12, 14, 16, 18, 21, 23, 24]:
    print(f'*** Cell {i} ***')
    for line in nb.cells[i].source.split('\n'):
        if any(k in line.lower() for k in ['title', 'xlabel', 'ylabel', 'suptitle', 'savefig', '# figure', '# bảng', '# biểu đồ', 'plt.figure']):
            print(' ', line.strip())
