# Phase 0 Research — MCP Account Provisioning Server

## Chinese National ID Validation Algorithm
- **Decision:** Implement GB 11643-1999 18-digit validation with region-date-body checksum enforcement, using the official weight table `[7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]` and parity map `['1','0','X','9','8','7','6','5','4','3','2']`. Treat the final character case-insensitively and reject any input whose address code, birthdate (including leap-year Feb 29), sequence digits, or checksum fail validation.
- **Rationale:** GB 11643-1999 is the authoritative specification for PRC Resident Identity Cards. Enforcing structured validation (address code range, YYYYMMDD date with calendar check, sequence code not “000”, checksum parity) ensures FR-002 compliance and prevents issuing credentials for malformed records. The checksum map guarantees a deterministic, auditable failure mode.
- **Alternatives considered:**
  - Length-only or regex checks (insufficient; cannot detect checksum or calendar errors).
  - Third-party API lookups (adds latency, privacy exposure, and external dependencies; unnecessary for deterministic local validation).
  - Accepting 15-digit legacy IDs (explicitly out of scope per spec assumptions).

## Deterministic Transliteration Rules
- **Decision:** Use `pypinyin` with `Style.NORMAL`, `heteronym=False`, and `strict=True`, feeding a `pypinyin.contrib.tone_convert.TONE2` blacklist to force neutral-tone output, then collapse spaces and digits to produce lowercase ASCII handles. For rare or unrecognized Hanzi, configure the `errors='default'` hook to raise a validation error; optionally supplement with a custom mapping dictionary maintained in `server/transliteration.py`.
- **Rationale:** `pypinyin` is production-proven, supports deterministic transliteration, and handles polyphonic characters when heteronyms are disabled. The strict mode fails fast on symbols, aligning with FR-003 and UX consistency principles. Maintaining a custom override table covers uncommon corporate names while remaining auditable.
- **Alternatives considered:**
  - `xpinyin` / `pinyin-jyutping` libraries (smaller surface but lack strict failure hooks and strong heteronym controls).
  - Rolling a bespoke transliteration mapping (high maintenance and risks divergence from linguistic standards).
  - Allowing fallback initials or phonetic guesses (would violate deterministic handle requirement and complicate auditing).

## Secure Password Generation for Onboarding Credentials
- **Decision:** Generate 16-character passwords using `secrets.choice` over an allowed charset of uppercase letters `A-Z`, lowercase `a-z`, digits `0-9`, and the symbols `@#%+=!` (ASCII-safe). Enforce presence of at least one character from each required class and rely on `secrets.SystemRandom` (via the `secrets` module) for cryptographically secure randomness. Document alignment with NIST SP 800-63B guidance and log only masked hashes.
- **Rationale:** A 16-character length with diverse charset exceeds FR-005 minimums and follows OWASP ASVS 9.4 + NIST SP 800-63B recommendations for memorized secrets. Using `secrets` ensures entropy sourced from `/dev/urandom`. Explicit post-generation checks guarantee compliance while maintaining deterministic failure handling.
- **Alternatives considered:**
  - `random` module (not cryptographically secure—fails compliance).
  - Shorter 12-character passwords (meets spec’s floor but offers less entropy).
  - Including the full punctuation set (increases confusion and risk of downstream system incompatibility; chosen subset balances security with compatibility).

## Integration Testing Strategy for `fastapi-mcp` Tools
- **Decision:** Use `pytest` + `anyio` with `fastapi-mcp` TestServer utilities and `httpx.AsyncClient` to exercise both MCP tools end-to-end. Spin up the FastAPI app via lifespan context, invoke tool handlers through MCP JSON-RPC envelopes, and assert on responses, error codes, and logs. Mock environment variables via `pytest-env` fixtures, and capture log output using `caplog` to verify audit entries.
- **Rationale:** This mirrors real MCP interactions, satisfying Constitution Principle II (tests first) and Success Criteria SC-001/SC-002. `httpx.AsyncClient` integrates cleanly with FastAPI’s ASGI app, and `anyio` provides concurrency compatibility. Logging assertions ensure compliance with FR-007.
- **Alternatives considered:**
  - Unit-testing tool functions in isolation (faster but misses wiring, authentication hooks, and lifecycle bugs).
  - Manual MCP client tests (good for smoke checks but unsuitable for automated regression suites).
  - Starlette TestClient (sync) (simpler but blocks async-only code paths and MCP streaming features).

## Remaining Risks / Follow-ups
1. **Regional code maintenance:** Need up-to-date GB/T 2260 tables to validate the first six digits; schedule periodic refresh or embed the latest release and document update cadence.
2. **Rare character transliteration:** Coordinate with HR to collect edge-case names and expand the custom mapping table before launch.
3. **Password policy alignment:** Confirm downstream email/Git systems accept the chosen symbol subset; adjust charset if stronger restrictions exist.
4. **Integration test harness drift:** `fastapi-mcp` testing utilities may lag behind framework updates—pin versions in `pyproject.toml` and add smoke tests in CI to detect breaking changes early.
