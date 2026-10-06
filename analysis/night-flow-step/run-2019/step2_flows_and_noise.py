"""Protocol 9724c60, steps 2-3: check 2019 flows, compute night values and noise. No leak records."""
import hashlib, json, sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from common import ROOT, read_flows, night_and_step, noise_changes, robust_sigma

f18 = ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv'
f19 = ROOT / 'data/l-town/readings/2019_SCADA_Flows.csv'
md5 = hashlib.md5(f19.read_bytes()).hexdigest()
assert md5 == '28fc99fdcbf80fcd26079e7fe602d6dc', f'checksum mismatch: {md5}'

raw19 = pd.read_csv(f19, sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')
raw18 = pd.read_csv(f18, sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')
assert list(raw19.columns) == list(raw18.columns) == ['p227', 'p235', 'PUMP_1'], raw19.columns
assert raw18.index[-1] == pd.Timestamp('2018-12-31 23:55') and raw19.index[0] == pd.Timestamp('2019-01-01 00:00'), \
    (raw18.index[-1], raw19.index[0])
assert raw19.index.is_unique and (raw19.index.to_series().diff().dropna() == pd.Timedelta(minutes=5)).all()

night, step = night_and_step(read_flows(f18, f19))
c = noise_changes(night, 2019)
res = {
    'protocol': '9724c60',
    'file': '2019_SCADA_Flows.csv', 'md5': md5, 'md5_matches_zenodo': True,
    'rows': int(len(raw19)), 'first': str(raw19.index[0]), 'last': str(raw19.index[-1]),
    'continuous_with_2018': True,
    'missing_5min_values': {c_: int(raw19[c_].isna().sum()) for c_ in raw19.columns},
    'missing_nights_2019': int(night.loc['2019-01-01':'2019-12-31'].isna().sum()),
    'noise_2019_common_basis': {
        'basis': 'nights 15 Jan - 31 Dec 2019, changes within span (16 Jan - 31 Dec)',
        'changes': int(len(c)),
        'original_statistic_std': round(float(c.std()), 2), 'original_cutoff': 4.5,
        'robust_sigma': round(robust_sigma(c), 2), 'like_for_like_robust_cutoff': 2.22,
        'role': 'REPORTED, NOT GATING (option B). The original 2018 noise stop failed and remains failed.',
    },
    'noise_2018_for_reference': {'std': 6.04, 'robust_sigma': 2.98},
}
res['noise_2019_common_basis']['std_above_original_cutoff'] = res['noise_2019_common_basis']['original_statistic_std'] > 4.5
res['noise_2019_common_basis']['robust_above_like_for_like_cutoff'] = res['noise_2019_common_basis']['robust_sigma'] > 2.22
(HERE / 'step2-flows-and-noise.json').write_text(json.dumps(res, indent=2) + '\n')
pd.DataFrame({'night_residual': night, 'step': step}).loc['2018-12-20':'2019-12-31'] \
  .to_csv(HERE / 'night-and-step-2019.csv', index_label='night')
print(json.dumps(res, indent=2))
