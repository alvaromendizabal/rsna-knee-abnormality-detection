#!/usr/bin/env python3
"""Verify saved notebook outputs against public evidence; also works with python -O."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from rsna_review.evidence import verify_notebook

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notebook', type=Path)
    parser.add_argument('--number', choices=('12', '13', '14'), default='14')
    args = parser.parse_args()
    verify_notebook(ROOT, args.notebook, args.number)
    print('PUBLIC_REVIEW_NOTEBOOK_VERIFIED')
