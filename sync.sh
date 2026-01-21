#!/bin/bash
# Chroma Signal - Quick Sync Script
# Usage: ./sync.sh "Your commit message"

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default commit message
MESSAGE="${1:-Update Chroma Signal}"

echo -e "${YELLOW}🔄 Syncing Chroma Signal to GitHub...${NC}"
echo ""

# Show what's changed
echo -e "${YELLOW}📋 Changes to be committed:${NC}"
git status --short
echo ""

# Check if there are changes
if git diff-index --quiet HEAD -- && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo -e "${GREEN}✅ Nothing to commit, working tree clean${NC}"
    exit 0
fi

# Stage all changes (respects .gitignore)
echo -e "${YELLOW}📦 Staging changes...${NC}"
git add -A

# Show staged files
echo -e "${YELLOW}📋 Staged files:${NC}"
git diff --cached --name-only
echo ""

# Commit
echo -e "${YELLOW}💾 Committing: ${MESSAGE}${NC}"
git commit -m "$MESSAGE"

# Push to chroma-signal remote
echo -e "${YELLOW}🚀 Pushing to GitHub (chroma-signal)...${NC}"
git push chroma-signal main

echo ""
echo -e "${GREEN}✅ Successfully synced to GitHub!${NC}"
echo -e "${GREEN}   View at: https://github.com/chroma-core/chroma-signal${NC}"



