"""
Memgraph database implementation using gqlalchemy.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from gqlalchemy import Memgraph
from app.common.interfaces.database import IDatabase
from app.common.config_loader import config_loader

# Configure logging
logger = logging.getLogger(__name__)


class MemgraphDB(IDatabase):
    """Memgraph database implementation."""

    def __init__(self):
        """Initialize the Memgraph database connection."""
        self.memgraph: Optional[Memgraph] = None
        self.connected = False

    async def connect(self) -> None:
        """Establish connection to the Memgraph database."""
        if self.connected:
            logger.warning("Already connected to Memgraph")
            return

        try:
            # Get database configuration
            db_config = config_loader.get('database', {})
            uri = db_config.get('uri', 'bolt://localhost:7687')
            user = db_config.get('user', 'memgraph')
            password = db_config.get('password', 'password')

            # Create Memgraph connection
            self.memgraph = Memgraph(
                host=uri.split('://')[1].split(':')[0],
                port=int(uri.split(':')[2]),
                username=user,
                password=password
            )

            # Test connection
            await self.execute_query("MATCH (n) RETURN count(n) LIMIT 1")
            self.connected = True
            logger.info(f"Successfully connected to Memgraph at {uri}")

        except Exception as e:
            logger.error(f"Failed to connect to Memgraph: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to the Memgraph database."""
        if not self.connected or not self.memgraph:
            logger.warning("Not connected to Memgraph")
            return

        try:
            # In gqlalchemy, connections are managed automatically
            # but we'll mark as disconnected for consistency
            self.connected = False
            self.memgraph = None
            logger.info("Disconnected from Memgraph")

        except Exception as e:
            logger.error(f"Error disconnecting from Memgraph: {e}")
            raise

    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results.

        Args:
            query: The query string to execute
            parameters: Optional parameters for the query

        Returns:
            List of result rows as dictionaries
        """
        if not self.connected or not self.memgraph:
            raise RuntimeError("Not connected to Memgraph")

        try:
            # Execute the query
            if parameters:
                result = self.memgraph.execute_and_fetch(query, parameters)
            else:
                result = self.memgraph.execute_and_fetch(query)

            # Convert result to list of dictionaries
            return [dict(row) for row in result]

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    async def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute a write operation and return the number of affected rows.

        Args:
            query: The write query to execute
            parameters: Optional parameters for the query

        Returns:
            Number of affected rows
        """
        if not self.connected or not self.memgraph:
            raise RuntimeError("Not connected to Memgraph")

        try:
            # Execute the write query
            if parameters:
                result = self.memgraph.execute(query, parameters)
            else:
                result = self.memgraph.execute(query)

            # Return affected rows count (this might vary based on the operation)
            return result

        except Exception as e:
            logger.error(f"Error executing write query: {e}")
            raise

    async def vector_search(self, collection: str, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search using Memgraph MAGE.

        Args:
            collection: The collection/table name to search in
            query_vector: The query vector for similarity search
            top_k: Number of top results to return

        Returns:
            List of search results
        """
        if not self.connected or not self.memgraph:
            raise RuntimeError("Not connected to Memgraph")

        try:
            # Use Memgraph MAGE for vector similarity search
            # This is a simplified example - actual implementation may vary
            query = """
            CALL vector_search($collection, $query_vector, $top_k)
            YIELD node, similarity
            RETURN node, similarity
            ORDER BY similarity DESC
            LIMIT $top_k
            """

            parameters = {
                'collection': collection,
                'query_vector': query_vector,
                'top_k': top_k
            }

            result = self.memgraph.execute_and_fetch(query, parameters)
            return [dict(row) for row in result]

        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
            raise

    async def keyword_search(self, collection: str, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform keyword search using Memgraph Fulltext Index.

        Args:
            collection: The collection/table name to search in
            query_text: The text to search for
            top_k: Number of top results to return

        Returns:
            List of search results
        """
        if not self.connected or not self.memgraph:
            raise RuntimeError("Not connected to Memgraph")

        try:
            # Use Memgraph Fulltext Index for keyword search
            # This is a simplified example - actual implementation may vary
            query = """
            CALL text_search($collection, $query_text, $top_k)
            YIELD node, score
            RETURN node, score
            ORDER BY score DESC
            LIMIT $top_k
            """

            parameters = {
                'collection': collection,
                'query_text': query_text,
                'top_k': top_k
            }

            result = self.memgraph.execute_and_fetch(query, parameters)
            return [dict(row) for row in result]

        except Exception as e:
            logger.error(f"Error performing keyword search: {e}")
            raise

    async def store_vector(self, collection: str, vector: List[float], metadata: Dict[str, Any]) -> str:
        """
        Store a vector with metadata in Memgraph.

        Args:
            collection: The collection/table name to store in
            vector: The vector to store
            metadata: Metadata associated with the vector

        Returns:
            ID of the stored vector
        """
        if not self.connected or not self.memgraph:
            raise RuntimeError("Not connected to Memgraph")

        try:
            # Create a node with vector and metadata
            query = """
            CREATE (n:Vector {vector: $vector})
            SET n += $metadata
            RETURN id(n) as node_id
            """

            parameters = {
                'vector': vector,
                'metadata': metadata
            }

            result = list(self.memgraph.execute_and_fetch(query, parameters))
            if result:
                return str(result[0]['node_id'])
            else:
                raise RuntimeError("Failed to store vector")

        except Exception as e:
            logger.error(f"Error storing vector: {e}")
            raise

    async def store_graph_node(self, label: str, properties: Dict[str, Any]) -> str:
        """
        Store a graph node in Memgraph.

        Args:
            label: The label/type of the node
            properties: Properties of the node

        Returns:
            ID of the stored node
        """
        if not self.connected or not self.memgraph:
            raise RuntimeError("Not connected to Memgraph")

        try:
            # Create a node with the specified label and properties
            query = f"""
            CREATE (n:{label} $properties)
            RETURN id(n) as node_id
            """

            parameters = {
                'properties': properties
            }

            result = list(self.memgraph.execute_and_fetch(query, parameters))
            if result:
                return str(result[0]['node_id'])
            else:
                raise RuntimeError("Failed to store graph node")

        except Exception as e:
            logger.error(f"Error storing graph node: {e}")
            raise

    async def store_graph_relationship(self, source_id: str, target_id: str, relationship_type: str,
                                     properties: Dict[str, Any]) -> str:
        """
        Store a graph relationship in Memgraph.

        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relationship_type: Type of the relationship
            properties: Properties of the relationship

        Returns:
            ID of the stored relationship
        """
        if not self.connected or not self.memgraph:
            raise RuntimeError("Not connected to Memgraph")

        try:
            # Create a relationship between two nodes
            query = """
            MATCH (a), (b)
            WHERE id(a) = $source_id AND id(b) = $target_id
            CREATE (a)-[r:$relationship_type $properties]->(b)
            RETURN id(r) as relationship_id
            """

            # Note: In Cypher, relationship types cannot be parameterized,
            # so we need to format the query string directly
            query = query.replace('$relationship_type', relationship_type)

            parameters = {
                'source_id': int(source_id),
                'target_id': int(target_id),
                'properties': properties
            }

            result = list(self.memgraph.execute_and_fetch(query, parameters))
            if result:
                return str(result[0]['relationship_id'])
            else:
                raise RuntimeError("Failed to store graph relationship")

        except Exception as e:
            logger.error(f"Error storing graph relationship: {e}")
            raise