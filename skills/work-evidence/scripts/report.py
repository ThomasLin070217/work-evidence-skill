#!/usr/bin/env python3
"""Validate a private work ledger and print a Markdown report. No network I/O."""

import argparse
from collections import defaultdict
from datetime import date, datetime
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


KINDS = ("recorded", "recalled", "estimated", "forecast")
KIND_NAMES = dict(zip(KINDS, ("记录", "本人回忆", "估算", "预计")))


class LedgerError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise LedgerError(message)


def text_field(obj, key):
    value = obj.get(key)
    require(isinstance(value, str) and bool(value.strip()), f"Missing text field: {key}")
    return value.strip()


def parse_date(value):
    require(isinstance(value, str), "Dates must be YYYY-MM-DD strings")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise LedgerError("Invalid YYYY-MM-DD date") from exc
    require(parsed.isoformat() == value, "Dates must use YYYY-MM-DD")
    return parsed


def parse_time(value, zone):
    require(isinstance(value, str), "Timed entries require ISO timestamps")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LedgerError("Invalid ISO timestamp") from exc
    require(parsed.utcoffset() is not None, "Timestamps require explicit timezone offsets")
    require(parsed.second == 0 and parsed.microsecond == 0, "Use whole-minute timestamps")
    require(parsed.utcoffset() == parsed.astimezone(zone).utcoffset(),
            "Timestamp offset does not agree with ledger timezone")
    return parsed


def safe_url(value):
    require(isinstance(value, str) and not any(c.isspace() for c in value), "Invalid evidence URL")
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
    except ValueError as exc:
        raise LedgerError("Invalid evidence URL") from exc
    require(parsed.scheme in ("https", "http") and bool(hostname),
            "Evidence URLs must be HTTP(S)")
    require(not parsed.username and not parsed.password, "Do not embed credentials in evidence URLs")
    return value


def week_number(day):
    first = day.replace(day=1)
    return (first.weekday() + day.day - 1) // 7 + 1


def validate(data):
    require(isinstance(data, dict), "Ledger must be a JSON object")
    first = parse_date(data.get("period_start"))
    last = parse_date(data.get("period_end"))
    cutoff = parse_date(data.get("as_of"))
    require(first <= last and (first.year, first.month) == (last.year, last.month),
            "Use one ledger per calendar month")
    require(first <= cutoff <= last, "Cutoff must be inside reporting period")
    try:
        zone = ZoneInfo(text_field(data, "timezone"))
    except ZoneInfoNotFoundError as exc:
        raise LedgerError("Unknown IANA timezone") from exc
    require(isinstance(data.get("tasks"), list) and data["tasks"], "Tasks must be a nonempty list")
    tasks = {}
    for task in data["tasks"]:
        require(isinstance(task, dict), "Each task must be an object")
        task_id = text_field(task, "id")
        require(task_id not in tasks, "Duplicate task ID")
        text_field(task, "title")
        text_field(task, "output")
        require(isinstance(task.get("evidence"), list), "Task evidence must be a list")
        for item in task["evidence"]:
            require(isinstance(item, dict), "Evidence must be an object")
            text_field(item, "label")
            safe_url(item.get("url"))
        tasks[task_id] = task
    require(isinstance(data.get("entries"), list) and data["entries"], "Entries must be a nonempty list")
    seen, entries, timed = set(), [], []
    daily_minutes = defaultdict(int)
    for item in data["entries"]:
        require(isinstance(item, dict), "Each entry must be an object")
        entry_id = text_field(item, "id")
        require(entry_id not in seen, "Duplicate entry ID; reconcile duplicate sources")
        seen.add(entry_id)
        task_id = text_field(item, "task_id")
        require(task_id in tasks, "Entry refers to an unknown task")
        kind = item.get("kind")
        require(kind in KINDS, "Unknown time kind")
        text_field(item, "basis")
        if "start" in item or "end" in item:
            require("date" not in item and "minutes" not in item, "Use either timed or untimed entry fields")
            start = parse_time(item.get("start"), zone)
            end = parse_time(item.get("end"), zone)
            require(end > start, "Timed duration must be positive")
            day = start.astimezone(zone).date()
            require(day == end.astimezone(zone).date(), "Split cross-midnight activity into daily entries")
            minutes = int((end - start).total_seconds() // 60)
            timed.append((start, end))
        else:
            day = parse_date(item.get("date"))
            minutes = item.get("minutes")
            require(type(minutes) is int and minutes > 0, "Minutes must be a positive integer")
        require(first <= day <= last, "Entry outside reporting period")
        require(day > cutoff if kind == "forecast" else day <= cutoff,
                "Forecast must be after cutoff; historical entries must not be after cutoff")
        daily_minutes[day] += minutes
        require(daily_minutes[day] <= 1440, "Daily personal work exceeds 24 hours; check double-counting")
        entries.append({"task_id": task_id, "date": day, "kind": kind, "minutes": minutes})
    timed.sort(key=lambda item: item[0])
    for previous, current in zip(timed, timed[1:]):
        require(current[0] >= previous[1], "Overlapping timed work; split or deduplicate it")
    return first, last, cutoff, tasks, entries


def duration(minutes):
    # Decimal hours are exact to two places when whole minutes are divisible by 3.
    if minutes % 3 == 0:
        return f"{minutes / 60:.2f}".rstrip("0").rstrip(".") + "h"
    hours, remaining = divmod(minutes, 60)
    return f"{hours}h{remaining:02d}m"


def md_text(value):
    value = " ".join(value.split())
    for char in ("\\", "|", "[", "]", "<", ">", "*", "_", "`"):
        value = value.replace(char, "\\" + char)
    return value


def render(data):
    first, last, cutoff, tasks, entries = validate(data)
    minutes_by_kind = {kind: 0 for kind in KINDS}
    by_task = defaultdict(list)
    for entry in entries:
        by_task[entry["task_id"]].append(entry)
        minutes_by_kind[entry["kind"]] += entry["minutes"]
    total = sum(minutes_by_kind.values())
    past = total - minutes_by_kind["forecast"]
    lines = [f"# {first:%Y年%m月}工作投入与产出简报", "",
             f"周期：{first.isoformat()}—{last.isoformat()}｜截至：{cutoff.isoformat()}", "",
             f"共{len(by_task)}项任务，投入合计 **{duration(total)}**；"
             f"历史投入{duration(past)}，预计投入{duration(minutes_by_kind['forecast'])}。", "",
             "口径：" + "、".join(f"{KIND_NAMES[k]}{duration(v)}" for k, v in minutes_by_kind.items() if v), "",
             "| 任务与产出／状态 | 开展周次 | 工时（含沟通交接） | 证据 |",
             "|---|---|---:|---|"]
    for task_id, task in tasks.items():
        if task_id not in by_task:
            continue
        items = by_task[task_id]
        weeks = "、".join(f"第{n}周" for n in sorted({week_number(x["date"]) for x in items}))
        links = []
        for evidence in task["evidence"]:
            url = evidence["url"].replace("(", "%28").replace(")", "%29").replace("|", "%7C")
            links.append(f"[{md_text(evidence['label'])}]({url})")
        forecast = sum(x["minutes"] for x in items if x["kind"] == "forecast")
        hours = duration(sum(x["minutes"] for x in items))
        if forecast:
            hours += f"（含预计{duration(forecast)}）"
        lines.append(f"| {md_text(task['title'])}：{md_text(task['output'])} | {weeks} | {hours} | "
                     + ("、".join(links) or "待补充") + " |")
    lines += ["", "周次按周一至周日划分，月初月末仅计当月部分。工时种类见上方口径，"
              "证据支持任务及产出，不自动认证估算时长；预计工作需在完成后核对。", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    try:
        with args.ledger.open(encoding="utf-8") as stream:
            data = json.load(stream)
        print(render(data), end="")
    except (LedgerError, OSError, ValueError) as exc:
        print(f"Ledger error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
