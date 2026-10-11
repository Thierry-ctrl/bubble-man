"""Standalone DRAFT storage accounting; checks use INVENTED data only.

No file loader, detector imports or integration with the frozen pilot tools.
Inputs are explicit interval-mean net boundary flow (m3/h), endpoint water
depths (m) and approved monotone depth/volume tables (m, m3). Outputs are
withdrawals plus losses, never a leak diagnosis. See STORAGE-DESIGN.md.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math
from typing import Mapping, Optional, Sequence, Tuple

DRAFT_STATUS = "draft; invented-case checks only; not integrated or field validated"


def _finite(value):
    try:
        return not isinstance(value, bool) and math.isfinite(value)
    except (TypeError, ValueError, OverflowError):
        return False


def _utc(value):
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware datetimes")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class VolumeCurve:
    """Approved piecewise-linear depth (m) / stored-volume (m3) relationship."""

    depths_m: Tuple[float, ...]
    volumes_m3: Tuple[float, ...]

    def __post_init__(self):
        # Freeze a caller's lists too, so later mutation cannot change geometry.
        object.__setattr__(self, "depths_m", tuple(self.depths_m))
        object.__setattr__(self, "volumes_m3", tuple(self.volumes_m3))
        if len(self.depths_m) != len(self.volumes_m3) or len(self.depths_m) < 2:
            raise ValueError("geometry needs at least two paired depths and volumes")
        for values in (self.depths_m, self.volumes_m3):
            if any(not _finite(x) or x < 0 for x in values):
                raise ValueError("geometry values must be finite and nonnegative")
            if any(b <= a for a, b in zip(values, values[1:])):
                raise ValueError("geometry depths and volumes must strictly increase")

    @classmethod
    def constant_area(cls, area_m2, min_depth_m, max_depth_m, volume_at_min_m3=0):
        """Vertical rectangular/cylindrical section, with an explicit depth range."""
        if not _finite(area_m2) or area_m2 <= 0:
            raise ValueError("area must be finite and positive")
        if not all(_finite(x) for x in (min_depth_m, max_depth_m, volume_at_min_m3)):
            raise ValueError("depth range and minimum volume must be finite")
        return cls((min_depth_m, max_depth_m),
                   (volume_at_min_m3,
                    volume_at_min_m3 + area_m2 * (max_depth_m - min_depth_m)))

    @classmethod
    def vertical_cylinder(cls, diameter_m, height_m):
        if not _finite(diameter_m) or diameter_m <= 0:
            raise ValueError("diameter must be finite and positive")
        try:
            area = math.pi * (diameter_m / 2) ** 2
        except OverflowError as error:
            raise ValueError("diameter produces nonfinite geometry") from error
        return cls.constant_area(area, 0, height_m)

    def volume(self, depth_m):
        if (not _finite(depth_m) or depth_m < self.depths_m[0]
                or depth_m > self.depths_m[-1]):
            raise ValueError("depth outside approved geometry or not finite")
        i = min(bisect_right(self.depths_m, depth_m) - 1, len(self.depths_m) - 2)
        fraction = (depth_m - self.depths_m[i]) / (self.depths_m[i + 1] - self.depths_m[i])
        return self.volumes_m3[i] + fraction * (self.volumes_m3[i + 1] - self.volumes_m3[i])


@dataclass(frozen=True)
class LevelReading:
    at: datetime
    depth_m: Optional[float]
    usable: bool = True
    error_bound_m: Optional[float] = None
    received_at: Optional[datetime] = None


@dataclass(frozen=True)
class FlowInterval:
    start: datetime
    end: datetime
    mean_net_inflow_m3_h: Optional[float]
    usable: bool = True
    error_bound_m3_h: Optional[float] = None
    received_at: Optional[datetime] = None


@dataclass(frozen=True)
class StorageCorrection:
    start: datetime
    end: datetime
    not_before: datetime
    status: str
    mean_net_inflow_m3_h: Optional[float]
    tank_changes_m3: Tuple[Tuple[str, float], ...]
    mean_storage_change_m3_h: Optional[float]
    mean_withdrawals_and_losses_m3_h: Optional[float]
    bounded_range_m3_h: Optional[Tuple[float, float]]
    notes: Tuple[str, ...]


def _received(value, measurement_end):
    if value is None:
        return measurement_end
    value = _utc(value)
    if value < measurement_end:
        raise ValueError("received_at cannot precede measurement time/interval end")
    return value


def correct_storage(
    intervals: Sequence[FlowInterval],
    curves: Mapping[str, VolumeCurve],
    levels: Mapping[str, Sequence[LevelReading]],
    *,
    expected_interval: timedelta,
    inventory_confirmed: bool,
) -> Tuple[StorageCorrection, ...]:
    """Subtract sum(V_end - V_start)/duration from signed boundary inflow.

    Exact timestamp endpoints only; no temporal interpolation, clamping,
    clipping, gap filling or partial-tank correction. Unknown uncertainty
    yields a nominal number with no bounded range. Supplied absolute error
    bounds are combined conservatively, conditional on exact geometry and
    synchronized time. Structural errors raise ValueError; unusable data
    yield unassessable rows. not_before is a lower bound on availability.
    """
    if not isinstance(expected_interval, timedelta) or expected_interval <= timedelta(0):
        raise ValueError("expected_interval must be a positive timedelta")
    if not isinstance(inventory_confirmed, bool):
        raise ValueError("inventory_confirmed must be an explicit boolean")
    if any(not isinstance(k, str) or not k.strip() for k in curves):
        raise ValueError("tank IDs must be nonempty strings")
    if any(not isinstance(c, VolumeCurve) for c in curves.values()):
        raise ValueError("every tank needs an approved VolumeCurve")
    if set(levels) - set(curves):
        raise ValueError("readings include tanks not declared in the geometry inventory")

    indexed = {}
    for tank_id in curves:
        rows = {}
        for reading in levels.get(tank_id, ()):
            at = _utc(reading.at)
            if at in rows:
                raise ValueError("duplicate level timestamp for " + tank_id)
            if not isinstance(reading.usable, bool):
                raise ValueError("usable must be a boolean")
            _received(reading.received_at, at)
            rows[at] = reading
        indexed[tank_id] = rows

    output = []
    previous_end = None
    for interval in intervals:
        start, end = _utc(interval.start), _utc(interval.end)
        if end - start != expected_interval:
            raise ValueError("flow interval must equal expected_interval")
        if previous_end is not None and start < previous_end:
            raise ValueError("flow intervals must be ordered, distinct and nonoverlapping")
        if not isinstance(interval.usable, bool):
            raise ValueError("usable must be a boolean")
        notes = []
        if previous_end is not None and start > previous_end:
            notes.append("gap_before_interval; no rows manufactured")
        previous_end = end
        available = _received(interval.received_at, end)
        problems = []
        changes, lower_changes, upper_changes = [], [], []
        bounded = interval.error_bound_m3_h is not None
        flow = interval.mean_net_inflow_m3_h
        if not inventory_confirmed:
            problems.append("internal_tank_inventory_not_confirmed")
        if not interval.usable or not _finite(flow):
            problems.append("unusable_or_missing_boundary_flow")
        if (interval.error_bound_m3_h is not None and
                (not _finite(interval.error_bound_m3_h) or interval.error_bound_m3_h < 0)):
            problems.append("invalid_flow_error_bound")

        for tank_id, curve in curves.items():
            first, last = indexed[tank_id].get(start), indexed[tank_id].get(end)
            if first is None or last is None:
                problems.append(tank_id + ":missing_exact_endpoint")
                continue
            available = max(available, _received(first.received_at, start),
                            _received(last.received_at, end))
            if not first.usable or not last.usable:
                problems.append(tank_id + ":flagged_endpoint")
                continue
            try:
                change = curve.volume(last.depth_m) - curve.volume(first.depth_m)
                changes.append((tank_id, change))
                if any(x is not None and (not _finite(x) or x < 0) for x in
                       (first.error_bound_m, last.error_bound_m)):
                    problems.append(tank_id + ":invalid_level_error_bound")
                    continue
                first_range = (None if first.error_bound_m is None else
                               (curve.volume(first.depth_m - first.error_bound_m),
                                curve.volume(first.depth_m + first.error_bound_m)))
                last_range = (None if last.error_bound_m is None else
                              (curve.volume(last.depth_m - last.error_bound_m),
                               curve.volume(last.depth_m + last.error_bound_m)))
                if first_range is None or last_range is None:
                    bounded = False
                    continue
                lower_changes.append(last_range[0] - first_range[1])
                upper_changes.append(last_range[1] - first_range[0])
            except ValueError:
                problems.append(tank_id + ":endpoint_or_error_range_outside_geometry")

        if problems:
            output.append(StorageCorrection(start, end, available, "unassessable", flow,
                          tuple(changes), None, None, None, tuple(notes + problems)))
            continue
        hours = expected_interval.total_seconds() / 3600
        bounds = None
        if not bounded:
            notes.append("measurement_uncertainty_unquantified")
        try:
            rate = math.fsum(change for _, change in changes) / hours
            corrected = flow - rate
            if bounded:
                bounds = (flow - interval.error_bound_m3_h - math.fsum(upper_changes) / hours,
                          flow + interval.error_bound_m3_h - math.fsum(lower_changes) / hours)
        except OverflowError:
            rate, corrected = math.inf, math.nan
        if (not _finite(rate) or not _finite(corrected) or
                (bounds is not None and any(not _finite(x) for x in bounds))):
            output.append(StorageCorrection(start, end, available, "unassessable", flow,
                          tuple(changes), None, None, None,
                          tuple(notes + ["nonfinite_calculation"])))
            continue
        if corrected < 0:
            notes.append("negative_corrected_flow; check boundary, timing and measurement")
        output.append(StorageCorrection(start, end, available, "ok", flow, tuple(changes),
                      rate, corrected, bounds, tuple(notes)))
    return tuple(output)
