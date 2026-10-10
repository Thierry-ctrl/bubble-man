"""Validate a utility export (format in PILOT-READINESS.md) and convert it to the input of the
frozen night-flow method: one zone's NET INFLOW, m3/h, on a 30-minute grid, local standard
time, columns Timestamp,Value. Detection rules are NOT touched here.

Usage: python3 convert_utility_data.py EXPORT_DIR OUT_DIR [--accept-estimated]
                                       [--allow-uncorrected-storage]

What it does, in order:
  1. checks files and columns; parses timestamps (an explicit UTC offset is required);
  2. converts each meter to m3/h (L/s, m3/h, m3/s; interval volumes; cumulative totals);
  3. treats readings flagged estimated/fault/missing, duplicates, resets and negative rates
     as MISSING (never repaired or interpolated);
  4. averages into 30-minute bins - a bin is kept only if every expected reading is present;
  5. net inflow = inlets + transfers in - outlets - transfers out (missing if any part is);
  6. writes the series from the first local midnight, plus conversion-report.json with every
     problem found and the suitability flags for the night-flow method.
Not done (see pilot/SOFTWARE-GAPS.md): storage correction, supply-schedule handling,
multi-zone networks, daylight-saving time, live operation.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd

RATE_UNITS = {'m3/h': 1.0, 'l/s': 3.6, 'm3/s': 3600.0}
VOLUME_UNITS = {'m3': 1.0, 'l': 0.001}
VALUE_TYPES = {'instantaneous_rate', 'interval_average_rate', 'interval_volume', 'cumulative_total'}
SIGN = {'inlet': 1, 'transfer_in': 1, 'outlet': -1, 'transfer_out': -1}
NEED = {
    'flow_readings': ['meter_id', 'timestamp', 'value', 'unit', 'quality'],
    'meters': ['meter_id', 'role', 'zone_id', 'value_type', 'unit', 'interval_minutes', 'timestamp_marks'],
    'zone': ['zone_id', 'supply_regime', 'internal_storage', 'storage_level_meter',
             'boundary_valves_confirmed_closed', 'local_time_zone'],
}
OPTIONAL = {'operating_log': ['event_id', 'start', 'end', 'event_type', 'assets', 'description'],
            'repair_records': ['record_id', 'first_report_time', 'report_source', 'confirmed_time',
                               'repair_start_time', 'repair_completed_time', 'location']}


class ExportError(Exception):
    pass


def find(d: Path, stem: str):
    hits = sorted(d.glob(f'*{stem}.csv'))
    return hits[0] if hits else None


def load(d: Path, stem: str, cols, required=True):
    f = find(d, stem)
    if f is None:
        if required:
            raise ExportError(f'missing file *{stem}.csv')
        return None
    t = pd.read_csv(f, dtype=str, keep_default_na=False)
    t.columns = [c.strip().lower() for c in t.columns]
    miss = [c for c in cols if c not in t.columns]
    if miss:
        raise ExportError(f'{f.name}: missing columns {miss}')
    return t


def parse_offset(text: str) -> pd.Timedelta:
    m = re.fullmatch(r'(?:UTC)?\s*([+-])(\d{2}):?(\d{2})', text.strip(), re.I)
    if not m:
        raise ExportError(f'local_time_zone must look like UTC+02:00, got {text!r}')
    sign = 1 if m.group(1) == '+' else -1
    return sign * pd.Timedelta(hours=int(m.group(2)), minutes=int(m.group(3)))


def to_local(ts: pd.Series, offset: pd.Timedelta, what: str) -> pd.Series:
    """Explicit-offset ISO timestamps -> naive local standard time (offset fixed, no DST)."""
    if (~ts.str.contains(r'(?:Z|[+-]\d{2}:?\d{2})$', regex=True)).any():
        raise ExportError(f'{what}: every timestamp needs an explicit UTC offset, e.g. 2026-03-02T02:15:00+02:00')
    utc = pd.to_datetime(ts, utc=True, errors='coerce')
    if utc.isna().any():
        raise ExportError(f'{what}: {int(utc.isna().sum())} unparseable timestamps')
    return (utc + offset).dt.tz_localize(None)


def meter_rate(r: pd.DataFrame, m: pd.Series, accept_estimated: bool, problems: list) -> pd.Series:
    """One meter -> m3/h, indexed by the START of the interval each value describes."""
    mid, vt, unit = m.meter_id, m.value_type, m.unit.strip().lower()
    step = pd.Timedelta(minutes=int(m.interval_minutes))
    if vt not in VALUE_TYPES:
        raise ExportError(f'{mid}: value_type {vt!r} not one of {sorted(VALUE_TYPES)}')
    if set(r.unit.str.strip().str.lower()) - {unit}:
        raise ExportError(f'{mid}: readings use units {sorted(set(r.unit))}, meters.csv says {m.unit}')
    r = r.sort_values('t')
    dup = r.t.duplicated(keep=False)
    if dup.any():
        problems.append(f'{mid}: {int(dup.sum())} readings share a timestamp - treated as missing')
    r = r[~dup]
    off_grid = ((r.t - r.t.dt.floor(step)) != pd.Timedelta(0))
    if off_grid.any():
        problems.append(f'{mid}: {int(off_grid.sum())} timestamps not on the {m.interval_minutes}-minute grid - treated as missing')
        r = r[~off_grid]
    q = r.quality.str.strip().str.lower()
    good = q.eq('ok') | (q.eq('estimated') & accept_estimated)
    bad_counts = q[~good].value_counts().to_dict()
    if bad_counts:
        problems.append(f'{mid}: readings not used because of quality flag: {bad_counts}')
    v = pd.to_numeric(r.value, errors='coerce').where(good.values)
    if v.isna().sum() > (~good).sum():
        problems.append(f'{mid}: {int(v.isna().sum() - (~good).sum())} non-numeric values - treated as missing')
    s = pd.Series(v.values, index=pd.DatetimeIndex(r.t.values))
    grid = pd.date_range(s.index.min(), s.index.max(), freq=step)
    s = s.reindex(grid)
    if vt in ('instantaneous_rate', 'interval_average_rate'):
        if unit not in RATE_UNITS:
            raise ExportError(f'{mid}: rate unit {m.unit!r} not one of {sorted(RATE_UNITS)}')
        rate = s * RATE_UNITS[unit]
        if vt == 'interval_average_rate' and m.timestamp_marks == 'interval_end':
            rate.index = rate.index - step
    else:
        if unit not in VOLUME_UNITS:
            raise ExportError(f'{mid}: volume unit {m.unit!r} not one of {sorted(VOLUME_UNITS)}')
        vol = s * VOLUME_UNITS[unit]
        if vt == 'cumulative_total':
            d = vol.diff()                          # volume over (t - step, t]
            resets = int((d < 0).sum())
            if resets:
                problems.append(f'{mid}: {resets} decreases in the cumulative total (reset/rollover) - treated as missing')
            d[d < 0] = np.nan
            rate = d / (step / pd.Timedelta(hours=1))
            rate.index = rate.index - step          # describes the interval that ends at t
            rate = rate.iloc[1:]
        else:                                       # interval_volume
            rate = vol / (step / pd.Timedelta(hours=1))
            if m.timestamp_marks == 'interval_end':
                rate.index = rate.index - step
    neg = int((rate < 0).sum())
    if neg:
        problems.append(f'{mid}: {neg} negative flow rates - treated as missing')
        rate[rate < 0] = np.nan
    return rate


def to_30min(rate: pd.Series, interval_min: int) -> pd.Series:
    if 30 % interval_min:
        raise ExportError(f'interval {interval_min} min does not divide 30 minutes')
    per = 30 // interval_min
    g = rate.groupby(rate.index.floor('30min'))
    out = g.mean().where(g.count() == per)
    return out


def convert(export: Path, out: Path, accept_estimated=False, allow_storage=False) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    problems, flags = [], []
    fr = load(export, 'flow_readings', NEED['flow_readings'])
    mt = load(export, 'meters', NEED['meters'])
    zn = load(export, 'zone', NEED['zone'])
    if len(zn) != 1:
        raise ExportError('zone.csv must describe exactly one zone')
    z = zn.iloc[0]
    offset = parse_offset(z.local_time_zone)
    bad_roles = set(mt.role) - set(SIGN)
    if bad_roles:
        raise ExportError(f'meters.csv: unknown roles {sorted(bad_roles)}; use {sorted(SIGN)}')
    if not (mt.role.isin(['inlet', 'transfer_in'])).any():
        raise ExportError('no inlet meter listed')
    unknown = set(fr.meter_id) - set(mt.meter_id)
    if unknown:
        raise ExportError(f'readings for meters not in meters.csv: {sorted(unknown)}')
    fr['t'] = to_local(fr.timestamp, offset, 'flow_readings')

    # ---- suitability for the night-flow method -------------------------------------------
    regime = z.supply_regime.strip().lower()
    if regime != 'continuous':
        flags.append(f'UNSUITABLE for the current night-flow method: supply_regime = {z.supply_regime!r}. '
                     'Night refilling of household tanks after interruptions looks like leakage.')
    storage = z.internal_storage.strip().lower()
    if storage not in ('', 'none', 'no'):
        msg = ('zone has internal storage; its fill/draw changes net inflow and is NOT corrected here '
               f'(level meter: {z.storage_level_meter or "none listed"})')
        if not allow_storage:
            raise ExportError(msg + '. Re-run with --allow-uncorrected-storage only to inspect the data.')
        flags.append('CAUTION: ' + msg)
    if z.boundary_valves_confirmed_closed.strip().lower() != 'yes':
        flags.append('CAUTION: boundary valves not confirmed closed - unmetered flow may cross the boundary')

    # ---- per-meter conversion --------------------------------------------------------------
    parts, per_meter = [], {}
    for m in mt.itertuples():
        r = fr[fr.meter_id == m.meter_id]
        if r.empty:
            raise ExportError(f'{m.meter_id}: listed in meters.csv but has no readings')
        rate = meter_rate(r, pd.Series(m._asdict()), accept_estimated, problems)
        b = to_30min(rate, int(m.interval_minutes))
        parts.append(SIGN[m.role] * b)
        per_meter[m.meter_id] = {'role': m.role, 'readings': int(len(r)),
                                 'first': str(r.t.min()), 'last': str(r.t.max()),
                                 'complete_30min_bins': int(b.notna().sum()), 'bins': int(len(b)),
                                 'median_m3h': round(float(b.median()), 2) if b.notna().any() else None}
    idx = parts[0].index
    for p in parts[1:]:
        idx = idx.union(p.index)
    net = sum(p.reindex(idx) for p in parts)            # NaN if any component missing
    start = idx.min().ceil('D') if idx.min() != idx.min().normalize() else idx.min()
    grid = pd.date_range(start, idx.max().floor('30min'), freq='30min')
    net = net.reindex(grid)
    if (net < 0).any():
        problems.append(f'net inflow negative in {int((net < 0).sum())} bins - kept, but check meter roles and transfers')
    pd.DataFrame({'Timestamp': net.index.strftime('%Y-%m-%d %H:%M:%S'), 'Value': net.round(3).values}) \
        .to_csv(out / 'zone_net_inflow_30min.csv', index=False)

    # ---- readiness for the frozen method --------------------------------------------------
    days = net.groupby(net.index.normalize()).apply(lambda x: int(x.notna().sum()) == 48)
    ready = {'days_covered': int(len(days)), 'complete_days': int(days.sum()),
             'share_of_30min_bins_present': round(float(net.notna().mean()), 3) if len(net) else 0.0,
             'first_14_days_complete': bool(len(days) >= 14 and days.iloc[:14].all()),
             'note': ('The frozen method needs about a year: days 1-14 complete to learn day types, '
                      '20 step values on days 9-28 for the threshold, and 300 step values from day 29.')}
    ready['likely_assessable_by_frozen_method'] = bool(ready['first_14_days_complete'] and ready['days_covered'] >= 337)

    # ---- optional logs: checked, not used by the detector ----------------------------------
    logs = {}
    ol = load(export, 'operating_log', OPTIONAL['operating_log'], required=False)
    if ol is not None:
        logs['operating_log'] = {'events': int(len(ol)), 'by_type': ol.event_type.value_counts().to_dict(),
                                 'note': 'listed for interpretation; the frozen rule does not read it'}
        to_local(ol.start, offset, 'operating_log.start')
    rr = load(export, 'repair_records', OPTIONAL['repair_records'], required=False)
    if rr is not None:
        T = {c: pd.to_datetime(rr[c].where(rr[c] != ''), utc=True, errors='coerce')
             for c in ('first_report_time', 'confirmed_time', 'repair_start_time', 'repair_completed_time')}
        order_bad = int(((T['confirmed_time'] < T['first_report_time']) |
                         (T['repair_completed_time'] < T['repair_start_time']) |
                         (T['repair_start_time'] < T['first_report_time'])).sum())
        logs['repair_records'] = {
            'records': int(len(rr)), 'with_first_report': int(T['first_report_time'].notna().sum()),
            'with_confirmation': int(T['confirmed_time'].notna().sum()),
            'with_repair_completed': int(T['repair_completed_time'].notna().sum()),
            'records_with_times_out_of_order': order_bad,
            'note': 'first report is NOT the leak onset; it is an upper bound on when the leak began'}
        if order_bad:
            problems.append(f'repair_records: {order_bad} records have times out of order')

    report = {'zone_id': z.zone_id, 'local_standard_time': z.local_time_zone, 'meters': per_meter,
              'problems': problems, 'suitability_flags': flags, 'readiness': ready, 'logs': logs,
              'output': 'zone_net_inflow_30min.csv (Timestamp,Value; m3/h; local standard time)'}
    (out / 'conversion-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('export'); ap.add_argument('out')
    ap.add_argument('--accept-estimated', action='store_true')
    ap.add_argument('--allow-uncorrected-storage', action='store_true')
    a = ap.parse_args()
    try:
        rep = convert(Path(a.export), Path(a.out), a.accept_estimated, a.allow_uncorrected_storage)
    except ExportError as e:
        sys.exit(f'EXPORT NOT ACCEPTED: {e}')
    print(json.dumps({k: rep[k] for k in ('meters', 'problems', 'suitability_flags', 'readiness')}, indent=2))
