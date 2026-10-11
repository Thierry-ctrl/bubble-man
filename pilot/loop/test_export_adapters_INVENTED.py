"""All source files, meters, dates, quality codes and values are INVENTED.

These checks exercise export formats and the unchanged converter only.
They never import/run a detector or open incident/repair/leak records.
"""
from copy import deepcopy
import csv
from decimal import Decimal
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from export_adapters import AdapterError, adapt_export, number_text

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "adapter-fixtures-INVENTED"
SCRATCH = FIXTURES / "_scratch"
BASE = json.loads((FIXTURES / "example-mapping-INVENTED.json").read_text())
WIDE_SERIES = [
    {"meter_id": "INVENTED-M1", "value": "INVENTED-M1 flow", "quality": "INVENTED-M1 flag"},
    {"meter_id": "INVENTED-M2", "value": "INVENTED-M2 flow", "quality": "INVENTED-M2 flag"},
]
INVENTED_TIME = "2026-01-01T00:00:00+02:00"


def config_for(layout="long", fmt="csv", native=False):
    cfg = deepcopy(BASE)
    cfg["layout"], cfg["source_format"] = layout, fmt
    if layout == "wide":
        cfg["columns"] = {"timestamp": "Time"}
        cfg["series"] = deepcopy(WIDE_SERIES)
    if fmt == "xlsx":
        cfg["sheet"] = "INVENTED_NativeDates" if native else "INVENTED_" + layout.title()
        cfg["header_row"] = 3
        cfg["decimal_mark"] = "."
        cfg["naive_utc_offset"] = "+00:00"  # First two Excel layouts explicitly store UTC wall time.
    if native:
        cfg["naive_utc_offset"] = "+02:00"
    return cfg


def source_for(layout="long", fmt="csv"):
    return FIXTURES / ("exports-INVENTED.xlsx" if fmt == "xlsx" else
                       layout + "-decimal-comma-INVENTED.csv")


def read_rows(folder):
    with (folder / "flow_readings.csv").open(newline="") as handle:
        return list(csv.DictReader(handle))


class InventedAdapterCases(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="INVENTED-", dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)

    def custom(self, rows=None, headers=None, config=None):
        cfg = deepcopy(BASE) if config is None else config
        cfg["meters"] = cfg["meters"][:1]
        p = self.work / "custom-INVENTED.csv"
        with p.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, delimiter=cfg.get("delimiter", ";"))
            writer.writerow(["Meter", "Time", "Reading", "Units", "Status"] if headers is None else headers)
            writer.writerows([["INVENTED-M1", INVENTED_TIME, "1,25", "L/s", "GOOD"]] if rows is None else rows)
        return p, cfg

    def assert_rejected(self, source, cfg):
        target = self.work / "rejected-output-INVENTED"
        with self.assertRaises(AdapterError):
            adapt_export(source, cfg, target)
        self.assertFalse(target.exists(), "validation failure must not create a partial export")

    def test_01_long_csv_decimal_comma_preserves_zero_missing_flags_and_units(self):
        target = self.work / "out"
        report = adapt_export(source_for(), config_for(), target)
        rows = read_rows(target)
        self.assertEqual(len(rows), 12)
        self.assertEqual(Decimal(rows[0]["value"]), Decimal("1.25"))
        self.assertEqual(rows[4]["value"], "0")
        self.assertEqual(rows[6]["value"], "")
        self.assertEqual(rows[6]["quality"], "missing")
        self.assertEqual(rows[5]["quality"], "estimated")
        self.assertEqual(rows[8]["quality"], "fault")
        self.assertEqual(rows[0]["unit"], "L/s")
        self.assertEqual(report["blank_measurements"], 1)

    def test_02_all_five_valid_layouts_have_same_canonical_meaning(self):
        results = []
        for i, (layout, fmt, native) in enumerate([
            ("long", "csv", False), ("wide", "csv", False),
            ("long", "xlsx", False), ("wide", "xlsx", False), ("wide", "xlsx", True)]):
            target = self.work / f"out-{i}"
            adapt_export(source_for(layout, fmt), config_for(layout, fmt, native), target)
            results.append([(x["meter_id"], datetime.fromisoformat(x["timestamp"]).astimezone(timezone.utc),
                             None if x["value"] == "" else Decimal(x["value"]), x["unit"], x["quality"])
                            for x in read_rows(target)])
        self.assertTrue(all(rows == results[0] for rows in results))

    def test_03_unchanged_converter_accepts_every_layout_with_same_invented_output(self):
        converter_path = HERE.parent / "convert_utility_data.py"
        before = hashlib.sha256(converter_path.read_bytes()).hexdigest()
        spec = importlib.util.spec_from_file_location("unchanged_converter_invented_check", converter_path)
        converter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(converter)
        for i, (layout, fmt) in enumerate([("long", "csv"), ("wide", "csv"),
                                           ("long", "xlsx"), ("wide", "xlsx")]):
            source = self.work / f"canonical-{i}"
            output = self.work / f"converted-{i}"
            adapt_export(source_for(layout, fmt), config_for(layout, fmt), source)
            report = converter.convert(source, output)
            with (output / "zone_net_inflow_30min.csv").open() as handle:
                rows = list(csv.DictReader(handle))
            # First half-hour: mean inlet 1.875 L/s = 6.75 m3/h, minus 2 m3/h outlet.
            self.assertEqual(Decimal(rows[0]["Value"]), Decimal("4.75"))
            self.assertEqual([x["Value"] for x in rows[1:]], ["", "", ""])
            self.assertFalse(report["readiness"]["likely_assessable_by_frozen_method"])
        self.assertEqual(hashlib.sha256(converter_path.read_bytes()).hexdigest(), before)

    def test_04_native_excel_date_requires_declared_offset(self):
        cfg = config_for("wide", "xlsx")
        cfg["sheet"] = "INVENTED_NativeDates"
        del cfg["naive_utc_offset"]
        self.assert_rejected(source_for(fmt="xlsx"), cfg)

    def test_05_formula_cells_are_rejected_without_using_cached_value(self):
        cfg = config_for("wide", "xlsx")
        cfg["sheet"] = "INVENTED_Formula"
        self.assert_rejected(source_for(fmt="xlsx"), cfg)

    def test_06_merged_headers_are_rejected(self):
        cfg = config_for("wide", "xlsx")
        cfg["sheet"] = "INVENTED_Merged"
        self.assert_rejected(source_for(fmt="xlsx"), cfg)

    def test_07_missing_or_wrong_excel_sheet_is_rejected(self):
        for sheet in (None, "INVENTED_DOES_NOT_EXIST"):
            cfg = config_for(fmt="xlsx")
            cfg["sheet"] = sheet
            self.assert_rejected(source_for(fmt="xlsx"), cfg)

    def test_08_legacy_excel_extension_is_explicitly_unsupported(self):
        p = self.work / "legacy-INVENTED.xls"
        shutil.copyfile(source_for(fmt="xlsx"), p)
        self.assert_rejected(p, config_for(fmt="xlsx"))

    def test_09_strict_declared_grouping_handles_thousands_without_guessing(self):
        self.assertEqual(number_text("1.234,560", ",", "."), "1234.560")
        self.assertEqual(number_text("1,234.5", ".", ","), "1234.5")
        self.assertEqual(number_text("1 234,5", ",", " "), "1234.5")
        self.assertEqual(number_text("-1,25e2", ","), "-125")
        self.assertEqual(number_text(",5", ","), "0.5")

    def test_10_mixed_or_malformed_grouping_is_rejected(self):
        for value in ("1.25", "12,3,4", "1 234,5", "1.23,45", "1234.567,8"):
            with self.assertRaises(AdapterError):
                number_text(value, ",", ".")

    def test_11_typed_excel_number_does_not_depend_on_display_locale(self):
        self.assertEqual(number_text(1.25, ",", "."), "1.25")
        self.assertEqual(number_text(0, ","), "0")

    def test_12_nonnumeric_and_nonfinite_values_fail_visibly(self):
        for value in (True, float("nan"), float("inf"), "NaN", "2 L/s", "=1+1"):
            with self.assertRaises(AdapterError):
                number_text(value)

    def test_13_negative_measurement_is_preserved_for_converter_to_review(self):
        p, cfg = self.custom(rows=[["INVENTED-M1", INVENTED_TIME, "-1,25", "L/s", "GOOD"]])
        target = self.work / "out"
        adapt_export(p, cfg, target)
        self.assertEqual(read_rows(target)[0]["value"], "-1.25")

    def test_14_explicit_missing_token_is_not_zero(self):
        p, cfg = self.custom(rows=[["INVENTED-M1", INVENTED_TIME, "NA", "L/s", "GOOD"]])
        target = self.work / "out"
        adapt_export(p, cfg, target)
        self.assertEqual(read_rows(target)[0]["value"], "")
        self.assertEqual(read_rows(target)[0]["quality"], "missing")

    def test_15_unmapped_quality_code_does_not_become_ok(self):
        p, cfg = self.custom(rows=[["INVENTED-M1", INVENTED_TIME, "1", "L/s", "MAYBE"]])
        self.assert_rejected(p, cfg)

    def test_16_quality_not_present_needs_explicit_constant(self):
        p, cfg = self.custom()
        del cfg["columns"]["quality"]
        cfg["ignore_columns"] = ["Status"]
        self.assert_rejected(p, cfg)
        cfg["constant_quality"] = "ok"
        target = self.work / "accepted"
        adapt_export(p, cfg, target)
        self.assertEqual(read_rows(target)[0]["quality"], "ok")

    def test_17_unknown_meter_and_unit_mismatch_are_rejected(self):
        for mid, unit in (("INVENTED-UNKNOWN", "L/s"), ("INVENTED-M1", "m3/h")):
            p, cfg = self.custom(rows=[[mid, INVENTED_TIME, "1", unit, "GOOD"]])
            self.assert_rejected(p, cfg)

    def test_18_duplicate_meter_metadata_is_rejected(self):
        p, cfg = self.custom()
        cfg["meters"].append(deepcopy(cfg["meters"][0]))
        self.assert_rejected(p, cfg)

    def test_19_duplicate_readings_survive_and_are_counted(self):
        row = ["INVENTED-M1", INVENTED_TIME, "1", "L/s", "GOOD"]
        p, cfg = self.custom(rows=[row, row])
        target = self.work / "out"
        report = adapt_export(p, cfg, target)
        self.assertEqual(len(read_rows(target)), 2)
        self.assertEqual(report["duplicate_meter_instants"], 1)

    def test_20_gaps_and_source_order_are_not_filled_or_sorted(self):
        rows = [["INVENTED-M1", "2026-01-01T02:00:00+02:00", "2", "L/s", "GOOD"],
                ["INVENTED-M1", INVENTED_TIME, "1", "L/s", "GOOD"]]
        p, cfg = self.custom(rows=rows)
        target = self.work / "out"
        adapt_export(p, cfg, target)
        self.assertEqual([x["timestamp"] for x in read_rows(target)], [r[1] for r in rows])

    def test_21_ambiguous_date_needs_format_and_offset(self):
        p, cfg = self.custom(rows=[["INVENTED-M1", "03/04/2026 00:00", "1", "L/s", "GOOD"]])
        self.assert_rejected(p, cfg)
        cfg["timestamp_format"] = "%d/%m/%Y %H:%M"
        self.assert_rejected(p, cfg)
        cfg["naive_utc_offset"] = "+02:00"
        target = self.work / "accepted"
        adapt_export(p, cfg, target)
        self.assertEqual(read_rows(target)[0]["timestamp"], "2026-04-03T00:00:00+02:00")

    def test_22_timestamp_is_not_snapped_or_shifted_to_interval_start(self):
        time = "2026-01-01T00:01:01+02:00"
        p, cfg = self.custom(rows=[["INVENTED-M1", time, "1", "L/s", "GOOD"]])
        cfg["meters"][0]["timestamp_marks"] = "interval_end"
        target = self.work / "out"
        adapt_export(p, cfg, target)
        self.assertEqual(read_rows(target)[0]["timestamp"], time)

    def test_23_missing_headers_or_duplicate_headers_are_rejected(self):
        for headers in (["Meter", "Time", "Reading", "Units", "Units"],
                        ["Meter", "Time", "Reading", "Units", ""]):
            p, cfg = self.custom(headers=headers)
            self.assert_rejected(p, cfg)

    def test_24_extra_source_column_needs_explicit_ignore(self):
        p, cfg = self.custom(headers=["Meter", "Time", "Reading", "Units", "Status", "Comment"],
                             rows=[["INVENTED-M1", INVENTED_TIME, "1", "L/s", "GOOD", "INVENTED"]])
        self.assert_rejected(p, cfg)
        cfg["ignore_columns"] = ["Comment"]
        report = adapt_export(p, cfg, self.work / "accepted")
        self.assertEqual(report["ignored_columns"], ["Comment"])

    def test_25_unquoted_decimal_comma_cannot_change_column_positions(self):
        p, cfg = self.custom()
        p.write_text("Meter,Time,Reading,Units,Status\nINVENTED-M1," + INVENTED_TIME + ",1,25,L/s,GOOD\n")
        cfg["delimiter"] = ","
        self.assert_rejected(p, cfg)

    def test_26_wide_series_cannot_drop_or_duplicate_declared_meter(self):
        for mappings in (WIDE_SERIES[:1], [WIDE_SERIES[0], WIDE_SERIES[0]]):
            cfg = config_for("wide")
            cfg["series"] = deepcopy(mappings)
            self.assert_rejected(source_for("wide"), cfg)

    def test_27_metadata_semantics_are_required_not_inferred(self):
        for field, value in (("unit", "unknown"), ("value_type", "unknown"),
                             ("timestamp_marks", "unknown"), ("interval_minutes", 7),
                             ("role", "customer"), ("zone_id", "INVENTED-OTHER")):
            p, cfg = self.custom()
            cfg["meters"][0][field] = value
            self.assert_rejected(p, cfg)

    def test_28_no_rows_for_a_declared_meter_is_visible(self):
        p, cfg = self.custom()
        cfg["meters"] = deepcopy(BASE["meters"])
        self.assert_rejected(p, cfg)

    def test_29_existing_destination_is_never_overwritten(self):
        target = self.work / "existing"
        target.mkdir()
        sentinel = target / "INVENTED-sentinel.txt"
        sentinel.write_text("keep")
        with self.assertRaises(AdapterError):
            adapt_export(source_for(), config_for(), target)
        self.assertEqual(sentinel.read_text(), "keep")

    def test_30_source_is_unchanged_and_audit_keeps_original_quality_and_value(self):
        source = source_for()
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        target = self.work / "out"
        report = adapt_export(source, config_for(), target)
        audit = [json.loads(line) for line in (target / "source-audit.jsonl").read_text().splitlines()]
        self.assertEqual(audit[0]["source_value"], "1,25")
        self.assertEqual(audit[6]["source_quality"], "GOOD")
        self.assertEqual(audit[6]["canonical"]["quality"], "missing")
        self.assertEqual(before, report["source_sha256"])
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)

    def test_31_meter_and_zone_context_survives(self):
        target = self.work / "out"
        adapt_export(source_for(), config_for(), target)
        with (target / "zone.csv").open() as handle:
            zone = list(csv.DictReader(handle))[0]
        with (target / "meters.csv").open() as handle:
            meters = list(csv.DictReader(handle))
        self.assertEqual(zone["notes"], BASE["zone"]["notes"])
        self.assertEqual(meters[0]["timestamp_marks"], "interval_start")
        self.assertEqual(meters[1]["role"], "outlet")

    def test_32_unknown_supply_and_storage_are_not_changed_to_suitable(self):
        p, cfg = self.custom()
        cfg["zone"]["supply_regime"] = "unknown"
        cfg["zone"]["internal_storage"] = "unknown"
        cfg["zone"]["boundary_valves_confirmed_closed"] = "unknown"
        target = self.work / "out"
        adapt_export(p, cfg, target)
        with (target / "zone.csv").open() as handle:
            zone = list(csv.DictReader(handle))[0]
        self.assertEqual(zone["supply_regime"], "unknown")
        self.assertEqual(zone["internal_storage"], "unknown")

    def test_33_cumulative_counter_reset_is_preserved_not_repaired(self):
        p, cfg = self.custom(rows=[
            ["INVENTED-M1", INVENTED_TIME, "100", "m3", "GOOD"],
            ["INVENTED-M1", "2026-01-01T00:15:00+02:00", "105", "m3", "GOOD"],
            ["INVENTED-M1", "2026-01-01T00:30:00+02:00", "2", "m3", "GOOD"]])
        cfg["meters"][0].update(value_type="cumulative_total", unit="m3", timestamp_marks="reading_time")
        target = self.work / "out"
        adapt_export(p, cfg, target)
        self.assertEqual([x["value"] for x in read_rows(target)], ["100", "105", "2"])

    def test_34_one_explicit_row_quality_column_can_apply_to_both_meters(self):
        cfg = config_for("wide")
        for series in cfg["series"]:
            series["quality"] = "Status"
        p = self.work / "shared-quality-INVENTED.csv"
        with p.open("w", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(["Time", "INVENTED-M1 flow", "INVENTED-M2 flow", "Status"])
            writer.writerow([INVENTED_TIME, "1,25", "2,0", "FAULT"])
        target = self.work / "out"
        adapt_export(p, cfg, target)
        self.assertEqual([x["quality"] for x in read_rows(target)], ["fault", "fault"])

    def test_35_audit_retains_whitespace_in_original_quality_code(self):
        p, cfg = self.custom(rows=[["INVENTED-M1", INVENTED_TIME, "1", "L/s", " GOOD "]])
        target = self.work / "out"
        adapt_export(p, cfg, target)
        audit = json.loads((target / "source-audit.jsonl").read_text())
        self.assertEqual(audit["source_quality"], " GOOD ")
        self.assertEqual(audit["canonical"]["quality"], "ok")

    def test_36_measurement_cannot_alias_timestamp_or_quality_column(self):
        for name in ("Time", "INVENTED-M1 flag"):
            cfg = config_for("wide")
            cfg["series"][0]["value"] = name
            self.assert_rejected(source_for("wide"), cfg)


if __name__ == "__main__":
    unittest.main()
