# Commit ID map after the 30 Oct 2026 email rewrite

All commits were rewritten to replace the author/committer email with a GitHub noreply address before the repository was made public. File contents, messages and dates are unchanged; only commit IDs changed. Documents in this repository quote the OLD short IDs as evidence that protocols were committed before results; use this table to find the corresponding new commit (each pair has an identical file tree).

| Old ID | New ID | Date | Message |
|---|---|---|---|
| 2e83ab7 | 42b03ee | 2026-09-28 | Bubble-man: leak-detection experiments on L-Town |
| fb40588 | ad68cb6 | 2026-09-28 | Check how much Jan-Feb drift is real leaks, not baseline staleness |
| 1f1ac6d | c4d9416 | 2026-09-28 | Add deep research review and evidence log (2026-09-28) |
| 3943dcd | ec4f403 | 2026-09-29 | Add event-level leak scorer, worked checks and a null baseline |
| cf188f2 | 1632574 | 2026-09-29 | Scorer v2: corrected timing, neutral categories, zones from the network map |
| 02da697 | fb63386 | 2026-09-29 | Verify water accounting across the zone boundaries |
| ce7e2e5 | 860f6a4 | 2026-09-29 | Run main-zone evaluation with two frozen experiments |
| 9142e46 | 240f884 | 2026-09-29 | Add review bundle README with document status and reproduction steps |
| 50d3055 | 2a7c24b | 2026-09-29 | Fix retrospective-credit defect; define leak activity by positive flow |
| 5644376 | 3860ef4 | 2026-09-29 | Update review README for round-2 corrections |
| 3b2553d | 9671f0a | 2026-09-29 | Fix expired-leak credit under overlapping candidates |
| 0567e43 | b353eb2 | 2026-10-02 | Add p673 walkthrough: why the warning arrived 94 hours late |
| 28128e1 | 4581d3d | 2026-10-02 | Test whether a change measure sees new leaks during an open alert |
| 72955bc | c4fa5c2 | 2026-10-03 | Freeze the real-time new-rise rule before scoring |
| b5176a1 | a446d4c | 2026-10-03 | Real-time new-rise rule: credits every leak, but no better than chance |
| 1dc59fb | 434c5c2 | 2026-10-04 | Review new-rise-realtime: reconcile random runs, test calibration overlap |
| ac3d5eb | 7f6f30c | 2026-10-04 | Freeze the pressure comparison before examining outcomes |
| c42c917 | 66b1364 | 2026-10-04 | Pressure evidence study: mixed, and a weekly artefact in the baseline |
| d804f2c | 73ea182 | 2026-10-04 | Diagnose the weekend artefact and freeze a replacement baseline |
| 3f011f9 | ccc63f8 | 2026-10-04 | Rerun 2018 comparisons with the repaired weekend baseline |
| 8065d16 | 00e338f | 2026-10-05 | Explain the 5,826-hour alert: labelled leaks and non-labelled excess |
| 1d72cef | e8224ab | 2026-10-05 | Audit live inputs for separating demand from sustained leakage |
| b944498 | b9623ca | 2026-10-06 | Freeze the night-flow step rule before any check or scoring |
| 2842973 | ef540f5 | 2026-10-06 | Night-flow step check: beats all 49 week shifts, but trips its noise stop |
| ad6a019 | 9b86713 | 2026-10-06 | Draft locked 2019 protocol and decision memo for the night-flow step check |
| 154113c | 5fcc30e | 2026-10-06 | Revise 2019 protocol draft: correct delay claim, make noise check consistent |
| 9724c60 | 9a26cd2 | 2026-10-06 | Protocol revision 3: option B, revised exploratory evaluation |
| fd045b4 | ec17e9b | 2026-10-06 | Add locked-run code for 2019 (protocol 9724c60), verified on 2018 |
| 04beb0b | a89535c | 2026-10-06 | 2019 run steps 2-3: flows verified, noise recorded, weekday shift found |
| 2d0671b | 1092ead | 2026-10-06 | 2019 run step 4: complete warning list, committed before leak records |
| bce3b85 | 8b4dd79 | 2026-10-06 | 2019 run step 5: leak records verified, eligible list built |
| d98a143 | a9d8f98 | 2026-10-06 | 2019 locked run result: FAIL under the revised exploratory protocol |
| 319acf6 | 53ce1e0 | 2026-10-06 | Fix a self-contradictory sentence in RESULTS-2019.md |
| 5874bea | 1dac857 | 2026-10-07 | Prepare next fair evaluation: baseline idea, dataset review, draft experiment |
| 043c7e4 | 22d9959 | 2026-10-07 | LeakDB protocol revision 2: separate transfer from weekly-slip repair |
| d7459a9 | df2a4b4 | 2026-10-07 | LeakDB protocol revision 3: scoring and shift code frozen and tested before data |
| 0dbd107 | 621c55a | 2026-10-08 | LeakDB protocol revision 4: archive-layout correction before extraction |
| 7e6bdcc | 50a6488 | 2026-10-08 | LeakDB step 3: archive verified (size, md5), 490 Hanoi inlet files extracted, manifest |
| bcb24fe | 22ccfa6 | 2026-10-08 | LeakDB step 4: all Q1 and Q2 warning lists committed before any leak record |
| 0bb399a | c8a9043 | 2026-10-08 | LeakDB step 5: leak table (509 records, 374 scenarios); summary-count defect documented |
| 87e8160 | 7926597 | 2026-10-08 | LeakDB single locked run: Q1 FAIL (yield 18.1% < 50%); Q2 re-aligned |
| 1952eac | f5a4dd6 | 2026-10-09 | LeakDB development diagnosis, one proposed change, draft 1000-set protocol |
| bf45959 | 6f329b2 | 2026-10-10 | Freeze 1000-scenario protocol, code and invented-case tests before any held-out reading |
| 34df57d | 7048879 | 2026-10-10 | LeakDB 1000-set step 1: archive re-verified, 1000 inlet files extracted, manifest |
| 0d718f3 | 8290855 | 2026-10-10 | LeakDB 1000-set correction 1: Index-format files (before any warning or leak record) |
| 0d23e7c | 2214b29 | 2026-10-10 | LeakDB 1000-set step 2: both warning lists committed before any leak record |
| a779327 | a1bc4b7 | 2026-10-10 | LeakDB 1000-set step 3: leak table (1022 records, 763 scenarios) |
| 5b0166e | e91a1fd | 2026-10-10 | LeakDB 1000-set single held-out test: improved, but below the practical target |
| 0519b4a | 8004b5a | 2026-10-10 | Reporting corrections: leak endings, calendar months, fluctuation wording, temporal association |
| eeeeebe | 11bcaa8 | 2026-10-10 | Pilot readiness: guide, utility request draft, invented example format, input tools |
| 0992c96 | ab663fa | 2026-10-11 | Research public real-network datasets for Bubble Man pilot |
| 0f8325a | ac3923b | 2026-10-11 | Research Rwanda utility infrastructure and pilot data access |
| 836cb26 | 60d159e | 2026-10-11 | Draft real-record scoring with invented-case checks |
| 12331f7 | 9f69390 | 2026-10-11 | Document intermittent supply methods and pilot limits |
| 154fe74 | e061d41 | 2026-10-11 | Prepare standalone tank storage correction |
| 5eecde8 | 56c3e21 | 2026-10-11 | Prepare explicit utility export format adapters |
| 93bf4b5 | 28ab6b9 | 2026-10-11 | Prepare draft utility pilot paperwork |
| 4f2a336 | 14e54b4 | 2026-10-11 | Index pilot materials and audit preparation completion |
| fb9a949 | bd32db7 | 2026-10-18 | Freeze Yorkshire Water N4 real-data protocol, code and invented-case tests |
| 853594a | 35de811 | 2026-10-18 | Yorkshire N4 revision 1: autumn clock-change hour set missing (before repairs opened) |
| e4e198f | 2015f38 | 2026-10-18 | Yorkshire N4 step 2: both warning lists committed before repairs file is opened |
| 600d137 | e1c3559 | 2026-10-18 | Yorkshire N4 results (no association beyond chance, p = 0.0625) and next-evidence decision brief |
| 55012ef | 28ab55a | 2026-10-19 | Record real-zone studies and preregister matched-workload comparison |
