"""DEVELOPMENT DIAGNOSIS of the frozen Q1 run on LeakDB Hanoi scenarios 11-500.
Recomputes the frozen method (identical code), re-scores per warning, and attaches
retrospective features. Leak labels explain; they are never inputs to the warning rule."""
import json
from common_dev import *

warn_rows, leak_rows, scen_rows = [], [], []
for a in A.itertuples():
    k = a.scenario
    s = inlet(k); r = M.run(s, 'self_aligning')
    days = [d for d, _, _ in r.warnings]
    assert days == sorted(W1[W1.scenario == k].day_index.tolist()), f'recomputation differs {k}'
    day0 = s.index[0].normalize(); grid = s.index
    lk = L[(L.scenario == k) & L.start.notna()]
    res = S.score_scenario(days, day0, r.night_start_hour, lk)
    lf = leak_flow(k, grid)
    tot = sum(lf.values()) if lf else pd.Series(0.0, index=grid)
    hourly_leak = tot.values.reshape(-1, 2).mean(1).reshape(-1, 24)
    ns = r.night_start_hour
    night_leak = hourly_leak[:, ns:ns + 2].mean(1)               # leak flow in the night window
    D = M.hourly_days(s); nightflow = D[:, ns:ns + 2].mean(1)
    # leak-free spread of steps over the whole evaluation year (retrospective)
    st = r.step; free = np.array([np.isfinite(st[d]) and night_leak[max(0, d - 8):d + 1].max() <= 0 for d in range(len(st))])
    late = np.array([d >= 28 for d in range(len(st))])
    q = lambda x: (np.percentile(x, 75) - np.percentile(x, 25)) / 1.349 if len(x) > 10 else np.nan
    sig_early = r.threshold / 4
    scen_rows.append({'scenario': k, 'threshold': r.threshold, 'sigma_early': sig_early,
                      'sigma_leakfree_days29plus': q(st[free & late]), 'leakfree_nights_29plus': int((free & late).sum()),
                      'mean_night_flow_days1_14': float(nightflow[:14].mean()),
                      'warnings': len(days), 'n_leaks': len(lk)})
    for e, d in zip(sorted(res['events'], key=lambda e: e['run_start']), days):
        nl = night_leak
        warn_rows.append({'scenario': k, 'day': d, 'outcome': e['outcome'], 'step': st[d], 'T': r.threshold,
                          'step_over_T': st[d] / r.threshold,
                          'pair_minus_ref_night_D': r.night[d] - np.mean(r.night[d - 8:d - 1]),
                          'pair_minus_ref_night_D1': r.night[d - 1] - np.mean(r.night[d - 8:d - 1]),
                          'next3_minus_ref': (np.nanmean(r.night[d + 1:d + 4]) - np.mean(r.night[d - 8:d - 1])) if d + 4 <= len(st) else np.nan,
                          'leak_night_flow_D': nl[d], 'leak_night_change_pair_vs_ref': nl[d - 1:d + 1].mean() - nl[d - 8:d - 1].mean(),
                          'leak_types_flowing': '|'.join(sorted({l.type for l in lk.itertuples() if l.start <= day0 + pd.Timedelta(days=d, hours=ns + 1) <= l.end})),
                          'oldest_flowing_leak_age_days': max([(day0 + pd.Timedelta(days=d) - l.start) / pd.Timedelta(days=1)
                                                               for l in lk.itertuples() if l.start <= day0 + pd.Timedelta(days=d, hours=ns + 1) <= l.end], default=np.nan),
                          'day_type': r.day_type[d], 'weekday': d % 7, 'night_flow': nightflow[d]})
    for p in res['leaks']:
        if p['eligibility'] != 'eligible': continue
        l = lk[lk.link == p['link']].iloc[0]
        d0 = int((l.start - day0) / pd.Timedelta(days=1))
        # size of the leak at night over its first 7 nights, and the step it produced
        win = range(d0, min(d0 + 8, len(st)))
        leak_rows.append({'scenario': k, 'link': p['link'], 'type': p['type'], 'outcome': p['outcome'],
                          'delay_h': p['delay_hours_from_first_flow'], 'start_day': d0,
                          'night_leak_flow_day7': float(nl[min(d0 + 7, len(nl) - 1)]),
                          'max_step_first_8_nights': float(np.nanmax(st[list(win)])) if len(win) else np.nan,
                          'T': r.threshold,
                          'leak_size_over_T': float(nl[min(d0 + 7, len(nl) - 1)]) / r.threshold,
                          'other_leak_flowing_at_start': bool(any((o.start < l.start <= o.end) for o in lk.itertuples() if o.link != l.link)),
                          'warning_in_previous_7_days': any(d0 - 7 <= w < d0 + 1 for w in days)})
pd.DataFrame(warn_rows).to_csv(HERE / 'dev-warnings.csv', index=False)
pd.DataFrame(leak_rows).to_csv(HERE / 'dev-leaks.csv', index=False)
pd.DataFrame(scen_rows).to_csv(HERE / 'dev-scenarios.csv', index=False)
print(len(warn_rows), len(leak_rows), len(scen_rows))
