#!/usr/bin/env python3
"""Check the public Git index and proposed working files without printing content.

Run from any directory: python tools/check_publication_boundary.py
Only Git-tracked files and nonignored additions are candidates. Ignored private
workspaces are not opened. Index blobs are checked independently of working files,
so editing a staged secret out of the working copy cannot hide the pending commit.
This is a publication gate, not a Git-history audit or proof of anonymization.

Audited exceptions below are the existing Plotly distributions and saved chart PNGs.
Their exact path, size and SHA-256 are required; no directory-wide binary exemption
exists. Synthetic row fixtures need an examples/ or tests/fixtures/ path AND explicit
synthetic-/demo-/fixture- identifiers; aggregate configuration CSVs remain allowed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_PUBLIC_BYTES = 2 * 1024 * 1024
# Exact existing chart/library assets, not MRI or learned model artifacts.
AUDITED_ASSETS = {}  # No vendored experiment plots require binary exceptions.

PRIVATE_PARTS = {
    'data', 'artifacts', 'logs', 'returns', 'checkpoints', 'models', 'model_weights',
    'raw', 'raw_mri', 'dicom', 'dicoms', 'train_images', 'test_images',
    'private', 'private_data', 'demo-output', '.aws', '.ssh', '.huggingface',
}
PRIVATE_SUFFIXES = {
    '.dcm', '.dicom', '.nii', '.nrrd', '.mha', '.mhd', '.ima',
    '.pt', '.pth', '.ckpt', '.safetensors', '.gguf', '.onnx', '.h5', '.hdf5',
    '.npy', '.npz', '.parquet', '.feather', '.arrow', '.pkl', '.pickle', '.joblib', '.mmap',
    '.zip', '.pyz', '.tar', '.gz', '.tgz', '.bz2', '.xz', '.7z', '.rar',
}
RUNNER = re.compile(r'^(?:runners?|runner\d+(?:v\d+)?|(?:test_)?runner\d*\.py)$', re.I)
PREDICTION_NAME = re.compile(r'(?:^|[_-])(?:predictions?|submission|oof)(?:[_\-.]|$)', re.I)
IDENTIFIER_KEYS = {'studyinstanceuid', 'seriesinstanceuid', 'studyuid', 'studyid', 'patientid', 'rowid', 'ids', 'studyuids', 'patientids'}
PREDICTION_KEYS = {'predictions', 'probabilities', 'oof'}
SYNTHETIC_ID = re.compile(r'^(?:synthetic|demo|fixture)[_-][A-Za-z0-9_-]+$')
# Published AWS documentation examples are inert; no general placeholder bypass.
DOCUMENTATION_EXAMPLES = {
    'AKIAIOSFODNN7EXAMPLE',
    'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
}
CREDENTIAL_PATTERNS = (
    ('AWS_ACCESS_KEY', re.compile(r'(?<![A-Z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Z0-9])')),
    ('GITHUB_TOKEN', re.compile(r'(?<![A-Za-z0-9_])gh[pousr]_[A-Za-z0-9]{36,255}(?![A-Za-z0-9])')),
    ('GITHUB_FINE_GRAINED_TOKEN', re.compile(r'(?<![A-Za-z0-9_])github_pat_[A-Za-z0-9_]{22,255}(?![A-Za-z0-9_])')),
    ('AWS_SECRET_VALUE', re.compile(r'''(?ix)\b(?:aws_secret_access_key|secret_access_key|aws_session_token)\b["']?\s*[:=]\s*["']?([A-Za-z0-9/+=]{40,})(?![A-Za-z0-9/+=])''')),
    ('PRIVATE_KEY', re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----')),
)


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(['git', '-C', str(root), *args], stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise ValueError('GIT_INVENTORY_UNAVAILABLE')
    return result.stdout


def _path_rule(name: str) -> str | None:
    path = PurePosixPath(name)
    parts = {part.lower() for part in path.parts}
    if path.is_absolute() or '..' in path.parts or not path.parts:
        return 'UNSAFE_PATH'
    if PRIVATE_PARTS & parts or any(part.startswith('.rsna_') for part in parts):
        return 'PRIVATE_DIRECTORY'
    if any(RUNNER.fullmatch(part) for part in path.parts):
        return 'PRIVATE_RUNNER'
    if path.suffix.lower() in PRIVATE_SUFFIXES:
        return 'PRIVATE_ARTIFACT_TYPE'
    if path.name.lower() in {'kaggle.json', 'credentials', 'id_rsa', 'id_ed25519'}:
        return 'CREDENTIAL_FILE'
    if path.name == '.env' or (path.name.startswith('.env.') and path.name != '.env.example'):
        return 'CREDENTIAL_FILE'
    return None


def _synthetic_location(name: str) -> bool:
    path = PurePosixPath(name)
    return path.parts[:1] == ('examples',) or path.parts[:2] == ('tests', 'fixtures')


def _normalized(key: str) -> str:
    return ''.join(character for character in key.lower() if character.isalnum())


def _private_rows(name: str, text: str) -> bool:
    path = PurePosixPath(name)
    if path.suffix.lower() in {'.csv', '.tsv'}:
        rows = list(csv.reader(io.StringIO(text), delimiter='\t' if path.suffix.lower() == '.tsv' else ','))
        if not rows:
            return False
        identifiers = [i for i, value in enumerate(rows[0]) if _normalized(value) in IDENTIFIER_KEYS]
        sensitive = bool(identifiers or PREDICTION_NAME.search(path.name))
        if not sensitive:
            return False
        if not _synthetic_location(name) or not identifiers:
            return True
        return not all(len(row) > max(identifiers) and all(SYNTHETIC_ID.fullmatch(row[i]) for i in identifiers)
                       for row in rows[1:] if row)
    if path.suffix.lower() != '.json':
        return False
    try:
        value = json.loads(text)
    except (ValueError, RecursionError):
        return True  # A malformed JSON data artifact needs review before publication.
    identifiers = []
    def gather(item):
        if isinstance(item, dict):
            for key, child in item.items():
                if _normalized(key) in IDENTIFIER_KEYS and isinstance(child, (str, list)) and child:
                    identifiers.extend(child if isinstance(child, list) else [child])
                gather(child)
        elif isinstance(item, list):
            for child in item:
                gather(child)
    gather(value)
    synthetic = bool(_synthetic_location(name) and identifiers and
                     all(isinstance(x, str) and SYNTHETIC_ID.fullmatch(x) for x in identifiers))
    if PREDICTION_NAME.search(path.name) and not synthetic:
        return True
    def visit(item):
        if isinstance(item, dict):
            for key, child in item.items():
                key = _normalized(key)
                if key in IDENTIFIER_KEYS and isinstance(child, (str, list)) and child:
                    ids = child if isinstance(child, list) else [child]
                    if not synthetic or not all(isinstance(x, str) and SYNTHETIC_ID.fullmatch(x) for x in ids):
                        return True
                if key in PREDICTION_KEYS and isinstance(child, list) and child and not synthetic:
                    return True
                if visit(child):
                    return True
        elif isinstance(item, list):
            return any(visit(child) for child in item)
        return False
    return visit(value)


def inspect_bytes(name: str, raw: bytes) -> list[str]:
    """Return rule names only; content and matched values never leave this function."""
    rule = _path_rule(name)
    if rule:
        return [rule]
    pin = AUDITED_ASSETS.get(name)
    if pin is not None:
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            return ['AUDITED_ASSET_CHANGED']
        return []
    if len(raw) > MAX_PUBLIC_BYTES:
        return ['UNEXPECTED_LARGE_FILE']
    if raw[128:132] == b'DICM' or raw.startswith((b'PK\x03\x04', b'\x93NUMPY')):
        return ['PRIVATE_BINARY_SIGNATURE']
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        return ['UNEXPECTED_BINARY_FILE']
    if '\x00' in text:
        return ['UNEXPECTED_BINARY_FILE']
    issues = []
    for label, pattern in CREDENTIAL_PATTERNS:
        for match in pattern.finditer(text):
            candidate = match.group(1) if label == 'AWS_SECRET_VALUE' else match.group(0)
            if candidate not in DOCUMENTATION_EXAMPLES:
                issues.append(label)
                break
    if _private_rows(name, text):
        issues.append('PRIVATE_ROW_LEVEL_DATA')
    return issues


def _safe_path(name: str) -> str:
    for _, pattern in CREDENTIAL_PATTERNS:
        name = pattern.sub('[REDACTED]', name)
    return name


def scan_repository(root: Path) -> dict:
    root = root.resolve()
    actual = Path(os.fsdecode(_git(root, 'rev-parse', '--show-toplevel')).strip()).resolve()
    if actual != root:
        raise ValueError('CHECK_REPOSITORY_ROOT_REQUIRED')
    entries = {}
    issues = []
    def add(name, location, rules):
        issues.extend({'path': _safe_path(name), 'location': location, 'rule': rule} for rule in rules)
    for record in _git(root, 'ls-files', '--stage', '-z').split(b'\0'):
        if not record:
            continue
        header, raw_name = record.split(b'\t', 1)
        mode, oid, stage = header.decode('ascii').split()
        name = os.fsdecode(raw_name)
        if mode not in {'100644', '100755'} or stage != '0':
            add(name, 'index', ['NONREGULAR_OR_UNMERGED_INDEX_ENTRY'])
            continue
        entries[name] = oid
    candidates = {os.fsdecode(name) for name in _git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').split(b'\0') if name}
    for name, oid in entries.items():
        rule = _path_rule(name)
        if rule:
            add(name, 'index', [rule]); continue
        size = int(_git(root, 'cat-file', '-s', oid))
        limit = AUDITED_ASSETS.get(name, {}).get('bytes', MAX_PUBLIC_BYTES)
        if size > limit:
            add(name, 'index', ['UNEXPECTED_LARGE_FILE']); continue
        add(name, 'index', inspect_bytes(name, _git(root, 'cat-file', 'blob', oid)))
    for name in sorted(candidates):
        rule = _path_rule(name)
        if rule:
            add(name, 'working_tree', [rule]); continue
        path = root / name
        if any(parent.is_symlink() for parent in (path, *path.parents) if parent != root):
            add(name, 'working_tree', ['SYMLINK_NOT_ALLOWED']); continue
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue  # A deletion is still covered by its index blob above.
        if not stat.S_ISREG(info.st_mode):
            add(name, 'working_tree', ['NONREGULAR_FILE']); continue
        limit = AUDITED_ASSETS.get(name, {}).get('bytes', MAX_PUBLIC_BYTES)
        if info.st_size > limit:
            add(name, 'working_tree', ['UNEXPECTED_LARGE_FILE']); continue
        add(name, 'working_tree', inspect_bytes(name, path.read_bytes()))
    return {'status': 'FAIL' if issues else 'PASS', 'scope': 'git_index_and_nonignored_working_candidates',
            'history_scanned': False, 'index_files': len(entries), 'candidate_files': len(candidates),
            'audited_asset_exceptions': len(AUDITED_ASSETS), 'issues': issues}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        report = scan_repository(args.root)
    except (ValueError, OSError, subprocess.SubprocessError):
        report = {'status': 'FAIL', 'scope': 'git_index_and_nonignored_working_candidates',
                  'issues': [{'rule': 'INVENTORY_CHECK_FAILED'}]}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
