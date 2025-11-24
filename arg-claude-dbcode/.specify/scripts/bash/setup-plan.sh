#!/bin/bash

# Setup plan for RAG backend feature

# Find the latest spec file
FEATURE_SPEC=$(find specs -name spec.md | sort | head -1)
if [ -z "$FEATURE_SPEC" ]; then
    echo "ERROR: No spec.md found in specs directory"
    exit 1
fi

# Get feature number from directory name
FEATURE_NUMBER=$(basename $(dirname "$FEATURE_SPEC") | cut -d'-' -f1)
FEATURE_NAME=$(basename $(dirname "$FEATURE_SPEC") | cut -d'-' -f2-)

# Create plans directory
SPECS_DIR=$(dirname "$FEATURE_SPEC")
PLANS_DIR="$SPECS_DIR/plans"
mkdir -p "$PLANS_DIR"

# Copy template plan
cat > "$PLANS_DIR/impl.md" << 'TEMPLATE'
# Implementation Plan: [FEATURE_NAME]

## Technical Context

### Dependencies
- [Dependency 1]: [Version/Details]
- [Dependency 2]: [Version/Details]

### Technology Stack
- [Technology 1]: [Purpose]
- [Technology 2]: [Purpose]

### Integration Points
- [Integration 1]: [Details]

## Constitution Check
- [ ] Principle 1: [Status]
- [ ] Principle 2: [Status]
- [ ] Principle 3: [Status]
- [ ] Principle 4: [Status]

## Gates

### Gate 1 - Architecture Alignment
- [ ] Architecture review completed
- [ ] Technical debt impact assessed

### Gate 2 - Security
- [ ] Input validation requirements identified
- [ ] Authentication/authorization requirements identified

### Gate 3 - Performance
- [ ] Performance targets defined
- [ ] Scalability considerations addressed

## Phases

### Phase 0: Research & Preparation
- [ ] Generate research.md
- [ ] Resolve all NEEDS CLARIFICATION items

### Phase 1: Data Model & Contracts
- [ ] Generate data-model.md
- [ ] Generate API contracts

### Phase 2: Implementation
- [ ] Implement core functionality
- [ ] Write tests
- [ ] Run tests

### Phase 3: Integration & Testing
- [ ] Integrate components
- [ ] Run integration tests
- [ ] Fix any issues

## Implementation Tasks

### Task 1: [Task Name] (Priority: P1)
- [ ] Step 1: [Description]
- [ ] Step 2: [Description]

### Task 2: [Task Name] (Priority: P2)
- [ ] Step 1: [Description]
- [ ] Step 2: [Description]

### Task 3: [Task Name] (Priority: P3)
- [ ] Step 1: [Description]
- [ ] Step 2: [Description]
TEMPLATE

# Get current branch name
BRANCH=$(git branch --show-current)

# Output JSON
echo "{"
echo "  \"FEATURE_SPEC\": \"$FEATURE_SPEC\","
echo "  \"IMPL_PLAN\": \"$PLANS_DIR/impl.md\","
echo "  \"SPECS_DIR\": \"$SPECS_DIR\","
echo "  \"BRANCH\": \"$BRANCH\""
echo "}"
