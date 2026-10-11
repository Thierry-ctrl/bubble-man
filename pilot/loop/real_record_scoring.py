"""DRAFT — not frozen; needs human approval before any real records are seen.

Standalone preparation code. Tested ONLY with explicitly invented cases.
No file loaders, detector imports, onset estimates, or real-data evaluation entry point.
The accompanying SCORING-DRAFT.md defines the proposed interpretation and limitations.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
import hashlib
import math
import random

UTC = timezone.utc
WEEK = timedelta(days=7)
DRAFT_STATUS = "not frozen — needs human approval before any real records are seen"


@dataclass(frozen=True)
class Window:
    zone_id: str
    start: datetime
    end: datetime  # exclusive; also the record/visit observation cutoff


@dataclass(frozen=True)
class TimeRange:
    earliest: datetime
    latest: datetime  # inclusive; equal endpoints mean an exact timestamp


@dataclass(frozen=True)
class Warning:
    warning_id: str
    zone_id: str
    issued_at: datetime


@dataclass(frozen=True)
class Incident:
    incident_id: str
    zone_id: str
    first_report: TimeRange | None
    confirmed_at: datetime | None
    repair_completed_at: datetime | None = None
    pre_existing: bool = False


@dataclass(frozen=True)
class Visit:
    visit_id: str
    zone_id: str
    planned_at: datetime
    outcome: str  # leak_found / checked_nothing_found / incomplete_check / not_checked
    origin: str  # warning / random_control
    checked_at: datetime | None = None
    warning_id: str | None = None
    incident_ids: tuple[str, ...] = ()
    staff_minutes: float | None = None
    selection_probability: float | None = None


def _time(value):
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("An explicit UTC offset is required for every timestamp")
    return value.astimezone(UTC)


def _window(window):
    start, end = _time(window.start), _time(window.end)
    if not window.zone_id or start >= end:
        raise ValueError("Window needs a zone and start < end")
    if (not isinstance(window.start.tzinfo, timezone)
            or not isinstance(window.end.tzinfo, timezone)
            or window.start.utcoffset() != window.end.utcoffset()):
        raise ValueError("This draft supports one fixed local UTC offset, without DST")
    return start, end


def _unique(items, attr):
    ids = [getattr(item, attr) for item in items]
    if any(not isinstance(i, str) or not i.strip() for i in ids) or len(set(ids)) != len(ids):
        raise ValueError(f"Empty or duplicate {attr}")


def _warnings(warnings, window):
    _unique(warnings, "warning_id")
    issue_times = set()
    for warning in warnings:
        t = _time(warning.issued_at)
        if t in issue_times:
            raise ValueError("Duplicate issue time; evaluate each rule separately")
        issue_times.add(t)
        if warning.zone_id != window.zone_id:
            raise ValueError("Warning belongs to a different zone")


def _incident(incident):
    if incident.first_report is not None:
        first = _time(incident.first_report.earliest)
        last = _time(incident.first_report.latest)
        if first > last:
            raise ValueError("Reversed report-time bounds")
    else:
        first = None
    confirmation = _time(incident.confirmed_at) if incident.confirmed_at is not None else None
    repair = _time(incident.repair_completed_at) if incident.repair_completed_at is not None else None
    if first is not None and confirmation is not None and confirmation < first:
        raise ValueError("Confirmation precedes the earliest possible first report")
    if repair is not None and ((confirmation is not None and repair < confirmation)
                               or (first is not None and repair < first)):
        raise ValueError("Repair completion has an impossible ordering")


def _maximum_associations(graph):
    """Maximum one-to-one graph count; returns no arbitrarily chosen pipe attribution."""
    owner = {}

    def augment(warning_id, seen):
        for incident_id in sorted(graph.get(warning_id, ())):
            if incident_id in seen:
                continue
            seen.add(incident_id)
            if incident_id not in owner or augment(owner[incident_id], seen):
                owner[incident_id] = warning_id
                return True
        return False

    for warning_id in sorted(graph):
        augment(warning_id, set())
    return len(owner)


def score_timing(warnings, incidents, window, eligible_issue_times, lookback=WEEK):
    """Proposed retrospective timing associations, never true leak-onset detections.

    The exposure mask must be fixed from readings/operating information, before labels.
    All input warnings are retained in the rows; only the common exposure is compared.
    """
    warnings, incidents = tuple(warnings), tuple(incidents)
    start, end = _window(window)
    if not isinstance(lookback, timedelta) or lookback <= timedelta(0):
        raise ValueError("Lookback must be positive")
    _warnings(warnings, window)
    _unique(incidents, "incident_id")
    mask = {_time(t) for t in eligible_issue_times}
    if any(not start <= t < end for t in mask):
        raise ValueError("Exposure-mask time outside the evaluation window")

    incident_rows, eligible = [], []
    for incident in sorted(incidents, key=lambda i: i.incident_id):
        _incident(incident)
        opportunities = None
        if incident.zone_id != window.zone_id:
            status = "other_zone"
        elif incident.pre_existing:
            status = "pre_existing_record"
        elif incident.confirmed_at is None:
            status = "not_confirmed"
        elif _time(incident.confirmed_at) >= end:
            status = "confirmation_after_cutoff"
        elif incident.first_report is None:
            status = "missing_first_report"
        elif _time(incident.first_report.earliest) < start + lookback:
            status = "incomplete_pre_report_window"
        elif _time(incident.first_report.latest) >= end:
            status = "report_range_outside_cutoff"
        else:
            earliest, latest = (_time(incident.first_report.earliest),
                                _time(incident.first_report.latest))
            opportunities = sum(t < earliest and latest - t <= lookback and t + lookback < end
                                for t in mask)
            status = "eligible" if opportunities else "no_approved_issue_opportunity"
            if opportunities:
                eligible.append(incident)
        incident_rows.append({"incident_id": incident.incident_id, "status": status,
                              "approved_issue_opportunities": opportunities})

    guaranteed, possible, warning_rows = {}, {}, []
    for warning in sorted(warnings, key=lambda w: (_time(w.issued_at), w.warning_id)):
        t = _time(warning.issued_at)
        candidates, uncertain, leads = [], [], {}
        if not start <= t < end:
            status = "outside_evaluation_window"
        elif t not in mask:
            status = "outside_approved_exposure"
        elif t + lookback >= end:
            status = "incomplete_followup_window"
        else:
            for incident in eligible:
                earliest, latest = (_time(incident.first_report.earliest),
                                    _time(incident.first_report.latest))
                if t < earliest and latest - t <= lookback:
                    candidates.append(incident.incident_id)
                    leads[incident.incident_id] = [(earliest - t).total_seconds() / 3600,
                                                  (latest - t).total_seconds() / 3600]
                elif t < latest and earliest - t <= lookback:
                    uncertain.append(incident.incident_id)
            guaranteed[warning.warning_id] = tuple(candidates)
            possible[warning.warning_id] = tuple(candidates + uncertain)
            status = ("single_candidate_time_association" if len(candidates) == 1 else
                      "multiple_candidate_time_association" if candidates else
                      "uncertain_report_time_association" if uncertain else
                      "no_recorded_eligible_leak")
        warning_rows.append({"warning_id": warning.warning_id, "status": status,
                             "candidate_incidents": candidates,
                             "uncertain_candidates": uncertain,
                             "lead_to_first_report_hours": leads})

    count = _maximum_associations(guaranteed)
    per_incident = {i.incident_id: sorted(w for w, ids in guaranteed.items()
                                        if i.incident_id in ids) for i in eligible}
    for row in incident_rows:
        row["candidate_warnings"] = per_incident.get(row["incident_id"], [])
    return {"status": DRAFT_STATUS, "interpretation": "timing association, not causal detection",
            "warnings_in_window": sum(start <= _time(w.issued_at) < end for w in warnings),
            "warnings_in_timing_exposure": len(guaranteed),
            "eligible_confirmed_records": len(eligible),
            "maximum_unique_time_associations": count,
            "maximum_with_uncertain_report_times": _maximum_associations(possible),
            "record_association_share": count / len(eligible) if eligible else None,
            "warnings_with_multiple_candidates": sum(len(ids) > 1 for ids in guaranteed.values()),
            "records_with_multiple_candidate_warnings": sum(len(ids) > 1 for ids in per_incident.values()),
            "warning_rows": warning_rows, "incident_rows": incident_rows}


def _episode_outcome(visits):
    outcomes = {v.outcome for v in visits}
    if "leak_found" in outcomes:
        return "leak_found"
    if not outcomes or "not_checked" in outcomes or "incomplete_check" in outcomes:
        return "unknown"
    return "checked_nothing_found"


def _yield(outcomes):
    found = outcomes.count("leak_found")
    nothing = outcomes.count("checked_nothing_found")
    unknown = outcomes.count("unknown")
    return {"leak_found": found, "checked_nothing_found": nothing, "unknown": unknown,
            "completed_check_yield": found / (found + nothing) if found + nothing else None,
            "completion_share": (found + nothing) / len(outcomes) if outcomes else None}


def score_field_visits(warnings, visits, window):
    """Separate visit findings/workload. Unvisited warnings remain unknown."""
    warnings, visits = tuple(warnings), tuple(visits)
    start, end = _window(window)
    _warnings(warnings, window)
    _unique(visits, "visit_id")
    active = {w.warning_id: w for w in warnings if start <= _time(w.issued_at) < end}
    by_warning = {i: [] for i in active}
    controls, validated = [], []
    warning_days = {_time(w.issued_at).astimezone(window.start.tzinfo).date() for w in active.values()}
    for visit in visits:
        if visit.zone_id != window.zone_id or not start <= _time(visit.planned_at) < end:
            raise ValueError("Visit zone/time outside the evaluation window")
        if visit.outcome not in {"leak_found", "checked_nothing_found", "incomplete_check", "not_checked"}:
            raise ValueError("Unknown visit outcome")
        if visit.outcome == "not_checked":
            if visit.checked_at is not None or visit.incident_ids or visit.staff_minutes is not None:
                raise ValueError("An unchecked visit cannot claim findings or completed staff time")
        elif visit.checked_at is None:
            raise ValueError("Checked outcome needs an actual check timestamp")
        if visit.checked_at is not None and not _time(visit.planned_at) <= _time(visit.checked_at) < end:
            raise ValueError("Check precedes planning or is beyond the observation cutoff")
        if visit.outcome == "leak_found" and not visit.incident_ids:
            raise ValueError("A leak finding needs an auditable incident identifier")
        if visit.outcome != "leak_found" and visit.incident_ids:
            raise ValueError("Only a leak finding can carry incident identifiers")
        if (len(set(visit.incident_ids)) != len(visit.incident_ids)
                or any(not isinstance(i, str) or not i.strip() for i in visit.incident_ids)):
            raise ValueError("Empty or duplicate incident identifier within a visit")
        if visit.staff_minutes is not None and (isinstance(visit.staff_minutes, bool)
                or not isinstance(visit.staff_minutes, (int, float))
                or not math.isfinite(visit.staff_minutes) or visit.staff_minutes < 0):
            raise ValueError("Staff time must be finite and nonnegative")
        if visit.origin == "warning":
            if visit.warning_id not in active:
                raise ValueError("Visit links to no in-window warning")
            if _time(visit.planned_at) < _time(active[visit.warning_id].issued_at):
                raise ValueError("Warning investigation was planned before the warning was issuable")
            by_warning[visit.warning_id].append(visit)
        elif visit.origin == "random_control":
            probability = visit.selection_probability
            if (visit.warning_id is not None or isinstance(probability, bool)
                    or not isinstance(probability, (int, float))
                    or not math.isfinite(probability) or not 0 < probability <= 1):
                raise ValueError("Random control needs a selection probability and no warning link")
            if _time(visit.planned_at).astimezone(window.start.tzinfo).date() in warning_days:
                raise ValueError("Random control was assigned to a warning day")
            controls.append(visit)
        else:
            raise ValueError("Unknown visit origin")
        validated.append(visit)
    outcomes = {i: _episode_outcome(vs) for i, vs in sorted(by_warning.items())}
    findings = {i: sorted({incident for visit in vs for incident in visit.incident_ids})
                for i, vs in by_warning.items()}
    incident_episodes = {}
    for warning_id, ids in findings.items():
        for incident_id in ids:
            incident_episodes.setdefault(incident_id, []).append(warning_id)
    months = {}
    for warning in active.values():
        month = _time(warning.issued_at).astimezone(window.start.tzinfo).strftime("%Y-%m")
        months[month] = months.get(month, 0) + 1
    known_minutes = [v.staff_minutes for v in validated if v.staff_minutes is not None]
    return {"status": DRAFT_STATUS, "warning_investigation_episodes": len(active),
            "warning_visits": sum(v.origin == "warning" for v in validated),
            "control_visits": len(controls), "warnings_per_calendar_month": dict(sorted(months.items())),
            "warning_episode_findings": _yield(list(outcomes.values())),
            "control_visit_findings": _yield([_episode_outcome([v]) for v in controls]),
            "distinct_warning_finding_incidents": len(incident_episodes),
            "repeat_warning_finding_incidents": {i: sorted(ids) for i, ids in sorted(incident_episodes.items())
                                                 if len(ids) > 1},
            "distinct_control_finding_incidents": len({i for v in controls for i in v.incident_ids}),
            "staff_minutes_recorded": sum(known_minutes) if known_minutes else None,
            "visits_missing_staff_minutes": sum(v.staff_minutes is None for v in validated),
            "warning_rows": [{"warning_id": i, "field_outcome": o,
                              "finding_incident_ids": findings[i],
                              "visit_ids": sorted(v.visit_id for v in by_warning[i])}
                             for i, o in outcomes.items()]}


def select_control_nights(warnings, window, eligible_issue_times, count, seed):
    """INVENTED-case planning helper: uniform selection from approved no-warning days.

    Does not take incident records. A live trial needs a separately approved online plan.
    """
    start, end = _window(window)
    warnings = tuple(warnings)
    _warnings(warnings, window)
    dates = {_time(w.issued_at).astimezone(window.start.tzinfo).date()
             for w in warnings if start <= _time(w.issued_at) < end}
    pool = sorted({_time(t) for t in eligible_issue_times})
    if any(not start <= t < end for t in pool):
        raise ValueError("Control calendar extends outside the window")
    if len({t.astimezone(window.start.tzinfo).date() for t in pool}) != len(pool):
        raise ValueError("Control calendar must contain at most one issue time per local day")
    pool = [t for t in pool if t.astimezone(window.start.tzinfo).date() not in dates]
    if isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= len(pool):
        raise ValueError("Requested control count exceeds its eligible pool")
    selected = sorted(random.Random(seed).sample(pool, count))
    digest = hashlib.sha256("\n".join(t.isoformat() for t in pool).encode()).hexdigest()
    return {"status": DRAFT_STATUS, "population": len(pool), "count": count, "seed": seed,
            "inclusion_probability": count / len(pool) if pool else None,
            "pool_sha256": digest, "selected_issue_times": selected}


def compare_week_shifts(warnings, incidents, window, eligible_issue_times, lookback=WEEK):
    """Descriptive whole-week rotations on identical complete exposure; NOT a p-value.

    Reject a whole rotation if ANY shifted warning falls outside common exposure. No
    warning is silently dropped. Repeating/identity patterns are reported separately.
    """
    start, end = _window(window)
    weeks, remainder = divmod(end - start, WEEK)
    if remainder or weeks < 2:
        raise ValueError("Shift window must contain an integer number of at least two weeks")
    warnings, incidents, mask = tuple(warnings), tuple(incidents), tuple(eligible_issue_times)
    observed = score_timing(warnings, incidents, window, mask, lookback)
    exposed = {row["warning_id"] for row in observed["warning_rows"]
               if row["status"] in {"single_candidate_time_association",
                                    "multiple_candidate_time_association",
                                    "uncertain_report_time_association",
                                    "no_recorded_eligible_leak"}}
    core = tuple(w for w in warnings if w.warning_id in exposed)
    if not core or not observed["eligible_confirmed_records"]:
        return {"status": "not_assessable", "draft_status": DRAFT_STATUS,
                "reason": "no exposed warnings or eligible confirmed records", "reference_patterns": [],
                "rank_fraction_including_observed": None, "observed": observed}
    duration = end - start
    original = tuple(sorted(_time(w.issued_at) for w in core))
    seen = {original}
    patterns, rejected = [], []
    for offset in range(1, weeks):
        shifted = tuple(replace(w, issued_at=start + ((_time(w.issued_at) - start + offset * WEEK) % duration))
                        for w in core)
        signature = tuple(sorted(_time(w.issued_at) for w in shifted))
        if signature == original:
            rejected.append({"week_offset": offset, "reason": "identity_pattern"})
            continue
        if signature in seen:
            rejected.append({"week_offset": offset, "reason": "duplicate_pattern"})
            continue
        seen.add(signature)
        result = score_timing(shifted, incidents, window, mask, lookback)
        if result["warnings_in_timing_exposure"] != len(core):
            rejected.append({"week_offset": offset, "reason": "unequal_or_incomplete_exposure"})
            continue
        patterns.append({"week_offset": offset, "warning_count": len(core),
                         "issued_at": list(signature),
                         "maximum_unique_time_associations": result["maximum_unique_time_associations"]})
    actual = observed["maximum_unique_time_associations"]
    as_good = sum(p["maximum_unique_time_associations"] >= actual for p in patterns)
    return {"status": "descriptive_only" if patterns else "not_assessable",
            "draft_status": DRAFT_STATUS, "formal_p_value": None,
            "observed": observed, "shifted_warning_count": len(core),
            "reference_patterns": patterns, "rejected_rotations": rejected,
            "patterns_at_least_as_high": as_good,
            "rank_fraction_including_observed": (1 + as_good) / (1 + len(patterns)) if patterns else None,
            "limitations": "circular boundary, seasonality and non-exchangeability; no causal or significance claim"}
