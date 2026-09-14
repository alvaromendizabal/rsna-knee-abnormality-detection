#!/usr/bin/env python3
"""User-run allowlist check of a showcase directory or clone, ignoring .git internals."""
from pathlib import Path
import argparse
import json
import re
ALLOWED={'README.md','RESEARCH_OVERVIEW.md','RESULTS.md','NOTICE.md','SECURITY.md','.gitignore','reports/status.json'}
p=argparse.ArgumentParser(description=__doc__); p.add_argument('directory',type=Path); a=p.parse_args()
root=a.directory.expanduser().resolve(); found=set()
for path in root.rglob('*'):
    relative=path.relative_to(root)
    if '.git' in relative.parts: continue
    if path.is_symlink(): raise SystemExit('STOP: symlink in showcase.')
    if not path.is_file(): continue
    name=str(relative)
    if name not in ALLOWED: raise SystemExit('STOP: unapproved file in showcase: '+name)
    if path.stat().st_size>100*1024: raise SystemExit('STOP: unexpected file size.')
    text=path.read_text(encoding='utf-8')
    if re.search(r'(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN .*PRIVATE KEY-----|X-Amz-Signature=|X-Goog-Signature=)',text):
        raise SystemExit('STOP: possible secret in showcase; inspect locally.')
    found.add(name)
if found!=ALLOWED: raise SystemExit('STOP: missing showcase documents.')
s=json.loads((root/'reports/status.json').read_text())
if s.get('official_score') is not None or s.get('model_fits')!=0 or s.get('predictive_feature_gains_established') is not False:
    raise SystemExit('STOP: this release is not authorized to make predictive-score claims.')
print('SHOWCASE_ALLOWLIST_PASS. Manual content/license/history review is still required. No Git action performed.')
