"""Memory gates remain enforced when Linux process IDs are remapped."""
import json

import pytest

from rsna_knee import runtime


def unavailable_process():
    raise runtime.psutil.NoSuchProcess(2)


def test_pid_namespace_fallback_keeps_memory_gate(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime.psutil, 'Process', unavailable_process)
    original_read = runtime.Path.read_text

    def read_statm(path, *args, **kwargs):
        if str(path) == '/proc/self/statm':
            return '100 64 0 0 0 0 0\n'
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(runtime.Path, 'read_text', read_statm)
    monkeypatch.setattr(runtime.os, 'sysconf', lambda key: 4096)
    progress = runtime.Progress(tmp_path / 'progress.jsonl', rss_gib=1)
    progress.log('schema', 'started')
    assert json.loads(progress.path.read_text())['rss_gib'] == 0.0
    assert runtime.current_rss_bytes() == 262144
    progress.rss_gib = 0.0001
    with pytest.raises(RuntimeError, match='memory limit'):
        progress.log('schema', 'still_enforced')


def test_missing_memory_telemetry_fails_closed(monkeypatch):
    monkeypatch.setattr(runtime.psutil, 'Process', unavailable_process)

    def denied(*args, **kwargs):
        raise PermissionError('restricted procfs')

    monkeypatch.setattr(runtime.Path, 'read_text', denied)
    with pytest.raises(RuntimeError, match='telemetry is unavailable'):
        runtime.current_rss_bytes()
