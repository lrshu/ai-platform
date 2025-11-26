from src.llm import get_llm
from src.state import AgentState
from langgraph.types import interrupt

import os

# LLM 初始化代码
llm = get_llm() 

async def info_collector_node(state: AgentState):
    info = state.get("employee_info", {})
    if not info.get("school"):
        school = interrupt("请填写您的毕业院校：")
        info["school"] = school
    if not info.get("position"):
        position = interrupt("请填写您的岗位（行政/ IT）：")
        while position.lower() not in ["行政", "it"]:
            position = interrupt("请输入行政或 IT 岗位：")
        info["position"] = position
        
    # Fallback
    return {"checklist": {**state["checklist"], "info_collected": True}, "employee_info": info, "next_step": "permissions_granted"}
