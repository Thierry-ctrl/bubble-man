# Step 3 — review before any run

**Proposed question:** if both methods create the same number of visits in a zone, which responds to smaller added leaks sooner?

**Judgement:** compare our current rule first with CUSUM, a change detector that adds up repeated small changes. Use exactly the same flow signal. Bayesian changepoint detection is not an extra candidate in this plan.

**Your two instructions are recorded:**

- Match warning counts **within each zone**, before comparing injected responses. Keep unattainable counts blank. Show detection probability beside delay, so responding quickly to only a few leaks cannot look like a win.
- Develop on the same five zones. The other **38 IDs are explicitly reserved**, using existing quality metadata only. They were already part of the original Yorkshire test, so they are not completely unseen data. No new detector analysis of them has occurred.

**A proposed detail to review:** for later work on those 38, use the first 182 days for learning/calibration and keep the final 183 days for confirmation. Freeze each method's settings before confirmation values enter this new analysis. Equal calibration workload may drift later; only genuinely equal later warning counts can support a matched-workload comparison. Other points remain visible and unmatched, with no threshold adjustment.

**Unknown:** real false alarms. A warning on untouched real flow might be a real leak. The plan separately specifies invented no-leak controls for model-specific false-alarm estimates; they cannot establish utility performance.

**Verified now:** design and reservation files only. No comparison code, detector/calibration/injection run, repair rescoring, new data download or contact. The reservation includes all 43 previously assessable zones exactly once (5 development, 38 reserved). Earlier results remain unchanged. This is local written pre-registration for review, not a public registration or a completed test.

Read [PREREGISTRATION.md](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step3-change-design/PREREGISTRATION.md); parameter/timing details are in [design.json](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step3-change-design/design.json).

**When ready to freeze the written plan**, these commands save the new study folder, including the still-untracked steps 1–2 that supply its dependencies and saved injection dates. They add nothing outside this study. I have not run them:

```sh
cd /Users/uwonkundathierryrugira/Bubble-man
git add -- analysis/real-zone-study
git diff --cached --stat -- analysis/real-zone-study
git commit --only -m "Record real-zone studies and preregister matched-workload comparison" -- analysis/real-zone-study
```

Stop for founder review here. Approval of this document does not execute a comparison or waive the review stops for steps 4 and 5.
