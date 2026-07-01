#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

FRONTMATTER_DELIMITER = '---'
SKILL_FILENAME = 'SKILL.md'
PLUGINS_DIR_NAME = 'plugins'
SKILLS_DIR_NAME = 'skills'
CURSOR_SKILLS_DIR = '.cursor/skills'
SKILLS_NAMESPACE = '<ORG>'
COMMANDS_DIR_NAME = 'commands'
CURSOR_COMMANDS_DIR = '.cursor/commands'
SCRIPTS_DIR_NAME = 'scripts'
REFERENCES_DIR_NAME = 'references'
ASSETS_DIR_NAME = 'assets'
DEFAULT_REPO_URL = 'git@<GITHUB_HOST>:<ORG>/claude-sauce.git'


def find_skill_files(repo_root: Path) -> List[Tuple[Path, str]]:
    found_skills = []
    plugins_dir = repo_root / PLUGINS_DIR_NAME

    if not plugins_dir.exists():
        return found_skills

    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue

        skills_dir = plugin_dir / SKILLS_DIR_NAME
        if not skills_dir.exists():
            continue

        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_file = skill_dir / SKILL_FILENAME
            if skill_file.exists():
                skill_name = skill_dir.name
                found_skills.append((skill_file, skill_name))

    return found_skills


def find_command_files(repo_root: Path) -> List[Tuple[Path, str]]:
    found_commands = []
    plugins_dir = repo_root / PLUGINS_DIR_NAME

    if not plugins_dir.exists():
        return found_commands

    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue

        commands_dir = plugin_dir / COMMANDS_DIR_NAME
        if not commands_dir.exists():
            continue

        for cmd_file in commands_dir.glob('*.md'):
            if cmd_file.name == 'README.md':
                continue

            cmd_name = cmd_file.stem
            found_commands.append((cmd_file, cmd_name))

    return found_commands


def parse_frontmatter(content: str) -> Tuple[dict, str]:
    if not content.startswith(FRONTMATTER_DELIMITER):
        return {}, content

    parts = content.split(FRONTMATTER_DELIMITER, 2)
    if len(parts) < 3:
        return {}, content

    yaml_content = parts[1].strip()
    body = parts[2].lstrip('\n')

    if HAS_YAML:
        try:
            frontmatter = yaml.safe_load(yaml_content)
            return frontmatter or {}, body
        except yaml.YAMLError:
            return {}, content

    frontmatter = {}
    lines = yaml_content.split('\n')
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index].strip()
        if ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if value.startswith('|'):
                value_lines = []
                line_index += 1
                while line_index < len(lines) and lines[line_index].startswith(' '):
                    value_lines.append(lines[line_index].strip())
                    line_index += 1
                value = '\n'.join(value_lines)
                line_index -= 1
            else:
                value = value.strip('"').strip("'")

            frontmatter[key] = value
        line_index += 1
    return frontmatter, body


def normalize_description(description: str) -> str:
    normalized = description.strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    normalized = normalized.replace('\n', ' ').replace('  ', ' ').strip()
    return normalized


def get_skill_info(skill_file: Path) -> Tuple[str, str]:
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter, _ = parse_frontmatter(content)
    skill_name = frontmatter.get('name', skill_file.parent.name)
    description = frontmatter.get('description', 'No description available')

    if isinstance(description, str):
        description = normalize_description(description)
        if len(description) > 100:
            description = description[:97] + '...'

    return skill_name, description


def get_command_info(cmd_file: Path) -> Tuple[str, str]:
    with open(cmd_file, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter, _ = parse_frontmatter(content)
    cmd_name = frontmatter.get('name', cmd_file.stem)
    description = frontmatter.get('description', 'No description available')

    if isinstance(description, str):
        description = normalize_description(description)
        if len(description) > 100:
            description = description[:97] + '...'

    return cmd_name, description


def parse_selection_input(user_input: str, max_number: int) -> Optional[List[int]]:
    if not user_input.strip():
        return []

    selected = set()
    parts = re.split(r'[,\s]+', user_input.strip())

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if '-' in part:
            try:
                start, end = part.split('-', 1)
                start_num = int(start.strip())
                end_num = int(end.strip())
                if start_num < 1 or end_num > max_number or start_num > end_num:
                    return None
                selected.update(range(start_num, end_num + 1))
            except ValueError:
                return None
        else:
            try:
                num = int(part)
                if num < 1 or num > max_number:
                    return None
                selected.add(num)
            except ValueError:
                return None

    return sorted(list(selected))


def interactive_skill_selection(skills: List[Tuple[Path, str]]) -> List[Tuple[Path, str]]:
    if not skills:
        return []

    print(f"\nFound {len(skills)} skill(s) available:\n")

    for idx, (skill_file, _) in enumerate(skills, 1):
        display_name, description = get_skill_info(skill_file)
        print(f"{idx}. {display_name}")
        print(f"   {description}\n")

    while True:
        user_input = input('Enter skill numbers to install (comma/space separated, or ranges like 1-3): ').strip()

        if not user_input:
            print('No skills selected. Exiting.')
            return []

        selected_indices = parse_selection_input(user_input, len(skills))

        if selected_indices is None:
            print(f"Invalid input. Please enter numbers between 1 and {len(skills)}.")
            continue

        if not selected_indices:
            print('No valid skills selected. Exiting.')
            return []

        selected_skills = [skills[idx - 1] for idx in selected_indices]
        return selected_skills


def interactive_command_selection(commands: List[Tuple[Path, str]]) -> List[Tuple[Path, str]]:
    if not commands:
        return []

    print(f"\nFound {len(commands)} command(s) available:\n")

    for idx, (cmd_file, _) in enumerate(commands, 1):
        display_name, description = get_command_info(cmd_file)
        print(f"{idx}. {display_name}")
        print(f"   {description}\n")

    while True:
        user_input = input('Enter command numbers to install (comma/space separated, or ranges like 1-3): ').strip()

        if not user_input:
            print('No commands selected. Exiting.')
            return []

        selected_indices = parse_selection_input(user_input, len(commands))

        if selected_indices is None:
            print(f"Invalid input. Please enter numbers between 1 and {len(commands)}.")
            continue

        if not selected_indices:
            print('No valid commands selected. Exiting.')
            return []

        selected_commands = [commands[idx - 1] for idx in selected_indices]
        return selected_commands


def remove_existing_target(target_path: Path) -> None:
    if target_path.exists():
        if target_path.is_symlink() or target_path.is_file():
            target_path.unlink()
        else:
            shutil.rmtree(target_path)


def copy_directory(source_path: Path, target_path: Path, resource_name: str) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    remove_existing_target(target_path)
    shutil.copytree(source_path, target_path)
    print(f"Copied {resource_name}: {source_path} -> {target_path}")


def copy_skill_directory(skill_dir: Path, target_dir: Path, skill_name: str, dry_run: bool = False) -> None:
    if dry_run:
        print(f"[DRY RUN] Would copy skill directory: {skill_dir} -> {target_dir}")
        return

    target_dir.mkdir(parents=True, exist_ok=True)

    skill_file = skill_dir / SKILL_FILENAME
    if skill_file.exists():
        target_skill_file = target_dir / SKILL_FILENAME
        shutil.copy2(skill_file, target_skill_file)
        print(f"Copied SKILL.md: {skill_file} -> {target_skill_file}")

    for resource_dir_name in [SCRIPTS_DIR_NAME, REFERENCES_DIR_NAME, ASSETS_DIR_NAME]:
        resource_source = skill_dir / resource_dir_name
        if resource_source.exists() and resource_source.is_dir():
            resource_target = target_dir / resource_dir_name
            copy_directory(resource_source, resource_target, resource_dir_name)


def validate_git_url(git_url: str) -> None:
    ALLOWED_HOST = '<GITHUB_HOST>'

    if not git_url or not isinstance(git_url, str):
        raise ValueError('Invalid git_url provided')

    if not git_url.startswith(('git@', 'https://', 'http://')):
        raise ValueError(f"Security restriction: Only {ALLOWED_HOST} URLs are allowed. "
                         f"URL must start with git@, https://, or http://. "
                         f"Expected formats: git@{ALLOWED_HOST}:owner/repo.git or "
                         f"https://{ALLOWED_HOST}/owner/repo.git")

    if git_url.startswith('git@'):
        if ':' not in git_url:
            raise ValueError(f"Security restriction: Invalid git@ URL format. "
                             f"Expected: git@{ALLOWED_HOST}:owner/repo.git")

        parts = git_url.split(':', 1)
        if len(parts) != 2:
            raise ValueError(f"Security restriction: Invalid git@ URL format. "
                             f"Expected: git@{ALLOWED_HOST}:owner/repo.git")

        user_host = parts[0]
        repo_path = parts[1]

        if not user_host.startswith('git@'):
            raise ValueError(f"Security restriction: Invalid git@ URL format. "
                             f"Expected: git@{ALLOWED_HOST}:owner/repo.git")

        if '@' in user_host[4:]:
            raise ValueError(f"Security restriction: Multiple @ symbols not allowed. "
                             f"Expected: git@{ALLOWED_HOST}:owner/repo.git")

        host = user_host[4:]
        if host != ALLOWED_HOST:
            raise ValueError(f"Security restriction: Only {ALLOWED_HOST} URLs are allowed. "
                             f"Provided URL uses domain: {host}. "
                             f"Expected: git@{ALLOWED_HOST}:owner/repo.git")

        if not re.match(r'^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(?:\.git)?$', repo_path):
            raise ValueError(f"Security restriction: Invalid repository path format. "
                             f"Expected: git@{ALLOWED_HOST}:owner/repo.git")

    elif git_url.startswith(('https://', 'http://')):
        parsed = urlparse(git_url)
        if not parsed.netloc:
            raise ValueError(f"Security restriction: Invalid URL format. "
                             f"Expected: https://{ALLOWED_HOST}/owner/repo.git")

        host = parsed.netloc.split(':')[0]
        if host != ALLOWED_HOST:
            raise ValueError(f"Security restriction: Only {ALLOWED_HOST} URLs are allowed. "
                             f"Provided URL uses domain: {host}. "
                             f"Expected: https://{ALLOWED_HOST}/owner/repo.git")

        if not parsed.path or parsed.path == '/':
            raise ValueError(f"Security restriction: Repository path is required. "
                             f"Expected: https://{ALLOWED_HOST}/owner/repo.git")

        path_match = re.match(r'^/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(?:\.git)?/?$', parsed.path)
        if not path_match:
            raise ValueError(f"Security restriction: Invalid repository path format. "
                             f"Expected: https://{ALLOWED_HOST}/owner/repo.git")


def clone_repository(git_url: str, target_dir: Path) -> Path:
    validate_git_url(git_url)

    print(f"Cloning repository: {git_url}")
    git_command = ['git', 'clone', git_url, str(target_dir)]
    try:
        subprocess.run(  # nosec B603
            git_command, check=True, capture_output=True, text=True, shell=False)
        return target_dir
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else e.stdout if e.stdout else 'Unknown error'
        print(f"Error cloning repository: {error_msg}")
        raise
    except FileNotFoundError:
        print('Error: git command not found. Please install git.')
        raise


def sync_skill(skill_file: Path, skill_name: str, repo_root: Path, target_project_root: Path, dry_run: bool = False,
               force: bool = False) -> None:
    skill_dir = skill_file.parent
    target_dir = target_project_root / CURSOR_SKILLS_DIR / SKILLS_NAMESPACE / skill_name

    if target_dir.exists() and not force and not dry_run:
        print(f"Skipping {skill_name}: skill already exists (use --force to overwrite)")
        return

    print(f"\nInstalling skill: {skill_name}")
    print(f"  Source: {skill_dir}")
    print(f"  Target: {target_dir}")

    if target_dir.exists() and force and not dry_run:
        remove_existing_target(target_dir)

    copy_skill_directory(skill_dir, target_dir, skill_name, dry_run)


def sync_command(cmd_file: Path, cmd_name: str, repo_root: Path, target_project_root: Path, dry_run: bool = False,
                 force: bool = False) -> None:
    cmd_dir = cmd_file.parent
    target_file = target_project_root / CURSOR_COMMANDS_DIR / cmd_file.name

    if target_file.exists() and not force and not dry_run:
        print(f"Skipping {cmd_name}: command already exists (use --force to overwrite)")
        return

    print(f"\nInstalling command: {cmd_name}")
    print(f"  Source: {cmd_file}")
    print(f"  Target: {target_file}")

    if dry_run:
        print(f"[DRY RUN] Would copy command file: {cmd_file} -> {target_file}")
        scripts_dir = cmd_dir / SCRIPTS_DIR_NAME
        if scripts_dir.exists() and scripts_dir.is_dir():
            target_scripts_dir = target_project_root / CURSOR_COMMANDS_DIR / SCRIPTS_DIR_NAME / cmd_name
            print(f"[DRY RUN] Would copy scripts directory: {scripts_dir} -> {target_scripts_dir}")
        return

    if target_file.exists() and force:
        target_file.unlink()

    target_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cmd_file, target_file)
    print(f"Copied command file: {cmd_file} -> {target_file}")

    scripts_dir = cmd_dir / SCRIPTS_DIR_NAME
    if scripts_dir.exists() and scripts_dir.is_dir():
        target_scripts_dir = target_project_root / CURSOR_COMMANDS_DIR / SCRIPTS_DIR_NAME / cmd_name
        if target_scripts_dir.exists() and force:
            remove_existing_target(target_scripts_dir)
        copy_directory(scripts_dir, target_scripts_dir, f"scripts for {cmd_name}")


def main():
    parser = argparse.ArgumentParser(description='Interactive installer for Claude skills and commands to Cursor')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without making them')
    parser.add_argument('--all', action='store_true', help='Install all available items without prompting')
    parser.add_argument('--force', action='store_true', help='Auto-overwrite existing items without prompting')
    parser.add_argument('--skills', action='store_true', help='Sync skills (default: True unless --commands is used without --skills)')
    parser.add_argument('--commands', action='store_true', help='Sync commands')
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(), help='Repository root directory (default: current directory)')
    parser.add_argument('--git-url', type=str, default=None,
                        help='Git repository URL to clone (defaults to internal repo if not found locally)')

    args = parser.parse_args()

    sync_skills = args.skills or not args.commands
    sync_commands = args.commands

    if not sync_skills and not sync_commands:
        print('Error: Must specify at least one of --skills or --commands')
        sys.exit(1)

    repo_root = args.repo_root.resolve()
    cleanup_temp_dir = None

    try:
        if not (repo_root / PLUGINS_DIR_NAME).exists():
            git_url = args.git_url or DEFAULT_REPO_URL
            temp_dir = tempfile.mkdtemp(prefix='claude-sauce-')
            cleanup_temp_dir = Path(temp_dir)

            try:
                clone_repository(git_url, cleanup_temp_dir)
                repo_root = cleanup_temp_dir.resolve()
            except Exception as e:
                print(f"Failed to clone repository: {e}")
                if cleanup_temp_dir.exists():
                    shutil.rmtree(cleanup_temp_dir, ignore_errors=True)
                sys.exit(1)

        if not (repo_root / PLUGINS_DIR_NAME).exists():
            print(f"Error: plugins directory not found in {repo_root}")
            sys.exit(1)

        target_project_root = Path.cwd()

        if sync_skills:
            skills = find_skill_files(repo_root)
            selected_skills = []

            if not skills:
                print('No skills found in plugins directory')
            else:
                if args.all:
                    selected_skills = skills
                    print(f"Installing all {len(selected_skills)} skill(s)...")
                else:
                    selected_skills = interactive_skill_selection(skills)
                    if not selected_skills:
                        print('No skills selected.')
                    else:
                        print(f"\nInstalling {len(selected_skills)} selected skill(s)...")

                if selected_skills and not args.dry_run:
                    namespace_dir = target_project_root / CURSOR_SKILLS_DIR / SKILLS_NAMESPACE
                    if namespace_dir.exists() and any(namespace_dir.iterdir()):
                        existing_items = list(namespace_dir.iterdir())
                        print(f"\nWarning: {SKILLS_NAMESPACE} directory contains {len(existing_items)} existing item(s):")
                        for item in existing_items:
                            print(f"  - {item.name}")

                        if args.force:
                            print(f"\nCleaning existing {SKILLS_NAMESPACE} directory (--force enabled)...")
                            for item in existing_items:
                                remove_existing_target(item)
                        else:
                            response = input(f"\nDelete all existing items in {SKILLS_NAMESPACE} directory? [y/N]: ").strip().lower()
                            if response == 'y':
                                print(f"Cleaning existing {SKILLS_NAMESPACE} directory...")
                                for item in existing_items:
                                    remove_existing_target(item)
                                args.force = True
                            else:
                                print('Skipping cleanup. Existing items will be skipped.')

                for skill_file, skill_name in selected_skills:
                    sync_skill(skill_file, skill_name, repo_root, target_project_root, args.dry_run, args.force)

        if sync_commands:
            commands = find_command_files(repo_root)
            selected_commands = []

            if not commands:
                print('No commands found in plugins directory')
            else:
                if args.all:
                    selected_commands = commands
                    print(f"Installing all {len(selected_commands)} command(s)...")
                else:
                    selected_commands = interactive_command_selection(commands)
                    if not selected_commands:
                        print('No commands selected.')
                    else:
                        print(f"\nInstalling {len(selected_commands)} selected command(s)...")

                for cmd_file, cmd_name in selected_commands:
                    sync_command(cmd_file, cmd_name, repo_root, target_project_root, args.dry_run, args.force)

        print(f"\nInstallation complete!")

    finally:
        if cleanup_temp_dir and cleanup_temp_dir.exists():
            try:
                shutil.rmtree(cleanup_temp_dir, ignore_errors=True)
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temporary directory: {cleanup_error}")


if __name__ == '__main__':
    main()
