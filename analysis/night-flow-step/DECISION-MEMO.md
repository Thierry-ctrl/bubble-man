# Decision memo — should we run the one locked 2019 test?

*6 October 2026. Nothing has been run on 2019.*

## Where we are

On 2018, the night-flow step check issued **5 warnings in a year** and associated
**3 of 6 sudden leaks**. Moving the same warnings to other weeks never did as well (all 49
distinct shifts beaten, p = 0.02). I re-checked every one of those numbers independently;
they hold.

Against that:
- it **failed the noise check it set itself** (6.04 against a limit of 4.5);
- it **missed half the sudden leaks**, each time because another leak was starting,
  ending or growing at the same moment;
- the idea was motivated by 2018 data, so 2018 cannot confirm it.

## Two problems found in review

1. **A leak carried over from 2018 would have been scored as a new 2019 leak.** The 2019
   file starts at the window's first moment, so the scorer would see those leaks
   "begin" on 1 January. Fixed in the protocol by excluding p427, p654 and p810 by name,
   using 2018 data only.
2. **The 2019 leak schedule is not truly sealed.** It sits in a file next to the 2018
   schedule and was printed on screen during the scorer work on 28–29 September. The 2019
   flow readings have never been downloaded. So the test can be blind to readings, not to
   the list of leaks. The rule was not built from that list, but you should know.

## The decision in front of you

**First: does the failed noise check stand?**

- **If yes**, the method is dropped on 2018's evidence and the protocol is not run.
- **If you accept the amendment**, the check is redone with a robust measure (interquartile
  range instead of standard deviation) at the **same** cutoff of 4.5. The reason: the
  standard deviation was inflated by the very leak events the method detects. It would be
  recorded throughout as an amendment made after seeing 2018, and 2018's failure stays on
  record.

**Then: approve or change the draft protocol** — especially the success criteria:

| | Required |
|---|---|
| Gate | approved noise check passes on 2019 readings |
| Enough events | at least 3 eligible sudden leaks |
| Real hits | at least 2 sudden leaks associated |
| Beyond chance | at most 1 of 51 week-shifts does as well (p ≤ 0.05) |
| Workload | at least half of all warnings associate a new leak |

The workload criterion is my suggestion, not a statistical result. Please confirm or
change it.

## My recommendation

**Accept the amended noise check, openly labelled, and approve the protocol** — with eyes
open about the weak points. This is the first method in the project to beat its own
random comparison under a test fixed in advance, at a workload of a few warnings a year,
and its misses have a clear cause. A single locked 2019 run is the cheapest way to learn
whether 2018 was luck.

Expect it may well fail, or come back inconclusive if 2019 holds few sudden main-zone
leaks. Either outcome is informative; neither would be rerun.

## If you approve, the single run does exactly this

1. Commit the approved protocol.
2. Download 2019 flow readings only; check them; compute the noise check; **commit**.
3. Generate the warnings; **commit them before any 2019 leak record is opened**.
4. Download 2019 leak records; build the eligible list; **commit**.
5. Score, compare with 51 week-shifts, and report every specified number — including every
   warning an operator would have had to investigate, not only the "false alerts".

No second run. No changes afterwards.
