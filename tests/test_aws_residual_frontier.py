import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.rsna_research.aws_residual_frontier import (
    detect_image_layout,
    canonical_nhwc_shape,
    uint8_payload_gib,
    confirmation_gate,
)

class AwsResidualFrontierTests(unittest.TestCase):
    def test_canonical_nchw(self):
        shape=(72,3,336,336)
        self.assertEqual(detect_image_layout(shape),'NCHW')
        self.assertEqual(canonical_nhwc_shape(shape),(72,336,336,3))

    def test_legacy_nhwc(self):
        shape=(72,336,336,3)
        self.assertEqual(detect_image_layout(shape),'NHWC')
        self.assertEqual(canonical_nhwc_shape(shape),shape)

    def test_reject_ambiguous(self):
        with self.assertRaises(ValueError): detect_image_layout((4,3,10,3))
        with self.assertRaises(ValueError): detect_image_layout((3,10,10))

    def test_payload_estimate(self):
        self.assertAlmostEqual(uint8_payload_gib(187872,224,224,3),26.34,places=2)

    def test_stage70_screen_passes_public_aggregate_gate(self):
        d=confirmation_gate(
            candidate_mean=0.7662324468731795,
            mean_blend_delta=0.0013285202826023301,
            fold_deltas={0:0.0018020157597883335,2:0.0008550248054163267},
            worst_target_delta=-0.0026200070965126665,
            bootstrap_positive_fraction=0.9633333333333334,
            median_spearman=0.8176557722232383,
        )
        self.assertTrue(d['promoted'])

    def test_stage71_confirmation_fails_only_all_fold_nonnegative_gate(self):
        d=confirmation_gate(
            candidate_mean=0.7726475832913674,
            mean_blend_delta=0.0024371589736764676,
            fold_deltas={1:0.002299888073846512,3:-0.00008538643241529087,4:0.005096975279598404},
            worst_target_delta=-0.0015010533880218668,
            bootstrap_positive_fraction=1.0,
            median_spearman=0.6980628021603761,
        )
        self.assertFalse(d['promoted'])
        failed=[k for k,v in d['gates'].items() if not v]
        self.assertEqual(failed,['all_confirmation_folds_nonnegative'])

if __name__=='__main__':
    unittest.main()
