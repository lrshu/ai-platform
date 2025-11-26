"""CLI runtime wiring for onboarding workflow."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_core.messages import BaseMessage, SystemMessage

from .agents import (
    create_access_agent,
    create_followup_agent,
    create_identity_agent,
    create_info_agent,
    create_onboarding_agent,
    create_role_brief_agent,
)
from .checklist import Checklist, ChecklistItem
from .models import AccountInfo, EmployeeProfile, IdentityDocument, RoleBriefing
from .services import (
    answer_question,
    build_followup_tasks,
    build_profile,
    describe_role,
    open_access,
    verify_identity,
)
from .state import OnboardingState
from .tools import FakeEmailProvisioner, FakeGitProvisioner, build_account_tool


class InMemorySession:
    """Simplified orchestrator that mimics a conversation loop."""

    def __init__(self) -> None:
        self.state = OnboardingState(
            identity=None,
            profile=None,
            accounts=None,
            checklist=Checklist(),
            messages=[],
        )
        self.identity_agent = create_identity_agent()
        self.info_agent = create_info_agent()
        self.role_agent = create_role_brief_agent()
        self.access_agent = create_access_agent(
            tools=[
                build_account_tool(FakeEmailProvisioner(), FakeGitProvisioner()),
            ]
        )
        self.followup_agent = create_followup_agent()
        self.supervisor = create_onboarding_agent()

    def add_message(self, message: BaseMessage) -> None:
        self.state.messages.append(message)


def _prompt_input(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:  # pragma: no cover - defensive CLI guard
        return ""


def run_cli() -> None:
    session = InMemorySession()
    print("欢迎来到智能入职助手，按照提示完成流程。")

    # Identity verification mock
    image_path = _prompt_input("上传身份证图片路径: ")
    full_name = _prompt_input("身份证姓名: ")
    id_number = _prompt_input("身份证号(18位): ")
    identity = verify_identity(
        {"image_path": image_path, "full_name": full_name, "id_number": id_number}
    )
    session.state.identity = identity
    session.state.checklist.mark_done(ChecklistItem.ID_VERIFICATION)
    print(identity.feedback)

    # Info collection
    university = _prompt_input("毕业院校: ")
    degree = _prompt_input("学历(本科/硕士/博士/专科): ")
    role = _prompt_input("岗位类别(行政/IT): ")
    position = _prompt_input("具体岗位: ")
    profile = build_profile(
        {
            "full_name": full_name,
            "id_number": id_number,
            "university": university,
            "degree": degree,
            "role": role,
            "position": position,
        },
        identity,
    )
    session.state.profile = profile
    session.state.checklist.mark_done(ChecklistItem.INFO_COMPLETION)

    # Role briefing
    briefing = describe_role(profile)
    session.state.checklist.mark_done(ChecklistItem.ROLE_BRIEFING)
    print("岗位简介:", briefing.summary)
    print("核心职责:")
    for item in briefing.responsibilities:
        print("-", item)
    print("试用期目标:")
    for goal in briefing.probation_goals:
        print("-", goal)

    # Access setup
    accounts = open_access(profile)
    session.state.accounts = accounts
    session.state.checklist.mark_done(ChecklistItem.ACCESS_SETUP)
    if accounts.email_account:
        print("邮箱账号:", accounts.email_account)
    if accounts.git_account:
        print("git 账号:", accounts.git_account)
    print(accounts.instructions)

    # Follow up tasks
    tasks = build_followup_tasks(profile)
    session.state.checklist.mark_done(ChecklistItem.FINAL_GUIDANCE)
    print("线下待办:")
    for task in tasks:
        print("-", task)

    print("流程已完成，感谢配合！")
