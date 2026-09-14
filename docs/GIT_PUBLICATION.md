# Manual publication gate — not part of M01

Do not run Git initialization, pulls, resets, pushes or merges during this milestone. The package installer preserves existing files and refuses differing code; it is not a Git synchronization tool. The live repository has not been re-inspected. Existing uncommitted work must remain intact.

After M01 evidence is reviewed, inspect the intended repository in a terminal yourself:

```bash
cd "$HOME/rsna-knee-abnormality-detection"
git status --short --branch
git remote -v
git diff --stat
git diff -- . ':!notebooks/*'
```

If Git reports this is not a repository, stop: do not invent its origin/history or delete the folder. We will prepare the appropriate non-destructive initialization or integration instructions from that result. Do not paste remote URLs containing embedded credentials.

Before a future commit: rerun the tests, review notebook outputs for prohibited material, inspect `git check-ignore` on private directories, then stage only explicitly reviewed public source/configuration/documentation/notebook paths. Never use `git add .` as a substitute for a review. Verify `git diff --cached --stat` and `git diff --cached` before committing. No push commands are included here because the current branch and remote state have not been verified.
