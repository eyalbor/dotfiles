#!/usr/bin/env python3

import argparse
import json
import os
import re
import shutil
import ssl
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class Colors:
    RED = '\033[0;31m' if sys.stdout.isatty() else ''
    GREEN = '\033[0;32m' if sys.stdout.isatty() else ''
    YELLOW = '\033[1;33m' if sys.stdout.isatty() else ''
    CYAN = '\033[0;36m' if sys.stdout.isatty() else ''
    NC = '\033[0m' if sys.stdout.isatty() else ''


class GitHubAPIError(Exception):
    pass


class GitHubAPIClient:

    def __init__(self, hostname: Optional[str] = None):
        self.hostname = hostname or 'github.com'
        self.base_url = f"https://api.{self.hostname}" if self.hostname != 'github.com' else 'https://api.github.com'
        self.token = self._get_token()
        if not self.token:
            raise ValueError("GitHub token not found. Add 'TOKEN' to ~/.claude-sauce.json under 'github' section")

    def _get_token(self) -> Optional[str]:
        # Read from .claude-sauce.json (only source)
        claude_sauce_path = Path.home() / '.claude-sauce.json'
        if claude_sauce_path.exists():
            try:
                with open(claude_sauce_path) as f:
                    config = json.load(f)
                    github_config = config.get('github', {})
                    token = github_config.get('TOKEN')
                    if token:
                        return token
            except Exception as e:
                log_warn(f"Failed to read GitHub token from {claude_sauce_path}: {e}")

        return None

    def api_request(self, endpoint: str, method: str = 'GET') -> Dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'codacy-integration-script'}
        if self.token:
            headers['Authorization'] = f'token {self.token}'

        request = Request(url, headers=headers, method=method)
        context = ssl.create_default_context()

        try:
            with urlopen(request, context=context) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            error_body = e.read().decode()
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('message', error_body)
            except json.JSONDecodeError:
                error_msg = error_body
            raise GitHubAPIError(f"GitHub API error {e.code}: {error_msg}")
        except URLError as e:
            raise GitHubAPIError(f"Connection error: {e.reason}")

    def get_pr_by_branch(self, org: str, repo: str, branch: str) -> Optional[int]:
        endpoint = f"repos/{org}/{repo}/pulls?head={org}:{branch}&state=open"
        try:
            prs = self.api_request(endpoint)
            if prs and len(prs) > 0:
                return prs[0].get('number')
        except GitHubAPIError:
            pass
        return None

    def get_pr_commit_sha(self, org: str, repo: str, pr_num: int) -> Optional[str]:
        endpoint = f"repos/{org}/{repo}/pulls/{pr_num}"
        try:
            pr_data = self.api_request(endpoint)
            return pr_data.get('head', {}).get('sha')
        except Exception:
            return None

    def get_pr_status_checks(self, org: str, repo: str, commit_sha: str) -> List[Dict]:
        endpoint = f"repos/{org}/{repo}/commits/{commit_sha}/check-runs"
        try:
            data = self.api_request(endpoint)
            if 'check_runs' in data:
                return data.get('check_runs', [])
            return []
        except Exception:
            return []

    def get_pr_status_check_rollup(self, org: str, repo: str, pr_num: int) -> List[Dict]:
        endpoint = f"repos/{org}/{repo}/pulls/{pr_num}"
        try:
            pr_data = self.api_request(endpoint)
            commit_sha = pr_data.get('head', {}).get('sha')
            if commit_sha:
                return self.get_pr_status_checks(org, repo, commit_sha)

            endpoint_rollup = f"repos/{org}/{repo}/pulls/{pr_num}"
            pr_data_full = self.api_request(endpoint_rollup)
            status_check_rollup = pr_data_full.get('statusCheckRollup', {})
            if isinstance(status_check_rollup, list):
                return status_check_rollup
            return []
        except Exception:
            return []

    def get_pr_files(self, org: str, repo: str, pr_num: int) -> List[Dict]:
        endpoint = f"repos/{org}/{repo}/pulls/{pr_num}/files"
        try:
            return self.api_request(endpoint)
        except GitHubAPIError:
            return []

    def get_current_pr_number(self, org: str, repo: str) -> Optional[int]:
        try:
            branch = get_git_branch()
            if not branch:
                return None

            return self.get_pr_by_branch(org, repo, branch)
        except Exception:
            return None


def log_info(msg: str):
    print(f"{Colors.GREEN}[*]{Colors.NC} {msg}", file=sys.stderr)


def log_warn(msg: str):
    print(f"{Colors.YELLOW}[!]{Colors.NC} {msg}", file=sys.stderr)


def log_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}", file=sys.stderr)


def log_success(msg: str):
    print(f"{Colors.GREEN}[+]{Colors.NC} {msg}", file=sys.stderr)


def get_current_pr_number(hostname: Optional[str] = None) -> Optional[int]:
    git_info = parse_git_remote()
    if not git_info:
        return None

    provider, org, repo = git_info
    if provider not in ['gh', 'ghe']:
        return None

    try:
        client = GitHubAPIClient(hostname=hostname)
        branch = get_git_branch()
        if not branch:
            return None
        return client.get_pr_by_branch(org, repo, branch)
    except Exception:
        return None


def get_pr_from_url(pr_url: str) -> Optional[Tuple[int, Optional[str], Optional[str], Optional[str]]]:
    patterns = [
        (r'(?:https?://)?([^/]+)/([^/]+)/([^/]+)/pull/(\d+)', True),
        (r'github\.com/([^/]+)/([^/]+)/pull/(\d+)', False),
        (r'/pull/(\d+)', False),
        (r'pull/(\d+)', False),
    ]

    for pattern, full_match in patterns:
        match = re.search(pattern, pr_url)
        if match:
            if full_match and len(match.groups()) == 4:
                hostname = match.group(1)
                org = match.group(2)
                repo = match.group(3)
                pr_num = int(match.group(4))
                return (pr_num, hostname, org, repo)
            elif len(match.groups()) == 3:
                org = match.group(1)
                repo = match.group(2)
                pr_num = int(match.group(3))
                return (pr_num, None, org, repo)
            else:
                pr_num = int(match.group(1))
                return (pr_num, None, None, None)

    return None


def get_pr_status_checks(pr_number: int, hostname: Optional[str] = None, org: Optional[str] = None,
                         repo: Optional[str] = None) -> Optional[list]:
    if not org or not repo:
        git_info = parse_git_remote()
        if not git_info:
            log_error('Could not determine repository from git remote')
            return None
        _, org, repo = git_info

    try:
        client = GitHubAPIClient(hostname=hostname)
        commit_sha = client.get_pr_commit_sha(org, repo, pr_number)
        if commit_sha:
            return client.get_pr_status_checks(org, repo, commit_sha)
        else:
            return client.get_pr_status_check_rollup(org, repo, pr_number)
    except ValueError as e:
        log_error(str(e))
        log_info("Add 'TOKEN' to ~/.claude-sauce.json under 'github' section")
        log_info('Example: {"github": {"TOKEN": "your-token-here"}}')
        return None
    except Exception as e:
        log_error(f"Failed to get status checks: {e}")
        return None


def find_codacy_check(status_checks: list) -> Optional[Dict]:
    if not status_checks:
        return None

    for check in status_checks:
        name = check.get('name', '').lower()
        if 'codacy' in name:
            codacy_url = check.get('details_url') or check.get('targetUrl') or check.get('target_url')
            if codacy_url:
                return {'name': check.get('name'), 'targetUrl': codacy_url, 'details_url': codacy_url}
            return check

    return None


def get_git_branch() -> Optional[str]:
    try:
        git_dir = Path('.git')
        if not git_dir.exists():
            return None

        head_file = git_dir / 'HEAD'
        if not head_file.exists():
            return None

        with open(head_file, 'r') as f:
            head_content = f.read().strip()

        if head_content.startswith('ref: refs/heads/'):
            return head_content.replace('ref: refs/heads/', '')
        return None
    except Exception:
        return None


def parse_git_remote() -> Optional[Tuple[str, str, str]]:
    try:
        git_config = Path('.git') / 'config'
        if not git_config.exists():
            return None

        remote_url = None
        in_remote_origin = False

        with open(git_config, 'r') as f:
            for line in f:
                line = line.strip()
                if line == '[remote "origin"]':
                    in_remote_origin = True
                    continue
                elif line.startswith('['):
                    in_remote_origin = False
                    continue

                if in_remote_origin and line.startswith('url'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        remote_url = parts[1].strip()
                        break

        if not remote_url:
            return None
    except Exception:
        return None

    patterns = [
        (r'<GITHUB_HOST>[:/]([^/]+)/([^/]+?)(?:\.git)?$', 'ghe'),
        (r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', 'gh'),
        (r'([^/:]+)[:/]([^/]+)/([^/]+?)(?:\.git)?$', 'gh'),
        (r'bitbucket\.org[:/]([^/]+)/([^/]+?)(?:\.git)?$', 'bb'),
    ]

    for pattern, provider in patterns:
        match = re.search(pattern, remote_url)
        if match:
            if len(match.groups()) == 3:
                org = match.group(2)
                repo = match.group(3).rstrip('.git')
            else:
                org = match.group(1)
                repo = match.group(2).rstrip('.git')
            return (provider, org, repo)

    return None


def parse_codacy_url(codacy_url: str) -> Optional[Tuple[str, str, str]]:
    pattern = r'app\.codacy\.com/organizations/([^/]+)/([^/]+)/repositories/([^/]+)'
    match = re.search(pattern, codacy_url)
    if match:
        provider = match.group(1)
        org = match.group(2)
        repo = match.group(3)
        return (provider, org, repo)
    return None


def main():
    parser = argparse.ArgumentParser(description='Extract Codacy URL from GitHub PR status checks',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--pr', type=int, help='PR number')
    parser.add_argument('--url', help='PR URL')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress status messages')

    args = parser.parse_args()

    pr_number = None
    hostname = None
    org = None
    repo = None

    if args.pr:
        pr_number = args.pr
    elif args.url:
        url_info = get_pr_from_url(args.url)
        if not url_info:
            log_error(f"Could not extract PR number from URL: {args.url}")
            sys.exit(1)
        pr_number, hostname, org, repo = url_info
    else:
        if not args.quiet:
            log_info('Auto-detecting PR from current branch...')
        git_info = parse_git_remote()
        if git_info:
            provider, org, repo = git_info
            git_config = Path('.git') / 'config'
            if git_config.exists():
                try:
                    with open(git_config, 'r') as f:
                        content = f.read()
                        if '<GITHUB_HOST>' in content:
                            hostname = '<GITHUB_HOST>'
                except (IOError, OSError):
                    pass
            if provider == 'ghe':
                hostname = '<GITHUB_HOST>'
        pr_number = get_current_pr_number(hostname=hostname)
        if not pr_number:
            log_error('Could not auto-detect PR number.')
            log_info("Make sure you're on a PR branch or specify --pr or --url")
            sys.exit(1)

    if not args.quiet:
        log_info(f"Checking PR #{pr_number}...")

    status_checks = get_pr_status_checks(pr_number, hostname, org, repo)
    if status_checks is None:
        sys.exit(1)

    codacy_check = find_codacy_check(status_checks)
    if not codacy_check:
        log_error('No Codacy status check found in this PR.')
        log_info('Make sure Codacy is configured for this repository.')
        sys.exit(1)

    codacy_url = codacy_check.get('targetUrl')
    if not codacy_url:
        log_error('Codacy check found but no URL available.')
        sys.exit(1)

    git_info = parse_git_remote()
    url_info = parse_codacy_url(codacy_url)

    pr_url = None
    if hostname and org and repo:
        if not hostname.startswith('http'):
            pr_url = f"https://{hostname}/{org}/{repo}/pull/{pr_number}"
        else:
            pr_url = f"{hostname}/{org}/{repo}/pull/{pr_number}"
    elif git_info:
        _, org_git, repo_git = git_info
        pr_url = f"https://github.com/{org_git}/{repo_git}/pull/{pr_number}"

    if args.json:
        output = {
            'codacy_url': codacy_url,
            'pr_number': pr_number,
        }
        if pr_url:
            output['pr_url'] = pr_url
        if url_info:
            output['provider'] = url_info[0]
            output['organization'] = url_info[1]
            output['repository'] = url_info[2]
        elif git_info:
            output['provider'] = git_info[0]
            output['organization'] = git_info[1]
            output['repository'] = git_info[2]
        print(json.dumps(output, indent=2))
    else:
        if not args.quiet:
            log_success(f"Found Codacy URL: {codacy_url}")
        print(codacy_url)

        if url_info:
            provider, org, repo = url_info
            if not args.quiet:
                print(f"Provider: {provider}", file=sys.stderr)
                print(f"Organization: {org}", file=sys.stderr)
                print(f"Repository: {repo}", file=sys.stderr)
        elif git_info:
            provider, org, repo = git_info
            if not args.quiet:
                print(f"Provider: {provider} (from git remote)", file=sys.stderr)
                print(f"Organization: {org} (from git remote)", file=sys.stderr)
                print(f"Repository: {repo} (from git remote)", file=sys.stderr)


if __name__ == '__main__':
    main()
