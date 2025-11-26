"""Domain services that power the onboarding workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import AccountInfo, EmployeeProfile, IdentityDocument, RoleBriefing
from .tools import (
    FakeEmailProvisioner,
    FakeGitProvisioner,
    provision_accounts,
)

ROLE_LIBRARY: dict[tuple[str, str], dict[str, Any]] = {
    ("行政", "人事专员"): {
        "summary": "负责支持企业日常行政管理与员工服务，保障组织高效运转。",
        "responsibilities": [
            "办理入转调离手续，维护员工档案",
            "协调会议、差旅及办公资源",
            "落地各项行政制度与费用控制",
        ],
        "probation": ["独立完成 3 场全流程入职安排", "完成行政资产盘点并输出改进建议"],
    },
    ("IT", "后端工程师"): {
        "summary": "设计与实现核心服务，保障平台稳定与扩展性。",
        "responsibilities": [
            "负责业务模块的架构与编码实现",
            "编写自动化测试，保障质量",
            "持续优化性能与上线流程",
        ],
        "probation": ["上线 1 个核心功能迭代", "编写 10+ 条监控与应急预案"],
    },
}

MANDATORY_FOLLOWUPS = ["领取工牌", "向部门领导汇报", "参加入职培训"]


def verify_identity(payload: dict[str, Any]) -> IdentityDocument:
    image_path = payload.get("image_path", "").strip()
    name = payload.get("full_name", "").strip()
    id_number = payload.get("id_number", "").strip()

    suffix_valid = Path(image_path).suffix.lower() in {".png", ".jpg", ".jpeg"}
    id_valid = len(id_number) == 18 and id_number[:-1].isdigit()
    is_valid = bool(name) and suffix_valid and id_valid
    feedback = "验证通过" if is_valid else "照片或证件号存在问题，请重新上传清晰正面图，并确认 18 位身份证号。"

    return IdentityDocument(
        image_path=image_path or "未提供",
        extracted_name=name or "未知",
        extracted_id_number=id_number or "未知",
        is_valid=is_valid,
        feedback=feedback,
    )


def build_profile(payload: dict[str, Any], identity: IdentityDocument | None) -> EmployeeProfile:
    profile = EmployeeProfile(**payload)
    if identity and identity.extracted_name not in {"未知", profile.full_name}:
        raise ValueError("身份证姓名与填写信息不一致")
    if identity and identity.extracted_id_number not in {"未知", profile.id_number}:
        raise ValueError("身份证号与填写信息不一致")
    return profile


def describe_role(profile: EmployeeProfile) -> RoleBriefing:
    key = (profile.role, profile.position)
    config = ROLE_LIBRARY.get(key)
    if not config:
        config = {
            "summary": f"{profile.position} 需配合 {profile.role} 团队完成年度目标。",
            "responsibilities": [
                "熟悉团队交付流程",
                "根据 mentor 计划完成指定任务",
                "沉淀复盘材料并推动持续优化",
            ],
            "probation": ["按计划输出阶段成果", "完成不少于 2 次复盘"],
        }
    return RoleBriefing(
        position=profile.position,
        summary=config["summary"],
        responsibilities=config["responsibilities"],
        probation_goals=config["probation"],
    )


def open_access(profile: EmployeeProfile) -> AccountInfo:
    return provision_accounts(
        profile,
        email_provisioner=FakeEmailProvisioner(),
        git_provisioner=FakeGitProvisioner(),
    )


def answer_question(question: str, profile: EmployeeProfile | None, briefing: RoleBriefing | None) -> str:
    base = "线上流程已完成。" if profile else "需要先完成基础信息填写。"
    details = []
    if briefing:
        details.append(f"当前岗位：{briefing.position}，需聚焦 {briefing.responsibilities[0]}。")
    details.append("如需帮助，可随时联系 HRBP。")
    return base + " " + " ".join(details) + f" 员工问题：{question}"


def build_followup_tasks(profile: EmployeeProfile | None) -> list[str]:
    tasks = list(MANDATORY_FOLLOWUPS)
    if profile:
        if profile.role == "IT":
            tasks.append("完成开发环境与代码仓库自测")
        else:
            tasks.append("与行政负责人确认物资领用")
    return tasks
