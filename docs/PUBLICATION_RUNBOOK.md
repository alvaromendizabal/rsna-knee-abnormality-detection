# Public showcase, private research — manual Git workflow

## The boundary

Keep `$HOME/rsna-knee-abnormality-detection` as the private working directory in AWS. Keep its data, environments, checkpoints, original notebooks, and uncommitted work intact. The public repository must NOT be a byte-for-byte mirror of it.

Recommended long-term layout:

- Existing public repository: `alvaromendizabal/rsna-knee-abnormality-detection`, presentation/evidence only.
- Separate optional private repository: `alvaromendizabal/rsna-knee-abnormality-detection-research`, private source and research history. Create it as an independent **Private** repository, not a fork of a public repository.
- Private raw data, image caches, credentials, fitted models and row-level predictions remain outside Git, even in a private repository.

Public content remains copyable. GitHub's terms permit viewing and forking public repositories. Changing visibility or deleting files does not retract copies or already-granted rights. The bundled notice is not a legal guarantee. Do not replace an existing license or rewrite history blindly.

## 1. Inventory the existing AWS working tree

In the existing activated project terminal:

```bash
cd "$HOME/rsna-knee-abnormality-detection"
source .venv/bin/activate
python scripts/inventory_publication.py
```

This reads local Git metadata only. It does not contact GitHub or change files other than its local inventory receipt. Preserve `artifacts/publication_inventory.json`. When the local history scan is incomplete, or the remote has old source/notebooks, publication cleaning is a separate decision gate. Local Git state cannot prove current remote visibility/history.

## 2. Prepare the public presentation after Round 1 passes

```bash
python scripts/prepare_portfolio.py
python scripts/check_portfolio.py "$HOME/rsna-knee-abnormality-detection-portfolio-export"
```

The export refuses to overwrite an existing export directory. Read all seven files. The status page is conservative: tests/M01/Round 1 can be verified, but no image-model score is invented. No raw research notebook or source module is included.

## 3. Obtain a separate public clone yourself

Open the public repository in your browser and inspect **Code**, **Branches**, **Settings**, and any license. Do not place a private research branch in this public repository.

In Terminal, first check whether the destination already exists:

```bash
test ! -e "$HOME/rsna-knee-abnormality-detection-public" || { echo "STOP: public clone already exists; inspect it, do not overwrite."; exit 1; }
git clone https://github.com/alvaromendizabal/rsna-knee-abnormality-detection.git "$HOME/rsna-knee-abnormality-detection-public"
```

Git authentication is your own normal GitHub authentication; never paste a token into chat or place it inside the remote URL. The copied-link-only rule applies to Kaggle; it does not require changing existing GitHub authentication.

Inspect the clone:

```bash
git -C "$HOME/rsna-knee-abnormality-detection-public" status --short
python "$HOME/rsna-knee-abnormality-detection/scripts/inventory_publication.py" --directory "$HOME/rsna-knee-abnormality-detection-public"
```

**STOP** when `history_review_required` or `license_review_required` is true, the scan is incomplete, or the working tree is dirty. Do not run `git reset --hard`, `git clean`, `git push --force`, `git push --mirror`, history-filter commands, or bulk deletion. The correct cleanup depends on what is already published. A presentation-only new commit does not conceal old research commits. Return the inventory before any destructive cleanup.

## 4. Only for an empty repository or a reviewed presentation-only history

Copy ONLY the approved seven files into the separate clone. This deliberately never stages the AWS working tree:

```bash
cd "$HOME/rsna-knee-abnormality-detection-public"
cp "$HOME/rsna-knee-abnormality-detection-portfolio-export/README.md" README.md
cp "$HOME/rsna-knee-abnormality-detection-portfolio-export/RESEARCH_OVERVIEW.md" RESEARCH_OVERVIEW.md
cp "$HOME/rsna-knee-abnormality-detection-portfolio-export/RESULTS.md" RESULTS.md
cp "$HOME/rsna-knee-abnormality-detection-portfolio-export/NOTICE.md" NOTICE.md
cp "$HOME/rsna-knee-abnormality-detection-portfolio-export/SECURITY.md" SECURITY.md
cp "$HOME/rsna-knee-abnormality-detection-portfolio-export/.gitignore" .gitignore
mkdir -p reports
cp "$HOME/rsna-knee-abnormality-detection-portfolio-export/reports/status.json" reports/status.json
python "$HOME/rsna-knee-abnormality-detection/scripts/check_portfolio.py" "$PWD"
git status --short
git diff --check
git diff
```

Do not proceed until the diffs are exactly the presentation update you intend. These copy commands are for the clean, separately cloned public directory only; Git retains the prior tracked presentation versions.

### Existing `main` branch: commit, push, and merge a PR

```bash
git switch -c portfolio/m01-r01-evidence
git add README.md RESEARCH_OVERVIEW.md RESULTS.md NOTICE.md SECURITY.md .gitignore reports/status.json
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m "Publish reviewed research overview and verified pipeline evidence"
git push -u origin portfolio/m01-r01-evidence
```

On GitHub: **Compare & pull request** → base **main** → review **Files changed** → **Create pull request** → merge only after your review and any configured checks succeed. Do not claim CI passed when no workflow exists or has run. Then:

```bash
git switch main
git pull --ff-only origin main
git status --short
git rev-parse HEAD
git log -1 --oneline
```

The public clone is now synchronized with public `main` only after these commands succeed. The AWS research directory is intentionally not mirrored into it.

### Truly empty remote: bootstrap once, then use PRs for later updates

An empty repository has no existing `main` to merge a first PR into. In the clean public clone after the same content review:

```bash
git symbolic-ref HEAD refs/heads/main
git add README.md RESEARCH_OVERVIEW.md RESULTS.md NOTICE.md SECURITY.md .gitignore reports/status.json
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m "Initialize public research portfolio with verified pipeline evidence"
git push -u origin main
```

If `main` already exists or either command reports an unexpected state, stop rather than deleting or force-switching branches. The initial push is a bootstrap, not a merged PR. Future changes use feature branches and review.

## Private research versioning

Do not run `git add .` or push the existing research tree to its old public remote. A private source repository is useful, but it requires a verified private destination and review of tracked/untracked material first. Create the independent private repository in your browser, record its visibility, and preserve the local inventory. The follow-on private-source migration should use an explicit source allowlist, not a raw workspace copy, and must retain existing local history and uncommitted work. This package does not automate that migration or claim that all research is already committed.

## Return evidence

Return `artifacts/publication_inventory.json`. After a successful manual public push/merge, also supply the public commit SHA or PR link, the final short status, and whether configured CI actually ran. Never send `.git`, Git bundles, credential files, signed URLs, or private image/report data.

## Primary references

- GitHub licensing: https://docs.github.com/articles/licensing-a-repository
- GitHub sensitive-data/history limitations: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
- GitHub forks: https://docs.github.com/en/pull-requests/reference/forks

These are platform guidance, not personalized legal advice. Competition-specific prize, code-sharing, and publication obligations must be reviewed separately before making ownership/publication decisions.

## Optional first private source snapshot — a separate, bounded action

This is distinct from publishing the seven-file showcase. It does not transfer old Git history. Preserve the original working tree and its history without rewriting them.

After the tests pass, run:

```bash
cd "$HOME/rsna-knee-abnormality-detection"
source .venv/bin/activate
python scripts/export_private_source.py
```

This creates `$HOME/rsna-knee-abnormality-detection-private-export`: allowlisted source/configuration/documentation and notebooks with outputs cleared. It excludes raw data, credentials, images, environment, logs, checkpoints and `.git`. A basic secret scan is not a security guarantee; read code cells, markdown and configs before committing. The existing executed notebooks stay unchanged in AWS. Preserve private runtime evidence separately under your existing permitted private storage plan; it is not pushed by this workflow.

In GitHub in your browser, create the independent repository **`alvaromendizabal/rsna-knee-abnormality-detection-research`**, select **Private**, and initialize with a README. Do not create a public fork or change the existing public repository's visibility. Do not replace or reuse a pre-existing research repository without inspecting it. Confirm the **Private** badge before cloning and again before pushing.

For that newly created private repository only:

```bash
test ! -e "$HOME/rsna-knee-abnormality-detection-research" || { echo "STOP: destination exists; inspect it."; exit 1; }
git clone https://github.com/alvaromendizabal/rsna-knee-abnormality-detection-research.git "$HOME/rsna-knee-abnormality-detection-research"
cd "$HOME/rsna-knee-abnormality-detection-research"
git status --short
git switch -c research/m01-r01-source
cp -a "$HOME/rsna-knee-abnormality-detection-private-export/." .
git status --short
git diff --check
git add src scripts tests configs docs notebooks portfolio requirements-audit.txt requirements-research.txt pytest.ini README.md NEXT_STEPS.md ARTIFACT_MANIFEST.json RESEARCH_ARTIFACT_MANIFEST.json RESEARCH_STATIC_REVIEW.json PRIVATE_SNAPSHOT.json .gitignore
git diff --cached --name-only
git diff --cached --stat
git diff --cached --check
git diff --cached
```

Pause and review the staged contents and destination's **Private** badge. There must be no data, runtime artifacts, tokens, executed notebook outputs, or restricted third-party code. The prior manifests describe their original prepared artifacts; notebook-output stripping does not manufacture new execution receipts.

Then, only after that review:

```bash
git commit -m "Preserve private research source and reproducible feature investigations"
git push -u origin research/m01-r01-source
```

Create and review a pull request **within the private repository**, base `main`, and merge after your review and any configured checks pass. Then:

```bash
git switch main
git pull --ff-only origin main
git status --short
git rev-parse HEAD
```

Record the commit and PR yourself. This is a reviewed snapshot of source, not a live bidirectional sync and not proof of CI execution. Later snapshots need a new review against private `main`; never copy `.git` from the AWS working tree, never use `push --mirror`, and never upload private source to the public showcase branch.
