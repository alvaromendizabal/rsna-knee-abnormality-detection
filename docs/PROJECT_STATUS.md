# Project status

## Completed and verified

- Metadata and supervision audit completed.
- Protocol/acquisition feature research completed for the current 130-column representation.
- One real MRI series processed through the image-context pipeline; the second invocation reused its verified checkpoint.
- Supervision-rule study completed on a fixed training-only report sample.
- Multilingual-teacher infrastructure completed, but the experiment was stopped by its synthetic canary before any real competition report was sent to the model.
- Executed research notebooks preserve aggregate Plotly outputs and PNG companions.

## Not yet established

- No official development macro ROC AUC has been measured for an image model at this checkpoint.
- No feature family has yet been promoted on the basis of a controlled AUC gain.
- Patient-level disjointness is not established from the documented CSV metadata alone.
- The current local teacher is not approved as a source of training targets.
- No claim is made about beating the competition leaderboard.

## Next score-bearing gates

1. Establish a fixed, defensible score-bearing baseline on protected evaluation rows.
2. Compare plane and contrast representations with the same encoder/training budget.
3. Compare whole-knee versus localized field-of-view representations.
4. Compare through-slice context windows and positional/geometry features.
5. Measure per-finding gains, stability, uncertainty, and compute cost before promotion.
