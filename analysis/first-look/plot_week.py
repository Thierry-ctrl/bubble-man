from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
flow = pd.read_csv(ROOT/'data/l-town/readings/2018_SCADA_Flows.csv', sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')
truth = pd.read_csv(ROOT/'data/l-town/reference/2018_Leakages.csv', sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')
week = flow.loc['2018-03-02':'2018-03-08']
leak = truth.loc[week.index, 'p673']
assert len(week) == 2016 and week.index.is_unique
assert not week.isna().any().any() and not leak.isna().any()
assert (week.index.to_series().diff().dropna() == pd.Timedelta(minutes=5)).all()
onset = leak[leak > 0].index[0]
assert onset == pd.Timestamp('2018-03-05 15:45')

plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11, 'axes.spines.top':False, 'axes.spines.right':False})
fig, (ax, ref) = plt.subplots(2, 1, figsize=(11, 6.8), sharex=True, gridspec_kw={'height_ratios':[2.3, 1]})
fig.subplots_adjust(left=.10, right=.97, top=.83, bottom=.19, hspace=.44)
fig.suptitle('What changes when a leak starts?', x=.10, y=.97, ha='left', fontsize=21, weight='bold')
fig.text(.10, .91, 'L-Town simulated data  |  March 2–8, 2018  |  Readings every 5 minutes', color='#4b5563')
ax.plot(week.index, week['p227'], color='#146aab', linewidth=1)
ax.set_title('1. What the flow meter sees — meter p227', loc='left', fontsize=13, pad=12)
ax.set_ylabel('Water flow (m³/hour)')
ax.set_ylim(0, week['p227'].max()*1.14)
ax.text(onset+pd.Timedelta(hours=2), ax.get_ylim()[1]*.94, 'Recorded leak begins\nMarch 5, 15:45', fontsize=10, va='top', color='#93431b')
ref.step(leak.index, leak, where='post', color='#b95523', linewidth=2)
ref.fill_between(leak.index, leak, step='post', color='#b95523', alpha=.12)
ref.set_title('2. The answer sheet — known leak on pipe p673', loc='left', fontsize=13, pad=12)
ref.set_ylabel('Leak flow (m³/hour)')
ref.set_ylim(-2, 37)
ref.set_yticks([0, 15, 30])
ref.text(pd.Timestamp('2018-03-06 08:00'), 31, 'About 28.4 m³/hour leaking', fontsize=10, color='#93431b')
for a in (ax,ref):
    a.axvline(onset, color='#93431b', linestyle='--', linewidth=1.2)
    a.grid(axis='y', alpha=.16)
    a.spines['left'].set_color('#9ca3af')
    a.spines['bottom'].set_color('#9ca3af')
ref.xaxis.set_major_locator(mdates.DayLocator())
ref.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ref.set_xlim(week.index[0], week.index[-1])
ref.set_xlabel('Date (dataset timestamps)')
fig.text(.10,.105,'The lower line is known simulation truth, not a prediction from our software.',fontsize=10)
fig.text(.10,.067,'Other leaks already exist in this period. Flow changes also reflect demand and network operation.',fontsize=9,color='#4b5563')
fig.text(.10,.033,'Source: BattLeDIM, Vrachimis et al. • zenodo.org/records/4017659 • CC BY 4.0',fontsize=9,color='#4b5563')
fig.savefig(OUT/'first-week.png',dpi=170,facecolor='white')
summary={'source':'https://zenodo.org/records/4017659','range':['2018-03-02 00:00','2018-03-08 23:55'],'rows':len(week),'missing_flow_values':int(week.isna().sum().sum()),'meter_plotted':'p227','leak_reference':'p673','known_onset':str(onset),'raw_readings':True,'aggregation':'none','all_meter_daily_means':{str(k):{a:round(float(b),3) for a,b in v.items()} for k,v in week.resample('D').mean().to_dict('index').items()}}
(OUT/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(OUT/'first-week.png')
