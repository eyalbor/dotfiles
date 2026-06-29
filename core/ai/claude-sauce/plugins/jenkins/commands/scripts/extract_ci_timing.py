#!/usr/bin/env python3
"""
Generic CI/Jenkins log timing extractor.

Usage:
    python3 extract_ci_timing.py <LOG_FILE_PATH>

Produces:
    <log_basename>_timing_breakdown.txt  — structured report
    <log_basename>_all_test_durations.csv — per-test CSV
"""
import csv
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Regex patterns (Jenkins/pytest)
# ---------------------------------------------------------------------------

TIMESTAMP_RE = re.compile(r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})')
BRACKET_TS_RE = re.compile(r'\[([^\]]+)\]')

SESSION_PASS_FAIL_RE = re.compile(
    r'(\d+)\s+(?:failed|passed).*?(\d+)\s+(?:passed|failed).*?in\s+([\d.]+)s(?:\s+\((\d+:\d+:\d+)\))?'
)
SESSION_PASS_ONLY_RE = re.compile(
    r'(\d+)\s+passed.*?in\s+([\d.]+)s(?:\s+\((\d+:\d+:\d+)\))?'
)
SESSION_FAIL_PASS_RE = re.compile(
    r'(\d+)\s+failed.*?(\d+)\s+passed.*?in\s+([\d.]+)s'
)

TEST_DURATION_RE = re.compile(r'\[([^\]]+)\]\s+([\d.]+)s\s+call\s+(.+)')

GROUP_START_RE = re.compile(
    r'\[([^\]]+)\].*?=== Running test:\s*(.+?)\s+in group:\s*(.+?)\s+on agent:\s*(.+?)(?:\s|$)'
)
GROUP_COMPLETE_RE = re.compile(
    r'\[([^\]]+)\].*?=== Group\s+(.+?)\s+completed on agent\s+(.+?)(?:\s|$)'
)

POLLING_RE = re.compile(r'Job result is still None', re.IGNORECASE)

NODE_RE = re.compile(r'Running on\s+(\S+)')
AGENT_POOL_RE = re.compile(r'Agent pool distribution', re.IGNORECASE)

TIMEOUT_RE = re.compile(r'Timeout set to expire in\s+(.+)', re.IGNORECASE)
OUTCOME_RE = re.compile(r'Finished:\s+(SUCCESS|FAILURE|ABORTED)', re.IGNORECASE)
EXCEEDED_RE = re.compile(r'Timeout has been exceeded', re.IGNORECASE)

WORKFLOW_PENDING_RE = re.compile(r'[Ww]orkflow.*?initiated|status.*?PENDING', re.IGNORECASE)

ERROR_RE = re.compile(r'FAILED|ERROR|Traceback|Exception', re.IGNORECASE)


def seconds_to_hms(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    return f"{h}:{m:02d}:{s:02d}"


def parse_ts(ts_str):
    """Try to parse a timestamp from a bracket-enclosed string."""
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ):
        try:
            return datetime.strptime(ts_str.strip(), fmt)
        except ValueError:
            continue
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_ci_timing.py <LOG_FILE_PATH>")
        sys.exit(1)

    log_path = Path(sys.argv[1])
    if not log_path.exists():
        print(f"File not found: {log_path}")
        sys.exit(1)

    print(f"Reading {log_path} ...")
    lines = log_path.read_text(encoding="utf-8", errors="replace").split("\n")
    total_lines = len(lines)
    print(f"  {total_lines:,} lines loaded")

    sessions = []
    tests = []
    group_starts = []
    group_completions = []
    nodes = set()
    polling_count = 0
    timeout_setting = None
    outcome = None
    timeout_exceeded = False
    first_ts = None
    last_ts = None
    workflow_pending_lines = []
    error_lines = []

    for i, line in enumerate(lines):
        ts_m = BRACKET_TS_RE.search(line)
        if ts_m:
            parsed = parse_ts(ts_m.group(1))
            if parsed:
                if first_ts is None:
                    first_ts = parsed
                last_ts = parsed

        m = SESSION_PASS_FAIL_RE.search(line)
        if m and "call" not in line:
            sessions.append({
                "line": i + 1,
                "raw": line[:120],
                "count1": int(m.group(1)),
                "count2": int(m.group(2)),
                "seconds": float(m.group(3)),
                "hms": m.group(4) or seconds_to_hms(float(m.group(3))),
                "has_fail": "failed" in line.lower()[:80],
            })

        m2 = SESSION_PASS_ONLY_RE.search(line)
        if m2 and "call" not in line and "failed" not in line.lower():
            sec = float(m2.group(2))
            if not any(abs(s["seconds"] - sec) < 0.1 for s in sessions[-5:]):
                sessions.append({
                    "line": i + 1,
                    "raw": line[:120],
                    "count1": int(m2.group(1)),
                    "count2": 0,
                    "seconds": sec,
                    "hms": m2.group(3) or seconds_to_hms(sec),
                    "has_fail": False,
                })

        m3 = SESSION_FAIL_PASS_RE.search(line)
        if m3 and "===" in line:
            sec = float(m3.group(3))
            if not any(abs(s["seconds"] - sec) < 0.1 for s in sessions[-5:]):
                sessions.append({
                    "line": i + 1,
                    "raw": line[:120],
                    "count1": int(m3.group(1)),
                    "count2": int(m3.group(2)),
                    "seconds": sec,
                    "hms": seconds_to_hms(sec),
                    "has_fail": True,
                })

        m = TEST_DURATION_RE.search(line)
        if m:
            tests.append({
                "ts": m.group(1),
                "seconds": float(m.group(2)),
                "test": m.group(3).strip(),
            })

        m = GROUP_START_RE.search(line)
        if m:
            group_starts.append({
                "ts": m.group(1),
                "test": m.group(2).strip(),
                "group": m.group(3).strip(),
                "agent": m.group(4).strip(),
            })

        m = GROUP_COMPLETE_RE.search(line)
        if m:
            group_completions.append({
                "ts": m.group(1),
                "group": m.group(2).strip(),
                "agent": m.group(3).strip(),
            })

        m = NODE_RE.search(line)
        if m:
            nodes.add(m.group(1))

        if POLLING_RE.search(line):
            polling_count += 1

        m = TIMEOUT_RE.search(line)
        if m and not timeout_setting:
            timeout_setting = m.group(1).strip()

        m = OUTCOME_RE.search(line)
        if m:
            outcome = m.group(1).upper()

        if EXCEEDED_RE.search(line):
            timeout_exceeded = True

        if WORKFLOW_PENDING_RE.search(line):
            workflow_pending_lines.append({"line": i + 1, "raw": line[:200]})

        if len(error_lines) < 200 and ERROR_RE.search(line):
            if "call" not in line and "PASSED" not in line:
                error_lines.append({"line": i + 1, "raw": line[:200]})

    # Deduplicate sessions
    seen = set()
    unique_sessions = []
    for s in sessions:
        key = (s["seconds"], s["line"])
        if key not in seen:
            seen.add(key)
            unique_sessions.append(s)

    # Group timeline per agent
    agent_groups = defaultdict(list)
    first_start_by_group = {}
    for gs in group_starts:
        if gs["group"] not in first_start_by_group:
            first_start_by_group[gs["group"]] = gs

    for gc in group_completions:
        start_info = first_start_by_group.get(gc["group"])
        agent_groups[gc["agent"]].append({
            "group": gc["group"],
            "start_ts": start_info["ts"] if start_info else "?",
            "end_ts": gc["ts"],
            "agent": gc["agent"],
        })

    # Build structured report
    out = []
    sep = "=" * 100

    out.append(sep)
    out.append("CI BUILD LOG — DETAILED TIMING ANALYSIS")
    out.append(sep)
    out.append("")
    out.append(f"  Log file:        {log_path.name}")
    out.append(f"  Total lines:     {total_lines:,}")
    out.append(f"  First timestamp: {first_ts}")
    out.append(f"  Last timestamp:  {last_ts}")
    if first_ts and last_ts:
        delta = last_ts - first_ts
        if delta.total_seconds() < 0:
            from datetime import timedelta
            delta += timedelta(days=1)
        out.append(f"  Wall-clock:      {delta} ({delta.total_seconds():.0f}s)")
    out.append(f"  Timeout setting: {timeout_setting or 'not found'}")
    out.append(f"  Outcome:         {outcome or 'not found'}")
    out.append(f"  Timeout exceeded:{timeout_exceeded}")
    out.append(f"  Agents/nodes:    {', '.join(sorted(nodes)) or 'not detected'}")
    out.append(f"  Polling waits:   {polling_count:,} occurrences")
    if polling_count > 0:
        out.append(f"  Est. poll time:  {seconds_to_hms(polling_count * 15)} (at 15s each)")
    out.append(f"  Workflow pending: {len(workflow_pending_lines)} occurrences")
    out.append("")

    out.append(sep)
    out.append("## 1. TEST SESSION SUMMARIES (pytest wall-clock per group)")
    out.append("-" * 80)
    total_session_seconds = 0
    for s in unique_sessions:
        if s["has_fail"]:
            label = f"{s['count1']} failed, {s['count2']} passed"
        else:
            label = f"{s['count1']} passed"
        out.append(f"  {label:30s} | {s['seconds']:>10.1f}s  ({s['hms']})")
        total_session_seconds += s["seconds"]
    out.append(f"\n  TOTAL test execution time: {total_session_seconds:,.1f}s ({seconds_to_hms(total_session_seconds)})")
    out.append(f"  (sum of pytest sessions — overlapping across parallel agents)")
    out.append("")

    out.append(sep)
    out.append("## 2. GROUP COMPLETION TIMELINE")
    out.append("-" * 80)
    for gc in group_completions:
        out.append(f"  [{gc['ts']}] {gc['group']:50s} on {gc['agent']}")
    out.append("")

    out.append(sep)
    out.append("## 3. PER-AGENT GROUP TIMELINE")
    out.append("-" * 80)
    for agent in sorted(agent_groups.keys()):
        out.append(f"\n  --- {agent} ({len(agent_groups[agent])} groups) ---")
        for g in agent_groups[agent]:
            out.append(f"    [{g['start_ts']}] -> [{g['end_ts']}]  {g['group']}")
    out.append("")

    out.append(sep)
    out.append("## 4. SLOWEST INDIVIDUAL TESTS (>60s)")
    out.append("-" * 80)
    by_suite = defaultdict(list)
    for t in tests:
        if t["seconds"] >= 60:
            parts = t["test"].split("/")
            suite = "/".join(parts[2:5]) if len(parts) > 5 else parts[-1].split("::")[0][:50]
            by_suite[suite].append(t)

    for suite in sorted(by_suite.keys(), key=lambda x: -max(t["seconds"] for t in by_suite[x])):
        out.append(f"\n  ### {suite}")
        for t in sorted(by_suite[suite], key=lambda x: -x["seconds"])[:15]:
            name = t["test"].split("::")[-1][:70]
            out.append(f"    {t['seconds']:>8.1f}s  {name}")
    out.append("")

    out.append(sep)
    out.append("## 5. ALL INDIVIDUAL TEST DURATIONS (slowest 200)")
    out.append("-" * 80)
    for t in sorted(tests, key=lambda x: -x["seconds"])[:200]:
        path = t["test"].split("::")[0]
        name = t["test"].split("::")[-1] if "::" in t["test"] else t["test"]
        out.append(f"  {t['seconds']:>8.1f}s  {path.split('/')[-1].replace('.py', '')[:35]:35s} :: {name[:75]}")
    out.append("")

    if polling_count > 10:
        out.append(sep)
        out.append("## 6. POLLING / STUCK WAIT ANALYSIS")
        out.append("-" * 80)
        out.append(f"  'Job result is still None' appeared {polling_count:,} times")
        out.append(f"  At 15s per poll: ~{seconds_to_hms(polling_count * 15)} of cumulative wait")
        out.append("  This is often the #1 reason for long builds — sync jobs that never return.")
        out.append("")

    if workflow_pending_lines:
        out.append(sep)
        out.append("## 7. WORKFLOW / APPROVAL PENDING EVENTS")
        out.append("-" * 80)
        for wf in workflow_pending_lines[:30]:
            out.append(f"  Line {wf['line']}: {wf['raw'][:150]}")
        out.append("")

    if error_lines:
        out.append(sep)
        out.append("## 8. ERROR / FAILURE SAMPLE (first 50)")
        out.append("-" * 80)
        for e in error_lines[:50]:
            out.append(f"  Line {e['line']}: {e['raw'][:150]}")
        out.append("")

    out.append(sep)
    out.append("## STATS SUMMARY")
    out.append("-" * 80)
    out.append(f"  Unique pytest sessions:  {len(unique_sessions)}")
    out.append(f"  Individual tests timed:  {len(tests)}")
    out.append(f"  Group completions:       {len(group_completions)}")
    out.append(f"  Agents/nodes detected:   {len(nodes)}")
    out.append(f"  Polling wait messages:   {polling_count:,}")
    out.append(f"  Workflow pending events:  {len(workflow_pending_lines)}")
    out.append(f"  Error/failure lines:      {len(error_lines)}")

    # Write outputs
    stem = log_path.stem.replace("#", "job")
    out_dir = log_path.parent

    report_path = out_dir / f"{stem}_timing_breakdown.txt"
    report_path.write_text("\n".join(out), encoding="utf-8")
    print(f"\nReport:  {report_path}")

    csv_path = out_dir / f"{stem}_all_test_durations.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seconds", "minutes", "test_path", "test_name"])
        for t in sorted(tests, key=lambda x: -x["seconds"]):
            path = t["test"].split("::")[0]
            name = t["test"].split("::")[-1] if "::" in t["test"] else t["test"]
            w.writerow([t["seconds"], round(t["seconds"] / 60, 1), path, name])
    print(f"CSV:     {csv_path} ({len(tests)} tests)")

    print(f"\nDone. {len(unique_sessions)} sessions, {len(tests)} tests, {len(group_completions)} group completions.")


if __name__ == "__main__":
    main()
