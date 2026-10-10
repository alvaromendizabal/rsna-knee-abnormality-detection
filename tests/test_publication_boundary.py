"""Publication checks use temporary Git repositories and inert generated fixtures."""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('publication_boundary', ROOT / 'tools/check_publication_boundary.py')
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


def github_fixture():
    return 'gh' + 'p_' + 'aB7c' * 9


def aws_fixture():
    return 'AK' + 'IA' + 'A1B2' * 4


class PublicationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git('init', '--quiet')

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data.encode() if isinstance(data, str) else data)
        return path

    def rules(self):
        return {issue['rule'] for issue in guard.scan_repository(self.root)['issues']}

    def test_source_docs_and_aggregate_configuration_are_allowed(self):
        self.write('README.md', 'Use environment variables; never publish aws_secret_access_key.\n')
        self.write('src/demo.py', "import os\nvalue = os.environ['AWS_SECRET_ACCESS_KEY']\n")
        self.write('configs/metrics.csv', 'metric,value\nmacro_auc,0.75\n')
        self.write('reports/results.json', json.dumps({'rows': 870, 'macro_auc': .75}))
        self.git('add', 'README.md')
        report = guard.scan_repository(self.root)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual((report['index_files'], report['candidate_files']), (1, 4))
        self.assertFalse(report['history_scanned'])

    def test_ignored_private_data_is_not_opened_but_forced_tracking_fails(self):
        self.write('.gitignore', 'data/\ndemo-output/\n')
        self.write('data/private.dcm', b'private')
        self.write('demo-output/submission.csv', 'irrelevant')
        self.assertEqual(guard.scan_repository(self.root)['status'], 'PASS')
        self.git('add', '--force', 'data/private.dcm')
        self.assertIn('PRIVATE_DIRECTORY', self.rules())

    def test_staged_secret_is_detected_after_working_copy_is_cleaned(self):
        token = github_fixture()
        path = self.write('config.txt', token)
        self.git('add', 'config.txt')
        path.write_text('safe replacement\n')
        report = guard.scan_repository(self.root)
        self.assertEqual(report['issues'], [{'path': 'config.txt', 'location': 'index', 'rule': 'GITHUB_TOKEN'}])
        self.assertNotIn(token, json.dumps(report))

    def test_untracked_and_working_tree_credentials_are_checked(self):
        self.write('safe.txt', 'safe')
        self.git('add', 'safe.txt')
        self.write('safe.txt', aws_fixture())
        self.write('new.txt', github_fixture())
        self.assertEqual(self.rules(), {'AWS_ACCESS_KEY', 'GITHUB_TOKEN'})

    def test_credential_signatures_without_echoing_matches(self):
        fixtures = {
            'AWS_ACCESS_KEY': aws_fixture(),
            'GITHUB_TOKEN': github_fixture(),
            'GITHUB_FINE_GRAINED_TOKEN': 'github_' + 'pat_' + 'b8' * 30,
            'AWS_SECRET_VALUE': 'aws_secret_access_key = ' + 'aB/+' * 10,
            'PRIVATE_KEY': '-----BEGIN ' + 'OPENSSH PRIVATE KEY-----',
        }
        for rule, value in fixtures.items():
            with self.subTest(rule=rule):
                self.assertIn(rule, guard.inspect_bytes('example.txt', value.encode()))
        self.assertEqual(guard.inspect_bytes('README.md', b'AKIAIOSFODNN7EXAMPLE'), [])
        self.assertEqual(guard.inspect_bytes('config.py', b"key = os.environ['AWS_SECRET_ACCESS_KEY']"), [])
        self.assertEqual(guard.inspect_bytes('docs.md', b'github_pat_<YOUR_TOKEN>'), [])

    def test_raw_arrays_weights_archives_and_private_runner_files_fail(self):
        for name in ('scan.dcm', 'scan.nii.gz', 'weights.pth', 'model.safetensors',
                     'outputs.npz', 'table.parquet', 'handoff.zip', 'run.pyz',
                     'runner115.py', 'runner115v5/entry.py', 'runners/main.py'):
            with self.subTest(name=name):
                self.assertTrue(guard.inspect_bytes(name, b'placeholder'))
        self.assertEqual(guard.inspect_bytes('research/teacher/run.py', b'print("example")'), [])

    def test_mislabeled_binary_and_large_files_fail(self):
        for raw in (b'\x00hidden', b'\xff\xfe', b'PK\x03\x04payload', b'\x93NUMPYhidden', b' ' * 128 + b'DICM'):
            with self.subTest(signature=hashlib.sha256(raw).hexdigest()):
                self.assertTrue(guard.inspect_bytes('notes.txt', raw))
        self.assertEqual(guard.inspect_bytes('large.txt', b'x' * (guard.MAX_PUBLIC_BYTES + 1)), ['UNEXPECTED_LARGE_FILE'])

    def test_real_row_csv_is_rejected_even_under_examples(self):
        for name in ('reports/predictions.csv', 'examples/predictions.csv', 'table.csv'):
            self.assertIn('PRIVATE_ROW_LEVEL_DATA', guard.inspect_bytes(name, b'StudyInstanceUID,ACL\n123456,0.4\n'))
        self.assertIn('PRIVATE_ROW_LEVEL_DATA', guard.inspect_bytes('predictions.csv', b'ACL,PCL\n0.4,0.5\n'))

    def test_synthetic_csv_requires_both_location_and_explicit_ids(self):
        raw = b'StudyInstanceUID,ACL\nsynthetic-0,0.1\nfixture-1,0.9\n'
        self.assertEqual(guard.inspect_bytes('examples/predictions.csv', raw), [])
        self.assertEqual(guard.inspect_bytes('tests/fixtures/submission.csv', raw), [])
        self.assertIn('PRIVATE_ROW_LEVEL_DATA', guard.inspect_bytes('reports/predictions.csv', raw))
        self.assertIn('PRIVATE_ROW_LEVEL_DATA', guard.inspect_bytes('examples/predictions.csv', b'ACL\n0.1\n'))

    def test_row_json_cannot_be_disguised_as_an_aggregate_or_synthetic_fixture(self):
        raw = json.dumps({'ids': ['patient-real'], 'predictions': [[.1, .2]]}).encode()
        self.assertIn('PRIVATE_ROW_LEVEL_DATA', guard.inspect_bytes('reports/results.json', raw))
        self.assertIn('PRIVATE_ROW_LEVEL_DATA', guard.inspect_bytes('examples/fixture.json', raw))
        raw = json.dumps({'ids': ['synthetic-1'], 'predictions': [[.1, .2]]}).encode()
        self.assertEqual(guard.inspect_bytes('examples/predictions.json', raw), [])
        self.assertIn('PRIVATE_ROW_LEVEL_DATA', guard.inspect_bytes('examples/fixture.json', b'{"predictions":[[0.1]]}'))

    def test_notebook_credentials_are_scanned(self):
        raw = json.dumps({'cells': [{'outputs': [{'text': github_fixture()}]}]}).encode()
        self.assertIn('GITHUB_TOKEN', guard.inspect_bytes('notebooks/demo.ipynb', raw))

    def test_symlink_is_not_followed(self):
        (self.root / 'link.txt').symlink_to('/not/a/public/file')
        self.assertIn('SYMLINK_NOT_ALLOWED', self.rules())
        self.git('add', 'link.txt')
        self.assertIn('NONREGULAR_OR_UNMERGED_INDEX_ENTRY', self.rules())

    def test_existing_asset_allowance_requires_exact_path_and_bytes(self):
        for name in (next(x for x in guard.AUDITED_ASSETS if x.endswith('.png')),
                     next(x for x in guard.AUDITED_ASSETS if x.endswith('.js'))):
            raw = (ROOT / name).read_bytes()
            self.assertEqual(guard.inspect_bytes(name, raw), [])
            self.assertEqual(guard.inspect_bytes(name, raw + b'changed'), ['AUDITED_ASSET_CHANGED'])
            self.assertTrue(guard.inspect_bytes('elsewhere/' + Path(name).name, raw))

    def test_cli_reports_only_safe_locations_and_rules(self):
        token = github_fixture()
        self.write('leak.txt', token)
        output = io.StringIO()
        with redirect_stdout(output):
            code = guard.main(['--root', str(self.root)])
        self.assertEqual(code, 1)
        self.assertNotIn(token, output.getvalue())
        self.assertEqual(json.loads(output.getvalue())['issues'][0]['rule'], 'GITHUB_TOKEN')

    def test_scanning_subdirectory_is_rejected(self):
        child = self.root / 'nested';child.mkdir()
        with self.assertRaisesRegex(ValueError, 'CHECK_REPOSITORY_ROOT_REQUIRED'):
            guard.scan_repository(child)


if __name__ == '__main__':
    unittest.main()
