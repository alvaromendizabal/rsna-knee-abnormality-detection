# Offline figure archive

The three original figure exports contain 36 Plotly specifications and their HTML
views. Each `EXPORT_MANIFEST.json` retains its original bytes and original hashes.
The matching notebooks and scientific chart values are unchanged.

`_vendor/plotly-3.1.0.min.js` serves the three exports locally. Consolidating their
identical copies removes **9,527,986 bytes** from the working tree. The later
`saved_results` runtime is a different version and is retained separately.

`ASSET_LAYOUT.json` records the publication layout change. The verifier checks
every original figure, the shared runtime, and every adjusted HTML view. Reversing
only the script-path substitution must recover the original HTML hash; the
original export manifest is never rewritten to conceal a content change.

```bash
python tools/check_figure_exports.py
```

Open a figure from the full checkout, or serve the checkout with
`python -m http.server 8000`. Keep the containing `reports/figures` directory when
copying an export so its shared runtime remains available. No CDN is required.
