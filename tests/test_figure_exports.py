import importlib.util
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("figure_exports", ROOT / "tools/check_figure_exports.py")
exports = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exports)


def test_relocated_archive_preserves_all_original_evidence():
    result = exports.check_exports()
    assert result["original_figure_specs"] == 36
    assert result["relocated_html_files"] == 36
    assert result["duplicate_runtime_bytes_removed"] == 9527986


@pytest.mark.parametrize("kind", ["html", "runtime", "manifest"])
def test_archive_tampering_is_rejected(tmp_path, kind):
    figures = tmp_path / "reports/figures"
    shutil.copytree(ROOT / "reports/figures", figures)
    target = {"html": next(figures.glob("0*/*/figure_01.html")),
              "runtime": figures / "_vendor/plotly-3.1.0.min.js",
              "manifest": next(figures.glob("0*/*/EXPORT_MANIFEST.json"))}[kind]
    target.write_bytes(target.read_bytes() + b" ")
    with pytest.raises(ValueError, match="changed"):
        exports.check_exports(tmp_path)
