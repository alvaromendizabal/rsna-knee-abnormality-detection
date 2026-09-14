# Sources and what they support

Public-source research checked for this delivery on September 13, 2026 (America/Los_Angeles). The review container's UTC date may already be September 14.

1. Official competition data: https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/data
   Supports per-study twelve-finding targets, sparse expert labels, training-only multilingual reports, and absence of reports during testing. The exact CSV schema and actual row counts are also checked against the user's frozen files. The official organizer definitions take precedence over our conservative lexical hypotheses.
2. Official evaluation: https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/overview/evaluation
   Metric source and submission constraints. A score on the tiny example test data is not an independent validation score.
3. Official leaderboard: https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/leaderboard
   The page was located, but the leading numeric rows were not exposed to the research browser. No current winning score is invented or taken from an older participant comment.
4. RSNA challenge description: https://www.rsna.org/artificial-intelligence/ai-image-challenge/knee-mri-ai-challenge
   Supports the multilingual and multi-site scope; does not establish this package's clinical accuracy.
5. Irvin et al., CheXpert: https://arxiv.org/abs/1901.07031
   Primary study of report-derived labels and pathology-dependent uncertainty handling in chest radiography. Motivates keeping uncertainty separate. It does not validate our knee rules, English vocabulary, or any uncertainty policy for this competition.
6. Peng et al., NegBio: https://arxiv.org/abs/1712.05898
   Primary study of negation/uncertainty scope via dependency patterns in radiology. Motivates scope-specific tests. Our bounded-clause prototype does not implement NegBio or claim its performance.
7. Bien et al., MRNet: https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002699
   Primary knee-MRI work supporting investigation of plane-aware and slice-aware learned representations. Its data/tasks/metrics are not directly comparable to this twelve-label competition.
8. Plotly rendering: https://plotly.com/python/renderers/
   Plotly MIME payloads need a compatible frontend; saved payloads alone do not establish visible plots.
9. Matplotlib backends: https://matplotlib.org/stable/users/explain/figure/backends.html
   Agg can write PNG images without a graphical desktop or browser. PNG companions in this package are rendered from the same aggregate specification, not exported by Kaleido.

Source-derived statements, user's measured evidence, and proposed hypotheses are intentionally distinct. Participant-generated pseudo-label datasets or gold-outcome-tuned thresholds are not imported. No package function contacts these URLs.
