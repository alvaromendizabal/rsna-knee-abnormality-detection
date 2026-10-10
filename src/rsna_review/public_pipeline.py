"""Offline synthetic engineering demonstration, unrelated to MRI model training.

The twelve public target names exercise the public metric contract. Features,
labels, identifiers and scanner/group assignments are entirely generated here.
No clinical validity or competition performance can be inferred from this demo.
"""
from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
from dataclasses import asdict, dataclass
import hashlib
import html
import io
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import zipfile

import numpy as np
import pandas as pd

from rsna_knee import metrics as public_metrics
from rsna_knee import schema as public_schema
from rsna_knee.schema import LABELS

SCHEMA = "public-synthetic-pipeline-v1"
SCOPE = "SYNTHETIC_ONLY: generated tabular features and labels; not MRI training or clinical evidence."
MAX_CHECKPOINT_BYTES = 2 * 1024**2


class CacheValidationError(ValueError):
    """An existing checkpoint cannot safely be reused."""


@dataclass(frozen=True)
class DemoConfig:
    seed: int = 2026
    folds: int = 5
    scanners: int = 10
    groups_per_scanner: int = 12
    rows_per_group: int = 4
    features: int = 20
    epochs: int = 120
    learning_rate: float = 0.15
    l2: float = 0.002

    def validate(self):
        for name in ("seed", "folds", "scanners", "groups_per_scanner", "rows_per_group", "features", "epochs"):
            value = getattr(self, name)
            if type(value) is not int or value < (0 if name == "seed" else 1):
                raise ValueError(f"Invalid configuration: {name}")
        if self.folds < 2 or self.scanners < self.folds or self.scanners % self.folds:
            raise ValueError("Scanners must divide evenly across at least two folds.")
        if not np.isfinite(self.learning_rate) or not 0 < self.learning_rate <= 1:
            raise ValueError("learning_rate must be finite and in (0, 1].")
        if not np.isfinite(self.l2) or self.l2 < 0:
            raise ValueError("l2 must be finite and nonnegative.")


@dataclass
class SyntheticData:
    ids: np.ndarray
    groups: np.ndarray
    scanners: np.ndarray
    folds: np.ndarray
    features: np.ndarray
    labels: np.ndarray


def _sigmoid(values):
    return 1.0 / (1.0 + np.exp(-np.clip(values, -40.0, 40.0)))


def make_synthetic_data(config: DemoConfig = DemoConfig()) -> SyntheticData:
    """Generate a fixed cohort; fold assignment uses scanner identity, never labels."""
    config.validate()
    rng = np.random.default_rng(config.seed)
    group_count = config.scanners * config.groups_per_scanner
    group = np.repeat(np.arange(group_count), config.rows_per_group)
    scanner = group // config.groups_per_scanner
    scanner_fold = np.empty(config.scanners, dtype=np.int64)
    scanner_fold[rng.permutation(config.scanners)] = np.arange(config.scanners) % config.folds
    features = (rng.normal(size=(len(group), config.features))
                + 0.2 * rng.normal(size=(group_count, config.features))[group]
                + 0.15 * rng.normal(size=(config.scanners, config.features))[scanner])
    weights = rng.normal(size=(config.features, 12)) / np.sqrt(config.features)
    probability = _sigmoid(2.2 * features @ weights + np.linspace(-0.6, 0.6, 12))
    labels = (rng.random(probability.shape) < probability).astype(np.int64)
    return SyntheticData(
        ids=np.asarray([f"synthetic-{i:05d}" for i in range(len(group))]),
        groups=np.asarray([f"synthetic-group-{i:04d}" for i in group]),
        scanners=np.asarray([f"synthetic-scanner-{i:02d}" for i in scanner]),
        folds=scanner_fold[scanner], features=features.astype(np.float64), labels=labels)


def validate_data(data: SyntheticData, config: DemoConfig) -> None:
    n = len(data.ids)
    if n == 0 or any(a.shape != (n,) for a in (data.ids, data.groups, data.scanners, data.folds)):
        raise ValueError("Cohort identifiers and folds must be aligned one-dimensional arrays.")
    if len(set(data.ids.tolist())) != n or any(not str(x).startswith("synthetic-") for x in data.ids):
        raise ValueError("Unique, explicitly synthetic row identifiers are required.")
    if data.features.shape != (n, config.features) or not np.isfinite(data.features).all():
        raise ValueError("Feature shape or finite-value contract failed.")
    if data.labels.shape != (n, 12) or not np.isin(data.labels, [0, 1]).all():
        raise ValueError("Exactly twelve binary targets are required.")
    if data.folds.dtype.kind not in "iu" or set(data.folds.tolist()) != set(range(config.folds)):
        raise ValueError("Every configured fold must contain rows.")
    for identity, values in (("scanner", data.scanners), ("group", data.groups)):
        for value in np.unique(values):
            if len(np.unique(data.folds[values == value])) != 1:
                raise ValueError(f"Leakage: a {identity} spans multiple folds.")
    for fold in range(config.folds):
        validate_split(data, np.flatnonzero(data.folds != fold), np.flatnonzero(data.folds == fold))


def validate_split(data: SyntheticData, train: np.ndarray, heldout: np.ndarray) -> None:
    """Fail before fitting on overlapping rows, groups or scanner identities."""
    joined = np.concatenate([train, heldout])
    if joined.dtype.kind not in "iu" or not np.array_equal(np.sort(joined), np.arange(len(data.ids))):
        raise ValueError("Leakage or missing rows in train/heldout partition.")
    for name, values in (("group", data.groups), ("scanner", data.scanners)):
        if set(values[train]) & set(values[heldout]):
            raise ValueError(f"Leakage: train/heldout {name} overlap.")
    for rows in (train, heldout):
        if not len(rows) or any(len(np.unique(data.labels[rows, j])) != 2 for j in range(12)):
            raise ValueError("Every train and heldout fold needs both classes for all twelve targets.")


def fit_fold(data: SyntheticData, fold: int, config: DemoConfig) -> dict[str, np.ndarray]:
    """Full-batch logistic regression with normalization learned from training rows."""
    train, heldout = np.flatnonzero(data.folds != fold), np.flatnonzero(data.folds == fold)
    validate_split(data, train, heldout)
    mean = data.features[train].mean(axis=0)
    scale = data.features[train].std(axis=0)
    scale = np.where(scale > 1e-12, scale, 1.0)
    x = (data.features[train] - mean) / scale
    y = data.labels[train]
    weights = np.zeros((config.features, 12), dtype=np.float64)
    bias = np.zeros(12, dtype=np.float64)
    for _ in range(config.epochs):
        error = _sigmoid(x @ weights + bias) - y
        weights -= config.learning_rate * (x.T @ error / len(train) + config.l2 * weights)
        bias -= config.learning_rate * error.mean(axis=0)
    probabilities = _sigmoid(((data.features[heldout] - mean) / scale) @ weights + bias)
    return {"ids": data.ids[heldout], "probabilities": probabilities,
            "mean": mean, "scale": scale, "weights": weights, "bias": bias}


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _code_fingerprint() -> str:
    # Include the actual metric/schema implementations, not only a version label.
    sources = {"pipeline": Path(__file__).read_bytes(),
               "metrics": Path(public_metrics.__file__).read_bytes(),
               "schema": Path(public_schema.__file__).read_bytes()}
    return _sha(_canonical({name: _sha(raw) for name, raw in sources.items()}))


def _input_fingerprint(data: SyntheticData) -> str:
    digest = hashlib.sha256()
    for name in ("ids", "groups", "scanners", "folds", "features", "labels"):
        array = np.ascontiguousarray(getattr(data, name))
        if array.dtype.hasobject:
            raise ValueError("Object arrays are not a supported input representation.")
        digest.update(_canonical([name, list(array.shape), array.dtype.str]))
        digest.update(array.tobytes())
    return digest.hexdigest()


def _identity(data, config):
    return {"schema": SCHEMA, "config": asdict(config), "targets": LABELS,
            "input_sha256": _input_fingerprint(data), "code_sha256": _code_fingerprint(),
            "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                        "pandas": pd.__version__, "machine": platform.machine(),
                        "byteorder": sys.byteorder, "numerical": _numerical_runtime()}}


def _numerical_runtime() -> dict:
    """Bind resume to the actual NumPy build, dispatch and numerical environment.

    NumPy's runtime report includes loaded BLAS architecture/thread information
    when its optional introspection support is present, and CPU SIMD dispatch
    regardless. Hash the complete report so paths/hostnames need not be published.
    No additional package is installed or required by this demonstration.
    """
    captured = io.StringIO()
    with redirect_stdout(captured):
        np.show_runtime()
    build = np.show_config(mode="dicts")
    backend_fields = ("name", "found", "version", "openblas configuration")
    backends = {name: {key: value for key, value in details.items() if key in backend_fields}
                for name, details in build.get("Build Dependencies", {}).items()
                if name in ("blas", "lapack")}
    variables = ("OPENBLAS_CORETYPE", "OPENBLAS_NUM_THREADS", "OPENBLAS_DEFAULT_NUM_THREADS",
                 "OPENBLAS_MAIN_FREE", "GOTO_NUM_THREADS", "OMP_NUM_THREADS", "OMP_DYNAMIC",
                 "OMP_PROC_BIND", "OMP_PLACES", "MKL_NUM_THREADS", "MKL_DYNAMIC", "MKL_CBWR",
                 "MKL_ENABLE_INSTRUCTIONS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
                 "NPY_DISABLE_CPU_FEATURES", "NPY_ENABLE_CPU_FEATURES", "NPY_PROMOTION_STATE")
    return {"backends": backends, "cpu_dispatch": build.get("SIMD Extensions", {}),
            "numpy_runtime_sha256": _sha(captured.getvalue().encode()),
            "environment": {name: os.environ.get(name) for name in variables},
            "floating_point_errors": np.geterr(),
            "determinism_scope": "Identical recorded source, inputs, build, numerical environment and runtime report; no cross-platform bitwise guarantee."}


def _atomic_write(path: Path, raw: bytes) -> None:
    if path.is_symlink():
        raise CacheValidationError("Refusing a symlink output.")
    fd, temporary = tempfile.mkstemp(prefix=".atomic-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        if hasattr(os, "O_DIRECTORY"):
            directory = os.open(path.parent, os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def _single_writer(output: Path):
    lock = output / ".pipeline-lock"
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise CacheValidationError("Output is locked. Verify no other run is active before removing .pipeline-lock.") from exc
    try:
        yield
    finally:
        lock.rmdir()


def _read_checked(path: Path, size=None, digest=None) -> bytes:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_CHECKPOINT_BYTES:
        raise CacheValidationError("Checkpoint file missing, oversized, or unsafe.")
    raw = path.read_bytes()
    if (size is not None and len(raw) != size) or (digest is not None and _sha(raw) != digest):
        raise CacheValidationError("Checkpoint checksum mismatch; use a new output directory.")
    return raw


def _load_fold(raw, data, fold, config):
    names = {"ids", "probabilities", "mean", "scale", "weights", "bias"}
    heldout = data.folds == fold
    shapes = {"probabilities": (int(heldout.sum()), 12), "mean": (config.features,),
              "scale": (config.features,), "weights": (config.features, 12), "bias": (12,)}
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            if (len(archive.namelist()) != len(names) or set(archive.namelist()) != {n + ".npy" for n in names}
                    or sum(i.file_size for i in archive.infolist()) > MAX_CHECKPOINT_BYTES):
                raise ValueError("Archive schema")
            # A small ZIP member can contain a huge declared NumPy shape. Check
            # headers and payload sizes before np.load can allocate that shape.
            for name in names:
                info = archive.getinfo(name + ".npy")
                with archive.open(info) as member:
                    version = np.lib.format.read_magic(member)
                    if version not in ((1, 0), (2, 0)):
                        raise ValueError("Unsupported array header version")
                    reader = (np.lib.format.read_array_header_1_0 if version == (1, 0)
                              else np.lib.format.read_array_header_2_0)
                    shape, fortran, dtype = reader(member, max_header_size=10000)
                    expected_shape = (int(heldout.sum()),) if name == "ids" else shapes[name]
                    expected_dtype = data.ids.dtype if name == "ids" else np.dtype(np.float64)
                    if shape != expected_shape or dtype != expected_dtype or dtype.hasobject or fortran:
                        raise ValueError("Array header schema")
                    count = 1
                    for dimension in shape:
                        count *= dimension
                    if member.tell() + count * dtype.itemsize != info.file_size:
                        raise ValueError("Array payload size")
        with np.load(io.BytesIO(raw), allow_pickle=False) as archive:
            values = {name: archive[name] for name in names}
        if not np.array_equal(values["ids"], data.ids[heldout]):
            raise ValueError("Row identity")
        for name, shape in shapes.items():
            if values[name].dtype != np.float64 or values[name].shape != shape or not np.isfinite(values[name]).all():
                raise ValueError("Array schema")
        if not (values["scale"] > 0).all() or not ((values["probabilities"] >= 0) & (values["probabilities"] <= 1)).all():
            raise ValueError("Numeric range")
        return values
    except (ValueError, KeyError, OSError, EOFError, TypeError, zipfile.BadZipFile) as exc:
        raise CacheValidationError("Invalid checkpoint arrays; use a new output directory.") from exc


def _render_report(result) -> str:
    metrics = result["metrics"]
    auc = f'{metrics["macro_auc_12"]:.4f}' if metrics else "Pending"
    bars = "".join(
        f'<tr><th>{html.escape(label)}</th><td><div class="track"><span style="width:{value * 100:.2f}%"></span></div></td><td>{value:.4f}</td></tr>'
        for label, value in (metrics["per_label_auc"].items() if metrics else []))
    folds = "".join(f'<tr><td>{r["fold"] + 1}</td><td>{r["train_rows"]}</td><td>{r["heldout_rows"]}</td><td>{r["heldout_scanners"]}</td><td>0 / 0</td></tr>' for r in result["folds"])
    provenance = html.escape(json.dumps(result["provenance"], indent=2, sort_keys=True))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Synthetic pipeline · Engineering evidence</title><style>
:root{{color-scheme:light;--navy:#142e46;--teal:#087f8c}}*{{box-sizing:border-box}}body{{margin:0;background:#f4f7fa;color:var(--navy);font:16px/1.6 system-ui,sans-serif}}main{{max-width:1060px;margin:auto;padding:44px 24px}}header{{border-top:5px solid var(--teal);padding-top:22px}}h1{{font-size:clamp(2rem,4vw,3.2rem);line-height:1.12;letter-spacing:-.04em;margin:8px 0 18px}}h2{{font-size:1.3rem}}.eyebrow{{text-transform:uppercase;letter-spacing:.13em;font-size:.8rem;font-weight:750;color:var(--teal)}}.note{{max-width:850px;color:#456077}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:28px 0}}.card,section{{background:white;border:1px solid #dce5ed;border-radius:12px;padding:22px}}.card strong{{display:block;font-size:2rem;line-height:1.3}}.card span{{color:#456077}}section{{margin-bottom:20px;overflow:auto}}table{{border-collapse:collapse;width:100%;font-size:.9rem}}th,td{{text-align:left;padding:9px 8px;border-bottom:1px solid #e8eef3}}.track{{background:#e6f3f3;height:12px;border-radius:8px;min-width:100px}}.track span{{display:block;background:var(--teal);height:12px;border-radius:8px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.75rem;color:#35516b}}a{{color:var(--teal)}}@media(max-width:640px){{.cards{{grid-template-columns:1fr}}main{{padding:24px 14px}}.fold-table th,.fold-table td{{font-size:.72rem;padding:7px 4px}}}}
</style></head><body><main><header><div class="eyebrow">Offline · CPU · Synthetic only</div><h1>A pipeline you can inspect.</h1><p class="note">Generated features, actual logistic fits, scanner-separated evaluation and verified checkpoint resume. This is an engineering demonstration, not MRI training, clinical evidence or a competition score.</p></header>
<div class="cards"><div class="card"><strong>{html.escape(result["status"])}</strong><span>{result["completed_folds"]} / {result["total_folds"]} folds committed</span></div><div class="card"><strong>{auc}</strong><span>Synthetic heldout macro AUC · 12 targets</span></div><div class="card"><strong>{result["heldout_rows"]}</strong><span>Heldout rows · each predicted once</span></div></div>
<section><h2>Evaluation evidence</h2><p>Every model learns normalization from its training rows only. No scanner or synthetic patient group appears on both sides of a fold.</p><table class="fold-table"><thead><tr><th>Fold</th><th>Train rows</th><th>Heldout rows</th><th>Heldout scanners</th><th>Group / scanner overlap</th></tr></thead><tbody>{folds}</tbody></table></section>
<section><h2>Twelve-target synthetic ranking</h2><p>AUC uses average ranks for ties and requires both classes for every target. Scores characterize only this generated problem.</p><table><tbody>{bars or '<tr><td>Full-cohort metrics appear after every fold is complete.</td></tr>'}</tbody></table></section>
<section><h2>Resume and provenance</h2><p>This invocation fitted {result["execution"]["fitted_folds"]} folds and reused {result["execution"]["reused_folds"]} verified checkpoints. Input, configuration, source and runtime fingerprints must match; changed or corrupt caches are rejected. SHA-256 detects accidental corruption; this local manifest is not a signed attestation.</p><p><a href="results.json">Machine-readable results</a> · <a href="synthetic_predictions.csv">Synthetic heldout probabilities</a></p><details><summary>Inspect fingerprints</summary><pre>{provenance}</pre></details></section>
</main></body></html>'''


def run_pipeline(output, config: DemoConfig = DemoConfig(), *, data=None, stop_after_fold=None) -> dict:
    """Fit or resume complete folds. A deliberate stop returns PAUSED, not failure.

    `stop_after_fold` is the total number of committed folds (1-based count).
    Determinism is scoped to the recorded code and numerical runtime. One writer
    owns an output directory; after an unclean process kill, inspect/remove the
    stale lock before resuming. No checkpoint is silently repaired or discarded.
    """
    config.validate()
    if stop_after_fold is not None and (type(stop_after_fold) is not int or not 0 <= stop_after_fold <= config.folds):
        raise ValueError("stop_after_fold must be between zero and the configured fold count.")
    data = make_synthetic_data(config) if data is None else data
    validate_data(data, config)
    identity = _identity(data, config)
    output = Path(output)
    if output.is_symlink():
        raise CacheValidationError("Output directory must not be a symlink.")
    output.mkdir(parents=True, exist_ok=True)
    with _single_writer(output):
        cache = output / "checkpoints"
        if cache.is_symlink():
            raise CacheValidationError("Checkpoint directory must not be a symlink.")
        cache.mkdir(exist_ok=True)
        manifest_path = output / "checkpoint_manifest.json"
        if manifest_path.exists() or manifest_path.is_symlink():
            try:
                manifest = json.loads(_read_checked(manifest_path))
            except (ValueError, OSError) as exc:
                raise CacheValidationError("Invalid checkpoint manifest; use a new output directory.") from exc
            if (not isinstance(manifest, dict) or manifest.get("identity") != identity
                    or manifest.get("fingerprint") != _sha(_canonical(identity))):
                raise CacheValidationError("Input/config/code/runtime fingerprint changed; use a new output directory.")
            records = manifest.get("folds")
            if not isinstance(records, list) or len(records) > config.folds:
                raise CacheValidationError("Invalid checkpoint fold list.")
        else:
            if any((output / name).exists() for name in ("results.json", "report.html", "synthetic_predictions.csv")):
                raise CacheValidationError("Existing outputs have no provenance manifest; use a new output directory.")
            manifest = {"identity": identity, "fingerprint": _sha(_canonical(identity)), "folds": []}
            records = manifest["folds"]
            _atomic_write(manifest_path, _canonical(manifest))
        probabilities = np.full((len(data.ids), 12), np.nan)
        for fold, record in enumerate(records):
            if (not isinstance(record, dict) or set(record) != {"fold", "file", "bytes", "sha256"}
                    or record["fold"] != fold or record["file"] != f"fold-{fold:02d}.npz"):
                raise CacheValidationError("Checkpoint fold identity or path changed.")
            values = _load_fold(_read_checked(cache / record["file"], record["bytes"], record["sha256"]), data, fold, config)
            probabilities[data.folds == fold] = values["probabilities"]
        reused = len(records)
        stop = config.folds if stop_after_fold is None else stop_after_fold
        for fold in range(len(records), stop):
            values = fit_fold(data, fold, config)
            buffer = io.BytesIO()
            np.savez_compressed(buffer, **values)
            raw = buffer.getvalue()
            _load_fold(raw, data, fold, config)
            name = f"fold-{fold:02d}.npz"
            _atomic_write(cache / name, raw)
            # Commit data first, then the manifest: an interruption never points
            # at a partially written fold. Unreferenced files are not trusted.
            records.append({"fold": fold, "file": name, "bytes": len(raw), "sha256": _sha(raw)})
            _atomic_write(manifest_path, _canonical(manifest))
            probabilities[data.folds == fold] = values["probabilities"]
        completed = len(records)
        done = completed == config.folds
        mask = data.folds < completed
        metrics = None
        if done:
            metrics = public_metrics.macro_auc_12(
                pd.DataFrame(data.labels, columns=LABELS, index=data.ids),
                pd.DataFrame(probabilities, columns=LABELS, index=data.ids))
        frame = pd.DataFrame(probabilities[mask], columns=LABELS)
        frame.insert(0, "fold", data.folds[mask])
        frame.insert(0, "synthetic_id", data.ids[mask])
        csv_raw = frame.to_csv(index=False, float_format="%.17g", lineterminator="\n").encode()
        _atomic_write(output / "synthetic_predictions.csv", csv_raw)
        result = {"schema": SCHEMA, "evidence_type": "SYNTHETIC_ONLY", "scope": SCOPE,
                  "status": "COMPLETE" if done else "PAUSED", "completed_folds": completed,
                  "total_folds": config.folds, "rows": len(data.ids), "heldout_rows": int(mask.sum()),
                  "targets": LABELS, "metrics": metrics, "provenance": identity,
                  "predictions_sha256": _sha(csv_raw),
                  "validation": {"group_overlap": 0, "scanner_overlap": 0,
                                 "train_only_normalization": True, "every_row_heldout_once": done,
                                 "committed_checkpoint_checksums_verified": True},
                  "execution": {"reused_folds": reused, "fitted_folds": completed - reused},
                  "folds": [{"fold": fold, "train_rows": int((data.folds != fold).sum()),
                             "heldout_rows": int((data.folds == fold).sum()),
                             "heldout_scanners": len(np.unique(data.scanners[data.folds == fold]))}
                            for fold in range(completed)]}
        _atomic_write(output / "results.json", json.dumps(result, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n")
        _atomic_write(output / "report.html", _render_report(result).encode())
        return result
