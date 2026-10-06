# Step 2–3 record — 2019 flow readings and noise (protocol 9724c60)

Recorded before warnings were generated and before any 2019 leak record was opened.

- `2019_SCADA_Flows.csv`: md5 `28fc99fdcbf80fcd26079e7fe602d6dc` — matches Zenodo.
  105,120 rows, 1 Jan 00:00 – 31 Dec 23:55, continuous with 2018, **no missing values**.
- **Noise, common basis (350 changes, 16 Jan – 31 Dec 2019): std 17.34, robust 16.77 m³/h.**
  2018 was 6.04 and 2.98. Reported, not gating. The original 2018 noise stop failed and
  remains failed.

## Finding: the 2019 weekly demand cycle sits one day later than the calendar

From the 2019 readings alone: each 2019 calendar weekday's average 24-hour flow shape
matches the **previous** weekday's 2018 shape with r = 1.000 (2019 Sunday ↔ 2018 Saturday,
2019 Saturday ↔ 2018 Friday, and so on). The simulated demand cycle repeats every 365 days,
and 2018 is 52 weeks + 1 day, so in 2019 it lands one weekday later.

The frozen baseline assigns day types by **calendar date**. In 2019 it therefore compares
Saturday-like Sundays with the Sun–Thu profile, Friday-like Saturdays with the Saturday
profile, and Thursday-like Fridays with the Friday profile. That produces a large weekly
swing in the night residual (2019 means: Sun 94.9, Fri 52.2, others 62–71 m³/h) and
explains most of the jump in noise.

**This is not a code defect.** The code does exactly what the protocol specifies. Re-aligning
the day types now would change the method after seeing 2019 data, so the rule and baseline
remain as frozen and the run continues. The consequence is reported as a central result.
