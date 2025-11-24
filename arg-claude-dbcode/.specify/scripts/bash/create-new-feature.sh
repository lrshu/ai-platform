#!/bin/bash

# Create new feature directory and branch
FEATURE_NUMBER=$1
FEATURE_NAME=$2

# Create specs directory
SPEC_DIR="specs/${FEATURE_NUMBER}-${FEATURE_NAME}"
mkdir -p "${SPEC_DIR}"
mkdir -p "${SPEC_DIR}/checklists"

# Create initial spec file
cat > "${SPEC_DIR}/spec.md" << 'SPEC_CONTENT'
# Feature Specification Template

## Basic Information
**Feature Name**: ${FEATURE_NAME}  
**Feature Number**: ${FEATURE_NUMBER}  
**Status**: Draft  
**Created By**: Claude Code  
**Created On**: $(date +%Y-%m-%d)  
**Last Updated**: $(date +%Y-%m-%d)  

## Overview
A clear, concise description of the feature.

## User Scenarios & Testing
- Scenario 1: ...

## Functional Requirements
- Requirement 1: ...

## Success Criteria
- Criterion 1: ...

## Key Entities
- Entity 1: ...

## Assumptions
- Assumption 1: ...

## Dependencies
- Dependency 1: ...
SPEC_CONTENT

# Create branch (if not exists)
BRANCH_NAME="${FEATURE_NUMBER}-${FEATURE_NAME}"
git checkout -b "${BRANCH_NAME}" 2>/dev/null || git checkout "${BRANCH_NAME}"

echo "{"
echo "  \"BRANCH_NAME\": \"${BRANCH_NAME}\","
echo "  \"SPEC_FILE\": \"${SPEC_DIR}/spec.md\""
echo "}"
