# Public source and evidence boundary

The [completed project](PROJECT_CLOSEOUT.md) publishes the final context evaluation,
its necessary controls, and the numerical/data contracts behind the public reference.
The [reproduction guide](REPRODUCIBILITY.md) is the canonical execution path.

## Included

The maintained source contains twelve-label scoring, physical slice-order and
DICOM-decoding checks, global attention-pooling contracts, grouped uncertainty,
fitted synthetic controls, verified checkpoint reuse, a genuinely executed final
aggregate notebook, tests, and the browser demonstration.

## Excluded

MRI/DICOM inputs, patient/study identifiers, private row-level predictions, model
weights, tuned private inference settings, credentials and private run bundles are
not distributed. Generated local checkpoints belong outside the checkout.

Original aggregate measurements and their population limits are preserved. Synthetic
training and aggregate replay do not reproduce the withheld MRI model or establish
clinical validity. The external and grouped development results remain distinct.

## Verification

The configured CI checks cover the maintained source, all retained native tests,
clean-kernel notebook replay, pause/resume and prediction identity, browser behavior,
publication boundaries, and repository navigation. A clean public checkout requires
no old AWS space or private cloud resource.

[Model and evaluation scope](CONTEXT_MODELING_FRONTIER.md) · [Attribution](SOURCES.md)
