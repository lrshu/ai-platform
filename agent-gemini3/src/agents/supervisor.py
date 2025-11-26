from langchain_core.messages import SystemMessage,AIMessage
from src.state import AgentState
from src.llm import get_llm
from src.tools import get_checklist, get_json




llm = get_llm()

async def supervisor_node(state: AgentState):
    """入职主管：规划流程"""
    checklist = get_checklist(state)
    messages = state.get("messages", [])
    # 根据 messages 和 checklist 确定下一个节点
    system_prompt = """
    你是一个入职主管，负责规划入职流程。根据当前聊天的上下文信息和当前的检查列表，确定下一个需要执行的节点。
    检查列表：
    - first_chat: 与员工首次互动
    - id_verified: 员工是否已验证 ID，员工上传身份证照片，使用 VL 模型验证照片是否正确，并提取身份信息
    - info_collected: 员工是否已提供必要信息，包括毕业学校、岗位（行政、 IT）
    - permissions_granted: 员工是否已开通邮箱账号权限，git 账号权限
    - final_briefing: 员工是否已完成最终介绍
    可选的执行节点：
    - first_chat: 与员工首次互动
    - id_verifier: 验证员工 ID
    - info_collector: 收集员工必要信息
    - permissions_granted: 员工是否已开通邮箱账号权限，git 账号权限
    - final_briefing: 完成最终介绍
    - query_checklist: 查询检查列表
    - others: 其他情况，如需要与员工互动
    以 JSON 格式返回,返回示例：
    {
        "guide_msg": "请上传您的身份证照片以便核验身份。",
        "next_step": "first_chat"
    }
    """

    messages.append(SystemMessage(content=system_prompt))


    # 调用 LLM 生成下一个节点
    response = await llm.ainvoke(
        messages
    )
    next_json = get_json(response.content)
    # Supervisor 总是把 next_step 写入状态，供路由使用
    return {"messages": [AIMessage(content=next_json["guide_msg"])], "checklist": checklist, "next_step": next_json["next_step"]}
