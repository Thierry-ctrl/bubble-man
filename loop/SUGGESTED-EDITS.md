# Suggested edits for human review

Existing files are not changed by this loop.

## 1. Clarify acceptable sampling interval in the pilot request

**Verified (local source links):** [PILOT-READINESS.md](/Users/uwonkundathierryrugira/Bubble-man/PILOT-READINESS.md) requests “15 minutes or finer” but lists 30 minutes among its accepted examples. Its unsuitable-data section excludes intervals slower than 30 minutes. [SOFTWARE-GAPS.md](/Users/uwonkundathierryrugira/Bubble-man/pilot/SOFTWARE-GAPS.md) describes conversion to the frozen 30-minute grid. These statements leave the preferred and maximum acceptable intervals unclear.

**My inference — suggested wording:** “15-minute readings or finer are preferred; regular 30-minute readings may also be usable, subject to compatibility checks.” This keeps a potentially suitable public or utility sample from being rejected solely because it is not 15-minute data. A human should align the request and guide if this policy is intended. No sampling rule or tool has been changed.

## 2. Qualify and reconcile the September research claims

**Verified (local source links):** [deep-research-report.md](/Users/uwonkundathierryrugira/Bubble-man/research/2026-09-28/deep-research-report.md) and [evidence-log.md](/Users/uwonkundathierryrugira/Bubble-man/research/2026-09-28/evidence-log.md) contain the claims audited in section 6 of the [Rwanda landscape report](/Users/uwonkundathierryrugira/Bubble-man/research/loop/rwanda-utility-landscape.md). These existing files were not edited.

**My inference — suggested human review:** apply the dated scope and source reconciliation in that audit. In particular, do not promote the unreproduced equipment inventory or review tallies to verified facts. For the JICA figures, clarify the measurement units and the source's internal inconsistencies. Distinguish the pilot-area evidence from country-wide conditions and the study's data-availability statement from utility policy. Keep uncertain current access and procurement status explicit.

**Verified (source link):** the publisher names the 2019 SPC authors as Jaehyun Ahn and **Donghwi Jung**; the earlier report says “Ahn & Jun.” [Publisher issue and abstract](https://ascelibrary.com/toc/jwrmd5/145/9).

**My inference — suggested correction:** fix the author's name in both older documents. Replace the categorical explanation of the gap between published accuracies and blind-test results with a caution that the studies' metrics and conditions are not directly comparable. The retrieved review supports a comparability concern; it does not establish that lack of blind testing alone caused every gap. This changes attribution and interpretation, not any locked detector result.

## 3. Bridge the warning export to a future approved real-record scorer

**Verified (local source links):** [run_frozen_rule.py](/Users/uwonkundathierryrugira/Bubble-man/pilot/run_frozen_rule.py:16) exports both rules with `issue_time_local`, but no stable warning ID. [convert_utility_data.py](/Users/uwonkundathierryrugira/Bubble-man/pilot/convert_utility_data.py:72) deliberately converts timestamps to naive local standard time and retains the offset in its report. This is the existing frozen-reader convention, not a detector defect.

**My inference — proposed integration work after approval:** an adapter for the [scoring draft](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/SCORING-DRAFT.md) should select one rule per evaluation, derive stable warning IDs and restore explicit offsets using the conversion metadata. Do not assume UTC or merge comparator/primary warnings into one investigation stream. The standalone draft currently has no file loader or integration; these existing tools were not modified.
