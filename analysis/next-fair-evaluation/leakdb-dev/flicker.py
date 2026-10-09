"""DEVELOPMENT, labels retrospective: how leak flow behaves at night inside each leak's active period."""
import json
from common_dev import *
rows = []
for k in sorted(L.scenario.unique()):
    s = inlet(k); a = A[A.scenario == k].iloc[0]; ns = int(a.night_start_hour)
    for name, v in leak_flow(k, s.index).items():
        rec = L[(L.scenario == k) & (L.link.astype(str) == name)]
        if rec.empty or rec.never_flowed.iloc[0]: continue
        rec = rec.iloc[0]
        n = v.values.reshape(-1, 2).mean(1).reshape(-1, 24)[:, ns:ns + 2].mean(1)
        d0 = int((rec.start - s.index[0]) / pd.Timedelta(days=1)) + 1; d1 = int((rec.end - s.index[0]) / pd.Timedelta(days=1))
        act = n[d0:d1]
        if len(act) < 7: continue
        big = act.max()
        rows.append({'scenario': k, 'type': rec.type, 'nights': len(act),
                     'share_nights_near_zero': float((act < 0.05 * big).mean()),
                     'on_off_switches_per_week': float((np.abs(np.diff(act)) > 0.5 * big).sum() / len(act) * 7),
                     'max_night_leak_flow': float(big)})
F = pd.DataFrame(rows); F.to_csv(HERE / 'dev-leak-night-behaviour.csv', index=False)
out = F.groupby('type')[['share_nights_near_zero', 'on_off_switches_per_week', 'max_night_leak_flow']].median().round(3).to_dict()
out['share_of_leaks_switching_at_least_weekly'] = F.groupby('type').apply(lambda g: round(float((g.on_off_switches_per_week >= 1).mean()), 3)).to_dict()
(HERE / 'dev-leak-night-behaviour.json').write_text(json.dumps(out, indent=2) + '\n'); print(json.dumps(out, indent=1))
