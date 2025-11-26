from src.llm import get_llm
from src.tools import get_checklist
from src.state import AgentState

# LLM 初始化代码
llm = get_llm()

async def first_chat_node(state: AgentState):
    # 给出入职说明和待处理的 checklist
    prompt = "写一段入职说明，包括需要提供的信息和需要完成的任务，用户需完成的checklist包括： 身份验证，个人信息填写，开通账号， 引导用户执行下一步操作。"
    resp = llm.invoke(prompt)
    next_step = "id_verifier"
    # 更新 checklist
    checklist = get_checklist(state)
    checklist["first_chat"] = True
    return {
        "messages": [resp],
        "next_step": next_step,
        "checklist": checklist
    }