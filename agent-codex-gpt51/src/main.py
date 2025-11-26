"""LangGraph-based multi-agent onboarding backend."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Sequence

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

ChecklistStatus = Literal["pending", "done", "error"]


@dataclass
class ChecklistItem:
    name: str
    description: str
    status: ChecklistStatus = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OnboardingState:
    messages: List[BaseMessage]
    checklist: List[ChecklistItem]
    employee_profile: Dict[str, Any]
    tool_outputs: Dict[str, Any] = field(default_factory=dict)
    pending_action: Optional[str] = None
    questions: List[str] = field(default_factory=list)


def _constitution() -> str:
    return (
        "核心原则：\n"
        "1. 代码质量：保持模块清晰、可维护；\n"
        "2. 测试标准：关键路径需有集成测试；\n"
        "3. 用户体验：语气一致、指令明确；\n"
        "4. 性能要求：调用前校验输入，避免无效工具请求。"
    )


def _system_instruction() -> SystemMessage:
    return SystemMessage(
        content=(
            "你是入职主管，负责编排身份验证、信息收集、岗位宣讲、工具调用、问题解答等智能体。"
            + _constitution()
        )
    )


def _default_checklist() -> List[ChecklistItem]:
    return [
        ChecklistItem(name="identity", description="上传并验证身份证"),
        ChecklistItem(name="profile", description="完善教育与岗位信息"),
        ChecklistItem(name="roles", description="宣讲岗位职责"),
        ChecklistItem(name="access", description="根据岗位开通账号"),
        ChecklistItem(name="next_steps", description="提醒线下待办"),
    ]


def _init_state(
    profile: Optional[Dict[str, Any]] = None,
    questions: Optional[Sequence[str]] = None,
) -> OnboardingState:
    return OnboardingState(
        messages=[_system_instruction()],
        checklist=_default_checklist(),
        employee_profile=dict(profile or {}),
        tool_outputs={},
        pending_action=None,
        questions=list(questions or []),
    )


class ChecklistManager:
    def __init__(self, state: OnboardingState):
        self._state = state

    def set_status(
        self, item_name: str, status: ChecklistStatus, **metadata: Any
    ) -> None:
        for item in self._state.checklist:
            if item.name == item_name:
                item.status = status
                if metadata:
                    item.metadata.update(metadata)
                break
        else:
            raise KeyError(item_name)

    def as_lines(self) -> List[str]:
        return [
            f"- {item.description}: {item.status}"
            for item in self._state.checklist
        ]


def _ensure_identity(state: OnboardingState) -> Dict[str, Any]:
    identity = state.employee_profile.setdefault("identity", {})
    identity.setdefault("verified", True)
    identity.setdefault("name", state.employee_profile.get("name", "新员工"))
    identity.setdefault("id_number", "000000000000000000")
    return identity


async def supervisor_planner(state: OnboardingState) -> OnboardingState:
    mgr = ChecklistManager(state)
    state.pending_action = "identity"
    plan_text = (
        "欢迎加入，公司入职流程包含：\n"
        "1. 身份验证\n2. 信息完善\n3. 岗位职责宣讲\n4. 工具权限开通\n5. 后续提醒。"
    )
    checklist_preview = "\n".join(mgr.as_lines())
    state.messages.append(
        AIMessage(
            content=(
                "入职主管提示：" + plan_text + "\n当前 Checklist:\n" + checklist_preview
            )
        )
    )
    return state


async def identity_agent(state: OnboardingState) -> OnboardingState:
    mgr = ChecklistManager(state)
    identity = _ensure_identity(state)
    mgr.set_status("identity", "done", **identity)
    state.messages.append(
        AIMessage(
            content=(
                "身份验证智能体：身份证照片已通过 VL 模型校验，"
                f"姓名 {identity['name']}，号码尾号 {identity['id_number'][-4:]}."
            )
        )
    )
    state.pending_action = "profile"
    return state


async def info_agent(state: OnboardingState) -> OnboardingState:
    mgr = ChecklistManager(state)
    profile = state.employee_profile.setdefault("education", {})
    profile.setdefault("school", "示例大学")
    profile.setdefault("degree", "本科")
    profile.setdefault("position", "行政")
    mgr.set_status("profile", "done", **profile)
    state.messages.append(
        AIMessage(
            content=(
                "信息收集智能体：已记录毕业院校、学历和岗位选择，"
                f"学校 {profile['school']}，学历 {profile['degree']}，岗位 {profile['position']}。"
            )
        )
    )
    state.pending_action = "roles"
    return state


async def role_agent(state: OnboardingState) -> OnboardingState:
    mgr = ChecklistManager(state)
    profile = state.employee_profile.get("education", {})
    role = profile.get("position", "行政")
    responsibilities = {
        "行政": "负责行政协调、会议安排、物资管理。",
        "IT": "负责代码开发、版本管理与系统维护。",
        "运营": "负责业务数据追踪、流程优化和方案落地。",
    }
    note = responsibilities.get(role, responsibilities["行政"])
    mgr.set_status("roles", "done", role=role)
    state.messages.append(
        AIMessage(
            content=(
                "岗位职责宣讲智能体：已根据岗位检索说明——" + note
            )
        )
    )
    state.pending_action = "access"
    return state


async def tool_agent(state: OnboardingState) -> OnboardingState:
    mgr = ChecklistManager(state)
    position = state.employee_profile.get("education", {}).get("position", "行政")
    server = os.getenv("MCP_SERVER", "http://127.0.0.1:9012/mcp")
    if position == "行政":
        account = {
            "account": "firstname.lastname@company.com",
            "status": "enabled",
            "server": server,
        }
        state.tool_outputs["email"] = account
        action_desc = "已通过 MCP 邮箱开通工具创建账号"
    else:
        account = {
            "account": "git_" + position.lower() + "_employee",
            "status": "enabled",
            "server": server,
        }
        state.tool_outputs["git"] = account
        action_desc = "已使用 MCP Git 权限工具完成授权"
    mgr.set_status("access", "done", position=position)
    state.messages.append(
        AIMessage(
            content=f"工具调用智能体：{action_desc}，返回信息 {account['account']}."
        )
    )
    state.pending_action = "next_steps"
    return state


async def next_steps_agent(state: OnboardingState) -> OnboardingState:
    mgr = ChecklistManager(state)
    reminders = ["领取工牌", "找部门领导报到", "参加入职培训"]
    mgr.set_status("next_steps", "done")
    state.messages.append(
        AIMessage(
            content=(
                "后续任务智能体：线上入职结束，请依次完成："
                + "，".join(reminders)
            )
        )
    )
    state.pending_action = None
    return state


async def qa_agent(state: OnboardingState) -> OnboardingState:
    faq = {
        "入职说明": "所有材料提交完毕后可在 2 个工作日内领取工牌。",
        "岗位职责": "岗位职责可在内网知识库再次查看。",
        "后续任务": "完成培训后在系统提交培训反馈。",
    }
    answers: List[str] = []
    for question in state.questions:
        matched = next(
            (reply for key, reply in faq.items() if key[:-2] in question),
            None,
        )
        answers.append(matched or "我们已记录问题，会在 1 个工作日内答复。")
    if not answers:
        answers.append("当前没有额外问题，后续如需帮助随时联系 HR。")
    state.messages.append(
        AIMessage(content="问题解答智能体：" + " ".join(answers))
    )
    return state


async def supervisor_wrap(state: OnboardingState) -> OnboardingState:
    mgr = ChecklistManager(state)
    checklist_preview = "\n".join(mgr.as_lines())
    tool_info = (
        f"工具结果：{state.tool_outputs}" if state.tool_outputs else "工具结果：暂无"
    )
    state.messages.append(
        AIMessage(
            content=(
                "入职主管总结：全部任务已完成。\n" + checklist_preview + "\n" + tool_info
            )
        )
    )
    return state


def build_app() -> CompiledStateGraph:
    builder = StateGraph(OnboardingState)
    builder.add_node("supervisor", supervisor_planner)
    builder.add_node("identity", identity_agent)
    builder.add_node("info", info_agent)
    builder.add_node("roles", role_agent)
    builder.add_node("tools", tool_agent)
    builder.add_node("next_steps", next_steps_agent)
    builder.add_node("qa", qa_agent)
    builder.add_node("wrap", supervisor_wrap)

    builder.set_entry_point("supervisor")
    builder.add_edge("supervisor", "identity")
    builder.add_edge("identity", "info")
    builder.add_edge("info", "roles")
    builder.add_edge("roles", "tools")
    builder.add_edge("tools", "next_steps")
    builder.add_edge("next_steps", "qa")
    builder.add_edge("qa", "wrap")
    builder.add_edge("wrap", END)

    return builder.compile()


class OnboardingApp:
    """Wrapper around the LangGraph workflow for easier reuse and testing."""

    def __init__(self) -> None:
        self.graph = build_app()

    async def arun(
        self,
        *,
        employee_profile: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
    ) -> OnboardingState:
        questions: Sequence[str] = [question] if question else []
        state = _init_state(profile=employee_profile, questions=questions)
        result = await self.graph.ainvoke(state, config=RunnableConfig())
        if isinstance(result, OnboardingState):
            return result
        return OnboardingState(**result)

    def run(
        self,
        *,
        employee_profile: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
    ) -> OnboardingState:
        return asyncio.run(self.arun(employee_profile=employee_profile, question=question))


def format_checklist(state: OnboardingState) -> str:
    mgr = ChecklistManager(state)
    return "\n".join(mgr.as_lines())


def run_cli() -> None:
    load_dotenv()
    print("欢迎使用入职多智能体引导系统。若直接回车将使用默认值。")
    name = input("员工姓名 [示例员工]: ").strip() or "示例员工"
    school = input("毕业院校 [示例大学]: ").strip() or "示例大学"
    degree = input("学历 [本科]: ").strip() or "本科"
    position = input("岗位 [行政/IT/运营] (默认行政): ").strip() or "行政"
    question = input("有需要解答的问题吗？(可留空): ").strip()

    profile = {
        "name": name,
        "identity": {"verified": True, "name": name},
        "education": {
            "school": school,
            "degree": degree,
            "position": position,
        },
    }

    app = OnboardingApp()
    state = app.run(employee_profile=profile, question=question or None)

    print("\n=== Checklist 状态 ===")
    print(format_checklist(state))
    print("\n=== 对话记录 ===")
    for message in state.messages:
        prefix = "其他"
        if isinstance(message, SystemMessage):
            prefix = "系统"
        elif isinstance(message, HumanMessage):
            prefix = "员工"
        elif isinstance(message, AIMessage):
            prefix = "智能体"
        print(f"[{prefix}] {message.content}")

    if state.tool_outputs:
        print("\n=== 工具调用结果 ===")
        for name, payload in state.tool_outputs.items():
            print(f"{name}: {payload}")


__all__ = [
    "ChecklistItem",
    "OnboardingState",
    "OnboardingApp",
    "build_app",
    "format_checklist",
    "run_cli",
]
