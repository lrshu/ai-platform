# Feature Specification: MCP Account Provisioning Server

**Feature Branch**: `001-provision-mcp-accounts`
**Created**: 2025-11-25
**Status**: Draft
**Input**: User description: "create feature mcp server specify / 构建一个简单的标准化的 mcp server，使用 fastapi-mcp 作为整体框架, 实现 开通邮箱账号权限 和 开通 git 账号权限 功能"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Self-service email access (Priority: P1)
IT support staff submits an employee's Chinese name and national ID to instantly provision an email login package for onboarding.

**Why this priority**: Email access is the first credential required for all hires; delaying it blocks downstream orientation tasks.

**Independent Test**: Submit valid name + ID via MCP client, verify response includes `{name_pinyin}@email.com` plus a compliant random password, and confirm ID validation errors block bad data.

**Acceptance Scenarios**:

1. **Given** a valid 18-digit ID and name, **When** the request type is "email", **Then** the service returns a lowercase pinyin email handle at `@email.com` and a random password meeting complexity rules.
2. **Given** an invalid ID (bad checksum or length), **When** the request is submitted, **Then** the service rejects it with a precise validation error and no credentials are minted.

---

### User Story 2 - Git repository access (Priority: P2)
Development managers request Git credentials for contributors using the same identity data to keep tooling access aligned with HR records.

**Why this priority**: Code access is needed after email but still within day-one onboarding; aligning identity inputs reduces duplicated forms.

**Independent Test**: Submit a "git" request with valid identity data and verify the response contains `{name_pinyin}@git.com`, a compliant random password, and audit metadata confirming the issuance.

**Acceptance Scenarios**:

1. **Given** a valid name and ID, **When** the request type is "git", **Then** the service returns a git-handle email at `@git.com` plus a random password that includes letters and digits.
2. **Given** duplicate requests for the same identity within one session, **When** each request is processed, **Then** the service returns deterministic handles but freshly generated passwords so downstream systems can rotate credentials.

---

### Edge Cases

- Invalid ID input: less than 18 characters, non-numeric tail, or checksum mismatch must trigger descriptive errors without generating credentials.
- Unsupported characters in names (punctuation, numerals) must be sanitized or rejected with guidance to update HR records.
- Environmental misconfiguration (missing `PORT`, unsupported locale dictionary) must cause a startup failure rather than silent defaults.
- Concurrent requests for different services using the same identity must not leak passwords between responses.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The server MUST expose MCP tools for `email_account` and `git_account`, each accepting `name` and `national_id` inputs.
- **FR-002**: The system MUST validate Chinese 18-digit ID numbers, including length, numeric structure, and checksum, and reject invalid submissions with actionable error codes.
- **FR-003**: The system MUST transliterate Chinese names into full lowercase pinyin without spaces; names that cannot be transliterated MUST return a clear failure response.
- **FR-004**: Successful email requests MUST return `{pinyin}@email.com`; successful git requests MUST return `{pinyin}@git.com` with ASCII-only handles.
- **FR-005**: Every successful response MUST include a randomly generated password at least 12 characters long containing upper-case letters, lower-case letters, and digits.
- **FR-006**: Responses MUST include metadata describing the request type, timestamp, and deterministic handle so that downstream systems can audit provenance.
- **FR-007**: The service MUST log every request outcome (success or validation error) with masked IDs to satisfy compliance traceability.
- **FR-008**: The server MUST refuse processing if required environment configuration (e.g., `PORT`) is missing or malformed, emitting a startup error message.
- **FR-009**: The system MUST return localized human-readable error messages plus machine-readable error codes for client automation.

### Key Entities *(include if feature involves data)*

- **IdentitySubmission**: Represents user-provided `name` and `national_id`, plus derived `name_pinyin`. Used for validation, auditing, and handle construction.
- **ProvisioningResponse**: Contains `account_type`, `handle`, `generated_password`, `timestamp`, and `status_code` fields returned to the MCP client.
- **AuditRecord**: Internal log entry referencing `IdentitySubmission`, outcome, and masked identifiers for compliance reporting.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of valid provisioning requests return credentials in under 3 seconds end-to-end.
- **SC-002**: 100% of invalid IDs are rejected with explicit validation messages and zero credential leakage.
- **SC-003**: At least 98% of transliterations produce deterministic, lowercase handles that match downstream directory requirements.
- **SC-004**: Incident response reviews confirm that every request (success or failure) appears in audit logs within 1% timestamp drift.

## Assumptions

1. National ID inputs follow the GB 11643-1999 18-digit standard; shorter legacy IDs are out of scope.
2. Name transliteration leverages the organization’s existing pinyin library; tone marks are removed and spaces converted to nothing (e.g., “张 三” → `zhangsan`).
3. Generated passwords are transient: downstream systems will persist and rotate them, so the MCP server does not store plaintext secrets beyond the response lifecycle.
4. The MCP runtime will be deployed with Python 3.12+ and fastapi-mcp per product direction, but this specification remains implementation-agnostic.
