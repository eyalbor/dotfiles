asj # GitHub Search Syntax Guide

Advanced search operators for repositories and code search on GitHub Enterprise.

## Repository Search

### Basic Qualifiers

| Qualifier | Example | Description |
|-----------|---------|-------------|
| `in:name` | `api in:name` | Search in repository name |
| `in:description` | `api in:description` | Search in description |
| `in:readme` | `api in:readme` | Search in README |
| `in:topics` | `api in:topics` | Search in topics |

### Owner/Organization

```bash
# By owner
gh search repos "query" --owner <ORG>

# By organization (via gh api)
gh api search/repositories?q=org:<ORG>+query -h <GITHUB_HOST>
```

### Language

```bash
# Single language
gh search repos "api" --language python

# Multiple languages (use API)
gh api "search/repositories?q=language:python+language:javascript" -h <GITHUB_HOST>
```

### Size and Activity

| Qualifier | Example | Description |
|-----------|---------|-------------|
| `size:n` | `size:>1000` | Repo size in KB |
| `stars:n` | `stars:>100` | Star count |
| `forks:n` | `forks:>=50` | Fork count |
| `created:date` | `created:>2023-01-01` | Creation date |
| `pushed:date` | `pushed:>2024-01-01` | Last push date |

### Boolean Operators

```bash
# AND (implicit)
gh search repos "api client" -h <GITHUB_HOST>

# OR
gh api "search/repositories?q=api+OR+sdk" -h <GITHUB_HOST>

# NOT
gh api "search/repositories?q=api+NOT+deprecated" -h <GITHUB_HOST>
```

## Code Search

### File Qualifiers

| Qualifier | Example | Description |
|-----------|---------|-------------|
| `filename:` | `filename:config.yaml` | Search in specific filename |
| `extension:` | `extension:py` | Search by file extension |
| `path:` | `path:src/` | Search in specific path |
| `language:` | `language:python` | Search in specific language |

### Examples

```bash
# Find function definitions in Python
gh search code "def authenticate" --language python -h <GITHUB_HOST>

# Find config files
gh search code "database" --filename "*.yaml" -h <GITHUB_HOST>

# Find in specific directory
gh search code "import" --repo owner/repo -h <GITHUB_HOST> | grep "src/"

# Find TODO comments
gh search code "TODO:" --language python -h <GITHUB_HOST>
```

### Exact Matches

Use quotes for exact phrase matching:

```bash
gh search code "\"def authenticate_user\"" -h <GITHUB_HOST>
```

### Symbol Search

For function/class names (requires code indexing):

```bash
gh search code "symbol:authenticate" --language python -h <GITHUB_HOST>
```

## Date Formats

GitHub accepts these date formats:
- `YYYY-MM-DD` - Full date
- `YYYY-MM` - Year and month
- `YYYY` - Year only

Relative dates:
- `>2024-01-01` - After date
- `<2024-01-01` - Before date
- `2024-01-01..2024-06-01` - Date range

## Sorting Results

### Via gh CLI

```bash
gh search repos "api" --sort stars --order desc -h <GITHUB_HOST>
```

### Via API

```bash
gh api "search/repositories?q=api&sort=stars&order=desc" -h <GITHUB_HOST>
```

Sort options for repos: `stars`, `forks`, `help-wanted-issues`, `updated`
Sort options for code: `indexed` (default), `best-match`

## Pagination

### Via gh CLI

```bash
# Get more results
gh search repos "api" --limit 100 -h <GITHUB_HOST>
```

### Via API

```bash
# Page through results
gh api "search/repositories?q=api&per_page=30&page=2" -h <GITHUB_HOST>
```

## Rate Limits

Search API has separate rate limits:
- Authenticated: 30 requests/minute
- Unauthenticated: 10 requests/minute

Check current limits:
```bash
gh api rate_limit -h <GITHUB_HOST> --jq '.resources.search'
```
