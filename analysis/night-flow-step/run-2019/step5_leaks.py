"""Protocol 9724c60, step 5: verify 2019 leak records and build the leak list (§6)."""
import collections, hashlib, json, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from common import ROOT
sys.path.insert(0, str(ROOT / 'analysis/scorer'))
from leak_scorer import load_leaks, add_observed_activity

f = ROOT / 'data/l-town/reference/2019_Leakages.csv'
md5 = hashlib.md5(f.read_bytes()).hexdigest()
assert md5 == 'e1f0a43683813a90a9fec8562dde599b', f'checksum mismatch {md5}'
truth19 = pd.read_csv(f, sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')

# zones by the same network-map procedure as 2018 (recomputed, then checked against the saved table)
lines = (ROOT / 'data/l-town/L-TOWN.inp').read_text(errors='ignore').splitlines(); sec = None; links = {}
for line in lines:
    l = line.strip()
    if l.startswith('['): sec = l.strip('[]').upper(); continue
    if not l or l.startswith(';') or sec is None: continue
    p = l.split()
    if sec in ('PIPES', 'PUMPS', 'VALVES') and len(p) >= 3: links[p[0]] = (p[1], p[2])
adj = collections.defaultdict(set)
for lid, (a, b) in links.items():
    if lid in {'p227', 'p235', 'PUMP_1'}: continue
    adj[a].add(b); adj[b].add(a)
seen, comps = set(), []
for n in list(adj):
    if n in seen: continue
    st, c = [n], set()
    while st:
        x = st.pop()
        if x in c: continue
        c.add(x); seen.add(x); st.extend(adj[x] - c)
    comps.append(c)
MAIN = sorted(comps, key=len, reverse=True)[0]
zone = lambda link: 'main' if any(e in MAIN for e in links[link]) else 'AreaC'

sched = load_leaks(ROOT / 'research/2026-09-21/battledim-config.yaml')
in19 = sched[(sched.end >= '2019-01-01') & (sched.start <= '2019-12-31 23:55')].copy()
in19['zone'] = [zone(l) for l in in19.link]
saved = dict(pd.read_csv(ROOT / 'analysis/scorer/leak-zones-from-network-map.csv')[['link', 'zone']].values)
assert all(saved[l] == z for l, z in zip(in19.link, in19.zone)), 'zone assignment disagrees with saved table'
missing_cols = [l for l in in19.link if l not in truth19.columns]
assert not missing_cols, f'leaks missing from the 2019 file: {missing_cols}'

act = add_observed_activity(in19, f)
flowing_at_start = sorted(c for c in truth19.columns if truth19[c].iloc[0] > 0)
CARRIED = {'p427': '2018-02-16 04:15', 'p654': '2018-07-07 09:10', 'p810': '2018-07-30 18:40'}
assert set(CARRIED) <= set(flowing_at_start), flowing_at_start
for link, t in CARRIED.items():
    act.loc[act.link == link, 'start'] = pd.Timestamp(t)
act['status'] = ['carried over (excluded)' if l in CARRIED
                 else 'Area C (not in signal)' if z != 'main'
                 else ('eligible' if pd.Timestamp('2019-01-01') <= s <= pd.Timestamp('2019-12-31 23:00') else 'other')
                 for l, z, s in zip(act.link, act.zone, act.start)]
scorer_list = act[act.zone == 'main'].copy()          # eligible 2019 leaks + carried-over (2018 start)
cols = ['link', 'type', 'zone', 'configured_start', 'start', 'end', 'status']
act[cols].sort_values('start').to_csv(HERE / 'leaks-2019-all.csv', index=False)
scorer_list[['link', 'type', 'zone', 'start', 'end', 'status']].to_csv(HERE / 'leaks-2019-scorer-list.csv', index=False)
el = act[act.status == 'eligible']
res = {'protocol': '9724c60', 'file': '2019_Leakages.csv', 'md5': md5, 'md5_matches_zenodo': True,
       'leaks_active_in_2019': int(len(act)), 'flowing_at_first_2019_timestamp': flowing_at_start,
       'carried_over_main_excluded': sorted(CARRIED), 'area_c_leaks': sorted(act[act.zone != 'main'].link),
       'eligible_main_zone': int(len(el)), 'eligible_sudden': int((el.type == 'abrupt').sum()),
       'eligible_gradual': int((el.type == 'incipient').sum()),
       'S1_at_least_3_eligible_sudden': bool((el.type == 'abrupt').sum() >= 3)}
(HERE / 'step5-leaks.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps(res, indent=2))
print(act[cols].sort_values('start').to_string(index=False))
