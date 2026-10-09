# Correction note — 9 October 2026 (no score changes)

The locked LeakDB result (`RESULTS-LEAKDB.md`, commit 87e8160) and the 2019 L-Town result are
unchanged. This note corrects wording in the locked text, found during development diagnosis
of the same 490 scenarios.

## 1. LeakDB leaks do stop

`PROTOCOL-LEAKDB.md` (§8.3) and `RESULTS-LEAKDB.md` say LeakDB leaks "are never repaired"
and "never stop". That was taken from the generator code on GitHub, which sets every leak's
end to the end of the year. **The archived scenarios differ.**
- Each leak's info file records its own "Leak End".
- In none of the 508 leaks that flow does the flow reach the last timestamp.
- The median leak stops about 98 days before the end of the year. Median duration is 45
  days; the longest is 337 days.
- Observed flow stops within 1.75 hours of the recorded end for the median leak, though not
  for all.

**Effect on scores: none.** Scoring always used observed flow, from first to last positive
leak flow, as the protocol specified. False alerts were counted only when no leak was
flowing. The explanation of `unattributable` in `RESULTS-LEAKDB.md` should read: "a leak
was flowing, but it had started more than 7 days earlier".

## 2. "Gradual" leaks switch on and off

Nearly all of LeakDB's incipient ("gradual") leaks (98%) switch on and off at night at least
once a week. Their median is 2.7 switches per week, and about 31% of their active nights
carry almost no leak flow. Sudden leaks do not do this (0.4%). Their documented intent is
steady growth from zero; the archived flows do not show it
(`leakdb-dev/dev-leak-night-behaviour.json`).

**Effect on scores: none.** But it changes how the 878 `unattributable` warnings should be
read: most are re-triggered by a leak switching back on, not by a leak growing.

## 3. Scoring timing at the edge of the night window

Six warnings were scored `false_alert` although a leak began at 03:30, inside the night
window's last hour. The scorer times a warning at the start of that hour (03:00), as the
frozen scorer always has. In five of the six, the 7-day spacing then blocked a creditable
warning for a large sudden leak.

Sensitivity only, verdict unchanged: crediting leaks that start inside the flagged hour
would give 217 of 234 sudden leaks found and a yield of 18.4% (407 of 2,217). That is still a
fail.
