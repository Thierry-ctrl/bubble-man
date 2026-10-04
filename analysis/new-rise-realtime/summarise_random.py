"""Summarise the 300 saved random runs that the chart plots. Reads only.

Written during review to give every random-comparison number in FINDINGS.md one
saved, reproducible source. It does not re-run anything or change the rule.
"""
import json
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent
runs = json.loads((OUT / 'random-distributions.json').read_text())
real = json.loads((OUT / 'realtime-results.json').read_text())['new_rule']
total, abrupt, delay = (np.array(runs[k]) for k in
                        ('total_credited', 'abrupt_credited', 'median_delay_hours'))
summary = {
    'source': 'random-distributions.json, written by plot_realtime.py, seed 20261003',
    'runs': int(len(total)),
    'total_credited': {'median': float(np.median(total)), 'p95': float(np.percentile(total, 95)),
                       'max': int(total.max()), 'share_reaching_12': round(float((total == 12).mean()), 4)},
    'abrupt_credited': {'distinct_values': sorted(int(v) for v in set(abrupt)),
                        'share_reaching_6': round(float((abrupt == 6).mean()), 4)},
    'median_delay_hours': {'median': round(float(np.median(delay)), 2),
                           'p5': round(float(np.percentile(delay, 5)), 2),
                           'p95': round(float(np.percentile(delay, 95)), 2),
                           'share_as_fast_or_faster_than_real': round(
                               float((delay <= real['median_delay_hours']).mean()), 4)},
    'real': {'credited': real['leaks_credited'], 'abrupt': real['abrupt_credited'],
             'median_delay_hours': real['median_delay_hours']},
}
(OUT / 'random-summary-300.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
