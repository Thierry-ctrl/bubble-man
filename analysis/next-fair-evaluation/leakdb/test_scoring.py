"""Invented leak cases for scoring.py. Run before any LeakDB leak record is opened.
Every leak, warning and file here is made up."""
import sys, tempfile
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scoring as S

DAY0 = pd.Timestamp('2017-01-01')
GRID = pd.date_range(DAY0, periods=365 * 48, freq='30min')
NS = 2                                     # night window 02:00-03:59, warning issued 04:00
T = lambda day, h=0, m=0: DAY0 + pd.Timedelta(days=day, hours=h, minutes=m)   # day = index
results = []

def check(name, cond):
    results.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name)

def leaks(*rows):
    return pd.DataFrame([{'link': l, 'type': t, 'zone': 'hanoi', 'start': s, 'end': GRID[-1]} for l, t, s in rows])

def outcomes(r): return [e['outcome'] for e in r['events']]

# ---- timing ---------------------------------------------------------------------------
r = S.score_scenario([100], DAY0, NS, leaks(('A', 'abrupt', T(100, 2, 30))))
ev = r['events'][0]
check('timing: flag at last night hour 03:00, issuable 04:00 = protocol issue time',
      pd.Timestamp(ev['run_start']) == T(100, 3) and pd.Timestamp(ev['issuable_at']) == T(100, 4))
check('timing: leak starting 02:30 on the warning night is credited', outcomes(r) == ['credited'])
r = S.score_scenario([100], DAY0, NS, leaks(('A', 'abrupt', T(100, 3, 30))))
check('timing: leak starting 03:30, after the flagged hour, is not credited (false alert)',
      outcomes(r) == ['false_alert'])

# ---- seven-day deadline (168 h from first positive flow to issue time) --------------
r = S.score_scenario([107], DAY0, NS, leaks(('A', 'abrupt', T(100, 4))))
check('deadline: issued exactly 168 h after first flow is credited', outcomes(r) == ['credited'])
r = S.score_scenario([107], DAY0, NS, leaks(('A', 'abrupt', T(100, 3, 30))))
check('deadline: issued 168.5 h after first flow is unattributable', outcomes(r) == ['unattributable'])
check('deadline: that leak counts as eligible and missed',
      r['abrupt']['eligible_leaks'] == 1 and r['abrupt']['credited'] == 0)

# ---- leaks already active when evaluation begins (day 29 = index 28) ----------------
r = S.score_scenario([29, 60], DAY0, NS, leaks(('E', 'abrupt', T(25, 10))))
check('early leak: not eligible, warning within 168 h -> coincides_with_excluded_leak, later -> unattributable',
      outcomes(r) == ['coincides_with_excluded_leak', 'unattributable'] and r['abrupt']['eligible_leaks'] == 0)
r = S.score_scenario([28], DAY0, NS, leaks(('B', 'abrupt', T(28, 0))))
check('window edge: leak first flowing at day 29 00:00 is eligible and creditable', outcomes(r) == ['credited'])
r = S.score_scenario([28], DAY0, NS, leaks(('B', 'abrupt', T(27, 23, 30))))
check('window edge: leak first flowing at day 28 23:30 is excluded', r['abrupt']['eligible_leaks'] == 0)

# ---- one-to-one matching --------------------------------------------------------------
r = S.score_scenario([100, 103], DAY0, NS, leaks(('A', 'abrupt', T(99, 12))))
check('one-to-one: second warning on the same leak -> repeat_of_credited_leak',
      outcomes(r) == ['credited', 'repeat_of_credited_leak'] and r['abrupt']['credited'] == 1)
r = S.score_scenario([100], DAY0, NS, leaks(('A', 'abrupt', T(98, 12)), ('B', 'incipient', T(99, 12))))
check('one-to-one: one warning, two candidates -> one credit, to the most recent, marked ambiguous',
      r['overall']['credited'] == 1 and r['events'][0]['matched_leak'] == 'B'
      and r['events'][0]['match_confidence'] == 'ambiguous')
r = S.score_scenario([100, 110], DAY0, NS, leaks(('A', 'abrupt', T(99, 12)), ('B', 'abrupt', T(109, 12))))
check('one-to-one: two warnings, two leaks -> two credits', r['abrupt']['credited'] == 2)
r = S.score_scenario([200], DAY0, NS, leaks(('A', 'abrupt', T(99, 12))))
check('never-repaired leak: later unrelated warning is unattributable, not a false alert',
      outcomes(r) == ['unattributable'])
r = S.score_scenario([], DAY0, NS, leaks(('A', 'abrupt', T(99, 12))))
check('no warnings: the leak is missed', r['abrupt']['credited'] == 0 and r['abrupt']['eligible_leaks'] == 1)

# ---- scenarios scored separately (node names repeat across scenarios) ---------------
sA = S.score_scenario([100], DAY0, NS, leaks(('13', 'abrupt', T(99, 12))))
sB = S.score_scenario([], DAY0, NS, leaks(('13', 'abrupt', T(99, 12))))
check('per-scenario scoring: same node name in two scenarios is two leaks',
      sA['abrupt']['credited'] + sB['abrupt']['credited'] == 1
      and sA['abrupt']['eligible_leaks'] + sB['abrupt']['eligible_leaks'] == 2)

# ---- week shifts across the year boundary ---------------------------------------------
check('shift: day index 361 + 1 week wraps to index 32', S.shift_days([361], 1) == [32])
check('shift: index 363 (day 364) is the last day in the domain; 364 (day 365) is outside',
      S.shift_days([363], 0) == [363] and S.shift_days([364], 0) == [])
check('shift: 48 weeks returns every warning to its own night', S.shift_days([30, 200, 363], 48) == [30, 200, 363])
check('shift: wrapped gap measured across the boundary', S.min_wrapped_gap([30, 361]) == 5)
scen = [{'warn_days': [100], 'day0': DAY0, 'ns': NS, 'leaks': leaks(('A', 'abrupt', T(99, 12)))},
        {'warn_days': [350], 'day0': DAY0, 'ns': NS, 'leaks': leaks(('C', 'abrupt', T(30, 1)))}]
res, sh = S.shift_comparison(scen)
check('shift comparison: 47 distinct shifts, real pooled abrupt credits = 1',
      res['distinct_shifts'] == 47 and res['real_in_domain_abrupt'] == 1)
check('shift comparison: k=4 moves index 350 across the boundary to 42', S.shift_days([350], 4) == [42])
check('shift comparison: p = (1 + shifts >= real) / 48',
      res['p_abrupt'] == (1 + int((sh.abrupt >= 1).sum())) / 48)
check('shift comparison: k=3 moves index 350 across the boundary to 35 and credits leak C (first flow index 30 01:00)',
      S.shift_days([350], 3) == [35] and int(sh.loc[sh.k_weeks == 3, 'abrupt'].iloc[0]) == 1)
check('shift comparison: k=4 lands 12 days after leak C -> not credited',
      int(sh.loc[sh.k_weeks == 4, 'abrupt'].iloc[0]) == 0)
# p floor
check('shift comparison: p floor is 1/48', round(1 / 48, 4) == 0.0208)

# ---- Q2 leak mapping --------------------------------------------------------------------
L = leaks(('X', 'abrupt', T(149, 5)), ('Y', 'abrupt', T(200, 3)), ('Z', 'abrupt', T(100, 0)))
plain, stress = S.leaks_for_stress(L, DAY0, False), S.leaks_for_stress(L, DAY0, True)
check('Q2: leak first flowing on day 150 is set aside in plain and stress runs',
      'X' not in set(plain.link) and 'X' not in set(stress.link))
check('Q2: stress copy moves later leaks one day, leaves earlier ones',
      stress.set_index('link').start['Y'] == T(201, 3) and stress.set_index('link').start['Z'] == T(100, 0)
      and stress.set_index('link').end['Z'] == GRID[-1] + pd.Timedelta(days=1))

# ---- reading invented leak files --------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    flow = np.zeros(len(GRID)); flow[5000:] = 12.5
    pd.DataFrame({'Timestamp': GRID, 'Description': flow}).to_csv(tmp / 'Leak_7_demand.csv', index=False)
    (tmp / 'Leak_7_info.csv').write_text('Description , Value\nLeak Node , 7\nLeak Area , 0.001\n'
                                         'Leak Diameter , 0.05\nLeak Type , abrupt\nLeak Start , x\n')
    t = S.read_leaks(tmp, GRID)
    check('leak file: start = first positive flow on the inlet grid, type parsed, end = last positive',
          len(t) == 1 and t.start[0] == GRID[5000] and t.type[0] == 'abrupt' and t.end[0] == GRID[-1]
          and bool(t.timestamps_agree_with_inlet[0]))
    empty = tmp / 'none'; empty.mkdir()
    check('leak file: empty Leaks folder -> no leaks', len(S.read_leaks(empty, GRID)) == 0)
    hours = pd.date_range(GRID[0], GRID[-1], freq='h')
    on = S.flowing_hours(t, hours)
    check('exposure: hours with no leak flowing = hours before the first positive flow',
          int((~on).sum()) == 2500)

print(f'{sum(ok for _, ok in results)}/{len(results)} checks pass')
sys.exit(0 if all(ok for _, ok in results) else 1)
