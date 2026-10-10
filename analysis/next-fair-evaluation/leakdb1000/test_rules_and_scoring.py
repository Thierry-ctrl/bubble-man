"""Invented cases, run before any 1,000-scenario reading is opened. Everything here is made up."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import prospective as P
import rules as R
sys.path.insert(0, str(HERE.parents[1] / 'scorer'))

DAY0 = pd.Timestamp('2017-01-01'); NS = 2; END = DAY0 + pd.Timedelta(days=364, hours=23, minutes=30)
T = lambda day, h=0, m=0: DAY0 + pd.Timedelta(days=day, hours=h, minutes=m)
res = []
def check(name, ok): res.append(ok); print(('PASS ' if ok else 'FAIL ') + name)
def leaks(*rows):
    return pd.DataFrame([{'link': r[0], 'type': r[1], 'zone': 'hanoi', 'start': r[2], 'end': r[3] if len(r) > 3 else END} for r in rows])
oc = lambda r: [e['outcome'] for e in r['events']]

# ---- timing definitions ----------------------------------------------------------------
tf, tl, ti = P.night_times(DAY0, 100, NS)
check('timing: contributing readings 02:00..03:30, complete 03:30, issuable 04:00',
      (tf, tl, ti) == (T(100, 2), T(100, 3, 30), T(100, 4)))
# ---- leak before / during / after the contributing interval ----------------------------
for h, m, want in [(1, 30, 'credited'), (2, 0, 'credited'), (3, 0, 'credited'), (3, 30, 'credited'),
                   (4, 0, 'false_alert'), (10, 0, 'false_alert')]:
    r = P.score([100], DAY0, NS, leaks(('A', 'abrupt', T(100, h, m))))
    check(f'leak first flowing {h:02d}:{m:02d} on the warning night -> {want}', oc(r) == [want])
r = P.score([100], DAY0, NS, leaks(('A', 'abrupt', T(100, 3, 30))))
check('delay measured to issue time: 03:30 onset -> 0.5 h', r['leaks'][0]['delay_h'] == 0.5)
r = P.score([100], DAY0, NS, leaks(('A', 'abrupt', T(99, 23, 0))))
check('leak from the previous evening -> credited, delay 5 h', oc(r) == ['credited'] and r['leaks'][0]['delay_h'] == 5.0)
# ---- a pre-existing warning must not claim a later leak --------------------------------
r = P.score([100, 107], DAY0, NS, leaks(('A', 'abrupt', T(100, 4))))
check('pre-existing warning: night 100 cannot claim a leak first flowing 04:00; night 107 (168 h) can',
      oc(r) == ['false_alert', 'credited'] and r['events'][1]['leak'] == 'A')
r = P.score([100], DAY0, NS, leaks(('A', 'abrupt', T(100, 4)), ('B', 'abrupt', T(99, 12))))
check('pre-existing warning with an earlier leak claims that one, never the later one',
      r['events'][0]['leak'] == 'B' and [p['outcome'] for p in r['leaks'] if p['link'] == 'A'] == ['missed'])
# ---- deadline ----------------------------------------------------------------------------
check('deadline: 168 h exactly credited', oc(P.score([107], DAY0, NS, leaks(('A', 'abrupt', T(100, 4))))) == ['credited'])
check('deadline: 168.5 h unattributable', oc(P.score([107], DAY0, NS, leaks(('A', 'abrupt', T(100, 3, 30))))) == ['unattributable'])
# ---- leaks ending around the night -------------------------------------------------------
check('leak flowing in the night but stopped before issue -> retrospective_association',
      oc(P.score([100], DAY0, NS, leaks(('A', 'abrupt', T(99, 12), T(100, 3, 30))))) == ['retrospective_association'])
check('leak stopped before the contributing interval -> false_alert',
      oc(P.score([100], DAY0, NS, leaks(('A', 'abrupt', T(90, 12), T(100, 1, 30))))) == ['false_alert'])
# ---- leaks active when evaluation begins -------------------------------------------------
r = P.score([29, 60], DAY0, NS, leaks(('E', 'abrupt', T(25, 10))))
check('early leak: excluded; within 168 h -> coincides_with_excluded_leak; later -> unattributable',
      oc(r) == ['coincides_with_excluded_leak', 'unattributable'] and r['abrupt']['eligible'] == 0)
check('window edge: first flow at day 29 00:00 is eligible',
      P.score([28], DAY0, NS, leaks(('B', 'abrupt', T(28))))['abrupt'] == {'eligible': 1, 'credited': 1})
# ---- one-to-one --------------------------------------------------------------------------
r = P.score([100, 103], DAY0, NS, leaks(('A', 'abrupt', T(99, 12))))
check('one-to-one: second warning -> repeat_of_credited_leak', oc(r) == ['credited', 'repeat_of_credited_leak'])
r = P.score([100], DAY0, NS, leaks(('A', 'abrupt', T(98, 12)), ('B', 'incipient', T(99, 12))))
check('one warning, two candidates -> one credit, most recent, ambiguous',
      r['events'][0]['leak'] == 'B' and r['events'][0]['confidence'] == 'ambiguous' and r['outcomes']['credited'] == 1)
r = P.score([100, 110], DAY0, NS, leaks(('A', 'abrupt', T(99, 12)), ('B', 'abrupt', T(109, 12))))
check('two warnings, two leaks -> two credits', r['abrupt']['credited'] == 2)
# ---- agreement with the locked scorer where its hour-start convention does not bite ------
sys.path.insert(0, str(HERE.parents[0] / 'leakdb')); import scoring as S
rng = np.random.default_rng(1); agree = True
for _ in range(200):
    days = sorted(rng.choice(np.arange(28, 365), size=6, replace=False))
    st = [T(int(rng.integers(20, 360)), int(rng.choice([0, 5, 9, 12, 18, 23]))) for _ in range(2)]
    lk = leaks(('A', 'abrupt', st[0]), ('B', 'incipient', st[1]))
    old = S.score_scenario(days, DAY0, NS, lk); new = P.score(days, DAY0, NS, lk)
    agree &= [e['outcome'] for e in sorted(old['events'], key=lambda e: e['run_start'])] == oc(new)
    agree &= old['abrupt']['credited'] == new['abrupt']['credited']
check('200 random invented scenarios with onsets away from the night edge: same outcomes as the locked scorer', agree)
# ---- the edge the locked scorer got wrong --------------------------------------------------
lk = leaks(('A', 'abrupt', T(174, 3, 30)))
check('locked scorer: 03:30 onset -> false_alert; prospective rule -> credited',
      [e['outcome'] for e in S.score_scenario([174], DAY0, NS, lk)['events']] == ['false_alert']
      and oc(P.score([174], DAY0, NS, lk)) == ['credited'])
# ---- shifts across the year boundary -------------------------------------------------------
check('shift: index 361 + 1 week wraps to 32', P.shift_days([361], 1) == [32])
check('shift: day 365 (index 364) outside the domain', P.shift_days([364], 0) == [])
scen = [{'warn_days': [100], 'day0': DAY0, 'ns': NS, 'leaks': leaks(('A', 'abrupt', T(99, 12)))},
        {'warn_days': [350], 'day0': DAY0, 'ns': NS, 'leaks': leaks(('C', 'abrupt', T(30, 1)))}]
sres, sh = P.shift_comparison(scen)
check('shift comparison: 47 shifts, real = 1, k=3 wraps 350 -> 35 and credits C, p = (1+#>=)/48',
      sres['distinct_shifts'] == 47 and sres['real_in_domain_abrupt'] == 1 and P.shift_days([350], 3) == [35]
      and int(sh.loc[sh.k_weeks == 3, 'abrupt'].iloc[0]) == 1 and sres['p_abrupt'] == (1 + int((sh.abrupt >= 1).sum())) / 48)
# ---- leak-free exposure --------------------------------------------------------------------
check('exposure: leak from day 100 00:00 to end -> (100-28) days of leak-free hours',
      P.leak_free_hours(leaks(('A', 'abrupt', T(100))), DAY0) == 72 * 24)
# ---- adaptive threshold edge cases ---------------------------------------------------------
st = np.full(365, np.nan); st[8:] = np.tile([1.0, -1.0, 2.0, -2.0], 90)[:357]
Tf = 99.0; Ta = R.adaptive_thresholds(st, Tf)
check('adaptive: frozen T until 20 values exist in days D-56..D-9 (first adaptive at index 36)',
      (Ta[:36] == Tf).all() and Ta[36] != Tf)
st2 = st.copy(); st2[100] = 1e6
Tb = R.adaptive_thresholds(st2, Tf)
check('adaptive: T(D) never uses steps of D or D-1..D-8 (spike at 100 changes T only from index 109)',
      np.array_equal(Tb[:109], Ta[:109]) and Tb[109] >= Ta[109])
st3 = st.copy(); st3[40:80] = np.nan
check('adaptive: missing steps are skipped; frozen T when fewer than 20 remain',
      R.adaptive_thresholds(st3, Tf)[85] == Tf)
st4 = np.full(365, np.nan); st4[8:] = 5.0
check('adaptive: zero spread -> frozen T', (R.adaptive_thresholds(st4, Tf) == Tf).all())
lo = np.full(365, 1.0); lo[200] = 50; Tt = np.full(365, 10.0)
w = R.warn(lo, Tt, NS, DAY0)
check('warn: per-night threshold, issue at end of window, armed logic', [x[0] for x in w] == [200] and w[0][1] == T(200, 4))
print(f'{sum(res)}/{len(res)} checks pass'); sys.exit(0 if all(res) else 1)
