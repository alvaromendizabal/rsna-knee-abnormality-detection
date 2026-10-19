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
    args = parser.parse_args()
    verify_notebook(ROOT, args.notebook)
    print('PUBLIC_REVIEW_NOTEBOOK_VERIFIED')
