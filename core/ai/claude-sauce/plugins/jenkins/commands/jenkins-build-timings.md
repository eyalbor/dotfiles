---
description: Analyze a Jenkins console log file — extract test timings, map agent timelines, identify bottlenecks, and produce a root-cause report
---

# Jenkins Build Timings

Perform a multi-layered timing analysis of CI console log files. Produce structured reports, CSV exports, and a root-cause narrative. Follow every phase in order.

**Input required:** The user must provide the **path to the Jenkins console log file** (e.g. `/Users/name/Downloads/#194.txt`). If no path is given, ask for it.

## Phase 1: Initial Reconnaissance

Read the first ~500 lines and last ~100 lines of the log to establish:

1. **Build metadata**: job name, build number, trigger, branch, start timestamp
2. **Timeout setting**: look for `Timeout set to expire in`
3. **Final outcome**: `Finished: SUCCESS|FAILURE|ABORTED`, `Timeout has been exceeded`
4. **Overall wall-clock**: first timestamp to last timestamp

Report this immediately before deeper analysis.

## Phase 2: Structure Mapping

Search the log for pipeline structure markers:

| What | Grep pattern |
|------|-------------|
| Stage names | `\[Pipeline\] \{ \(` |
| Agent/node distribution | `Agent pool distribution` or `Running on` |
| Test group starts | `=== Running test:.*in group:.*on agent:` |
| Test group completions | `=== Group.*completed on agent` |
| Pytest session summaries | `\d+ passed.*in \d+\.\d+s` |
| Individual test durations | `\d+\.\d+s call\s+` |
| Slowest test headers | `slowest \d+ durations` |
| Polling/stuck patterns | `Job result is still None` or similar repeated wait messages |
| Errors and failures | `FAILED\|ERROR\|error:\|Exception\|Traceback` |

Build a **group-to-agent mapping** and **per-agent sequential timeline**.

## Phase 3: Timing Extraction

Run the extraction script:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/commands/scripts/extract_ci_timing.py" "<LOG_FILE_PATH>"
```

This produces two files next to the log:
- `<log_basename>_timing_breakdown.txt` — structured report
- `<log_basename>_all_test_durations.csv` — every individual test with seconds, minutes, path, name

Review the output and incorporate it into your analysis.

## Phase 4: Per-Agent Wall-Clock Timeline

For each agent, build a Gantt-style timeline:

```
─── AGENT <name> ──────────────────────────────────
     Start    End       Duration   Group (passed/failed)
     HH:MM    HH:MM     XhYYm     Group Name (Np/Mf)
      gap: ~N min (overhead)
     HH:MM    HH:MM     XhYYm     Next Group (Np/Mf)
     ──────────────────────────────────
     TOTAL RUN TIME: ~XhYYm
     FINISHED: HH:MM UTC
```

Calculate idle time per agent (time between agent finish and build end).

## Phase 5: Bottleneck Identification

Identify the **critical path** — the slowest agent that determined overall build time.

For each major time sink:
1. State the group name, agent, and wall-clock duration
2. List the top 5 slowest individual tests with durations
3. Identify the pattern: slow external API? polling loop? test reruns? failures?

For polling loops:
- Count occurrences of the repeated message
- Calculate total potential wait time (count * interval)
- Identify which test triggered the polling

## Phase 6: Root Cause Deep Dive

For the #1 bottleneck:
- Identify the specific test(s) running when the build timed out or spent the most time
- Look for external service calls, error responses, workflow triggers
- Check for patterns like pending approvals, 404 errors, authentication failures
- Trace the last meaningful activity timestamp before the polling started

## Phase 7: Report Assembly

Generate `<log_basename>_full_analysis.txt` with sections:

```
1. BUILD OVERVIEW
2. AGENT DISTRIBUTION
3. PER-AGENT GANTT TIMELINE
4. ROOT CAUSE
5. SECONDARY BOTTLENECKS
6. IDLE AGENT WASTE
7. SUMMARY: WHY X HOURS?
8. DEEP DIVE
9. RECOMMENDATIONS
```

Verify the math: phase durations + overhead must add up to total wall-clock.

## Phase 8: Deliver Results

Tell the user:
1. Root cause in 2-3 sentences
2. Where the generated files are saved
3. Key numbers (total time, bottleneck %, idle waste)
4. Actionable recommendations

## Adapting to Non-Jenkins Logs

- **GitHub Actions**: look for `##[group]`, step timestamps, job boundaries
- **GitLab CI**: look for `section_start`/`section_end` markers
- **Generic pytest**: look for `===` session lines, `slowest N durations`, PASSED/FAILED markers
- **Generic logs**: focus on timestamps, repeated patterns, gaps between activity
