# Development sensitivity — prospective timing rule (10 Oct 2026)

**The locked 490-scenario result is unchanged:** FAIL, yield 18.1%, 212 of 234 sudden leaks,
under the locked scorer (`../RESULTS-LEAKDB.md`). This file only shows what the same
warnings score under the prospective timing rule of `PROTOCOL-LEAKDB-1000.md` §5. That rule
was fixed before this ran, together with the adaptive rule and the G1–G5 criteria.
**Nothing here was used to change them.**

Source: `prospective_sensitivity.py` → `dev-prospective-sensitivity.json`. Both rules'
warnings, recomputed by the frozen code (`leakdb1000/rules.py`), are identical to the locked
frozen warnings and to the development adaptive warnings.

| 490 development scenarios (11–500) | Frozen, locked scorer | Frozen, prospective | Adaptive, locked scorer | Adaptive, prospective |
|---|---|---|---|---|
| Warnings | 2,217 | 2,217 | 831 | 831 |
| Credited | 401 | 407 | 381 | 387 |
| Yield | 18.1% | 18.4% | 45.9% | 46.6% |
| Warnings without a newly eligible leak | 1,816 | 1,810 | 450 | 444 |
| — no leak flowing | 932 | 926 | 138 | 132 |
| Sudden leaks found / 234 | 212 | 217 | 208 | 213 |
| Gradual leaks associated / 238 | 189 | 190 | 173 | 174 |
| Median delay, sudden (h) | 14.5 | 14.5 | 14.5 | 14.5 |
| Week-shift test (real vs best of 47) | 212 vs 28 | 217 vs 28 | 208 vs 11 | 213 vs 11 |

The only change is the six warnings whose leak first flowed at 03:30, inside the last
contributing reading. They now count as credited, which frees five sudden-leak credits that
the 7-day spacing had blocked.

Against the frozen criteria, the adaptive rule would show in development:
- G3: 91.0% vs 92.7%, met;
- G4: 444 ≤ 905, met;
- G5: 46.6%, not met.

Its own result here would read "improved, but below the practical target". Being chosen on
this data, that is the optimistic case.
