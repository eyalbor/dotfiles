#!/usr/bin/env python3
"""
Discover Node and Python projects under the sandbox directory.
Outputs JSON array of { path, type, manifest } for each project root.
"""
import argparse
import json
import sys
from pathlib import Path

# Manifest file -> project type
NODE_MANIFESTS = ["package.json"]
PYTHON_MANIFESTS = ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]


def discover_projects(sandbox: Path) -> list[dict]:
    """Find all project roots under sandbox. Each root is a dir containing a known manifest."""
    sandbox = sandbox.resolve()
    if not sandbox.is_dir():
        return []

    projects = []
    seen = set()  # (path, type) to avoid duplicates

    for repo_dir in sorted(sandbox.iterdir()):
        if not repo_dir.is_dir() or repo_dir.name.startswith("."):
            continue
        for path in repo_dir.rglob("*"):
            if not path.is_file():
                continue
            name = path.name
            root = path.parent
            key = (str(root), "node")
            if name in NODE_MANIFESTS and key not in seen:
                seen.add(key)
                projects.append({
                    "path": str(root),
                    "type": "node",
                    "manifest": name,
                })
            key = (str(root), "python")
            if name in PYTHON_MANIFESTS and key not in seen:
                seen.add(key)
                projects.append({
                    "path": str(root),
                    "type": "python",
                    "manifest": name,
                })

    return sorted(projects, key=lambda p: (p["path"], p["type"]))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover Node and Python projects in the sandbox."
    )
    parser.add_argument(
        "--sandbox",
        type=Path,
        default=Path("sandbox"),
        help="Sandbox directory (default: ./sandbox)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "paths"],
        default="json",
        help="Output format: json (default) or paths (one path per line)",
    )
    args = parser.parse_args()

    projects = discover_projects(args.sandbox)

    if args.format == "paths":
        for p in projects:
            print(p["path"])
        return 0

    print(json.dumps(projects, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
