"""Recompute every 2018 number the protocol cites and check the text agrees. 2018 only.

Does not read 2019 data or the leak schedule file.
"""
import re, sys
from pathlib import Path
import numpy as np
import pandas as pd
OUT = Path(__file__).resolve().parent; ROOT = OUT.parents[1]
sys.path.insert(0, str(OUT))
from night_signal import night_series
text = (OUT / 'PROTOCOL-2019-DRAFT.md').read_text()
memo = (OUT / 'DECISION-MEMO.md').read_text()
night, step = night_series()
rs = lambda x: (np.percentile(x, 75) - np.percentile(x, 25)) / 1.349
c_main = night.loc['2018-01-15':'2018-12-31'].diff().iloc[1:]
c_full = night.loc['2018-01-01':'2018-12-31'].diff().iloc[1:]
c_ref = night.loc['2018-01-15':'2018-01-23'].diff().iloc[1:]
checks = {
    'changes on common basis = 350': len(c_main) == 350,
    'nights 15 Jan-31 Dec 2019 = 351': (pd.Timestamp('2019-12-31') - pd.Timestamp('2019-01-15')).days + 1 == 351,
    'std 6.04 cited': f'{c_main.std():.2f}' == '6.04' and '6.04' in text,
    'robust 2.98 cited': f'{rs(c_main):.2f}' == '2.98' and '2.98' in text,
    'full-year robust 2.96 cited': f'{rs(c_full):.2f}' == '2.96' and '2.96' in text,
    'January std 2.25 cited': f'{c_ref.std():.2f}' == '2.25' and '2.25' in text,
    'January robust 1.11 cited': f'{rs(c_ref):.2f}' == '1.11' and '1.11' in text,
    'robust cutoff 2.22 = 2 x 1.11': '2.22' in text and abs(2 * round(rs(c_ref), 2) - 2.22) < 1e-9,
    'January reference has 8 changes': len(c_ref) == 8,
    'armed entering 2019': bool((step.loc['2018-12-24':'2018-12-31'] < 10).all()),
    'last step >= 10 on 10 Oct': str(step.loc['2018-10-06':][step.loc['2018-10-06':] >= 10].index.max().date()) == '2018-10-10',
    'S3 arithmetic': abs(2 / 52 - 0.038) < 5e-4 and abs(3 / 52 - 0.058) < 5e-4,
    'p floor 0.019': abs(1 / 52 - 0.019) < 5e-4,
    '1 Jan 2019 Tuesday, 30 Dec 2019 Monday': pd.Timestamp('2019-01-01').day_name() == 'Tuesday' and pd.Timestamp('2019-12-30').day_name() == 'Monday',
    'no 48 h causal flag left (only the withdrawal note mentions it)':
        [l for l in text.splitlines() if re.search(r'\b48 ?h', l)] ==
        [l for l in text.splitlines() if 'withdrew the claim that credits after 48 hours' in l],
    'no 2 Jan / 364-change basis left in noise check': '2 Jan – 31 Dec 2019' not in text and '(364 changes)' not in text,
    'S4 labelled proposed target (protocol)': 'proposed operational target' in text,
    'S4 labelled proposed target (memo)': 'proposed target' in memo,
    'section references resolve (§2.4 exists)': '4. **The 2019 leak schedule is not blind.**' in text,
    'carry-over start times cited': all(t in text for t in ['2018-02-16 04:15', '2018-07-07 09:10', '2018-07-30 18:40']),
    'original failure kept on record': '6.04 — FAILED' in text,
}
for k, v in checks.items():
    print(f"  {'PASS' if v else 'FAIL'}  {k}")
print(f"\n{sum(checks.values())}/{len(checks)} consistency checks passed")
sys.exit(0 if all(checks.values()) else 1)
