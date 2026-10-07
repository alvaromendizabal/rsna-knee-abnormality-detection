#!/usr/bin/env python3
"""Synthetic fixture: public twelve-label metric and submission contracts, no patient data."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def run_demo():
    import pandas as pd
    from rsna_knee.metrics import macro_auc_12, validate_submission
    from rsna_knee.schema import ContractError, LABELS, STUDY
    from rsna_research.current_frontier import paired_interval_state

    ids = ['synthetic-0', 'synthetic-1', 'synthetic-2', 'synthetic-3']
    truth = pd.DataFrame({label: [0, 0, 1, 1] for label in LABELS}, index=ids)
    predictions = pd.DataFrame({label: [.1, .4, .35, .8] for label in LABELS}, index=ids)
    result = macro_auc_12(truth, predictions)
    if result['macro_auc_12'] != .75:
        raise ValueError('Synthetic ranking fixture changed')
    submission = predictions.rename_axis(STUDY).reset_index()
    validate_submission(submission, submission.copy())
    rejected = []
    for name, bad in [('misordered', submission.iloc[::-1]), ('nonfinite', submission.assign(**{LABELS[0]: float('nan')}))]:
        try:
            validate_submission(bad, submission)
        except ContractError:
            rejected.append(name)
        else:
            raise ValueError('Invalid submission was accepted: ' + name)
    state = paired_interval_state(delta=.001, lower=-.002, upper=.003)
    if state != 'INCONCLUSIVE':
        raise ValueError('Uncertainty fixture changed')
    return {'evidence_type': 'SYNTHETIC_ONLY', 'studies': 4, 'targets': 12, 'macro_auc': result['macro_auc_12'], 'invalid_inputs_rejected': rejected, 'positive_point_estimate_decision': state}


if __name__ == '__main__':
    print(json.dumps(run_demo(), indent=2))
