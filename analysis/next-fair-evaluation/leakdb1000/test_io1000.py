"""Invented files for the Index-format readers (correction 1). No LeakDB data."""
import sys, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import io1000
res = []
def check(n, ok): res.append(ok); print(('PASS ' if ok else 'FAIL ') + n)
rng = np.random.default_rng(0); v = rng.uniform(2000, 5000, io1000.N).round(1)
grid = pd.date_range(io1000.ORIGIN, periods=io1000.N, freq='30min')
with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    pd.DataFrame({'Index': np.arange(1, io1000.N + 1), 'Value': v}).to_csv(t / 'i.csv', index=False)
    pd.DataFrame({'Timestamp': grid, 'Value': v}).to_csv(t / 't.csv', index=False)
    a, b = io1000.read_inlet(t / 'i.csv'), io1000.read_inlet(t / 't.csv')
    check('Index-format inlet = same series as the Timestamp-format file', a.equals(b) and a.index[0] == io1000.ORIGIN)
    check('Index-format: step n placed at origin + (n-1) x 30 min', a.index[17519] == io1000.ORIGIN + pd.Timedelta(minutes=30 * 17519))
    bad = pd.DataFrame({'Index': np.r_[np.arange(1, 100), np.arange(101, io1000.N + 2)], 'Value': v}); bad.to_csv(t / 'b.csv', index=False)
    try: io1000.read_inlet(t / 'b.csv'); ok = False
    except AssertionError: ok = True
    check('Index with a gap -> stop (not silently realigned)', ok)
    (t / 'L').mkdir(); lf = np.zeros(io1000.N); lf[9001:] = 50.0
    pd.DataFrame({'Index': np.arange(1, io1000.N + 1), 'Description': lf}).to_csv(t / 'L/Leak_7_demand.csv', index=False)
    (t / 'L/Leak_7_info.csv').write_text('Description , Value\nLeak Node , 7\nLeak Diameter , 0.05\nLeak Type , incipient\n')
    L = io1000.read_leaks(t / 'L', a.index)
    check('Index-format leak file: first flow at row 9001 -> grid[9001], format recorded, positions agree',
          L.start[0] == a.index[9001] and L.file_index_format[0] == 'Index' and bool(L.positions_agree_with_inlet[0]) and L.type[0] == 'incipient')
print(f'{sum(res)}/{len(res)} checks pass'); sys.exit(0 if all(res) else 1)
