"""
Agent module initialization.
"""

# Import all agents
from .supervisor import supervisor_agent
from .identity_verification import identity_verification_agent
from .information_collection import information_collection_agent
from .tool_calling import tool_calling_agent
from .qa import qa_agent

# Make agents available at package level
__all__ = [
    'supervisor_agent',
    'identity_verification_agent',
    'information_collection_agent',
    'tool_calling_agent',
    'qa_agent'
]