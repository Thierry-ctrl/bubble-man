"""Night-flow step check with the self-aligning baseline (Idea A), for one LeakDB inlet series.

Implements PROTOCOL-LEAKDB.md exactly. Reads ONLY an inlet flow file (Flows/Link_1.csv).
Nothing here reads, or accepts, leak information.

Day indexing: day index 0 = the first day in the file ("day 1" in the protocol). LeakDB's
weekly demand pattern is tied to the position in the series, not to the calendar date in
the timestamps (the public sample is stamped 2017, the generator code 2018), so "weekday"
means day index mod 7.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import io
import numpy as np
import pandas as pd

STEP_MIN = 30
LEARN_DAYS = 14                 # days 1-14
ALIGN_FROM = 21                 # Idea A from day 22 (index 21)
THRESH_DAYS = range(8, 28)      # steps on days 9-28 (indices 8..27): 20 values
WARN_FROM = 28                  # warnings from day 29 (index 28)
MULT_GROUP, MULT_T = 3.0, 4.0
MIN_THRESH_STEPS, MIN_EVAL_STEPS = 15, 300
SPACING_DAYS = 7
STRESS_DAY = 149                # day 150 is repeated in the stress copy (index 149)


def read_inlet(source) -> pd.Series:
    """30-minute readings -> Series on a complete 30-minute grid (missing -> NaN)."""
    raw = pd.read_csv(source if not isinstance(source, bytes) else io.BytesIO(source))
    assert list(raw.columns) == ['Timestamp', 'Value'], f'unexpected columns {list(raw.columns)}'
    t = pd.to_datetime(raw.Timestamp, errors='coerce')
    v = pd.to_numeric(raw.Value, errors='coerce')
    s = pd.Series(v.values, index=t).loc[lambda x: x.index.notna()]
    s = s[~s.index.duplicated(keep=False)]           # duplicated stamps -> treated as missing
    start = s.index.min()
    grid = pd.date_range(start, periods=365 * 48, freq=f'{STEP_MIN}min')
    return s.reindex(grid)


def hourly_days(s: pd.Series) -> np.ndarray:
    """(days, 24) array of hourly means; an hour needs both of its readings."""
    x = s.values.reshape(-1, 2)
    h = np.where(np.isfinite(x).all(axis=1), x.mean(axis=1), np.nan)
    return h.reshape(-1, 24)


def rms(a): return float(np.sqrt(np.nanmean(np.square(a))))
def z(x): return (x - x.mean()) / x.std()


@dataclass
class Result:
    assessable: bool
    reason: str = ''
    types: list = field(default_factory=list)          # type name per weekday 0..6
    night_start_hour: int | None = None
    threshold: float | None = None
    n_threshold_steps: int = 0
    day_type: list = field(default_factory=list)       # assigned type per day
    night: np.ndarray | None = None
    step: np.ndarray | None = None
    warnings: list = field(default_factory=list)       # (day index, issue Timestamp, step)


def learn(D):
    """Weekday grouping and profiles from days 1-14 (BASELINE-FROZEN rule, 3x)."""
    first = D[:LEARN_DAYS]
    rep = [rms(first[w] - first[w + 7]) for w in range(7)]
    dist = []
    for w in range(7):
        others = np.delete(first, [w, w + 7], axis=0)
        dist.append(rms(first[[w, w + 7]].mean(axis=0) - np.median(others, axis=0)))
    cut = MULT_GROUP * max(rep)
    types = [f'W{w}' if dist[w] > cut else 'P' for w in range(7)]
    prof = {t: np.median(first[[d for d in range(LEARN_DAYS) if types[d % 7] == t]], axis=0)
            for t in sorted(set(types))}
    return types, prof


def run(s: pd.Series, mode: str = 'self_aligning') -> Result:
    """mode: 'self_aligning' (Idea A, the primary method) or 'calendar' (fixed weekday map)."""
    assert mode in ('self_aligning', 'calendar')
    if s.index[0] != s.index[0].normalize():
        return Result(False, 'first timestamp not at 00:00')
    D = hourly_days(s)
    n = len(D)
    if not np.isfinite(D[:LEARN_DAYS]).all():
        return Result(False, 'days 1-14 incomplete')
    types, prof = learn(D)
    pooled = np.median(D[:LEARN_DAYS], axis=0)
    ns = int(np.argmin([pooled[h] + pooled[h + 1] for h in range(23)]))   # no wrap past midnight

    day_type = [types[d % 7] for d in range(n)]
    if mode == 'self_aligning' and len(prof) > 1:
        zp = {t: z(p) for t, p in prof.items()}
        for d in range(ALIGN_FROM, n):
            past = D[[d - 7, d - 14, d - 21]]
            if not np.isfinite(past).all():
                continue                                   # keep the learned weekday map
            shape = z(past.mean(axis=0))
            day_type[d] = max(sorted(zp), key=lambda t: np.corrcoef(shape, zp[t])[0, 1])

    resid = np.array([D[d] - prof[day_type[d]] for d in range(n)])
    night = resid[:, ns:ns + 2].mean(axis=1)                 # NaN if either hour missing
    step = np.full(n, np.nan)
    for d in range(8, n):
        w = night[d - 8:d + 1]
        if np.isfinite(w).all():
            step[d] = night[d - 1:d + 1].mean() - night[d - 8:d - 1].mean()

    early = step[list(THRESH_DAYS)]
    early = early[np.isfinite(early)]
    res = Result(True, '', types, ns, None, len(early), day_type, night, step)
    if len(early) < MIN_THRESH_STEPS:
        res.assessable, res.reason = False, f'only {len(early)} of 20 threshold steps'
        return res
    q1, q3 = np.percentile(early, [25, 75])
    sigma = (q3 - q1) / 1.349
    if not (np.isfinite(sigma) and sigma > 0):
        res.assessable, res.reason = False, 'robust spread of threshold steps is not positive'
        return res
    res.threshold = float(MULT_T * sigma)
    if np.isfinite(step[WARN_FROM:]).sum() < MIN_EVAL_STEPS:
        res.assessable, res.reason = False, 'fewer than 300 step values from day 29'
        return res

    armed, last = True, None
    day0 = s.index[0].normalize()
    for d in range(WARN_FROM, n):
        if not np.isfinite(step[d]):
            continue                                       # missing night: state unchanged
        if step[d] < res.threshold:
            armed = True
            continue
        issue = day0 + pd.Timedelta(days=d, hours=ns + 2)  # end of the night window
        if armed and (last is None or issue - last >= pd.Timedelta(days=SPACING_DAYS)):
            res.warnings.append((d, issue, float(step[d])))
            armed, last = False, issue
    return res


def stress_copy(s: pd.Series, day: int = STRESS_DAY) -> pd.Series:
    """Controlled weekly-slip stress: day `day` is played twice, so every later day carries
    the pattern of the weekday before its position (as L-Town 2019 did at New Year).
    Readings are not altered, only repeated once; result is 366 days long."""
    v = s.values.reshape(-1, 48)
    v2 = np.vstack([v[:day + 1], v[day:day + 1], v[day + 1:]]).ravel()
    return pd.Series(v2, index=pd.date_range(s.index[0], periods=len(v2), freq=f'{STEP_MIN}min'))


def true_type_after_stress(types, d, day: int = STRESS_DAY):
    """Type of the weekday whose pattern stressed day d actually carries."""
    return types[d % 7] if d <= day else types[(d - 1) % 7]
