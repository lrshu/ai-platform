# 聚合文件：导入所有智能体
from src.agents.supervisor import supervisor_node
from src.agents.id_verifier import id_verifier_node
from src.agents.info_collector import info_collector_node
from src.agents.others import others_node
from src.agents.query_checklist import query_checklist_node
from src.agents.final_briefing import final_briefing_node
from src.agents.first_chat import first_chat_node
from src.agents.permissions_granted import permissions_granted_node


# 为了兼容性，可以在这里添加一些常用的导入
__all__ = [
    "supervisor_node",
    "id_verifier_node",
    "info_collector_node",
    "others_node",
    "query_checklist_node",
    "final_briefing_node",
    "first_chat_node",
    "permissions_granted_node"
]