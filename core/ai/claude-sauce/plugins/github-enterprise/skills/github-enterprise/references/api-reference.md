# GitHub Enterprise API Reference

Direct API endpoints for <GITHUB_HOST> using `gh api`.

## Base Usage

```bash
gh api <endpoint> -h <GITHUB_HOST> [options]
```

Common options:
- `--jq '<filter>'` - Filter JSON output
- `-H "Header: value"` - Add headers
- `-X METHOD` - HTTP method (GET, POST, PUT, DELETE)
- `-f field=value` - Add form field
- `-F field=@file` - Add field from file

## Repositories

### Get Repository

```bash
gh api repos/{owner}/{repo} -h <GITHUB_HOST>
```

### List Organization Repos

```bash
gh api orgs/{org}/repos -h <GITHUB_HOST> --jq '.[].full_name'
```

### List User Repos

```bash
gh api users/{username}/repos -h <GITHUB_HOST>
```

### Get Repository Languages

```bash
gh api repos/{owner}/{repo}/languages -h <GITHUB_HOST>
```

### Get Repository Topics

```bash
gh api repos/{owner}/{repo}/topics -h <GITHUB_HOST> \
  -H "Accept: application/vnd.github.mercy-preview+json"
```

## Contents

### Get File Contents

```bash
# As JSON (base64 encoded)
gh api repos/{owner}/{repo}/contents/{path} -h <GITHUB_HOST>

# Raw content
gh api repos/{owner}/{repo}/contents/{path} -h <GITHUB_HOST> \
  -H "Accept: application/vnd.github.raw"

# From specific branch
gh api "repos/{owner}/{repo}/contents/{path}?ref={branch}" -h <GITHUB_HOST>
```

### List Directory

```bash
gh api repos/{owner}/{repo}/contents/{directory} -h <GITHUB_HOST> \
  --jq '.[].name'
```

### Get Repository Tree

```bash
# Full tree (recursive)
gh api repos/{owner}/{repo}/git/trees/{branch}?recursive=1 -h <GITHUB_HOST> \
  --jq '.tree[].path'

# Filter by extension
gh api repos/{owner}/{repo}/git/trees/{branch}?recursive=1 -h <GITHUB_HOST> \
  --jq '.tree[] | select(.path | endswith(".py")) | .path'
```

## Branches

### List Branches

```bash
gh api repos/{owner}/{repo}/branches -h <GITHUB_HOST> --jq '.[].name'
```

### Get Branch

```bash
gh api repos/{owner}/{repo}/branches/{branch} -h <GITHUB_HOST>
```

### Get Branch Protection

```bash
gh api repos/{owner}/{repo}/branches/{branch}/protection -h <GITHUB_HOST>
```

## Commits

### List Commits

```bash
gh api repos/{owner}/{repo}/commits -h <GITHUB_HOST>

# Filter by author
gh api "repos/{owner}/{repo}/commits?author={username}" -h <GITHUB_HOST>

# Filter by date
gh api "repos/{owner}/{repo}/commits?since=2024-01-01T00:00:00Z" -h <GITHUB_HOST>

# Filter by path
gh api "repos/{owner}/{repo}/commits?path={filepath}" -h <GITHUB_HOST>
```

### Get Commit

```bash
gh api repos/{owner}/{repo}/commits/{sha} -h <GITHUB_HOST>
```

### Get Commit Diff

```bash
gh api repos/{owner}/{repo}/commits/{sha} -h <GITHUB_HOST> \
  -H "Accept: application/vnd.github.diff"
```

### Compare Commits/Branches

```bash
gh api repos/{owner}/{repo}/compare/{base}...{head} -h <GITHUB_HOST>

# Get just filenames
gh api repos/{owner}/{repo}/compare/{base}...{head} -h <GITHUB_HOST> \
  --jq '.files[].filename'

# Get as diff
gh api repos/{owner}/{repo}/compare/{base}...{head} -h <GITHUB_HOST> \
  -H "Accept: application/vnd.github.diff"
```

## Pull Requests

### List PRs

```bash
gh api repos/{owner}/{repo}/pulls -h <GITHUB_HOST>

# Filter by state
gh api "repos/{owner}/{repo}/pulls?state=open" -h <GITHUB_HOST>
gh api "repos/{owner}/{repo}/pulls?state=closed" -h <GITHUB_HOST>
gh api "repos/{owner}/{repo}/pulls?state=all" -h <GITHUB_HOST>
```

### Get PR

```bash
gh api repos/{owner}/{repo}/pulls/{number} -h <GITHUB_HOST>
```

### Get PR Diff

```bash
gh api repos/{owner}/{repo}/pulls/{number} -h <GITHUB_HOST> \
  -H "Accept: application/vnd.github.diff"
```

### Get PR Files

```bash
gh api repos/{owner}/{repo}/pulls/{number}/files -h <GITHUB_HOST> \
  --jq '.[].filename'
```

### Get PR Commits

```bash
gh api repos/{owner}/{repo}/pulls/{number}/commits -h <GITHUB_HOST>
```

### Get PR Comments

```bash
# Review comments (on code)
gh api repos/{owner}/{repo}/pulls/{number}/comments -h <GITHUB_HOST>

# Issue comments (general)
gh api repos/{owner}/{repo}/issues/{number}/comments -h <GITHUB_HOST>
```

### Get PR Reviews

```bash
gh api repos/{owner}/{repo}/pulls/{number}/reviews -h <GITHUB_HOST>
```

## Issues

### List Issues

```bash
gh api repos/{owner}/{repo}/issues -h <GITHUB_HOST>

# Filter by state/labels
gh api "repos/{owner}/{repo}/issues?state=open&labels=bug" -h <GITHUB_HOST>
```

### Get Issue

```bash
gh api repos/{owner}/{repo}/issues/{number} -h <GITHUB_HOST>
```

### Get Issue Comments

```bash
gh api repos/{owner}/{repo}/issues/{number}/comments -h <GITHUB_HOST>
```

## Search

### Search Repositories

```bash
gh api "search/repositories?q={query}" -h <GITHUB_HOST>

# With qualifiers
gh api "search/repositories?q=language:python+org:<ORG>" -h <GITHUB_HOST>
```

### Search Code

```bash
gh api "search/code?q={query}" -h <GITHUB_HOST>

# In specific repo
gh api "search/code?q={query}+repo:{owner}/{repo}" -h <GITHUB_HOST>
```

### Search Issues/PRs

```bash
gh api "search/issues?q={query}" -h <GITHUB_HOST>

# Only PRs
gh api "search/issues?q={query}+type:pr" -h <GITHUB_HOST>

# Only issues
gh api "search/issues?q={query}+type:issue" -h <GITHUB_HOST>
```

## Users and Organizations

### Get User

```bash
gh api users/{username} -h <GITHUB_HOST>
```

### Get Organization

```bash
gh api orgs/{org} -h <GITHUB_HOST>
```

### List Organization Members

```bash
gh api orgs/{org}/members -h <GITHUB_HOST> --jq '.[].login'
```

### List Organization Teams

```bash
gh api orgs/{org}/teams -h <GITHUB_HOST>
```

## Releases

### List Releases

```bash
gh api repos/{owner}/{repo}/releases -h <GITHUB_HOST>
```

### Get Latest Release

```bash
gh api repos/{owner}/{repo}/releases/latest -h <GITHUB_HOST>
```

### Get Release by Tag

```bash
gh api repos/{owner}/{repo}/releases/tags/{tag} -h <GITHUB_HOST>
```

## Rate Limits

### Check Rate Limit

```bash
gh api rate_limit -h <GITHUB_HOST>

# Just search limits
gh api rate_limit -h <GITHUB_HOST> --jq '.resources.search'

# Just core limits
gh api rate_limit -h <GITHUB_HOST> --jq '.resources.core'
```

## Pagination

For endpoints returning lists, use pagination:

```bash
# Page 2, 50 items per page
gh api "repos/{owner}/{repo}/commits?per_page=50&page=2" -h <GITHUB_HOST>
```

Or use `--paginate` for all results:

```bash
gh api repos/{owner}/{repo}/commits -h <GITHUB_HOST> --paginate
```
