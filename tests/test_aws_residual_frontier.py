import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.rsna_research.aws_residual_frontier import public_gap, detect_image_layout, canonical_nhwc_shape, uint8_payload_gib

class AwsResidualFrontierTests(unittest.TestCase):
    def test_public_gap(self):
        self.assertEqual(public_gap(0.933,0.961),0.028)
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

if __name__=='__main__': unittest.main()
