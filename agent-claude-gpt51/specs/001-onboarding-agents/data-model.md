# Data Model — New Hire Onboarding Multi-Agent Backend

## Entities

### OnboardingSession
- **Fields**: `id` (UUID), `employee_id`, `status` (enum: pending_identity, pending_profile, pending_role_briefing, pending_access, completed), `current_step`, `checklist_state` (JSON), `language_pref`, `created_at`, `updated_at`, `transcript_ref`
- **Relationships**: 1:1 with EmployeeProfile; 1:many with ChecklistItem snapshots; 1:many with AccountProvisioningRequest
- **Rules**:
  - Status transitions must follow defined order; cannot skip identity verification.
  - Checklist state must update atomically with the corresponding agent completion event.
  - Transcript reference retained for at least audit duration defined by HR.

### EmployeeProfile
- **Fields**: `id` (UUID), `session_id`, `legal_name`, `id_number` (encrypted), `birth_date`, `university`, `degree_level` (enum), `desired_role`, `role_brief_id`, `identity_image_path` (temp), `validated_at`
- **Relationships**: Belongs to OnboardingSession; references RoleKnowledgeAsset for `role_brief_id`.
- **Rules**:
  - Identity data cannot persist image path longer than 24h; cleanup job removes file once validated.
  - Degree level must come from allowed list [Associate, Bachelor, Master, Doctorate, Other].
  - Desired role must map to role taxonomy; otherwise fallback to generic brief and flag.

### ChecklistItem
- **Fields**: `id` (UUID), `session_id`, `step` (enum), `status` (pending/in_progress/completed/blocked), `completed_by_agent`, `completed_at`, `notes`
- **Relationships**: Belongs to OnboardingSession.
- **Rules**:
  - Only supervisor agent can create/update checklist beyond its own step.
  - Blocked status requires `notes` describing reason and next action.

### RoleKnowledgeAsset
- **Fields**: `id`, `role_key`, `language`, `responsibility_summary`, `post_tasks`, `last_reviewed_by`
- **Relationships**: Referenced by EmployeeProfile and Q&A agent.
- **Rules**:
  - Must maintain bilingual entries; when entry missing, fallback to default `zh-CN` + `en-US` copy.
  - Updates require `last_reviewed_by` to ensure traceability.

### AccountProvisioningRequest
- **Fields**: `id`, `session_id`, `role_key`, `tool_name` (email_provisioner/git_provisioner), `payload`, `result`, `status`, `credential_reference`, `requested_at`, `completed_at`
- **Relationships**: Belongs to OnboardingSession; optionally references stored credential vault entry.
- **Rules**:
  - Tool name derived from role taxonomy mapping; cannot trigger both email and git unless role requires.
  - Result payload stored after scrubbing secrets; actual credentials referenced via secure vault pointer.

### QAInteractionLog
- **Fields**: `id`, `session_id`, `question`, `answer`, `source_reference`, `responded_at`
- **Relationships**: Belongs to OnboardingSession; sources include role assets, checklist copy, or policy docs.
- **Rules**:
  - Questions tagged with topic (identity/profile/access/post_onboarding) for analytics.
  - Logs must respect localization preference.

## State Transitions

1. **Session Creation** → status `pending_identity`, checklist seeded with all steps pending.
2. **Identity Verified** → status `pending_profile`, update EmployeeProfile with extracted data, mark checklist item completed.
3. **Profile Completed** → status `pending_role_briefing`, trigger RoleKnowledgeAsset lookup and store summary reference.
4. **Brief Delivered** → status `pending_access`, ensure role responsibilities stored in transcript.
5. **Provisioning Complete** → status `completed` once tooling agent returns credentials; supervisor sends offline reminders.
6. **Blocked Flow** → any failure marks corresponding checklist item `blocked` with instructions; session stays in same status until resolved.
