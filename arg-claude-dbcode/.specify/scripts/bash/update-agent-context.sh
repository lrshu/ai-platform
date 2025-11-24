#!/bin/bash

# Update agent context script
AGENT_NAME=$1
CONTEXT_FILE=".specify/agents/${AGENT_NAME}.md"

mkdir -p "$(dirname "$CONTEXT_FILE")"

# If context file doesn't exist, create it
if [ ! -f "$CONTEXT_FILE" ]; then
    cat > "$CONTEXT_FILE" << 'INIT'
# Agent Context for Claude Code

## Current Feature
- Branch: [CURRENT_BRANCH]
- Spec: [CURRENT_SPEC]
- Plan: [CURRENT_PLAN]

## Technology Stack
- [TECH]

## Dependencies
- [DEPENDENCY]

## Notes
- [NOTES]
INIT
fi

# Update current branch, spec, and plan
BRANCH=$(git branch --show-current)
SPEC=$(find specs -name spec.md | sort | head -1)
PLAN=$(find specs -name impl.md | sort | head -1)

# Escape slashes in paths for sed
ESCAPED_SPEC=$(echo "$SPEC" | sed 's/\//\\\//g')
ESCAPED_PLAN=$(echo "$PLAN" | sed 's/\//\\\//g')

# Replace placeholders
sed -i.bak "s/\[CURRENT_BRANCH\]/$BRANCH/" "$CONTEXT_FILE"
sed -i.bak "s/\[CURRENT_SPEC\]/$ESCAPED_SPEC/" "$CONTEXT_FILE"
sed -i.bak "s/\[CURRENT_PLAN\]/$ESCAPED_PLAN/" "$CONTEXT_FILE"

# Remove backup
rm "$CONTEXT_FILE.bak"
