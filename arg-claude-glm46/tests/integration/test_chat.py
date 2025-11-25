"""Integration tests for the conversation flow."""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services.orchestration.conversation_manager import ConversationManager
from src.models.conversation import Conversation


def test_conversation_flow_integration():
    """Test the complete conversation flow."""
    # Create conversation manager
    manager = ConversationManager()

    # Mock the answer generator
    with patch('src.services.orchestration.conversation_manager.answer_generator') as mock_generator:
        mock_generator.generate_answer.return_value = "This is a test response"

        # Create a conversation
        conversation = manager.create_conversation(
            user_id="test_user",
            document_name="test_doc",
            title="Test Conversation"
        )

        # Verify conversation was created correctly
        assert isinstance(conversation, Conversation)
        assert conversation.user_id == "test_user"
        assert conversation.document_name == "test_doc"
        assert conversation.title == "Test Conversation"
        assert conversation.is_active == True

        # Process a message
        response = manager.process_message(conversation, "Hello, how are you?")

        # Verify response
        assert response == "This is a test response"
        mock_generator.generate_answer.assert_called_once_with(
            conversation=conversation,
            user_message="Hello, how are you?",
            document_name="test_doc"
        )

        # End the conversation
        manager.end_conversation(conversation)

        # Verify conversation was ended
        assert conversation.is_active == False


def test_conversation_validation():
    """Test conversation validation."""
    manager = ConversationManager()

    # Test invalid user_id
    with pytest.raises(ValueError):
        manager.create_conversation("", "test_doc")

    # Test invalid document_name
    with pytest.raises(ValueError):
        manager.create_conversation("test_user", "")

    # Test invalid conversation object for processing
    with pytest.raises(ValueError):
        manager.process_message(None, "Hello")

    # Test invalid user message
    conversation = manager.create_conversation("test_user", "test_doc")
    with pytest.raises(ValueError):
        manager.process_message(conversation, "")

    # Test processing message for inactive conversation
    conversation.is_active = False
    with pytest.raises(ValueError):
        manager.process_message(conversation, "Hello")


if __name__ == "__main__":
    pytest.main([__file__])