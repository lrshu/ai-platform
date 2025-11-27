from langgraph.graph import StateGraph, END, START
from src.state import AgentState
from src.agents import (
    supervisor_node, id_verifier_node, info_collector_node,
    others_node, query_checklist_node, final_briefing_node,
    first_chat_node, permissions_granted_node
)

def build_graph():
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("first_chat", first_chat_node)
    workflow.add_node("id_verifier", id_verifier_node)
    workflow.add_node("info_collector", info_collector_node)
    workflow.add_node("permissions_granted", permissions_granted_node)
    workflow.add_node("final_briefing", final_briefing_node)
    workflow.add_node("others", others_node)
    workflow.add_node("query_checklist", query_checklist_node)




    # 通用路由函数：读取 state["next_step"]
    def route_logic(state):
        return state["next_step"]

    # 1. Start -> Supervisor
    workflow.add_edge(START, "supervisor")

    # 2. Supervisor -> Agents (Supervisor 决定谁干活)
    workflow.add_conditional_edges(
        "supervisor",
        route_logic,
        {
            "supervisor": "supervisor",
            "first_chat": "first_chat",
            "id_verifier": "id_verifier",
            "info_collector": "info_collector",
            "permissions_granted": "permissions_granted",
            "final_briefing": "final_briefing",
            "others": "others",
            "query_checklist": "query_checklist",
            "END": END
        }
    )

    # 3. Agents -> Supervisor OR END (Agents 决定是干完了还是等用户)
    # 所有 Agent 节点都使用相同的路由逻辑
    sequence_nodes = ["first_chat", "id_verifier", "info_collector", "permissions_granted", "final_briefing"]
    for i in range(len(sequence_nodes) - 1):
        workflow.add_conditional_edges(
            sequence_nodes[i],
            route_logic,
            {
                "supervisor": "supervisor",
                sequence_nodes[i+1]: sequence_nodes[i+1],
                "END": END
            }
        )

    return workflow.compile()



graph = build_graph()