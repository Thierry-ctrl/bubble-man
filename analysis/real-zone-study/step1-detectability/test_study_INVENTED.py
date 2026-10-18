"""All time series, events and values here are INVENTED; no real-data reads."""
from copy import deepcopy
import json
import unittest

import numpy as np
import pandas as pd

import study as S


class InventedStudyChecks(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((S.HERE / "plan.json").read_text())
        self.index = pd.date_range("2020-01-01", periods=365 * 48, freq="30min")
        self.s = pd.Series(np.arange(len(self.index), dtype=float), index=self.index)

    def warning(self, stamp):
        return (0, pd.Timestamp(stamp), 9.0, 2.0)

    def test_01_injection_changes_only_finite_onset_and_later_bins(self):
        self.s.iloc[3001] = np.nan
        before = self.s.copy()
        altered = S.inject(self.s, self.index[3000], 2.0)
        pd.testing.assert_series_equal(self.s, before)
        pd.testing.assert_series_equal(altered.iloc[:3000], before.iloc[:3000])
        self.assertTrue(np.isnan(altered.iloc[3001]))
        self.assertEqual(altered.iloc[3000], before.iloc[3000] + 2)
        self.assertEqual(altered.iloc[-1], before.iloc[-1] + 2)

    def test_02_zero_injection_is_identical(self):
        self.s.iloc[4000] = np.nan
        pd.testing.assert_series_equal(S.inject(self.s, self.index[3000], 0), self.s)

    def test_03_invalid_sizes_and_off_grid_onset_are_rejected(self):
        for value in [-1, np.nan, np.inf]:
            with self.assertRaises(ValueError): S.inject(self.s, self.index[3000], value)
        with self.assertRaises(ValueError): S.inject(self.s, self.index[3000] + pd.Timedelta(minutes=1), 2)

    def test_04_existing_warning_is_not_injected_response(self):
        onset = self.index[3000]
        issue = onset + pd.Timedelta(hours=5)
        r = S.response([self.warning(issue)], {issue}, onset)
        self.assertTrue(r["any_warning"])
        self.assertFalse(r["primary_response"])
        self.assertIsNone(r["delay_hours"])

    def test_05_retimed_warning_uses_first_new_issue(self):
        onset = self.index[3000]
        old = onset + pd.Timedelta(hours=24)
        new = onset + pd.Timedelta(hours=48)
        r = S.response([self.warning(old), self.warning(new)], {old}, onset)
        self.assertEqual(r["delay_hours"], 48)

    def test_06_seven_day_boundary_and_contributing_bin_guard(self):
        onset = self.index[3000]
        self.assertTrue(S.response([self.warning(onset + pd.Timedelta(hours=168))], set(), onset)["primary_response"])
        self.assertFalse(S.response([self.warning(onset + pd.Timedelta(hours=168, minutes=30))], set(), onset)["primary_response"])
        self.assertFalse(S.response([self.warning(onset)], set(), onset)["primary_response"])
        self.assertTrue(S.response([self.warning(onset + pd.Timedelta(minutes=30))], set(), onset)["primary_response"])

    def test_07_selection_uses_completeness_then_numeric_id_only(self):
        sources = {"10": self.s.copy(), "2": self.s.copy(), "1": self.s.copy()}
        sources["1"].iloc[100] = np.nan
        chosen = S.select_zones(sources, ["10", "1", "2"], 2)
        self.assertEqual([r["dma"] for r in chosen], ["2", "10"])

    def test_08_random_starts_reproducible_unique_and_in_bounds(self):
        dates = S.random_onsets(self.index, "11", self.plan)
        self.assertEqual(len(dates), 200)
        self.assertEqual(len(set(dates)), 200)
        self.assertTrue(dates.equals(S.random_onsets(self.index, "11", self.plan)))
        self.assertGreaterEqual(dates.min(), self.index[0] + pd.Timedelta(days=56))
        self.assertLessEqual(dates.max() + pd.Timedelta(hours=168), self.index[-1])
        self.assertFalse(dates.equals(S.random_onsets(self.index, "12", self.plan)))

    def test_09_reference_uses_complete_nights_and_not_residuals(self):
        values = np.tile(np.repeat([8, 6, 4, 2, 10, 12] + [100] * 18, 2), 365).astype(float)
        s = pd.Series(values, index=self.index)
        s.iloc[30 * 48] = np.nan
        value, n = S.night_reference(s)
        self.assertEqual(value, 3)
        self.assertEqual(n, 336)

    def test_10_relative_sizes_and_duplicate_absolute_size(self):
        plan = deepcopy(self.plan)
        plan["relative_sizes_percent"] = [5]
        sizes = S.sizes_for(10, plan)
        half = next(tags for size, tags in sizes if size == 0.5)
        self.assertIn("absolute", half)
        self.assertIn("5% reference", half)
        self.assertEqual(len(sizes), 7)
        self.assertEqual(len(S.sizes_for(None, plan)), 7)

    def test_11_zero_reference_is_not_a_percent_scale(self):
        s = pd.Series(np.zeros(len(self.index)), index=self.index)
        self.assertIsNone(S.night_reference(s)[0])

    def test_12_misses_stay_in_denominator_but_not_median_delay(self):
        rows = [{"primary_response": False, "any_warning": False, "delay_hours": None}] * 9
        rows += [{"primary_response": True, "any_warning": True, "delay_hours": 24}]
        result = S.summarise(rows)
        self.assertEqual(result["primary_probability"], 0.1)
        self.assertEqual(result["median_delay_h"], 24)

    def test_13_minimum_requires_every_larger_tested_size(self):
        rows = [{"size_m3h": x, "primary_probability": p} for x, p in [(0.5, .95), (1, .8), (2, .95)]]
        self.assertEqual(S.minimum_size(rows, .9), 2)
        rows[-1]["primary_probability"] = .89
        self.assertIsNone(S.minimum_size(rows, .9))

    def test_14_full_unchanged_rules_preserve_past_and_respond_to_large_invented_step(self):
        rng = np.random.default_rng(20261018)
        daily = np.tile(np.repeat([10, 9, 8, 9, 12, 14] + [20] * 18, 2), 365).astype(float)
        daily += np.repeat(rng.normal(0, .15, 365), 48)
        s = pd.Series(daily, index=self.index)
        original, fz, ad = S.yw.R.both_rules(s)
        onset = self.index[100 * 48 + 20]
        changed, fz2, ad2 = S.yw.R.both_rules(S.inject(s, onset, 20))
        self.assertTrue(original.assessable and changed.assessable)
        self.assertEqual(original.threshold, changed.threshold)
        for old, new in [(fz, fz2), (ad, ad2)]:
            old_times = {w[1] for w in old}
            self.assertEqual({w[1] for w in old if w[1] < onset}, {w[1] for w in new if w[1] < onset})
            self.assertTrue(S.response(new, old_times, onset)["primary_response"])
        self.assertTrue(S.all_seven_opportunities(original, s.index[0], onset, 168))


if __name__ == "__main__":
    unittest.main()
