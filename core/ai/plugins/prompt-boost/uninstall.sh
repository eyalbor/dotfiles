#!/usr/bin/env bash

# Prompt Enhancement Tool - Uninstallation Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
  echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   Prompt Enhancement Tool - Uninstaller                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

log_warning "This will remove:"
echo "  • Cursor commands (~/.cursor/commands/prompt-boost-*.md)"
echo "  • Claude Code skill (~/.claude/skills/prompt-boost/)"
echo ""

read -p "Continue with uninstallation? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  log_info "Uninstallation cancelled"
  exit 0
fi

echo ""

# Remove Cursor commands
if [ -f "$HOME/.cursor/commands/prompt-boost-advanced.md" ] || [ -f "$HOME/.cursor/commands/prompt-boost-lite.md" ]; then
  log_info "Removing Cursor commands..."
  rm -f "$HOME/.cursor/commands/prompt-boost-advanced.md"
  rm -f "$HOME/.cursor/commands/prompt-boost-lite.md"
  log_success "Cursor commands removed"
else
  log_info "No Cursor commands found (already removed)"
fi

# Remove Claude Code skill
if [ -d "$HOME/.claude/skills/prompt-boost" ]; then
  log_info "Removing Claude Code skill..."
  rm -rf "$HOME/.claude/skills/prompt-boost"
  log_success "Claude Code skill removed"
else
  log_info "No Claude Code skill found (already removed)"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Uninstallation Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
log_info "To reinstall:"
echo "  1. Download the latest release from GitHub"
echo "  2. Extract and copy files to your home directory"
echo "  3. See: https://github.com/eyalbor/prompt-boost/releases"
echo ""
