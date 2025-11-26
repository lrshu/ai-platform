"""
Integration tests for the complete employee onboarding flow.
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_agent_initialization():
    """Test that all agents can be initialized without errors."""
    try:
        from src.agents.supervisor import supervisor_agent
        from src.agents.identity_verification import identity_verification_agent
        from src.agents.information_collection import information_collection_agent
        from src.agents.tool_calling import tool_calling_agent
        from src.agents.qa import qa_agent
        assert True
    except Exception as e:
        pytest.fail(f"Failed to initialize agents: {e}")

def test_qa_functionality():
    """Test Q&A agent functionality."""
    from src.agents.qa import qa_agent

    # Test Q&A agent
    answer = qa_agent.answer_question("What is the onboarding process?")
    assert 'answer' in answer
    assert 'onboarding process' in answer['answer'].lower()

    # Test position responsibilities query
    answer = qa_agent.answer_question("What are my responsibilities?",
                                    {'position': 'software_engineer'})
    assert 'answer' in answer
    assert 'responsibilities' in answer['answer'].lower()

def test_model_creation():
    """Test that all models can be imported without errors."""
    try:
        from src.models import Employee, OnboardingChecklist, IDPhoto, AccountCredentials
        assert True
    except Exception as e:
        pytest.fail(f"Failed to import models: {e}")

def test_service_initialization():
    """Test that all services can be initialized without errors."""
    try:
        from src.services.id_verification_service import id_verification_service
        from src.services.position_service import position_service
        from src.services.mcp_client import mcp_client
        from src.services.session_service import session_service
        assert True
    except Exception as e:
        pytest.fail(f"Failed to initialize services: {e}")

if __name__ == "__main__":
    pytest.main([__file__])