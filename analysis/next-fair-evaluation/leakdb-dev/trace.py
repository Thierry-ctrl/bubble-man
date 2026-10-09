"""DEVELOPMENT: trace four representative warnings back through the readings and the rule.
Colours: blue = observed, orange = expected (January profile), red = leak flow (known truth,
shown retrospectively; the rule never sees it)."""
import json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common_dev import *
BLUE, ORANGE, RED, INK, MUTED = '#2a6fbb', '#e08a1e', '#c0262d', '#222222', '#888888'
CASES = [(42, 140, 205, 'A. Leak-free scenario 42: a warning every Saturday in June-July'),
         (336, 120, 185, 'B. Scenario 336: warning while a gradual leak keeps growing'),
         (148, 150, 200, 'C. Scenario 148: leak starts 03:30 inside the night window; warning scored false (timed 03:00), then 7-day spacing blocks'),
         (350, 70, 125, 'D. Scenario 350: a typical sudden leak, warned 16 h after it began')]
fig, axes = plt.subplots(8, 1, figsize=(11, 20), gridspec_kw={'height_ratios': [1.1, 1] * 4})
notes = {}
for i, (k, a, b, title) in enumerate(CASES):
    s = inlet(k); r = M.run(s, 'self_aligning'); D = M.hourly_days(s); ns = r.night_start_hour
    prof = M.learn(D)[1]
    obs = D[:, ns:ns + 2].mean(1); exp = np.array([prof[t][ns:ns + 2].mean() for t in r.day_type])
    lf = leak_flow(k, s.index); tot = sum(lf.values()) if lf else pd.Series(0.0, index=s.index)
    nl = tot.values.reshape(-1, 2).mean(1).reshape(-1, 24)[:, ns:ns + 2].mean(1)
    x = np.arange(a, b); wd = [d for d, _, _ in r.warnings if a <= d < b]
    ax = axes[2 * i]; ax.set_title(title, loc='left', fontsize=11, color=INK)
    ax.plot(x, obs[a:b], color=BLUE, lw=2, label='observed night flow')
    ax.plot(x, exp[a:b], color=ORANGE, lw=2, label='expected (January profile, assigned day type)')
    ax.set_ylabel('m³/h', color=MUTED)
    ax2 = axes[2 * i + 1]
    ax2.plot(x, r.step[a:b], color=INK, lw=1.5, label='step: last 2 nights minus 7 before')
    ax2.axhline(r.threshold, color=MUTED, ls='--', lw=1.2, label=f'threshold T = {r.threshold:.0f}')
    ax2.plot(x, nl[a:b], color=RED, lw=2, label='leak flow at night (truth, retrospective)')
    for d in wd:
        for axx in (ax, ax2): axx.axvline(d, color=MUTED, lw=0.8, alpha=0.6)
        ax2.annotate('warning', (d, r.step[d]), textcoords='offset points', xytext=(3, 4), fontsize=8, color=INK)
    ax2.set_ylabel('m³/h', color=MUTED); ax2.set_xlabel('day of the simulated year', color=MUTED)
    for axx in (ax, ax2):
        axx.spines[['top', 'right']].set_visible(False); axx.grid(axis='y', color='#eeeeee')
        axx.legend(loc='upper left', fontsize=8, frameon=False)
    notes[k] = {'threshold': round(r.threshold, 1), 'warning_days_in_view': wd,
                'steps_at_warnings': {d: round(float(r.step[d]), 1) for d in wd},
                'day_types_at_warnings': {d: r.day_type[d] for d in wd},
                'leak_night_flow_at_warnings': {d: round(float(nl[d]), 1) for d in wd}}
fig.tight_layout(); fig.savefig(HERE / 'traces.png', dpi=110)
(HERE / 'traces.json').write_text(json.dumps(notes, indent=2) + '\n'); print(json.dumps(notes, indent=1))
