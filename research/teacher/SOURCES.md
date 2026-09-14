# Primary-source register — checked September 14, 2026

1. Official Kaggle dataset and target contract: https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/data . Reports are training-only and multilingual; deriving report supervision is part of the stated task. No official leaderboard performance is inferred from these local results.
2. Original model publisher: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 . General-purpose, non-thinking instruction model, multilingual capability claims and Apache-2.0 licensing. These are not claims of validated knee-report extraction.
3. Quantization publisher and file: https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/blob/main/Qwen3-4B-Instruct-2507-Q4_K_M.gguf . Exact bytes 2,497,281,120 and LFS SHA-256 3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597. Pinned repository revision a06e946bb6b655725eafa393f4a9745d460374c9. Third-party quantization is not the original publisher's clinical validation.
4. Official native runtime release: https://github.com/ggml-org/llama.cpp/releases/tag/b10937 . Pinned prerelease, user preflight required. GitHub's release asset digest is resolved during user setup and verified before executing the binary. Digest retrieval is not a signature-based security audit.
5. Pinned server documentation: https://raw.githubusercontent.com/ggml-org/llama.cpp/b10937/tools/server/README.md . CPU inference, JSON-schema response format, token-count endpoint, thread/context controls, local binding, authentication file, offline mode and disabling agent/UI/slots. The configured inference endpoint is loopback, not a paid remote service.
6. Plotly renderers: https://plotly.com/python/renderers/ . Plotly MIME availability differs from front-end visibility; this stage writes separate ordinary image outputs as well.
7. Matplotlib non-interactive backends: https://matplotlib.org/stable/users/explain/figure/backends.html . Agg renders PNG companions from the same numeric specifications without browser infrastructure.
8. MRNet original knee MRI work: https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002699 . Supports researching multi-plane image and slice representations. Its data/tasks/metrics are not interchangeable with this competition, and no score equivalence is claimed.

## Returned project evidence (not outside research)

The supplied `rsna-knee-supervision-return.zip` contained 73 declared members plus RETURN_MANIFEST.json. All declared hashes matched during inspection. Evidence reports 80 passing tests, a 256-report sample, 330/3,072 binary candidate cells in the joint lexical arm, 58 expert studies plus four report-overlap exclusions, and zero fitted models. Notebook 04 contains 12 PNG and 12 Plotly outputs. These are the basis for choosing this small supervision comparison rather than another metadata expansion.

## Unverified items

Current leaderboard top row, clinical validity of either prompt, patient/site identity, original-model training-corpus overlap, current competition external-weight permission, installed runtime compatibility and local model speed remain unverified. Do not fill these gaps with a claimed score or implicit authorization.
