import operator
from typing import Annotated, List, TypedDict, Optional, Dict, Any
from langchain_core.messages import BaseMessage

class EmployeeInfo(TypedDict):
    name: Optional[str]
    id_number: Optional[str]
    school: Optional[str]
    role: Optional[str]   # e.g., "admin", "developer"
    photo_verified: bool
    email_account: Optional[str]
    email_password: Optional[str]
    git_account: Optional[str]
    git_password: Optional[str]

class Checklist(TypedDict):
    id_verified: bool
    info_collected: bool
    role_briefed: bool
    permissions_granted: bool
    final_briefing: bool

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    employee_info: EmployeeInfo
    checklist: Checklist
    next_step: Optional[str]
    error_msg: Optional[str]