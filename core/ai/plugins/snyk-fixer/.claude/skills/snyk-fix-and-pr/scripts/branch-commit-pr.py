#!/usr/bin/env python3
"""
Create a branch, commit Snyk fixes with the required message pattern, push, and open a PR.
Run from project root; --repo is the path to the sandbox repo (e.g. sandbox/renaissance).
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        sys.exit(result.returncode)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Branch, commit (SNYK-000: fix snyk issues - message), push, and create PR."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        required=True,
        help="Path to the repo (e.g. sandbox/renaissance)",
    )
    parser.add_argument(
        "--branch",
        type=str,
        required=True,
        help="Branch name (e.g. fix/snyk-issues-20250305)",
    )
    parser.add_argument(
        "--message",
        type=str,
        required=True,
        help="Short summary for the commit message after the prefix",
    )
    parser.add_argument(
        "--ticket",
        type=str,
        default="SNYK-000",
        help="Ticket ID prefix (default: SNYK-000)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands only, do not run",
    )
    parser.add_argument(
        "--no-pr",
        action="store_true",
        help="Push branch but do not run gh pr create",
    )
    args = parser.parse_args()

    repo = args.repo.resolve()
    if not repo.is_dir() or not (repo / ".git").exists():
        print(f"Not a git repo: {repo}", file=sys.stderr)
        return 1

    commit_msg = f"{args.ticket}: fix snyk issues - {args.message}"
    pr_title = f"{args.ticket}: fix snyk issues"
    pr_body = f"Automated Snyk remediation.\n\nSummary: {args.message}"

    steps = [
        (["git", "checkout", "-b", args.branch], "create branch"),
        (["git", "add", "-A"], "stage all"),
        (["git", "commit", "-m", commit_msg], "commit"),
        (["git", "push", "-u", "origin", args.branch], "push"),
    ]
    if not args.no_pr:
        steps.append(
            (["gh", "pr", "create", "--title", pr_title, "--body", pr_body], "create PR"),
        )

    for cmd, desc in steps:
        if args.dry_run:
            print(f"# {desc}\n  {' '.join(cmd)}")
            continue
        if cmd[0] == "git" and cmd[1] == "commit":
            status = run(["git", "status", "--porcelain"], cwd=repo, check=True)
            if not status.stdout.strip():
                print("No changes to commit; skipping commit/push/PR.", file=sys.stderr)
                return 0
        run(cmd, cwd=repo)

    return 0


if __name__ == "__main__":
    sys.exit(main())
