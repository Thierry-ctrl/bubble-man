"""Yorkshire Water DMA test (PROTOCOL-YORKSHIRE-N4.md): reading, association scoring, shifts.
The detection rules are the unchanged ones in analysis/next-fair-evaluation/leakdb1000/rules.py."""
from __future__ import annotations
import re, sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'next-fair-evaluation/leakdb1000'))
import rules as R
M = R.M

START = pd.Timestamp('2016-04-01 00:00')          # wall-clock (UK local) time, as in the file
AUTUMN_AMBIGUOUS = pd.Timestamp('2016-10-30 01:00')  # the UK hour that occurred twice
N_DAYS = 365
LOOKBACK = 28                                      # days before the completion date (protocol section 6)
WARN_FROM = M.WARN_FROM                            # day index 28 = day 29
DOMAIN_DAYS = 336                                  # days 29-364, 48 whole weeks
FIRST_ELIGIBLE = WARN_FROM + LOOKBACK              # completion day index >= 56 (day 57)


def dma_key(x) -> str:
    """Same DMA in both files: numeric identifiers compared as integers ('011' == '11')."""
    x = str(x).strip()
    return str(int(x)) if x.isdigit() else x


def read_area(path) -> tuple[dict, dict]:
    """Area CSV -> {DMA: 30-minute Series (Timestamp index, m3/h, NaN = missing)}, report.
    Rules (section 4): only validity 'V' is used; L/s x 3.6; a 30-minute value needs both of its
    15-minute readings; wall-clock stamps that occur twice (autumn clock change) are treated
    as missing; stamps that never occur (spring) stay missing; negative flows are missing."""
    t = pd.read_csv(path, dtype={'DMA': str, 'Date': str, 'Time': str, 'Flow Validity Code': str})
    need = ['DMA', 'Date', 'Time', 'Flow', 'Flow Validity Code']
    assert list(t.columns) == need, f'unexpected columns {list(t.columns)} - stop'
    t['ts'] = pd.to_datetime(t.Date + ' ' + t.Time, format='%d/%m/%Y %H:%M:%S', errors='coerce')
    rep = {'rows': len(t), 'unparseable_stamps': int(t.ts.isna().sum()),
           'validity_codes': t['Flow Validity Code'].value_counts().to_dict()}
    t = t[t.ts.notna()]
    flow = pd.to_numeric(t.Flow, errors='coerce')
    ok = (t['Flow Validity Code'].str.strip() == 'V') & flow.notna() & (flow >= 0)
    rep['negative_valid_flows'] = int(((t['Flow Validity Code'].str.strip() == 'V') & (flow < 0)).sum())
    t = t.assign(v=np.where(ok, flow * 3.6, np.nan))
    dup = t.duplicated(['DMA', 'ts'], keep=False)
    rep['duplicated_stamps'] = int(dup.sum())
    rep['duplicated_stamp_dates'] = sorted({str(d.date()) for d in t.ts[dup]})[:10]
    t = t[~dup]
    # Revision 1 (see protocol section 9): the file holds ONE copy of the repeated autumn hour,
    # so it cannot be told which of the two hours it is; treat it as missing, as section 4 intends.
    amb = (t.ts >= AUTUMN_AMBIGUOUS) & (t.ts < AUTUMN_AMBIGUOUS + pd.Timedelta(hours=1))
    rep['autumn_ambiguous_hour_readings_set_missing'] = int(amb.sum())
    t.loc[amb, 'v'] = np.nan
    grid15 = pd.date_range(START, periods=N_DAYS * 96, freq='15min')
    out = {}
    t['DMA'] = t.DMA.map(dma_key)
    for dma, g in t.groupby('DMA'):
        s = g.set_index('ts').v.reindex(grid15)
        x = s.values.reshape(-1, 2)
        half = np.where(np.isfinite(x).all(axis=1), x.mean(axis=1), np.nan)
        out[dma] = pd.Series(half, index=pd.date_range(START, periods=N_DAYS * 48, freq='30min'))
    rep['dmas'] = len(out)
    return out, rep


def to_frozen_reader(series: pd.Series) -> pd.Series:
    """Pass through the frozen reader exactly as every earlier test did."""
    csv = pd.DataFrame({'Timestamp': series.index.strftime('%Y-%m-%d %H:%M:%S'), 'Value': series.values}).to_csv(index=False)
    return M.read_inlet(csv.encode())


def read_repairs(path) -> tuple[pd.DataFrame, dict]:
    """Mains repairs -> DMA, completion date. Column rule (section 5): exactly one column whose
    name contains 'dma' and exactly one whose name contains 'date'; dates day-first. Anything
    else stops the run for a documented correction."""
    r = pd.read_csv(path, dtype=str)
    dcol = [c for c in r.columns if 'dma' in c.lower()]
    tcol = [c for c in r.columns if 'date' in c.lower()]
    assert len(dcol) == 1 and len(tcol) == 1, f'repair columns not recognised: {list(r.columns)} - stop'
    d = pd.to_datetime(r[tcol[0]], dayfirst=True, errors='coerce').dt.normalize()
    out = pd.DataFrame({'dma': r[dcol[0]].map(dma_key), 'completed': d})
    rep = {'rows': len(r), 'columns': list(r.columns), 'unparseable_dates': int(d.isna().sum())}
    return out[out.completed.notna()].reset_index(drop=True), rep


def day_index(ts) -> int:
    return int((pd.Timestamp(ts).normalize() - START) / pd.Timedelta(days=1))


def associate(warn_days: dict, repairs: pd.DataFrame, dmas: set, last_day=N_DAYS - 1):
    """warn_days: {DMA: [day indices]} (assessable DMAs only, same window for every rule).
    A repair is ELIGIBLE if its DMA is assessable and its completion day index is in
    [FIRST_ELIGIBLE, last_day]. It is PRECEDED if a warning in that DMA falls on a day in
    [completion - 28, completion - 1]. Same-day warnings are counted separately.
    A warning is FOLLOWED if an eligible-or-not repair in its DMA completes 1-28 days later."""
    rows = []
    for r in repairs.itertuples():
        if r.dma not in dmas:
            continue
        c = day_index(r.completed)
        if not (FIRST_ELIGIBLE <= c <= last_day):
            continue
        w = warn_days.get(r.dma, [])
        rows.append({'dma': r.dma, 'completed_day': c,
                     'preceded': any(c - LOOKBACK <= d <= c - 1 for d in w),
                     'same_day_warning': c in w,
                     'days_before': min([c - d for d in w if c - LOOKBACK <= d <= c - 1], default=None)})
    rep_by = repairs.assign(c=repairs.completed.map(day_index)).groupby('dma').c.apply(list).to_dict()
    followed = sum(any(1 <= c - d <= LOOKBACK for c in rep_by.get(dma, [])) for dma, w in warn_days.items() for d in w)
    n_warn = sum(len(w) for w in warn_days.values())
    E = pd.DataFrame(rows, columns=['dma', 'completed_day', 'preceded', 'same_day_warning', 'days_before'])
    return {'eligible_repairs': len(E), 'preceded': int(E.preceded.sum()) if len(E) else 0,
            'same_day_only': int((E.same_day_warning & ~E.preceded).sum()) if len(E) else 0,
            'median_days_before': float(E.days_before.dropna().median()) if E.days_before.notna().any() else None,
            'warnings': n_warn, 'warnings_followed_by_repair_within_28d': int(followed)}, E


def shift_days(days, k):
    return sorted(WARN_FROM + ((d - WARN_FROM + 7 * k) % DOMAIN_DAYS) for d in days if WARN_FROM <= d < WARN_FROM + DOMAIN_DAYS)


def shift_comparison(warn_days: dict, repairs: pd.DataFrame, dmas: set):
    """Whole-week shifts of every DMA's warnings, same k, on the 48-week domain; statistic =
    eligible repairs preceded (repairs completing up to day 364 + 0; same eligibility)."""
    last = WARN_FROM + DOMAIN_DAYS - 1
    real = associate({k: shift_days(v, 0) for k, v in warn_days.items()}, repairs, dmas, last_day=last)[0]['preceded']
    sh = [associate({k: shift_days(v, j) for k, v in warn_days.items()}, repairs, dmas, last_day=last)[0]['preceded']
          for j in range(1, DOMAIN_DAYS // 7)]
    return {'real_in_domain': real, 'shifts': len(sh), 'shift_max': max(sh), 'shift_median': float(np.median(sh)),
            'p': (1 + sum(x >= real for x in sh)) / (len(sh) + 1)}, sh
