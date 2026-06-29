#!/usr/bin/env python3
"""
Clone non-disabled repos from repos.config.yaml into a sandbox directory.
Uses only stdlib (no PyYAML) by parsing the known YAML structure.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def parse_repos_config(path: Path) -> list[dict]:
    """Parse repos.config.yaml; return list of {name, repository, disabled}."""
    text = path.read_text()
    repos = []
    block = re.compile(
        r"-\s*name:\s*([^\n]+)\s+repository:\s*([^\n]+)(?:\s+disabled:\s*(true|false))?",
        re.MULTILINE,
    )
    for m in block.finditer(text):
        name = m.group(1).strip()
        repository = m.group(2).strip()
        disabled_str = (m.group(3) or "false").strip().lower()
        disabled = disabled_str == "true"
        repos.append({"name": name, "repository": repository, "disabled": disabled})
    return repos


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clone non-disabled repos from repos.config.yaml into a sandbox."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("repos.config.yaml"),
        help="Path to repos config YAML (default: repos.config.yaml in cwd)",
    )
    parser.add_argument(
        "--sandbox",
        type=Path,
        default=Path("sandbox"),
        help="Sandbox directory for clones (default: ./sandbox)",
    )
    parser.add_argument(
        "--pull",
        action="store_true",
        help="Run git pull in existing clones to update",
    )
    parser.add_argument(
        "--shallow",
        action="store_true",
        help="Clone with --depth 1 (only for new clones)",
    )
    args = parser.parse_args()

    config = args.config.resolve()
    if not config.is_file():
        print(f"Config not found: {config}", file=sys.stderr)
        return 1

    sandbox = args.sandbox.resolve()
    repos = parse_repos_config(config)
    to_clone = [r for r in repos if not r["disabled"]]

    if not to_clone:
        print("No non-disabled repositories in config.")
        return 0

    print(f"Sandbox: {sandbox}")
    print(f"Cloning/updating {len(to_clone)} repo(s)...")

    ok = 0
    for r in to_clone:
        repo_dir = sandbox / r["name"]
        if repo_dir.exists():
            if (repo_dir / ".git").exists():
                if args.pull:
                    ret = subprocess.run(
                        ["git", "pull"],
                        cwd=repo_dir,
                        capture_output=True,
                        text=True,
                    )
                    if ret.returncode == 0:
                        print(f"  Updated: {repo_dir.name}")
                        ok += 1
                    else:
                        print(f"  git pull failed: {repo_dir.name}", file=sys.stderr)
                else:
                    print(f"  Exists (skip): {repo_dir.name}")
                    ok += 1
            else:
                print(f"  Skipping (not a git repo): {repo_dir.name}", file=sys.stderr)
        else:
            sandbox.mkdir(parents=True, exist_ok=True)
            cmd = (
                ["git", "clone"]
                + (["--depth", "1"] if args.shallow else [])
                + [r["repository"], str(repo_dir)]
            )
            ret = subprocess.run(cmd, capture_output=True, text=True)
            if ret.returncode == 0:
                print(f"  Cloned: {repo_dir.name}")
                ok += 1
            else:
                print(f"  Clone failed {repo_dir.name}: {ret.stderr}", file=sys.stderr)

    print(f"Done. {ok}/{len(to_clone)} repo(s) ready.")
    return 0 if ok == len(to_clone) else 1


if __name__ == "__main__":
    sys.exit(main())
