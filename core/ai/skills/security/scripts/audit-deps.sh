#!/bin/bash
set -euo pipefail

# Dependency Vulnerability Audit Script
# Scans Python and Node.js dependencies for known vulnerabilities

TARGET_DIR="${1:-.}"
FINDINGS=0

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "Auditing dependencies in: $TARGET_DIR"
echo "────────────────────────────────────────"

# Python dependency audit
echo -e "\n${GREEN}Scanning Python dependencies...${NC}"

# Find directories with Pipfile or requirements.txt
python_projects=$(find "$TARGET_DIR" \( -name "Pipfile" -o -name "requirements.txt" -o -name "pyproject.toml" \) -not -path "*/node_modules/*" 2>/dev/null || true)

if [[ -n "$python_projects" ]]; then
    while IFS= read -r project_file; do
        project_dir=$(dirname "$project_file")
        project_name=$(basename "$project_dir")
        
        echo -e "${BLUE}Checking: $project_name${NC}"
        
        # Check if pip-audit is available
        if command -v pip-audit &> /dev/null; then
            if [[ -f "$project_dir/requirements.txt" ]]; then
                if ! pip-audit -r "$project_dir/requirements.txt" --strict 2>/dev/null; then
                    echo -e "${RED}[HIGH]${NC} Vulnerabilities found in $project_name"
                    ((FINDINGS++)) || true
                fi
            elif [[ -f "$project_dir/Pipfile.lock" ]]; then
                # pip-audit can work with Pipfile.lock through pipenv
                echo -e "${YELLOW}[INFO]${NC} Pipfile.lock found - run 'pipenv check' in $project_dir"
            fi
        else
            echo -e "${YELLOW}[INFO]${NC} pip-audit not installed. Install with: pip install pip-audit"
        fi
        
        # Check for safety (alternative tool)
        if command -v safety &> /dev/null; then
            if [[ -f "$project_dir/requirements.txt" ]]; then
                if ! safety check -r "$project_dir/requirements.txt" --short-report 2>/dev/null; then
                    echo -e "${RED}[HIGH]${NC} Safety found vulnerabilities in $project_name"
                    ((FINDINGS++)) || true
                fi
            fi
        fi
        
    done <<< "$python_projects"
else
    echo "No Python projects found"
fi

# Node.js dependency audit
echo -e "\n${GREEN}Scanning Node.js dependencies...${NC}"

node_projects=$(find "$TARGET_DIR" -name "package.json" -not -path "*/node_modules/*" 2>/dev/null || true)

if [[ -n "$node_projects" ]]; then
    while IFS= read -r package_file; do
        project_dir=$(dirname "$package_file")
        project_name=$(basename "$project_dir")
        
        echo -e "${BLUE}Checking: $project_name${NC}"
        
        if [[ -f "$project_dir/package-lock.json" ]] || [[ -f "$project_dir/yarn.lock" ]]; then
            cd "$project_dir"
            
            if [[ -f "package-lock.json" ]]; then
                audit_result=$(npm audit --audit-level=high --json 2>/dev/null || true)
                vuln_count=$(echo "$audit_result" | grep -o '"high":[0-9]*' | grep -o '[0-9]*' || echo "0")
                critical_count=$(echo "$audit_result" | grep -o '"critical":[0-9]*' | grep -o '[0-9]*' || echo "0")
                
                if [[ "$critical_count" -gt 0 ]]; then
                    echo -e "${RED}[CRITICAL]${NC} $critical_count critical vulnerabilities in $project_name"
                    ((FINDINGS++)) || true
                fi
                if [[ "$vuln_count" -gt 0 ]]; then
                    echo -e "${RED}[HIGH]${NC} $vuln_count high vulnerabilities in $project_name"
                    ((FINDINGS++)) || true
                fi
            elif [[ -f "yarn.lock" ]]; then
                if command -v yarn &> /dev/null; then
                    if ! yarn audit --level high 2>/dev/null; then
                        echo -e "${RED}[HIGH]${NC} Vulnerabilities found in $project_name"
                        ((FINDINGS++)) || true
                    fi
                fi
            fi
            
            cd - > /dev/null
        else
            echo -e "${YELLOW}[INFO]${NC} No lock file in $project_name - run npm install first"
        fi
        
    done <<< "$node_projects"
else
    echo "No Node.js projects found"
fi

# Check for outdated dependencies with known issues
echo -e "\n${GREEN}Checking for outdated critical packages...${NC}"

# Known vulnerable package versions to flag
VULNERABLE_PATTERNS=(
    "requests<2.25"
    "urllib3<1.26.5"
    "cryptography<3.3"
    "pyyaml<5.4"
    "jinja2<2.11.3"
)

for pattern in "${VULNERABLE_PATTERNS[@]}"; do
    package=$(echo "$pattern" | cut -d'<' -f1)
    if grep -rq "$package" "$TARGET_DIR" --include="requirements.txt" --include="Pipfile" 2>/dev/null; then
        version_check=$(grep -rh "$package" "$TARGET_DIR" --include="requirements.txt" --include="Pipfile" 2>/dev/null | head -1 || true)
        echo -e "${YELLOW}[INFO]${NC} Check version of $package: $version_check"
    fi
done

echo -e "\n────────────────────────────────────────"
if [[ $FINDINGS -eq 0 ]]; then
    echo -e "${GREEN}✓ No dependency vulnerabilities detected${NC}"
else
    echo -e "${RED}Found $FINDINGS dependency issue(s)${NC}"
    exit 1
fi
