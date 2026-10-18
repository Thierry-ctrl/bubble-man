# Step 3 — smaller leaks sooner, at the same workload

**19 October 2026. Written before any new comparison run. Review copy, not committed or publicly registered.** No implementation, calibration, injection or confirmation run is authorised now. The founder must approve and commit this plan and its zone reservation before later work. Locked results stay unchanged.

**Review revision 2:** adds the founder-requested secondary realised-point dominance check before any run; the exact-match comparison remains primary.

## Question and comparison

**Judgement:** compare our adaptive rule with a **one-sided CUSUM**, which accumulates repeated positive changes. The frozen rule is a secondary comparator. CUSUM satisfies the requested “CUSUM or Bayesian changepoint” alternative; a Bayesian model is not an additional candidate in this design.

All use the current causal night-flow step and the same warning opportunities, with seven days between visits. The only adaptive/frozen parameter swept is the threshold multiplier in separately named comparison variants. The original multiplier-4 rules remain unchanged reference points, **not evidence of a fair comparison when their workloads differ**. [NIST describes CUSUM and its reference/decision limits](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm); our serially correlated step does not inherit its textbook error guarantees.

## Reservation made now

**Verified:** existing assessability metadata gives 43 zones. Development remains **784, 1586, 664, 526, 698**. The other **38**, listed individually in [zone-reservation.csv](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step3-change-design/zone-reservation.csv), are reserved from this new comparison. No substitution by performance or additional development-zone selection.

**Prior exposure:** all N4 zones were read and the 43 assessable zones were scored in the earlier Yorkshire repair study. The 38 are therefore **reserved from new detector development, not never-seen data**. No new flow/warning/repair analysis of them is performed now. No repair records or step-2 leakage-share estimates enter this comparison.

## Exact workload matching on the five development zones

**Judgement:** for each zone separately, target **1, 2, 3, 4, 8 and 12 warnings over its 337 calendar days**. Annualise counts by `365/337`; count every warning, including repeats. Use all fixed candidate thresholds in [design.json](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step3-change-design/design.json).

Calibrate on the **untouched development background only**, before injection runs: for each target count choose the largest listed threshold producing exactly that count. Save thresholds, actual counts and warning lists first. Freeze those settings for every injected copy; never retune them after adding a leak. For the **primary exact-match comparison**, compare adaptive–CUSUM and frozen–CUSUM only where their untouched counts are **exactly equal within that zone**. If a count is unattainable, leave that cell unmatched. No approximation, interpolation, warning deletion or random thinning creates equality.

This is development on reused real backgrounds, not an independent accuracy estimate.

## Injected responses and outputs

Reuse step 1's **200 saved starts per zone**, permanent added-flow shapes, size grid, missing-data policy and full-history replay. These are **synthetic additions to real readings**, with no hydraulic pressure feedback. No resets at the artificial onset.

Primary response: a new or retimed warning within 168 hours absent from the paired untouched list, with its final input bin at/after onset. Keep every sampled start, including gaps and existing warnings. Report the untouched coincidence probability separately.

At each matched workload and size show response probabilities by **24, 48, 72 and 168 hours**, conditional delay quartiles, and the smallest tested size reaching 90% by seven days at that and every larger size. Nonresponses stay in the denominator; do not conceal them behind faster responder-only medians. Plot delay/response against **actual warnings per zone-year**, with leak size shown; no single winner is selected from a pooled workload total. All five zones, unmatched cells and all fixed sizes remain visible.

## Pre-declared secondary comparison: realised-point dominance

For **every zone and fixed leak size**, separately in development and confirmation, compare the methods' realised points `(untouched warnings per zone-year, seven-day primary response probability)`. Use the same evaluation window and sampled starts. Include every evaluated setting already retained by this plan, including native reference points and realised zero-warning points; do not expand the grid or fit settings for this check.

An A setting **dominates** a B setting if `warnings_A ≤ warnings_B` and `response_A ≥ response_B`, with **at least one strict inequality**. The reverse is **dominated**; otherwise report **neither**, including identical coordinates. A dominance claim against a B setting must name at least one actual A setting witnessing it. Use actual unrounded counts and response fractions; no interpolation, extrapolation or fitted frontier.

Beside the exact-match results, report **dominates / dominated / neither** for every realised setting pair in each zone/size for adaptive–CUSUM, frozen–CUSUM and adaptive–frozen. Include method/setting IDs and both coordinates, and preserve all witness pairs. Missing points are **unavailable**, not “neither”. Crossing point sets retain their conflicting pairwise relationships; one favourable pair is not a claim that an entire method dominates all settings of another. Unequal warning rates can support this secondary check, but do not become exact matches. It is a descriptive comparison of injected responses, not a significance test, real-leak accuracy claim or new pass/fail rule.

## Later confirmation on the 38 — reserved from this new comparison

**Judgement — proposed temporal split:** when separately authorised, each reserved zone's first **182 days** is calibration/history only; the final **183 days** is confirmation. The first 28 days supply the existing local learning. Use days 28–181 to fit exact common warning-count targets; lock settings and replay to the boundary **before using days 182–364 in the new analysis**. The shared raw file was previously read: a future adapter must expose only prefix values to calibration, with confirmation values withheld from calculations/preview. Reuse the already-fixed assessability list; do not inspect the suffix to re-qualify zones. This prevents fitting a threshold on the period whose injected responses will be evaluated. It is not 38 fresh full-year tests.

Use the same fixed target counts and threshold grids. Later confirmation starts, relative-size reference and scoring are fixed in the JSON. Every zone remains in the report, including unavailable calibration targets. Before opening any reserved-zone readings, the founder must commit the implementation, five-zone development results and a choice record naming the candidate/design to confirm (or no choice). Changes after reserved results are seen become exploratory and cannot be rescued on these zones.

**Important limit:** equal calibration counts cannot guarantee equal future counts. Freeze the finite settings, generate/save the later untouched warning lists, then run the injected copies. For the **primary exact-match comparison**, compare only settings with **exactly matching realised confirmation warning counts**; show every other point as unmatched, without retuning. Pre-specified cross-target pairs may be compared if their actual counts match; all such pairs are shown, with no selection by injection performance. If no positive rate matches, a matched-workload comparison is unavailable; the secondary realised-point dominance check still applies to available points. Do not call a lower-warning, slower method better by default.

## What error rate is actually known?

**Unknown:** true false alarms on these real backgrounds. Untouched warnings may concern existing real leaks or normal operation. Call them **warning workload**, not measured false alarms. True field error rates still need independent negative checks.

**Judgement:** a separate, fully **INVENTED stationary no-leak control**, specified in the JSON, will estimate model-specific false alarms for settings frozen from development. Report that curve separately; no null-model or threshold fitting to its results. It checks a declared mathematical model, not real utility error rates. Neither CUSUM nor a Bayesian probability would turn unverified real warnings into known false alarms.

**Review stop:** writing only. No new pass/fail claim, Yorkshire repair rescoring, download, contact, commit, merge or push. Steps 4–5 remain pending.
