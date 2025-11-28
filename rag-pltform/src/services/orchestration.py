"""
Orchestration service for coordinating the RAG pipeline.
"""
import logging
import time
from typing import List, Optional, Tuple
from ..models.document import Document
from ..models.query import Query
from ..models.search_result import SearchResult
from ..models.response import Response
from ..models.conversation import Conversation
from ..lib.database import DatabaseConnection
from ..lib.exceptions import DatabaseError
from ..services.pre_retrieval import PreRetrievalService
from ..services.retrieval import RetrievalService
from ..services.post_retrieval import PostRetrievalService
from ..services.generation import GenerationService

logger = logging.getLogger(__name__)


class OrchestrationService:
    """Service for orchestrating the complete RAG pipeline."""

    def __init__(
        self,
        db_connection: DatabaseConnection,
        pre_retrieval_service: Optional[PreRetrievalService] = None,
        retrieval_service: Optional[RetrievalService] = None,
        post_retrieval_service: Optional[PostRetrievalService] = None,
        generation_service: Optional[GenerationService] = None
    ):
        """Initialize orchestration service.

        Args:
            db_connection: Database connection instance
            pre_retrieval_service: Pre-retrieval service (optional, will create default if not provided)
            retrieval_service: Retrieval service (optional, will create default if not provided)
            post_retrieval_service: Post-retrieval service (optional, will create default if not provided)
            generation_service: Generation service (optional, will create default if not provided)
        """
        self.db_connection = db_connection
        self.pre_retrieval_service = pre_retrieval_service or PreRetrievalService()
        self.retrieval_service = retrieval_service or RetrievalService(db_connection)
        self.post_retrieval_service = post_retrieval_service or PostRetrievalService()
        self.generation_service = generation_service or GenerationService()

    def search(
        self,
        name: str,
        question: str,
        top_k: int = 5,
        expand_query: bool = True,
        rerank: bool = True,
        enable_vector_search: bool = True,
        enable_graph_search: bool = True
    ) -> Tuple[List[SearchResult], List[str]]:
        """Perform a complete search operation.

        Args:
            name: Name of the document collection to search
            question: Question to ask about the documents
            top_k: Number of results to return
            expand_query: Enable query expansion
            rerank: Enable result reranking
            enable_vector_search: Enable vector search
            enable_graph_search: Enable graph search

        Returns:
            Tuple of (search results, chunk contents)

        Raises:
            ValueError: If inputs are invalid
            DatabaseError: If database operations fail
        """
        start_time = time.time()
        logger.info("Starting search operation for collection: %s, question: %s", name, question)

        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Collection name cannot be empty")

        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be positive")

        try:
            # 1. Process query (pre-retrieval)
            logger.info("Step 1: Processing query")
            query = self.pre_retrieval_service.process_query(question, expand_query=expand_query)

            # 2. Retrieve relevant documents
            logger.info("Step 2: Retrieving documents")
            search_results = self.retrieval_service.search(
                query, name, top_k=top_k,
                enable_vector_search=enable_vector_search,
                enable_graph_search=enable_graph_search
            )

            # 3. Post-process results
            logger.info("Step 3: Post-processing results")
            search_results = self.post_retrieval_service.process_results(search_results, query, rerank=rerank)

            # 4. Retrieve chunk contents
            logger.info("Step 4: Retrieving chunk contents")
            chunk_contents = []
            for result in search_results:
                try:
                    chunk = self.retrieval_service.get_chunk_content(result.chunk_id)
                    if chunk:
                        chunk_contents.append(chunk.content)
                    else:
                        chunk_contents.append("[Content not available]")
                        logger.warning("Chunk content not found for chunk_id: %s", result.chunk_id)
                except Exception as e:
                    chunk_contents.append("[Content retrieval failed]")
                    logger.error("Failed to retrieve chunk content for chunk_id %s: %s", result.chunk_id, str(e))

            total_duration = time.time() - start_time
            logger.info("Search operation completed in %.2f seconds, returning %d results", total_duration, len(search_results))

            return search_results, chunk_contents

        except ValueError:
            # Re-raise value errors
            raise
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            logger.error("Search operation failed: %s", str(e))
            raise DatabaseError(f"Search operation failed: {str(e)}")

    def chat(
        self,
        name: str,
        question: str,
        conversation: Optional[Conversation] = None,
        top_k: int = 5,
        expand_query: bool = True,
        rerank: bool = True,
        enable_vector_search: bool = True,
        enable_graph_search: bool = True
    ) -> Tuple[Response, Conversation]:
        """Engage in a conversation about indexed documents.

        Args:
            name: Name of the document collection to chat about
            question: Question to ask about the documents
            conversation: Existing conversation (optional)
            top_k: Number of results to return
            expand_query: Enable query expansion
            rerank: Enable result reranking
            enable_vector_search: Enable vector search
            enable_graph_search: Enable graph search

        Returns:
            Tuple of (response, updated conversation)

        Raises:
            ValueError: If inputs are invalid
            DatabaseError: If database operations fail
        """
        start_time = time.time()
        logger.info("Starting chat operation for collection: %s, question: %s", name, question)

        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Collection name cannot be empty")

        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be positive")

        try:
            # Create or update conversation
            if conversation is None:
                conversation = Conversation(session_id=f"chat_{int(time.time())}")
                logger.info("Created new conversation: %s", conversation.id)
            else:
                conversation.update_last_activity()
                logger.info("Using existing conversation: %s", conversation.id)

            # 1. Process query (pre-retrieval)
            logger.info("Step 1: Processing query")
            query = self.pre_retrieval_service.process_query(question, expand_query=expand_query)

            # 2. Retrieve relevant documents
            logger.info("Step 2: Retrieving documents")
            search_results = self.retrieval_service.search(
                query, name, top_k=top_k,
                enable_vector_search=enable_vector_search,
                enable_graph_search=enable_graph_search
            )

            # 3. Post-process results
            logger.info("Step 3: Post-processing results")
            search_results = self.post_retrieval_service.process_results(search_results, query, rerank=rerank)

            # 4. Retrieve chunk contents
            logger.info("Step 4: Retrieving chunk contents")
            chunk_contents = []
            for result in search_results:
                try:
                    chunk = self.retrieval_service.get_chunk_content(result.chunk_id)
                    if chunk:
                        chunk_contents.append(chunk.content)
                    else:
                        chunk_contents.append("[Content not available]")
                        logger.warning("Chunk content not found for chunk_id: %s", result.chunk_id)
                except Exception as e:
                    chunk_contents.append("[Content retrieval failed]")
                    logger.error("Failed to retrieve chunk content for chunk_id %s: %s", result.chunk_id, str(e))

            # 5. Get previous responses for context (if in conversation)
            previous_responses = []
            if conversation.id:
                previous_responses = self._get_previous_responses(conversation.id)

            # 6. Generate response
            logger.info("Step 5: Generating response")
            try:
                if previous_responses:
                    response = self.generation_service.generate_follow_up_response(
                        query, search_results, chunk_contents, previous_responses, conversation.context
                    )
                else:
                    response = self.generation_service.generate_response(
                        query, search_results, chunk_contents, conversation.context
                    )
            except Exception as e:
                logger.error("Failed to generate response: %s", str(e))
                response = Response(
                    query_id=query.id,
                    content="Sorry, I encountered an error while generating a response. Please try again.",
                    model_used="error-handler"
                )

            # 7. Store conversation data
            logger.info("Step 6: Storing conversation data")
            try:
                self._store_conversation_data(conversation, query, response)
            except Exception as e:
                logger.error("Failed to store conversation data: %s", str(e))
                # Continue without storing data

            # Update conversation context
            conversation.update_context({
                "last_question": question,
                "last_response_length": len(response.content)
            })

            total_duration = time.time() - start_time
            logger.info("Chat operation completed in %.2f seconds", total_duration)

            return response, conversation

        except ValueError:
            # Re-raise value errors
            raise
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            logger.error("Chat operation failed: %s", str(e))
            raise DatabaseError(f"Chat operation failed: {str(e)}")

    def _get_previous_responses(self, conversation_id: str) -> List[Response]:
        """Get previous responses in a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            List of Response objects
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (c:Conversation {id: $conversation_id})-[:HAS_RESPONSE]->(r:Response)
                RETURN r
                ORDER BY r.generated_at DESC
                LIMIT 5
                """

                result = session.run(query, {"conversation_id": conversation_id})

                responses = []
                for record in result:
                    node = record["r"]
                    responses.append(Response.from_dict(dict(node)))

                # Reverse to get chronological order
                responses.reverse()
                return responses

        except Exception as e:
            logger.error("Failed to retrieve previous responses: %s", str(e))
            return []  # Return empty list on failure

    def _store_conversation_data(self, conversation: Conversation, query: Query, response: Response) -> None:
        """Store conversation data in database.

        Args:
            conversation: Conversation object
            query: Query object
            response: Response object
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                # Store conversation if it's new
                if conversation.created_at == conversation.updated_at:
                    conv_query = """
                    CREATE (c:Conversation {
                        id: $id,
                        session_id: $session_id,
                        context: $context,
                        started_at: $started_at,
                        last_activity: $last_activity,
                        created_at: $created_at,
                        updated_at: $updated_at
                    })
                    """
                    session.run(conv_query, conversation.to_dict())

                # Store query
                query_query = """
                CREATE (q:Query {
                    id: $id,
                    original_text: $original_text,
                    expanded_text: $expanded_text,
                    user_id: $user_id,
                    timestamp: $timestamp,
                    created_at: $created_at,
                    updated_at: $updated_at
                })
                """
                session.run(query_query, query.to_dict())

                # Store response
                response_query = """
                CREATE (r:Response {
                    id: $id,
                    query_id: $query_id,
                    content: $content,
                    model_used: $model_used,
                    tokens_used: $tokens_used,
                    generated_at: $generated_at,
                    created_at: $created_at,
                    updated_at: $updated_at
                })
                """
                session.run(response_query, response.to_dict())

                # Create relationships
                rel_query = """
                MATCH (c:Conversation {id: $conversation_id}), (q:Query {id: $query_id}), (r:Response {id: $response_id})
                CREATE (c)-[:HAS_QUERY]->(q), (c)-[:HAS_RESPONSE]->(r), (q)-[:GENERATED]->(r)
                """
                session.run(rel_query, {
                    "conversation_id": conversation.id,
                    "query_id": query.id,
                    "response_id": response.id
                })

        except Exception as e:
            logger.error("Failed to store conversation data: %s", str(e))
            raise DatabaseError(f"Failed to store conversation data: {str(e)}")

    def get_conversation_history(self, conversation_id: str) -> List[Tuple[Query, Response]]:
        """Get conversation history.

        Args:
            conversation_id: ID of the conversation

        Returns:
            List of (Query, Response) tuples

        Raises:
            DatabaseError: If database operations fail
        """
        try:
            driver = self.db_connection.get_driver()
            with driver.session() as session:
                query = """
                MATCH (c:Conversation {id: $conversation_id})-[:HAS_QUERY]->(q:Query)-[:GENERATED]->(r:Response)
                RETURN q, r
                ORDER BY q.timestamp ASC
                """

                result = session.run(query, {"conversation_id": conversation_id})

                history = []
                for record in result:
                    query_node = record["q"]
                    response_node = record["r"]
                    query_obj = Query.from_dict(dict(query_node))
                    response_obj = Response.from_dict(dict(response_node))
                    history.append((query_obj, response_obj))

                return history

        except Exception as e:
            logger.error("Failed to retrieve conversation history: %s", str(e))
            raise DatabaseError(f"Failed to retrieve conversation history: {str(e)}")