#!/usr/bin/env python3

import argparse
import json
import os
import re
import shutil
import ssl
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
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

    def get_pr_files(self, org: str, repo: str, pr_num: int) -> List[Dict]:
        endpoint = f"repos/{org}/{repo}/pulls/{pr_num}/files"
        try:
            return self.api_request(endpoint)
        except GitHubAPIError:
            return []


def log_info(msg: str):
    print(f"{Colors.GREEN}[*]{Colors.NC} {msg}", file=sys.stderr)


def log_warn(msg: str):
    print(f"{Colors.YELLOW}[!]{Colors.NC} {msg}", file=sys.stderr)


def log_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}", file=sys.stderr)


def log_success(msg: str):
    print(f"{Colors.GREEN}[+]{Colors.NC} {msg}", file=sys.stderr)


def validate_branch_name(branch: str) -> bool:
    if not branch:
        return False
    if len(branch) > 255:
        return False
    invalid_chars = ['\n', '\r', '\t', '\0', ' ', '~', '^', ':', '?', '*', '[', '\\']
    if any(char in branch for char in invalid_chars):
        return False
    if branch.startswith('.') or branch.endswith('.'):
        return False
    if branch.endswith('.lock'):
        return False
    return True


def load_config() -> Tuple[str, str]:
    api_token = None
    base_url = 'https://api.codacy.com'

    # Load from ~/.claude-sauce.json
    claude_sauce_path = Path.home() / '.claude-sauce.json'
    if claude_sauce_path.exists():
        try:
            with open(claude_sauce_path) as f:
                config = json.load(f)
                codacy_config = config.get('codacy', {})
                api_token = codacy_config.get('API_TOKEN')
                base_url = codacy_config.get('API_URL', base_url)
        except Exception as e:
            log_warn(f"Failed to read config from {claude_sauce_path}: {e}")

    if not api_token:
        log_error("Codacy API token not found.")
        log_info("Add 'API_TOKEN' to ~/.claude-sauce.json under 'codacy' section")
        log_info('Example: {"codacy": {"API_TOKEN": "your-token-here"}}')
        sys.exit(1)

    return base_url.rstrip('/'), api_token


def parse_codacy_url(codacy_url: str) -> Optional[Tuple[str, str, str, Optional[str], Optional[int], Optional[str]]]:
    patterns = [
        (r'(https?://[^/]+)/organizations/([^/]+)/([^/]+)/repositories/([^/]+)', True, False),
        (r'(https?://codacy\.[^/]+)/([^/]+)/([^/]+)/([^/]+)/pullRequest\?prid=(\d+)', False, True),
        (r'(https?://codacy\.[^/]+)/([^/]+)/([^/]+)/([^/]+)', False, False),
    ]

    pr_id = None
    pr_url = None
    for pattern, is_org_format, has_pr_id in patterns:
        match = re.search(pattern, codacy_url)
        if match:
            if is_org_format:
                base_url = match.group(1)
                provider = match.group(2)
                org = match.group(3)
                repo = match.group(4)
            elif has_pr_id:
                base_url = match.group(1)
                provider = match.group(2)
                org = match.group(3)
                repo = match.group(4)
                pr_id = int(match.group(5))
            else:
                base_url = match.group(1)
                provider = match.group(2)
                org = match.group(3)
                repo = match.group(4)

            if provider in ['gh', 'ghe', 'bb']:
                api_base = base_url.split('/pullRequest')[0].rstrip('/')
                hostname_match = re.search(r'(https?://[^/]+)', codacy_url)
                detected_hostname = None
                if hostname_match:
                    detected_hostname = hostname_match.group(1)
                    if '<GITHUB_HOST>' in detected_hostname or provider == 'ghe':
                        pr_url = f"https://<GITHUB_HOST>/{org}/{repo}"
                    else:
                        pr_url = f"https://github.com/{org}/{repo}"
                return (provider, org, repo, api_base, pr_id, pr_url)
            elif provider == 'github.com':
                return ('gh', org, repo, base_url, pr_id, pr_url)
            elif provider == 'bitbucket.org':
                return ('bb', org, repo, base_url, pr_id, pr_url)

    return None


def get_pr_number_from_branch(hostname: Optional[str], org: str, repo: str, branch: str) -> Optional[int]:
    if not validate_branch_name(branch):
        log_warn(f"Invalid branch name: {branch}")
        return None

    try:
        sanitized_hostname = None
        if hostname:
            sanitized_hostname = hostname.replace('https://', '').replace('http://', '')
        client = GitHubAPIClient(hostname=sanitized_hostname)
        return client.get_pr_by_branch(org, repo, branch)
    except ValueError:
        return None
    except Exception:
        return None


def get_pr_changed_files(pr_url: str, hostname: Optional[str] = None, org: Optional[str] = None, repo: Optional[str] = None,
                         branch: Optional[str] = None) -> Optional[Set[str]]:
    pr_match = re.search(r'github\.com/([^/]+)/([^/]+)/pull/(\d+)', pr_url)
    if not pr_match:
        pr_match = re.search(r'([^/]+)/([^/]+)/pull/(\d+)', pr_url)
        if not pr_match:
            if hostname and org and repo and branch:
                pr_num = get_pr_number_from_branch(hostname, org, repo, branch)
                if pr_num:
                    pr_match = type('obj', (object,), {'group': lambda self, n: [None, org, repo, pr_num][n]})()
            else:
                return None

    detected_hostname = hostname
    if not detected_hostname:
        if '<GITHUB_HOST>' in pr_url:
            detected_hostname = '<GITHUB_HOST>'
        elif 'github.com' in pr_url:
            hostname_match = re.search(r'(https?://[^/]+)', pr_url)
            if hostname_match:
                detected_hostname = hostname_match.group(1).replace('https://', '').replace('http://', '')

    org_name = pr_match.group(1) if pr_match else org
    repo_name = pr_match.group(2) if pr_match else repo
    pr_num = pr_match.group(3) if pr_match else None

    if not pr_num:
        return None

    try:
        sanitized_hostname = None
        if detected_hostname:
            sanitized_hostname = detected_hostname.replace('https://', '').replace('http://', '')
        client = GitHubAPIClient(hostname=sanitized_hostname)
        files_data = client.get_pr_files(org_name, repo_name, int(pr_num))
        changed_files = {f.get('filename') for f in files_data}
        return changed_files
    except ValueError:
        return None
    except Exception as e:
        log_warn(f"Could not fetch PR files: {e}")
        return None


def make_request(url: str, api_token: str, data: Optional[Dict] = None, method: str = 'POST') -> Dict:
    headers = {'api-token': api_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}

    body = json.dumps(data).encode() if data else b'{}'
    request = Request(url, data=body, headers=headers, method=method)

    ssl_verify = os.environ.get('CODACY_SSL_VERIFY', 'true').lower() != 'false'
    if ssl_verify:
        context = ssl.create_default_context()
    else:
        context = ssl._create_unverified_context()

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

        log_error(f"HTTP Error {e.code}: {error_msg}")
        if e.code == 401:
            log_info("Check your API token in ~/.claude-sauce.json under 'codacy' section")
        elif e.code == 404:
            log_info('Repository not found. Check provider, organization, and repository names.')
        sys.exit(1)
    except URLError as e:
        log_error(f"Connection Error: {e.reason}")
        sys.exit(1)


def fetch_issues(base_url: str, api_token: str, provider: str, organization: str, repository: str, branch: Optional[str] = None,
                 levels: Optional[List[str]] = None, categories: Optional[List[str]] = None) -> Dict:
    endpoint = f"{base_url}/api/v3/analysis/organizations/{provider}/{organization}/repositories/{repository}/issues/search"

    if branch:
        endpoint += f"?branch={branch}"

    request_body = {}
    if levels:
        request_body['levels'] = levels
    if categories:
        request_body['categories'] = categories

    return make_request(endpoint, api_token, request_body)


def format_issue(issue: Dict) -> str:
    file_path = issue.get('filePath', 'unknown')
    line = issue.get('lineNumber', issue.get('line', '?'))
    pattern_info = issue.get('patternInfo', {})
    pattern_id = pattern_info.get('id', 'unknown')
    level = pattern_info.get('level', pattern_info.get('severityLevel', 'unknown'))
    category = pattern_info.get('category', issue.get('category', 'unknown'))
    message = issue.get('message', 'No message')
    language = issue.get('language', '')
    line_text = issue.get('lineText', '')

    result = f"  {file_path}:{line} [{level}] {category}"
    if language:
        result += f" ({language})"
    result += f" - {message}"
    if pattern_id != 'unknown':
        result += f" (pattern: {pattern_id})"
    if line_text:
        result += f"\n    Code: {line_text.strip()}"

    return result


def format_issues_human(issues_data: Dict, changed_files: Optional[Set[str]] = None):
    issues = issues_data.get('data', [])
    total = issues_data.get('total', len(issues))

    if changed_files:
        issues = [issue for issue in issues if issue.get('filePath') in changed_files]
        if not issues:
            log_success('No issues found in files changed by this PR!')
            return
        log_info(f"Found {len(issues)} issue(s) in PR files (filtered from {total} total):\n")
    else:
        if not issues:
            log_success('No issues found!')
            return
        log_info(f"Found {total} issue(s):\n")

    issues_by_file = {}
    for issue in issues:
        file_path = issue.get('filePath', 'unknown')
        if file_path not in issues_by_file:
            issues_by_file[file_path] = []
        issues_by_file[file_path].append(issue)

    for file_path in sorted(issues_by_file.keys()):
        print(f"\n{file_path}:")
        for issue in issues_by_file[file_path]:
            print(format_issue(issue))


def main():
    parser = argparse.ArgumentParser(description='Fetch code quality issues from Codacy API',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--provider', choices=['gh', 'ghe', 'bb'], help='Provider (gh=GitHub, ghe=GitHub Enterprise, bb=Bitbucket)')
    parser.add_argument('--organization', help='Organization name')
    parser.add_argument('--repository', help='Repository name')
    parser.add_argument('--branch', help='Branch name')
    parser.add_argument('--commit', help='Commit SHA (not yet supported by API)')
    parser.add_argument('--levels', help='Comma-separated levels (Error,Warning,Info)')
    parser.add_argument(
        '--categories',
        help='Comma-separated categories (Security,CodeStyle,ErrorProne,Performance,Compatibility,UnusedCode,Complexity,Documentation)')
    parser.add_argument('--url', help='Codacy URL (extracts provider/org/repo)')
    parser.add_argument('--pr-url', help='GitHub PR URL to filter issues by changed files')
    parser.add_argument('--json', action='store_true', help='Output raw JSON')

    args = parser.parse_args()

    base_url, api_token = load_config()

    provider = args.provider
    organization = args.organization
    repository = args.repository

    changed_files = None
    pr_url_from_codacy = None

    if args.url:
        url_info = parse_codacy_url(args.url)
        if not url_info:
            log_error(f"Could not parse Codacy URL: {args.url}")
            log_info('Expected format: https://app.codacy.com/organizations/{provider}/{org}/repositories/{repo}/...')
            log_info('Or for self-hosted: https://codacy.domain.com/{provider}/{org}/{repo}/...')
            sys.exit(1)
        provider, organization, repository, url_base, pr_id, pr_url_base_from_codacy = url_info
        if url_base:
            base_url = url_base
            log_info(f"Using base URL from Codacy URL: {base_url}")
        log_info(f"Extracted from URL: provider={provider}, org={organization}, repo={repository}")

        if pr_url_base_from_codacy and args.branch and not args.pr_url:
            pr_num = get_pr_number_from_branch('<GITHUB_HOST>' if '<GITHUB_HOST>' in pr_url_base_from_codacy else None, organization,
                                               repository, args.branch)
            if pr_num:
                pr_url_full = f"{pr_url_base_from_codacy}/pull/{pr_num}"
                args.pr_url = pr_url_full
                log_info(f"Auto-detected PR URL from branch: {pr_url_full}")
            elif pr_id:
                log_warn(f"PR ID {pr_id} found in Codacy URL, but cannot auto-detect GitHub PR number. Use --pr-url to filter by PR files.")

    if args.pr_url:
        pr_url_from_codacy = args.pr_url
        changed_files = get_pr_changed_files(args.pr_url, None, organization, repository, args.branch)
        if changed_files:
            log_info(f"Filtering issues to {len(changed_files)} file(s) changed in PR")
        else:
            log_warn('Could not fetch PR files. Showing all issues on branch.')
    elif pr_url_from_codacy:
        changed_files = get_pr_changed_files(pr_url_from_codacy, None, organization, repository, args.branch)
        if changed_files:
            log_info(f"Filtering issues to {len(changed_files)} file(s) changed in PR")
        else:
            log_warn('Could not fetch PR files. Showing all issues on branch.')

    if not provider or not organization or not repository:
        log_error('Missing required arguments: --provider, --organization, --repository (or --url)')
        parser.print_help()
        sys.exit(1)

    if args.commit:
        log_warn('--commit parameter is not yet supported by Codacy API v3')

    levels = None
    if args.levels:
        levels = [l.strip() for l in args.levels.split(',')]
        valid_levels = ['Error', 'Warning', 'Info']
        invalid = [l for l in levels if l not in valid_levels]
        if invalid:
            log_warn(f"Invalid levels: {invalid}. Valid levels: {', '.join(valid_levels)}")
            levels = [l for l in levels if l in valid_levels]

    categories = None
    if args.categories:
        categories = [c.strip() for c in args.categories.split(',')]
        valid_categories = [
            'Security', 'CodeStyle', 'ErrorProne', 'Performance', 'Compatibility', 'UnusedCode', 'Complexity', 'Documentation'
        ]
        invalid = [c for c in categories if c not in valid_categories]
        if invalid:
            log_warn(f"Invalid categories: {invalid}. Valid categories: {', '.join(valid_categories)}")
            categories = [c for c in categories if c in valid_categories]

    if not args.json:
        log_info(f"Fetching issues for {provider}/{organization}/{repository}...")
        if args.branch:
            log_info(f"Branch: {args.branch}")
        if levels:
            log_info(f"Levels: {', '.join(levels)}")
        if categories:
            log_info(f"Categories: {', '.join(categories)}")

    try:
        issues_data = fetch_issues(base_url=base_url, api_token=api_token, provider=provider, organization=organization,
                                   repository=repository, branch=args.branch, levels=levels, categories=categories)

        if args.json:
            if changed_files:
                filtered_issues = [issue for issue in issues_data.get('data', []) if issue.get('filePath') in changed_files]
                issues_data['data'] = filtered_issues
                issues_data['total'] = len(filtered_issues)
            print(json.dumps(issues_data, indent=2))
        else:
            format_issues_human(issues_data, changed_files)
    except KeyboardInterrupt:
        log_error('\nInterrupted by user')
        sys.exit(1)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
