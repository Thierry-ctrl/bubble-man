"""Draw saved accounting ranges; never read utility readings or run a detector."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd

HERE = Path(__file__).resolve().parent
t = pd.read_csv(HERE / 'run/summary.csv')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.titleweight': 'bold'})
fig, axes = plt.subplots(1, 2, figsize=(13.6, 6.8), gridspec_kw={'width_ratios': [1.1, 1]})
fig.subplots_adjust(top=.73, bottom=.24, left=.10, right=.97, wspace=.26)
fig.patch.set_facecolor('#fbfcfe')
fig.text(.055, .944, 'What could account for the water flowing at night?', fontsize=21, weight='bold', color='#172b4d')
fig.text(.055, .893, 'Five Yorkshire zones • 2016–17 • conditional accounting, not measured losses', fontsize=12, color='#475569')
for y, r in enumerate(t.itertuples()):
    axes[0].plot([r.observed_q10_m3h, r.observed_q90_m3h], [y-.11, y-.11], color='#1875ba', lw=6, solid_capstyle='round')
    axes[0].plot(r.observed_median_m3h, y-.11, 'o', color='#0b4a7a', markersize=7)
    axes[0].plot([r.legitimate_use_low_m3h, r.legitimate_use_high_m3h], [y+.16, y+.16], color='#d58420', lw=6, solid_capstyle='round')
    axes[1].plot([100*r.variation_envelope_share_low, 100*r.variation_envelope_share_high], [y, y], color='#aab7c9', lw=2)
    axes[1].plot([100*r.conditional_plausible_share_low, 100*r.conditional_plausible_share_high], [y, y], color='#8049a0', lw=7, solid_capstyle='round')
    axes[1].text(101.5, y, f'{100*r.conditional_plausible_share_low:.0f}–{100*r.conditional_plausible_share_high:.0f}%', va='center', fontsize=11)
for ax in axes:
    ax.set_facecolor('#fbfcfe')
    ax.set_ylim(4.6, -.6)
    ax.grid(axis='x', color='#e2e8f0', linewidth=.7)
    ax.set_axisbelow(True)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', length=0)
axes[0].set_yticks(range(5), [f'DMA {int(x)}' for x in t.dma])
axes[1].set_yticks(range(5), [])
axes[0].set_title('Measured flow versus assumed ordinary use', loc='left', pad=14, fontsize=12)
axes[1].set_title('Conditional plausible leakage share', loc='left', pad=14, fontsize=12)
axes[0].set_xlabel('Water flow (m³/hour)')
axes[0].set_xlim(0, 22)
axes[1].set_xlabel('Share of measured night flow (%)')
axes[1].set_xlim(0, 114)
axes[1].set_xticks([0, 25, 50, 75, 100])
fig.legend(handles=[
    Line2D([0], [0], color='#1875ba', lw=6, marker='o', label='Observed: median and 10th–90th night percentiles'),
    Line2D([0], [0], color='#d58420', lw=6, label='Assumed legitimate use: broad rate scenarios'),
    Line2D([0], [0], color='#8049a0', lw=6, label='Possible remainder at median observed flow'),
    Line2D([0], [0], color='#aab7c9', lw=2, label='Also allowing 10th–90th night variation')],
    loc='lower left', bbox_to_anchor=(.05, .095), frameon=False, fontsize=10, ncol=2, columnspacing=2)
fig.text(.055, .067, 'Assumptions: household 1–4 L/property/hour; business 0.7–60.6. These are scenarios, not confidence intervals.', fontsize=10, color='#475569')
fig.text(.055, .035, 'Unknown large users, storage, boundaries and meter error can explain the remainder. Utility and customer leaks cannot be separated.', fontsize=9.5, color='#475569')
fig.savefig(HERE / 'run/night-flow-accounting.png', dpi=160, facecolor=fig.get_facecolor())
fig.savefig(HERE / 'run/night-flow-accounting.svg', facecolor=fig.get_facecolor())
plt.close(fig)
