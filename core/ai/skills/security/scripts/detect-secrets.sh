#!/bin/bash
set -euo pipefail

# Secret Detection Script
# Scans for hardcoded credentials, API keys, and sensitive patterns

TARGET_DIR="${1:-.}"
FINDINGS=0

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_pattern() {
    local pattern="$1"
    local severity="$2"
    local description="$3"
    local files="${4:-*.py *.tf *.yml *.yaml *.json}"
    
    local results
    results=$(grep -rn "$pattern" "$TARGET_DIR" \
        --include="*.py" --include="*.tf" --include="*.yml" \
        --include="*.yaml" --include="*.json" --include="*.sh" \
        2>/dev/null || true)
    
    if [[ -n "$results" ]]; then
        if [[ "$severity" == "CRITICAL" ]]; then
            echo -e "${RED}[CRITICAL]${NC} $description"
        else
            echo -e "${YELLOW}[HIGH]${NC} $description"
        fi
        echo "$results" | head -10
        echo ""
        ((FINDINGS++)) || true
    fi
}

echo "Scanning for secrets in: $TARGET_DIR"
echo "────────────────────────────────────────"

# AWS Access Keys
check_pattern "AKIA[0-9A-Z]\{16\}" "CRITICAL" "AWS Access Key ID detected"

# AWS Secret Keys (common patterns)
check_pattern "aws_secret_access_key\s*=" "CRITICAL" "AWS Secret Key assignment"

# Port credentials hardcoded
check_pattern "clientId.*['\"][a-zA-Z0-9]\{20,\}['\"]" "CRITICAL" "Possible hardcoded Port Client ID"
check_pattern "clientSecret.*['\"][a-zA-Z0-9]\{20,\}['\"]" "CRITICAL" "Possible hardcoded Port Client Secret"

# Generic API keys
check_pattern "api_key\s*=\s*['\"][^'\"]\+['\"]" "HIGH" "Hardcoded API key"
check_pattern "apikey\s*=\s*['\"][^'\"]\+['\"]" "HIGH" "Hardcoded API key"

# Passwords in code
check_pattern "password\s*=\s*['\"][^'\"]\+['\"]" "CRITICAL" "Hardcoded password"
check_pattern "passwd\s*=\s*['\"][^'\"]\+['\"]" "CRITICAL" "Hardcoded password"

# Private keys
check_pattern "BEGIN.*PRIVATE KEY" "CRITICAL" "Private key in code"
check_pattern "BEGIN RSA PRIVATE KEY" "CRITICAL" "RSA private key in code"

# JWT secrets
check_pattern "jwt_secret\|JWT_SECRET" "HIGH" "JWT secret reference"

# Database connection strings with credentials
check_pattern "://[^:]\+:[^@]\+@" "HIGH" "Connection string with credentials"

# Slack/Discord webhooks
check_pattern "hooks.slack.com/services" "HIGH" "Slack webhook URL"
check_pattern "discord.com/api/webhooks" "HIGH" "Discord webhook URL"

# GitHub tokens
check_pattern "ghp_[a-zA-Z0-9]\{36\}" "CRITICAL" "GitHub Personal Access Token"
check_pattern "github_token\|GITHUB_TOKEN.*=" "HIGH" "GitHub token reference"

# OpenAI keys
check_pattern "sk-[a-zA-Z0-9]\{48\}" "CRITICAL" "OpenAI API key"

# Check for .env files that shouldn't be committed
if find "$TARGET_DIR" -name ".env" -o -name ".env.local" -o -name ".env.prod" 2>/dev/null | grep -q .; then
    echo -e "${YELLOW}[HIGH]${NC} .env files found (should be in .gitignore):"
    find "$TARGET_DIR" -name ".env*" 2>/dev/null | grep -v ".env.example"
    ((FINDINGS++)) || true
fi

# Check for tfvars with potential secrets
if grep -rn "secret\|password\|token\|key" "$TARGET_DIR" --include="*.tfvars" 2>/dev/null | grep -v "\.template" | grep -qv "_id\|_name"; then
    echo -e "${YELLOW}[HIGH]${NC} Potential secrets in .tfvars files:"
    grep -rn "secret\|password\|token" "$TARGET_DIR" --include="*.tfvars" 2>/dev/null | grep -v "\.template" | head -5
    ((FINDINGS++)) || true
fi

echo "────────────────────────────────────────"
if [[ $FINDINGS -eq 0 ]]; then
    echo -e "\033[0;32m✓ No secrets detected\033[0m"
else
    echo -e "${RED}Found $FINDINGS potential secret issue(s)${NC}"
    exit 1
fi
