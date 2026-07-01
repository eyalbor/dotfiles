#!/usr/bin/env python3
"""
Jenkins Console Fetcher - Fetch console text from Jenkins jobs

Fetches console output from Jenkins builds (tests, CI/CD jobs, etc.)
for AI-powered analysis.

Supports Windows, macOS, and Linux.
Requires: Python 3.7+
"""

import sys
import argparse
import re
import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import ssl

# =============================================================================
# LOGGING HELPERS
# =============================================================================

class Colors:
    """Color codes with fallback for non-TTY"""
    RED = '\033[0;31m' if sys.stdout.isatty() else ''
    GREEN = '\033[0;32m' if sys.stdout.isatty() else ''
    YELLOW = '\033[1;33m' if sys.stdout.isatty() else ''
    CYAN = '\033[0;36m' if sys.stdout.isatty() else ''
    NC = '\033[0m' if sys.stdout.isatty() else ''

def log_info(msg: str):
    print(f"{Colors.GREEN}[*]{Colors.NC} {msg}", file=sys.stderr)

def log_warn(msg: str):
    print(f"{Colors.YELLOW}[!]{Colors.NC} {msg}", file=sys.stderr)

def log_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}", file=sys.stderr)

def log_success(msg: str):
    print(f"{Colors.GREEN}[+]{Colors.NC} {msg}", file=sys.stderr)


# =============================================================================
# CURL PARSING & AUTH HELPERS
# =============================================================================

def parse_curl_command(curl_cmd: str) -> Dict:
    """Extract headers and cookies from a cURL command."""
    result = {"headers": {}, "cookies": ""}

    # Extract cookies from -b or --cookie
    cookie_match = re.search(r"-b\s+'([^']+)'|--cookie\s+'([^']+)'", curl_cmd)
    if cookie_match:
        result["cookies"] = cookie_match.group(1) or cookie_match.group(2)

    # Extract headers (only keep useful ones)
    skip_headers = ['accept', 'accept-language', 'cache-control', 'connection',
                    'sec-fetch-dest', 'sec-fetch-mode', 'sec-fetch-site', 'sec-fetch-user',
                    'upgrade-insecure-requests', 'sec-ch-ua', 'sec-ch-ua-mobile', 'sec-ch-ua-platform']
    for match in re.finditer(r"-H\s+'([^:]+):\s*([^']+)'", curl_cmd):
        header_name, header_value = match.groups()
        if header_name.lower() not in skip_headers:
            result["headers"][header_name] = header_value

    return result


def get_curl_from_user() -> Dict:
    """Prompt user to paste cURL command."""
    print("\n" + "="*60, file=sys.stderr)
    print("BROWSER SESSION AUTHENTICATION", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print("\nTo get the cURL command:", file=sys.stderr)
    print("1. Open Jenkins build page in Chrome (make sure you're logged in)", file=sys.stderr)
    print("2. Press F12 → Network tab", file=sys.stderr)
    print("3. Refresh the page (F5)", file=sys.stderr)
    print("4. Right-click the FIRST request → Copy → Copy as cURL", file=sys.stderr)
    print("\nPaste the cURL command below (press Enter twice when done):", file=sys.stderr)
    print("-"*60, file=sys.stderr)

    lines = []
    while True:
        try:
            line = input()
            if line:
                lines.append(line)
            elif lines:
                break
        except EOFError:
            break

    curl_cmd = " ".join(lines)
    return parse_curl_command(curl_cmd)


def open_browser_for_session(url: str) -> Optional[Dict]:
    """Open browser and attempt to capture session."""
    import webbrowser

    base_url = re.sub(r'/consoleText/?$', '', url)

    print("\n" + "="*60, file=sys.stderr)
    print("BROWSER SESSION CAPTURE", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print("\nOpening Jenkins in your default browser...", file=sys.stderr)
    print("Please log in if prompted.\n", file=sys.stderr)

    webbrowser.open(base_url)

    print("After logging in:\n", file=sys.stderr)
    print(f"{Colors.CYAN}Option 1:{Colors.NC} Copy cURL from browser (recommended)", file=sys.stderr)
    print("  1. Press F12 → Network tab", file=sys.stderr)
    print("  2. Refresh the page (F5)", file=sys.stderr)
    print("  3. Right-click the FIRST request → Copy → Copy as cURL", file=sys.stderr)
    print("  4. Paste below\n", file=sys.stderr)
    print(f"{Colors.CYAN}Option 2:{Colors.NC} Copy cookies manually", file=sys.stderr)
    print("  1. Press F12 → Application tab → Cookies", file=sys.stderr)
    print("  2. Copy the JSESSIONID value", file=sys.stderr)
    print("  3. Type 'cookie:' followed by the value\n", file=sys.stderr)
    print("-"*60, file=sys.stderr)
    print("Paste cURL command, type 'cookie:VALUE', or 'skip' to cancel:", file=sys.stderr)

    lines = []
    while True:
        try:
            line = input()
            if line.lower() == 'skip':
                return None
            if line.lower().startswith('cookie:'):
                cookie_value = line[7:].strip()
                return {"cookies": f"JSESSIONID={cookie_value}", "headers": {}}
            if line:
                lines.append(line)
            elif lines:
                break
        except EOFError:
            break

    if lines:
        curl_cmd = " ".join(lines)
        return parse_curl_command(curl_cmd)
    return None


def suggest_auth_alternatives(url: str, error_code: int = 401) -> Optional[Dict]:
    """Display auth failure options."""
    print("\n" + "="*60, file=sys.stderr)
    print(f"{Colors.RED}AUTHENTICATION FAILED{Colors.NC}", file=sys.stderr)
    print("="*60, file=sys.stderr)

    if error_code == 401:
        print("\nThe server returned 401 Unauthorized.", file=sys.stderr)
    elif error_code == 403:
        print("\nThe server returned 403 Forbidden.", file=sys.stderr)

    print("\nOptions:", file=sys.stderr)
    print(f"  {Colors.GREEN}1{Colors.NC}) Open browser to capture session", file=sys.stderr)
    print(f"  {Colors.GREEN}2{Colors.NC}) Paste a cURL command from browser", file=sys.stderr)
    print(f"  {Colors.GREEN}3{Colors.NC}) Enter new username and token", file=sys.stderr)
    print(f"  {Colors.GREEN}4{Colors.NC}) Exit", file=sys.stderr)
    print(file=sys.stderr)

    try:
        choice = input("Enter choice [1-4]: ").strip()
    except (KeyboardInterrupt, EOFError):
        return None

    if choice == '1':
        return open_browser_for_session(url)
    elif choice == '2':
        return get_curl_from_user()
    elif choice == '3':
        return {'prompt_credentials': True}
    else:
        return None


# =============================================================================
# JENKINS CONSOLE FETCHER
# =============================================================================

class JenkinsConsoleFetcher:
    """Fetches console text from Jenkins jobs."""

    def __init__(self, url: str, user: Optional[str] = None, token: Optional[str] = None,
                 cookie: Optional[str] = None, headers: Optional[Dict] = None,
                 verify_ssl: bool = True, workspace: str = "analysis_workspace"):
        self.url = self._normalize_url(url)
        self.user = user
        self.token = token
        self.cookie = cookie
        self.headers = headers or {}
        self.verify_ssl = verify_ssl
        self.build_num = self._extract_build_num()
        self.build_id = self._extract_build_id()

        # Create workspace
        workspace_with_build = f"{workspace}/{self.build_id}"
        self.workspace = Path(workspace_with_build)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.workspace / f".cache_build_{self.build_num}"

    def _normalize_url(self, url: str) -> str:
        """Ensure URL ends with /consoleText"""
        url = url.strip().rstrip('/')
        if not url.endswith('/consoleText'):
            url += '/consoleText'
        return url

    def _extract_build_num(self) -> str:
        """Extract build number from URL"""
        url_without_suffix = re.sub(r'/consoleText/?$', '', self.url)
        match = re.search(r'/(\d+)/?$', url_without_suffix)
        return match.group(1) if match else "unknown"

    def _extract_build_id(self) -> str:
        """Extract unique build identifier from URL"""
        domain_match = re.search(r'https?://([^/]+)', self.url)
        domain = domain_match.group(1) if domain_match else "unknown"
        build_num = self._extract_build_num()
        unique_id = f"{domain}_{build_num}".replace('.', '_').replace('/', '_')
        return unique_id

    def _get_cookie_from_config(self) -> Optional[str]:
        """Get COOKIE from ~/.claude-sauce.json jenkins section.
        Stored as raw JSESSIONID value; prefixed with key on use."""
        claude_sauce_path = Path.home() / '.claude-sauce.json'
        if claude_sauce_path.exists():
            try:
                with open(claude_sauce_path) as f:
                    config = json.load(f)
                    cookie = config.get('jenkins', {}).get('COOKIE')
                    if cookie:
                        # If raw value (no '='), prepend the Jenkins SSO cookie key
                        if '=' not in cookie:
                            cookie = f'JSESSIONID.2b634e4d={cookie}'
                        return cookie
            except Exception as e:
                log_warn(f"Failed to read Jenkins cookie from {claude_sauce_path}: {e}")
        return None

    def _get_credentials(self, prompt: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """Get credentials from ~/.claude-sauce.json or prompt."""
        if self.user and self.token:
            return self.user, self.token

        # Try to load from ~/.claude-sauce.json
        claude_sauce_path = Path.home() / '.claude-sauce.json'
        if claude_sauce_path.exists():
            try:
                with open(claude_sauce_path) as f:
                    config = json.load(f)
                    jenkins_config = config.get('jenkins', {})
                    user = jenkins_config.get('USER')
                    token = jenkins_config.get('TOKEN')
                    if user and token:
                        return user, token
            except Exception as e:
                log_warn(f"Failed to read Jenkins credentials from {claude_sauce_path}: {e}")

        # Fall back to interactive prompt
        if prompt:
            log_info("Enter Jenkins credentials:")
            try:
                user = input("    Username: ").strip()
                import getpass
                token = getpass.getpass("    API Token: ")
                return user, token
            except (KeyboardInterrupt, EOFError):
                log_error("Credential entry cancelled")
                return None, None

        return None, None

    def fetch(self, force: bool = False, tail_lines: int = 0,
              interactive: bool = True) -> Optional[str]:
        """Fetch Jenkins console output. Returns console text or None on failure."""

        # Check cache
        log_path = self.workspace / 'console.txt'
        if log_path.exists() and not force:
            log_info(f"Using cached console for build #{self.build_num}")
            with open(log_path, 'r', encoding='utf-8') as f:
                return f.read()

        max_retries = 2
        attempt = 0

        while attempt < max_retries:
            attempt += 1
            log_info(f"Fetching console from: {self.url}")

            try:
                content = self._fetch_content()
                if content is None:
                    return None

                if not content.strip():
                    log_error("Console output is empty.")
                    return None

                # Apply tail if specified
                if tail_lines > 0:
                    lines = content.split('\n')
                    if len(lines) > tail_lines:
                        log_warn(f"Truncating from {len(lines)} to last {tail_lines} lines")
                        content = '\n'.join(lines[-tail_lines:])

                # Save to cache
                self._save_content(content)
                return content

            except HTTPError as e:
                log_error(f"HTTP {e.code}: {e.reason}")

                if e.code in (401, 403) and interactive:
                    alt_auth = suggest_auth_alternatives(self.url, e.code)
                    if alt_auth:
                        if alt_auth.get('prompt_credentials'):
                            user, token = self._get_credentials(prompt=True)
                            if user and token:
                                self.user = user
                                self.token = token
                                self.cookie = None
                                continue
                        else:
                            self.cookie = alt_auth.get("cookies")
                            self.headers.update(alt_auth.get("headers", {}))
                            self.user = None
                            self.token = None
                            continue
                return None

            except URLError as e:
                error_msg = str(e.reason)
                log_error(f"Connection failed: {error_msg}")

                if ('SSL' in error_msg or 'certificate' in error_msg.lower()) and interactive and self.verify_ssl:
                    print(f"\n{Colors.YELLOW}SSL certificate verification failed.{Colors.NC}", file=sys.stderr)
                    try:
                        response = input("Disable SSL verification and retry? [y/N]: ").strip().lower()
                        if response == 'y':
                            self.verify_ssl = False
                            continue
                    except (KeyboardInterrupt, EOFError):
                        pass
                return None

            except Exception as e:
                log_error(f"Error fetching console: {e}")
                return None

        log_error("Max retries exceeded")
        return None

    def _fetch_content(self) -> Optional[str]:
        """Fetch content from Jenkins."""
        req = Request(self.url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        if self.user and self.token:
            credentials = base64.b64encode(f"{self.user}:{self.token}".encode()).decode()
            req.add_header('Authorization', f'Basic {credentials}')

        if self.cookie:
            req.add_header('Cookie', self.cookie)

        for key, value in self.headers.items():
            req.add_header(key, value)

        ssl_context = None
        if not self.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        with urlopen(req, timeout=60, context=ssl_context) as response:
            return response.read().decode('utf-8', errors='ignore')

    def _save_content(self, content: str):
        """Save console content to workspace."""
        log_path = self.workspace / 'console.txt'
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(content)

        self.cache_file.touch()

        # Save metadata
        info_path = self.workspace / 'build_info.txt'
        job_url = self.url.replace('/consoleText', '')
        with open(info_path, 'w') as f:
            f.write(f"Build: #{self.build_num}\n")
            f.write(f"Job URL: {job_url}\n")
            f.write(f"Console URL: {self.url}\n")
            f.write(f"Downloaded: {datetime.now().isoformat()}\n")
            f.write(f"Lines: {len(content.split(chr(10)))}\n")

        log_success(f"Console saved to {log_path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Fetch Jenkins console text for AI analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url "https://jenkins.com/job/my-job/123/"
  %(prog)s --url "https://jenkins.com/job/my-job/123/" --user admin --token abc123
  %(prog)s --url "https://jenkins.com/job/my-job/123/" --from-curl
  %(prog)s --url "https://jenkins.com/job/my-job/123/" --tail 5000
        """
    )

    parser.add_argument('--url', required=True, help='Jenkins job URL')
    parser.add_argument('--user', help='Jenkins username (or configure in ~/.claude-sauce.json)')
    parser.add_argument('--token', help='Jenkins API token (or configure in ~/.claude-sauce.json)')
    parser.add_argument('--from-curl', action='store_true', help='Extract auth from browser cURL command')
    parser.add_argument('--cookie', help='Session cookie value')
    parser.add_argument('--prompt', action='store_true', help='Prompt for credentials')
    parser.add_argument('--tail', type=int, default=0, help='Only output last N lines (0=all)')
    parser.add_argument('--force', action='store_true', help='Force re-download (ignore cache)')
    parser.add_argument('--workspace', default='analysis_workspace', help='Workspace directory for caching')
    parser.add_argument('--no-verify-ssl', action='store_true', help='Disable SSL certificate verification')
    parser.add_argument('--no-interactive', action='store_true', help='Disable interactive prompts')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only output console text (no status messages)')

    args = parser.parse_args()

    # Get auth from cURL if requested
    cookie = args.cookie
    headers = {}
    if args.from_curl:
        curl_data = get_curl_from_user()
        cookie = curl_data.get("cookies")
        headers = curl_data.get("headers", {})
        log_success("Extracted session from cURL command")

    # Create fetcher
    fetcher = JenkinsConsoleFetcher(
        args.url,
        user=args.user,
        token=args.token,
        cookie=cookie,
        headers=headers,
        verify_ssl=not args.no_verify_ssl,
        workspace=args.workspace
    )

    # Get credentials if needed
    if not cookie and not (fetcher.user and fetcher.token):
        # Try cookie from config first (for SSO instances)
        cookie = fetcher._get_cookie_from_config()
        if cookie:
            fetcher.cookie = cookie
        else:
            user, token = fetcher._get_credentials(prompt=args.prompt)
            if user and token:
                fetcher.user = user
                fetcher.token = token

    # Fetch console
    interactive = not args.no_interactive
    content = fetcher.fetch(force=args.force, tail_lines=args.tail, interactive=interactive)

    if content is None:
        sys.exit(1)

    # Output console text to stdout
    print(content)

    if not args.quiet:
        log_success(f"Fetched {len(content.split(chr(10)))} lines from build #{fetcher.build_num}")


if __name__ == '__main__':
    main()

