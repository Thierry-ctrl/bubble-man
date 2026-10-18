"""Development: synthetic additive steps on real readings; no repair/label access.

Call the existing two rules unchanged. PLAN.md/plan.json define all design choices.
prepare records selection and sampled dates before run creates any injected outcomes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "analysis/yorkshire-n4"))
import yw  # noqa: E402 - reader and unchanged warning rules; no top-level data access

FLOW = ROOT / "data/yorkshire/N4_2016_2017.csv"
ASSESS = ROOT / "analysis/yorkshire-n4/run/dma-assessability.csv"
OLD_WARNINGS = ROOT / "analysis/yorkshire-n4/run/warnings-both-rules.csv"
SOURCE_RECORD = ROOT / "analysis/yorkshire-n4/run/step1-download.json"
RUN = HERE / "run"
PROTECTED = [
    ROOT / "PILOT-READINESS.md",
    ROOT / "pilot/loop/NEXT-REAL-EVIDENCE.md",
    ROOT / "pilot/loop/SCORING-DRAFT.md",
    ROOT / "analysis/yorkshire-n4/PROTOCOL-YORKSHIRE-N4.md",
    ROOT / "analysis/yorkshire-n4/RESULTS-YORKSHIRE-N4.md",
    ROOT / "analysis/yorkshire-n4/yw.py",
    ROOT / "analysis/next-fair-evaluation/leakdb1000/rules.py",
    ROOT / "analysis/next-fair-evaluation/leakdb/method.py",
    ROOT / "analysis/next-fair-evaluation/RESULTS-LEAKDB.md",
    ROOT / "analysis/next-fair-evaluation/RESULTS-LEAKDB-1000.md",
    ROOT / "analysis/night-flow-step/RESULTS-2019.md",
    ASSESS, OLD_WARNINGS, SOURCE_RECORD,
]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    with Path(path).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def install_csv_read_guard():
    """Reject any CSV read except flows, prior warning/quality tables and this plan's dates."""
    allowed = {p.resolve() for p in [FLOW, ASSESS, OLD_WARNINGS,
                                   RUN / "selection.csv", RUN / "onsets.csv"]}
    reads = set()

    def guard(event, args):
        if event != "open" or not isinstance(args[0], (str, bytes)):
            return
        path = Path(args[0].decode() if isinstance(args[0], bytes) else args[0]).resolve()
        mode, flags = args[1:3]
        reading = ("r" in mode or "+" in mode) if isinstance(mode, str) else (flags & 3) == 0
        if reading and path.suffix.lower() == ".csv":
            if path not in allowed:
                raise PermissionError(f"Study CSV read not permitted: {path}")
            reads.add(str(path.relative_to(ROOT)))

    sys.addaudithook(guard)
    return reads


def snapshots():
    paths = [HERE / "PLAN.md", HERE / "plan.json", HERE / "study.py",
             HERE / "test_study_INVENTED.py", *PROTECTED, FLOW]
    return {str(p.relative_to(ROOT)): sha(p) for p in paths}


def check_snapshots(record):
    for name, expected in record.items():
        if sha(ROOT / name) != expected:
            raise RuntimeError(f"Recorded input/code changed: {name}")


def select_zones(series, candidates, number):
    rows = [{"dma": str(dma), "finite_bins": int(series[str(dma)].notna().sum()),
             "total_bins": len(series[str(dma)])} for dma in candidates]
    return sorted(rows, key=lambda r: (-r["finite_bins"], int(r["dma"])))[:number]


def random_onsets(index, dma, plan):
    eligible = index[(index >= index[0] + pd.Timedelta(days=plan["first_start_day_index"])) &
                     (index <= index[-1] - pd.Timedelta(hours=plan["horizon_hours"]))]
    rng = np.random.default_rng([plan["seed"], int(dma)])
    positions = np.sort(rng.choice(len(eligible), plan["starts_per_zone"], replace=False))
    return eligible[positions]


def night_reference(series):
    daily = yw.M.hourly_days(series)
    early = daily[28:, :6]
    good = np.isfinite(early).all(axis=1)
    if not good.any():
        return None, 0
    two_hours = (early[good, :-1] + early[good, 1:]) / 2
    value = float(np.median(two_hours.min(axis=1)))
    return (value if value > 0 and np.isfinite(value) else None), int(good.sum())


def sizes_for(reference, plan):
    sizes = {float(x): ["absolute"] for x in plan["absolute_sizes_m3h"]}
    if reference is not None:
        for percent in plan["relative_sizes_percent"]:
            value = reference * percent / 100
            sizes.setdefault(value, []).append(f"{percent}% reference")
    return [(size, "; ".join(tags)) for size, tags in sorted(sizes.items())]


def inject(series, onset, amount):
    if not np.isfinite(amount) or amount < 0:
        raise ValueError("Injection must be finite and nonnegative")
    if onset not in series.index:
        raise ValueError("Onset must be an existing grid timestamp")
    copy = series.copy(deep=True)
    mask = (copy.index >= onset) & copy.notna()
    copy.loc[mask] += amount
    return copy


def response(warnings, baseline, onset, horizon=168):
    end = onset + pd.Timedelta(hours=horizon)
    valid = [pd.Timestamp(w[1]) for w in warnings
             if onset <= pd.Timestamp(w[1]) - pd.Timedelta(minutes=30)
             and pd.Timestamp(w[1]) <= end]
    changed = [t for t in valid if t not in baseline]
    return {"any_warning": bool(valid), "primary_response": bool(changed),
            "delay_hours": float((min(changed) - onset) / pd.Timedelta(hours=1)) if changed else None}


def all_seven_opportunities(result, day0, onset, horizon):
    issues = pd.date_range(day0 + pd.Timedelta(hours=result.night_start_hour + 2),
                           periods=len(result.step), freq="D")
    mask = ((issues - pd.Timedelta(minutes=30) >= onset) &
            (issues <= onset + pd.Timedelta(hours=horizon)))
    return bool(mask.sum() == 7 and np.isfinite(result.step[mask]).all())


def summarise(rows):
    delays = [r["delay_hours"] for r in rows if r["primary_response"]]
    count = sum(r["primary_response"] for r in rows)
    return {"trials": len(rows), "primary_responses": count,
            "primary_probability": count / len(rows),
            "any_warning_probability": sum(r["any_warning"] for r in rows) / len(rows),
            "median_delay_h": float(np.median(delays)) if delays else None,
            "q25_delay_h": float(np.percentile(delays, 25)) if delays else None,
            "q75_delay_h": float(np.percentile(delays, 75)) if delays else None}


def minimum_size(rows, target):
    ordered = sorted(rows, key=lambda r: r["size_m3h"])
    for i, row in enumerate(ordered):
        if all(r["primary_probability"] >= target for r in ordered[i:]):
            return row["size_m3h"]
    return None


def prepare():
    plan = json.loads((HERE / "plan.json").read_text())
    record = snapshots()  # record plan/code before flow values/selection
    expected = json.loads(SOURCE_RECORD.read_text())
    assert FLOW.stat().st_size == expected["bytes"]
    assert record[str(FLOW.relative_to(ROOT))] == expected["sha256"], "Original flow checksum mismatch"
    if RUN.exists():
        raise FileExistsError("Output folder already exists; do not overwrite a plan or run")
    series, read_report = yw.read_area(FLOW)
    candidates = pd.read_csv(ASSESS, dtype={"dma": str})
    candidates = candidates.loc[candidates.assessable == True, "dma"].tolist()  # noqa: E712
    selected = select_zones(series, candidates, plan["zones"])
    assert len(selected) == plan["zones"] and len(candidates) == 43
    dates, details = [], []
    for row in selected:
        dma = row["dma"]
        s = yw.to_frozen_reader(series[dma])
        reference, nights = night_reference(s)
        details.append({**row, "reference_m3h": reference, "reference_complete_nights": nights,
                        "sizes": sizes_for(reference, plan)})
        dates.extend({"dma": dma, "trial": i, "onset_local": str(t)}
                     for i, t in enumerate(random_onsets(s.index, dma, plan)))
    RUN.mkdir()
    pd.DataFrame(selected).to_csv(RUN / "selection.csv", index=False)
    pd.DataFrame(dates).to_csv(RUN / "onsets.csv", index=False)
    write_json(RUN / "prepared.json", {
        "prepared_utc": datetime.now(timezone.utc).isoformat(),
        "input_hashes": record, "reader_report": read_report,
        "candidate_zones": len(candidates), "selected": details,
        "selection_sha256": sha(RUN / "selection.csv"),
        "onsets_sha256": sha(RUN / "onsets.csv"),
        "outcomes_computed": False,
        "note": "Selection and starts saved before baseline or injected warning runs."})
    print(json.dumps({"selected": details, "random_starts": len(dates),
                      "outcomes_computed": False}, indent=2), flush=True)


def run(csv_reads):
    prepared = json.loads((RUN / "prepared.json").read_text())
    plan = json.loads((HERE / "plan.json").read_text())
    check_snapshots(prepared["input_hashes"])
    assert sha(RUN / "selection.csv") == prepared["selection_sha256"]
    assert sha(RUN / "onsets.csv") == prepared["onsets_sha256"]
    if (RUN / "trials.csv").exists():
        raise FileExistsError("An injected run already exists; refusing to rerun/overwrite")
    series, _ = yw.read_area(FLOW)
    dates = pd.read_csv(RUN / "onsets.csv", dtype={"dma": str})
    previous = pd.read_csv(OLD_WARNINGS, dtype={"dma": str})
    summaries, baselines = [], []
    columns = ["dma", "rule", "size_m3h", "size_percent_reference", "trial", "onset_local",
               "primary_response", "any_warning", "delay_hours", "baseline_any_warning",
               "complete_seven_opportunities"]
    with (RUN / "trials.csv").open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for zone in prepared["selected"]:
            dma, reference = zone["dma"], zone["reference_m3h"]
            s = yw.to_frozen_reader(series[dma])
            result, frozen, adaptive = yw.R.both_rules(s)
            assert result.assessable, (dma, result.reason)
            baseline = {"frozen": frozen, "adaptive": adaptive}
            stamps = {name: {pd.Timestamp(w[1]) for w in ws} for name, ws in baseline.items()}
            onsets = [pd.Timestamp(x) for x in dates.loc[dates.dma == dma, "onset_local"]]
            complete = [all_seven_opportunities(result, s.index[0], t, plan["horizon_hours"])
                        for t in onsets]
            chances = {name: [response(ws, set(), t)["any_warning"] for t in onsets]
                       for name, ws in baseline.items()}
            for name, ws in baseline.items():
                old = previous[(previous.dma == dma) & (previous.rule == name)]
                assert sorted(stamps[name]) == sorted(pd.to_datetime(old.issue_time_local)), (dma, name)
                baselines.append({"dma": dma, "rule": name, "warnings": len(ws),
                                  "calendar_days": len(s) / 48 - plan["warnings_from_day_index"],
                                  "available_step_nights": int(np.isfinite(result.step[28:]).sum()),
                                  "warnings_per_zone_year": len(ws) * 365 / (len(s) / 48 - 28),
                                  "reference_m3h": reference,
                                  "reference_complete_nights": zone["reference_complete_nights"],
                                  "night_start_hour": result.night_start_hour,
                                  "seven_day_coincidence_probability": sum(chances[name]) / len(onsets),
                                  "complete_seven_opportunity_probability": sum(complete) / len(onsets)})
            for size, origin in zone["sizes"]:
                rows = {"frozen": [], "adaptive": []}
                for trial, onset in enumerate(onsets):
                    changed = inject(s, onset, size)
                    altered_result, fz, ad = yw.R.both_rules(changed)
                    assert altered_result.assessable, (dma, size, trial)
                    assert altered_result.night_start_hour == result.night_start_hour
                    assert altered_result.types == result.types
                    assert altered_result.threshold == result.threshold
                    for name, ws in (("frozen", fz), ("adaptive", ad)):
                        assert {pd.Timestamp(w[1]) for w in ws if pd.Timestamp(w[1]) < onset} == \
                               {t for t in stamps[name] if t < onset}, "Pre-onset warning changed"
                        r = response(ws, stamps[name], onset, plan["horizon_hours"])
                        row = {"dma": dma, "rule": name, "size_m3h": size,
                               "size_percent_reference": size / reference * 100 if reference else None,
                               "trial": trial, "onset_local": str(onset), **r,
                               "baseline_any_warning": chances[name][trial],
                               "complete_seven_opportunities": complete[trial]}
                        writer.writerow(row)
                        rows[name].append(row)
                for name in rows:
                    summaries.append({"dma": dma, "rule": name, "size_m3h": size,
                                      "size_percent_reference": size / reference * 100 if reference else None,
                                      "size_origin": origin, **summarise(rows[name])})
                handle.flush()
                print(f"Completed DMA {dma}, injected {size:.6g} m3/h, {len(onsets)} dates, both rules", flush=True)
    pd.DataFrame(summaries).to_csv(RUN / "curves.csv", index=False)
    pd.DataFrame(baselines).to_csv(RUN / "untouched.csv", index=False)
    minima = []
    for zone in prepared["selected"]:
        for name in ("frozen", "adaptive"):
            size = minimum_size([r for r in summaries if r["dma"] == zone["dma"] and r["rule"] == name],
                                plan["minimum_response_probability"])
            minima.append({"dma": zone["dma"], "rule": name, "smallest_tested_90pct_m3h": size,
                           "percent_reference": size / zone["reference_m3h"] * 100
                           if size is not None and zone["reference_m3h"] else None,
                           "status": "reached on tested grid" if size is not None else "not reached on tested grid"})
    pd.DataFrame(minima).to_csv(RUN / "minimum-sizes.csv", index=False)
    plot_and_report(prepared, summaries, baselines, minima)
    check_snapshots(prepared["input_hashes"])
    outputs = [p for p in RUN.iterdir() if p.is_file()]
    write_json(RUN / "finished.json", {
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "numpy": np.__version__, "pandas": pd.__version__,
        "csv_inputs_read": sorted(csv_reads), "repairs_read": False,
        "rules_unchanged": True, "baseline_warnings_match_saved_lists": True,
        "original_inputs_unchanged": True, "new_pass_fail_claim": False,
        "trial_rule_rows": len(summaries) * plan["starts_per_zone"],
        "files_sha256": {p.name: sha(p) for p in outputs}})
    print("Finished injected development study; stop for founder review.", flush=True)


def plot_and_report(prepared, rows, baselines, minima):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {"frozen": "#0d9488", "adaptive": "#7c3aed"}
    for zone in prepared["selected"]:
        dma, reference = zone["dma"], zone["reference_m3h"]
        fig, axes = plt.subplots(2, 1, figsize=(9, 7.8), sharex=True,
                                 gridspec_kw={"height_ratios": [1.25, 1]})
        for name in ("frozen", "adaptive"):
            group = sorted([r for r in rows if r["dma"] == dma and r["rule"] == name], key=lambda r: r["size_m3h"])
            x = np.array([r["size_m3h"] for r in group])
            axes[0].plot(x, [r["primary_probability"] * 100 for r in group], "o-", color=colors[name], label=name.capitalize())
            median = [r["median_delay_h"] if r["median_delay_h"] is not None else np.nan for r in group]
            low = [r["q25_delay_h"] if r["q25_delay_h"] is not None else np.nan for r in group]
            high = [r["q75_delay_h"] if r["q75_delay_h"] is not None else np.nan for r in group]
            axes[1].plot(x, median, "o-", color=colors[name], label=name.capitalize())
            axes[1].fill_between(x, low, high, color=colors[name], alpha=0.13)
        axes[0].axhline(90, color="#64748b", linewidth=1, linestyle="--", label="90% reporting convention")
        axes[0].set(ylabel="Extra / retimed warning within 7 days (%)", ylim=(-3, 103))
        axes[0].legend(loc="lower right", fontsize=9)
        axes[1].set(ylabel="Delay among responders (hours)", xlabel="Injected constant extra flow (m³/h, logarithmic scale)", ylim=(0, 170))
        axes[1].set_yticks([0, 24, 48, 72, 96, 120, 144, 168])
        for ax in axes:
            ax.set_xscale("log")
            ax.grid(alpha=0.2)
            ax.spines[["top", "right"]].set_visible(False)
        if reference:
            top = axes[0].secondary_xaxis("top", functions=(lambda x: x / reference * 100,
                                                           lambda x: x * reference / 100))
            top.set_xlabel("Added flow as % of this zone's minimum-night-flow reference", labelpad=9)
        fig.suptitle(f"DMA {dma}: artificial leaks on real Yorkshire readings\n200 random dates per size; both rules unchanged", fontsize=14, y=0.985)
        b = {r["rule"]: r for r in baselines if r["dma"] == dma}
        reference_text = f"{reference:.2f} m³/h" if reference is not None else "unavailable"
        footer = (f"Untouched warnings/year: frozen {b['frozen']['warnings_per_zone_year']:.1f}, adaptive {b['adaptive']['warnings_per_zone_year']:.1f}. "
                  f"Reference night flow: {reference_text}.\n"
                  "Delay lines: median; bands: middle 50% of responders. Misses remain in probability denominator.\n"
                  "Injected-step response, not real-leak accuracy. Background warnings are not known false alarms.")
        fig.text(0.08, 0.015, footer, fontsize=9, color="#475569", va="bottom")
        fig.subplots_adjust(left=0.105, right=0.96, bottom=0.18, top=0.81, hspace=0.12)
        for extension in ("png", "svg"):
            fig.savefig(RUN / f"dma-{dma}-detectability.{extension}", dpi=150, facecolor="white")
        plt.close(fig)
    lines = ["# What added leaks can the unchanged rules see?", "",
             "**Verified — development results:** constant synthetic flow was added to real Yorkshire N4 readings. These are injected responses, not observed real-leak detection. No repairs were read and no pass/fail test was run.", "",
             "**My judgement — fixed design:** five previously assessable zones selected only by exact completeness (numeric-ID tie break); 200 random start times per zone, shared across sizes/rules. Separate permanent steps: 0.5–32 m³/h plus 5–80% of each zone's minimum-night-flow reference. See [PLAN.md](../PLAN.md).", "",
             "**Verified — response meaning:** a warning within 168 hours at a time absent from the untouched run (extra or retimed). Existing coincident warnings do not count. The unchanged rule keeps its learning, adaptive threshold, arming and spacing. Delays describe responders only.", "",
             "| Zone | Night-flow reference, m³/h | Smallest tested 90% size: frozen / adaptive, m³/h | Untouched warnings/year: frozen / adaptive |", "|---|---:|---:|---:|"]
    for zone in prepared["selected"]:
        dma = zone["dma"]
        mm = {r["rule"]: r for r in minima if r["dma"] == dma}
        bb = {r["rule"]: r for r in baselines if r["dma"] == dma}
        size_text = lambda name: f"{mm[name]['smallest_tested_90pct_m3h']:.2f}" if mm[name]['smallest_tested_90pct_m3h'] is not None else "not reached"
        ref_text = f"{zone['reference_m3h']:.2f}" if zone['reference_m3h'] else "unavailable"
        lines.append(f"| {dma} | {ref_text} | {size_text('frozen')} / {size_text('adaptive')} | {bb['frozen']['warnings_per_zone_year']:.2f} / {bb['adaptive']['warnings_per_zone_year']:.2f} |")
    lines += ["", "**Verified:** the 90% size requires that size and every larger tested size to reach 90%; it is a grid result, not an interpolated physical limit. The reference is the median daily minimum complete two-hour mean within 00:00–06:00, days 29–365. It includes customer use and any existing losses. Percent sizes are in `minimum-sizes.csv`; all probabilities/counts and conditional delay quartiles are in `curves.csv`.", "",
              "**Verified:** `untouched.csv` gives warning counts over 337 calendar days, finite step nights, random-date seven-day warning coincidences and complete observation opportunities. Those warnings have unknown real outcomes. `trials.csv` preserves each start/size/rule result; `prepared.json` records selection, seeds and input/code hashes. Five paired-rule curves are below.", "",
              "**Unknown:** actual leak truth, pressure feedback, boundary/storage status and future performance. Additive steps omit pressure/demand interactions, gradual growth and repairs. Best-recorded zones and one reused year are not representative. Overlapping trials and a 200-date sample do not establish field confidence limits. No tuning or grid expansion followed outcomes.", "",
              "**My judgement:** review the curves and workload before step 2. This study measures what added steps stand out against these backgrounds, not how often crews would find real leaks.", ""]
    for zone in prepared["selected"]:
        dma = zone["dma"]
        lines.append(f"![Injected-step detectability for DMA {dma}](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/run/dma-{dma}-detectability.png)")
        lines.append("")
    with (RUN / "FINDINGS.md").open("x") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run"])
    action = parser.parse_args().action
    reads = install_csv_read_guard()
    if action == "prepare":
        prepare()
    else:
        run(reads)
