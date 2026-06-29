# Jenkins Plugin

Fetch and analyze Jenkins build console logs to identify root causes of CI/CD failures, sorted by severity.

## Overview

This plugin provides a skill and a command for analyzing Jenkins console output:
- **jenkins-console-analyzer** (skill, job URL): Fetch console from Jenkins, identify test failures and infrastructure issues, prioritize by severity, determine root cause
- **jenkins-build-timings** (command): Analyze timing data from a local log file — per-test durations, agent timelines, bottlenecks, root-cause report; invoke via `/jenkins-build-timings`

## Prerequisites

- Python 3.7+
- Network access to Jenkins instance

## Authentication/Setup

Credentials are stored in `~/.claude-sauce.json`:

```json
{
  "jenkins": {
    "USER": "your-jenkins-username",
    "TOKEN": "your-jenkins-api-token",
    "COOKIE": "your-jsessionid.2b634e4d-value-here"
  }
}
```

Use either `TOKEN` or `COOKIE` (JSESSIONID value). Auth priority: `--cookie` > `--token` > config `COOKIE` > config `TOKEN`.

### Automated Credential Setup

The first time you use the Jenkins analyzer, Claude will automatically guide you through credential setup:

1. Claude detects missing credentials and offers to help
2. Guides you to generate a Jenkins API token:
   - Log into your Jenkins instance
   - Click your name (top right) → Configure
   - Under "API Token", click "Add new Token"
   - Generate and copy the token
3. Collects your username and API token securely via masked input
4. Saves credentials to `~/.claude-sauce.json` automatically
5. Retries your analysis

No manual file editing required!

### Cookie Authentication (JSESSIONID)

For Jenkins instances with SSO authentication, API tokens may not work. Use your browser session cookie instead.

**How to get the JSESSIONID:**

1. Open your browser and log in to your Jenkins instance
2. Open Developer Tools (`F12` or `Cmd+Option+I` on Mac)
3. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox)
4. In the left sidebar, expand **Cookies** and select the Jenkins URL
5. Find the cookie named `JSESSIONID.2b634e4d` and copy its **Value** (e.g. `node01b9jyhtlt56hblghqc2kyitas127027.node0`)
6. Paste the value (not the full `key=value`) into `~/.claude-sauce.json` under the `COOKIE` key

**Note:** The cookie key suffix (`.2b634e4d`) is fixed per Jenkins instance — only the value changes when your session expires. Update the `COOKIE` value in `~/.claude-sauce.json` when it expires.

### Manual Setup

If you prefer to set up credentials manually:

1. Generate a Jenkins API token:
   - Jenkins → Your Profile → Configure → API Token → Add new Token
2. Or get your JSESSIONID.2b634e4d from browser DevTools as described above
3. Create or edit `~/.claude-sauce.json` with the structure shown above
4. Set appropriate file permissions: `chmod 600 ~/.claude-sauce.json`

## Skills

### jenkins-console-analyzer

Automatically triggered when you provide a Jenkins job URL or ask to debug a build failure.

**Capabilities:**
- Fetches console text from Jenkins jobs
- Analyzes output for errors, warnings, and failures
- Groups issues by type (test failures, infrastructure, build errors, etc.)
- Sorts by severity (critical → high → medium → low)
- Identifies root cause and distinguishes code vs infrastructure issues
- Provides actionable next steps

**Example triggers:**
```
"Analyze this Jenkins build: https://jenkins.example.com/job/my-job/123/"
"Debug this failed CI run: <jenkins-url>"
"What went wrong in this Jenkins build?"
```

For detailed skill documentation, see [skills/jenkins-console-analyzer/SKILL.md](skills/jenkins-console-analyzer/SKILL.md).

## Commands

### jenkins-build-timings

Invoke via `/jenkins-build-timings` to analyze **local** Jenkins console log files (path on disk). Diagnoses long-running or stuck builds.

**Capabilities:**
- Extract per-test timing and rank the slowest tests
- Map which test groups ran on which agents (Gantt-style timeline)
- Identify the critical path and bottlenecks (polling loops, stuck jobs, idle agents)
- Produce a root-cause report with actionable recommendations
- Export a CSV of every test duration

**Usage:** Run `/jenkins-build-timings`, then provide the log file path when prompted.

For full command documentation, see [commands/jenkins-build-timings.md](commands/jenkins-build-timings.md).

## Usage Patterns

### Analyzing a Failed Build

```
1. Copy the Jenkins job URL from your browser
2. Paste it in Claude with a request like:
   "Analyze this build failure: https://jenkins.example.com/job/my-job/123/"
3. Claude fetches console output and provides root cause analysis
```

### Analyzing Recent Failures

```
"Check the last 500 lines of this build: <jenkins-url>"
(Uses --tail 500 for faster analysis of recent output)
```

### Re-analyzing After Changes

```
"Re-analyze this build with fresh data: <jenkins-url>"
(Uses --force to bypass cache and fetch latest console output)
```

## Analysis Output

The analyzer provides:

**Job Summary:**
- Build status (SUCCESS/FAILURE/UNSTABLE/etc.)
- Build number and duration
- Timestamp

**Issues by Severity:**
- **Critical**: Blocking issues requiring immediate attention
- **High**: Important failures that prevent success
- **Medium**: Issues that should be addressed
- **Low**: Minor warnings or informational items

**Issue Categories:**
- Test failures (with test names and failure messages)
- Infrastructure problems (network, service availability)
- Build errors (compilation, dependency issues)
- Deployment issues (environment, configuration)
- Security problems (vulnerability scanning failures)

**Root Cause Summary:**
- Most likely cause of failure
- Whether it's a code issue or infrastructure/environment issue
- Actionable next steps for resolution

## Troubleshooting

### Authentication Failures

**Symptoms**: 401 Unauthorized or "Authentication required" errors

**Solutions**:
1. Verify your username is correct in `~/.claude-sauce.json`
2. Regenerate Jenkins API token (old token may have expired)
3. Update `~/.claude-sauce.json` with new token
4. For SSO instances, use `COOKIE` in `~/.claude-sauce.json` instead of `TOKEN` (see Cookie Authentication section)

### Connection Issues

**Symptoms**: Timeout or connection refused errors

**Solutions**:
1. Verify Jenkins URL is accessible from your machine
2. Check VPN connection if Jenkins is internal
3. Use `--no-verify-ssl` flag for self-signed certificates
4. Verify firewall settings allow access to Jenkins

### Missing Console Output

**Symptoms**: "No console text found" or empty analysis

**Solutions**:
1. Verify the build has completed (may not have console output if still running)
2. Check build number is correct in URL
3. Ensure you have permission to access the job
4. Try `--force` flag to bypass cache

### Large Console Logs

**Symptoms**: Analysis takes too long or times out

**Solutions**:
1. Use `--tail N` to analyze only last N lines (e.g., `--tail 1000`)
2. Focus on the end of logs where errors typically appear
3. For very large logs, consider analyzing in chunks

### SSL Certificate Errors

**Symptoms**: SSL verification failed errors

**Solutions**:
1. Use `--no-verify-ssl` flag for self-signed certificates
2. Verify Jenkins URL is correct (http vs https)
3. Check certificate validity with Jenkins administrator

## Plugin Details

**Name**: jenkins
**Version**: 1.0.0
**Author**: <AUTHOR_NAME>

---

**Quick Start**: Paste any Jenkins job URL and ask Claude to analyze it!
