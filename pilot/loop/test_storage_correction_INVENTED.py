"""Every tank, reading, date, flow and error bound below is INVENTED.

These are accounting checks, not leak-detector runs or field evidence.
"""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import math
import unittest

from storage_correction import (
    FlowInterval, LevelReading, VolumeCurve, correct_storage,
)

INVENTED_LOCAL = timezone(timedelta(hours=2))
INVENTED_START = datetime(2026, 1, 1, tzinfo=INVENTED_LOCAL)
HALF_HOUR = timedelta(minutes=30)
INVENTED_END = INVENTED_START + HALF_HOUR
INVENTED_TANK = "INVENTED-T1"


class InventedStorageCases(unittest.TestCase):
    def setUp(self):
        self.curve = VolumeCurve.constant_area(100, 0, 4)
        self.flow = FlowInterval(INVENTED_START, INVENTED_END, 100)
        self.levels = [LevelReading(INVENTED_START, 1), LevelReading(INVENTED_END, 1.2)]

    def run_case(self, *, flow=None, readings=None, curve=None, confirmed=True):
        return correct_storage(
            [self.flow if flow is None else flow],
            {INVENTED_TANK: self.curve if curve is None else curve},
            {INVENTED_TANK: self.levels if readings is None else readings},
            expected_interval=HALF_HOUR, inventory_confirmed=confirmed)[0]

    def test_01_filling_is_subtracted(self):
        r = self.run_case()
        self.assertEqual(r.status, "ok")
        self.assertAlmostEqual(r.mean_storage_change_m3_h, 40)
        self.assertAlmostEqual(r.mean_withdrawals_and_losses_m3_h, 60)

    def test_02_drawing_is_added_back(self):
        r = self.run_case(readings=[replace(self.levels[0], depth_m=1.2),
                                    replace(self.levels[1], depth_m=1)])
        self.assertAlmostEqual(r.mean_storage_change_m3_h, -40)
        self.assertAlmostEqual(r.mean_withdrawals_and_losses_m3_h, 140)

    def test_03_steady_storage_keeps_boundary_flow(self):
        r = self.run_case(readings=[self.levels[0], replace(self.levels[1], depth_m=1)])
        self.assertEqual(r.mean_withdrawals_and_losses_m3_h, 100)

    def test_04_tank_can_supply_customers_with_zero_boundary_inflow(self):
        r = self.run_case(flow=replace(self.flow, mean_net_inflow_m3_h=0),
                          readings=[replace(self.levels[0], depth_m=2),
                                    replace(self.levels[1], depth_m=1.5)])
        self.assertEqual(r.mean_withdrawals_and_losses_m3_h, 100)

    def test_05_two_tanks_filling_and_drawing_both_count(self):
        r = correct_storage([self.flow], {INVENTED_TANK: self.curve, "INVENTED-T2": self.curve},
                            {INVENTED_TANK: self.levels, "INVENTED-T2": [
                             LevelReading(INVENTED_START, 2), LevelReading(INVENTED_END, 1.9)]},
                            expected_interval=HALF_HOUR, inventory_confirmed=True)[0]
        self.assertAlmostEqual(r.mean_storage_change_m3_h, 20)
        self.assertAlmostEqual(r.mean_withdrawals_and_losses_m3_h, 80)
        self.assertEqual(len(r.tank_changes_m3), 2)

    def test_06_signed_net_export_can_be_offset_by_tank_draw(self):
        r = self.run_case(flow=replace(self.flow, mean_net_inflow_m3_h=-10),
                          readings=[replace(self.levels[0], depth_m=2),
                                    replace(self.levels[1], depth_m=1.5)])
        self.assertEqual(r.mean_withdrawals_and_losses_m3_h, 90)

    def test_07_dead_volume_cancels_from_storage_change(self):
        a = self.run_case()
        b = self.run_case(curve=VolumeCurve.constant_area(100, 1, 4, 250))
        self.assertAlmostEqual(a.mean_storage_change_m3_h, b.mean_storage_change_m3_h)

    def test_08_nonconstant_area_uses_volume_curve(self):
        r = self.run_case(curve=VolumeCurve((0, 1, 2), (0, 10, 40)),
                          readings=[replace(self.levels[0], depth_m=.5),
                                    replace(self.levels[1], depth_m=1.5)])
        self.assertEqual(r.mean_storage_change_m3_h, 40)
        self.assertEqual(r.mean_withdrawals_and_losses_m3_h, 60)

    def test_09_vertical_cylinder_geometry_in_metres(self):
        curve = VolumeCurve.vertical_cylinder(2, 4)
        self.assertAlmostEqual(curve.volume(2), 2 * math.pi)
        r = self.run_case(curve=curve)
        self.assertAlmostEqual(r.mean_storage_change_m3_h, .4 * math.pi)

    def test_10_missing_one_of_two_tanks_prevents_partial_correction(self):
        r = correct_storage([self.flow], {INVENTED_TANK: self.curve, "INVENTED-T2": self.curve},
                            {INVENTED_TANK: self.levels, "INVENTED-T2": self.levels[:1]},
                            expected_interval=HALF_HOUR, inventory_confirmed=True)[0]
        self.assertEqual(r.status, "unassessable")
        self.assertIsNone(r.mean_storage_change_m3_h)
        self.assertIsNone(r.mean_withdrawals_and_losses_m3_h)

    def test_11_entire_tank_reading_set_missing_is_not_zero(self):
        r = correct_storage([self.flow], {INVENTED_TANK: self.curve}, {},
                            expected_interval=HALF_HOUR, inventory_confirmed=True)[0]
        self.assertEqual(r.status, "unassessable")

    def test_12_flagged_endpoint_is_unusable(self):
        for i in range(2):
            levels = list(self.levels)
            levels[i] = replace(levels[i], usable=False)
            self.assertEqual(self.run_case(readings=levels).status, "unassessable")

    def test_13_missing_or_nonfinite_flow_is_unusable(self):
        for value in (None, math.nan, math.inf, -math.inf, True, "100"):
            r = self.run_case(flow=replace(self.flow, mean_net_inflow_m3_h=value))
            self.assertEqual(r.status, "unassessable")

    def test_14_flagged_boundary_flow_is_unusable(self):
        self.assertEqual(self.run_case(flow=replace(self.flow, usable=False)).status, "unassessable")

    def test_15_invalid_depth_is_not_clamped(self):
        for value in (None, math.nan, math.inf, -.1, 4.1, "1", True):
            r = self.run_case(readings=[self.levels[0], replace(self.levels[1], depth_m=value)])
            self.assertEqual(r.status, "unassessable")
            self.assertIsNone(r.mean_withdrawals_and_losses_m3_h)

    def test_16_nearby_or_future_level_cannot_replace_exact_endpoint(self):
        for shift in (-1, 1, 60):
            levels = [self.levels[0], replace(self.levels[1], at=INVENTED_END + timedelta(seconds=shift))]
            self.assertEqual(self.run_case(readings=levels).status, "unassessable")

    def test_17_interval_is_not_available_at_its_start(self):
        r = self.run_case()
        self.assertEqual(r.not_before, INVENTED_END.astimezone(timezone.utc))
        self.assertGreater(r.not_before, r.start)

    def test_18_received_time_delays_availability(self):
        levels = [self.levels[0], replace(self.levels[1], received_at=INVENTED_END + timedelta(hours=2))]
        r = self.run_case(flow=replace(self.flow, received_at=INVENTED_END + timedelta(minutes=10)),
                          readings=levels)
        self.assertEqual(r.not_before, (INVENTED_END + timedelta(hours=2)).astimezone(timezone.utc))

    def test_19_offsets_match_only_when_they_represent_same_instant(self):
        levels = [replace(x, at=x.at.astimezone(timezone.utc)) for x in self.levels]
        self.assertEqual(self.run_case(readings=levels).status, "ok")
        wrong = [replace(x, at=x.at.replace(tzinfo=timezone.utc)) for x in self.levels]
        self.assertEqual(self.run_case(readings=wrong).status, "unassessable")

    def test_20_naive_timestamps_are_rejected(self):
        with self.assertRaises(ValueError):
            self.run_case(flow=replace(self.flow, start=INVENTED_START.replace(tzinfo=None)))
        with self.assertRaises(ValueError):
            self.run_case(readings=[replace(self.levels[0], at=INVENTED_START.replace(tzinfo=None)),
                                    self.levels[1]])

    def test_21_duplicate_levels_are_rejected_even_with_different_offset(self):
        with self.assertRaises(ValueError):
            self.run_case(readings=self.levels + [replace(self.levels[0],
                          at=INVENTED_START.astimezone(timezone.utc))])

    def test_22_wrong_duration_and_overlapping_flows_are_rejected(self):
        for end in (INVENTED_START, INVENTED_END + timedelta(minutes=1)):
            with self.assertRaises(ValueError):
                self.run_case(flow=replace(self.flow, end=end))
        with self.assertRaises(ValueError):
            correct_storage([self.flow, self.flow], {INVENTED_TANK: self.curve},
                            {INVENTED_TANK: self.levels}, expected_interval=HALF_HOUR,
                            inventory_confirmed=True)

    def test_23_gap_is_preserved_without_manufacturing_intervals(self):
        late = replace(self.flow, start=INVENTED_START + timedelta(hours=2),
                       end=INVENTED_END + timedelta(hours=2))
        levels = self.levels + [replace(x, at=x.at + timedelta(hours=2)) for x in self.levels]
        result = correct_storage([self.flow, late], {INVENTED_TANK: self.curve},
                                 {INVENTED_TANK: levels}, expected_interval=HALF_HOUR,
                                 inventory_confirmed=True)
        self.assertEqual(len(result), 2)
        self.assertTrue(any("gap_before" in x for x in result[1].notes))

    def test_24_unconfirmed_inventory_blocks_correction(self):
        self.assertEqual(self.run_case(confirmed=False).status, "unassessable")

    def test_25_confirmed_no_storage_is_explicit_pass_through(self):
        result = correct_storage([replace(self.flow, error_bound_m3_h=2)], {}, {},
                                 expected_interval=HALF_HOUR, inventory_confirmed=True)[0]
        self.assertEqual(result.mean_storage_change_m3_h, 0)
        self.assertEqual(result.mean_withdrawals_and_losses_m3_h, 100)
        self.assertEqual(result.bounded_range_m3_h, (98, 102))

    def test_26_unknown_error_is_not_treated_as_zero(self):
        r = self.run_case()
        self.assertIsNone(r.bounded_range_m3_h)
        self.assertIn("measurement_uncertainty_unquantified", r.notes)

    def test_27_level_resolution_error_grows_as_interval_shortens(self):
        for minutes, expected_error in ((30, 4), (5, 24)):
            step = timedelta(minutes=minutes)
            end = INVENTED_START + step
            levels = [LevelReading(INVENTED_START, 2, error_bound_m=.005),
                      LevelReading(end, 2, error_bound_m=.005)]
            r = correct_storage([FlowInterval(INVENTED_START, end, 100, error_bound_m3_h=0)],
                                {INVENTED_TANK: VolumeCurve.constant_area(200, 0, 4)},
                                {INVENTED_TANK: levels}, expected_interval=step,
                                inventory_confirmed=True)[0]
            self.assertAlmostEqual(r.bounded_range_m3_h[0], 100 - expected_error)
            self.assertAlmostEqual(r.bounded_range_m3_h[1], 100 + expected_error)

    def test_28_nonconstant_area_gives_asymmetric_bounds(self):
        r = self.run_case(curve=VolumeCurve((0, 1, 2), (0, 10, 30)),
                          flow=replace(self.flow, mean_net_inflow_m3_h=20, error_bound_m3_h=0),
                          readings=[replace(self.levels[0], depth_m=.5, error_bound_m=0),
                                    replace(self.levels[1], depth_m=.95, error_bound_m=.1)])
        self.assertAlmostEqual(r.mean_withdrawals_and_losses_m3_h, 11)
        self.assertAlmostEqual(r.bounded_range_m3_h[0], 8)
        self.assertAlmostEqual(r.bounded_range_m3_h[1], 13)

    def test_29_uncertainty_outside_geometry_prevents_extrapolation(self):
        for other_error in (.01, None):
            r = self.run_case(readings=[replace(self.levels[0], depth_m=0, error_bound_m=.01),
                                        replace(self.levels[1], error_bound_m=other_error)])
            self.assertEqual(r.status, "unassessable")

    def test_30_negative_result_is_retained_and_flagged(self):
        r = self.run_case(flow=replace(self.flow, mean_net_inflow_m3_h=10))
        self.assertAlmostEqual(r.mean_withdrawals_and_losses_m3_h, -30)
        self.assertTrue(any("negative_corrected_flow" in x for x in r.notes))

    def test_31_invented_fill_draw_sequence_closes_full_volume_balance(self):
        # Handwritten INVENTED story: storage 10,15,12,12,8,10 m3;
        # net entering volumes 35,27,30,26,32 m3; withdrawals 30 m3 each.
        depths = (1, 1.5, 1.2, 1.2, .8, 1)
        mean_flows = (70, 54, 60, 52, 64)
        levels = [LevelReading(INVENTED_START + i * HALF_HOUR, h) for i, h in enumerate(depths)]
        flows = [FlowInterval(INVENTED_START + i * HALF_HOUR,
                              INVENTED_START + (i + 1) * HALF_HOUR, q)
                 for i, q in enumerate(mean_flows)]
        rows = correct_storage(flows, {INVENTED_TANK: VolumeCurve.constant_area(10, 0, 4)},
                               {INVENTED_TANK: levels}, expected_interval=HALF_HOUR,
                               inventory_confirmed=True)
        for r in rows:
            self.assertAlmostEqual(r.mean_withdrawals_and_losses_m3_h, 60)
        self.assertAlmostEqual(sum(r.mean_storage_change_m3_h * .5 for r in rows), 0)
        self.assertAlmostEqual(sum(r.mean_withdrawals_and_losses_m3_h * .5 for r in rows), 150)

    def test_32_invalid_geometry_is_rejected(self):
        for depths, volumes in [((0,), (0,)), ((0, 1), (0,)), ((0, 0), (0, 10)),
                                 ((0, 1), (10, 0)), ((0, 1), (0, 0)),
                                 ((-.1, 1), (0, 10)), ((0, 1), (0, math.inf))]:
            with self.assertRaises(ValueError):
                VolumeCurve(depths, volumes)
        for area in (0, -1, math.inf):
            with self.assertRaises(ValueError):
                VolumeCurve.constant_area(area, 0, 4)

    def test_33_undeclared_tank_is_rejected(self):
        with self.assertRaises(ValueError):
            correct_storage([self.flow], {}, {INVENTED_TANK: self.levels},
                            expected_interval=HALF_HOUR, inventory_confirmed=True)

    def test_34_invalid_error_bound_is_not_hidden_by_other_unknown_bound(self):
        for error in (-.1, math.nan, math.inf):
            r = self.run_case(readings=[replace(self.levels[0], error_bound_m=error), self.levels[1]])
            self.assertEqual(r.status, "unassessable")
            self.assertEqual(self.run_case(flow=replace(self.flow, error_bound_m3_h=error)).status,
                             "unassessable")

    def test_35_receipt_before_measurement_is_rejected(self):
        with self.assertRaises(ValueError):
            self.run_case(flow=replace(self.flow, received_at=INVENTED_START))
        with self.assertRaises(ValueError):
            self.run_case(readings=[self.levels[0], replace(self.levels[1], received_at=INVENTED_START)])

    def test_36_nonfinite_arithmetic_has_no_corrected_output(self):
        # Deliberately impossible INVENTED magnitudes exercise the numeric guard.
        huge = VolumeCurve((0, 1), (0, 1e308))
        r = correct_storage([self.flow], {"INVENTED-T1": huge, "INVENTED-T2": huge},
                            {name: [LevelReading(INVENTED_START, 0), LevelReading(INVENTED_END, 1)]
                             for name in ("INVENTED-T1", "INVENTED-T2")},
                            expected_interval=HALF_HOUR, inventory_confirmed=True)[0]
        self.assertEqual(r.status, "unassessable")
        self.assertIsNone(r.mean_withdrawals_and_losses_m3_h)
        with self.assertRaises(ValueError):
            VolumeCurve.vertical_cylinder(1e308, 1)


if __name__ == "__main__":
    unittest.main()
