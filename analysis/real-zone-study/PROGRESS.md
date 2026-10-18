# Real-zone study progress

**Verified (task scope):** five ordered steps, with a founder review stop after each. Existing results remain unchanged. No Git commit, merge, push, outreach or new pass/fail test is authorised here.

| Step | Status |
|---|---|
| 1. Injected-leak detectability on at most five real Yorkshire zones | Complete; founder authorised step 2 with explicit limits on rates, wording, download and detector separation. |
| 2. Night-flow decomposition with property counts | Complete; founder authorised step 3 with matched-workload and 38-zone reservation requirements. Conditional plausible leakage shares only; nothing feeds the detector. |
| 3. Written change-detector comparison design | Complete; awaiting founder review. CUSUM comparison at exact matched warning counts; 5/38 reservation saved; no implementation/calibration/injection run. |
| 4. Proposed raw-data request changes | Pending preceding reviews; existing request stays unchanged. |
| 5. One-page independent validation plan | Pending preceding reviews. |

**My judgement:** step 1 measures responses to artificial added flow against a real background, not real-leak accuracy. Stop after reporting it.

**Unknown:** actual leak onsets/flows, legitimate night use, pressures and operating conditions. Repair records are not inputs to step 1.

**Verified (local outputs):** 12,000 separate injected copies, 24,000 rule-result rows, 200 shared random starts per zone and 14 invented checks. The adaptive rule's smallest tested 90% response size is 2–8 m³/h across these five zones; this is an injected development result. The existing data, detector code and locked reports retain their recorded hashes. No Git action was performed.

**My judgement:** stop here for the requested review before step 2. See [findings](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/run/FINDINGS.md) and [run record / commit command](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/RUN-RECORD.md).

## Review gate

**Verified (first post-step review check):** the preceding goal turn made progress by completing step 1. On the next automatic continuation, the saved state still awaited founder review and no review decision was available. A choice to proceed to step 2 or revise step 1 was requested. This check makes no new analytical progress; review is required by the objective's “stop after each for my review” instruction. No later step has started and the overall goal remains active.

**Verified (third consecutive review-gate encounter):** the same gate was present when step 1 was delivered, at the first post-step check above, and at this next continuation. No founder decision has arrived. The preceding goal turn is classified as **no progress**, not a verified process wait. Current file hashes confirm step 1 remains complete; there is no unfinished run to resume. **My judgement:** no required analytical work can proceed without crossing the explicit review boundary. Mark the goal **blocked awaiting founder review**, preserving all five steps and their original scope. This is a review dependency, not a scientific failure or a claim that the overall goal is complete.

**Verified (founder review received, 18 October 2026):** the founder authorised step 2: cite night-use sources and use ranges; disclose the age and UK context of Managing Leakage (1994); describe only a **plausible leakage share**, with wide uncertainty, never a measured loss; download the 39 kB property-count file; feed nothing into the detector. This clears the preceding review gate. Stop again after step 2. Steps 3–5 remain pending review.

## Step 2 completed

**Verified:** the property download matches the published 39,098-byte size and MD5; all five selected N4 zones join uniquely. Separate fixed-hour weekday flow summaries use 240–241 complete later nights per zone. Nine invented checks and an independent raw-flow aggregation agree; all 42 protected earlier files remain byte-identical. The checksum-guard recovery is disclosed in the step-2 run record, and all numeric tables are unchanged by that correction. No detector imported/run, repair file opened, detector input changed, commit, merge, push or outreach.

**Conditional calculation:** at median observed flow, plausible leakage-share scenarios are 0–73% (784), 10–89% (1586), 70–94% (664), 67–95% (526), 78–98% (698). These depend on old UK rate references and an explicitly chosen household sensitivity range; wider night-variation envelopes and incompatible high-use corners are reported. They are not measured losses or confidence intervals.

**Unknown:** exceptional users, customer versus utility leakage, pressure, storage, boundaries, meter accuracy and transferability. Without assumptions, the data do not establish a useful leakage-share lower bound.

**My judgement:** three zones have a substantial unexplained remainder under the stated scenarios, warranting field checks rather than a measured-loss claim. Stop for founder review here. Step 3 has not begun, and the five-step goal is not complete.

**Review check, 19 October 2026:** the preceding goal turn made **progress** by completing step 2. All 25 files in its finished manifest and all 42 protected earlier files still match their saved hashes. No step-2 review decision has arrived. The goal's explicit “stop after each for my review” instruction therefore prevents beginning step 3. Requested a choice between proceeding to its written comparison plan and revising step 2. There is no live process being polled; this is a human review dependency, not a verified process wait. This is the first post-delivery check at the new step-2 gate; the goal remains active and incomplete.

**Verified (founder review received, 19 October 2026):** the founder authorised the step-3 design with two instructions: compare detectors at the same untouched warning rate per zone-year, and reserve the other 38 assessable N4 zones before any new comparison runs. The step-2 gate is cleared. Existing quality metadata alone identifies the 5/38 split; a reservation manifest was written before implementation/calibration. No new reserved-zone flow analysis or detector run is authorised by this writing step. Stop for review after the design.

## Step 3 completed

**Verified:** [PREREGISTRATION.md](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step3-change-design/PREREGISTRATION.md), parameter JSON and the exact 5-development/38-reserved split are saved before any new comparison. Metadata/document checks pass; all 68 protected earlier source/artifact files match their hashes. No detector implementation, calibration, injection, new reserved-zone flow analysis, repair rescoring, dataset download, contact, commit, merge or push occurred. This is a local review copy, not public registration or a completed experiment.

**Judgement:** CUSUM is the first comparator, on the same causal night-flow step. Threshold variants may be compared only at exactly equal per-zone warning counts; unattainable cells remain unmatched. Both response probability and delay are shown. The proposed later 38-zone split reserves the first 182 days for learning/calibration and the final 183 for confirmation, with settings locked before suffix values enter this new analysis. Equal calibration counts do not guarantee equal later workload; no threshold rescue is permitted.

**Unknown:** true field false alarms and future response. Fully invented stationary no-leak controls are specified separately for model-specific false-alarm estimates. The 38 zones were already part of the original Yorkshire test; this reservation protects the new comparison, not completely unseen data.

**Review stop:** [REVIEW.md](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step3-change-design/REVIEW.md) explains the decisions and provides exact manual commit commands for the new study folder. Step 3 is complete as writing only. Steps 4–5 have not started and the overall goal remains incomplete. Founder review is required before step 4; approval of the document is not permission to run the comparison.

**First post-step-3 review check, 19 October 2026:** the preceding goal turn made **progress**, completing the written design and exact reservation. Current manifest checks show no step-3 artifact changes, no comparison implementation and no run folder. No founder answer to the pending step-3 review question has arrived. This continuation makes **no new analytical progress**; it is a human review dependency, not a verified process wait. The explicit “stop after each for my review” instruction still prevents starting step 4. This is the first post-delivery encounter at this gate; leave the overall goal active and incomplete. Do not repeat the already-pending review question or start a later step without its answer.

**Third consecutive step-3 gate encounter, 19 October 2026:** the same dependency was present when step 3 was delivered, at the first continuation above, and at this continuation. The preceding goal turn is classified as **no progress**, not a process wait. Revalidation finds the saved step-3 artifacts unchanged, steps 4–5 unstarted and no founder review reply. No required work can proceed without crossing the explicit review boundary. Mark the overall goal **blocked awaiting step-3 review**, preserving its full five-step scope. This status stops repeated automatic checks; it is not completion, a scientific failure or a founder-requested pause. The existing review question remains pending.

**Founder-requested step-3 amendment, 19 October 2026:** before committing, the founder requested one pre-declared secondary realised-point dominance comparison in `PREREGISTRATION.md` and `design.json`, then a stop. Revision 2 adds the per-zone/per-fixed-size rule: an A setting dominates a B setting when it has no more warnings and no lower seven-day primary response probability, with at least one strict inequality. Report dominates/dominated/neither for all actual setting pairs beside the primary exact-match results, including witness IDs and coordinates. No interpolation, fitted frontier, new settings or retuning. Equal coordinates are neither; missing points are unavailable; conflicting pointwise relationships are not a method-wide winner. This authorises only the requested written amendment, not step 4 or any comparison run. Stop again for review.
