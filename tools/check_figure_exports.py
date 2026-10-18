#!/usr/bin/env python3
"""Verify offline figure relocation against the untouched original export hashes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_exports(root=ROOT):
    root = Path(root).resolve()

    def checked(path):
        result = root / path
        require(not result.is_symlink() and result.resolve().is_relative_to(root), "Unsafe figure path")
        require(result.is_file(), "Missing figure asset: " + str(path))
        return result

    def digest(raw):
        return hashlib.sha256(raw).hexdigest()

    layout = json.loads(checked("reports/figures/ASSET_LAYOUT.json").read_text())
    require(layout["schema"] == "rsna-figure-layout-v1" and layout["research_reexecuted"] is False,
            "Invalid publication layout scope")
    shared = layout["shared_asset"]
    shared_path = checked(shared["path"])
    raw = shared_path.read_bytes()
    require(len(raw) == shared["bytes"] and digest(raw) == shared["sha256"], "Shared runtime changed")
    discovered = {p.relative_to(root).as_posix() for p in (root / "reports/figures").glob("0*/*/EXPORT_MANIFEST.json")}
    require(discovered == {entry["manifest"] for entry in layout["exports"]}, "Incomplete export coverage")
    figures = html_files = 0
    for entry in layout["exports"]:
        manifest_path = checked(entry["manifest"])
        require(digest(manifest_path.read_bytes()) == entry["manifest_sha256"], "Original manifest changed")
        original = json.loads(manifest_path.read_text())
        require(original["files"]["plotly.min.js"] == shared["sha256"], "Runtime differs from original export")
        require(not (manifest_path.parent / "plotly.min.js").exists(), "Redundant runtime copy reintroduced")
        require((manifest_path.parent / entry["relocated_runtime"]).resolve() == shared_path, "Incorrect offline runtime path")
        changed = set()
        for name, expected in original["files"].items():
            if name == "plotly.min.js":
                continue
            require(Path(name).name == name, "Invalid original file path")
            path = checked((manifest_path.parent / name).relative_to(root))
            raw = path.read_bytes()
            if name in entry["html_files"]:
                new = ('src="' + entry["relocated_runtime"] + '"').encode()
                require(raw.count(new) == 1 and digest(raw) == entry["html_files"][name], "Relocated HTML changed")
                # Reversing the one allowed path edit must recover the original bytes.
                raw = raw.replace(new, b'src="plotly.min.js"')
                changed.add(name)
                html_files += 1
            require(digest(raw) == expected, "Figure differs from original export: " + name)
            figures += name.endswith(".json")
        require(changed == set(entry["html_files"]), "Unknown HTML layout entry")
    return {"status": "PASS", "original_manifests": len(discovered), "original_figure_specs": figures,
            "relocated_html_files": html_files, "duplicate_runtime_bytes_removed": 2 * shared["bytes"]}


if __name__ == "__main__":
    print(json.dumps(check_exports(), indent=2))
