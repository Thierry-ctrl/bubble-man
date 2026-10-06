# Decision memo — should we run the one locked 2019 test?

*Revision 2, 7 October 2026. Nothing has been run on 2019.*

## Where we are

On 2018, the night-flow step check issued **5 warnings in a year** and associated
**3 of 6 sudden leaks**. Moving the same warnings to other weeks never did as well (all 49
distinct shifts beaten, p = 0.02). I re-checked every one of those numbers independently;
they hold.

Against that:
- it **failed the noise check it set itself**;
- it **missed half the sudden leaks**, each time because another leak was starting, ending
  or growing at the same moment;
- the idea was motivated by 2018 data, so 2018 cannot confirm it.

## What changed since the first draft

**1. The robust noise amendment does not survive a consistent calculation.**
I had proposed swapping the standard deviation for a robust spread while keeping the
4.5 cutoff. But 4.5 was twice January's *standard deviation*. Measured the same robust way,
January's reference is 1.11, so the like-for-like cutoff is **2.22** — and 2018 scores
2.98. **2018 fails the amended check too.** I have withdrawn the recommendation to adopt it.

Both January references come from just **eight** night-to-night changes, so neither cutoff
is reliable. That cuts both ways: the gate cannot be trusted to say the method is too
noisy, and it cannot be trusted to say it is fine.

**2. I was wrong about late credits.** I said a credit more than 48 hours after a leak began
was unlikely to be caused by it. The step compares the last two nights with the seven
before, so a leak's onset stays in the comparison for up to eight nights, fading by
one-seventh each night. A 20 m³/h leak keeps the step above 10 for about five nights.
Delays are now reported without drawing conclusions about cause from them.

**3. The 50% warning yield is a proposed target, not a validated requirement.** It is my
suggestion for acceptable workload. A real utility would set it from its crew capacity.

Kept from the first draft: the disclosure that the 2019 leak schedule was displayed during
earlier work (so the test is blind to readings, not to the list of leaks); the explicit
exclusion of the three leaks carried over from 2018 (p427, p654, p810); and counting
**every** warning as an operator investigation.

## The decision in front of you

- **(A) Drop.** The noise check failed on 2018, both as written and in a like-for-like
  robust form. On that evidence, no 2019 run.
- **(B) Run, with the noise check reported but not deciding.** The outcome rests on the
  other criteria, especially the comparison with week-shifted warnings, which tests the
  noise check's underlying question directly — do the warnings beat the same pattern
  placed at other times? — using the year's own data instead of eight January nights.
  **This demotes a gate after it failed.** It must be labelled a weaker protocol in every
  result.

| If (B) | Required |
|---|---|
| Enough events | at least 3 eligible sudden leaks (else "inconclusive") |
| Real hits | at least 2 sudden leaks associated |
| Beyond chance | at most 1 of 51 week-shifts does as well (p ≤ 0.05) |
| Workload | at least half of all warnings associate a new leak — *proposed target* |

## My recommendation

**(B), as a judgement call — and (A) is a defensible choice if you weigh strict
pre-registration above learning from one more run.**

My reasoning: the noise gate rests on a reference too small to decide anything, and the
shift comparison measures what the gate was standing in for. The run costs little, its
outcome is fixed in advance, and a fail would be reported as a fail. But I want to be plain:
this is moving a goalpost, and nobody reading the result should be left unaware of it.

## If you choose (B), the single run does exactly this

1. Commit the approved protocol.
2. Download 2019 flow readings only; check them; compute both noise statistics; **commit**.
3. Generate the warnings; **commit them before any 2019 leak record is opened**.
4. Download 2019 leak records; build the eligible list; **commit**.
5. Score, compare with 51 week-shifts, and report every specified number — including every
   warning an operator would have had to investigate.

No second run. No changes afterwards.
