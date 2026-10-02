# Frozen rule — written before any leak was scored

**2018 development test.** We have already studied these six leaks, so nothing here is a
performance claim. Committed before the scoring script was run; see git history.

## Can the threshold be chosen without the six leak outcomes?

Yes, but only from a thin sample, and the choice has to be declared rather than derived.

The obvious candidate — the reserved quiet window of 15–23 January — **cannot be used**:
a level alert is open for **0 of its 186 hours**, so it contains no example of the regime
this rule operates in. It also means the quiet window gives this rule **no exposure at
all** for counting false alerts.

The calibration period is therefore **2 January 05:00 – 14 January 23:00** (the step needs
30 hours of history, so it cannot start on 1 January). That stretch:

- lies entirely **before** the evaluation window opens on 15 January;
- contains **no main-zone leak** (the first, p461, begins 23 January);
- does **not** overlap the reserved quiet window;
- gives roughly 307 hourly step values.

307 values is too thin for a reliable 99th percentile — it would rest on about three
observations. So the threshold uses a robust spread estimate instead, which does not
depend on the extreme tail.

## The rule, frozen

1. **Threshold**
   `threshold = median(step) + 3 × IQR(step) / 1.349`
   over 2 Jan 05:00 – 14 Jan 23:00. The divisor converts the interquartile range into a
   standard-deviation-equivalent for a normal distribution, so "3 sigma" has its usual
   meaning without being hostage to three tail points. The multiplier 3 is the
   conventional process-control choice, declared here, not tuned.

2. **Condition**
   A new-rise warning may be raised **only while an Experiment A level alert is already
   open** (`issuable_at ≤ t ≤ run end`). This rule exists to answer the question "can we
   see a new rise during an open alert", and is not a general-purpose detector.

3. **Issue timing**
   The step for hour `t` uses hours `t−29 … t` and is complete at the end of hour `t`.
   A warning is therefore raised at **`t + 1`**, matching the scorer's one-hour
   reporting lag.

4. **Re-arming**
   After a warning, no further new-rise warning until the step has fallen **back below
   the threshold**, and in no case within **24 hours** of the previous one.

## What is fixed before scoring

- The step measure is unchanged from `analysis/new-rise-during-alert/`.
- The baseline, level threshold (10 m³/h) and persistence (6 h) of Experiment A are
  unchanged.
- The scorer and its matching rules are unchanged; it is imported, not edited.
- 2019 is not read.

## Fair random comparison

The rule can only fire while a level alert is open. A random baseline placed uniformly
across the year would therefore be competing on hours where the real rule was forbidden
to act. The comparison instead places the **same number of warnings** at hours drawn
uniformly **from the open-alert hours only**, honouring the same 24-hour minimum gap, and
scores them identically. 200 repetitions.

## Pre-declared decision criteria

- **Useful improvement**: credits at least two of the three leaks Experiment A missed
  (p538, p866, p158), beats the random comparison, and adds fewer than about 2 extra
  warnings per week of open alert.
- **Inconclusive**: credits leaks but cannot be separated from the random comparison, or
  the extra-warning cost is unclear.
- **Drop**: credits no more leaks than random placement does.
