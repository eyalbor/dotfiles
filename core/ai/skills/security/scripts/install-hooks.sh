#!/bin/bash
set -euo pipefail

# Install Security Pre-commit Hook
# Usage: ./scripts/install-hooks.sh [target_repo_path]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_REPO="${1:-.}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [[ ! -d "$TARGET_REPO/.git" ]]; then
    echo "Error: $TARGET_REPO is not a git repository"
    exit 1
fi

HOOKS_DIR="$TARGET_REPO/.git/hooks"
PRE_COMMIT_HOOK="$HOOKS_DIR/pre-commit"

# Backup existing hook if present
if [[ -f "$PRE_COMMIT_HOOK" ]]; then
    echo -e "${YELLOW}Backing up existing pre-commit hook...${NC}"
    mv "$PRE_COMMIT_HOOK" "$PRE_COMMIT_HOOK.backup"
fi

# Copy the security hook
cp "$SCRIPT_DIR/pre-commit-security.sh" "$PRE_COMMIT_HOOK"
chmod +x "$PRE_COMMIT_HOOK"

echo -e "${GREEN}✓ Security pre-commit hook installed to: $PRE_COMMIT_HOOK${NC}"
echo ""
echo "The hook will check for:"
echo "  - Hardcoded AWS keys"
echo "  - Hardcoded passwords"
echo "  - Private keys"
echo "  - Port credentials"
echo "  - GitHub tokens"
echo "  - .env files"
echo "  - Secrets in .tfvars"
echo ""
echo "To bypass (not recommended): git commit --no-verify"
