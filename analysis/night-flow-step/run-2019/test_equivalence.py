"""Before any 2019 file exists: the run code must reproduce the 2018 results exactly."""
import sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from common import ROOT, read_flows, night_and_step, generate_warnings, noise_changes, robust_sigma
from night_signal import night_series

n_ref, s_ref = night_series()
n_new, s_new = night_and_step(read_flows(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv'))
assert np.allclose(n_ref.values, n_new.values, equal_nan=True), 'night values differ'
assert np.allclose(s_ref.values, s_new.values, equal_nan=True), 'step values differ'
w = generate_warnings(s_new, '2018-01-15', '2018-12-31')
assert [str(d.date()) for d in w] == ['2018-02-03', '2018-03-06', '2018-05-11', '2018-08-08', '2018-10-06'], w
c = noise_changes(n_new, 2018)
assert len(c) == 350 and f'{c.std():.2f}' == '6.04' and f'{robust_sigma(c):.2f}' == '2.98'
print('equivalence OK: identical night and step series; same 5 warnings; 350 changes, std 6.04, robust 2.98')
