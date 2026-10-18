#!/usr/bin/env python3
"""Print a Loopology Session Timer link that asks to add one or more history entries.

The page reads #add=<base64url JSON> in the browser and asks before saving.
Nothing in the hash is sent to a server.

Examples:
  python3 tools/make-entry-link.py \\
    --id S-2026-020 --title "Evening loops" \\
    --date 2026-10-20 --time "7:00 PM" --duration 01:30:00 \\
    --plan planned --note "Bring the new motif"

  python3 tools/make-entry-link.py --json sessions.json
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
DEFAULT_BASE = "https://gdotbennettmusic.github.io/LST-10/"


def parse_clock(value: str) -> tuple[int, int, int]:
    text = value.strip()
    ampm = ""
    lower = text.lower()
    if lower.endswith("am") or lower.endswith("pm"):
        ampm = lower[-2:]
        text = text[:-2].strip()
    parts = text.split(":")
    if len(parts) not in (1, 2, 3) or not parts[0]:
        raise SystemExit(f"Could not read time {value!r}. Use 7:00 PM or 19:00.")
    try:
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        second = int(parts[2]) if len(parts) > 2 else 0
    except ValueError:
        raise SystemExit(f"Could not read time {value!r}. Use 7:00 PM or 19:00.")
    if ampm == "pm" and hour < 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59 or second > 59:
        raise SystemExit(f"Could not read time {value!r}. Use 7:00 PM or 19:00.")
    return hour, minute, second


def aware_start(date: str | None, time_value: str | None, start: str | None) -> datetime | None:
    if start:
        text = start.strip()
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            raise SystemExit(f"Could not read --start {start!r}. Use an ISO 8601 time.")
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=ET)
        return parsed.astimezone(ET)
    if date and time_value:
        if len(date) != 10 or date[4] != "-" or date[7] != "-":
            raise SystemExit("date must be YYYY-MM-DD.")
        hour, minute, second = parse_clock(time_value)
        year, month, day = (int(date[0:4]), int(date[5:7]), int(date[8:10]))
        return datetime(year, month, day, hour, minute, second, tzinfo=ET)
    return None


def build_entry(args: argparse.Namespace) -> dict:
    if args.date and (len(args.date) != 10 or args.date[4] != "-" or args.date[7] != "-"):
        raise SystemExit("date must be YYYY-MM-DD.")
    if args.plan and args.plan not in ("done", "planned"):
        raise SystemExit('--plan must be "done" or "planned".')
    entry: dict = {}
    if args.id:
        entry["id"] = args.id
    if args.title:
        entry["title"] = args.title
    if args.date:
        entry["date"] = args.date
    if args.time:
        entry["time"] = args.time
    if args.start:
        entry["start"] = args.start
    if args.end:
        entry["end"] = args.end
    if args.duration:
        entry["duration"] = args.duration
    if args.note:
        entry["notes"] = list(args.note)
    when = aware_start(args.date, args.time, args.start)
    plan = args.plan
    if not plan and when is not None:
        plan = "planned" if when > datetime.now(ET) else "done"
    if plan:
        entry["planStatus"] = plan
    if not entry:
        raise SystemExit("Give at least one field, or pass --json.")
    return entry


def encode(payload: object) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def main() -> None:
    parser = argparse.ArgumentParser(description="Print an LST-10 #add= link for session history.")
    parser.add_argument("--base", default=DEFAULT_BASE, help=f"Page URL (default: {DEFAULT_BASE})")
    parser.add_argument("--id", help="Session id, such as S-2026-020")
    parser.add_argument("--title", help="Session title")
    parser.add_argument("--date", help="Calendar date YYYY-MM-DD, America/New_York")
    parser.add_argument("--time", help='Clock time, such as 7:00 PM or 19:00, America/New_York')
    parser.add_argument("--start", help="ISO 8601 start. A value without a zone is America/New_York.")
    parser.add_argument("--end", help="ISO 8601 end. A value without a zone is America/New_York.")
    parser.add_argument("--duration", help="HH:MM:SS, 90m, 1h30m, or a number of seconds")
    parser.add_argument("--plan", choices=("done", "planned"), help="done or planned. Default follows the start time.")
    parser.add_argument("--note", action="append", help="Note text. Repeat for several notes.")
    parser.add_argument("--json", dest="json_path", help="JSON object or array to encode instead of the flags above. Use - for stdin.")
    parser.add_argument("--show-json", action="store_true", help="Also print the JSON payload to stderr.")
    args = parser.parse_args()

    field_given = any([args.id, args.title, args.date, args.time, args.start, args.end, args.duration, args.plan, args.note])
    if args.json_path and field_given:
        raise SystemExit("Use either --json or the field flags, not both.")
    if args.json_path:
        if args.json_path == "-":
            payload = json.load(sys.stdin)
        else:
            with open(args.json_path, encoding="utf-8") as handle:
                payload = json.load(handle)
        if not isinstance(payload, (dict, list)):
            raise SystemExit("JSON must be a session object or an array of sessions.")
    else:
        payload = build_entry(args)

    base = args.base.split("#", 1)[0]
    if args.show_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False), file=sys.stderr)
    print(f"{base}#add={encode(payload)}")


if __name__ == "__main__":
    main()
