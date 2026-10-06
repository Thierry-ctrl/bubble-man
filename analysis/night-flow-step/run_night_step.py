"""Generate the frozen night-step warnings and score them. 2018 only; 2019 sealed.

Rule: RULE-FROZEN.md (committed b944498 before this ran). The scorer is imported, not
edited. Leak labels enter only through the scorer.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(OUT)); sys.path.insert(0, str(ROOT / 'analysis/scorer'))
from night_signal import night_series                                  # noqa: E402
from leak_scorer import Rules, add_observed_activity, load_leaks, score  # noqa: E402

THRESHOLD, SPACING = 10.0, pd.Timedelta(days=7)
RULES = Rules(gap_tolerance_hours=0, reporting_lag_hours=1.0, max_delay_hours=168)
WINDOW = ('2018-01-15 00:00', '2018-12-31 23:00')
DOMAIN = ('2018-01-15', '2018-12-30')            # 350 nights = 50 whole weeks

night, step = night_series()

# ---------------- frozen warning rule -----------------------------------------
warn_nights, armed, last = [], True, None
for d, s in step.loc['2018-01-15':'2018-12-31'].items():
    if not np.isfinite(s):
        continue
    if s < THRESHOLD:
        armed = True
        continue
    issue = d + pd.Timedelta(hours=4)
    if armed and (last is None or issue - last >= SPACING):
        warn_nights.append(d)
        armed, last = False, issue

def to_series(nights, start, end):
    idx = pd.date_range(start, end, freq='h')
    s = pd.Series(False, index=idx)
    for d in nights:
        t = pd.Timestamp(d) + pd.Timedelta(hours=3)   # hour labelled 03:00 -> issuable 04:00
        if t in s.index:
            s.loc[t] = True
    return s

zones = dict(pd.read_csv(ROOT / 'analysis/scorer/leak-zones-from-network-map.csv')[['link', 'zone']].values)
cfg = load_leaks(ROOT / 'research/2026-09-21/battledim-config.yaml', zones)
leaks = cfg[(cfg.start.dt.year == 2018) & (cfg.zone == 'main')].reset_index(drop=True)
leaks = add_observed_activity(leaks, ROOT / 'data/l-town/reference/2018_Leakages.csv')

full = score(to_series(warn_nights, *WINDOW), 1, leaks, RULES)

# ---------------- whole-week circular shifts over the 350-night domain -----------
domain_nights = pd.date_range(*DOMAIN, freq='D')
assert len(domain_nights) == 350
pos = [domain_nights.get_loc(d) for d in warn_nights if d in domain_nights]
dom_end = DOMAIN[1] + ' 23:00'

def score_positions(p):
    return score(to_series([domain_nights[i] for i in p], DOMAIN[0], dom_end), 1, leaks, RULES)

real_dom = score_positions(pos)
shifts, wrap_gaps = [], []
for k in range(1, 50):
    p = sorted((i + 7 * k) % 350 for i in pos)
    gaps = np.diff(p).tolist() + ([p[0] + 350 - p[-1]] if p else [])
    wrap_gaps.append(min(gaps) if gaps else None)
    o = score_positions(p)
    shifts.append({'k_weeks': k, 'abrupt': o['abrupt']['credited'], 'all': o['overall']['credited'],
                   'median_delay_h': o['overall']['median_delay_hours'],
                   'min_gap_days': min(gaps) if gaps else None})
sh = pd.DataFrame(shifts)
assert sh.k_weeks.nunique() == 49
ra = real_dom['abrupt']['credited']; rall = real_dom['overall']['credited']
p_abrupt = (1 + int((sh.abrupt >= ra).sum())) / 50
p_all = (1 + int((sh['all'] >= rall).sum())) / 50
beats = int((sh.abrupt < ra).sum())

# ---------------- workload --------------------------------------------------
ev = pd.DataFrame(full['events'])
ev['month'] = pd.to_datetime(ev.run_start).dt.strftime('%b')
months = pd.date_range('2018-01-01', '2018-12-01', freq='MS').strftime('%b')
per_month = {m: {'warnings': int((ev.month == m).sum()),
                 'credited': int(((ev.month == m) & (ev.outcome == 'credited')).sum()),
                 'not_credited': int(((ev.month == m) & (ev.outcome != 'credited')).sum())} for m in months}

report = {
    'label': '2018 DEVELOPMENT TEST — leaks examined before; 2019 sealed',
    'rule': 'RULE-FROZEN.md (b944498)',
    'warnings_full_window': len(warn_nights),
    'warning_nights': [str(d.date()) for d in warn_nights],
    'full_window': {k: full[k] for k in ('alert_events_total', 'outcomes', 'overall', 'abrupt', 'incipient')},
    'per_leak': full['leaks'],
    'events': [{k: e[k] for k in ('run_start', 'issuable_at', 'outcome', 'matched_leak', 'match_confidence',
                                  'leaks_running', 'candidates')} for e in full['events']],
    'per_month': per_month,
    'shift_comparison': {
        'domain': '15 Jan - 30 Dec 2018, 350 nights', 'distinct_shifts': 49,
        'real_in_domain': {'warnings': len(pos), 'abrupt': ra, 'all': rall,
                           'median_delay_h': real_dom['overall']['median_delay_hours']},
        'shifts_abrupt_distribution': sh.abrupt.value_counts().sort_index().to_dict(),
        'shifts_all_distribution': sh['all'].value_counts().sort_index().to_dict(),
        'shifts_beaten_on_abrupt': beats, 'needed_to_pass': 47,
        'p_one_sided_abrupt': round(p_abrupt, 3), 'p_one_sided_all': round(p_all, 3),
        'shifts_with_a_gap_under_7_days': int((sh.min_gap_days < 7).sum()),
        'shift_median_delay_h_median': float(sh.median_delay_h.dropna().median()) if sh.median_delay_h.notna().any() else None,
    },
    'shifts': shifts,
}
(OUT / 'night-step-results.json').write_text(json.dumps(report, indent=2, default=str) + '\n')
pd.DataFrame(full['leaks']).to_csv(OUT / 'per-leak.csv', index=False)
pd.DataFrame(report['events']).to_csv(OUT / 'warnings.csv', index=False)
sh.to_csv(OUT / 'shifts.csv', index=False)

print(f"warnings: {len(warn_nights)}  nights: {[str(d.date()) for d in warn_nights]}")
print(f"credited {full['overall']['credited']}/12  abrupt {full['abrupt']['credited']}/{full['abrupt']['eligible_leaks']}"
      f"  gradual {full['incipient']['credited']}/{full['incipient']['eligible_leaks']}  median delay {full['overall']['median_delay_hours']} h")
print(f"outcomes: {full['outcomes']}")
print("\nper leak:")
for r in full['leaks']:
    print(f"  {r['link']:5s} {r['type']:9s} {r['outcome']:8s} delay {r['delay_hours_from_first_flow']}")
print("\nper month (warnings / credited / not credited):")
print("  " + "  ".join(f"{m} {v['warnings']}/{v['credited']}/{v['not_credited']}" for m, v in per_month.items()))
s = report['shift_comparison']
print(f"\nSHIFTS: real in domain abrupt {ra}, all {rall}; 49 distinct shifts abrupt dist {s['shifts_abrupt_distribution']}")
print(f"  beaten on abrupt: {beats}/49 (need 47)   p(abrupt) = {s['p_one_sided_abrupt']}   p(all) = {s['p_one_sided_all']}")
print(f"  all-leak dist {s['shifts_all_distribution']}   shifts with a wrapped gap < 7 days: {s['shifts_with_a_gap_under_7_days']}")
