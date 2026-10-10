"""The two warning rules of PROTOCOL-LEAKDB-1000.md, section 4. Both share the frozen
method (leakdb/method.py) for day types, night window, self-aligning type and step."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'leakdb'))
import method as M

ADAPT_BACK, ADAPT_GAP, ADAPT_MIN = 56, 9, 20       # days D-56 .. D-9, at least 20 values


def robust_spread(x):
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return np.nan
    q1, q3 = np.percentile(x, [25, 75]); return (q3 - q1) / 1.349


def adaptive_thresholds(step, frozen_T):
    """T(D) for every day index d: 4 x spread of steps on indices max(8, d-56) .. d-9."""
    T = np.full(len(step), frozen_T, float)
    for d in range(len(step)):
        lo, hi = max(8, d - ADAPT_BACK), d - ADAPT_GAP           # inclusive bounds
        if hi < lo:
            continue
        past = step[lo:hi + 1]
        if np.isfinite(past).sum() >= ADAPT_MIN:
            s = robust_spread(past)
            if np.isfinite(s) and s > 0:
                T[d] = 4 * s
    return T


def warn(step, T, ns, day0, start=M.WARN_FROM):
    """Frozen warning logic with a per-night threshold: armed, re-arm below T(D), >= 7 days."""
    out, armed, last = [], True, None
    for d in range(start, len(step)):
        if not np.isfinite(step[d]):
            continue
        if step[d] < T[d]:
            armed = True; continue
        issue = day0 + pd.Timedelta(days=d, hours=ns + 2)
        if armed and (last is None or issue - last >= pd.Timedelta(days=M.SPACING_DAYS)):
            out.append((d, issue, float(step[d]), float(T[d]))); armed, last = False, issue
    return out


def both_rules(s: pd.Series):
    """Returns (frozen Result, frozen warnings, adaptive warnings). Not-assessable is judged on
    the frozen rule's inputs; then neither rule issues warnings."""
    r = M.run(s, 'self_aligning')
    if not r.assessable:
        return r, [], []
    day0 = s.index[0].normalize()
    frozen = [(d, i, st, r.threshold) for d, i, st in r.warnings]
    adaptive = warn(r.step, adaptive_thresholds(r.step, r.threshold), r.night_start_hour, day0)
    return r, frozen, adaptive
