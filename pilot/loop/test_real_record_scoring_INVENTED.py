"""All dates, warnings, incident records and visits below are INVENTED.

These checks validate draft bookkeeping, not a detector or real utility performance.
"""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import itertools
import unittest

from real_record_scoring import (
    DRAFT_STATUS, WEEK, Incident, TimeRange, Visit, Warning, Window,
    _maximum_associations, compare_week_shifts, score_field_visits, score_timing,
    select_control_nights,
)

LOCAL = timezone(timedelta(hours=2))
START = datetime(2026, 1, 5, tzinfo=LOCAL)


def invented_time(day, hour=4, minute=0):
    return START + timedelta(days=day, hours=hour, minutes=minute)


def invented_warning(name="W1", day=14, hour=4):
    return Warning("INVENTED-" + name, "INVENTED-ZONE", invented_time(day, hour))


def invented_incident(name="I1", day=15, hour=10):
    report = invented_time(day, hour)
    return Incident("INVENTED-" + name, "INVENTED-ZONE", TimeRange(report, report),
                    invented_time(day, max(hour, 12)))


class InventedScoringCases(unittest.TestCase):
    def setUp(self):
        self.window = Window("INVENTED-ZONE", START, START + 8 * WEEK)
        self.mask = [invented_time(d) for d in range(56)]

    def timing(self, warnings=None, incidents=None, mask=None):
        return score_timing([invented_warning()] if warnings is None else warnings,
                            [invented_incident()] if incidents is None else incidents,
                            self.window, self.mask if mask is None else mask)

    def visit(self, name="V1", warning=None, outcome="leak_found", **kwargs):
        w = invented_warning() if warning is None else warning
        defaults = {"checked_at": w.issued_at + timedelta(hours=4),
                    "warning_id": w.warning_id,
                    "incident_ids": ("INVENTED-I1",) if outcome == "leak_found" else (),
                    "staff_minutes": 30}
        defaults.update(kwargs)
        return Visit("INVENTED-" + name, self.window.zone_id,
                     w.issued_at + timedelta(hours=2), outcome, "warning", **defaults)

    def test_01_exact_report_lead_is_not_leak_start_delay(self):
        r = self.timing()
        self.assertEqual(r["maximum_unique_time_associations"], 1)
        self.assertEqual(r["warning_rows"][0]["lead_to_first_report_hours"], {"INVENTED-I1": [30, 30]})
        self.assertEqual(r["status"], DRAFT_STATUS)
        self.assertNotIn("detection_delay", r)

    def test_02_warning_at_report_time_is_not_early(self):
        r = self.timing(incidents=[invented_incident(day=14, hour=4)])
        self.assertEqual(r["maximum_unique_time_associations"], 0)
        self.assertEqual(r["warning_rows"][0]["status"], "no_recorded_eligible_leak")

    def test_03_seven_day_boundary_and_one_minute_outside(self):
        r = self.timing(incidents=[invented_incident(day=21, hour=4)])
        self.assertEqual(r["maximum_unique_time_associations"], 1)
        i = invented_incident(day=21, hour=4)
        later = i.first_report.earliest + timedelta(minutes=1)
        r = self.timing(incidents=[replace(i, first_report=TimeRange(later, later))])
        self.assertEqual(r["maximum_unique_time_associations"], 0)

    def test_04_date_only_same_day_is_uncertain(self):
        i = replace(invented_incident(day=14), first_report=TimeRange(
            invented_time(14, 0), invented_time(15, 0) - timedelta(microseconds=1)))
        r = self.timing(incidents=[i])
        self.assertEqual(r["maximum_unique_time_associations"], 0)
        self.assertEqual(r["maximum_with_uncertain_report_times"], 1)
        self.assertEqual(r["warning_rows"][0]["status"], "uncertain_report_time_association")

    def test_05_bounded_report_returns_a_lead_interval(self):
        i = replace(invented_incident(day=16), first_report=TimeRange(invented_time(15, 0), invented_time(16, 0)))
        r = self.timing(incidents=[i])
        self.assertEqual(r["warning_rows"][0]["lead_to_first_report_hours"], {"INVENTED-I1": [20, 44]})

    def test_06_report_uncertainty_crossing_horizon_is_not_guaranteed(self):
        i = replace(invented_incident(day=21), first_report=TimeRange(invented_time(21, 0), invented_time(22, 0)))
        r = self.timing(incidents=[i])
        self.assertEqual(r["maximum_unique_time_associations"], 0)
        self.assertEqual(r["maximum_with_uncertain_report_times"], 1)

    def test_07_one_warning_cannot_credit_two_incident_records(self):
        r = self.timing(incidents=[invented_incident("I1"), invented_incident("I2", day=16)])
        self.assertEqual(r["maximum_unique_time_associations"], 1)
        self.assertEqual(r["warnings_with_multiple_candidates"], 1)
        self.assertEqual(r["warning_rows"][0]["candidate_incidents"], ["INVENTED-I1", "INVENTED-I2"])

    def test_08_repeated_warnings_do_not_duplicate_a_record(self):
        r = self.timing(warnings=[invented_warning("W1", day=13), invented_warning("W2", day=14)])
        self.assertEqual(r["maximum_unique_time_associations"], 1)
        self.assertEqual(r["records_with_multiple_candidate_warnings"], 1)
        self.assertEqual(r["warnings_in_window"], 2)

    def test_09_maximum_matching_handles_an_augmenting_path(self):
        graph = {"INVENTED-W1": ("INVENTED-I1", "INVENTED-I2"), "INVENTED-W2": ("INVENTED-I1",)}
        self.assertEqual(_maximum_associations(graph), 2)

    def test_10_all_512_invented_three_by_three_graphs_against_brute_force(self):
        for bits in range(512):
            graph = {f"INVENTED-W{w}": tuple(f"INVENTED-I{i}" for i in range(3)
                        if bits & (1 << (3 * w + i))) for w in range(3)}
            best = 0
            for choices in itertools.product((None, 0, 1, 2), repeat=3):
                used = [i for i in choices if i is not None]
                if len(set(used)) != len(used):
                    continue
                if all(i is None or f"INVENTED-I{i}" in graph[f"INVENTED-W{w}"]
                       for w, i in enumerate(choices)):
                    best = max(best, len(used))
            self.assertEqual(_maximum_associations(graph), best, bits)

    def test_11_missing_report_time_is_not_invented(self):
        r = self.timing(incidents=[replace(invented_incident(), first_report=None)])
        self.assertEqual(r["incident_rows"][0]["status"], "missing_first_report")
        self.assertIsNone(r["record_association_share"])

    def test_12_suspected_and_future_confirmation_are_excluded(self):
        for confirmation, expected in [(None, "not_confirmed"), (self.window.end, "confirmation_after_cutoff")]:
            r = self.timing(incidents=[replace(invented_incident(), confirmed_at=confirmation)])
            self.assertEqual(r["incident_rows"][0]["status"], expected)
            self.assertEqual(r["eligible_confirmed_records"], 0)

    def test_13_preexisting_record_never_becomes_new_at_window_start(self):
        r = self.timing(incidents=[replace(invented_incident(), pre_existing=True)])
        self.assertEqual(r["incident_rows"][0]["status"], "pre_existing_record")
        self.assertEqual(r["maximum_unique_time_associations"], 0)

    def test_14_record_without_complete_pre_report_window_is_excluded(self):
        r = self.timing(warnings=[invented_warning(day=1)], incidents=[invented_incident(day=3)])
        self.assertEqual(r["incident_rows"][0]["status"], "incomplete_pre_report_window")

    def test_15_last_week_warning_is_censored_even_if_a_record_matches(self):
        r = self.timing(warnings=[invented_warning(day=50)], incidents=[invented_incident(day=51)])
        self.assertEqual(r["warning_rows"][0]["status"], "incomplete_followup_window")
        self.assertEqual(r["maximum_unique_time_associations"], 0)
        self.assertEqual(r["warnings_in_window"], 1)

    def test_16_mask_exclusion_keeps_warning_in_operator_count(self):
        w = invented_warning()
        r = self.timing(mask=[t for t in self.mask if t != w.issued_at])
        self.assertEqual(r["warning_rows"][0]["status"], "outside_approved_exposure")
        f = score_field_visits([w], [], self.window)
        self.assertEqual(f["warning_investigation_episodes"], 1)
        self.assertEqual(f["warning_episode_findings"]["unknown"], 1)

    def test_17_outside_zone_record_cannot_match(self):
        r = self.timing(incidents=[replace(invented_incident(), zone_id="INVENTED-OTHER")])
        self.assertEqual(r["incident_rows"][0]["status"], "other_zone")
        with self.assertRaises(ValueError):
            self.timing(warnings=[replace(invented_warning(), zone_id="INVENTED-OTHER")])

    def test_18_naive_times_bad_bounds_and_bad_chronology_fail(self):
        i = invented_incident()
        bad = [replace(i, confirmed_at=i.confirmed_at.replace(tzinfo=None)),
               replace(i, first_report=TimeRange(invented_time(16), invented_time(15))),
               replace(i, confirmed_at=invented_time(14)),
               replace(i, repair_completed_at=invented_time(14))]
        for item in bad:
            with self.assertRaises(ValueError):
                self.timing(incidents=[item])
        with self.assertRaises(ValueError):
            self.timing(warnings=[replace(invented_warning(), issued_at=START.replace(tzinfo=None))])

    def test_19_duplicate_ids_and_issue_times_fail(self):
        for ws in ([invented_warning(), invented_warning()],
                   [invented_warning("W1"), invented_warning("W2")]):
            with self.assertRaises(ValueError):
                self.timing(warnings=ws)
        with self.assertRaises(ValueError):
            self.timing(incidents=[invented_incident(), invented_incident()])

    def test_20_input_order_does_not_change_results(self):
        ws = [invented_warning("W1", day=13), invented_warning("W2", day=14)]
        incidents = [invented_incident("I1", day=15), invented_incident("I2", day=16)]
        self.assertEqual(self.timing(ws, incidents), self.timing(ws[::-1], incidents[::-1]))

    def test_21_timing_association_does_not_confirm_an_unvisited_warning(self):
        self.assertEqual(self.timing()["maximum_unique_time_associations"], 1)
        field = score_field_visits([invented_warning()], [], self.window)
        self.assertEqual(field["warning_rows"][0]["field_outcome"], "unknown")
        self.assertIsNone(field["warning_episode_findings"]["completed_check_yield"])

    def test_22_negative_completed_visit_is_not_called_a_false_alert(self):
        r = score_field_visits([invented_warning()], [self.visit(outcome="checked_nothing_found")], self.window)
        self.assertEqual(r["warning_rows"][0]["field_outcome"], "checked_nothing_found")
        self.assertNotIn("false_alert", str(r))

    def test_23_followup_finding_counts_one_episode_and_all_visits(self):
        negative = self.visit("V1", outcome="checked_nothing_found")
        found = replace(self.visit("V2"), planned_at=invented_time(16, 6), checked_at=invented_time(16, 8))
        r = score_field_visits([invented_warning()], [negative, found], self.window)
        self.assertEqual(r["warning_episode_findings"]["leak_found"], 1)
        self.assertEqual(r["warning_visits"], 2)
        self.assertEqual(r["staff_minutes_recorded"], 60)

    def test_24_pending_or_incomplete_followup_preserves_unknown(self):
        negative = self.visit("V1", outcome="checked_nothing_found")
        for followup in [self.visit("V2", outcome="not_checked", checked_at=None, staff_minutes=None),
                         self.visit("V2", outcome="incomplete_check")]:
            r = score_field_visits([invented_warning()], [negative, followup], self.window)
            self.assertEqual(r["warning_episode_findings"]["unknown"], 1)

    def test_25_missing_staff_time_is_not_zero(self):
        r = score_field_visits([invented_warning()], [self.visit(staff_minutes=None)], self.window)
        self.assertIsNone(r["staff_minutes_recorded"])
        self.assertEqual(r["visits_missing_staff_minutes"], 1)

    def test_26_invalid_visit_claims_are_rejected(self):
        bad = [self.visit(incident_ids=()), self.visit(incident_ids=("",)),
               self.visit(staff_minutes=float("nan")), self.visit(staff_minutes=-1),
               self.visit(checked_at=self.window.end),
               self.visit(outcome="not_checked", checked_at=None),
               self.visit(warning_id="INVENTED-MISSING")]
        for visit in bad:
            with self.assertRaises(ValueError):
                score_field_visits([invented_warning()], [visit], self.window)

    def test_27_warning_investigation_cannot_predate_issuance(self):
        v = replace(self.visit(), planned_at=invented_time(13), checked_at=invented_time(13, 6))
        with self.assertRaises(ValueError):
            score_field_visits([invented_warning()], [v], self.window)

    def test_28_controls_are_selected_without_incident_records(self):
        ws = [invented_warning("W1", day=14), invented_warning("W2", day=21)]
        r = select_control_nights(ws, self.window, self.mask, 3, 123)
        self.assertEqual(r["population"], 54)
        self.assertEqual(r["inclusion_probability"], 3 / 54)
        self.assertEqual(len(set(r["selected_issue_times"])), 3)
        self.assertFalse(set(r["selected_issue_times"]) & {w.issued_at for w in ws})
        self.assertEqual(r, select_control_nights(ws[::-1], self.window, self.mask[::-1], 3, 123))

    def test_29_control_pool_errors_are_not_silently_replaced(self):
        with self.assertRaises(ValueError):
            select_control_nights([], self.window, [invented_time(1), invented_time(1, 5)], 1, 1)
        with self.assertRaises(ValueError):
            select_control_nights([], self.window, [invented_time(1)], 2, 1)

    def test_30_control_findings_have_separate_unknown_and_yield_counts(self):
        c1 = Visit("INVENTED-C1", self.window.zone_id, invented_time(10), "leak_found", "random_control",
                   invented_time(10, 6), incident_ids=("INVENTED-CONTROL-LEAK",), selection_probability=0.1)
        c2 = Visit("INVENTED-C2", self.window.zone_id, invented_time(11), "not_checked", "random_control",
                   selection_probability=0.1)
        r = score_field_visits([invented_warning()], [c1, c2], self.window)
        self.assertEqual(r["control_visit_findings"]["leak_found"], 1)
        self.assertEqual(r["control_visit_findings"]["unknown"], 1)
        self.assertEqual(r["control_visit_findings"]["completion_share"], 0.5)
        self.assertEqual(r["warning_episode_findings"]["unknown"], 1)
        with self.assertRaisesRegex(ValueError, "warning day"):
            score_field_visits([invented_warning()], [replace(c1, planned_at=invented_time(14),
                                                               checked_at=invented_time(14, 6))], self.window)

    def test_31_control_probability_must_be_real_finite_and_nonzero(self):
        for p in (0, -0.1, 1.1, True, float("nan"), float("inf"), None):
            c = Visit("INVENTED-C1", self.window.zone_id, invented_time(10), "not_checked", "random_control",
                      selection_probability=p)
            with self.assertRaises(ValueError):
                score_field_visits([invented_warning()], [c], self.window)

    def test_32_shifts_preserve_weekday_clock_count_and_reject_censoring(self):
        r = compare_week_shifts([invented_warning()], [invented_incident()], self.window, self.mask)
        self.assertEqual(r["status"], "descriptive_only")
        self.assertEqual(len(r["reference_patterns"]), 6)
        self.assertEqual(r["rank_fraction_including_observed"], 1 / 7)
        self.assertIsNone(r["formal_p_value"])
        self.assertEqual(r["rejected_rotations"], [{"week_offset": 5, "reason": "unequal_or_incomplete_exposure"}])
        for p in r["reference_patterns"]:
            self.assertEqual(p["warning_count"], 1)
            t = p["issued_at"][0].astimezone(LOCAL)
            self.assertEqual((t.weekday(), t.hour), (0, 4))

    def test_33_no_partial_warning_drop_when_shift_hits_a_gap(self):
        mask = [t for t in self.mask if t != invented_time(21)]
        r = compare_week_shifts([invented_warning()], [invented_incident()], self.window, mask)
        self.assertIn({"week_offset": 1, "reason": "unequal_or_incomplete_exposure"}, r["rejected_rotations"])
        self.assertEqual(len(r["reference_patterns"]), 5)

    def test_34_identical_shift_patterns_are_not_extra_trials(self):
        window = replace(self.window, end=START + 6 * WEEK)
        ws = [invented_warning("W1", day=0), invented_warning("W2", day=21)]
        r = compare_week_shifts(ws, [invented_incident(day=22)], window,
                                [invented_time(d) for d in range(42)])
        self.assertEqual(len(r["reference_patterns"]), 1)
        reasons = [row["reason"] for row in r["rejected_rotations"]]
        self.assertEqual(reasons.count("identity_pattern"), 1)
        self.assertEqual(reasons.count("duplicate_pattern"), 2)

    def test_35_dense_weekly_stream_can_leave_no_valid_reference(self):
        ws = [invented_warning(f"W{i}", day=i * 7) for i in range(7)]
        r = compare_week_shifts(ws, [invented_incident()], self.window, self.mask)
        self.assertEqual(r["status"], "not_assessable")
        self.assertIsNone(r["rank_fraction_including_observed"])
        self.assertEqual(r["observed"]["warnings_in_window"], 7)

    def test_36_no_records_no_warnings_and_nonwhole_weeks(self):
        for ws, incidents in [([], [invented_incident()]), ([invented_warning()], [])]:
            r = compare_week_shifts(ws, incidents, self.window, self.mask)
            self.assertEqual(r["status"], "not_assessable")
            self.assertIsNone(r["rank_fraction_including_observed"])
        with self.assertRaises(ValueError):
            compare_week_shifts([], [], replace(self.window, end=self.window.end + timedelta(days=1)), [])

    def test_37_no_exposed_opportunity_is_not_a_missed_leak(self):
        r = self.timing(mask=[])
        self.assertEqual(r["incident_rows"][0]["status"], "no_approved_issue_opportunity")
        self.assertEqual(r["incident_rows"][0]["approved_issue_opportunities"], 0)
        self.assertEqual(r["eligible_confirmed_records"], 0)
        self.assertIsNone(r["record_association_share"])

    def test_38_report_level_exposure_is_visible(self):
        r = self.timing()
        self.assertEqual(r["incident_rows"][0]["approved_issue_opportunities"], 7)
        r = self.timing(mask=[t for t in self.mask if t != invented_time(14)])
        self.assertEqual(r["incident_rows"][0]["approved_issue_opportunities"], 6)

    def test_39_repeated_finding_is_not_two_distinct_leaks(self):
        ws = [invented_warning("W1", day=14), invented_warning("W2", day=21)]
        visits = [self.visit("V1", warning=ws[0]), self.visit("V2", warning=ws[1])]
        r = score_field_visits(ws, visits, self.window)
        self.assertEqual(r["warning_episode_findings"]["leak_found"], 2)
        self.assertEqual(r["distinct_warning_finding_incidents"], 1)
        self.assertEqual(r["repeat_warning_finding_incidents"],
                         {"INVENTED-I1": ["INVENTED-W1", "INVENTED-W2"]})
        self.assertEqual(r["warning_rows"][0]["finding_incident_ids"], ["INVENTED-I1"])


if __name__ == "__main__":
    unittest.main()
