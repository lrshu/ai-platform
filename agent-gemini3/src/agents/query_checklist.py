from src.llm import get_llm

from langchain_core.messages import HumanMessage
from src.state import AgentState
from src.tools import get_checklist, get_json


# LLM 初始化代码
llm = get_llm()


async def query_checklist_node(state: AgentState):
    checklist = get_checklist(state)
    checklist_str = get_json(checklist)

    prompt = f"""员工入职的检查列表如下：
检查列表：
    - first_chat: 与员工首次互动
    - id_verified: 员工是否已验证 ID，员工上传身份证照片，使用 VL 模型验证照片是否正确，并提取身份信息
    - info_collected: 员工是否已提供必要信息，包括毕业学校、岗位（行政、 IT）
    - permissions_granted: 员工是否已开通邮箱账号权限，git 账号权限
    - final_briefing: 员工是否已完成最终介绍
当前的检查列表状态：{checklist_str}
请整理检查列表，以便于阅读的格式输出检查列表状态信息，能很好的区分已完成和未完成的任务。
"""
    resp = await llm.ainvoke([HumanMessage(content=prompt)])
    return {"messages": [resp],
             "next_step": "END"
    }