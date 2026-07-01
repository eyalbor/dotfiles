#!/bin/bash
set -euo pipefail

# Security Scan Orchestrator
# Usage: ./security-scan.sh [all|secrets|iam|deps|terraform] [target_dir]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${2:-.}"
SCAN_TYPE="${1:-all}"

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_finding() {
    local severity="$1"
    local message="$2"
    case "$severity" in
        CRITICAL) echo -e "${RED}[CRITICAL]${NC} $message" ;;
        HIGH)     echo -e "${RED}[HIGH]${NC} $message" ;;
        MEDIUM)   echo -e "${YELLOW}[MEDIUM]${NC} $message" ;;
        LOW)      echo -e "${GREEN}[LOW]${NC} $message" ;;
        INFO)     echo -e "${BLUE}[INFO]${NC} $message" ;;
    esac
}

run_secrets_scan() {
    print_header "Secret Detection Scan"
    "${SCRIPT_DIR}/detect-secrets.sh" "$TARGET_DIR"
}

run_iam_scan() {
    print_header "IAM Permission Audit"
    "${SCRIPT_DIR}/audit-iam.sh" "$TARGET_DIR"
}

run_deps_scan() {
    print_header "Dependency Vulnerability Scan"
    "${SCRIPT_DIR}/audit-deps.sh" "$TARGET_DIR"
}

run_terraform_scan() {
    print_header "Terraform Security Scan"
    "${SCRIPT_DIR}/audit-terraform.sh" "$TARGET_DIR"
}

case "$SCAN_TYPE" in
    all)
        run_secrets_scan
        run_iam_scan
        run_deps_scan
        run_terraform_scan
        ;;
    secrets)
        run_secrets_scan
        ;;
    iam)
        run_iam_scan
        ;;
    deps)
        run_deps_scan
        ;;
    terraform)
        run_terraform_scan
        ;;
    *)
        echo "Usage: $0 [all|secrets|iam|deps|terraform] [target_dir]"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Security scan complete.${NC}"
