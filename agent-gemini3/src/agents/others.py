from src.llm import get_llm
from src.state import AgentState


# LLM 初始化代码
llm = get_llm()


async def others_node(state: AgentState):
    # 线上入职结束，提醒员工需完成的后续任务，包括领取工牌、找部门领导汇报、参加入职培训等；
    messages = state["messages"]
    resp = await llm.ainvoke(messages)
    return {"messages": [resp],
             "next_step": "END"
    }