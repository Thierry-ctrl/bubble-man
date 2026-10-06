"""Pre-declared noise stop, readings only: is night-to-night change small enough?"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from night_signal import night_series

OUT = Path(__file__).resolve().parent
night, step = night_series()
win = night.loc['2018-01-15':'2018-12-31']
change = win.diff().dropna()
st = step.loc['2018-01-15':'2018-12-31']
by_month = {f'{m:%b}': {'change_std': round(float(change[change.index.month == m.month].std()), 2),
                        'nights_with_step_ge_10': int((st[st.index.month == m.month] >= 10).sum()),
                        'nights': int((st.index.month == m.month).sum())}
            for m in sorted({d.replace(day=1) for d in st.index})}
res = {'missing_nights': int(night.loc['2018-01-01':'2018-12-31'].isna().sum()),
       'night_to_night_change_std_full_window': round(float(change.std()), 2),
       'january_reference_std': 2.25, 'stop_limit': 4.5,
       'noise_stop_triggered': bool(change.std() > 4.5),
       'change_percentiles': {f'p{q}': round(float(np.percentile(change, q)), 2) for q in (1, 5, 50, 95, 99)},
       'step_ge_10_nights': int((st >= 10).sum()), 'step_nights': int(st.notna().sum()),
       'step_percentiles': {f'p{q}': round(float(np.percentile(st.dropna(), q)), 2) for q in (50, 90, 95, 99)},
       'by_month': by_month}
(OUT / 'noise-check.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps({k: v for k, v in res.items() if k != 'by_month'}, indent=2))
print("month   change-std   nights with step >= 10")
for k, v in by_month.items(): print(f"  {k}      {v['change_std']:5.2f}        {v['nights_with_step_ge_10']:2d} / {v['nights']}")
