"""Browser-authorized Kaggle access. Importing this module does not contact Kaggle.

The user runs ``kaggle auth login --no-launch-browser`` in a terminal first.
No password, API-key creation, token printing, or copied download link is requested.
"""
from __future__ import annotations
from pathlib import Path
from .links import validate_url

COMPETITION = "rsna-knee-abnormality-detection"
METADATA_FILES = ("train.csv", "train_series.csv", "test.csv", "test_series.csv", "sample_submission.csv")

def metadata_command(cli: Path, name: str, destination: Path) -> list[str]:
    """Every permitted metadata request names exactly one allowlisted file."""
    if name not in METADATA_FILES:
        raise ValueError("Only the five metadata CSV filenames are permitted.")
    return [str(cli), "competitions", "download", COMPETITION,
            "-f", name, "-p", str(destination), "-q"]

def archive_location(*, api=None, request_factory=None) -> str:
    """Resolve an authorized archive location; DO NOT download its body.

    This uses the same request model and endpoint as Kaggle's official client.
    The caller must use the bounded byte-range reader, never a full-body GET.
    Injection arguments permit offline synthetic tests with no Kaggle import.
    The returned temporary URL is secret: never log, print, persist or publish it.
    """
    if api is None:
        from kaggle import api as authenticated_api
        api = authenticated_api
    if request_factory is None:
        from kaggle.api.kaggle_api_extended import ApiDownloadDataFilesRequest
        request_factory = ApiDownloadDataFilesRequest
    request = request_factory()
    request.competition_name = COMPETITION
    with api.build_kaggle_client() as client:
        response = client.competitions.competition_api_client.download_data_files(request)
    url = getattr(response, "url", None)
    if not isinstance(url, str) or not url:
        raise RuntimeError("Kaggle did not return a usable archive location; no image body downloaded.")
    return validate_url(url)
