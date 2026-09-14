# RSNA Knee — local multilingual-teacher pilot

This is one bounded supervision experiment, not another image-feature expansion and not a clinical-accuracy benchmark. The prior completed experiment has 330 binary candidates among 3,072 finding/report pairs (10.7422%). A multilingual model is a candidate source of training supervision, not ground truth.

## Experimental question

With model, quantization, decoder and original-language report held fixed, does adding anatomy-specific target definitions change usable candidate assertions, abstentions and disagreements? Two arms (`minimal_contract`, `domain_contract`) are run on the **same four training reports**. Cached English lexical results are shown on the intersection of successfully processed reports only. Neither greater coverage nor more negatives constitutes better accuracy.

Two fabricated operational checks (English and Spanish) run first with the domain contract. They must match their twelve predeclared states and pass exact-quote checks before competition reports are processed. A failed check or invalid real output stops additional real-report calls. No hidden retry or automatic label correction is performed. A blocked outcome is an explicit result that can still be plotted and packaged.

## Fixed model and resource envelope

- Qwen/Qwen3-4B-Instruct-2507, third-party Unsloth Q4_K_M GGUF, exact revision and SHA-256 in `MODEL_PROVENANCE.json`.
- Weight download: 2,497,281,120 bytes (2.50 decimal GB; about 2.33 GiB), performed only by the user's `prepare` command.
- Official llama.cpp Ubuntu x64 CPU runtime b10937. This pinned release is marked prerelease. No source compilation, pip installs, CUDA, account token, model API subscription, or new Python environment.
- The GitHub release API must supply the CPU asset SHA-256. Verify it, safely extract, and execute `--help` **before** downloading weights. An incompatible glibc/loader or changed asset is a stop, not an instruction to improvise installs.
- CPU only: 4 threads, 8,192-token context, at most 1,024 output tokens/call, 150 seconds/call, 900-second outer inference-worker guard, 10 GiB summed process-RSS guard. At most 2 canary calls + 8 report-arm calls.
- Preparation: at most 850 seconds including tests, runtime and public model transfer. No real-report inference during preparation. Minimum 6 GiB free before the first setup. A complete existing model is SHA-verified and reused.

These are hard guards, not measured time-to-completion estimates. The user's active CPU and persistent disk are still billable. No new GPU or storage allocation is requested. Actual runtime compatibility, download speed and inference throughput remain untested until the user executes this milestone.

## Privacy, data boundaries and limitations

Inference is local to `127.0.0.1` in the AWS space. The local server uses an automatically generated ephemeral authentication secret; the user is never asked for a password or API key. Tools/agents, Web UI, slots endpoint and runtime model downloads are disabled. Its inherited environment excludes account credentials and proxies; the loopback HTTP client bypasses proxies. Server logs are discarded. The server is terminated on normal exit, failures, supervisor timeout or parent death.

Only public artifacts are fetched externally. Reports, model quotes, IDs, selection and raw responses remain in `.private` files, and are excluded from the return ZIP. File hashes and aggregate counts are not proof that all privacy risks are eliminated: review the return before sharing.

Prior splits, sampled reports and candidate states are reused by checksum. All 58 expert-labeled studies plus four normalized-report overlaps stay reserved. Gold outcome values are not analyzed; their presence is checked to reject leakage. Normalized report groups do not establish patient/site disjointness. The four-report, script-aware sample is purposive and very small, not representative. Reports exceeding 3,000 characters are excluded without truncation; no long-report generalization is claimed.

The validator verifies twelve keys, states and verbatim evidence substrings. **A substring match is not semantic entailment.** A model can confidently misinterpret a real report while satisfying every software test. Both prompt arms may be wrong together. Domain definitions are conservative research hypotheses, not adjudicated RSNA target definitions. General multilingual capability is not clinical validation. Third-party quantization and unknown model pretraining provenance introduce additional uncertainty. Benchmark contamination cannot be ruled out.

The model license does not establish competition permission. Check current external-model/weight rules before any eventual competition submission. This package creates no submission, does not approve a label source, does not calculate image ROC AUC, and does not select a model winner based on coverage.

## User execution

1. Upload `rsna-knee-teacher.zip` and `install_rsna_teacher.py` to the AWS home directory.
2. `cd "$HOME" && python install_rsna_teacher.py`
3. `cd "$HOME/rsna-knee-abnormality-detection" && source .venv/bin/activate`
4. `python research/teacher/run.py prepare`
5. Open `notebooks/05_multilingual_teacher_pilot.ipynb`, select **RSNA Knee - audit**, restart kernel/run all, save, close, reopen.
6. `python research/teacher/run.py collect`
7. Return `returns/rsna-knee-teacher-return.zip`.

On any failure after installation: stop, then `python research/teacher/run.py diagnose`. The same return filename is created as an explicitly partial snapshot where possible. Do not retry a failed real inference unchanged. Completed call checkpoints are immutable and retain their hashes. A complete recorded pilot's second invocation performs zero new model calls and does not start the model server.

## Notebook outputs

Each of twelve chart cells creates an interactive Plotly output **and a separate PNG** from the identical numeric specification. Agg PNG generation uses the already installed Matplotlib 3.10.6, not Chrome/Kaleido. It is recreated on every execution; it is not a one-time output patch. Charts and captions distinguish count, coverage, synthetic matching and clinical accuracy. PNG, Plotly JSON, numeric-spec JSON and interactive HTML are saved together with a local plotting-library bundle.

The collector checks source identity, ordered execution counts, completion marker, errors, 12 PNG hashes, 12 Plotly specification hashes, prior provenance and checkpoint integrity. A complete evidence package can truthfully have `pilot_outcome=blocked_canary`; that is not successful teacher validation. Raw response files and evidence quotes are never automatically published.

## Following decision

Successful completion only establishes a usable local teacher pipeline and small paired candidate comparison. Before target promotion, independently adjudicate original-language report assertions using the supplied review protocol. Then plan two score-bearing image rounds: (1) complementary plane/contrast inclusion with one frozen encoder; (2) spatial crop/slice-context additions and removals on identical evaluation rows and training budgets. Preserve the expert-label holdout and document any new evaluation access deliberately.

Prepared code is statically inspected, not executed by the assistant. Tests, binary loading, downloads, inference, notebook execution, AWS actions and Git actions remain user-executed.
