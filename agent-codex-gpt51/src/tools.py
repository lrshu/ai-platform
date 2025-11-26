"""Tools exposed to agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from langchain.tools import BaseTool
from langchain_core.tools import tool

from .models import AccountInfo, EmployeeProfile


class EmailProvisioner(Protocol):
    def create_account(self, name: str) -> str: ...


class GitProvisioner(Protocol):
    def create_account(self, name: str) -> str: ...


@dataclass
class FakeEmailProvisioner:
    """Simple stub for email account creation."""

    domain: str = "example.com"

    def create_account(self, name: str) -> str:
        username = name.lower().replace(" ", ".")
        return f"{username}@{self.domain}"


@dataclass
class FakeGitProvisioner:
    """Simple stub for git account creation."""

    host: str = "git.example.com"

    def create_account(self, name: str) -> str:
        username = name.lower().replace(" ", "-")
        return f"git://{self.host}/{username}"


def build_account_tool(
    email_provisioner: EmailProvisioner,
    git_provisioner: GitProvisioner,
) -> BaseTool:
    """Return a tool that provisions accounts based on the employee role."""

    @tool("provision_accounts")
    def provision_accounts(profile: EmployeeProfile) -> AccountInfo:
        """根据员工信息开通邮箱或 git 账号，返回账号信息。"""

        email_account = None
        git_account = None
        if profile.role == "行政":
            email_account = email_provisioner.create_account(profile.full_name)
        elif profile.role == "IT":
            git_account = git_provisioner.create_account(profile.full_name)

        return AccountInfo(
            email_account=email_account,
            git_account=git_account,
            instructions="账号创建成功，首次登录请修改密码。",
        )

    return provision_accounts
