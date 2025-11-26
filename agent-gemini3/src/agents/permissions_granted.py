from src.llm import get_llm, get_agent_with_tools
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState


# LLM 初始化代码
llm = get_llm()


async def permissions_granted_node(state: AgentState):
    info = state.get("employee_info", {})
    position = info.get("position")
    prompt = ""
    if not position:
        return {"messages": [AIMessage(content="请先填写您的岗位（行政/ IT）。")],
                "next_step": "info_collector"}
    if position.lower() == "行政":
        prompt = f"您是行政岗位的员工，将申请邮箱账号权限, 调用邮件账号申请工具，姓名：{info.get('name')}， 身份证号：{info.get('id_number')}"
    elif position.lower() == "it":
        prompt = f"您是 IT 岗位的员工，将申请git账号权限, 调用git账号申请工具，姓名：{info.get('name')}， 身份证号：{info.get('id_number')}"
    agent = await get_agent_with_tools(llm)
    final_state = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
    last_message = final_state["messages"][-1]
    return {"messages": [last_message],
             "checklist": {**state["checklist"], "permissions_granted": True},
             "next_step": "final_briefing"
    }