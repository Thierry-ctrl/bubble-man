"""Scoring for PROTOCOL-LEAKDB.md (revision 3). Written and tested on invented leak cases
BEFORE any LeakDB leak record was opened. Uses the existing scorer unchanged.

Leak files (format from LeakDB's generator code, leakDataset.py):
  Leaks/Leak_<node>_demand.csv   columns Timestamp, Description (leak flow, m3/h)
  Leaks/Leak_<node>_info.csv     lines "Key , Value"; 'Leak Type' is abrupt / incipient
If two leaks fall on the same node, LeakDB writes ONE pair of files (the second overwrites
the first's info; the flow is their combined leak flow), so they appear as one leak.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scorer'))
from leak_scorer import Rules, score          # noqa: E402  (unchanged scorer)

RULES = Rules(gap_tolerance_hours=0, reporting_lag_hours=1.0, max_delay_hours=168)
WARN_FROM, DOMAIN_DAYS = 28, 336                # days 29-364 = indices 28..363 = 48 weeks
STRESS_DAY = 149


# ---------------------------------------------------------------- leak records ----------
def read_info(text: str) -> dict:
    out = {}
    for line in text.splitlines()[1:]:
        if ',' in line:
            k, v = line.split(',', 1)
            out[k.strip()] = v.strip()
    return out


def read_leaks(leak_dir: Path, grid: pd.DatetimeIndex) -> pd.DataFrame:
    """One row per leak file pair. Activity = first..last positive leak flow, placed on the
    inlet file's 30-minute grid BY ROW POSITION (timestamps checked and the check recorded)."""
    rows = []
    for f in sorted(Path(leak_dir).glob('Leak_*_demand.csv')):
        node = f.name[len('Leak_'):-len('_demand.csv')]
        info = read_info((f.parent / f'Leak_{node}_info.csv').read_text())
        d = pd.read_csv(f)
        v = pd.to_numeric(d.iloc[:, 1], errors='coerce').values
        assert len(v) == len(grid), f'leak file length {len(v)} != inlet grid {len(grid)}'
        pos = np.flatnonzero(v > 0)
        stamps_agree = bool((pd.to_datetime(d.iloc[:, 0]).values == grid.values).all())
        kind = info.get('Leak Type', '').strip().lower()
        assert kind in ('abrupt', 'incipient'), f'unexpected leak type {kind!r}'
        rows.append({'link': node, 'type': kind, 'zone': 'hanoi',
                     'start': grid[pos[0]] if len(pos) else pd.NaT,
                     'end': grid[pos[-1]] if len(pos) else pd.NaT,
                     'info_start': info.get('Leak Start'), 'diameter_m': float(info.get('Leak Diameter', 'nan')),
                     'timestamps_agree_with_inlet': stamps_agree, 'never_flowed': len(pos) == 0})
    cols = ['link', 'type', 'zone', 'start', 'end', 'info_start', 'diameter_m',
            'timestamps_agree_with_inlet', 'never_flowed']
    return pd.DataFrame(rows, columns=cols)


def flowing_hours(leaks: pd.DataFrame, hours: pd.DatetimeIndex) -> np.ndarray:
    """True for each hour in which any leak is flowing (start <= hour <= end)."""
    on = np.zeros(len(hours), bool)
    for l in leaks.itertuples():
        if pd.notna(l.start):
            on |= (hours >= l.start.floor('h')) & (hours <= l.end)
    return on


# ---------------------------------------------------------------- one scenario ----------
def flag_series(warn_days, day0, night_start_hour, first_day, last_day):
    """Hourly boolean series from day `first_day` 00:00 to day `last_day` 23:00. A warning on
    night d is flagged at its last night hour, so the scorer's issuable time (+1 h lag)
    equals the protocol's issue time (end of the night window)."""
    idx = pd.date_range(day0 + pd.Timedelta(days=first_day), day0 + pd.Timedelta(days=last_day, hours=23), freq='h')
    s = pd.Series(False, index=idx)
    for d in warn_days:
        t = day0 + pd.Timedelta(days=int(d), hours=night_start_hour + 1)
        if t in s.index:
            s.loc[t] = True
    return s


def score_scenario(warn_days, day0, ns, leaks, last_day=364):
    sc = leaks[leaks.start.notna()][['link', 'type', 'zone', 'start', 'end']]
    return score(flag_series(warn_days, day0, ns, WARN_FROM, last_day), 1, sc, RULES)


# ---------------------------------------------------------------- week shifts -----------
def shift_days(warn_days, k):
    """Move warnings on days 29-364 by k whole weeks, wrapping inside the 48-week domain."""
    return sorted(WARN_FROM + ((d - WARN_FROM + 7 * k) % DOMAIN_DAYS)
                  for d in warn_days if WARN_FROM <= d < WARN_FROM + DOMAIN_DAYS)


def min_wrapped_gap(days):
    if len(days) < 2:
        return None
    p = sorted(d - WARN_FROM for d in days)
    return int(min(np.diff(p).tolist() + [p[0] + DOMAIN_DAYS - p[-1]]))


def shift_comparison(scen):
    """scen: list of dicts with warn_days, day0, ns, leaks. Same k for every scenario."""
    def pooled(k):
        a = n = 0; gaps = []
        for s in scen:
            days = shift_days(s['warn_days'], k)
            r = score_scenario(days, s['day0'], s['ns'], s['leaks'], last_day=WARN_FROM + DOMAIN_DAYS - 1)
            a += r['abrupt']['credited']; n += r['overall']['credited']
            g = min_wrapped_gap(days)
            if g is not None: gaps.append(g)
        return a, n, (min(gaps) if gaps else None)
    real_a, real_all, _ = pooled(0)
    rows = []
    for k in range(1, DOMAIN_DAYS // 7):
        a, n, g = pooled(k)
        rows.append({'k_weeks': k, 'abrupt': a, 'all': n, 'min_wrapped_gap_days': g})
    sh = pd.DataFrame(rows)
    return {'real_in_domain_abrupt': real_a, 'real_in_domain_all': real_all,
            'distinct_shifts': len(sh),
            'p_abrupt': (1 + int((sh.abrupt >= real_a).sum())) / (len(sh) + 1),
            'p_all': (1 + int((sh['all'] >= real_all).sum())) / (len(sh) + 1),
            'shifts_with_wrapped_gap_under_7_days': int((sh.min_wrapped_gap_days.dropna() < 7).sum())}, sh


# ---------------------------------------------------------------- Q2 stress copy --------
def leaks_for_stress(leaks, day0, stressed: bool):
    """Q2 leak table: leaks whose first flow is on day 150 are set aside (all four runs);
    in the stress copy, times from day 151 on move one day later."""
    cut0, cut1 = day0 + pd.Timedelta(days=STRESS_DAY), day0 + pd.Timedelta(days=STRESS_DAY + 1)
    keep = leaks[~((leaks.start >= cut0) & (leaks.start < cut1))].copy()
    if stressed:
        for c in ('start', 'end'):
            keep[c] = pd.to_datetime(keep[c]).where(~(pd.to_datetime(keep[c]) >= cut1), pd.to_datetime(keep[c]) + pd.Timedelta(days=1))
    return keep
