"""DEVELOPMENT: the frozen rule and candidate single changes. Each uses only readings
available when a warning is issued. All candidates examined are listed here and reported."""
from common_dev import *

def warn(step, T, start, ns, day0):
    """The frozen warning rule (armed, re-arm below T, >= 7 days apart), T scalar or per-day."""
    Tv = np.broadcast_to(np.asarray(T, float), step.shape)
    out, armed, last = [], True, None
    for d in range(start, len(step)):
        if not (np.isfinite(step[d]) and np.isfinite(Tv[d])): continue
        if step[d] < Tv[d]: armed = True; continue
        issue = day0 + pd.Timedelta(days=d, hours=ns + 2)
        if armed and (last is None or issue - last >= pd.Timedelta(days=7)):
            out.append(d); armed, last = False, issue
    return out

def rsig(x):
    x = x[np.isfinite(x)]; q1, q3 = np.percentile(x, [25, 75]); return (q3 - q1) / 1.349

def run_variant(s, kind):
    r = M.run(s, 'self_aligning'); ns = r.night_start_hour; day0 = s.index[0].normalize()
    st = r.step
    if kind == 'frozen':
        return [d for d, _, _ in r.warnings], ns
    if kind == 'mult6':                                   # same rule, threshold 6 x early spread
        return warn(st, 1.5 * r.threshold, 28, ns, day0), ns
    if kind == 'ratio':                                   # residual as a fraction of the profile
        D = M.hourly_days(s); prof = M.learn(D)[1]
        rel = np.array([D[d] / prof[r.day_type[d]] - 1 for d in range(len(D))])
        n = rel[:, ns:ns + 2].mean(1)
        st2 = np.full(len(n), np.nan)
        for d in range(8, len(n)):
            if np.isfinite(n[d - 8:d + 1]).all(): st2[d] = n[d - 1:d + 1].mean() - n[d - 8:d - 1].mean()
        return warn(st2, 4 * rsig(st2[8:28]), 28, ns, day0), ns
    if kind == 'rolling_sigma':                           # threshold from the previous 8 weeks of steps
        T = np.full(len(st), r.threshold)
        for d in range(28, len(st)):
            past = st[max(8, d - 56):d - 8]
            if np.isfinite(past).sum() >= 20: T[d] = 4 * rsig(past)
        return warn(st, T, 28, ns, day0), ns
    if kind == 'weekday_differenced':                     # step minus the median of the same weekday's
        x = np.full(len(st), np.nan)                      # steps 1, 2 and 3 weeks earlier
        for d in range(29, len(st)):
            ref = st[[d - 7, d - 14, d - 21]]
            if np.isfinite(st[d]) and np.isfinite(ref).all(): x[d] = st[d] - np.median(ref)
        return warn(x, 4 * rsig(x[29:49]), 49, ns, day0), ns
    if kind == 'new_high':                                # frozen rule, plus: the last two nights must be
        n = r.night                                       # higher than every night of the previous 4 weeks
        x = np.full(len(st), -np.inf)
        for d in range(28, len(st)):
            past = n[max(0, d - 29):d - 1]
            if np.isfinite(st[d]) and np.isfinite(n[d - 1:d + 1]).all() and np.isfinite(past).any():
                x[d] = st[d] if n[d - 1:d + 1].mean() > np.nanmax(past) else -np.inf
            elif not np.isfinite(st[d]):
                x[d] = np.nan
        return warn(x, r.threshold, 28, ns, day0), ns
    raise ValueError(kind)

KINDS = ['frozen', 'mult6', 'ratio', 'rolling_sigma', 'weekday_differenced', 'new_high']
