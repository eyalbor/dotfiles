#!/usr/bin/env python3
"""
Run the verify command for a repo before creating a PR.
Reads verify_command from repos.config.yaml (global default or per-repo override).
Run from project root; --repo is the path to the sandbox repo (e.g. sandbox/renaissance).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_default_verify_command(text: str) -> str | None:
    """Get top-level verify_command from config text."""
    m = re.search(r"^verify_command:\s*(.+)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip().strip("'\"").strip()
    return None


def get_repo_verify_command(text: str, repo_name: str) -> str | None:
    """Get verify_command for a repo by name. Returns None if not set."""
    blocks = re.split(r"\n\s*-\s*name:\s*", text)
    for block in blocks[1:]:
        name_match = re.match(r"([^\n]+)", block)
        if not name_match:
            continue
        name = name_match.group(1).strip()
        if name != repo_name:
            continue
        vc = re.search(r"verify_command:\s*(.+)", block)
        if vc:
            return vc.group(1).strip().strip("'\"").strip()
        return None
    return None


def get_verify_command(config_path: Path, repo_name: str) -> str | None:
    """Return verify command for repo: per-repo override or global default."""
    text = config_path.read_text()
    cmd = get_repo_verify_command(text, repo_name)
    if cmd is not None:
        return cmd
    return get_default_verify_command(text)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run verify command for a repo (from repos.config.yaml) before creating PR."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("repos.config.yaml"),
        help="Path to repos config YAML",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        required=True,
        help="Path to the repo (e.g. sandbox/renaissance)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the verify command only, do not run",
    )
    args = parser.parse_args()

    config = args.config.resolve()
    if not config.is_file():
        print(f"Config not found: {config}", file=sys.stderr)
        return 1

    repo = args.repo.resolve()
    if not repo.is_dir():
        print(f"Repo directory not found: {repo}", file=sys.stderr)
        return 1

    repo_name = repo.name
    verify_cmd = get_verify_command(config, repo_name)
    if not verify_cmd:
        print(f"No verify_command for repo {repo_name}; skipping verify.", file=sys.stderr)
        return 0

    if args.dry_run:
        print(f"Would run in {repo}: {verify_cmd}")
        return 0

    result = subprocess.run(
        verify_cmd,
        cwd=repo,
        shell=True,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
