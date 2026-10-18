"""Invented cases for yw.py. No Yorkshire data."""
import sys, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import yw
res = []
def check(n, ok): res.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + n)

with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    g = pd.date_range(yw.START, periods=3 * 96, freq='15min')
    rows = [('11', x.strftime('%d/%m/%Y'), x.strftime('%H:%M:%S'), 2.0, 'V') for x in g]
    rows[8] = ('11', rows[8][1], rows[8][2], 2.0, 'I')                   # invalid reading 02:00 day 1
    rows[100] = ('11', rows[100][1], rows[100][2], -1.0, 'V')            # negative
    del rows[200]                                                      # a missing row
    rows.append(('11', rows[150][1], rows[150][2], 2.0, 'V'))           # duplicated stamp (clock change)
    rows += [('12', x.strftime('%d/%m/%Y'), x.strftime('%H:%M:%S'), 1.0, 'V') for x in g]
    pd.DataFrame(rows, columns=['DMA', 'Date', 'Time', 'Flow', 'Flow Validity Code']).to_csv(t / 'a.csv', index=False)
    S, rep = yw.read_area(t / 'a.csv')
    s = S['11']
    check('L/s x 3.6 -> 7.2 m3/h; 365-day 30-min grid', s.iloc[0] == 7.2 and len(s) == 365 * 48)
    check('invalid reading -> that 30-min value missing', np.isnan(s.loc['2016-04-01 02:00']))
    check('negative valid flow -> missing and counted', np.isnan(s.iloc[50]) and rep['negative_valid_flows'] == 1)
    check('missing row -> missing', np.isnan(s.iloc[100]))
    check('duplicated stamp (autumn clock change) -> both readings dropped', np.isnan(s.iloc[75]) and rep['duplicated_stamps'] == 2)
    check('days beyond the data are missing, DMA 12 intact', np.isnan(s.iloc[-1]) and S['12'].iloc[:144].notna().all())
    f = yw.to_frozen_reader(S['12'])
    check('frozen reader receives the same series', np.allclose(f.values[:144], 3.6) and f.index[0] == yw.START)
    pd.DataFrame({'Ref': ['a', 'b', 'c'], 'DMA Number': ['011', '12', '11'], 'Repair Completion Date': ['30/05/2016', '01/06/2016', 'x']}).to_csv(t / 'r.csv', index=False)
    rp, rr = yw.read_repairs(t / 'r.csv')
    check('repairs: DMA and date columns found, unparseable date counted', len(rp) == 2 and rr['unparseable_dates'] == 1 and rp.completed[0] == pd.Timestamp('2016-05-30') and rp.dma[0] == '11')
    pd.DataFrame({'DMA': ['1'], 'Date raised': ['1/1/2016'], 'Date completed': ['2/1/2016']}).to_csv(t / 'r2.csv', index=False)
    try: yw.read_repairs(t / 'r2.csv'); ok = False
    except AssertionError: ok = True
    check('ambiguous repair date columns -> stop', ok)

# association windows
C = 100; rep = pd.DataFrame({'dma': ['A'], 'completed': [yw.START + pd.Timedelta(days=C)]})
a = lambda w: yw.associate({'A': w}, rep, {'A'})[0]
check('warning 28 days before completion -> preceded', a([C - 28])['preceded'] == 1)
check('warning 29 days before -> not preceded', a([C - 29])['preceded'] == 0)
check('warning 1 day before -> preceded, 1 day', a([C - 1])['preceded'] == 1 and a([C - 1])['median_days_before'] == 1)
check('same-day warning only -> counted separately, not preceded', a([C])['preceded'] == 0 and a([C])['same_day_only'] == 1)
check('warning after completion -> not preceded', a([C + 3])['preceded'] == 0)
check('other DMA warning never counts', yw.associate({'B': [C - 3]}, rep, {'A', 'B'})[0]['preceded'] == 0)
check('repair in a not-assessable DMA -> not eligible', yw.associate({'A': []}, rep, set())[0]['eligible_repairs'] == 0)
early = pd.DataFrame({'dma': ['A'], 'completed': [yw.START + pd.Timedelta(days=55)]})
check('completion before day 57 -> not eligible (no full lookback)', yw.associate({'A': [40]}, early, {'A'})[0]['eligible_repairs'] == 0)
check('warning followed by a repair 1-28 days later counted', a([C - 10, C + 3])['warnings_followed_by_repair_within_28d'] == 1)
# shifts
check('shift wraps across the end of the domain', yw.shift_days([361], 1) == [32])
sres, sh = yw.shift_comparison({'A': [C - 5]}, rep, {'A'})
check('47 shifts; real = 1; p = (1 + #>=1)/48', sres['shifts'] == 47 and sres['real_in_domain'] == 1 and sres['p'] == (1 + sum(x >= 1 for x in sh)) / 48)
print(f'{sum(res)}/{len(res)} checks pass'); sys.exit(0 if all(res) else 1)
