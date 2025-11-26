"""
Integration tests for Q&A agent functionality.
"""

import pytest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_qa_agent_initialization():
    """Test that Q&A agent can be initialized without errors."""
    try:
        from src.agents.qa import qa_agent
        assert True
    except Exception as e:
        pytest.fail(f"Failed to initialize Q&A agent: {e}")

def test_answer_general_question():
    """Test answering a general onboarding question."""
    from src.agents.qa import qa_agent

    # Test general onboarding question
    result = qa_agent.answer_question("What is the onboarding process?")

    # Verify the result
    assert 'question' in result
    assert 'answer' in result
    assert 'category' in result
    assert result['question'] == "What is the onboarding process?"
    assert 'onboarding process' in result['answer'].lower()
    assert result['category'] == 'onboarding_process'

def test_answer_responsibilities_question():
    """Test answering a position responsibilities question."""
    from src.agents.qa import qa_agent

    # Test responsibilities question with context
    context = {'position': 'software_engineer'}
    result = qa_agent.answer_question("What are my responsibilities?", context)

    # Verify the result
    assert 'question' in result
    assert 'answer' in result
    assert 'category' in result
    assert result['question'] == "What are my responsibilities?"
    assert 'responsibilities' in result['answer'].lower()
    assert result['category'] == 'responsibilities'

def test_answer_post_tasks_question():
    """Test answering a post-onboarding tasks question."""
    from src.agents.qa import qa_agent

    # Test post-tasks question with context
    context = {'position': 'software_engineer'}
    result = qa_agent.answer_question("What are my next tasks?", context)

    # Verify the result
    assert 'question' in result
    assert 'answer' in result
    assert 'category' in result
    assert result['question'] == "What are my next tasks?"
    assert 'tasks' in result['answer'].lower()
    assert result['category'] == 'post_tasks'

def test_answer_unrecognized_question():
    """Test answering an unrecognized question."""
    from src.agents.qa import qa_agent

    # Test unrecognized question
    result = qa_agent.answer_question("What is the meaning of life?")

    # Verify the result
    assert 'question' in result
    assert 'answer' in result
    assert 'category' in result
    assert result['question'] == "What is the meaning of life?"
    assert 'not sure' in result['answer'].lower() or 'contact hr' in result['answer'].lower()
    assert result['category'] == 'general'

def test_get_position_responsibilities():
    """Test getting position responsibilities."""
    from src.agents.qa import qa_agent

    # Test getting responsibilities for a valid position
    result = qa_agent.get_position_responsibilities("software_engineer")

    # Verify the result
    assert 'position' in result
    assert result['position'] == "software_engineer"
    assert 'name' in result
    assert 'responsibilities' in result
    assert 'required_permissions' in result
    assert result['name'] == "Software Engineer"

def test_get_position_responsibilities_not_found():
    """Test getting position responsibilities for non-existent position."""
    from src.agents.qa import qa_agent

    # Test getting responsibilities for an invalid position
    result = qa_agent.get_position_responsibilities("non_existent_position")

    # Verify the result
    assert 'position' in result
    assert result['position'] == "non_existent_position"
    assert 'error' in result

def test_get_post_onboarding_tasks():
    """Test getting post-onboarding tasks."""
    from src.agents.qa import qa_agent

    # Test getting tasks for a valid position
    result = qa_agent.get_post_onboarding_tasks("software_engineer")

    # Verify the result
    assert 'position' in result
    assert result['position'] == "software_engineer"
    assert 'tasks' in result
    assert isinstance(result['tasks'], list)
    assert len(result['tasks']) > 0

if __name__ == "__main__":
    pytest.main([__file__])