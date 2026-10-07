#!/usr/bin/env python3
"""Execute the aggregate notebook in a real Jupyter kernel and verify saved outputs."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from rsna_review.evidence import NOTEBOOKS, fingerprints, verify_notebook

if __name__ == '__main__':
    import nbformat
    from nbclient import NotebookClient
    from jupyter_client import KernelManager

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--notebook', choices=('12', '13', '14'), default='14')
    parser.add_argument('--engine', choices=('jupyter', 'ipython-inprocess'), default='jupyter')
    args = parser.parse_args()
    notebook = nbformat.read(ROOT / NOTEBOOKS[args.notebook], as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    if args.engine == 'jupyter':
        manager = KernelManager(kernel_name='python3')
        manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
        client = NotebookClient(notebook, km=manager, timeout=90, startup_timeout=30, resources={'metadata': {'path': str(ROOT)}})
        client.execute()
    else:
        import os
        from IPython.core.interactiveshell import InteractiveShell
        from IPython.utils.capture import capture_output
        os.chdir(ROOT)
        shell = InteractiveShell.instance()
        for index, cell in enumerate((c for c in notebook.cells if c.cell_type == 'code'), 1):
            with capture_output() as captured:
                result = shell.run_cell(cell.source, store_history=False)
            if result.error_before_exec or result.error_in_exec:
                raise RuntimeError('Notebook execution failed') from (result.error_before_exec or result.error_in_exec)
            cell.execution_count = index
            for stream in ('stdout', 'stderr'):
                value = getattr(captured, stream)
                if value:
                    cell.outputs.append(nbformat.v4.new_output('stream', name=stream, text=value))
            for output in captured.outputs:
                cell.outputs.append(nbformat.v4.new_output('display_data', data=output.data, metadata=output.metadata))
    notebook.metadata['review_execution'] = {
        'engine': args.engine, 'executed_at_utc': datetime.now(timezone.utc).isoformat(),
        'python': sys.version.split()[0],
        'packages': {name: importlib.metadata.version(name) for name in ('plotly', 'matplotlib', 'nbclient', 'nbformat')},
        **fingerprints(ROOT, notebook),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, args.output)
    verify_notebook(ROOT, args.output, args.notebook)
    print('EXECUTED_SAVED_REOPENED_VERIFIED', args.output)
