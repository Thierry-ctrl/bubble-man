# v2 results, superseded 29 September 2026

Kept for traceability. Replaced after a reviewing agent found that the scorer credited
an alert whose `issuable_at` fell after the matched leak had already ended.

Changes made in v3:
1. `retrospective_association` separated from `credited`. An alert that could only be
   raised after the leak ended is not a timely actionable warning.
2. Evaluation-end boundary made explicit (`issuable_after_window`).
3. Leak activity redefined by POSITIVE SIMULATED LEAK FLOW, not configured onset, so
   quiet-period exposure and matching use one consistent definition. Configured onset
   retained and both delays reported.
4. The New Year's Day explanation for experiment B's alert count was tested and
   REFUTED; it has been removed rather than restated.
