# Current operating addendum

The user executes all project code, tests, notebooks, downloads and Git/cloud operations. Assistant file creation and static inspection do not constitute runtime testing.

## Kaggle access

Use the official browser authorization flow: `kaggle auth login --no-launch-browser`.
The user opens the displayed URL in their own browser, authorizes Kaggle, and pastes the returned value into the waiting terminal prompt. Never request a password in the terminal, manual API-token creation, a kaggle.json download, a copied/signed data URL, or browser cookies. Do not automate the user's approval. Never print access tokens.

The five-CSV downloader and the gated image-series downloader reuse saved authorization. They never prompt for a password or download link. Kaggle can still require a browser account sign-in, rule acceptance or other account verification; this flow does not bypass those requirements. A connected AWS session is not a Kaggle authorization grant.

Two feature investigations remain prepared together, with separate execution gates. Finish the metadata audit and first-round return package before image retrieval. Source ownership remains private by default; the public repository is a reviewed portfolio presentation, not a full research-tree mirror. No Git action is part of the access correction.
