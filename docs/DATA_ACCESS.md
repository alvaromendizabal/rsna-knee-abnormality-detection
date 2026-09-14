# Kaggle browser authorization and bounded data access

## One-time interactive action in the AWS terminal

```bash
cd "$HOME/rsna-knee-abnormality-detection"
source .venv/bin/activate
kaggle auth login --no-launch-browser
```

Open the URL printed by that command in the browser on your own computer. Complete the approval and paste the browser-provided value into the terminal prompt. Do not send it to ChatGPT, save it in a notebook, run `print-access-token`, or record the authentication screen. If the CLI reports an existing login for the correct account, continue without forcing another login.

No terminal password, manual API token, kaggle.json download, or copied dataset URL is needed. Browser sign-in and any competition-rule acceptance remain under the user's control. An expired browser session may still require authentication on Kaggle's website; a script cannot guarantee the provider will never request it.

The supplied base environment already pins `kaggle==2.2.4`. Do not rebuild the environment. Only if the activated environment lacks the command or rejects the auth subcommand, use:

```bash
python -m pip install --disable-pip-version-check --timeout 20 --retries 0 "kaggle==2.2.4"
kaggle auth login --no-launch-browser
```

If earlier environment-token instructions were followed and a subsequent download uses the wrong credential, remove only those variables from the current terminal with `unset KAGGLE_API_TOKEN KAGGLE_USERNAME KAGGLE_KEY`, then retry login. Do not delete credential files or display their contents. If a conflict remains, stop with the non-secret error text.

## Five metadata CSVs

After installing this update and passing tests:

```bash
python scripts/download_metadata.py
```

The code invokes the official CLI with `-f` for each of train.csv, train_series.csv, test.csv, test_series.csv and sample_submission.csv. It reuses existing header-valid, locally checksum-matching inputs. No full-archive fallback exists. Missing files are fetched into unique staging directories, bounded by 120 seconds per file, 600 seconds total, approximately 101 MiB polled staging bytes per file and 250 MiB installed CSVs. These are polling guards, not exact network-byte billing caps. Downloads may exceed a polling byte threshold briefly before termination.

Standard input is disabled inside the downloader, so authentication cannot turn into a hidden notebook prompt. Private CLI logs have owner-only permissions and are excluded from the return package. Receipts contain filenames, local hashes and status, never authorization values. Upstream checksums are not claimed to be independently verified. Full schema/value/join validation is performed by notebook 01, not by a header check alone.

`METADATA_READY` is the completion marker. `--check-local` validates the five files without network access. A permission error requires checking competition access in the browser; do not issue a full-data command or create alternate tokens.

## Later: one complete image series, using the same saved login

After the first-round evidence review, `python scripts/download_image_sample.py` uses the official Kaggle client to resolve an authorized archive location internally. It does NOT call the client's full-body download helper. The existing bounded range reader fetches the ZIP directory and only the selected study/series DICOM entries. You do not supply any download URL.

The body reader insists on HTTP 206, validates ranges and archive members, and refuses a server returning the full body instead. It retains the prior 512 MiB received-body cap, 600-request cap, 300-second inner guard, 8-96 slices, 16 MiB per-slice and 256 MiB uncompressed selected-series limits. A 330-second outer supervisor also bounds the authorization-location request. Unsupported archive layout or range support causes a stop, not a fallback. The location-response schema has been statically checked against official client source, not verified against this account at runtime.

## Primary sources

- https://github.com/Kaggle/kaggle-cli/blob/main/skills/references/auth.md
- https://github.com/Kaggle/kaggle-cli/blob/main/docs/competitions.md
- https://github.com/Kaggle/kaggle-cli/blob/main/src/kaggle/api/kaggle_api_extended.py (competition_download_files request construction only; body download is intentionally not called)
- https://pypi.org/project/kaggle/2.2.4/
