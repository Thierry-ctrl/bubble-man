# Bubble Man pilot FAQ for a utility engineer

**DRAFT - 11 October 2026. Not sent or agreed.**

## 1. What would the software tell our staff?

**Verified ([pilot guide][pilot]):** the current method looks for a rise in a zone's night flow. It compares the last two nights with the preceding week; its improved warning threshold follows recent variation. It does not identify a pipe or establish the cause of the rise. **My inference - suggested operator wording:** “Night flow rose more than usual. Review the operating log and consider investigating this zone.” This is proposed wording, not an existing live notification service.

## 2. Has it worked on real water-utility data?

**Verified ([locked results][results]):** all performance evidence so far comes from simulations. On 1,000 fresh LeakDB scenarios, sudden-leak detection was 88.6% among eligible leaks, with a median delay of 13.5 hours among credited detections. Warning yield was 47.2%, below the provisional 50% target. The earlier failed L-Town 2019 and LeakDB tests remain on record. **Unverified:** Rwanda or any real utility's detection/false-alert performance. The newer test uses the same generator family as development, so it is not proof of broad generalisation.

## 3. Do we need to buy sensors or install customer smart meters?

**My inference - proposed first stage:** use one zone's existing boundary-meter history and independently recorded incidents. No new installation is proposed for the historical trial. **Unverified:** whether your zone already has the right meters and retained records. Pressure or level sensors may be relevant later, but no purchase or performance improvement is established by this paperwork.

## 4. Which zone and readings are suitable?

**My inference - selection proposal:** a zone with every inlet/outlet/transfer identified, a verified boundary, continuous supply and usable night readings. Prefer 15-minute readings or finer. **Verified ([adapter guide][adapters]):** compatible declared intervals dividing 30 minutes, including regular 30-minute data, can reach the existing converter. Monthly totals cannot reproduce the required readings.

**My inference:** first inspect a permitted 2-4 week readings sample for semantics and quality. It is too short to judge detection. Request at least a year if suitable; longer retained history helps choose an agreed period. **Verified ([software gaps][gaps]):** the frozen reader currently takes a 365-day window; multi-year analysis and changes to the learning period need a separate design/protocol decision. Do not choose dates because the eventual leak results look favourable.

## 5. What file format should we provide?

**Verified ([adapter guide][adapters]):** CSV is straightforward. Explicitly mapped `.xlsx` long/wide tables and decimal-comma exports are supported by separate draft adapters. Meter roles, units, value type, interval, timestamp meaning and quality-code mappings are required. Proprietary/binary exports, formulas and merged table headers are not automatically supported. **Unverified:** compatibility with your actual export. A blank template/schema can establish the mapping before private rows are shared.

## 6. How should timestamps, gaps and meter faults be represented?

**My inference - proposed data contract:** preserve timestamps and flags, with timezone/UTC offset and whether values are instantaneous, interval averages/volumes or cumulative totals. Excel's timezone meaning must be stated explicitly. Leave gaps missing; do not turn them into zero or estimated normal readings. Keep resets, duplicates and fault/estimated flags visible.

**Verified ([converter/gaps][gaps], [adapters][adapters]):** adapters preserve these distinctions; the existing converter treats unusable readings as missing and does not interpolate. **Unverified:** actual sensor timing, accuracy, transmission delay and record completeness.

## 7. What if our zone has reservoirs or rationed supply?

**Verified ([software gaps][gaps]):** the converter refuses internal-storage zones by default. **Verified ([storage design][storage]):** a standalone accounting draft subtracts utility-tank filling and adds back draining, but it is not integrated or field-validated. It requires every relevant internal tank, approved geometry and aligned endpoint levels.

**My inference:** household tank refilling after interruptions is a separate demand pattern. Storage correction alone does not make rationed supply suitable. Select a simpler continuous-supply zone first, or agree a separate study. **Unverified:** a dependable intermittent-supply method for this project. [Literature review][intermittent]

## 8. Can it find leaks that have existed for months, or leaks that grow slowly?

**Verified ([pilot guide][pilot], [results][results]):** the present rule focuses on changes; simulation evidence is strongest for sudden leaks. Gradual-leak associations are reported but are not the acceptance endpoint, and the simulator's gradual flows fluctuate unusually. **My inference:** do not promise an inventory of old losses or detection of every slow leak. Investigating older losses needs other accounting or field evidence. A warning during an older leak may still be useful, but timing alone does not show what caused it or whether staff already knew.

## 9. What incident records are useful, and when would we open them?

**My inference - proposed sequence:** establish record definitions with a schema first. Keep detailed incident rows separate until rule, quality exclusions, observation window and scoring are approved, and the warning list is saved in an approved private audit store. Then use stable incident IDs with first report, confirmation and repair times separately, including date precision, asset/zone and inspection findings. Repeated tickets may describe the same leak; agree deduplication before matching warnings. [Scoring draft][scoring]

**My inference:** first report only establishes that a confirmed leak began no later than that report, if it concerns the same incident. A warning before it might have preceded the leak itself. Report the interval to the report as an association, never as a measured delay from true onset. Repair completion cannot silently replace first report. Date-only records need uncertainty bounds; missing dates are not invented.

## 10. Is a warning with no repair record a false alarm?

**My inference - proposed scoring:** no. It means “no recorded eligible leak”, not proof of a leak-free zone. Likewise, a recorded leak with no earlier warning is not automatically a measured miss when onset and coverage are unknown. In a live trial, keep “leak found”, “checked, nothing found” and “unknown/incomplete” separate. An unchecked warning stays unknown. A completed check finding nothing is not proof that no hidden leak exists. [Scoring draft][scoring]

## 11. How will we judge usefulness and workload fairly?

**My inference - proposed assessment:** report pre-report timing associations, data coverage and ambiguity separately from actual inspection findings. Count every warning as an investigation episode, with follow-up visits and staff time recorded separately. Show completion/unknown counts and distinct incidents so repeated findings cannot masquerade as new leaks. The provisional 50% simulation yield target is not an agreed utility requirement.

**My inference:** whole-week shifts move warnings to other weeks while retaining weekday/time as a reference. The current scoring draft treats that comparison as descriptive, not a formal significance test; seasonality and uneven gaps can undermine comparability. Agree the interpretation and workload targets before opening outcomes. A later shadow trial should also inspect a randomly selected set of eligible no-warning nights with comparable effort, recording cancellations and incomplete visits. Selection and inspection bias remain limitations. [Scoring draft][scoring]

## 12. Where would data go, who could see it, and could it be published?

**My inference - proposed terms:** use a named custodian, approved users, transfer channel, devices/storage/backup locations and any external providers. Household names or contact details are not needed for the initial zone-flow check. Do not assume opaque IDs make records anonymous, or that a file saved on a laptop stays outside cloud/AI services. Agree confidentiality, purpose, retention/deletion, legal/privacy review and the specific publication rights before access. No permission has been granted by this draft. See the [data-sharing outline][agreement].

**Unverified:** applicable permissions and personal-data classification for the actual files. The outline links Rwanda's official personal-data guidance; it does not establish legal compliance or grant cross-border storage/access rights.

## 13. What will it cost, and is anything live yet?

**Unverified:** fees, data-export effort and a sustainable inspection budget. **My inference:** agree these with the utility before the trial, including who supplies operational staff and what later support would cover. **Verified ([software gaps][gaps]):** the tools run historical files; live ingestion and notifications are not built. No current deployment, purchase or field intervention is part of this preparation.

## 14. What is the next practical action?

**My inference - proposal:** identify an authorised data owner and candidate zone; agree the sharing scope; review a small readings-only sample. If incompatible, report why. If compatible, approve and freeze a historical evaluation before accessing detailed incident outcomes. Consider a separately authorised shadow trial only after that evidence and workload review. These documents have not been sent, and preparing them does not authorise contact or a data transfer.

[pilot]: /Users/uwonkundathierryrugira/Bubble-man/PILOT-READINESS.md
[results]: /Users/uwonkundathierryrugira/Bubble-man/analysis/next-fair-evaluation/RESULTS-LEAKDB-1000.md
[gaps]: /Users/uwonkundathierryrugira/Bubble-man/pilot/SOFTWARE-GAPS.md
[adapters]: /Users/uwonkundathierryrugira/Bubble-man/pilot/loop/ADAPTERS.md
[storage]: /Users/uwonkundathierryrugira/Bubble-man/pilot/loop/STORAGE-DESIGN.md
[scoring]: /Users/uwonkundathierryrugira/Bubble-man/pilot/loop/SCORING-DRAFT.md
[intermittent]: /Users/uwonkundathierryrugira/Bubble-man/research/loop/intermittent-supply-methods.md
[agreement]: /Users/uwonkundathierryrugira/Bubble-man/pilot/loop/paperwork/DATA-SHARING-OUTLINE-DRAFT.md
