"""
Abstract base class for database interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio


class IDatabase(ABC):
    """Abstract base class for database operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the database."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the database."""
        pass

    @abstractmethod
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results.

        Args:
            query: The query string to execute
            parameters: Optional parameters for the query

        Returns:
            List of result rows as dictionaries
        """
        pass

    @abstractmethod
    async def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute a write operation and return the number of affected rows.

        Args:
            query: The write query to execute
            parameters: Optional parameters for the query

        Returns:
            Number of affected rows
        """
        pass

    @abstractmethod
    async def vector_search(self, collection: str, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.

        Args:
            collection: The collection/table name to search in
            query_vector: The query vector for similarity search
            top_k: Number of top results to return

        Returns:
            List of search results
        """
        pass

    @abstractmethod
    async def keyword_search(self, collection: str, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform keyword search.

        Args:
            collection: The collection/table name to search in
            query_text: The text to search for
            top_k: Number of top results to return

        Returns:
            List of search results
        """
        pass

    @abstractmethod
    async def store_vector(self, collection: str, vector: List[float], metadata: Dict[str, Any]) -> str:
        """
        Store a vector with metadata.

        Args:
            collection: The collection/table name to store in
            vector: The vector to store
            metadata: Metadata associated with the vector

        Returns:
            ID of the stored vector
        """
        pass

    @abstractmethod
    async def store_graph_node(self, label: str, properties: Dict[str, Any]) -> str:
        """
        Store a graph node.

        Args:
            label: The label/type of the node
            properties: Properties of the node

        Returns:
            ID of the stored node
        """
        pass

    @abstractmethod
    async def store_graph_relationship(self, source_id: str, target_id: str, relationship_type: str,
                                     properties: Dict[str, Any]) -> str:
        """
        Store a graph relationship.

        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relationship_type: Type of the relationship
            properties: Properties of the relationship

        Returns:
            ID of the stored relationship
        """
        pass