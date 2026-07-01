#!/bin/bash
set -euo pipefail

# Pre-commit Security Hook
# Install: cp scripts/pre-commit-security.sh .git/hooks/pre-commit

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Running pre-commit security checks..."

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

if [[ -z "$STAGED_FILES" ]]; then
    echo "No staged files to check"
    exit 0
fi

# Create temp dir with staged files
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

for file in $STAGED_FILES; do
    if [[ -f "$file" ]]; then
        mkdir -p "$TEMP_DIR/$(dirname "$file")"
        git show ":$file" > "$TEMP_DIR/$file" 2>/dev/null || true
    fi
done

# Run secret detection on staged files
echo "Checking for secrets in staged files..."

SECRETS_FOUND=0

# Check for AWS keys
if grep -rn "AKIA[0-9A-Z]\{16\}" "$TEMP_DIR" 2>/dev/null; then
    echo -e "${RED}[BLOCKED]${NC} AWS Access Key detected in staged files"
    SECRETS_FOUND=1
fi

# Check for hardcoded passwords
if grep -rn "password\s*=\s*['\"][^'\"\$]\+['\"]" "$TEMP_DIR" --include="*.py" --include="*.tf" 2>/dev/null | grep -v "password\s*=\s*['\"]['\"]"; then
    echo -e "${RED}[BLOCKED]${NC} Hardcoded password detected in staged files"
    SECRETS_FOUND=1
fi

# Check for private keys
if grep -rn "BEGIN.*PRIVATE KEY" "$TEMP_DIR" 2>/dev/null; then
    echo -e "${RED}[BLOCKED]${NC} Private key detected in staged files"
    SECRETS_FOUND=1
fi

# Check for Port credentials
if grep -rn "clientSecret.*['\"][a-zA-Z0-9]\{20,\}['\"]" "$TEMP_DIR" --include="*.py" 2>/dev/null; then
    echo -e "${RED}[BLOCKED]${NC} Hardcoded Port credentials detected in staged files"
    SECRETS_FOUND=1
fi

# Check for GitHub tokens
if grep -rn "ghp_[a-zA-Z0-9]\{36\}" "$TEMP_DIR" 2>/dev/null; then
    echo -e "${RED}[BLOCKED]${NC} GitHub token detected in staged files"
    SECRETS_FOUND=1
fi

# Check for .env files
for file in $STAGED_FILES; do
    if [[ "$file" == ".env" ]] || [[ "$file" == ".env.local" ]] || [[ "$file" == ".env.prod" ]]; then
        echo -e "${RED}[BLOCKED]${NC} .env file staged: $file"
        SECRETS_FOUND=1
    fi
done

# Check for tfvars with secrets
if grep -rn "secret\s*=\s*\"[^\"]\+\"" "$TEMP_DIR" --include="*.tfvars" 2>/dev/null | grep -v "\.template"; then
    echo -e "${RED}[BLOCKED]${NC} Secrets in .tfvars file"
    SECRETS_FOUND=1
fi

if [[ $SECRETS_FOUND -eq 1 ]]; then
    echo -e "\n${RED}Commit blocked due to security issues.${NC}"
    echo "Remove secrets and try again, or use 'git commit --no-verify' to bypass."
    exit 1
fi

echo -e "${GREEN}✓ Security checks passed${NC}"
exit 0
