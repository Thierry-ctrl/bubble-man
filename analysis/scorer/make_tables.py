"""Produce the deliverable tables at a mechanically-chosen reference setting.

Reference setting: threshold 10 m3/h, persistence 6 observations — the arithmetic
midpoint of the declared grid — with a 7-day matching deadline. The deadline is
justified by the leak-coverage finding (a leak runs 100% of 2018), NOT by any score.
"""
import json, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from leak_scorer import Rules, score
import run_scorer as run

OUT = Path(__file__).resolve().parent
THRESHOLD, PERSISTENCE, DEADLINE = 10, 6, 168

tables = {}
for name, (difference, base) in run.METHODS.items():
    rules = Rules(gap_tolerance_hours=base.gap_tolerance_hours,
                  min_history_days=0, max_delay_hours=DEADLINE)
    result = score(run.warn(difference, THRESHOLD, PERSISTENCE), run.leaks_2018, rules)
    tables[name] = result
    pd.DataFrame(result['leaks']).to_csv(OUT / f'leak-outcomes-{name}.csv', index=False)
    pd.DataFrame(result['events']).to_csv(OUT / f'alert-events-{name}.csv', index=False)

(OUT / 'reference-setting.json').write_text(json.dumps({
    'setting': {'threshold_m3_per_hour': THRESHOLD, 'persistence_observations': PERSISTENCE,
                'max_delay_hours': DEADLINE},
    'why_this_setting': 'Arithmetic midpoint of the declared grid. Not selected for score.',
    'results': {k: {kk: v[kk] for kk in ('alert_events_total', 'unmatched_alerts',
                                         'unmatched_alerts_per_week', 'repeat_alerts_scored_zero',
                                         'alerts_coinciding_with_excluded_leak',
                                         'overall', 'abrupt', 'incipient')}
                for k, v in tables.items()},
}, indent=2) + '\n')

print('=== LEAK OUTCOMES (frozen_week, threshold 10, persistence 6, 7-day deadline) ===')
frame = pd.DataFrame(tables['frozen_week']['leaks'])
print(frame[['link','type','start','eligibility','outcome','delay_hours','match_confidence']].to_string(index=False))
print('\n=== SUMMARY BY METHOD ===')
for name, r in tables.items():
    o = r['overall']
    print(f"  {name:18s} events={r['alert_events_total']:4d}  matched={o['matched']:2d}/{o['eligible_leaks']}"
          f"  abrupt={r['abrupt']['matched']}/{r['abrupt']['eligible_leaks']}"
          f"  incipient={r['incipient']['matched']}/{r['incipient']['eligible_leaks']}"
          f"  unmatched/wk={r['unmatched_alerts_per_week']}"
          f"  ambiguous={o['ambiguous_matches']}  median delay={o['median_delay_hours']}h")
