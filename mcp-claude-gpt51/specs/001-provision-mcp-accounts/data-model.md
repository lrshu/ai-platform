# Data Model — MCP Account Provisioning

## Overview
This document captures the core entities, invariants, and relationships for the MCP Account Provisioning feature. Entities draw from the feature specification and phase-0 research to ensure deterministic handles, compliant passwords, and auditable flows.

---

## IdentitySubmission

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Full Chinese name provided by the requester; must contain only Hanzi and common separators. |
| `national_id` | string (18 chars) | GB 11643-1999 Resident Identity Card number. |
| `name_pinyin` | string (derived) | Lowercase, ASCII-only transliteration with spaces removed. |
| `request_type` | enum | See **Enumerations** section (`email`, `git`). |

### Validation Rules
1. **Name Sanitization**
   - Reject digits, punctuation, or unsupported symbols; instruct HR updates if necessary.
   - Enforce deterministic transliteration using `pypinyin` (`Style.NORMAL`, `heteronym=False`, `strict=True`); fail fast on unrecognized Hanzi.
2. **National ID Validation**
   - Exactly 18 characters; first 17 numeric, final digit numeric or `X/x`.
   - Enforce GB 11643-1999 structure:
     - Address code (first six digits) must exist in current GB/T 2260 tables.
     - Birthdate (YYYYMMDD) must be a valid calendar date, including leap years.
     - Sequence code (digits 15-17) cannot be `000`.
     - Checksum uses weight table `[7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]` and parity map `['1','0','X','9','8','7','6','5','4','3','2']`.
3. **Request Type Validation**
   - Must match supported enum values; case-insensitive input normalized to lowercase.

### Derived Properties
- `name_pinyin`: generated during validation; deterministic for identical inputs.
- `masked_id`: computed for logging (`first 3 digits + **** + last 4`); reused by `AuditRecord`.

---

## ProvisioningResponse

| Field | Type | Description |
| --- | --- | --- |
| `account_type` | enum | Mirrors `request_type` (email or git). |
| `handle` | string | Deterministic `{name_pinyin}@domain`, domain varies by account type. |
| `generated_password` | string | 16-character secret meeting password policy. |
| `timestamp` | ISO 8601 datetime | UTC issuance time. |
| `audit_id` | UUID | Correlates response with `AuditRecord`. |
| `status_code` | string/int | Machine-readable outcome (e.g., `EMAIL_ISSUED`, `INVALID_ID`). |

### Invariants
1. **Deterministic Handles**
   - Email handle: `{name_pinyin}@email.com`
   - Git handle: `{name_pinyin}@git.com`
   - Same `IdentitySubmission` + `request_type` always yields identical handle; passwords remain fresh per request.
2. **Password Policy**
   - Length 16, generated via `secrets.choice`.
   - Charset: `A-Z`, `a-z`, `0-9`, symbols `@ # % + = !`.
   - Must include at least one character from each class (upper, lower, digit, symbol).
3. **Response Integrity**
   - `audit_id` unique per request.
   - `status_code` aligned with localization strategy (human-readable message accompanies it).

---

## AuditRecord

| Field | Type | Description |
| --- | --- | --- |
| `audit_id` | UUID | Primary key; matches `ProvisioningResponse.audit_id`. |
| `masked_id` | string | Masked version of `national_id` (`XXX***********YYYY`). |
| `request_type` | enum | Mirrors originating submission. |
| `outcome` | enum | `success`, `validation_error`, `system_error`. |
| `created_at` | ISO 8601 datetime | Log timestamp (UTC). |

### Logging Requirements
- All requests—successful or failed—must emit an `AuditRecord`.
- Store only masked identifiers; never log plaintext passwords.
- Ensure timestamp drift ≤1% relative to response timestamp (Success Criterion SC-004).

---

## Relationships

| Source | Target | Cardinality | Notes |
| --- | --- | --- | --- |
| `IdentitySubmission` | `ProvisioningResponse` | 1 : 1 per processed request | Deterministic handle ensures idempotence; repeated requests generate new passwords but identical handles. |
| `IdentitySubmission` | `AuditRecord` | 1 : 1 per request | `audit_id` links response and audit log. |
| `ProvisioningResponse` | `AuditRecord` | 1 : 1 | Audit stores masked data for the same issuance. |

---

## Enumerations

### `request_type`
| Value | Description |
| --- | --- |
| `email` | Provisions corporate email account with `@email.com` domain. |
| `git` | Provisions Git credentials with `@git.com` handle suffix. |

### `outcome`
| Value | Description |
| --- | --- |
| `success` | Credentials issued without validation errors. |
| `validation_error` | Input failed ID/name/request-type checks; no credentials generated. |
| `system_error` | Infrastructure/config issue (e.g., missing env vars); request aborted.

---

## Invariants & Policies Summary
1. **Deterministic Transliteration**: identical `name` input results in identical `name_pinyin`; no best-effort guesses.
2. **Deterministic Handles**: handle equals `{name_pinyin}@domain`; no randomness.
3. **Password Policy**: 16 characters, all four character classes, cryptographically secure randomness, regenerated for every successful request.
4. **Validation Before Issuance**: credentials are generated only after all IdentitySubmission validations pass.
5. **Audit Completeness**: every request produces an `AuditRecord` with masked IDs and correlating `audit_id`.
6. **Config Fail-Fast**: missing required environment values prevents server start; no partial provisioning.
