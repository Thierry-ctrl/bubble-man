"""Descriptive night-flow accounting. No detector, repair reader or network access."""
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STEP1 = HERE.parent / 'step1-detectability'
FLOW = ROOT / 'data/yorkshire/N4_2016_2017.csv'
PROPS = HERE / 'source/DMA-property-count-2016-2017.csv'
START = pd.Timestamp('2016-04-01')
AMBIGUOUS = pd.Timestamp('2016-10-30 01:00')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def key(value):
    value = str(value).strip()
    if not value.isdigit():
        raise ValueError('DMA must be a numeric identifier')
    return str(int(value))


def share_bounds(flow_low, flow_high, use_low, use_high):
    """Feasible nonnegative residual shares across rectangular scenario ranges."""
    vals = (flow_low, flow_high, use_low, use_high)
    if not all(math.isfinite(x) for x in vals):
        raise ValueError('Ranges must be finite')
    if not (0 < flow_low <= flow_high and 0 <= use_low <= use_high):
        raise ValueError('Invalid flow/use interval')
    if flow_high < use_low:
        return None, None
    feasible_q_low = max(flow_low, use_low)
    lo = max(0.0, 1.0 - use_high / feasible_q_low)
    hi = 1.0 - use_low / flow_high
    return lo, hi


def components(households, businesses, household_rates, business_rates):
    if any(isinstance(x, bool) or not isinstance(x, (int, np.integer)) or x < 0
           for x in (households, businesses)):
        raise ValueError('Property counts must be nonnegative integers')
    for r in (household_rates, business_rates):
        if len(r) != 2 or not all(math.isfinite(x) for x in r) or not 0 <= r[0] <= r[1]:
            raise ValueError('Invalid rate range')
    hh = np.array(household_rates) * households / 1000
    nh = np.array(business_rates) * businesses / 1000
    return hh, nh, hh + nh


def hourly_from_quarters(quarters):
    """Four finite readings required, with no gap filling."""
    x = np.asarray(quarters, dtype=float).reshape(365, 24, 4)
    good = np.isfinite(x).all(axis=2)
    return np.where(good, x.mean(axis=2), np.nan)


def choose_hour(hours, dates, training_days=28, minimum=10):
    valid = np.isfinite(hours[:, :6]).all(axis=1)
    weekday = np.asarray(dates.dayofweek < 5)
    train = valid & weekday & (np.arange(365) < training_days)
    if train.sum() < minimum:
        raise ValueError('Insufficient complete training weekday nights')
    medians = np.median(hours[train, :6], axis=0)
    return int(np.argmin(medians)), train, medians


def property_rows(path, selected):
    t = pd.read_csv(path, dtype=str, keep_default_na=False)
    expected = ['DMA', 'Area', 'Number Of Household Properties', 'Number Of Non-Household Properties']
    if list(t.columns) != expected:
        raise ValueError('Unexpected property-count schema')
    t['dma'] = t.DMA.map(key)
    rows = []
    for dma in selected:
        g = t[t.dma == dma]
        if len(g) != 1 or g.iloc[0].Area.strip() != 'N4':
            raise ValueError('Need exactly one N4 property row per selected DMA')
        g = g.iloc[0]
        counts = [g[c].strip() for c in expected[2:]]
        if not all(x.isdigit() for x in counts):
            raise ValueError('Missing, negative or noninteger property count')
        rows.append({'dma': dma, 'area': 'N4', 'households': int(counts[0]),
                     'nonhouseholds': int(counts[1])})
    return rows


def load_quarters(path, selected):
    t = pd.read_csv(path, dtype={'DMA': str, 'Date': str, 'Time': str, 'Flow Validity Code': str})
    if list(t.columns) != ['DMA', 'Date', 'Time', 'Flow', 'Flow Validity Code']:
        raise ValueError('Unexpected flow schema')
    total_rows = len(t)
    t['dma'] = t.DMA.map(key)
    t = t[t.dma.isin(selected)].copy()
    t['ts'] = pd.to_datetime(t.Date + ' ' + t.Time, format='%d/%m/%Y %H:%M:%S', errors='coerce')
    if t.ts.isna().any():
        raise ValueError('Unparseable selected-zone timestamp')
    f = pd.to_numeric(t.Flow, errors='coerce')
    valid = t['Flow Validity Code'].str.strip().eq('V') & np.isfinite(f) & (f >= 0)
    t['v'] = np.where(valid, f * 3.6, np.nan)
    duplicate = t.duplicated(['dma', 'ts'], keep=False)
    duplicates = int(duplicate.sum())
    t = t[~duplicate].copy()
    ambiguous = (t.ts >= AMBIGUOUS) & (t.ts < AMBIGUOUS + pd.Timedelta(hours=1))
    t.loc[ambiguous, 'v'] = np.nan
    grid = pd.date_range(START, periods=365 * 96, freq='15min')
    arrays = {dma: t[t.dma == dma].set_index('ts').v.reindex(grid).to_numpy() for dma in selected}
    return arrays, {'source_rows': total_rows, 'selected_rows_after_duplicate_removal': len(t),
                    'selected_duplicate_rows_removed': duplicates,
                    'selected_ambiguous_autumn_readings_set_missing': int(ambiguous.sum())}


def main():
    out = HERE / 'run'
    if out.exists():
        raise FileExistsError('Refuse to overwrite an existing accounting run')
    prepared = json.loads((STEP1 / 'run/prepared.json').read_text())
    for name, expected in prepared['input_hashes'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('Step-1 protected input changed: ' + name)
    protected = {name: sha(ROOT / name) for name in prepared['input_hashes']}
    for p in STEP1.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and '_scratch' not in p.parts:
            protected[str(p.relative_to(ROOT))] = sha(p)
    a = json.loads((HERE / 'assumptions.json').read_text())
    selected = [x['dma'] for x in prepared['selected']]
    allowed_csv = {FLOW.resolve(), PROPS.resolve()}
    csv_reads = set()

    def guard(event, args):
        if event == 'open' and isinstance(args[0], (str, bytes)):
            path = Path(args[0]).resolve()
            mode = args[1]
            reading = mode is None or ('r' in mode or '+' in mode)
            if reading and path.suffix.lower() == '.csv':
                if path not in allowed_csv:
                    raise PermissionError('Unexpected CSV read during accounting: ' + str(path))
                csv_reads.add(str(path.relative_to(ROOT)))

    sys.addaudithook(guard)
    props = property_rows(PROPS, selected)
    arrays, reader_report = load_quarters(FLOW, selected)
    dates = pd.date_range(START, periods=365, freq='D')
    day = np.arange(365)
    weekday = np.asarray(dates.dayofweek < 5)
    candidate = (day >= a['training_days']) & weekday
    results, nights, selections, monthly = [], [], [], []
    for p, saved in zip(props, prepared['selected']):
        dma = p['dma']
        raw = arrays[dma]
        half = raw.reshape(-1, 2)
        finite_half = int(np.isfinite(half).all(axis=1).sum())
        if finite_half != saved['finite_bins']:
            raise ValueError('Step-1 completeness cross-check failed')
        h = hourly_from_quarters(raw)
        complete = np.isfinite(h[:, :6]).all(axis=1)
        step1_min = np.min((h[:, :5] + h[:, 1:6]) / 2, axis=1)
        step1_mask = complete & (day >= 28)
        ref = float(np.median(step1_min[step1_mask]))
        if not (np.isclose(ref, saved['reference_m3h'], rtol=0, atol=1e-8)
                and step1_mask.sum() == saved['reference_complete_nights']):
            raise ValueError('Step-1 reference cross-check failed')
        hour, train, medians = choose_hour(h, dates, a['training_days'], a['minimum_training_weekdays'])
        for i, median in enumerate(medians):
            selections.append({'dma': dma, 'hour_start': i, 'training_median_m3h': median,
                               'complete_training_weekdays': int(train.sum()), 'selected': i == hour})
        use = candidate & complete
        q = h[use, hour]
        q10, q50, q90 = np.quantile(q, a['quantiles'])
        hh, nh, total = components(p['households'], p['nonhouseholds'],
                                   a['household_l_property_h'], a['nonhousehold_l_property_h'])
        low, high = share_bounds(q50, q50, *total)
        wide_low, wide_high = share_bounds(q10, q90, *total)
        erasure = max(0.0, float(q50 - total[1]))
        results.append(dict(p, fixed_hour_start=hour, complete_training_weekdays=int(train.sum()),
            candidate_weekday_nights=int(candidate.sum()), complete_weekday_nights=int(use.sum()),
            missing_weekday_nights=int((candidate & ~complete).sum()),
            observed_q10_m3h=q10, observed_median_m3h=q50, observed_q90_m3h=q90,
            household_low_m3h=hh[0], household_high_m3h=hh[1],
            nonhousehold_low_m3h=nh[0], nonhousehold_high_m3h=nh[1],
            legitimate_use_low_m3h=total[0], legitimate_use_high_m3h=total[1],
            signed_residual_low_m3h=q50 - total[1], signed_residual_high_m3h=q50 - total[0],
            conditional_plausible_share_low=low, conditional_plausible_share_high=high,
            variation_envelope_share_low=wide_low, variation_envelope_share_high=wide_high,
            high_use_exceeds_median=bool(total[1] > q50),
            nights_high_use_exceeds_flow=int((total[1] > q).sum()),
            nights_low_use_exceeds_flow=int((total[0] > q).sum()),
            additional_business_use_erasing_high_rate_residual_m3h=erasure,
            additional_business_use_per_property_lph=erasure * 1000 / p['nonhouseholds'] if p['nonhouseholds'] else None,
            step1_reference_m3h=ref, step1_reference_complete_nights=int(step1_mask.sum()),
            fixed_median_vs_step1_reference_pct=100 * (q50 / ref - 1)))
        for d in range(365):
            if not candidate[d]:
                continue
            value = h[d, hour] if complete[d] else None
            nights.append({'dma': dma, 'date': dates[d].strftime('%Y-%m-%d'), 'fixed_hour_start': hour,
                           'complete_00_06': bool(complete[d]), 'flow_m3h': value})
        for month in sorted(set(dates[use].strftime('%Y-%m'))):
            mask = use & (dates.strftime('%Y-%m') == month)
            monthly.append({'dma': dma, 'month': month, 'complete_weekday_nights': int(mask.sum()),
                            'median_m3h': float(np.median(h[mask, hour]))})
    out.mkdir()
    for name, rows in [('properties', props), ('hour-selection', selections), ('nights', nights),
                       ('monthly', monthly), ('summary', results)]:
        pd.DataFrame(rows).to_csv(out / (name + '.csv'), index=False)
    # Guarded calculation ends; hash checks below also read protected earlier CSV files.
    allowed_csv.update((ROOT / n).resolve() for n in protected if n.lower().endswith('.csv'))
    calculation_csv_reads = sorted(csv_reads)
    allowed_csv.update(p.resolve() for p in out.glob('*.csv'))
    after = {name: sha(ROOT / name) for name in protected}
    if protected != after:
        raise ValueError('An earlier protected file changed')
    record = {'finished_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
              'numpy': np.__version__, 'pandas': pd.__version__, 'selected': selected,
              'reader_report': reader_report, 'calculation_csv_reads': calculation_csv_reads,
              'guard_scope': 'CSV reads during property/flow calculation; before/after hashes separately read protected files',
              'protected_hashes_before_and_after_identical': protected,
              'inputs': {str(p.relative_to(ROOT)): sha(p) for p in
                         [FLOW, PROPS, HERE / 'METHOD.md', HERE / 'assumptions.json', Path(__file__)]},
              'outputs': {p.name: sha(p) for p in out.glob('*.csv')},
              'detector_imported_or_run': False, 'repair_records_opened': False,
              'interpretation': 'Conditional plausible leakage share; not measured loss or confidence intervals'}
    (out / 'provenance.json').write_text(json.dumps(record, indent=2) + '\n')
    print(pd.DataFrame(results)[['dma', 'households', 'nonhouseholds', 'fixed_hour_start',
        'observed_median_m3h', 'legitimate_use_low_m3h', 'legitimate_use_high_m3h',
        'conditional_plausible_share_low', 'conditional_plausible_share_high',
        'variation_envelope_share_low', 'variation_envelope_share_high']].to_string(index=False))
    print('Earlier protected files unchanged:', len(protected))


if __name__ == '__main__':
    main()
