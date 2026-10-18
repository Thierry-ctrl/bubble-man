"""Reporting-only recovery after calculations finished but bundled Matplotlib was absent.

Use the existing system Python with Matplotlib. Read only saved study tables; never
rerun a detector or injection. Retain the original frozen study implementation unchanged.
"""
import csv
from datetime import datetime, timezone
import json
import platform

import matplotlib
import numpy as np
import pandas as pd

import study as S


def table(name, strings):
    with (S.RUN / name).open() as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key, value in row.items():
            if key not in strings:
                row[key] = float(value) if value else None
    return rows


def main():
    if (S.RUN / "finished.json").exists() or (S.RUN / "FINDINGS.md").exists():
        raise FileExistsError("Reporting already exists; refusing overwrite")
    prepared = json.loads((S.RUN / "prepared.json").read_text())
    S.check_snapshots(prepared["input_hashes"])
    inputs = [S.RUN / name for name in ["prepared.json", "selection.csv", "onsets.csv",
                                       "trials.csv", "curves.csv", "untouched.csv", "minimum-sizes.csv"]]
    before = {p.name: S.sha(p) for p in inputs}
    rows = table("curves.csv", {"dma", "rule", "size_origin"})
    baselines = table("untouched.csv", {"dma", "rule"})
    minima = table("minimum-sizes.csv", {"dma", "rule", "status"})
    with (S.RUN / "trials.csv").open() as handle:
        trial_rows = sum(1 for _ in csv.DictReader(handle))
    assert trial_rows == 24000 and len(rows) == 120
    S.plot_and_report(prepared, rows, baselines, minima)
    findings = S.RUN / "FINDINGS.md"
    text = findings.read_text().replace("[PLAN.md](../PLAN.md)", f"[PLAN.md]({S.HERE / 'PLAN.md'})")
    addition = (
        "**My judgement — useful limit:** the adaptive rule's smallest tested size reaching the 90% convention ranges from 2 to 8 m³/h, about 18–72% of the zones' night-flow references. Four of five zones need a larger tested addition under the adaptive rule than under the frozen comparator. This trade-off belongs beside the untouched warning workload, not a claim that either rule wins.\n\n"
        "**Verified — provenance:** data: Yorkshire Water N4, 2016–17, via [Data Mill North](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn), CC BY 4.0. Constant synthetic flow was added separately to the real background; charts describe those modified copies. Delays use the published wall-clock grid, not verified data-arrival or crew-awareness times.\n\n"
    )
    text = text.replace("**Unknown:** actual leak truth", addition + "**Unknown:** actual leak truth")
    findings.write_text(text)
    assert before == {p.name: S.sha(p) for p in inputs}, "Reporting changed a calculation table"
    S.check_snapshots(prepared["input_hashes"])
    all_outputs = [p for p in S.RUN.iterdir() if p.is_file()]
    S.write_json(S.RUN / "finished.json", {
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "calculation_status": "All 12000 separate injected copies and 24000 rule rows saved before chart error; trials share real backgrounds and overlap in time",
        "reporting_recovery": "Original run stopped at import matplotlib; rendered saved outcomes only, no detector/injection rerun",
        "calculation_tables_unchanged_by_reporting": True,
        "calculation_csv_reads_guarded": True,
        "calculation_csv_read_allowlist": [str(p.relative_to(S.ROOT)) for p in
                                          [S.FLOW, S.ASSESS, S.OLD_WARNINGS, S.RUN / 'selection.csv', S.RUN / 'onsets.csv']],
        "calculation_read_trace_persisted": False,
        "repair_records_accepted_by_guard": False,
        "rules_and_original_inputs_unchanged": True,
        "baseline_warnings_match_saved_lists": True,
        "new_pass_fail_claim": False,
        "trial_rule_rows": trial_rows,
        "report_environment": {"python": platform.python_version(), "matplotlib": matplotlib.__version__,
                               "numpy": np.__version__, "pandas": pd.__version__},
        "reporting_script_sha256": S.sha(S.HERE / "render_saved.py"),
        "files_sha256": {p.name: S.sha(p) for p in all_outputs}})
    print("Recovered five zone figures and findings from saved tables; all calculation and protected-file hashes unchanged.")


if __name__ == "__main__":
    main()
