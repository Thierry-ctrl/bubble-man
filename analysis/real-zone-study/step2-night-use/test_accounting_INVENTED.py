"""Accounting edge cases on invented inputs only; no utility/outcome files read."""
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import accounting as A


class AccountingChecks(unittest.TestCase):
    def test_physical_feasibility_does_not_silently_make_negative_leak(self):
        self.assertEqual(A.share_bounds(10, 10, 2, 12), (0, 0.8))
        self.assertEqual(A.share_bounds(10, 10, 12, 14), (None, None))

    def test_variation_range_excludes_infeasible_low_flow_corner(self):
        self.assertEqual(A.share_bounds(10, 20, 12, 14), (0, 0.4))

    def test_observed_night_variation_is_not_treated_as_uncertainty_on_use(self):
        lo, hi = A.share_bounds(5, 20, 1, 4)
        self.assertAlmostEqual(lo, 0.2)
        self.assertAlmostEqual(hi, 0.95)

    def test_bad_ranges_and_counts_stop(self):
        for vals in [(0, 10, 1, 2), (10, 5, 1, 2), (5, 10, 2, 1), (5, 10, float('nan'), 2)]:
            with self.assertRaises(ValueError):
                A.share_bounds(*vals)
        for count in [-1, 1.5, True]:
            with self.assertRaises(ValueError):
                A.components(count, 2, [1, 4], [0.7, 60.6])

    def test_litres_and_cubic_metres_are_not_confused(self):
        hh, nh, use = A.components(1000, 10, [1, 4], [10, 20])
        np.testing.assert_allclose(hh, [1, 4])
        np.testing.assert_allclose(nh, [0.1, 0.2])
        np.testing.assert_allclose(use, [1.1, 4.2])

    def test_missing_quarter_does_not_become_low_flow(self):
        q = np.full(365 * 96, 20.)
        q[8] = np.nan
        h = A.hourly_from_quarters(q)
        self.assertTrue(np.isnan(h[0, 2]))
        self.assertEqual(h[0, 3], 20)

    def test_hour_is_chosen_from_training_weekdays_only(self):
        dates = pd.date_range(A.START, periods=365)
        h = np.full((365, 24), 10.)
        h[:28, 2] = 5
        h[np.asarray(dates.dayofweek >= 5), 0] = 0
        h[28:, 4] = 0
        hour, training, _ = A.choose_hour(h, dates)
        self.assertEqual(hour, 2)
        self.assertEqual(int(training.sum()), 20)
        h[0, 5] = np.nan
        self.assertEqual(int(A.choose_hour(h, dates)[1].sum()), 19)

    def test_hour_ties_and_insufficient_training(self):
        dates = pd.date_range(A.START, periods=365)
        h = np.full((365, 24), 10.)
        self.assertEqual(A.choose_hour(h, dates)[0], 0)
        h[:28] = np.nan
        with self.assertRaises(ValueError):
            A.choose_hour(h, dates)

    def test_property_join_does_not_duplicate_or_substitute_zones(self):
        header = 'DMA,Area,Number Of Household Properties,Number Of Non-Household Properties\n'
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'invented.csv'
            p.write_text(header + '011,N4,100,6\n')
            self.assertEqual(A.property_rows(p, ['11'])[0]['households'], 100)
            for rows in ['11,N4,100,6\n011,N4,100,6\n', '11,N3,100,6\n',
                         '11,N4,,6\n', '11,N4,100,-2\n']:
                p.write_text(header + rows)
                with self.assertRaises(ValueError):
                    A.property_rows(p, ['11'])


if __name__ == '__main__':
    unittest.main()
