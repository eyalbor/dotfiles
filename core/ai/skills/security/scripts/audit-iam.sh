#!/bin/bash
set -euo pipefail

# IAM Permission Audit Script
# Checks for overly permissive IAM policies in Terraform and Serverless

TARGET_DIR="${1:-.}"
FINDINGS=0

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Auditing IAM permissions in: $TARGET_DIR"
echo "────────────────────────────────────────"

# Check for wildcard resources in serverless.yml
echo -e "\n${GREEN}Checking serverless.yml files...${NC}"
while IFS= read -r file; do
    if grep -q "Resource.*['\"]\\*['\"]" "$file" 2>/dev/null; then
        echo -e "${RED}[HIGH]${NC} Wildcard Resource in: $file"
        grep -n "Resource.*['\"]\\*['\"]" "$file" | head -3
        ((FINDINGS++)) || true
    fi
    
    if grep -q "Action.*['\"]\\*['\"]" "$file" 2>/dev/null; then
        echo -e "${RED}[CRITICAL]${NC} Wildcard Action in: $file"
        grep -n "Action.*['\"]\\*['\"]" "$file" | head -3
        ((FINDINGS++)) || true
    fi
    
    # Check for overly broad managed policies
    if grep -q "AdministratorAccess\|PowerUserAccess" "$file" 2>/dev/null; then
        echo -e "${RED}[CRITICAL]${NC} Overly broad managed policy in: $file"
        grep -n "AdministratorAccess\|PowerUserAccess" "$file"
        ((FINDINGS++)) || true
    fi
done < <(find "$TARGET_DIR" -name "serverless.yml" -o -name "serverless.yaml" 2>/dev/null)

# Check for wildcard in Terraform IAM resources
echo -e "\n${GREEN}Checking Terraform files...${NC}"
while IFS= read -r file; do
    # Wildcard resources
    if grep -q 'resources\s*=\s*\["\*"\]' "$file" 2>/dev/null; then
        echo -e "${RED}[HIGH]${NC} Wildcard resources in: $file"
        grep -n 'resources\s*=\s*\["\*"\]' "$file" | head -3
        ((FINDINGS++)) || true
    fi
    
    # Wildcard actions
    if grep -q 'actions\s*=\s*\["\*"\]' "$file" 2>/dev/null; then
        echo -e "${RED}[CRITICAL]${NC} Wildcard actions in: $file"
        grep -n 'actions\s*=\s*\["\*"\]' "$file" | head -3
        ((FINDINGS++)) || true
    fi
    
    # Resource = "*" pattern
    if grep -q 'Resource\s*=\s*"\*"' "$file" 2>/dev/null; then
        echo -e "${RED}[HIGH]${NC} Wildcard Resource in: $file"
        grep -n 'Resource\s*=\s*"\*"' "$file" | head -3
        ((FINDINGS++)) || true
    fi
done < <(find "$TARGET_DIR" -name "*.tf" 2>/dev/null)

# Check for missing encryption on S3 buckets
echo -e "\n${GREEN}Checking S3 bucket encryption...${NC}"
while IFS= read -r file; do
    if grep -q "aws_s3_bucket\s" "$file" 2>/dev/null; then
        bucket_names=$(grep -oP 'resource\s+"aws_s3_bucket"\s+"\K[^"]+' "$file" 2>/dev/null || true)
        for bucket in $bucket_names; do
            # Check if there's a corresponding encryption configuration
            if ! grep -q "aws_s3_bucket_server_side_encryption_configuration.*$bucket" "$file" 2>/dev/null; then
                # Check in the same directory for encryption config
                dir=$(dirname "$file")
                if ! grep -rq "aws_s3_bucket_server_side_encryption_configuration.*$bucket" "$dir" 2>/dev/null; then
                    echo -e "${YELLOW}[MEDIUM]${NC} S3 bucket '$bucket' may be missing encryption config in: $file"
                    ((FINDINGS++)) || true
                fi
            fi
        done
    fi
done < <(find "$TARGET_DIR" -name "*.tf" 2>/dev/null)

# Check for Port blueprint permissions
echo -e "\n${GREEN}Checking Port blueprint permissions...${NC}"
while IFS= read -r file; do
    if grep -q "port_blueprint\s" "$file" 2>/dev/null; then
        blueprint_names=$(grep -oP 'resource\s+"port_blueprint"\s+"\K[^"]+' "$file" 2>/dev/null || true)
        for blueprint in $blueprint_names; do
            # Check if there's a corresponding permissions resource
            if ! grep -q "port_blueprint_permissions.*$blueprint" "$file" 2>/dev/null; then
                dir=$(dirname "$file")
                if ! grep -rq "port_blueprint_permissions.*$blueprint" "$dir" 2>/dev/null; then
                    echo -e "${YELLOW}[MEDIUM]${NC} Blueprint '$blueprint' may be missing permissions in: $file"
                    ((FINDINGS++)) || true
                fi
            fi
        done
    fi
done < <(find "$TARGET_DIR" -name "*.tf" 2>/dev/null)

# Check for destructive Port actions accessible to Member role
echo -e "\n${GREEN}Checking Port action permissions...${NC}"
while IFS= read -r file; do
    # Check for unregister/delete operations allowed for Member
    if grep -B5 -A5 "unregister\|delete" "$file" 2>/dev/null | grep -q '"Member"'; then
        echo -e "${YELLOW}[MEDIUM]${NC} Destructive operation may be accessible to Member role in: $file"
        ((FINDINGS++)) || true
    fi
done < <(find "$TARGET_DIR" -name "*.tf" -path "*/blueprints/*" 2>/dev/null)

echo -e "\n────────────────────────────────────────"
if [[ $FINDINGS -eq 0 ]]; then
    echo -e "${GREEN}✓ No IAM permission issues detected${NC}"
else
    echo -e "${RED}Found $FINDINGS IAM permission issue(s)${NC}"
    exit 1
fi
