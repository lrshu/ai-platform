"""
Chat orchestration service for the RAG backend system.
"""

from typing import List, Dict, Any, Optional
from src.services.conversation_manager import get_conversation_manager
from src.services.answer_generator import get_answer_generator
from src.services.retrieval_service import get_retrieval_service
from src.models.query import Query
from src.models.conversation_context import ConversationContext
from src.lib.exceptions import ChatError
import uuid
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Orchestration service for conversational question answering."""

    def __init__(self):
        """Initialize the ChatService."""
        self.conversation_manager = get_conversation_manager()
        self.answer_generator = get_answer_generator()
        self.retrieval_service = get_retrieval_service()

    def chat_with_documents(self, collection_name: str, question: str,
                          session_id: Optional[str] = None,
                          top_k: int = 5,
                          enable_query_expansion: bool = True,
                          enable_reranking: bool = True,
                          enable_vector_search: bool = True,
                          enable_graph_search: bool = True) -> Dict[str, Any]:
        """
        Have a conversation about indexed documents.

        Args:
            collection_name: Name of the document collection
            question: The question to ask
            session_id: Identifier for the chat session (generated if not provided)
            top_k: Number of results to return
            enable_query_expansion: Whether to expand the query
            enable_reranking: Whether to re-rank results
            enable_vector_search: Whether to perform vector search
            enable_graph_search: Whether to perform graph search

        Returns:
            Dictionary containing the answer, sources, and session information

        Raises:
            ChatError: If chat operation fails
        """
        try:
            # Generate session ID if not provided
            if session_id is None:
                session_id = str(uuid.uuid4())

            logger.info(f"Starting chat session {session_id} with question: {question}")

            # Step 1: Retrieve conversation history
            conversation_history = self.conversation_manager.format_conversation_context(
                session_id, max_turns=5
            )

            # Step 2: Perform hybrid search
            retrieval_results = self.retrieval_service.hybrid_search(
                query_text=question,
                collection_name=collection_name,
                top_k=top_k,
                enable_query_expansion=enable_query_expansion,
                enable_reranking=enable_reranking,
                enable_vector_search=enable_vector_search,
                enable_graph_search=enable_graph_search
            )

            # Step 3: Format retrieved content for answer generation
            retrieved_content = []
            for result in retrieval_results:
                # In a real implementation, we'd retrieve the actual chunk content
                # For now, we'll create placeholder content
                content_item = {
                    "content": f"Content of chunk {result.chunk_id}",
                    "source": f"Document containing chunk {result.chunk_id}",
                    "relevance_score": result.relevance_score
                }
                retrieved_content.append(content_item)

            # Step 4: Generate answer
            answer_result = self.answer_generator.generate_answer_with_citations(
                question=question,
                retrieved_content=retrieved_content,
                conversation_history=conversation_history
            )

            # Step 5: Save conversation context
            query_obj = Query(content=question)
            conversation_entry = self.conversation_manager.add_conversation_entry(
                session_id=session_id,
                query_id=query_obj.id,
                response=answer_result["answer"]
            )

            # Step 6: Prepare response
            response = {
                "answer": answer_result["answer"],
                "sources": retrieved_content,
                "citations": answer_result["citations"],
                "session_id": session_id,
                "query_id": query_obj.id
            }

            logger.info(f"Chat completed for session {session_id}")
            return response

        except Exception as e:
            logger.error(f"Chat failed for session {session_id}: {e}")
            raise ChatError(f"Chat failed: {str(e)}")

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a session.

        Args:
            session_id: Identifier for the chat session

        Returns:
            List of conversation entries
        """
        try:
            history = self.conversation_manager.get_conversation_history(session_id)

            formatted_history = []
            for entry in history:
                formatted_entry = {
                    "id": entry.id,
                    "query_id": entry.query_id,
                    "response": entry.response,
                    "created_at": entry.created_at.isoformat()
                }
                formatted_history.append(formatted_entry)

            return formatted_history

        except Exception as e:
            logger.error(f"Failed to retrieve session history for {session_id}: {e}")
            raise ChatError(f"Failed to retrieve session history: {str(e)}")

    def clear_session_history(self, session_id: str) -> None:
        """
        Clear the conversation history for a session.

        Args:
            session_id: Identifier for the chat session
        """
        try:
            self.conversation_manager.clear_conversation_history(session_id)
            logger.info(f"Cleared conversation history for session {session_id}")

        except Exception as e:
            logger.error(f"Failed to clear session history for {session_id}: {e}")
            raise ChatError(f"Failed to clear session history: {str(e)}")

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get a summary of the conversation session.

        Args:
            session_id: Identifier for the chat session

        Returns:
            Dictionary with session summary information
        """
        try:
            summary = self.conversation_manager.get_session_summary(session_id)
            return summary

        except Exception as e:
            logger.error(f"Failed to generate session summary for {session_id}: {e}")
            raise ChatError(f"Failed to generate session summary: {str(e)}")


# Global chat service instance
chat_service = ChatService()


def get_chat_service() -> ChatService:
    """
    Get the global chat service instance.

    Returns:
        ChatService instance
    """
    return chat_service