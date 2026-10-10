from dataclasses import replace
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import numpy as np
import pandas as pd
import pytest

from rsna_review import public_pipeline as pipeline


def test_resume_matches_uninterrupted_predictions_and_metrics(tmp_path, monkeypatch):
    direct = pipeline.run_pipeline(tmp_path / "direct")
    paused = pipeline.run_pipeline(tmp_path / "resumed", stop_after_fold=2)
    assert paused["status"] == "PAUSED" and paused["metrics"] is None
    resumed = pipeline.run_pipeline(tmp_path / "resumed")
    assert resumed["execution"] == {"reused_folds": 2, "fitted_folds": 3}
    assert resumed["metrics"] == direct["metrics"]
    assert resumed["predictions_sha256"] == direct["predictions_sha256"]
    assert (tmp_path / "direct/synthetic_predictions.csv").read_bytes() == (tmp_path / "resumed/synthetic_predictions.csv").read_bytes()
    monkeypatch.setattr(pipeline, "fit_fold", lambda *a, **k: pytest.fail("Completed run must not fit again"))
    repeated = pipeline.run_pipeline(tmp_path / "resumed")
    assert repeated["execution"] == {"reused_folds": 5, "fitted_folds": 0}


def test_fits_produce_valid_complete_public_metrics_and_evidence(tmp_path):
    result = pipeline.run_pipeline(tmp_path)
    frame = pd.read_csv(tmp_path / "synthetic_predictions.csv")
    values = frame[pipeline.LABELS].to_numpy()
    assert result["status"] == "COMPLETE"
    assert result["evidence_type"] == "SYNTHETIC_ONLY"
    assert result["metrics"]["n_labels"] == 12
    assert 0.5 < result["metrics"]["macro_auc_12"] < 1.0
    assert values.shape == (480, 12) and np.isfinite(values).all()
    assert ((values > 0) & (values < 1)).all()
    assert frame.synthetic_id.is_unique
    assert result["validation"]["every_row_heldout_once"] is True
    report = (tmp_path / "report.html").read_text()
    assert "not MRI training" in report and "<table>" in report
    assert json.loads((tmp_path / "results.json").read_bytes()) == result


@pytest.mark.parametrize("kind", ["scanner", "group", "row"])
def test_leakage_guard_rejects_overlapping_partitions(kind):
    config = pipeline.DemoConfig()
    data = pipeline.make_synthetic_data(config)
    train, heldout = np.flatnonzero(data.folds != 0), np.flatnonzero(data.folds == 0)
    if kind == "row":
        train = np.append(train, heldout[0])
    else:
        values = data.scanners if kind == "scanner" else data.groups
        values[heldout[0]] = values[train[0]]
    with pytest.raises(ValueError, match="Leakage"):
        pipeline.validate_split(data, train, heldout)


def test_normalization_never_uses_heldout_features():
    config = pipeline.DemoConfig()
    data = pipeline.make_synthetic_data(config)
    first = pipeline.fit_fold(data, 0, config)
    data.features[data.folds == 0] += 1000
    changed = pipeline.fit_fold(data, 0, config)
    for name in ("mean", "scale", "weights", "bias"):
        np.testing.assert_array_equal(first[name], changed[name])
    assert not np.array_equal(first["probabilities"], changed["probabilities"])


def test_corrupt_fold_rejected_without_overwriting_cache(tmp_path):
    pipeline.run_pipeline(tmp_path, stop_after_fold=1)
    path = tmp_path / "checkpoints/fold-00.npz"
    path.write_bytes(b"not an archive")
    before = (tmp_path / "checkpoint_manifest.json").read_bytes()
    with pytest.raises(pipeline.CacheValidationError, match="checksum"):
        pipeline.run_pipeline(tmp_path)
    assert path.read_bytes() == b"not an archive"
    assert (tmp_path / "checkpoint_manifest.json").read_bytes() == before


@pytest.mark.parametrize("change", ["input", "config", "source", "runtime"])
def test_changed_identity_rejects_reuse(tmp_path, monkeypatch, change):
    config = pipeline.DemoConfig()
    data = pipeline.make_synthetic_data(config)
    pipeline.run_pipeline(tmp_path, config, data=data, stop_after_fold=1)
    if change == "input":
        data.features[0, 0] += 0.001
    elif change == "config":
        config = replace(config, learning_rate=0.2)
    elif change == "source":
        monkeypatch.setattr(pipeline, "_code_fingerprint", lambda: "0" * 64)
    else:
        monkeypatch.setattr(pipeline.np, "__version__", "different-runtime")
    with pytest.raises(pipeline.CacheValidationError, match="fingerprint"):
        pipeline.run_pipeline(tmp_path, config, data=data)


def test_changed_manifest_path_is_rejected(tmp_path):
    pipeline.run_pipeline(tmp_path, stop_after_fold=1)
    path = tmp_path / "checkpoint_manifest.json"
    manifest = json.loads(path.read_bytes())
    manifest["folds"][0]["file"] = "../outside.npz"
    path.write_text(json.dumps(manifest))
    with pytest.raises(pipeline.CacheValidationError, match="identity or path"):
        pipeline.run_pipeline(tmp_path)


def test_checkpoint_symlink_is_rejected(tmp_path):
    output = tmp_path / "run"
    pipeline.run_pipeline(output, stop_after_fold=1)
    path = output / "checkpoints/fold-00.npz"
    outside = tmp_path / "outside.npz"
    path.rename(outside)
    path.symlink_to(outside)
    with pytest.raises(pipeline.CacheValidationError, match="unsafe"):
        pipeline.run_pipeline(output)
    assert outside.is_file()


def test_atomic_manifest_failure_preserves_last_committed_fold(tmp_path, monkeypatch):
    pipeline.run_pipeline(tmp_path, stop_after_fold=1)
    original = pipeline._atomic_write
    def interrupted(path, raw):
        if path.name == "checkpoint_manifest.json":
            raise OSError("simulated interruption before manifest commit")
        return original(path, raw)
    with monkeypatch.context() as patch:
        patch.setattr(pipeline, "_atomic_write", interrupted)
        with pytest.raises(OSError, match="simulated interruption"):
            pipeline.run_pipeline(tmp_path)
    assert len(json.loads((tmp_path / "checkpoint_manifest.json").read_bytes())["folds"]) == 1
    resumed = pipeline.run_pipeline(tmp_path)
    assert resumed["execution"] == {"reused_folds": 1, "fitted_folds": 4}


def test_cli_stop_resume_and_invalid_cache_exit_codes(tmp_path):
    script = Path(__file__).resolve().parents[1] / "examples/run_public_pipeline.py"
    command = [sys.executable, str(script), "--output", str(tmp_path)]
    paused = subprocess.run(command + ["--stop-after-fold", "1"], capture_output=True, text=True, check=True)
    assert json.loads(paused.stdout)["status"] == "PAUSED"
    complete = subprocess.run(command, capture_output=True, text=True, check=True)
    assert json.loads(complete.stdout)["execution"] == {"reused_folds": 1, "fitted_folds": 4}
    incompatible = subprocess.run(command + ["--seed", "7"], capture_output=True, text=True)
    assert incompatible.returncode == 2 and "fingerprint changed" in incompatible.stderr


def test_fresh_process_changed_blas_cpu_policy_rejects_resume(tmp_path):
    script = Path(__file__).resolve().parents[1] / "examples/run_public_pipeline.py"
    command = [sys.executable, "-I", str(script), "--output", str(tmp_path)]
    native = dict(os.environ)
    native.pop("OPENBLAS_CORETYPE", None)
    subprocess.run(command + ["--stop-after-fold", "1"], env=native, capture_output=True, text=True, check=True)
    changed = dict(native, OPENBLAS_CORETYPE="Haswell")
    resumed = subprocess.run(command, env=changed, capture_output=True, text=True)
    assert resumed.returncode == 2 and "fingerprint changed" in resumed.stderr
    assert len(json.loads((tmp_path / "checkpoint_manifest.json").read_bytes())["folds"]) == 1


def test_changed_blas_build_rejects_resume(tmp_path, monkeypatch):
    pipeline.run_pipeline(tmp_path, stop_after_fold=1)
    build = pipeline.np.show_config(mode="dicts")
    changed = json.loads(json.dumps(build))
    changed["Build Dependencies"]["blas"]["version"] = "different-BLAS-build"
    monkeypatch.setattr(pipeline.np, "show_config", lambda **kwargs: changed)
    with pytest.raises(pipeline.CacheValidationError, match="fingerprint"):
        pipeline.run_pipeline(tmp_path)


def test_oversized_array_header_rejected_before_numpy_allocation(monkeypatch):
    config = pipeline.DemoConfig(epochs=1)
    data = pipeline.make_synthetic_data(config)
    arrays = pipeline.fit_fold(data, 0, config)
    original = io.BytesIO()
    np.savez_compressed(original, **arrays)
    oversized_header = io.BytesIO()
    np.lib.format.write_array_header_1_0(oversized_header, {
        "descr": "<f8", "fortran_order": False, "shape": (268435456,)})
    altered = io.BytesIO()
    with zipfile.ZipFile(original) as source, zipfile.ZipFile(altered, "w", zipfile.ZIP_DEFLATED) as target:
        for name in source.namelist():
            target.writestr(name, oversized_header.getvalue() if name == "weights.npy" else source.read(name))
    assert len(altered.getvalue()) < pipeline.MAX_CHECKPOINT_BYTES
    monkeypatch.setattr(pipeline.np, "load", lambda *a, **k: pytest.fail("Must reject the header before NumPy allocation"))
    with pytest.raises(pipeline.CacheValidationError, match="Invalid checkpoint arrays"):
        pipeline._load_fold(altered.getvalue(), data, 0, config)
