"""Would a detector that warns at RANDOM times score just as well?

The first scorer run matched 13 of 13 leaks at almost every setting and reported zero
unnecessary warnings. That is suspicious. This script checks the obvious explanation:
in 2018 some leak is nearly always running, so "a warning arrived while a leak was
active" may be almost impossible to fail.

Method: take each method's ACTUAL warning series and rotate it circularly by a random
offset. That keeps the number of alert events and their durations exactly as they were,
but destroys any relationship to when leaks actually began. If the rotated series scores
as well as the real one, the score is measuring alert density, not detection.

This follows the standard critique of time-series anomaly benchmarks: a random detector
that scores like a real one means the metric is broken (Kim et al., arXiv 2109.05257).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from leak_scorer import Rules, load_leaks, score  # noqa: E402
import run_scorer as run  # noqa: E402  (reuses the same methods and settings)

OUT = Path(__file__).resolve().parent
REPEATS = 200
rng = np.random.default_rng(20260929)

leaks = run.leaks_2018
window = run.frozen.index

# ---- how often is ANY leak running at all? ----
active_any = pd.Series(0, index=window)
active_eligible = pd.Series(0, index=window)
eligible_links = {'p461', 'p232', 'p427', 'p673', 'p628', 'p538', 'p866',
                  'p31', 'p654', 'p810', 'p183', 'p158', 'p369'}
for _, leak in leaks.iterrows():
    covered = (window >= leak.start) & (window <= leak.end)
    active_any += covered
    if leak.link in eligible_links:
        active_eligible += covered

coverage = {
    'hours_in_window': int(len(window)),
    'share_of_hours_with_at_least_one_leak_running': round(float((active_any > 0).mean()), 4),
    'share_of_hours_with_an_ELIGIBLE_leak_running': round(float((active_eligible > 0).mean()), 4),
    'median_leaks_running_at_once': int(active_any.median()),
    'max_leaks_running_at_once': int(active_any.max()),
}

CELLS = [(10, 6), (10, 24), (20, 24)]
rows = []
for name, (difference, rules) in run.METHODS.items():
    for threshold, persistence in CELLS:
        if name == 'night_rolling_14d' and persistence > 3:
            continue
        flagged = run.warn(difference, threshold, persistence)
        real = score(flagged, leaks, rules)
        values = flagged.to_numpy()
        matched = []
        for _ in range(REPEATS):
            rotated = pd.Series(np.roll(values, rng.integers(1, len(values))), index=flagged.index)
            matched.append(score(rotated, leaks, rules)['overall']['matched'])
        rows.append({
            'method': name, 'threshold': threshold, 'persistence': persistence,
            'alert_events': real['alert_events_total'],
            'real_matched': real['overall']['matched'],
            'random_matched_median': float(np.median(matched)),
            'random_matched_p5': float(np.percentile(matched, 5)),
            'random_matched_p95': float(np.percentile(matched, 95)),
            'eligible_leaks': real['overall']['eligible_leaks'],
        })
        print(f"  {name:18s} thr={threshold:2d} pers={persistence:2d}  "
              f"events={real['alert_events_total']:4d}  real={real['overall']['matched']:2d}/"
              f"{real['overall']['eligible_leaks']}  random median="
              f"{np.median(matched):.1f} (5-95%: {np.percentile(matched,5):.0f}-{np.percentile(matched,95):.0f})")

result = {'leak_coverage': coverage, 'null_comparison': rows, 'repeats': REPEATS}
(OUT / 'null-check.json').write_text(json.dumps(result, indent=2) + '\n')
print('\n=== how often is a leak running in 2018? ===')
print(json.dumps(coverage, indent=2))
