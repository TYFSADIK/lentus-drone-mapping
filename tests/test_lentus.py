import json
import unittest

import numpy as np

from lentus import detect, synthetic
from lentus.awareness import AwarenessMap
from lentus.survey import Camera, gsd_cm, plan


class TestLentus(unittest.TestCase):
    def test_gsd_scales_with_height(self):
        self.assertAlmostEqual(gsd_cm(Camera(), 100) / gsd_cm(Camera(), 50), 2.0)
        self.assertLess(plan(Camera(), 80)["line_spacing_m"], plan(Camera(), 80, side_overlap=0.3)["line_spacing_m"])

    def test_otsu_bimodal(self):
        v = np.r_[np.random.default_rng(0).normal(0, 0.1, 500), np.random.default_rng(1).normal(1, 0.1, 500)]
        self.assertAlmostEqual(detect.otsu(v), 0.5, delta=0.15)

    def test_flood_change_ignores_river(self):
        b, river = synthetic.landscape()
        a, truth = synthetic.flooded(b, river)
        new = detect.change(detect.flood_mask(b), detect.flood_mask(a))
        self.assertGreater((new & truth).sum() / (new | truth).sum(), 0.8)
        self.assertLess((new & river).sum(), 0.02 * river.sum())

    def test_awareness_delta(self):
        m = AwarenessMap(45, -75)
        m.add_tile(45.0001, -74.9999, "flood", 0.4, 0.9)
        self.assertEqual(len(json.loads(m.geojson(only_dirty=True))["features"]), 1)
        self.assertEqual(len(json.loads(m.geojson(only_dirty=True))["features"]), 0)


if __name__ == "__main__":
    unittest.main()
