#!/bin/bash
# Quick script to save Claude's email output as a draft file
# Usage: ./draft_and_save.sh

DRAFTS_DIR="$HOME/Desktop/Chroma GTM/email_drafts"
mkdir -p "$DRAFTS_DIR"

echo "Paste your email draft (Ctrl+D when done):"
CONTENT=$(cat)

# Generate filename from timestamp
FILENAME="draft_$(date +%Y%m%d_%H%M%S).txt"
FILEPATH="$DRAFTS_DIR/$FILENAME"

echo "$CONTENT" > "$FILEPATH"
echo ""
echo "✅ Saved to: $FILEPATH"
echo ""
echo "To create Gmail draft, run:"
echo "  python scripts/gmail_draft.py --file \"$FILEPATH\""

