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
AUDITED_ASSETS = {'reports/figures/01_metadata_and_representation_audit/8a4095f4e826bdc40b0c/plotly.min.js': {'bytes': 4763993,
                                                                                             'sha256': '122e3be346d66616944d0b83eaaf7242581508c3c1cfa0995a17af0d83eff770'},
 'reports/figures/02_protocol_feature_investigation/82d90a2f9d54f5a8cd7a/plotly.min.js': {'bytes': 4763993,
                                                                                          'sha256': '122e3be346d66616944d0b83eaaf7242581508c3c1cfa0995a17af0d83eff770'},
 'reports/figures/03_image_context_feature_investigation/6bc5b6131cb21b09e04c/plotly.min.js': {'bytes': 4763993,
                                                                                               'sha256': '122e3be346d66616944d0b83eaaf7242581508c3c1cfa0995a17af0d83eff770'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/054175b007951924.png': {'bytes': 41860,
                                                                                             'sha256': '22d34bfa520e51e5a56a3b1f407b9188a7d0000fc29307a1593383f1cf5f6582'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/186c0ce4a4c0b3d4.png': {'bytes': 83673,
                                                                                             'sha256': 'dcfc2d6ea490df19687b4c177796d70b9c15e562c64e939c7d524098d90929c7'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/36ae04a3ba905373.png': {'bytes': 38965,
                                                                                             'sha256': '9c36367fd9b1b75e4028b4f6af69b9305fc02c7710086f4a17412a77e85970ea'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/60e7ae4b138f1777.png': {'bytes': 54188,
                                                                                             'sha256': 'e014918b1d39eb0c16bfb12fc861687a81697ef3df5207b3eb1c409584a85d12'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/731b59af47d4239b.png': {'bytes': 43601,
                                                                                             'sha256': '06ed3b06d75e4383d71c04f412684392ffe5a64a29ab2d1923ed5bfac18d0413'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/900cba72416fab70.png': {'bytes': 56612,
                                                                                             'sha256': 'b5513edc0edf547c18ff95f6720ed2bf581ff6e06859f9c5393361b41aad38e5'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/9b876d274c26594d.png': {'bytes': 42509,
                                                                                             'sha256': '7c55cf4d77261aa3db19dce25166c2b92a40b9858cb1b307e3a50e22250d481b'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/aa21411ef18daf86.png': {'bytes': 38986,
                                                                                             'sha256': '2f5b9b72fa299493c25b085f3677fca5cf054364182b0fffcebdb0b0f3bb8b60'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/c7ab92227a42a9ce.png': {'bytes': 47296,
                                                                                             'sha256': 'fb1da07a4e8441f56c29c36e86ef4976b966252b60db27c95ef83787c4586114'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/cb09b9bf4b3ff8c9.png': {'bytes': 32906,
                                                                                             'sha256': '08518fdb67e9df42f4dbe541ed07c5cad7fecca9276b4e9051c11379d5cffe3f'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/d23102fd432514e7.png': {'bytes': 44277,
                                                                                             'sha256': '64c714e89f7eae8a418fe6ef9efec0ec6b50698174fdc24770127906e6f09476'},
 'reports/figures/saved_results/01_metadata_and_representation_audit/da398517727ef480.png': {'bytes': 35603,
                                                                                             'sha256': 'e211fde5b2b7ecd1afd60fe042ba031f457d8a9e0adfd9b139e33be64a752caf'},
 'reports/figures/saved_results/02_protocol_feature_investigation/1481d0bce49882fa.png': {'bytes': 47780,
                                                                                          'sha256': '26ed426b8ea2e35906cfdd0dfc43f802308e2d1bbbb47c20057a895a21152f27'},
 'reports/figures/saved_results/02_protocol_feature_investigation/1d6e427cf779db0b.png': {'bytes': 34811,
                                                                                          'sha256': '899dd6faf9d1cb913c7126dda502cbe4bb528d9be6a5d4e83c8eba71076ca66f'},
 'reports/figures/saved_results/02_protocol_feature_investigation/2cd986e66b880060.png': {'bytes': 39847,
                                                                                          'sha256': '9b87d2c3beea294b0b3fdc45a1602a20b4bdd7e123a57b841e1a5fe6117440b7'},
 'reports/figures/saved_results/02_protocol_feature_investigation/472f3540eeb856dc.png': {'bytes': 50301,
                                                                                          'sha256': '2531e46f48f18561a82c273b12a0690f7894833e5b2519a34bba1ee3ea1d9282'},
 'reports/figures/saved_results/02_protocol_feature_investigation/6eed67a207569d32.png': {'bytes': 61205,
                                                                                          'sha256': 'aa67aadf330c81420da74c4851da8a47dad2864081352465ec03ff8e098fd181'},
 'reports/figures/saved_results/02_protocol_feature_investigation/84f9863a21a16960.png': {'bytes': 48736,
                                                                                          'sha256': 'b11912fe37e8cfdcf37ca5774c14b7dd7a21d8481d2d062e87f25c2099c970d1'},
 'reports/figures/saved_results/02_protocol_feature_investigation/9218fd970c70b49f.png': {'bytes': 43893,
                                                                                          'sha256': '972c1154ac60ea9b4905e068a0a9230bfe5aff3d4815b833b55443b92a534e2f'},
 'reports/figures/saved_results/02_protocol_feature_investigation/94abc3e434d5facd.png': {'bytes': 58710,
                                                                                          'sha256': 'cd973729c787fd43677ed4c808a3c57d4d30890ece9260ed777ef7dfaa1fb35d'},
 'reports/figures/saved_results/02_protocol_feature_investigation/a6c0f2716ff2dee6.png': {'bytes': 39009,
                                                                                          'sha256': '1778f29e79e58d4a57955777a4d61f2f5d73b8e57844b7800afb59211ca515bb'},
 'reports/figures/saved_results/02_protocol_feature_investigation/aa3eef1a6dde23ec.png': {'bytes': 56073,
                                                                                          'sha256': '27dd86fb6a22565ec5ac7a26369febdc994e339d69e0958acec45d86ed804995'},
 'reports/figures/saved_results/02_protocol_feature_investigation/ba7f8059a2f2f1f1.png': {'bytes': 46798,
                                                                                          'sha256': 'ecdc58c143242c58244bdb2e4397932acdd095670e7dc8cf1eef93fb8bb9637d'},
 'reports/figures/saved_results/02_protocol_feature_investigation/e6fd6e713663b6fc.png': {'bytes': 58038,
                                                                                          'sha256': '7dfc6799ee06bca7843178d7de0f47d241054d03b193bdd8e0fbd40015d01593'},
 'reports/figures/saved_results/03_image_context_feature_investigation/01afcd95a2eafff1.png': {'bytes': 45915,
                                                                                               'sha256': '8b9936988adc332085afdeb89563b73f9ac833c740471127a64fb1a714d319b1'},
 'reports/figures/saved_results/03_image_context_feature_investigation/41bfdcb421c640bb.png': {'bytes': 50178,
                                                                                               'sha256': '52fb61f2453be18a33538e34b8f0219ae024b0600d3bd8362d9bef6c4846e9a5'},
 'reports/figures/saved_results/03_image_context_feature_investigation/6ada7ed777654d5e.png': {'bytes': 49503,
                                                                                               'sha256': '469e65471153132295f65b7ac1ae2e16114912d9103e9665b374638ef7216651'},
 'reports/figures/saved_results/03_image_context_feature_investigation/7bf169060135760e.png': {'bytes': 47727,
                                                                                               'sha256': 'cde0f8b683a8bb19d8ad032078e8ed925b6139d91c609fae84b7ff974df5d798'},
 'reports/figures/saved_results/03_image_context_feature_investigation/7f1bc6465dbbc201.png': {'bytes': 54858,
                                                                                               'sha256': 'f0b699c54b9761921533cf570a1923c2afab81e16b11981a29732dfbfb8ea3dd'},
 'reports/figures/saved_results/03_image_context_feature_investigation/93fa6db21f7f40e6.png': {'bytes': 43121,
                                                                                               'sha256': 'b8c4a0a2f354946f5acdd523f637124596d912420be5965114d8e3e21f980e42'},
 'reports/figures/saved_results/03_image_context_feature_investigation/982135a9d59f9d06.png': {'bytes': 37441,
                                                                                               'sha256': 'eeed05ddbfb797f6e96713a92310d5501c406bb88a724acea11fa481cf18efce'},
 'reports/figures/saved_results/03_image_context_feature_investigation/ba12d600e4fb898b.png': {'bytes': 49746,
                                                                                               'sha256': '976c4f04f2fe18874c5f92fa35e05f5a6ab875d7e475da042dd57277793ad965'},
 'reports/figures/saved_results/03_image_context_feature_investigation/c4ed93d5dd761c88.png': {'bytes': 51079,
                                                                                               'sha256': 'b8567493e0bff7b960c4b0a5814196b7ff158fb0ca14be0cb4047a9af27ab19f'},
 'reports/figures/saved_results/03_image_context_feature_investigation/c70dcacadd68902f.png': {'bytes': 59657,
                                                                                               'sha256': '86cf90315407289769311bc8289853c8140e8aa018954577787a80b2772b0839'},
 'reports/figures/saved_results/03_image_context_feature_investigation/d33408193e61144a.png': {'bytes': 35956,
                                                                                               'sha256': '7636e7412e73c402d5f1d41f574aecac791ca240d735d2b4d06eb8161c11ee77'},
 'reports/figures/saved_results/03_image_context_feature_investigation/ebfc6fcc506aabd3.png': {'bytes': 59745,
                                                                                               'sha256': 'ce58556a2d416a254ae6e8854a2b38c7d6ad75e31f2bf5dc604a142b78ea60d5'},
 'reports/figures/saved_results/plotly.min.js': {'bytes': 4838938,
                                                 'sha256': 'e2b0f77ee8156ff9d525852fe4acb7bfe7d85e8a2e1da0523f6d16209b848968'}}

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
