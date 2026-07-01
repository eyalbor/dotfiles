#!/bin/bash
set -euo pipefail

# Terraform Security Audit Script
# Checks for security misconfigurations in Terraform code

TARGET_DIR="${1:-.}"
FINDINGS=0

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "Auditing Terraform security in: $TARGET_DIR"
echo "────────────────────────────────────────"

# Check if tfsec is available
if command -v tfsec &> /dev/null; then
    echo -e "\n${GREEN}Running tfsec...${NC}"
    terraform_dirs=$(find "$TARGET_DIR" -name "*.tf" -exec dirname {} \; 2>/dev/null | sort -u || true)
    
    for tf_dir in $terraform_dirs; do
        if [[ -d "$tf_dir" ]]; then
            echo -e "${BLUE}Scanning: $tf_dir${NC}"
            if ! tfsec "$tf_dir" --minimum-severity HIGH 2>/dev/null; then
                ((FINDINGS++)) || true
            fi
        fi
    done
else
    echo -e "${YELLOW}[INFO]${NC} tfsec not installed. Install with: brew install tfsec"
    echo "Falling back to pattern-based checks..."
fi

# Manual security checks
echo -e "\n${GREEN}Running pattern-based security checks...${NC}"

# Check for hardcoded credentials in provider blocks
echo -e "\n${BLUE}Checking provider blocks...${NC}"
while IFS= read -r file; do
    # Port provider with hardcoded credentials
    if grep -A5 'provider\s*"port"' "$file" 2>/dev/null | grep -q 'client_id\s*=\s*"[^v]'; then
        echo -e "${RED}[CRITICAL]${NC} Possible hardcoded Port credentials in: $file"
        ((FINDINGS++)) || true
    fi
    
    # AWS provider with hardcoded credentials
    if grep -A5 'provider\s*"aws"' "$file" 2>/dev/null | grep -q 'access_key\s*=\s*"'; then
        echo -e "${RED}[CRITICAL]${NC} Hardcoded AWS credentials in: $file"
        ((FINDINGS++)) || true
    fi
done < <(find "$TARGET_DIR" -name "*.tf" 2>/dev/null)

# Check for missing encryption
echo -e "\n${BLUE}Checking encryption settings...${NC}"
while IFS= read -r file; do
    # RDS without encryption
    if grep -q 'aws_db_instance' "$file" 2>/dev/null; then
        if ! grep -A20 'aws_db_instance' "$file" 2>/dev/null | grep -q 'storage_encrypted\s*=\s*true'; then
            echo -e "${YELLOW}[MEDIUM]${NC} RDS instance may lack encryption in: $file"
            ((FINDINGS++)) || true
        fi
    fi
    
    # EBS volumes without encryption
    if grep -q 'aws_ebs_volume' "$file" 2>/dev/null; then
        if ! grep -A10 'aws_ebs_volume' "$file" 2>/dev/null | grep -q 'encrypted\s*=\s*true'; then
            echo -e "${YELLOW}[MEDIUM]${NC} EBS volume may lack encryption in: $file"
            ((FINDINGS++)) || true
        fi
    fi
    
    # SQS without encryption
    if grep -q 'aws_sqs_queue' "$file" 2>/dev/null; then
        if ! grep -A15 'aws_sqs_queue' "$file" 2>/dev/null | grep -q 'kms_master_key_id\|sqs_managed_sse_enabled'; then
            echo -e "${YELLOW}[MEDIUM]${NC} SQS queue may lack encryption in: $file"
            ((FINDINGS++)) || true
        fi
    fi
    
    # SNS without encryption
    if grep -q 'aws_sns_topic' "$file" 2>/dev/null; then
        if ! grep -A10 'aws_sns_topic' "$file" 2>/dev/null | grep -q 'kms_master_key_id'; then
            echo -e "${YELLOW}[LOW]${NC} SNS topic may lack encryption in: $file"
        fi
    fi
done < <(find "$TARGET_DIR" -name "*.tf" 2>/dev/null)

# Check for public access
echo -e "\n${BLUE}Checking for public access...${NC}"
while IFS= read -r file; do
    # S3 public ACL
    if grep -q 'acl\s*=\s*"public' "$file" 2>/dev/null; then
        echo -e "${RED}[HIGH]${NC} S3 bucket with public ACL in: $file"
        ((FINDINGS++)) || true
    fi
    
    # Security group with 0.0.0.0/0 ingress
    if grep -B5 -A10 'ingress' "$file" 2>/dev/null | grep -q '0.0.0.0/0\|::/0'; then
        echo -e "${YELLOW}[MEDIUM]${NC} Security group with open ingress in: $file"
        grep -n '0.0.0.0/0' "$file" 2>/dev/null | head -3 || true
        ((FINDINGS++)) || true
    fi
done < <(find "$TARGET_DIR" -name "*.tf" 2>/dev/null)

# Check for logging disabled
echo -e "\n${BLUE}Checking logging configurations...${NC}"
while IFS= read -r file; do
    # S3 without access logging
    if grep -q 'aws_s3_bucket\s' "$file" 2>/dev/null; then
        bucket_count=$(grep -c 'aws_s3_bucket\s' "$file" 2>/dev/null || echo "0")
        logging_count=$(grep -c 'aws_s3_bucket_logging' "$file" 2>/dev/null || echo "0")
        
        if [[ "$bucket_count" -gt "$logging_count" ]]; then
            echo -e "${YELLOW}[LOW]${NC} Some S3 buckets may lack access logging in: $file"
        fi
    fi
done < <(find "$TARGET_DIR" -name "*.tf" 2>/dev/null)

# Check for insecure defaults
echo -e "\n${BLUE}Checking for insecure defaults...${NC}"
while IFS= read -r file; do
    # Lambda without VPC (if it accesses internal resources)
    if grep -q 'aws_lambda_function' "$file" 2>/dev/null; then
        if ! grep -A30 'aws_lambda_function' "$file" 2>/dev/null | grep -q 'vpc_config'; then
            filename=$(basename "$file")
            echo -e "${YELLOW}[INFO]${NC} Lambda without VPC config in $filename (verify if needed)"
        fi
    fi
done < <(find "$TARGET_DIR" -name "*.tf" 2>/dev/null)

echo -e "\n────────────────────────────────────────"
if [[ $FINDINGS -eq 0 ]]; then
    echo -e "${GREEN}✓ No Terraform security issues detected${NC}"
else
    echo -e "${RED}Found $FINDINGS Terraform security issue(s)${NC}"
    exit 1
fi
