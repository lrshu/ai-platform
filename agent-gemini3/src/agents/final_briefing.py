from src.llm import get_llm
from langchain_core.messages import HumanMessage
from src.state import AgentState


# LLM 初始化代码
llm = get_llm()


async def final_briefing_node(state: AgentState):
    # 线上入职结束，提醒员工需完成的后续任务，包括领取工牌、找部门领导汇报、参加入职培训等；
    prompt = "员工线上入职结束，帮我生成一段话，提醒员工需完成的后续任务，包括领取工牌、找部门领导汇报、参加入职培训等；"
    resp = await llm.ainvoke([HumanMessage(content=prompt)])
    return {"messages": [resp],
             "checklist": {**state["checklist"], "final_briefing": True},
             "next_step": "END"
    }