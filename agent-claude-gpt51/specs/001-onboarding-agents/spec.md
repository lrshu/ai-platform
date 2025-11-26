# Feature Specification: New Hire Onboarding Multi-Agent Backend

**Feature Branch**: `001-onboarding-agents`
**Created**: 2025-11-25
**Status**: Draft
**Input**: User description:
```
create feature agent backend specify

构建一个简单的标准化的 新员工入职引导多智能体 后端系统，使用 langchain 下的 deepagents 作为整体框架

# 员工入职流程

1. 员工身份验证：员工需上传身份证照片；
2. 员工信息完善：包括毕业院校填写，学历选择，岗位选择；
3. 宣讲岗位职责：根据员工信息和选择的岗位，检索输出对应的岗位职责；
4. 开通权限： 行政岗位开通邮箱账号权限， IT 开发人员开通 git 账号权限，返回开通后的账号信息；
5. 线上入职结束，提醒员工需完成的后续任务，包括领取工牌、找部门领导汇报、参加入职培训等；

# 核心智能体角色说明

为保证智能体完成以上入职流程，规划以下角色， 每个角色一个智能体

1. 入职主管: 主智能体，负责规划和流转，员工提出入职申请时，给出入职说明和待处理的 checklist， 维护 Checklist 状态， 并可随时查看当前 checklist 状态，引导用户继续完成
2. 身份验证: 引导员工上传身份证照片，使用 VL 模型验证照片是否正确，并提取身份信息，如果不正确，提示如何修正并重新上传
3. 信息收集：一步一步引导员工填写相应的信息，比验证输入是否正确，如果错误，给出提示并引导用户重新输入
4. 工具调用：MCP 工具调用智能体，根据需要，确定调用的工具，包括开通邮箱账号权限、开通 git 账号权限登工具
5. 问题解答：问题解答智能体，根据需要，回答员工的提问，包括入职说明、岗位职责说明、后续任务说明等

# 技术栈

如果没有指定使用的技术方向，优先使用 deepagents 体系下的方式实现后续功能

- **Runtime**: Python 3.12+ (uv)
- **Framework**: deepagents
- **LLM**: qwen3-max, qwen3-vl-max

# 定义配置 .env

```env
# QWen Configuration
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY="sk-**"
MCP_SERVER="http://127.0.0.1:9012/mcp"

# Langsmith
LANGSMITH_API_KEY="**"
LANGSMITH_PROJECT="default"
```

## main.py

python main.py chat : 启动 langraph 智能体，开始聊天对话
```

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Guided onboarding kickoff (Priority: P1)

A newly hired employee starts the onboarding chat, receives a concise explanation of the process, and sees a live checklist that tracks which steps remain.

**Why this priority**: Every onboarding must begin with clear guidance and transparency about required actions, so this flow unlocks all others.

**Independent Test**: Initiate a fresh onboarding session, confirm the supervisor agent introduces the program, populates an initial checklist, and allows the employee to view checklist status without completing later steps.

**Acceptance Scenarios**:

1. **Given** a new hire enters the system, **When** the onboarding supervisor acknowledges the request, **Then** the agent posts an overview plus a checklist containing identity, profile, responsibilities, access, and wrap-up tasks.
2. **Given** the employee asks for status later, **When** the supervisor agent is queried, **Then** it returns the current completion state for each checklist item.

---

### User Story 2 - Identity verification and correction (Priority: P2)

The identity agent walks the employee through uploading an ID photo, validates it using a multimodal model, extracts legal data, and loops until a valid image is provided.

**Why this priority**: Legal identity verification is a compliance gate that must succeed before HR data can be trusted.

**Independent Test**: Provide sample photos (valid and invalid) and confirm the agent can detect issues, offer actionable feedback, and store extracted identity details once a valid upload is processed.

**Acceptance Scenarios**:

1. **Given** the employee uploads a clear ID photo, **When** the VL model validates it, **Then** the system stores the extracted name, ID number, and birth date while marking the checklist item complete.
2. **Given** the photo is cropped or unreadable, **When** validation fails, **Then** the agent explains the reason (e.g., glare) and prompts for a corrected upload without progressing the checklist.

---

### User Story 3 - Profile data collection and role briefing (Priority: P3)

After identity confirmation, the information collection agent asks for school, degree, and desired role, validates entries, and triggers the knowledge agent to summarize role responsibilities tailored to the input.

**Why this priority**: Accurate personal and role data enables downstream provisioning and ensures employees understand expectations.

**Independent Test**: Simulate data entry with valid and invalid values, ensuring validation feedback works and that a role-specific responsibility brief is delivered without invoking access provisioning.

**Acceptance Scenarios**:

1. **Given** the employee enters a school name outside allowed characters, **When** validation runs, **Then** the agent rejects the entry and provides formatting guidance.
2. **Given** the employee selects a defined role (e.g., IT developer), **When** the role briefing agent runs, **Then** it retrieves the correct responsibility summary and confirms delivery in chat.

---

### User Story 4 - Access provisioning and wrap-up (Priority: P4)

Once role data is captured, the tooling agent determines required account openings, invokes MCP tools to provision email or Git access, returns credentials, and the supervisor agent summarizes remaining offline tasks.

**Why this priority**: Providing working accounts and summarizing next steps marks the completion of digital onboarding and hands off to physical tasks.

**Independent Test**: Trigger the provisioning stage independently with mock MCP responses to confirm correct tool selection per role and that the final reminder list appears even if certain tools fail.

**Acceptance Scenarios**:

1. **Given** an administrative hire reaches provisioning, **When** the MCP email tool succeeds, **Then** the agent shares the new mailbox details and marks the checklist item complete.
2. **Given** an IT developer requires Git access, **When** the MCP Git tool returns credentials, **Then** the agent stores and displays them securely before presenting the offline task reminder list.

### Edge Cases

- ID photo is repeatedly rejected due to lighting or document mismatch; system must escalate with clearer instructions after multiple failures.
- Employee selects a role that lacks predefined responsibilities; system should default to a generic role brief and flag HR to update templates.
- MCP tool invocation fails or times out; tooling agent must retry with backoff and escalate to manual support if still unsuccessful.
- Employee drops the session mid-way; supervisor agent should preserve checklist state and resume on next login without data loss.
- Uploaded data conflicts (e.g., role choice incompatible with degree); information agent should prompt for confirmation or correction before proceeding.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The onboarding supervisor agent MUST initialize every session with process guidance and a multi-step checklist visible to the employee.
- **FR-002**: The system MUST accept government ID image uploads and store them securely for validation during the session.
- **FR-003**: The identity agent MUST run multimodal verification on each upload, extract legal name, ID number, and birth date, and attach results to the employee profile.
- **FR-004**: When verification fails, the identity agent MUST provide actionable correction tips (e.g., recapture angle, reduce glare) before allowing another attempt.
- **FR-005**: The information collection agent MUST gather graduation institution, degree level (e.g., bachelor, master), and desired role using field-specific validation rules.
- **FR-006**: The knowledge agent MUST retrieve and deliver a role responsibility summary that matches the collected role selection and employee attributes.
- **FR-007**: The onboarding system MUST maintain real-time checklist state, reflecting completion or pending status for each major step across the chat session.
- **FR-008**: The tooling agent MUST decide which MCP tooling operations to call based on role (e.g., email provisioning for administrative roles, Git for IT roles).
- **FR-009**: The system MUST capture and relay resulting account identifiers or credentials from MCP tooling back to the employee with confirmation of successful provisioning.
- **FR-010**: The question-answering agent MUST respond to employee inquiries about onboarding steps, role expectations, and post-onboarding tasks using up-to-date knowledge sources.
- **FR-011**: Upon completion of digital tasks, the supervisor agent MUST remind the employee of pending offline actions such as badge pickup, meeting the department lead, and training attendance, logging the reminder.
- **FR-012**: The system MUST log all agent decisions and MCP tool outcomes for auditability and troubleshooting by HR and IT.

### Key Entities

- **OnboardingSession**: Represents an individual employee’s journey, tracking session ID, employee identifier, current checklist statuses, timestamps, and agent transcripts.
- **EmployeeProfile**: Stores verified identity fields, education history, degree level, selected role, and generated responsibility brief references.
- **ChecklistItem**: Defines each onboarding step (identity, profile, responsibilities, provisioning, wrap-up) with status, timestamp, and actor agent responsible.
- **AccountProvisioningRequest**: Captures role-based tooling needs, invoked MCP tool names, request payloads, responses, and resulting account metadata.
- **RoleKnowledgeAsset**: References curated content describing responsibilities per role, including localized language, prerequisites, and escalation contacts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of employees can complete the entire digital onboarding flow (identity through reminders) within 20 minutes without live human intervention.
- **SC-002**: At least 90% of valid ID photos pass verification on the first or second attempt after following agent guidance.
- **SC-003**: 100% of completed sessions have all checklist items marked with accurate timestamps and associated agent logs for audit review.
- **SC-004**: 95% of employees receive the correct role responsibility brief and required account credentials that match their selected role with no subsequent correction tickets.
- **SC-005**: Post-onboarding survey indicates that 90% of employees report clarity on next offline tasks (badge, manager meeting, training) immediately after the digital flow.

## Assumptions

1. The organization supplies a compliant VL identity verification service capable of extracting text from ID photos in the target language.
2. Role responsibility content and MCP tooling endpoints already exist and can be referenced via deterministic identifiers.
3. Employees interact with the system in Chinese, and all agents can respond bilingually if necessary without additional localization work in this feature.
