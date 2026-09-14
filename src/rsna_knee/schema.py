"""Fail-closed metadata contract. Unknown clinical labels are never made negative."""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
import pandas as pd
STUDY = "StudyInstanceUID"
SERIES = "SeriesInstanceUID"
LABELS = ["ACL", "MCL", "Medial Meniscus", "Lateral Meniscus", "Medial OA", "Lateral OA",
          "PF OA", "Effusion", "Synovitis", "Baker's", "Contusion", "Fracture"]
PLANES = ["Sagittal", "Coronal", "Axial"]
SERIES_COLUMNS = [STUDY, SERIES, "Fluid_Sensitive", "Fat_Suppression", "Anatomical_Plane"]
FILE_COLUMNS = {"train.csv": [STUDY, "Report", *LABELS], "train_series.csv": SERIES_COLUMNS,
                "test.csv": [STUDY], "test_series.csv": SERIES_COLUMNS,
                "sample_submission.csv": [STUDY, *LABELS]}
FILES = tuple(FILE_COLUMNS)
MAX_FILE_BYTES = 100 * 1024**2
MAX_ROWS = 200_000

class ContractError(ValueError):
    """Stop on a contract violation; do not silently repair restricted inputs."""

def check_header(path: Path, filename: str) -> None:
    if filename not in FILE_COLUMNS:
        raise ContractError("Only the five allowlisted metadata CSVs are supported.")
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"Missing file or refused symlink: {filename}")
    if not 0 < path.stat().st_size <= MAX_FILE_BYTES:
        raise ContractError(f"Empty file or 100 MiB cap exceeded: {filename}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        try:
            header = next(csv.reader(handle))
        except (StopIteration, UnicodeError, csv.Error) as exc:
            raise ContractError(f"Cannot parse CSV header: {filename}") from exc
    if len(header) != len(set(header)) or set(header) != set(FILE_COLUMNS[filename]):
        raise ContractError(f"Columns differ from the documented schema: {filename}")
    if filename == "sample_submission.csv" and header != FILE_COLUMNS[filename]:
        raise ContractError("Submission column order differs; review the current contract.")

def numeric_binary(values: pd.Series, name: str, allow_unknown: bool) -> pd.Series:
    text = values.astype("string").str.strip()
    blank = text.isna() | text.eq("")
    result = pd.to_numeric(text.mask(blank), errors="coerce").astype(float)
    invalid = (~blank & result.isna()) | (result.notna() & ~result.isin([0., 1.]))
    if bool(invalid.any()):
        raise ContractError(f"Invalid binary values in {name}; count={int(invalid.sum())}.")
    if not allow_unknown and bool(result.isna().any()):
        raise ContractError(f"Missing required values in {name}.")
    return result

def _unique(frame: pd.DataFrame, column: str, name: str) -> None:
    text = frame[column].astype("string")
    if text.isna().any() or text.str.strip().eq("").any() or text.ne(text.str.strip()).any():
        raise ContractError(f"Missing/whitespace identifier {column} in {name}.")
    if text.duplicated().any():
        raise ContractError(f"Duplicate {column} in {name}; count={int(text.duplicated().sum())}.")

def validate_tables(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    if set(tables) != set(FILES):
        raise ContractError("Exactly five metadata tables are required.")
    out = {name: frame.copy(deep=True) for name, frame in tables.items()}
    for name, frame in out.items():
        if frame.empty or len(frame) > MAX_ROWS:
            raise ContractError(f"Empty table or row cap exceeded: {name}")
        if len(frame.columns) != len(set(frame.columns)) or set(frame.columns) != set(FILE_COLUMNS[name]):
            raise ContractError(f"Column contract differs: {name}")
    train, test, sample = out["train.csv"], out["test.csv"], out["sample_submission.csv"]
    for name in ("train.csv", "test.csv", "sample_submission.csv"):
        _unique(out[name], STUDY, name)
    if set(test[STUDY]) != set(sample[STUDY]):
        raise ContractError("Example-test and sample-submission study ID sets differ.")
    if list(sample.columns) != [STUDY, *LABELS]:
        raise ContractError("Submission column order differs from the documented contract.")
    for label in LABELS:
        train[label] = numeric_binary(train[label], label, True)
        prediction = pd.to_numeric(sample[label], errors="coerce")
        if not np.isfinite(prediction.to_numpy(float)).all() or not prediction.between(0, 1).all():
            raise ContractError(f"Invalid template probabilities in {label}.")
        sample[label] = prediction
    for split in ("train", "test"):
        frame = out[f"{split}_series.csv"]
        _unique(frame, SERIES, f"{split}_series.csv")
        ids = frame[STUDY].astype("string")
        if ids.isna().any() or ids.str.strip().eq("").any() or ids.ne(ids.str.strip()).any():
            raise ContractError(f"Invalid foreign keys in {split}_series.csv.")
        studies = set(out[f"{split}.csv"][STUDY])
        if set(ids) - studies or studies - set(ids):
            raise ContractError(f"Orphan series or studies without series in {split}.")
        for flag in ("Fluid_Sensitive", "Fat_Suppression"):
            frame[flag] = numeric_binary(frame[flag], flag, False).astype(int)
        if not frame["Anatomical_Plane"].isin(PLANES).all():
            raise ContractError(f"Missing/unrecognized anatomical plane in {split}_series.csv.")
    return out

def load_tables(directory: Path) -> dict[str, pd.DataFrame]:
    tables = {}
    for name in FILES:
        check_header(directory / name, name)
        # Real CSV parser: embedded newlines in reports are not additional studies.
        tables[name] = pd.read_csv(directory / name, dtype=str, keep_default_na=False,
            na_filter=False, encoding="utf-8-sig", nrows=MAX_ROWS + 1)
    return validate_tables(tables)
