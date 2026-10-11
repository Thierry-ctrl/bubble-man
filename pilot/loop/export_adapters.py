"""DRAFT export-layout adapters, tested only on clearly INVENTED files.

CSV/XLSX, long/wide layouts and explicitly declared decimal/group separators.
Writes flow_readings.csv, meters.csv and zone.csv for the unchanged converter.
No detector, storage correction, resampling, repair-record access or guessing.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re

FLOW_COLUMNS = ["meter_id", "timestamp", "value", "unit", "quality"]
METER_COLUMNS = ["meter_id", "role", "zone_id", "value_type", "unit", "interval_minutes", "timestamp_marks"]
ZONE_COLUMNS = ["zone_id", "supply_regime", "internal_storage", "storage_level_meter",
                "boundary_valves_confirmed_closed", "local_time_zone"]
QUALITIES = {"ok", "estimated", "fault", "missing"}
DRAFT_STATUS = "draft; invented-file checks only; real-export compatibility unverified"


class AdapterError(ValueError):
    pass


def parse_offset(value):
    match = re.fullmatch(r"(?:UTC)?([+-])(\d{2}):(\d{2})", str(value).strip(), re.I)
    if not match:
        raise AdapterError("offset must be explicit, such as +02:00 or UTC+02:00")
    sign, hours, minutes = match.groups()
    h, m = int(hours), int(minutes)
    if h > 14 or m > 59 or (h == 14 and m != 0):
        raise AdapterError("offset outside supported fixed UTC range")
    return timezone((1 if sign == "+" else -1) * timedelta(hours=h, minutes=m))


def number_text(value, decimal_mark=".", thousands_separator=None, missing_tokens=("",)):
    """Preserve numeric meaning; no unit conversion or precision rounding."""
    if value is None:
        return ""
    if isinstance(value, bool):
        raise AdapterError("boolean is not a meter measurement")
    if decimal_mark not in (".", ","):
        raise AdapterError("decimal_mark must be '.' or ','")
    if thousands_separator is not None and (
            thousands_separator not in (".", ",", " ", "\u00a0", "\u202f")
            or thousands_separator == decimal_mark):
        raise AdapterError("declare a distinct supported thousands separator")
    if isinstance(value, (int, float, Decimal)):
        raw = str(value)  # Typed Excel numbers do not use display-locale separators.
    elif isinstance(value, str):
        raw = value.strip()
        if raw in missing_tokens:
            return ""
        match = re.fullmatch(r"([+-]?)([^eE]+)([eE][+-]?\d+)?", raw)
        if not match:
            raise AdapterError("invalid numeric text: " + repr(value))
        sign, body, exponent = match.groups()
        pieces = body.split(decimal_mark)
        if len(pieces) > 2 or (len(pieces) == 2 and not pieces[1].isdigit()):
            raise AdapterError("invalid decimal grouping: " + repr(value))
        whole = pieces[0]
        if thousands_separator and thousands_separator in whole:
            groups = whole.split(thousands_separator)
            if (not 1 <= len(groups[0]) <= 3 or not all(x.isdigit() for x in groups)
                    or any(len(x) != 3 for x in groups[1:])):
                raise AdapterError("invalid thousands grouping: " + repr(value))
            whole = "".join(groups)
        if not whole and len(pieces) == 2:
            whole = "0"
        if not whole.isdigit():
            raise AdapterError("unexpected separator or nonnumeric value: " + repr(value))
        raw = sign + whole + ("." + pieces[1] if len(pieces) == 2 else "") + (exponent or "")
    else:
        raise AdapterError("unsupported measurement type")
    try:
        numeric = Decimal(raw)
    except InvalidOperation as error:
        raise AdapterError("invalid meter measurement") from error
    if not numeric.is_finite():
        raise AdapterError("nonfinite meter measurement")
    return format(numeric, "f")


def timestamp(value, config):
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        text = value.strip()
        try:
            if config.get("timestamp_format"):
                parsed = datetime.strptime(text, config["timestamp_format"])
            else:
                if not re.match(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}", text):
                    raise ValueError("use ISO datetime or an explicit timestamp_format")
                parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
        except ValueError as error:
            raise AdapterError("unparseable/ambiguous timestamp: " + repr(value)) from error
    else:
        raise AdapterError("timestamp must be text or a typed Excel datetime; no serial guessing")
    if parsed.utcoffset() is None:
        if not config.get("naive_utc_offset"):
            raise AdapterError("timezone missing; declare naive_utc_offset explicitly")
        parsed = parsed.replace(tzinfo=parse_offset(config["naive_utc_offset"]))
    return parsed.isoformat(), parsed.astimezone(timezone.utc)


def _text(value):
    if value is None:
        return ""
    if not isinstance(value, str):
        raise AdapterError("IDs, units, headers and quality codes must be text")
    return value.strip()


def _cell(cell):
    if cell.data_type in ("f", "e"):
        raise AdapterError("formula/error Excel cell is not a recorded value: " + cell.coordinate)
    return cell.value


def _read_table(source, config):
    header_row = config.get("header_row", 1)
    if isinstance(header_row, bool) or not isinstance(header_row, int) or header_row < 1:
        raise AdapterError("header_row must be a positive one-based row number")
    fmt = config.get("source_format")
    if fmt == "csv":
        delimiter = config.get("delimiter", ",")
        if not isinstance(delimiter, str) or len(delimiter) != 1:
            raise AdapterError("delimiter must be one declared character")
        with source.open(encoding="utf-8-sig", newline="") as handle:
            try:
                all_rows = list(csv.reader(handle, delimiter=delimiter, strict=True))
            except csv.Error as error:
                raise AdapterError("malformed delimited table") from error
        if len(all_rows) < header_row:
            raise AdapterError("header_row is beyond the source")
        headers = [_text(x) for x in all_rows[header_row - 1]]
        rows = [(i + 1, row) for i, row in enumerate(all_rows) if i >= header_row]
    elif fmt == "xlsx":
        if source.suffix.lower() != ".xlsx" or not config.get("sheet"):
            raise AdapterError("xlsx needs an explicit worksheet and .xlsx file")
        try:
            from openpyxl import load_workbook
        except ImportError as error:
            raise AdapterError("xlsx reading requires openpyxl (read-only use)") from error
        book = load_workbook(source, data_only=False, read_only=False, keep_links=False)
        try:
            if config["sheet"] not in book.sheetnames:
                raise AdapterError("declared worksheet not found")
            sheet = book[config["sheet"]]
            if header_row > sheet.max_row:
                raise AdapterError("header_row is beyond the worksheet")
            if any(r.max_row >= header_row for r in sheet.merged_cells.ranges):
                raise AdapterError("merged cells in the selected table need a separate explicit layout")
            cell_rows = list(sheet.iter_rows(min_row=header_row))
            # Remove empty trailing columns only if both headers and all rows are empty.
            width = max((i + 1 for row in cell_rows for i, cell in enumerate(row)
                         if cell.value is not None), default=0)
            headers = [_text(_cell(c)) for c in cell_rows[0][:width]]
            rows = [(header_row + i, [_cell(c) for c in row[:width]])
                    for i, row in enumerate(cell_rows[1:], 1)]
        finally:
            book.close()
    else:
        raise AdapterError("source_format must be csv or xlsx")
    if not headers or any(not x for x in headers) or len(set(headers)) != len(headers):
        raise AdapterError("table headers must be present, nonempty and unique")
    return headers, rows


def _metadata(config):
    if not isinstance(config.get("zone"), dict) or not isinstance(config.get("meters"), list):
        raise AdapterError("explicit zone and meter metadata required")
    zone = dict(config["zone"])
    if set(ZONE_COLUMNS) - set(zone):
        raise AdapterError("zone metadata lacks required converter fields")
    for field in ZONE_COLUMNS:
        zone[field] = _text(zone[field])
        if not zone[field] and field != "storage_level_meter":
            raise AdapterError("missing zone metadata: " + field)
    parse_offset(zone["local_time_zone"])
    if zone["supply_regime"] not in ("continuous", "intermittent", "unknown"):
        raise AdapterError("supply_regime must be continuous, intermittent or unknown")
    if zone["boundary_valves_confirmed_closed"] not in ("yes", "no", "unknown"):
        raise AdapterError("boundary confirmation must be yes, no or unknown")
    meters = {}
    for source_meter in config["meters"]:
        if not isinstance(source_meter, dict) or set(METER_COLUMNS) - set(source_meter):
            raise AdapterError("meter metadata lacks required converter fields")
        meter = dict(source_meter)
        for field in METER_COLUMNS:
            if field != "interval_minutes":
                meter[field] = _text(meter[field])
                if not meter[field]:
                    raise AdapterError("empty meter metadata: " + field)
        mid = meter["meter_id"]
        if mid in meters or meter["zone_id"] != zone["zone_id"]:
            raise AdapterError("duplicate meter ID or different zone")
        if meter["role"] not in ("inlet", "outlet", "transfer_in", "transfer_out"):
            raise AdapterError("unknown meter role")
        vt = meter["value_type"]
        if vt not in ("instantaneous_rate", "interval_average_rate", "interval_volume", "cumulative_total"):
            raise AdapterError("unknown meter value_type")
        allowed_units = {"m3/h", "l/s", "m3/s"} if vt.endswith("rate") else {"m3", "l"}
        if meter["unit"].lower() not in allowed_units:
            raise AdapterError("unit does not fit declared value_type")
        step = str(meter["interval_minutes"])
        if not step.isdigit() or int(step) <= 0 or 30 % int(step):
            raise AdapterError("interval_minutes must be a positive divisor of 30")
        meter["interval_minutes"] = step
        allowed_marks = {"reading_time"} if vt in ("instantaneous_rate", "cumulative_total") else {"interval_start", "interval_end"}
        if meter["timestamp_marks"] not in allowed_marks:
            raise AdapterError("timestamp_marks does not fit declared value_type")
        meters[mid] = meter
    if not meters or not any(x["role"] in ("inlet", "transfer_in") for x in meters.values()):
        raise AdapterError("declare all meters, including at least one inlet")
    return zone, meters


def _csv_write(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def adapt_export(source, config, destination):
    """Create a NEW canonical export folder plus source-row audit and mapping."""
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise AdapterError("destination must be a new folder; existing exports are not overwritten")
    zone, meters = _metadata(config)
    # Validate locale even when the first measurement happens to be a blank.
    number_text("0", config.get("decimal_mark", "."), config.get("thousands_separator"))
    columns = config.get("columns", {})
    layout = config.get("layout")
    if layout == "long":
        if set(("timestamp", "meter_id", "value")) - set(columns):
            raise AdapterError("long layout requires timestamp, meter_id and value columns")
        series = [columns]
    elif layout == "wide":
        series = config.get("series", [])
        if "timestamp" not in columns or not series:
            raise AdapterError("wide layout requires timestamp and explicit series mappings")
        if any(set(("meter_id", "value")) - set(s) for s in series):
            raise AdapterError("each wide series needs a meter ID and value column")
        ids = [s["meter_id"] for s in series]
        if len(set(ids)) != len(ids) or set(ids) != set(meters):
            raise AdapterError("wide series must map every declared meter exactly once")
    else:
        raise AdapterError("layout must be long or wide")
    quality_map = config.get("quality_map", {})
    if not isinstance(quality_map, dict) or any(v not in QUALITIES for v in quality_map.values()):
        raise AdapterError("quality_map targets must be ok, estimated, fault or missing")
    fixed_quality = config.get("constant_quality")
    if fixed_quality is not None and fixed_quality not in QUALITIES:
        raise AdapterError("constant_quality must be an explicit canonical quality")
    if any("quality" not in s and fixed_quality is None for s in series):
        raise AdapterError("quality column/mapping or explicit constant_quality required")
    used = {columns["timestamp"]}
    for s in series:
        used.update(s[k] for k in ("value", "quality", "unit") if k in s)
    if layout == "long":
        used.add(columns["meter_id"])
    # Time, ID and value fields are distinct; meters may share one row-quality field.
    fields = [columns["timestamp"]]
    for s in series:
        fields.append(s["value"])
    if layout == "long":
        fields.append(columns["meter_id"])
    quality_fields = {s["quality"] for s in series if "quality" in s}
    unit_fields = {s["unit"] for s in series if "unit" in s}
    if (len(set(fields)) != len(fields) or set(fields) & (quality_fields | unit_fields)
            or quality_fields & unit_fields):
        raise AdapterError("mapped source columns must be distinct")
    headers, source_rows = _read_table(source, config)
    ignored = config.get("ignore_columns", [])
    if not isinstance(ignored, list) or set(ignored) & used:
        raise AdapterError("ignore_columns must be separate from mapped columns")
    if used - set(headers) or set(ignored) - set(headers) or set(headers) - used - set(ignored):
        raise AdapterError("source headers must match mappings and explicitly ignored columns")
    tokens = config.get("missing_tokens", [""])
    if not isinstance(tokens, list) or any(not isinstance(x, str) for x in tokens):
        raise AdapterError("missing_tokens must be an explicit text list")
    output, audit = [], []
    blank_rows, keys = 0, Counter()
    for row_number, values in source_rows:
        if not values or all(x is None or x == "" for x in values):
            blank_rows += 1
            continue
        if len(values) != len(headers):
            raise AdapterError(f"source row {row_number}: wrong field count; check delimiter/quoting")
        row = dict(zip(headers, values))
        try:
            ts, instant = timestamp(row[columns["timestamp"]], config)
            for spec in series:
                mid = _text(row[columns["meter_id"]]) if layout == "long" else spec["meter_id"]
                if mid not in meters:
                    raise AdapterError("source contains undeclared meter: " + mid)
                unit = _text(row[spec["unit"]]) if "unit" in spec else meters[mid]["unit"]
                if unit.lower() != meters[mid]["unit"].lower():
                    raise AdapterError("source unit disagrees with meter metadata")
                original_quality = row[spec["quality"]] if "quality" in spec else None
                raw_quality = _text(original_quality) if "quality" in spec else None
                if raw_quality is not None:
                    if raw_quality not in quality_map:
                        raise AdapterError("unmapped source quality code: " + repr(raw_quality))
                    quality = quality_map[raw_quality]
                else:
                    quality = fixed_quality
                raw_value = row[spec["value"]]
                value = number_text(raw_value, config.get("decimal_mark", "."),
                                    config.get("thousands_separator"), tokens)
                mapped_quality = quality
                if value == "":
                    quality = "missing"
                canonical = dict(zip(FLOW_COLUMNS, (mid, ts, value, unit, quality)))
                output.append(canonical)
                keys[mid, instant] += 1
                audit.append({"source_row": row_number, "source_value_column": spec["value"],
                              "source_timestamp": row[columns["timestamp"]], "source_value": raw_value,
                              "source_quality": original_quality, "mapped_quality": mapped_quality,
                              "canonical": canonical})
        except AdapterError as error:
            raise AdapterError(f"source row {row_number}: {error}") from error
    counts = Counter(x["meter_id"] for x in output)
    if set(meters) - set(counts):
        raise AdapterError("no rows for one or more declared meters")
    report = {"status": DRAFT_STATUS, "source_format": config["source_format"], "layout": layout,
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "output_rows": len(output), "rows_per_meter": dict(counts),
              "blank_source_rows": blank_rows, "ignored_columns": ignored,
              "blank_measurements": sum(x["value"] == "" for x in output),
              "duplicate_meter_instants": sum(n > 1 for n in keys.values()),
              "quality_counts": dict(Counter(x["quality"] for x in output)),
              "changes": "reshape; declared timestamp/locale/quality mapping; no unit conversion, sorting, gap filling or resampling"}
    destination.mkdir(parents=True, exist_ok=False)
    _csv_write(destination / "flow_readings.csv", FLOW_COLUMNS, output)
    extra_meter_columns = sorted(set().union(*(set(x) for x in meters.values())) - set(METER_COLUMNS))
    _csv_write(destination / "meters.csv", METER_COLUMNS + extra_meter_columns, meters.values())
    _csv_write(destination / "zone.csv", ZONE_COLUMNS + sorted(set(zone) - set(ZONE_COLUMNS)), [zone])
    with (destination / "source-audit.jsonl").open("w", encoding="utf-8") as handle:
        for item in audit:
            handle.write(json.dumps(item, ensure_ascii=False, default=str) + "\n")
    (destination / "source-mapping.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    (destination / "adapter-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an explicitly mapped readings export; no detector run")
    parser.add_argument("source")
    parser.add_argument("mapping_json")
    parser.add_argument("new_destination")
    args = parser.parse_args()
    try:
        report = adapt_export(args.source, json.loads(Path(args.mapping_json).read_text()), args.new_destination)
    except (AdapterError, OSError, json.JSONDecodeError) as error:
        parser.exit(2, str(error) + "\n")
    print(json.dumps(report, indent=2))
